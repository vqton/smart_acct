from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from domain import (
    CCDCType, AllocationMethod, CCDCStatus, AllocationStatus,
    TransactionType, CCInventoryStatus, ResponsibilityType,
    CCategory, CCDCItem, CCDCAllocation, CCDCAllocationLine,
    CCDCTransaction, CCDCTransfer, CCDCInventory, CCDCInventoryLine,
    CCDCWriteOff, CCDCSparePart, CCDCImportLog,
    Result, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.cc_models import (
    CCategoryModel, CCDCItemModel, CCDCAllocationModel, CCDCAllocationLineModel,
    CCDCTransactionModel, CCDCTransferModel, CCDCInventoryModel,
    CCDCInventoryLineModel, CCDCWriteOffModel, CCDCSparePartModel,
    CCDCImportLogModel,
    CCDCTypeDB, AllocationMethodDB, CCDCStatusDB, AllocationStatusDB as CCAllocStatusDB,
    TransactionTypeDB, CCInventoryStatusDB, ResponsibilityTypeDB,
)


class CCRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Category ──────────────────────────────────────────────────────

    def _cat_to_domain(self, m: CCategoryModel) -> CCategory:
        d = CCategory(
            code=m.code, name=m.name, description=m.description,
            default_allocation_method=AllocationMethod(m.default_allocation_method.value),
            default_useful_life_months=m.default_useful_life_months,
            gl_asset_account=m.gl_asset_account,
            gl_alloc_account=m.gl_alloc_account,
            gl_expense_account=m.gl_expense_account,
            is_active=m.is_active,
            created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _cat_to_model(self, d: CCategory) -> CCategoryModel:
        return CCategoryModel(
            code=d.code, name=d.name, description=d.description,
            default_allocation_method=AllocationMethodDB(d.default_allocation_method.value)
                if isinstance(d.default_allocation_method, AllocationMethod)
                else AllocationMethodDB(d.default_allocation_method),
            default_useful_life_months=d.default_useful_life_months,
            gl_asset_account=d.gl_asset_account,
            gl_alloc_account=d.gl_alloc_account,
            gl_expense_account=d.gl_expense_account,
            is_active=d.is_active,
        )

    def create_category(self, category: CCategory) -> Result:
        existing = self.session.execute(
            select(CCategoryModel).where(CCategoryModel.code == category.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.CC_CATEGORY_CODE_DUPLICATE, code=category.code))
        model = self._cat_to_model(category)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cat_to_domain(model))

    def get_category(self, category_id: int) -> Optional[CCategory]:
        m = self.session.get(CCategoryModel, category_id)
        return self._cat_to_domain(m) if m else None

    def get_category_by_code(self, code: str) -> Optional[CCategory]:
        m = self.session.execute(
            select(CCategoryModel).where(CCategoryModel.code == code)
        ).scalar_one_or_none()
        return self._cat_to_domain(m) if m else None

    def update_category(self, category_id: int, **updates) -> Result:
        m = self.session.get(CCategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_CATEGORY_NOT_FOUND, category_id=category_id))
        if "code" in updates:
            dup = self.session.execute(
                select(CCategoryModel).where(
                    CCategoryModel.code == updates["code"],
                    CCategoryModel.id != category_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.CC_CATEGORY_CODE_DUPLICATE, code=updates["code"]))
        for key, val in updates.items():
            if key == "default_allocation_method" and isinstance(val, AllocationMethod):
                setattr(m, "default_allocation_method", AllocationMethodDB(val.value))
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._cat_to_domain(m))

    def delete_category(self, category_id: int) -> Result:
        m = self.session.get(CCategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_CATEGORY_NOT_FOUND, category_id=category_id))
        cnt = self.session.execute(
            select(func.count(CCDCItemModel.id)).where(CCDCItemModel.category_id == category_id)
        ).scalar() or 0
        if cnt > 0:
            return Result.failure(AccountError(ErrorCodes.CC_CATEGORY_HAS_ITEMS, category_id=category_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success(None)

    def list_categories(self) -> List[CCategory]:
        stmt = select(CCategoryModel).order_by(CCategoryModel.code)
        return [self._cat_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Item ──────────────────────────────────────────────────────────

    def _item_to_domain(self, m: CCDCItemModel) -> CCDCItem:
        d = CCDCItem(
            code=m.code, name=m.name, category_id=m.category_id,
            cc_type=CCDCType(m.cc_type.value) if isinstance(m.cc_type, CCDCTypeDB) else CCDCType(m.cc_type),
            status=CCDCStatus(m.status.value) if isinstance(m.status, CCDCStatusDB) else CCDCStatus(m.status),
            allocation_method=AllocationMethod(m.allocation_method.value) if isinstance(m.allocation_method, AllocationMethodDB) else AllocationMethod(m.allocation_method),
            quantity=m.quantity, unit=m.unit, unit_price=m.unit_price,
            total_cost=m.total_cost, allocated_amount=m.allocated_amount,
            remaining_amount=m.remaining_amount,
            allocation_status=AllocationStatus(m.allocation_status.value) if isinstance(m.allocation_status, CCAllocStatusDB) else AllocationStatus(m.allocation_status),
            useful_life_months=m.useful_life_months,
            allocation_start_period=m.allocation_start_period,
            department_id=m.department_id, employee_id=m.employee_id,
            location=m.location, supplier=m.supplier, invoice_ref=m.invoice_ref,
            purchase_date=m.purchase_date, in_use_date=m.in_use_date,
            warranty_expiry=m.warranty_expiry, description=m.description,
            notes=m.notes,
            responsibility_type=ResponsibilityType(m.responsibility_type.value) if isinstance(m.responsibility_type, ResponsibilityTypeDB) else ResponsibilityType(m.responsibility_type),
            responsible_person=m.responsible_person,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _item_to_model(self, d: CCDCItem) -> CCDCItemModel:
        return CCDCItemModel(
            code=d.code, name=d.name, category_id=d.category_id,
            cc_type=CCDCTypeDB(d.cc_type.value) if isinstance(d.cc_type, CCDCType) else CCDCTypeDB(d.cc_type),
            status=CCDCStatusDB(d.status.value) if isinstance(d.status, CCDCStatus) else CCDCStatusDB(d.status),
            allocation_method=AllocationMethodDB(d.allocation_method.value) if isinstance(d.allocation_method, AllocationMethod) else AllocationMethodDB(d.allocation_method),
            quantity=d.quantity, unit=d.unit, unit_price=d.unit_price,
            total_cost=d.total_cost, allocated_amount=d.allocated_amount,
            remaining_amount=d.remaining_amount,
            allocation_status=CCAllocStatusDB(d.allocation_status.value) if isinstance(d.allocation_status, AllocationStatus) else CCAllocStatusDB(d.allocation_status),
            useful_life_months=d.useful_life_months,
            allocation_start_period=d.allocation_start_period,
            department_id=d.department_id, employee_id=d.employee_id,
            location=d.location, supplier=d.supplier, invoice_ref=d.invoice_ref,
            purchase_date=d.purchase_date, in_use_date=d.in_use_date,
            warranty_expiry=d.warranty_expiry, description=d.description,
            notes=d.notes,
            responsibility_type=ResponsibilityTypeDB(d.responsibility_type.value) if isinstance(d.responsibility_type, ResponsibilityType) else ResponsibilityTypeDB(d.responsibility_type),
            responsible_person=d.responsible_person,
            created_by=d.created_by,
        )

    def create_item(self, item: CCDCItem) -> Result:
        existing = self.session.execute(
            select(CCDCItemModel).where(CCDCItemModel.code == item.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.CC_ITEM_CODE_DUPLICATE, code=item.code))
        model = self._item_to_model(item)
        self.session.add(model)
        self.session.flush()
        created = self._item_to_domain(model)
        return Result.success(created)

    def get_item(self, item_id: int) -> Optional[CCDCItem]:
        m = self.session.get(CCDCItemModel, item_id)
        return self._item_to_domain(m) if m else None

    def get_item_by_code(self, code: str) -> Optional[CCDCItem]:
        m = self.session.execute(
            select(CCDCItemModel).where(CCDCItemModel.code == code)
        ).scalar_one_or_none()
        return self._item_to_domain(m) if m else None

    def update_item(self, item_id: int, **updates) -> Result:
        m = self.session.get(CCDCItemModel, item_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_ITEM_NOT_FOUND, item_id=item_id))
        if "code" in updates:
            dup = self.session.execute(
                select(CCDCItemModel).where(
                    CCDCItemModel.code == updates["code"],
                    CCDCItemModel.id != item_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.CC_ITEM_CODE_DUPLICATE, code=updates["code"]))
        for key, val in updates.items():
            if key == "cc_type" and isinstance(val, CCDCType):
                setattr(m, "cc_type", CCDCTypeDB(val.value))
            elif key == "status" and isinstance(val, CCDCStatus):
                setattr(m, "status", CCDCStatusDB(val.value))
            elif key == "allocation_method" and isinstance(val, AllocationMethod):
                setattr(m, "allocation_method", AllocationMethodDB(val.value))
            elif key == "allocation_status" and isinstance(val, AllocationStatus):
                setattr(m, "allocation_status", CCAllocStatusDB(val.value))
            elif key == "responsibility_type" and isinstance(val, ResponsibilityType):
                setattr(m, "responsibility_type", ResponsibilityTypeDB(val.value))
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._item_to_domain(m))

    def delete_item(self, item_id: int) -> Result:
        m = self.session.get(CCDCItemModel, item_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_ITEM_NOT_FOUND, item_id=item_id))
        if m.status != CCDCStatusDB.DISPOSED and m.status != CCDCStatusDB.IN_STOCK:
            return Result.failure(AccountError(ErrorCodes.CC_CANNOT_DELETE, item_id=item_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success(None)

    def list_items(self, category_id: Optional[int] = None, status: Optional[str] = None,
                   department_id: Optional[int] = None, cc_type: Optional[str] = None) -> List[CCDCItem]:
        stmt = select(CCDCItemModel).order_by(CCDCItemModel.code)
        if category_id:
            stmt = stmt.where(CCDCItemModel.category_id == category_id)
        if status:
            stmt = stmt.where(CCDCItemModel.status == CCDCStatusDB(status))
        if department_id:
            stmt = stmt.where(CCDCItemModel.department_id == department_id)
        if cc_type:
            stmt = stmt.where(CCDCItemModel.cc_type == CCDCTypeDB(cc_type))
        return [self._item_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Allocation ────────────────────────────────────────────────────

    def _alloc_to_domain(self, m: CCDCAllocationModel) -> CCDCAllocation:
        d = CCDCAllocation(
            item_id=m.item_id,
            allocation_method=AllocationMethod(m.allocation_method.value) if isinstance(m.allocation_method, AllocationMethodDB) else AllocationMethod(m.allocation_method),
            total_amount=m.total_amount, allocated_amount=m.allocated_amount,
            remaining_amount=m.remaining_amount,
            start_period=m.start_period, end_period=m.end_period,
            total_periods=m.total_periods, amount_per_period=m.amount_per_period,
            status=AllocationStatus(m.status.value) if isinstance(m.status, CCAllocStatusDB) else AllocationStatus(m.status),
            gl_account_credit=m.gl_account_credit, gl_account_debit=m.gl_account_debit,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _alloc_to_model(self, d: CCDCAllocation) -> CCDCAllocationModel:
        return CCDCAllocationModel(
            item_id=d.item_id,
            allocation_method=AllocationMethodDB(d.allocation_method.value) if isinstance(d.allocation_method, AllocationMethod) else AllocationMethodDB(d.allocation_method),
            total_amount=d.total_amount, allocated_amount=d.allocated_amount,
            remaining_amount=d.remaining_amount,
            start_period=d.start_period, end_period=d.end_period,
            total_periods=d.total_periods, amount_per_period=d.amount_per_period,
            status=CCAllocStatusDB(d.status.value) if isinstance(d.status, AllocationStatus) else CCAllocStatusDB(d.status),
            gl_account_credit=d.gl_account_credit, gl_account_debit=d.gl_account_debit,
            created_by=d.created_by,
        )

    def create_allocation(self, alloc: CCDCAllocation) -> Result:
        model = self._alloc_to_model(alloc)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._alloc_to_domain(model))

    def get_allocation(self, alloc_id: int) -> Optional[CCDCAllocation]:
        m = self.session.get(CCDCAllocationModel, alloc_id)
        return self._alloc_to_domain(m) if m else None

    def update_allocation(self, alloc_id: int, **updates) -> Result:
        m = self.session.get(CCDCAllocationModel, alloc_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_NOT_FOUND, alloc_id=alloc_id))
        for key, val in updates.items():
            if key == "status" and isinstance(val, AllocationStatus):
                setattr(m, "status", CCAllocStatusDB(val.value))
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._alloc_to_domain(m))

    def list_allocations(self, item_id: Optional[int] = None) -> List[CCDCAllocation]:
        stmt = select(CCDCAllocationModel).order_by(CCDCAllocationModel.start_period)
        if item_id:
            stmt = stmt.where(CCDCAllocationModel.item_id == item_id)
        return [self._alloc_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Allocation Line ───────────────────────────────────────────────

    def _alloc_line_to_domain(self, m: CCDCAllocationLineModel) -> CCDCAllocationLine:
        d = CCDCAllocationLine(
            allocation_id=m.allocation_id, item_id=m.item_id, period=m.period,
            planned_amount=m.planned_amount, actual_amount=m.actual_amount,
            is_posted=m.is_posted, posted_at=m.posted_at,
            gl_journal_ref=m.gl_journal_ref, notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _alloc_line_to_model(self, d: CCDCAllocationLine) -> CCDCAllocationLineModel:
        return CCDCAllocationLineModel(
            allocation_id=d.allocation_id, item_id=d.item_id, period=d.period,
            planned_amount=d.planned_amount, actual_amount=d.actual_amount,
            is_posted=d.is_posted, posted_at=d.posted_at,
            gl_journal_ref=d.gl_journal_ref, notes=d.notes,
        )

    def create_allocation_line(self, line: CCDCAllocationLine) -> Result:
        model = self._alloc_line_to_model(line)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._alloc_line_to_domain(model))

    def get_allocation_line(self, line_id: int) -> Optional[CCDCAllocationLine]:
        m = self.session.get(CCDCAllocationLineModel, line_id)
        return self._alloc_line_to_domain(m) if m else None

    def update_allocation_line(self, line_id: int, **updates) -> Result:
        m = self.session.get(CCDCAllocationLineModel, line_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_ALLOCATION_LINE_NOT_FOUND, line_id=line_id))
        for key, val in updates.items():
            setattr(m, key, val)
        self.session.flush()
        return Result.success(self._alloc_line_to_domain(m))

    def list_allocation_lines(self, allocation_id: Optional[int] = None,
                              item_id: Optional[int] = None,
                              period: Optional[str] = None) -> List[CCDCAllocationLine]:
        stmt = select(CCDCAllocationLineModel).order_by(CCDCAllocationLineModel.period)
        if allocation_id:
            stmt = stmt.where(CCDCAllocationLineModel.allocation_id == allocation_id)
        if item_id:
            stmt = stmt.where(CCDCAllocationLineModel.item_id == item_id)
        if period:
            stmt = stmt.where(CCDCAllocationLineModel.period == period)
        return [self._alloc_line_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Transaction ───────────────────────────────────────────────────

    def _txn_to_domain(self, m: CCDCTransactionModel) -> CCDCTransaction:
        d = CCDCTransaction(
            item_id=m.item_id,
            transaction_type=TransactionType(m.transaction_type.value) if isinstance(m.transaction_type, TransactionTypeDB) else TransactionType(m.transaction_type),
            quantity=m.quantity, unit_price=m.unit_price, total_amount=m.total_amount,
            transaction_date=m.transaction_date, period=m.period,
            department_id=m.department_id, employee_id=m.employee_id,
            reference_doc=m.reference_doc, description=m.description,
            created_by=m.created_by, created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _txn_to_model(self, d: CCDCTransaction) -> CCDCTransactionModel:
        return CCDCTransactionModel(
            item_id=d.item_id,
            transaction_type=TransactionTypeDB(d.transaction_type.value) if isinstance(d.transaction_type, TransactionType) else TransactionTypeDB(d.transaction_type),
            quantity=d.quantity, unit_price=d.unit_price, total_amount=d.total_amount,
            transaction_date=d.transaction_date, period=d.period,
            department_id=d.department_id, employee_id=d.employee_id,
            reference_doc=d.reference_doc, description=d.description,
            created_by=d.created_by,
        )

    def create_transaction(self, txn: CCDCTransaction) -> Result:
        model = self._txn_to_model(txn)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._txn_to_domain(model))

    def get_transaction(self, txn_id: int) -> Optional[CCDCTransaction]:
        m = self.session.get(CCDCTransactionModel, txn_id)
        return self._txn_to_domain(m) if m else None

    def list_transactions(self, item_id: Optional[int] = None,
                          period: Optional[str] = None,
                          transaction_type: Optional[str] = None) -> List[CCDCTransaction]:
        stmt = select(CCDCTransactionModel).order_by(CCDCTransactionModel.transaction_date.desc())
        if item_id:
            stmt = stmt.where(CCDCTransactionModel.item_id == item_id)
        if period:
            stmt = stmt.where(CCDCTransactionModel.period == period)
        if transaction_type:
            stmt = stmt.where(CCDCTransactionModel.transaction_type == TransactionTypeDB(transaction_type))
        return [self._txn_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Transfer ──────────────────────────────────────────────────────

    def _transfer_to_domain(self, m: CCDCTransferModel) -> CCDCTransfer:
        d = CCDCTransfer(
            item_id=m.item_id,
            from_department_id=m.from_department_id, to_department_id=m.to_department_id,
            from_employee_id=m.from_employee_id, to_employee_id=m.to_employee_id,
            from_location=m.from_location, to_location=m.to_location,
            quantity=m.quantity, transfer_date=m.transfer_date,
            reason=m.reason, created_by=m.created_by, created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _transfer_to_model(self, d: CCDCTransfer) -> CCDCTransferModel:
        return CCDCTransferModel(
            item_id=d.item_id,
            from_department_id=d.from_department_id, to_department_id=d.to_department_id,
            from_employee_id=d.from_employee_id, to_employee_id=d.to_employee_id,
            from_location=d.from_location, to_location=d.to_location,
            quantity=d.quantity, transfer_date=d.transfer_date,
            reason=d.reason, created_by=d.created_by,
        )

    def create_transfer(self, transfer: CCDCTransfer) -> Result:
        model = self._transfer_to_model(transfer)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._transfer_to_domain(model))

    def get_transfer(self, transfer_id: int) -> Optional[CCDCTransfer]:
        m = self.session.get(CCDCTransferModel, transfer_id)
        return self._transfer_to_domain(m) if m else None

    def list_transfers(self, item_id: Optional[int] = None) -> List[CCDCTransfer]:
        stmt = select(CCDCTransferModel).order_by(CCDCTransferModel.transfer_date.desc())
        if item_id:
            stmt = stmt.where(CCDCTransferModel.item_id == item_id)
        return [self._transfer_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Inventory ─────────────────────────────────────────────────────

    def _inv_to_domain(self, m: CCDCInventoryModel) -> CCDCInventory:
        d = CCDCInventory(
            inventory_date=m.inventory_date, department_id=m.department_id,
            notes=m.notes,
            status=CCInventoryStatus(m.status.value) if isinstance(m.status, CCInventoryStatusDB) else CCInventoryStatus(m.status),
            created_by=m.created_by, created_at=m.created_at,
            resolved_at=m.resolved_at,
            lines=[self._inv_line_to_domain(l) for l in (m.lines or [])],
        )
        d.id = m.id
        return d

    def _inv_to_model(self, d: CCDCInventory) -> CCDCInventoryModel:
        return CCDCInventoryModel(
            inventory_date=d.inventory_date, department_id=d.department_id,
            notes=d.notes,
            status=CCInventoryStatusDB(d.status.value) if isinstance(d.status, CCInventoryStatus) else CCInventoryStatusDB(d.status),
            created_by=d.created_by,
        )

    def _inv_line_to_domain(self, m: CCDCInventoryLineModel) -> CCDCInventoryLine:
        d = CCDCInventoryLine(
            inventory_id=m.inventory_id, item_id=m.item_id,
            book_quantity=m.book_quantity, physical_quantity=m.physical_quantity,
            difference=m.difference, unit_price=m.unit_price,
            difference_amount=m.difference_amount,
            reason=m.reason, resolution=m.resolution,
        )
        d.id = m.id
        return d

    def _inv_line_to_model(self, d: CCDCInventoryLine) -> CCDCInventoryLineModel:
        return CCDCInventoryLineModel(
            inventory_id=d.inventory_id, item_id=d.item_id,
            book_quantity=d.book_quantity, physical_quantity=d.physical_quantity,
            difference=d.difference, unit_price=d.unit_price,
            difference_amount=d.difference_amount,
            reason=d.reason, resolution=d.resolution,
        )

    def create_inventory(self, inv: CCDCInventory) -> Result:
        model = self._inv_to_model(inv)
        self.session.add(model)
        self.session.flush()
        if inv.lines:
            for line in inv.lines:
                line.inventory_id = model.id
                self.session.add(self._inv_line_to_model(line))
            self.session.flush()
        created = self._inv_to_domain(
            self.session.get(CCDCInventoryModel, model.id)
        )
        return Result.success(created)

    def get_inventory(self, inv_id: int) -> Optional[CCDCInventory]:
        m = self.session.get(CCDCInventoryModel, inv_id)
        return self._inv_to_domain(m) if m else None

    def update_inventory(self, inv_id: int, **updates) -> Result:
        m = self.session.get(CCDCInventoryModel, inv_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_INVENTORY_NOT_FOUND, inv_id=inv_id))
        for key, val in updates.items():
            if key == "status" and isinstance(val, CCInventoryStatus):
                setattr(m, "status", CCInventoryStatusDB(val.value))
            elif key == "resolved_at":
                setattr(m, "resolved_at", val)
            elif hasattr(m, key):
                setattr(m, key, val)
        self.session.flush()
        return Result.success(self._inv_to_domain(m))

    def list_inventories(self, status: Optional[str] = None) -> List[CCDCInventory]:
        stmt = select(CCDCInventoryModel).order_by(CCDCInventoryModel.inventory_date.desc())
        if status:
            stmt = stmt.where(CCDCInventoryModel.status == CCInventoryStatusDB(status))
        return [self._inv_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Write-Off ─────────────────────────────────────────────────────

    def _wo_to_domain(self, m: CCDCWriteOffModel) -> CCDCWriteOff:
        d = CCDCWriteOff(
            item_id=m.item_id, write_off_date=m.write_off_date,
            quantity=m.quantity, remaining_value=m.remaining_value,
            reason=m.reason, disposal_method=m.disposal_method,
            proceeds=m.proceeds, loss_amount=m.loss_amount,
            approved_by=m.approved_by, document_ref=m.document_ref,
            created_by=m.created_by, created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _wo_to_model(self, d: CCDCWriteOff) -> CCDCWriteOffModel:
        return CCDCWriteOffModel(
            item_id=d.item_id, write_off_date=d.write_off_date,
            quantity=d.quantity, remaining_value=d.remaining_value,
            reason=d.reason, disposal_method=d.disposal_method,
            proceeds=d.proceeds, loss_amount=d.loss_amount,
            approved_by=d.approved_by, document_ref=d.document_ref,
            created_by=d.created_by,
        )

    def create_write_off(self, wo: CCDCWriteOff) -> Result:
        model = self._wo_to_model(wo)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._wo_to_domain(model))

    def get_write_off(self, wo_id: int) -> Optional[CCDCWriteOff]:
        m = self.session.get(CCDCWriteOffModel, wo_id)
        return self._wo_to_domain(m) if m else None

    def list_write_offs(self, item_id: Optional[int] = None) -> List[CCDCWriteOff]:
        stmt = select(CCDCWriteOffModel).order_by(CCDCWriteOffModel.write_off_date.desc())
        if item_id:
            stmt = stmt.where(CCDCWriteOffModel.item_id == item_id)
        return [self._wo_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Spare Part ────────────────────────────────────────────────────

    def _sp_to_domain(self, m: CCDCSparePartModel) -> CCDCSparePart:
        d = CCDCSparePart(
            item_id=m.item_id, code=m.code, name=m.name,
            quantity=m.quantity, unit=m.unit, unit_price=m.unit_price,
            total_value=m.total_value, location=m.location, notes=m.notes,
        )
        d.id = m.id
        return d

    def _sp_to_model(self, d: CCDCSparePart) -> CCDCSparePartModel:
        return CCDCSparePartModel(
            item_id=d.item_id, code=d.code, name=d.name,
            quantity=d.quantity, unit=d.unit, unit_price=d.unit_price,
            total_value=d.total_value, location=d.location, notes=d.notes,
        )

    def create_spare_part(self, sp: CCDCSparePart) -> Result:
        model = self._sp_to_model(sp)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._sp_to_domain(model))

    def get_spare_part(self, sp_id: int) -> Optional[CCDCSparePart]:
        m = self.session.get(CCDCSparePartModel, sp_id)
        return self._sp_to_domain(m) if m else None

    def update_spare_part(self, sp_id: int, **updates) -> Result:
        m = self.session.get(CCDCSparePartModel, sp_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_SPARE_PART_NOT_FOUND, sp_id=sp_id))
        for key, val in updates.items():
            setattr(m, key, val)
        self.session.flush()
        return Result.success(self._sp_to_domain(m))

    def delete_spare_part(self, sp_id: int) -> Result:
        m = self.session.get(CCDCSparePartModel, sp_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CC_SPARE_PART_NOT_FOUND, sp_id=sp_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success(None)

    def list_spare_parts(self, item_id: Optional[int] = None) -> List[CCDCSparePart]:
        stmt = select(CCDCSparePartModel).order_by(CCDCSparePartModel.code)
        if item_id:
            stmt = stmt.where(CCDCSparePartModel.item_id == item_id)
        return [self._sp_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Import Log ────────────────────────────────────────────────────

    def create_import_log(self, log: CCDCImportLog) -> Result:
        model = CCDCImportLogModel(
            filename=log.filename, import_type=log.filename.split('.')[-1] if '.' in log.filename else 'unknown',
            total_rows=log.total_rows, success_count=log.success_count,
            error_count=log.error_count, errors=log.errors,
            created_by=log.created_by,
        )
        self.session.add(model)
        self.session.flush()
        log.id = model.id
        return Result.success(log)

    def get_import_log(self, log_id: int) -> Optional[CCDCImportLog]:
        m = self.session.get(CCDCImportLogModel, log_id)
        if not m:
            return None
        return CCDCImportLog(
            id=m.id, filename=m.filename, import_date=m.import_date,
            total_rows=m.total_rows, success_count=m.success_count,
            error_count=m.error_count, errors=m.errors, created_by=m.created_by,
        )

    def list_import_logs(self, limit: int = 50) -> List[CCDCImportLog]:
        stmt = select(CCDCImportLogModel).order_by(CCDCImportLogModel.import_date.desc()).limit(limit)
        return [
            CCDCImportLog(
                id=m.id, filename=m.filename, import_date=m.import_date,
                total_rows=m.total_rows, success_count=m.success_count,
                error_count=m.error_count, errors=m.errors, created_by=m.created_by,
            )
            for m in self.session.execute(stmt).scalars().all()
        ]

    # ── Business Queries ──────────────────────────────────────────────

    def get_items_by_department(self, department_id: int) -> List[CCDCItem]:
        stmt = select(CCDCItemModel).where(
            CCDCItemModel.department_id == department_id,
            CCDCItemModel.status.in_([CCDCStatusDB.IN_USE, CCDCStatusDB.IN_STOCK])
        ).order_by(CCDCItemModel.code)
        return [self._item_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def get_items_by_employee(self, employee_id: int) -> List[CCDCItem]:
        stmt = select(CCDCItemModel).where(
            CCDCItemModel.employee_id == employee_id,
            CCDCItemModel.status == CCDCStatusDB.IN_USE
        ).order_by(CCDCItemModel.code)
        return [self._item_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def get_item_balance(self, item_id: int) -> Decimal:
        m = self.session.get(CCDCItemModel, item_id)
        if not m:
            return Decimal("0")
        return m.remaining_amount

    def get_total_ccdc_value(self, department_id: Optional[int] = None) -> Decimal:
        stmt = select(func.sum(CCDCItemModel.total_cost)).where(
            CCDCItemModel.status != CCDCStatusDB.DISPOSED
        )
        if department_id:
            stmt = stmt.where(CCDCItemModel.department_id == department_id)
        return self.session.execute(stmt).scalar() or Decimal("0")

    def get_unallocated_items(self) -> List[CCDCItem]:
        stmt = select(CCDCItemModel).where(
            CCDCItemModel.allocation_status == CCAllocStatusDB.PENDING,
            CCDCItemModel.status != CCDCStatusDB.DISPOSED,
        ).order_by(CCDCItemModel.code)
        return [self._item_to_domain(m) for m in self.session.execute(stmt).scalars().all()]
