from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from domain import (
    CCDCType, AllocationMethod, CCDCStatus, AllocationStatus,
    TransactionType, CCInventoryStatus, ResponsibilityType,
    CCategory, CCDCItem, CCDCAllocation, CCDCAllocationLine,
    CCDCTransaction, CCDCTransfer, CCDCInventory, CCDCInventoryLine,
    CCDCWriteOff, CCDCSparePart, CCDCImportLog,
    Result, ValidationError, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.cc_repository import CCRepository
from infrastructure.models.gl_models import AccountingPeriodModel, JournalEntryModel, JournalLineModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class CCUseCases:
    def __init__(self, session: Session):
        self.repo = CCRepository(session)
        self._session = session

    def _validate_period_open(self, period: str) -> None:
        p = self._session.get(AccountingPeriodModel, period)
        if p and p.is_closed:
            raise ValidationError(ErrorCodes.CC_PERIOD_CLOSED, period=period)

    def _get_category_or_fail(self, category_id: int) -> CCategory:
        cat = self.repo.get_category(category_id)
        if not cat:
            raise ValidationError(ErrorCodes.CC_CATEGORY_NOT_FOUND, category_id=category_id)
        return cat

    def _get_item_or_fail(self, item_id: int) -> CCDCItem:
        item = self.repo.get_item(item_id)
        if not item:
            raise ValidationError(ErrorCodes.CC_ITEM_NOT_FOUND, item_id=item_id)
        return item

    # ── UC-CC-01: Category Management ─────────────────────────────────

    def create_category(self, data: dict) -> Result:
        try:
            category = CCategory(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_category(category)

    def get_category(self, category_id: int) -> Result:
        try:
            cat = self._get_category_or_fail(category_id)
        except ValidationError as e:
            return Result.failure(e)
        return Result.success(cat)

    def update_category(self, category_id: int, **updates) -> Result:
        try:
            self._get_category_or_fail(category_id)
        except ValidationError as e:
            return Result.failure(e)
        return self.repo.update_category(category_id, **updates)

    def delete_category(self, category_id: int) -> Result:
        return self.repo.delete_category(category_id)

    def list_categories(self) -> Result:
        return Result.success(self.repo.list_categories())

    # ── UC-CC-02: CCDC Item Registration ──────────────────────────────

    def create_item(self, data: dict) -> Result:
        try:
            self._get_category_or_fail(data.get("category_id", 0))
            if "total_cost" not in data or data.get("total_cost") in (None, 0, "0", Decimal("0")):
                if "unit_price" in data and "quantity" in data:
                    qty = Decimal(str(data["quantity"]))
                    price = Decimal(str(data["unit_price"]))
                    data["total_cost"] = _vnd(qty * price)
            item = CCDCItem(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_item(item)

    def get_item(self, item_id: int) -> Result:
        try:
            item = self._get_item_or_fail(item_id)
        except ValidationError as e:
            return Result.failure(e)
        return Result.success(item)

    def update_item(self, item_id: int, **updates) -> Result:
        try:
            self._get_item_or_fail(item_id)
        except ValidationError as e:
            return Result.failure(e)
        return self.repo.update_item(item_id, **updates)

    def delete_item(self, item_id: int) -> Result:
        return self.repo.delete_item(item_id)

    def list_items(self, category_id: Optional[int] = None,
                   status: Optional[str] = None,
                   department_id: Optional[int] = None,
                   cc_type: Optional[str] = None) -> Result:
        items = self.repo.list_items(
            category_id=category_id, status=status,
            department_id=department_id, cc_type=cc_type,
        )
        return Result.success(items)

    # ── UC-CC-03: Allocation Processing ───────────────────────────────

    def create_allocation(self, data: dict) -> Result:
        try:
            item = self._get_item_or_fail(data.get("item_id", 0))
            alloc = CCDCAllocation(**data)
            if alloc.total_amount > item.remaining_amount:
                return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_EXCEEDS_COST))
            if alloc.allocation_method == AllocationMethod.one_time:
                alloc.amount_per_period = alloc.total_amount
                alloc.total_periods = 1
                alloc.status = AllocationStatus.fully_allocated
            elif alloc.allocation_method == AllocationMethod.two_time:
                alloc.amount_per_period = _vnd(alloc.total_amount / Decimal("2"))
                alloc.total_periods = 2
                alloc.status = AllocationStatus.partially_allocated
            else:
                if not alloc.total_periods or alloc.total_periods < 2:
                    return Result.failure(AccountError(ErrorCodes.CC_MISSING_REQUIRED_FIELD, field="total_periods"))
                alloc.amount_per_period = _vnd(alloc.total_amount / Decimal(alloc.total_periods))
                alloc.status = AllocationStatus.partially_allocated
            result = self.repo.create_allocation(alloc)
            if result.is_failure():
                return result
            created = result.get_data()
            created.total_amount = alloc.total_amount
            created.amount_per_period = alloc.amount_per_period

            lines = []
            for i in range(alloc.total_periods):
                from dateutil.relativedelta import relativedelta
                y, m = int(alloc.start_period.split("-")[0]), int(alloc.start_period.split("-")[1])
                d = date(y, m, 1) + relativedelta(months=i)
                period = d.strftime("%Y-%m")
                is_last = i == alloc.total_periods - 1
                amount = alloc.total_amount - alloc.amount_per_period * (alloc.total_periods - 1) if is_last else alloc.amount_per_period
                line = CCDCAllocationLine(
                    allocation_id=created.id, item_id=alloc.item_id,
                    period=period, planned_amount=amount,
                )
                line_result = self.repo.create_allocation_line(line)
                if line_result.is_failure():
                    self._session.rollback()
                    return line_result
                lines.append(line_result.get_data())

            if alloc.allocation_method == AllocationMethod.one_time:
                self.repo.update_item(item.id, allocated_amount=item.total_cost, remaining_amount=Decimal("0"),
                                      allocation_status=AllocationStatus.fully_allocated)
            else:
                self.repo.update_item(item.id, allocated_amount=Decimal("0"), remaining_amount=item.total_cost,
                                      allocation_status=AllocationStatus.partially_allocated)

            return Result.success({"allocation": created, "lines": lines})
        except ValidationError as e:
            return Result.failure(e)

    def get_allocation(self, alloc_id: int) -> Result:
        alloc = self.repo.get_allocation(alloc_id)
        if not alloc:
            return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_NOT_FOUND, alloc_id=alloc_id))
        lines = self.repo.list_allocation_lines(allocation_id=alloc_id)
        return Result.success({"allocation": alloc, "lines": lines})

    def list_allocations(self, item_id: Optional[int] = None) -> Result:
        allocs = self.repo.list_allocations(item_id=item_id)
        return Result.success(allocs)

    def post_allocation_line(self, line_id: int) -> Result:
        line = self.repo.get_allocation_line(line_id)
        if not line:
            return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_LINE_NOT_FOUND, line_id=line_id))
        if line.is_posted:
            return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_ALREADY_POSTED, line_id=line_id))
        try:
            self._validate_period_open(line.period)
        except ValidationError as e:
            return Result.failure(e)

        alloc = self.repo.get_allocation(line.allocation_id)
        item = self.repo.get_item(line.item_id)

        je = JournalEntryModel(
            journal_number=f"CC-ALOC-{line.period}-{line.id}",
            transaction_date=date(int(line.period.split("-")[0]), int(line.period.split("-")[1]), 1),
            description=f"Phân bổ CCDC {item.code} tháng {line.period}",
            period=line.period,
            is_posted=True,
            posted_date=datetime.now(timezone.utc),
            created_by="cc_system",
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(je)
        self._session.flush()

        debit_line = JournalLineModel(
            journal_entry_id=je.id,
            account_id=alloc.gl_account_debit,
            debit=line.planned_amount,
            credit=Decimal("0"),
            period=line.period,
        )
        self._session.add(debit_line)
        credit_line = JournalLineModel(
            journal_entry_id=je.id,
            account_id=alloc.gl_account_credit,
            debit=Decimal("0"),
            credit=line.planned_amount,
            period=line.period,
        )
        self._session.add(credit_line)

        self.repo.update_allocation_line(line_id,
            actual_amount=line.planned_amount,
            is_posted=True,
            posted_at=datetime.now(timezone.utc),
            gl_journal_ref=je.journal_number,
        )

        new_allocated = alloc.allocated_amount + line.planned_amount
        new_remaining = alloc.total_amount - new_allocated
        new_status = AllocationStatus.fully_allocated if new_remaining <= Decimal("0.001") else AllocationStatus.partially_allocated
        self.repo.update_allocation(line.allocation_id,
            allocated_amount=new_allocated, remaining_amount=max(new_remaining, Decimal("0")),
            status=new_status,
        )

        new_item_allocated = item.allocated_amount + line.planned_amount
        new_item_remaining = item.total_cost - new_item_allocated
        new_item_status = AllocationStatus.fully_allocated if new_item_remaining <= Decimal("0.001") else AllocationStatus.partially_allocated
        self.repo.update_item(line.item_id,
            allocated_amount=new_item_allocated, remaining_amount=max(new_item_remaining, Decimal("0")),
            allocation_status=new_item_status,
        )

        self._session.flush()
        return Result.success({
            "journal_id": je.id,
            "journal_number": je.journal_number,
            "allocation_line_id": line_id,
        })

    # ── UC-CC-04: Transaction Recording ───────────────────────────────

    def create_transaction(self, data: dict) -> Result:
        try:
            item = self._get_item_or_fail(data.get("item_id", 0))
            txn = CCDCTransaction(**data)
            qty = Decimal(str(txn.quantity))
            if txn.transaction_type == TransactionType.issuance and qty > item.quantity:
                return Result.failure(AccountError(ErrorCodes.CC_INSUFFICIENT_QUANTITY, item_id=item.id, available=item.quantity))
            if txn.transaction_type == TransactionType.issuance:
                self.repo.update_item(item.id, status=CCDCStatus.in_use, in_use_date=txn.transaction_date)
            elif txn.transaction_type == TransactionType.return_to_stock:
                self.repo.update_item(item.id, status=CCDCStatus.in_stock)
            result = self.repo.create_transaction(txn)
            return result
        except ValidationError as e:
            return Result.failure(e)

    def get_transaction(self, txn_id: int) -> Result:
        txn = self.repo.get_transaction(txn_id)
        if not txn:
            return Result.failure(AccountError(ErrorCodes.CC_TRANSACTION_NOT_FOUND, txn_id=txn_id))
        return Result.success(txn)

    def list_transactions(self, item_id: Optional[int] = None,
                          period: Optional[str] = None,
                          transaction_type: Optional[str] = None) -> Result:
        txns = self.repo.list_transactions(item_id=item_id, period=period, transaction_type=transaction_type)
        return Result.success(txns)

    # ── UC-CC-05: Transfer Management ─────────────────────────────────

    def create_transfer(self, data: dict) -> Result:
        try:
            item = self._get_item_or_fail(data.get("item_id", 0))
            transfer = CCDCTransfer(**data)
            if transfer.quantity > item.quantity:
                return Result.failure(AccountError(ErrorCodes.CC_INSUFFICIENT_QUANTITY, item_id=item.id, available=item.quantity))
            result = self.repo.create_transfer(transfer)
            if result.is_success():
                self.repo.update_item(item.id, status=CCDCStatus.transferred,
                                      department_id=transfer.to_department_id,
                                      employee_id=transfer.to_employee_id,
                                      location=transfer.to_location)
            return result
        except ValidationError as e:
            return Result.failure(e)

    def get_transfer(self, transfer_id: int) -> Result:
        t = self.repo.get_transfer(transfer_id)
        if not t:
            return Result.failure(AccountError(ErrorCodes.CC_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        return Result.success(t)

    def list_transfers(self, item_id: Optional[int] = None) -> Result:
        return Result.success(self.repo.list_transfers(item_id=item_id))

    # ── UC-CC-06: Inventory/Stocktake ─────────────────────────────────

    def create_inventory(self, data: dict, lines: List[dict]) -> Result:
        try:
            inv = CCDCInventory(**data)
            domain_lines = []
            for ld in lines:
                line = CCDCInventoryLine(**ld)
                domain_lines.append(line)
            inv.lines = domain_lines
            return self.repo.create_inventory(inv)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

    def get_inventory(self, inv_id: int) -> Result:
        inv = self.repo.get_inventory(inv_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.CC_INVENTORY_NOT_FOUND, inv_id=inv_id))
        return Result.success(inv)

    def resolve_inventory(self, inv_id: int, resolution: str) -> Result:
        inv = self.repo.get_inventory(inv_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.CC_INVENTORY_NOT_FOUND, inv_id=inv_id))
        if inv.status == CCInventoryStatus.resolved:
            return Result.failure(AccountError(ErrorCodes.CC_INVENTORY_ALREADY_RESOLVED, inv_id=inv_id))
        return self.repo.update_inventory(inv_id, status=CCInventoryStatus.resolved,
                                           resolved_at=datetime.now(timezone.utc))

    def list_inventories(self, status: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_inventories(status=status))

    # ── UC-CC-07: Disposal/Write-off ──────────────────────────────────

    def create_write_off(self, data: dict) -> Result:
        try:
            item = self._get_item_or_fail(data.get("item_id", 0))
            if item.status == CCDCStatus.disposed:
                return Result.failure(AccountError(ErrorCodes.CC_ITEM_ALREADY_DISPOSED, item_id=item.id))
            wo = CCDCWriteOff(**data)
            result = self.repo.create_write_off(wo)
            if result.is_success():
                self.repo.update_item(item.id, status=CCDCStatus.disposed)
            return result
        except ValidationError as e:
            return Result.failure(e)

    def get_write_off(self, wo_id: int) -> Result:
        wo = self.repo.get_write_off(wo_id)
        if not wo:
            return Result.failure(AccountError(ErrorCodes.CC_WRITE_OFF_NOT_FOUND, wo_id=wo_id))
        return Result.success(wo)

    def list_write_offs(self, item_id: Optional[int] = None) -> Result:
        return Result.success(self.repo.list_write_offs(item_id=item_id))

    # ── UC-CC-08: Spare Parts Management ──────────────────────────────

    def create_spare_part(self, data: dict) -> Result:
        try:
            sp = CCDCSparePart(**data)
            return self.repo.create_spare_part(sp)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

    def get_spare_part(self, sp_id: int) -> Result:
        sp = self.repo.get_spare_part(sp_id)
        if not sp:
            return Result.failure(AccountError(ErrorCodes.CC_SPARE_PART_NOT_FOUND, sp_id=sp_id))
        return Result.success(sp)

    def update_spare_part(self, sp_id: int, **updates) -> Result:
        return self.repo.update_spare_part(sp_id, **updates)

    def delete_spare_part(self, sp_id: int) -> Result:
        return self.repo.delete_spare_part(sp_id)

    def list_spare_parts(self, item_id: Optional[int] = None) -> Result:
        return Result.success(self.repo.list_spare_parts(item_id=item_id))

    # ── UC-CC-09: Reports ─────────────────────────────────────────────

    def report_by_department(self, department_id: int) -> Result:
        items = self.repo.get_items_by_department(department_id)
        total_value = self.repo.get_total_ccdc_value(department_id=department_id)
        return Result.success({
            "department_id": department_id,
            "items": items,
            "total_value": str(total_value),
            "item_count": len(items),
        })

    def report_by_employee(self, employee_id: int) -> Result:
        items = self.repo.get_items_by_employee(employee_id)
        total_value = sum(i.total_cost for i in items)
        return Result.success({
            "employee_id": employee_id,
            "items": items,
            "total_value": str(total_value),
            "item_count": len(items),
        })

    def report_allocation_schedule(self, item_id: int) -> Result:
        lines = self.repo.list_allocation_lines(item_id=item_id)
        return Result.success({
            "item_id": item_id,
            "lines": lines,
            "total_lines": len(lines),
        })

    def report_value_summary(self) -> Result:
        items = self.repo.list_items()
        total_cost = sum(i.total_cost for i in items)
        total_allocated = sum(i.allocated_amount for i in items)
        total_remaining = sum(i.remaining_amount for i in items)
        in_stock = [i for i in items if i.status == CCDCStatus.in_stock]
        in_use = [i for i in items if i.status == CCDCStatus.in_use]
        disposed = [i for i in items if i.status == CCDCStatus.disposed]
        return Result.success({
            "total_items": len(items),
            "total_cost": str(total_cost),
            "total_allocated": str(total_allocated),
            "total_remaining": str(total_remaining),
            "in_stock_count": len(in_stock),
            "in_stock_value": str(sum(i.total_cost for i in in_stock)),
            "in_use_count": len(in_use),
            "in_use_value": str(sum(i.total_cost for i in in_use)),
            "disposed_count": len(disposed),
        })

    def report_inventory_status(self, inv_id: int) -> Result:
        inv = self.repo.get_inventory(inv_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.CC_INVENTORY_NOT_FOUND, inv_id=inv_id))
        surplus = sum(max(Decimal(str(l.difference)), Decimal("0")) for l in inv.lines)
        deficit = sum(abs(min(Decimal(str(l.difference)), Decimal("0"))) for l in inv.lines)
        return Result.success({
            "inventory": inv,
            "surplus_count": surplus,
            "deficit_count": deficit,
        })

    # ── UC-CC-10: Import/Export ───────────────────────────────────────

    def import_items(self, rows: List[dict], filename: str, created_by: Optional[str] = None) -> Result:
        success_count = 0
        error_count = 0
        errors = []
        for idx, row in enumerate(rows):
            try:
                cat = self.repo.get_category_by_code(row.get("category_code", ""))
                if not cat:
                    raise ValidationError(ErrorCodes.CC_CATEGORY_NOT_FOUND, category_code=row.get("category_code"))
                row["category_id"] = cat.id
                item = CCDCItem(**row)
                result = self.repo.create_item(item)
                if result.is_success():
                    success_count += 1
                else:
                    error_count += 1
                    errors.append({"row": idx, "error": str(result.error)})
            except (ValidationError, ValueError) as e:
                error_count += 1
                errors.append({"row": idx, "error": str(e)})

        log = CCDCImportLog(
            filename=filename, total_rows=len(rows),
            success_count=success_count, error_count=error_count,
            errors=errors, created_by=created_by,
        )
        self.repo.create_import_log(log)
        return Result.success({
            "total": len(rows), "success": success_count,
            "errors": error_count, "error_details": errors,
            "import_log_id": log.id,
        })

    def export_items(self, status: Optional[str] = None) -> Result:
        items = self.repo.list_items(status=status)
        rows = []
        for item in items:
            cat = self.repo.get_category(item.category_id)
            cat_code = cat.code if cat else ""
            rows.append({
                "code": item.code, "name": item.name,
                "category_code": cat_code, "category_id": item.category_id,
                "cc_type": item.cc_type.value, "status": item.status.value,
                "quantity": str(item.quantity), "unit": item.unit,
                "unit_price": str(item.unit_price), "total_cost": str(item.total_cost),
                "allocated_amount": str(item.allocated_amount),
                "remaining_amount": str(item.remaining_amount),
                "department_id": item.department_id,
                "location": item.location,
                "purchase_date": item.purchase_date.isoformat() if item.purchase_date else None,
            })
        return Result.success(rows)

    def get_import_logs(self) -> Result:
        return Result.success(self.repo.list_import_logs())

    # ── UC-CC-11: GL Auto-posting (Batch Period Post) ───────────────

    def post_period_allocations(self, period: str) -> Result:
        try:
            self._validate_period_open(period)
        except ValidationError as e:
            return Result.failure(e)

        lines = self.repo.list_allocation_lines(period=period, item_id=None)
        unposted = [l for l in lines if not l.is_posted]
        if not unposted:
            return Result.failure(AccountError(ErrorCodes.CC_NO_DATA, detail=f"No unposted allocation lines for {period}"))

        results = []
        for line in unposted:
            result = self.post_allocation_line(line.id)
            results.append({"line_id": line.id, "result": "success" if result.is_success() else "failed"})
        return Result.success({"period": period, "processed": len(unposted), "results": results})

    # ── UC-CC-12: Dashboard/KPI ──────────────────────────────────────

    def dashboard_summary(self) -> Result:
        items = self.repo.list_items()
        total = len(items)
        in_stock = sum(1 for i in items if i.status == CCDCStatus.in_stock)
        in_use = sum(1 for i in items if i.status == CCDCStatus.in_use)
        disposed = sum(1 for i in items if i.status == CCDCStatus.disposed)
        total_value = sum(i.total_cost for i in items)
        total_allocated = sum(i.allocated_amount for i in items)
        active = [i for i in items if i.status in (CCDCStatus.in_stock, CCDCStatus.in_use)]
        return Result.success({
            "total_items": total,
            "in_stock": in_stock,
            "in_use": in_use,
            "disposed": disposed,
            "total_value": str(total_value),
            "total_allocated": str(total_allocated),
            "allocation_rate": str(round(total_allocated / total_value * 100, 2)) if total_value > 0 else "0",
            "active_items": len(active),
        })
