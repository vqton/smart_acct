from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
import calendar

from domain import (
    InventoryType, MovementType, ValuationMethod,
    CheckMethod, InventoryCheckStatus, BatchStatus, SerialStatus,
    TransferStatus,
    InventoryCategory, Warehouse, InventoryItem, InventoryBatch,
    SerialNumber, InventoryReceipt, InventoryReceiptLine,
    InventoryIssue, InventoryIssueLine, InventoryTransfer,
    InventoryTransferLine, StockCard, InventoryCheck, InventoryCheckLine,
    InventoryAdjustment, InventoryAdjustmentLine,
    Result, ValidationError, AccountError,
)
from domain.inventory import InventoryStatus, AdjustmentType
from domain.i18n import ErrorCodes
from infrastructure.repositories.inventory_repository import InventoryRepository
from infrastructure.models.gl_models import AccountingPeriodModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _period_to_date(period: str) -> date:
    parts = period.split("-")
    y, m = int(parts[0]), int(parts[1])
    if m == 12:
        return date(y, 12, 31)
    return date(y, m, calendar.monthrange(y, m)[1])


class InventoryUseCases:
    def __init__(self, session: Session):
        self.repo = InventoryRepository(session)
        self._session = session

    def _validate_period_open(self, period: str) -> None:
        p = self._session.get(AccountingPeriodModel, period)
        if p and p.is_closed:
            raise ValidationError(ErrorCodes.INV_PERIOD_CLOSED, period=period)

    def _get_item_or_fail(self, item_id: int) -> InventoryItem:
        item = self.repo.get_item(item_id)
        if not item:
            raise ValidationError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id)
        return item

    def _get_warehouse_or_fail(self, wh_id: int) -> Warehouse:
        wh = self.repo.get_warehouse(wh_id)
        if not wh:
            raise ValidationError(ErrorCodes.INV_WAREHOUSE_NOT_FOUND, warehouse_id=wh_id)
        return wh

    # ── UC-INV-01: Category Management ──────────────────────────────

    def create_category(self, **data) -> Result:
        try:
            category = InventoryCategory(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_category(category)

    def get_category(self, category_id: int) -> Result:
        cat = self.repo.get_category(category_id)
        if not cat:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_NOT_FOUND, category_id=category_id))
        return Result.success(cat)

    def list_categories(self, inventory_type: Optional[str] = None,
                        is_active: Optional[bool] = None) -> List[InventoryCategory]:
        return self.repo.list_categories(inventory_type=inventory_type, is_active=is_active)

    def update_category(self, category_id: int, **data) -> Result:
        return self.repo.update_category(category_id, **data)

    def delete_category(self, category_id: int) -> Result:
        return self.repo.delete_category(category_id)

    # ── UC-INV-02: Item Master Data Management ─────────────────────

    def create_item(self, **data) -> Result:
        try:
            item = InventoryItem(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_item(item)

    def get_item(self, item_id: int) -> Result:
        item = self.repo.get_item(item_id)
        if not item:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        return Result.success(item)

    def list_items(self, category_id: Optional[int] = None,
                   inventory_type: Optional[str] = None,
                   status: Optional[str] = None,
                   search: Optional[str] = None,
                   low_stock: bool = False) -> List[InventoryItem]:
        return self.repo.list_items(
            category_id=category_id, inventory_type=inventory_type,
            status=status, search=search, low_stock=low_stock,
        )

    def update_item(self, item_id: int, **data) -> Result:
        return self.repo.update_item(item_id, **data)

    def delete_item(self, item_id: int) -> Result:
        return self.repo.delete_category(item_id)

    # ── UC-INV-03: Warehouse Management ────────────────────────────

    def create_warehouse(self, **data) -> Result:
        try:
            wh = Warehouse(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_warehouse(wh)

    def get_warehouse(self, warehouse_id: int) -> Result:
        wh = self.repo.get_warehouse(warehouse_id)
        if not wh:
            return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_NOT_FOUND, warehouse_id=warehouse_id))
        return Result.success(wh)

    def list_warehouses(self, is_active: Optional[bool] = None) -> List[Warehouse]:
        return self.repo.list_warehouses(is_active=is_active)

    def update_warehouse(self, warehouse_id: int, **data) -> Result:
        return self.repo.update_warehouse(warehouse_id, **data)

    def delete_warehouse(self, warehouse_id: int) -> Result:
        return self.repo.delete_warehouse(warehouse_id)

    # ── UC-INV-04: Goods Receipt ───────────────────────────────────

    def create_receipt(self, **data) -> Result:
        try:
            lines_data = data.pop("lines", [])
            receipt = InventoryReceipt(**data)
            receipt.lines = [InventoryReceiptLine(**l) for l in lines_data]
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        if not receipt.lines:
            return Result.failure(AccountError(ErrorCodes.INV_ZERO_QUANTITY))
        return self.repo.create_receipt(receipt)

    def get_receipt(self, receipt_id: int) -> Result:
        r = self.repo.get_receipt(receipt_id)
        if not r:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        return Result.success(r)

    def list_receipts(self, warehouse_id: Optional[int] = None,
                      date_from: Optional[date] = None, date_to: Optional[date] = None,
                      is_posted: Optional[bool] = None,
                      skip: int = 0, limit: int = 50) -> Tuple[List[InventoryReceipt], int]:
        return self.repo.list_receipts(
            warehouse_id=warehouse_id, date_from=date_from, date_to=date_to,
            is_posted=is_posted, skip=skip, limit=limit,
        )

    def post_receipt(self, receipt_id: int, gl_ref: Optional[str] = None) -> Result:
        receipt = self.repo.get_receipt(receipt_id)
        if not receipt:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        if receipt.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_ALREADY_POSTED, receipt_id=receipt_id))
        for line in receipt.lines:
            self.repo.adjust_stock(line.item_id, line.warehouse_id, line.quantity)
            if line.batch_id:
                self.repo.update_batch_quantity(line.batch_id, line.quantity)
        return self.repo.post_receipt(receipt_id, gl_ref=gl_ref)

    # ── UC-INV-05: Goods Issue ─────────────────────────────────────

    def create_issue(self, **data) -> Result:
        try:
            lines_data = data.pop("lines", [])
            issue = InventoryIssue(**data)
            issue.lines = [InventoryIssueLine(**l) for l in lines_data]
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        if not issue.lines:
            return Result.failure(AccountError(ErrorCodes.INV_ZERO_QUANTITY))
        return self.repo.create_issue(issue)

    def get_issue(self, issue_id: int) -> Result:
        r = self.repo.get_issue(issue_id)
        if not r:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_NOT_FOUND, issue_id=issue_id))
        return Result.success(r)

    def list_issues(self, warehouse_id: Optional[int] = None,
                    date_from: Optional[date] = None, date_to: Optional[date] = None,
                    is_posted: Optional[bool] = None,
                    skip: int = 0, limit: int = 50) -> Tuple[List[InventoryIssue], int]:
        return self.repo.list_issues(
            warehouse_id=warehouse_id, date_from=date_from, date_to=date_to,
            is_posted=is_posted, skip=skip, limit=limit,
        )

    def post_issue(self, issue_id: int, gl_ref: Optional[str] = None) -> Result:
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_NOT_FOUND, issue_id=issue_id))
        if issue.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_ALREADY_POSTED, issue_id=issue_id))
        wh = self.repo.get_warehouse(issue.warehouse_id)
        for line in issue.lines:
            item = self.repo.get_item(line.item_id)
            if not item:
                continue
            if item.current_stock < line.quantity and (not wh or not wh.allow_negative_stock):
                return Result.failure(AccountError(ErrorCodes.INV_INSUFFICIENT_STOCK,
                                                    item_id=line.item_id,
                                                    available=item.current_stock,
                                                    requested=line.quantity))
            self.repo.adjust_stock(line.item_id, line.warehouse_id, -line.quantity)
            if line.batch_id:
                self.repo.update_batch_quantity(line.batch_id, -line.quantity)
        return self.repo.post_issue(issue_id, gl_ref=gl_ref)

    # ── UC-INV-06: Inventory Transfer ──────────────────────────────

    def create_transfer(self, **data) -> Result:
        try:
            lines_data = data.pop("lines", [])
            transfer = InventoryTransfer(**data)
            transfer.lines = [InventoryTransferLine(**l) for l in lines_data]
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        if not transfer.lines:
            return Result.failure(AccountError(ErrorCodes.INV_ZERO_QUANTITY))
        return self.repo.create_transfer(transfer)

    def get_transfer(self, transfer_id: int) -> Result:
        t = self.repo.get_transfer(transfer_id)
        if not t:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        return Result.success(t)

    def list_transfers(self, from_warehouse_id: Optional[int] = None,
                       to_warehouse_id: Optional[int] = None,
                       status: Optional[str] = None,
                       skip: int = 0, limit: int = 50) -> Tuple[List[InventoryTransfer], int]:
        return self.repo.list_transfers(
            from_warehouse_id=from_warehouse_id, to_warehouse_id=to_warehouse_id,
            status=status, skip=skip, limit=limit,
        )

    def update_transfer_status(self, transfer_id: int, status: str) -> Result:
        try:
            s = TransferStatus(status)
        except (ValueError, ValidationError):
            return Result.failure(AccountError(ErrorCodes.STATE_TRANSITION, status=status))
        return self.repo.update_transfer_status(transfer_id, s)

    def post_transfer(self, transfer_id: int, gl_ref: Optional[str] = None) -> Result:
        transfer = self.repo.get_transfer(transfer_id)
        if not transfer:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        if transfer.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_ALREADY_POSTED, transfer_id=transfer_id))
        from_wh = self.repo.get_warehouse(transfer.from_warehouse_id)
        for line in transfer.lines:
            item = self.repo.get_item(line.item_id)
            if not item:
                continue
            if item.current_stock < line.quantity and (not from_wh or not from_wh.allow_negative_stock):
                return Result.failure(AccountError(ErrorCodes.INV_INSUFFICIENT_STOCK,
                                                    item_id=line.item_id,
                                                    available=item.current_stock,
                                                    requested=line.quantity))
            self.repo.adjust_stock(line.item_id, transfer.from_warehouse_id, -line.quantity)
            self.repo.adjust_stock(line.item_id, transfer.to_warehouse_id, line.quantity)
        return self.repo.post_transfer(transfer_id, gl_ref=gl_ref)

    # ── UC-INV-07: Batch Management ────────────────────────────────

    def create_batch(self, **data) -> Result:
        try:
            batch = InventoryBatch(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_batch(batch)

    def get_batch(self, batch_id: int) -> Result:
        b = self.repo.get_batch(batch_id)
        if not b:
            return Result.failure(AccountError(ErrorCodes.INV_BATCH_NOT_FOUND, batch_id=batch_id))
        return Result.success(b)

    def list_batches(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                     status: Optional[str] = None) -> List[InventoryBatch]:
        return self.repo.list_batches(item_id=item_id, warehouse_id=warehouse_id, status=status)

    def create_serial(self, **data) -> Result:
        try:
            serial = SerialNumber(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_serial(serial)

    def get_serial(self, serial_id: int) -> Result:
        s = self.repo.get_serial(serial_id)
        if not s:
            return Result.failure(AccountError(ErrorCodes.INV_SERIAL_NOT_FOUND, serial_id=serial_id))
        return Result.success(s)

    def list_serials(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                     status: Optional[str] = None) -> List[SerialNumber]:
        return self.repo.list_serials(item_id=item_id, warehouse_id=warehouse_id, status=status)

    # ── UC-INV-08: Stock Card / Balance ────────────────────────────

    def get_stock_card(self, item_id: int, warehouse_id: int, period: str) -> Result:
        card = self.repo.get_stock_card(item_id, warehouse_id, period)
        if not card:
            return Result.success(self._build_stock_card(item_id, warehouse_id, period))
        return Result.success(card)

    def list_stock_cards(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                         period_from: Optional[str] = None, period_to: Optional[str] = None) -> List[StockCard]:
        return self.repo.list_stock_cards(
            item_id=item_id, warehouse_id=warehouse_id,
            period_from=period_from, period_to=period_to,
        )

    def _build_stock_card(self, item_id: int, warehouse_id: int, period: str) -> StockCard:
        item = self.repo.get_item(item_id)
        if not item:
            raise ValidationError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id)
        return StockCard(
            item_id=item_id, warehouse_id=warehouse_id, period=period,
            opening_quantity=item.current_stock,
            opening_value=_vnd(item.current_stock * item.cost_price),
            unit_cost=item.cost_price,
        )

    def get_inventory_balance(self, item_id: int, warehouse_id: Optional[int] = None) -> Result:
        item = self.repo.get_item(item_id)
        if not item:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        return Result.success({
            "item_id": item_id,
            "item_code": item.code,
            "item_name": item.name,
            "current_stock": item.current_stock,
            "reserved_stock": item.reserved_stock,
            "available_stock": item.available_stock,
            "cost_price": item.cost_price,
            "stock_value": _vnd(item.current_stock * item.cost_price),
        })

    # ── UC-INV-09: Physical Inventory / Stocktake ──────────────────

    def create_check(self, **data) -> Result:
        try:
            lines_data = data.pop("lines", [])
            check = InventoryCheck(**data)
            check.lines = [InventoryCheckLine(**l) for l in lines_data]
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        if not check.lines:
            return Result.failure(AccountError(ErrorCodes.INV_ZERO_QUANTITY))
        return self.repo.create_check(check)

    def get_check(self, check_id: int) -> Result:
        c = self.repo.get_check(check_id)
        if not c:
            return Result.failure(AccountError(ErrorCodes.INV_CHECK_NOT_FOUND, check_id=check_id))
        return Result.success(c)

    def list_checks(self, warehouse_id: Optional[int] = None, status: Optional[str] = None,
                    skip: int = 0, limit: int = 50) -> Tuple[List[InventoryCheck], int]:
        return self.repo.list_checks(warehouse_id=warehouse_id, status=status, skip=skip, limit=limit)

    def approve_check(self, check_id: int, approved_by: Optional[str] = None) -> Result:
        return self.repo.update_check_status(check_id, InventoryCheckStatus.APPROVED, approved_by=approved_by)

    def update_check_status(self, check_id: int, status: str) -> Result:
        try:
            s = InventoryCheckStatus(status)
        except (ValueError, ValidationError):
            return Result.failure(AccountError(ErrorCodes.STATE_TRANSITION, status=status))
        return self.repo.update_check_status(check_id, s)

    # ── UC-INV-10: Inventory Adjustment ────────────────────────────

    def create_adjustment(self, **data) -> Result:
        try:
            lines_data = data.pop("lines", [])
            adj = InventoryAdjustment(**data)
            adj.lines = [InventoryAdjustmentLine(**l) for l in lines_data]
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        if not adj.lines:
            return Result.failure(AccountError(ErrorCodes.INV_ZERO_QUANTITY))
        return self.repo.create_adjustment(adj)

    def get_adjustment(self, adjustment_id: int) -> Result:
        a = self.repo.get_adjustment(adjustment_id)
        if not a:
            return Result.failure(AccountError(ErrorCodes.INV_ADJ_NOT_FOUND, adjustment_id=adjustment_id))
        return Result.success(a)

    def list_adjustments(self, warehouse_id: Optional[int] = None,
                         adjustment_type: Optional[str] = None,
                         skip: int = 0, limit: int = 50) -> Tuple[List[InventoryAdjustment], int]:
        return self.repo.list_adjustments(
            warehouse_id=warehouse_id, adjustment_type=adjustment_type,
            skip=skip, limit=limit,
        )

    def post_adjustment(self, adjustment_id: int, gl_ref: Optional[str] = None) -> Result:
        adj = self.repo.get_adjustment(adjustment_id)
        if not adj:
            return Result.failure(AccountError(ErrorCodes.INV_ADJ_NOT_FOUND, adjustment_id=adjustment_id))
        if adj.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_ADJ_ALREADY_POSTED, adjustment_id=adjustment_id))
        wh = self.repo.get_warehouse(adj.warehouse_id)
        for line in adj.lines:
            if line.quantity_change < 0 and (not wh or not wh.allow_negative_stock):
                item = self.repo.get_item(line.item_id)
                if item and item.current_stock < abs(line.quantity_change):
                    return Result.failure(AccountError(ErrorCodes.INV_INSUFFICIENT_STOCK,
                                                        item_id=line.item_id,
                                                        available=item.current_stock,
                                                        requested=abs(line.quantity_change)))
            self.repo.adjust_stock(line.item_id, line.warehouse_id, line.quantity_change)
        return self.repo.post_adjustment(adjustment_id, gl_ref=gl_ref)

    # ── UC-INV-11: Inventory Valuation ─────────────────────────────

    def calculate_moving_average(self, item_id: int, new_quantity: Decimal, new_unit_price: Decimal) -> Result:
        item = self.repo.get_item(item_id)
        if not item:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        total_qty = item.current_stock + new_quantity
        if total_qty <= 0:
            return Result.success({"unit_cost": item.cost_price})
        total_value = (item.current_stock * item.cost_price) + (new_quantity * new_unit_price)
        new_cost = _vnd(total_value / total_qty)
        return Result.success({"unit_cost": new_cost, "total_quantity": total_qty, "total_value": _vnd(total_value)})

    def revalue_item(self, item_id: int, new_unit_price: Decimal) -> Result:
        item = self.repo.get_item(item_id)
        if not item:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        return self.repo.update_item(item_id, cost_price=new_unit_price)

    # ── UC-INV-12: GL Auto-Posting ─────────────────────────────────

    def get_gl_accounts_for_item(self, item_id: int) -> Result:
        accounts = self.repo.get_item_gl_accounts(item_id)
        if not accounts:
            return Result.failure(AccountError(ErrorCodes.INV_GL_ACCOUNT_MISSING, item_id=item_id))
        return Result.success(accounts)

    def build_receipt_gl_entries(self, receipt_id: int) -> Result:
        receipt = self.repo.get_receipt(receipt_id)
        if not receipt:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        entries = []
        for line in receipt.lines:
            accounts = self.repo.get_item_gl_accounts(line.item_id)
            if not accounts:
                continue
            entries.append({
                "account_code": accounts.get("gl_inventory_account", "152"),
                "debit": _vnd(line.total_amount),
                "credit": Decimal("0"),
                "description": f"Nhập kho {line.item_id} PN {receipt.receipt_code}",
            })
            entries.append({
                "account_code": accounts.get("gl_receipt_account", "331"),
                "debit": Decimal("0"),
                "credit": _vnd(line.total_amount),
                "description": f"Phải trả NCC {line.item_id} PN {receipt.receipt_code}",
            })
        return Result.success(entries)

    def build_issue_gl_entries(self, issue_id: int) -> Result:
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_NOT_FOUND, issue_id=issue_id))
        entries = []
        for line in issue.lines:
            accounts = self.repo.get_item_gl_accounts(line.item_id)
            if not accounts:
                continue
            entries.append({
                "account_code": accounts.get("gl_cost_of_sales", "632"),
                "debit": _vnd(line.cost_amount or (line.quantity * line.cost_price)),
                "credit": Decimal("0"),
                "description": f"Giá vốn XK {line.item_id} PX {issue.issue_code}",
            })
            entries.append({
                "account_code": accounts.get("gl_inventory_account", "152"),
                "debit": Decimal("0"),
                "credit": _vnd(line.cost_amount or (line.quantity * line.cost_price)),
                "description": f"Xuất kho {line.item_id} PX {issue.issue_code}",
            })
        return Result.success(entries)

    # ── UC-INV-13: Reports ─────────────────────────────────────────

    def get_inventory_report(self, warehouse_id: Optional[int] = None,
                             category_id: Optional[int] = None) -> Result:
        items = self.repo.list_items(category_id=category_id)
        report = []
        for item in items:
            if warehouse_id and item.default_warehouse_id != warehouse_id:
                continue
            report.append({
                "item_id": item.id,
                "item_code": item.code,
                "item_name": item.name,
                "unit": item.unit,
                "current_stock": item.current_stock,
                "available_stock": item.available_stock,
                "cost_price": item.cost_price,
                "stock_value": _vnd(item.current_stock * item.cost_price),
                "min_stock": item.min_stock,
                "max_stock": item.max_stock,
                "status": item.status.value,
            })
        return Result.success({"items": report, "total_items": len(report)})

    def get_low_stock_report(self) -> Result:
        items = self.repo.list_items(low_stock=True)
        report = [{
            "item_id": i.id, "item_code": i.code, "item_name": i.name,
            "current_stock": i.current_stock, "reorder_point": i.reorder_point,
        } for i in items]
        return Result.success({"items": report, "total": len(report)})

    def get_stock_movement_report(self, item_id: int, date_from: date, date_to: date) -> Result:
        receipts, _ = self.repo.list_receipts(date_from=date_from, date_to=date_to, limit=9999)
        issues, _ = self.repo.list_issues(date_from=date_from, date_to=date_to, limit=9999)
        movements = []
        for r in receipts:
            for line in r.lines:
                if line.item_id == item_id:
                    movements.append({
                        "date": r.receipt_date.isoformat(),
                        "type": "receipt",
                        "ref": r.receipt_code,
                        "quantity": line.quantity,
                        "unit_price": line.unit_price,
                        "total_amount": line.total_amount,
                    })
        for i in issues:
            for line in i.lines:
                if line.item_id == item_id:
                    movements.append({
                        "date": i.issue_date.isoformat(),
                        "type": "issue",
                        "ref": i.issue_code,
                        "quantity": -line.quantity,
                        "unit_price": line.unit_price,
                        "total_amount": line.total_amount,
                    })
        movements.sort(key=lambda x: x["date"])
        return Result.success({"movements": movements, "total": len(movements)})

    # ── UC-INV-14: Import/Export ───────────────────────────────────

    def import_items_from_csv(self, rows: List[Dict[str, Any]]) -> Result:
        imported = 0
        errors = []
        for i, row in enumerate(rows):
            try:
                cat = self.repo.get_category_by_code(row.get("category_code", ""))
                if not cat:
                    errors.append({"row": i, "error": "Category not found"})
                    continue
                item = InventoryItem(
                    code=row["code"], name=row["name"],
                    category_id=cat.id,
                    unit=row.get("unit", "cái"),
                    cost_price=Decimal(str(row.get("cost_price", 0))),
                    unit_price=Decimal(str(row.get("unit_price", 0))),
                    selling_price=Decimal(str(row.get("selling_price", 0))),
                    current_stock=Decimal(str(row.get("current_stock", 0))),
                )
                result = self.repo.create_item(item)
                if result.is_failure():
                    errors.append({"row": i, "error": str(result.error)})
                else:
                    imported += 1
            except Exception as e:
                errors.append({"row": i, "error": str(e)})
        return Result.success({"imported": imported, "errors": errors})

    def export_items(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        items = self.repo.list_items(category_id=category_id)
        return [{
            "code": i.code, "name": i.name, "unit": i.unit,
            "cost_price": str(i.cost_price), "selling_price": str(i.selling_price),
            "current_stock": str(i.current_stock),
            "inventory_type": i.inventory_type.value,
        } for i in items]

    # ── UC-INV-15: Dashboard / KPI ─────────────────────────────────

    def get_dashboard(self) -> dict:
        return self.repo.get_dashboard()
