from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_, desc

from domain import (
    InventoryType, MovementType, ValuationMethod,
    CheckMethod, InventoryCheckStatus, BatchStatus, SerialStatus,
    TransferStatus,
    InventoryCategory, Warehouse, InventoryItem, InventoryBatch,
    SerialNumber, InventoryReceipt, InventoryReceiptLine,
    InventoryIssue, InventoryIssueLine, InventoryTransfer,
    InventoryTransferLine, StockCard, InventoryCheck, InventoryCheckLine,
    InventoryAdjustment, InventoryAdjustmentLine,
    Result, AccountError,
)
from domain.inventory import InventoryStatus, AdjustmentType
from domain.i18n import ErrorCodes
from infrastructure.models.inventory_models import (
    InventoryCategoryModel, WarehouseModel, InventoryItemModel,
    InventoryBatchModel, SerialNumberModel,
    InventoryReceiptModel, InventoryReceiptLineModel,
    InventoryIssueModel, InventoryIssueLineModel,
    InventoryTransferModel, InventoryTransferLineModel,
    StockCardModel,
    InventoryCheckModel, InventoryCheckLineModel,
    InventoryAdjustmentModel, InventoryAdjustmentLineModel,
    InventoryTypeDB, InventoryStatusDB, ValuationMethodDB,
    CheckMethodDB, InventoryCheckStatusDB, BatchStatusDB, SerialStatusDB,
    AdjustmentTypeDB, TransferStatusDB,
)


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


_INV_TYPE_MAP = {
    InventoryType.RAW_MATERIAL: InventoryTypeDB.RAW_MATERIAL,
    InventoryType.MATERIAL: InventoryTypeDB.MATERIAL,
    InventoryType.SEMI_FINISHED: InventoryTypeDB.SEMI_FINISHED,
    InventoryType.FINISHED_GOOD: InventoryTypeDB.FINISHED_GOOD,
    InventoryType.MERCHANDISE: InventoryTypeDB.MERCHANDISE,
    InventoryType.PACKAGING: InventoryTypeDB.PACKAGING,
    InventoryType.FUEL: InventoryTypeDB.FUEL,
    InventoryType.SPARE_PART: InventoryTypeDB.SPARE_PART,
    InventoryType.EQUIPMENT: InventoryTypeDB.EQUIPMENT,
    InventoryType.WASTE: InventoryTypeDB.WASTE,
    InventoryType.OTHER: InventoryTypeDB.OTHER,
}

_STATUS_MAP = {
    InventoryStatus.ACTIVE: InventoryStatusDB.ACTIVE,
    InventoryStatus.INACTIVE: InventoryStatusDB.INACTIVE,
    InventoryStatus.DISCONTINUED: InventoryStatusDB.DISCONTINUED,
}

_VAL_METHOD_MAP = {
    ValuationMethod.SPECIFIC: ValuationMethodDB.SPECIFIC,
    ValuationMethod.FIFO: ValuationMethodDB.FIFO,
    ValuationMethod.LIFO: ValuationMethodDB.LIFO,
    ValuationMethod.WEIGHTED_AVERAGE: ValuationMethodDB.WEIGHTED_AVERAGE,
    ValuationMethod.MOVING_AVERAGE: ValuationMethodDB.MOVING_AVERAGE,
    ValuationMethod.STANDARD: ValuationMethodDB.STANDARD,
    ValuationMethod.RETAIL: ValuationMethodDB.RETAIL,
}

_CHECK_METHOD_MAP = {
    CheckMethod.PERIODIC: CheckMethodDB.PERIODIC,
    CheckMethod.PERPETUAL: CheckMethodDB.PERPETUAL,
}

_INV_CHECK_STATUS_MAP = {
    InventoryCheckStatus.DRAFT: InventoryCheckStatusDB.DRAFT,
    InventoryCheckStatus.IN_PROGRESS: InventoryCheckStatusDB.IN_PROGRESS,
    InventoryCheckStatus.COMPLETED: InventoryCheckStatusDB.COMPLETED,
    InventoryCheckStatus.APPROVED: InventoryCheckStatusDB.APPROVED,
    InventoryCheckStatus.CANCELLED: InventoryCheckStatusDB.CANCELLED,
}

_BATCH_STATUS_MAP = {
    BatchStatus.ACTIVE: BatchStatusDB.ACTIVE,
    BatchStatus.EXPIRED: BatchStatusDB.EXPIRED,
    BatchStatus.QUARANTINED: BatchStatusDB.QUARANTINED,
    BatchStatus.DISPOSED: BatchStatusDB.DISPOSED,
}

_SERIAL_STATUS_MAP = {
    SerialStatus.IN_STOCK: SerialStatusDB.IN_STOCK,
    SerialStatus.ISSUED: SerialStatusDB.ISSUED,
    SerialStatus.RETURNED: SerialStatusDB.RETURNED,
    SerialStatus.SCRAPPED: SerialStatusDB.SCRAPPED,
    SerialStatus.QUARANTINED: SerialStatusDB.QUARANTINED,
}

_ADJ_TYPE_MAP = {
    AdjustmentType.WRITE_OFF: AdjustmentTypeDB.WRITE_OFF,
    AdjustmentType.WRITE_ON: AdjustmentTypeDB.WRITE_ON,
    AdjustmentType.DAMAGE: AdjustmentTypeDB.DAMAGE,
    AdjustmentType.THEFT: AdjustmentTypeDB.THEFT,
    AdjustmentType.DONATION: AdjustmentTypeDB.DONATION,
    AdjustmentType.SAMPLE: AdjustmentTypeDB.SAMPLE,
    AdjustmentType.ERROR_CORRECTION: AdjustmentTypeDB.ERROR_CORRECTION,
    AdjustmentType.REVALUATION: AdjustmentTypeDB.REVALUATION,
    AdjustmentType.OTHER: AdjustmentTypeDB.OTHER,
}

_TRANSFER_STATUS_MAP = {
    TransferStatus.DRAFT: TransferStatusDB.DRAFT,
    TransferStatus.IN_TRANSIT: TransferStatusDB.IN_TRANSIT,
    TransferStatus.COMPLETED: TransferStatusDB.COMPLETED,
    TransferStatus.CANCELLED: TransferStatusDB.CANCELLED,
}

_REV_INV_TYPE = {v: k for k, v in _INV_TYPE_MAP.items()}
_REV_STATUS = {v: k for k, v in _STATUS_MAP.items()}
_REV_VAL_METHOD = {v: k for k, v in _VAL_METHOD_MAP.items()}
_REV_CHECK_METHOD = {v: k for k, v in _CHECK_METHOD_MAP.items()}
_REV_INV_CHECK_STATUS = {v: k for k, v in _INV_CHECK_STATUS_MAP.items()}
_REV_BATCH_STATUS = {v: k for k, v in _BATCH_STATUS_MAP.items()}
_REV_SERIAL_STATUS = {v: k for k, v in _SERIAL_STATUS_MAP.items()}
_REV_ADJ_TYPE = {v: k for k, v in _ADJ_TYPE_MAP.items()}
_REV_TRANSFER_STATUS = {v: k for k, v in _TRANSFER_STATUS_MAP.items()}


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Category ─────────────────────────────────────────────────

    def _cat_to_domain(self, m: InventoryCategoryModel) -> InventoryCategory:
        d = InventoryCategory(
            code=m.code, name=m.name, description=m.description or "",
            parent_id=m.parent_id,
            inventory_type=_REV_INV_TYPE.get(m.inventory_type, InventoryType.MERCHANDISE),
            valuation_method=_REV_VAL_METHOD.get(m.valuation_method, ValuationMethod.WEIGHTED_AVERAGE),
            gl_inventory_account=m.gl_inventory_account,
            gl_receipt_account=m.gl_receipt_account,
            gl_issue_account=m.gl_issue_account,
            gl_sales_account=m.gl_sales_account,
            gl_cost_of_sales=m.gl_cost_of_sales,
            gl_return_account=m.gl_return_account,
            is_active=m.is_active,
            created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def create_category(self, category: InventoryCategory) -> Result:
        existing = self.session.execute(
            select(InventoryCategoryModel).where(InventoryCategoryModel.code == category.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_CODE_DUPLICATE, code=category.code))
        m = InventoryCategoryModel(
            code=category.code, name=category.name, description=category.description,
            parent_id=category.parent_id,
            inventory_type=_INV_TYPE_MAP.get(category.inventory_type, InventoryTypeDB.MERCHANDISE),
            valuation_method=_VAL_METHOD_MAP.get(category.valuation_method, ValuationMethodDB.WEIGHTED_AVERAGE),
            gl_inventory_account=category.gl_inventory_account,
            gl_receipt_account=category.gl_receipt_account,
            gl_issue_account=category.gl_issue_account,
            gl_sales_account=category.gl_sales_account,
            gl_cost_of_sales=category.gl_cost_of_sales,
            gl_return_account=category.gl_return_account,
            is_active=category.is_active,
        )
        self.session.add(m)
        self.session.flush()
        return Result.success(self._cat_to_domain(m))

    def get_category(self, category_id: int) -> Optional[InventoryCategory]:
        m = self.session.get(InventoryCategoryModel, category_id)
        return self._cat_to_domain(m) if m else None

    def get_category_by_code(self, code: str) -> Optional[InventoryCategory]:
        m = self.session.execute(
            select(InventoryCategoryModel).where(InventoryCategoryModel.code == code)
        ).scalar_one_or_none()
        return self._cat_to_domain(m) if m else None

    def list_categories(self, inventory_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[InventoryCategory]:
        q = select(InventoryCategoryModel).order_by(InventoryCategoryModel.code)
        if inventory_type:
            db_val = None
            for k, v in _INV_TYPE_MAP.items():
                if k.value == inventory_type or k.name == inventory_type or v.value == inventory_type:
                    db_val = v
                    break
            if db_val:
                q = q.where(InventoryCategoryModel.inventory_type == db_val)
        if is_active is not None:
            q = q.where(InventoryCategoryModel.is_active == is_active)
        results = self.session.execute(q).scalars().all()
        return [self._cat_to_domain(m) for m in results]

    def update_category(self, category_id: int, **updates) -> Result:
        m = self.session.get(InventoryCategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_NOT_FOUND, category_id=category_id))
        if "code" in updates:
            dup = self.session.execute(
                select(InventoryCategoryModel).where(
                    InventoryCategoryModel.code == updates["code"],
                    InventoryCategoryModel.id != category_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_CODE_DUPLICATE, code=updates["code"]))
        for key, val in updates.items():
            if key == "inventory_type" and val:
                setattr(m, "inventory_type", _INV_TYPE_MAP.get(val, InventoryTypeDB.MERCHANDISE))
            elif key == "valuation_method" and val:
                setattr(m, "valuation_method", _VAL_METHOD_MAP.get(val, ValuationMethodDB.WEIGHTED_AVERAGE))
            elif hasattr(m, key):
                setattr(m, key, val)
        self.session.flush()
        return Result.success(self._cat_to_domain(m))

    def delete_category(self, category_id: int) -> Result:
        m = self.session.get(InventoryCategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_NOT_FOUND, category_id=category_id))
        items_count = self.session.execute(
            select(func.count()).select_from(InventoryItemModel).where(InventoryItemModel.category_id == category_id)
        ).scalar()
        if items_count and items_count > 0:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_HAS_ITEMS, category_id=category_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success({"deleted": True})

    # ── Warehouse ─────────────────────────────────────────────────

    def _wh_to_domain(self, m: WarehouseModel) -> Warehouse:
        d = Warehouse(
            code=m.code, name=m.name, address=m.address or "",
            contact_person=m.contact_person, contact_phone=m.contact_phone,
            is_active=m.is_active, allow_negative_stock=m.allow_negative_stock,
            check_method=_REV_CHECK_METHOD.get(m.check_method, CheckMethod.PERPETUAL),
            gl_inventory_account=m.gl_inventory_account,
            notes=m.notes or "",
            created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def create_warehouse(self, warehouse: Warehouse) -> Result:
        existing = self.session.execute(
            select(WarehouseModel).where(WarehouseModel.code == warehouse.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_CODE_DUPLICATE, code=warehouse.code))
        m = WarehouseModel(
            code=warehouse.code, name=warehouse.name, address=warehouse.address,
            contact_person=warehouse.contact_person, contact_phone=warehouse.contact_phone,
            is_active=warehouse.is_active, allow_negative_stock=warehouse.allow_negative_stock,
            check_method=_CHECK_METHOD_MAP.get(warehouse.check_method, CheckMethodDB.PERPETUAL),
            gl_inventory_account=warehouse.gl_inventory_account,
            notes=warehouse.notes,
        )
        self.session.add(m)
        self.session.flush()
        return Result.success(self._wh_to_domain(m))

    def get_warehouse(self, warehouse_id: int) -> Optional[Warehouse]:
        m = self.session.get(WarehouseModel, warehouse_id)
        return self._wh_to_domain(m) if m else None

    def get_warehouse_by_code(self, code: str) -> Optional[Warehouse]:
        m = self.session.execute(
            select(WarehouseModel).where(WarehouseModel.code == code)
        ).scalar_one_or_none()
        return self._wh_to_domain(m) if m else None

    def list_warehouses(self, is_active: Optional[bool] = None) -> List[Warehouse]:
        q = select(WarehouseModel).order_by(WarehouseModel.code)
        if is_active is not None:
            q = q.where(WarehouseModel.is_active == is_active)
        results = self.session.execute(q).scalars().all()
        return [self._wh_to_domain(m) for m in results]

    def update_warehouse(self, warehouse_id: int, **updates) -> Result:
        m = self.session.get(WarehouseModel, warehouse_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_NOT_FOUND, warehouse_id=warehouse_id))
        if "code" in updates:
            dup = self.session.execute(
                select(WarehouseModel).where(
                    WarehouseModel.code == updates["code"],
                    WarehouseModel.id != warehouse_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_CODE_DUPLICATE, code=updates["code"]))
        for key, val in updates.items():
            if key == "check_method" and val:
                setattr(m, "check_method", _CHECK_METHOD_MAP.get(val, CheckMethodDB.PERPETUAL))
            elif hasattr(m, key):
                setattr(m, key, val)
        self.session.flush()
        return Result.success(self._wh_to_domain(m))

    def delete_warehouse(self, warehouse_id: int) -> Result:
        m = self.session.get(WarehouseModel, warehouse_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_NOT_FOUND, warehouse_id=warehouse_id))
        items_count = self.session.execute(
            select(func.count()).select_from(InventoryItemModel).where(
                InventoryItemModel.default_warehouse_id == warehouse_id
            )
        ).scalar()
        if items_count and items_count > 0:
            return Result.failure(AccountError(ErrorCodes.INV_WAREHOUSE_HAS_STOCK, warehouse_id=warehouse_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success({"deleted": True})

    # ── Item ─────────────────────────────────────────────────────

    def _item_to_domain(self, m: InventoryItemModel) -> InventoryItem:
        d = InventoryItem(
            code=m.code, name=m.name, category_id=m.category_id,
            default_warehouse_id=m.default_warehouse_id,
            inventory_type=_REV_INV_TYPE.get(m.inventory_type, InventoryType.MERCHANDISE),
            status=_REV_STATUS.get(m.status, InventoryStatus.ACTIVE),
            valuation_method=_REV_VAL_METHOD.get(m.valuation_method) if m.valuation_method else None,
            unit=m.unit, unit_price=m.unit_price, cost_price=m.cost_price,
            selling_price=m.selling_price,
            min_stock=m.min_stock, max_stock=m.max_stock,
            reorder_point=m.reorder_point, reorder_quantity=m.reorder_quantity,
            current_stock=m.current_stock, reserved_stock=m.reserved_stock,
            available_stock=m.available_stock,
            batch_tracking=m.batch_tracking, serial_tracking=m.serial_tracking,
            expiry_tracking=m.expiry_tracking,
            weight=m.weight, volume=m.volume, hs_code=m.hs_code, barcode=m.barcode,
            tax_rate=m.tax_rate, image_url=m.image_url, description=m.description or "",
            gl_inventory_account=m.gl_inventory_account,
            gl_receipt_account=m.gl_receipt_account,
            gl_issue_account=m.gl_issue_account,
            gl_sales_account=m.gl_sales_account,
            gl_cost_of_sales=m.gl_cost_of_sales,
            gl_return_account=m.gl_return_account,
            created_by=m.created_by,
            created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def create_item(self, item: InventoryItem) -> Result:
        existing = self.session.execute(
            select(InventoryItemModel).where(InventoryItemModel.code == item.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_CODE_DUPLICATE, code=item.code))
        cat = self.session.get(InventoryCategoryModel, item.category_id)
        if not cat:
            return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_NOT_FOUND, category_id=item.category_id))
        m = InventoryItemModel(
            code=item.code, name=item.name, category_id=item.category_id,
            default_warehouse_id=item.default_warehouse_id,
            inventory_type=_INV_TYPE_MAP.get(item.inventory_type, InventoryTypeDB.MERCHANDISE),
            status=_STATUS_MAP.get(item.status, InventoryStatusDB.ACTIVE),
            valuation_method=_VAL_METHOD_MAP.get(item.valuation_method) if item.valuation_method else None,
            unit=item.unit, unit_price=item.unit_price, cost_price=item.cost_price,
            selling_price=item.selling_price,
            min_stock=item.min_stock, max_stock=item.max_stock,
            reorder_point=item.reorder_point, reorder_quantity=item.reorder_quantity,
            current_stock=item.current_stock, reserved_stock=item.reserved_stock,
            available_stock=item.available_stock,
            batch_tracking=item.batch_tracking, serial_tracking=item.serial_tracking,
            expiry_tracking=item.expiry_tracking,
            weight=item.weight, volume=item.volume, hs_code=item.hs_code, barcode=item.barcode,
            tax_rate=item.tax_rate, image_url=item.image_url, description=item.description,
            gl_inventory_account=item.gl_inventory_account,
            gl_receipt_account=item.gl_receipt_account,
            gl_issue_account=item.gl_issue_account,
            gl_sales_account=item.gl_sales_account,
            gl_cost_of_sales=item.gl_cost_of_sales,
            gl_return_account=item.gl_return_account,
            created_by=item.created_by,
        )
        self.session.add(m)
        self.session.flush()
        return Result.success(self._item_to_domain(m))

    def get_item(self, item_id: int) -> Optional[InventoryItem]:
        m = self.session.get(InventoryItemModel, item_id)
        return self._item_to_domain(m) if m else None

    def get_item_by_code(self, code: str) -> Optional[InventoryItem]:
        m = self.session.execute(
            select(InventoryItemModel).where(InventoryItemModel.code == code)
        ).scalar_one_or_none()
        return self._item_to_domain(m) if m else None

    def list_items(self, category_id: Optional[int] = None, inventory_type: Optional[str] = None,
                   status: Optional[str] = None, search: Optional[str] = None,
                   low_stock: bool = False) -> List[InventoryItem]:
        q = select(InventoryItemModel).order_by(InventoryItemModel.code)
        if category_id:
            q = q.where(InventoryItemModel.category_id == category_id)
        if inventory_type:
            db_val = None
            for k, v in _INV_TYPE_MAP.items():
                if k.value == inventory_type or v.value == inventory_type:
                    db_val = v
                    break
            if db_val:
                q = q.where(InventoryItemModel.inventory_type == db_val)
        if status:
            db_status = None
            for k, v in _STATUS_MAP.items():
                if k.value == status or v.value == status:
                    db_status = v
                    break
            if db_status:
                q = q.where(InventoryItemModel.status == db_status)
        if search:
            pattern = f"%{search}%"
            q = q.where(
                or_(InventoryItemModel.code.ilike(pattern), InventoryItemModel.name.ilike(pattern))
            )
        if low_stock:
            q = q.where(
                and_(InventoryItemModel.current_stock <= InventoryItemModel.reorder_point,
                     InventoryItemModel.reorder_point > 0)
            )
        results = self.session.execute(q).scalars().all()
        return [self._item_to_domain(m) for m in results]

    def update_item(self, item_id: int, **updates) -> Result:
        m = self.session.get(InventoryItemModel, item_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        if "code" in updates:
            dup = self.session.execute(
                select(InventoryItemModel).where(
                    InventoryItemModel.code == updates["code"],
                    InventoryItemModel.id != item_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.INV_ITEM_CODE_DUPLICATE, code=updates["code"]))
        if "category_id" in updates:
            cat = self.session.get(InventoryCategoryModel, updates["category_id"])
            if not cat:
                return Result.failure(AccountError(ErrorCodes.INV_CATEGORY_NOT_FOUND, category_id=updates["category_id"]))
        for key, val in updates.items():
            if key == "inventory_type" and val:
                setattr(m, "inventory_type", _INV_TYPE_MAP.get(val, InventoryTypeDB.MERCHANDISE))
            elif key == "status" and val:
                setattr(m, "status", _STATUS_MAP.get(val, InventoryStatusDB.ACTIVE))
            elif key == "valuation_method":
                setattr(m, "valuation_method", _VAL_METHOD_MAP.get(val) if val else None)
            elif hasattr(m, key):
                setattr(m, key, val)
        self.session.flush()
        return Result.success(self._item_to_domain(m))

    def adjust_stock(self, item_id: int, warehouse_id: int, quantity_change: Decimal) -> Result:
        m = self.session.get(InventoryItemModel, item_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_ITEM_NOT_FOUND, item_id=item_id))
        new_stock = m.current_stock + quantity_change
        if new_stock < 0:
            wh = self.session.get(WarehouseModel, warehouse_id)
            if not wh or not wh.allow_negative_stock:
                return Result.failure(AccountError(ErrorCodes.INV_NEGATIVE_STOCK_NOT_ALLOWED, item_id=item_id))
        m.current_stock = new_stock
        m.available_stock = m.current_stock - m.reserved_stock
        self.session.flush()
        return Result.success(self._item_to_domain(m))

    # ── Batch ───────────────────────────────────────────────────

    def _batch_to_domain(self, m: InventoryBatchModel) -> InventoryBatch:
        d = InventoryBatch(
            item_id=m.item_id, warehouse_id=m.warehouse_id,
            batch_code=m.batch_code,
            manufacturing_date=m.manufacturing_date, expiry_date=m.expiry_date,
            received_date=m.received_date,
            quantity=m.quantity, remaining_quantity=m.remaining_quantity,
            unit_cost=m.unit_cost, total_cost=m.total_cost,
            status=_REV_BATCH_STATUS.get(m.status, BatchStatus.ACTIVE),
            supplier_batch=m.supplier_batch, notes=m.notes or "",
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def create_batch(self, batch: InventoryBatch) -> Result:
        existing = self.session.execute(
            select(InventoryBatchModel).where(
                InventoryBatchModel.batch_code == batch.batch_code,
                InventoryBatchModel.item_id == batch.item_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.INV_BATCH_CODE_DUPLICATE, code=batch.batch_code))
        m = InventoryBatchModel(
            item_id=batch.item_id, warehouse_id=batch.warehouse_id,
            batch_code=batch.batch_code,
            manufacturing_date=batch.manufacturing_date, expiry_date=batch.expiry_date,
            received_date=batch.received_date,
            quantity=batch.quantity, remaining_quantity=batch.remaining_quantity,
            unit_cost=batch.unit_cost, total_cost=batch.total_cost,
            status=_BATCH_STATUS_MAP.get(batch.status, BatchStatusDB.ACTIVE),
            supplier_batch=batch.supplier_batch, notes=batch.notes,
        )
        self.session.add(m)
        self.session.flush()
        return Result.success(self._batch_to_domain(m))

    def get_batch(self, batch_id: int) -> Optional[InventoryBatch]:
        m = self.session.get(InventoryBatchModel, batch_id)
        return self._batch_to_domain(m) if m else None

    def list_batches(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                     status: Optional[str] = None) -> List[InventoryBatch]:
        q = select(InventoryBatchModel).order_by(InventoryBatchModel.received_date.desc())
        if item_id:
            q = q.where(InventoryBatchModel.item_id == item_id)
        if warehouse_id:
            q = q.where(InventoryBatchModel.warehouse_id == warehouse_id)
        if status:
            db_status = None
            for k, v in _BATCH_STATUS_MAP.items():
                if k.value == status or v.value == status:
                    db_status = v
                    break
            if db_status:
                q = q.where(InventoryBatchModel.status == db_status)
        results = self.session.execute(q).scalars().all()
        return [self._batch_to_domain(m) for m in results]

    def update_batch_quantity(self, batch_id: int, delta: Decimal) -> Result:
        m = self.session.get(InventoryBatchModel, batch_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_BATCH_NOT_FOUND, batch_id=batch_id))
        m.remaining_quantity += delta
        if m.remaining_quantity < 0:
            m.remaining_quantity = Decimal("0")
        self.session.flush()
        return Result.success(self._batch_to_domain(m))

    # ── Serial ──────────────────────────────────────────────────

    def _serial_to_domain(self, m: SerialNumberModel) -> SerialNumber:
        d = SerialNumber(
            item_id=m.item_id, batch_id=m.batch_id, warehouse_id=m.warehouse_id,
            serial_code=m.serial_code,
            status=_REV_SERIAL_STATUS.get(m.status, SerialStatus.IN_STOCK),
            receipt_date=m.receipt_date, issue_date=m.issue_date,
            notes=m.notes or "", created_at=m.created_at,
        )
        d.id = m.id
        return d

    def create_serial(self, serial: SerialNumber) -> Result:
        existing = self.session.execute(
            select(SerialNumberModel).where(SerialNumberModel.serial_code == serial.serial_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.INV_SERIAL_CODE_DUPLICATE, code=serial.serial_code))
        m = SerialNumberModel(
            item_id=serial.item_id, batch_id=serial.batch_id, warehouse_id=serial.warehouse_id,
            serial_code=serial.serial_code,
            status=_SERIAL_STATUS_MAP.get(serial.status, SerialStatusDB.IN_STOCK),
            receipt_date=serial.receipt_date, issue_date=serial.issue_date,
            notes=serial.notes,
        )
        self.session.add(m)
        self.session.flush()
        return Result.success(self._serial_to_domain(m))

    def get_serial(self, serial_id: int) -> Optional[SerialNumber]:
        m = self.session.get(SerialNumberModel, serial_id)
        return self._serial_to_domain(m) if m else None

    def get_serial_by_code(self, code: str) -> Optional[SerialNumber]:
        m = self.session.execute(
            select(SerialNumberModel).where(SerialNumberModel.serial_code == code)
        ).scalar_one_or_none()
        return self._serial_to_domain(m) if m else None

    def list_serials(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                     status: Optional[str] = None) -> List[SerialNumber]:
        q = select(SerialNumberModel).order_by(SerialNumberModel.created_at.desc())
        if item_id:
            q = q.where(SerialNumberModel.item_id == item_id)
        if warehouse_id:
            q = q.where(SerialNumberModel.warehouse_id == warehouse_id)
        if status:
            db_status = None
            for k, v in _SERIAL_STATUS_MAP.items():
                if k.value == status or v.value == status:
                    db_status = v
                    break
            if db_status:
                q = q.where(SerialNumberModel.status == db_status)
        results = self.session.execute(q).scalars().all()
        return [self._serial_to_domain(m) for m in results]

    def update_serial_status(self, serial_id: int, status: SerialStatus) -> Result:
        m = self.session.get(SerialNumberModel, serial_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_SERIAL_NOT_FOUND, serial_id=serial_id))
        m.status = _SERIAL_STATUS_MAP.get(status, SerialStatusDB.IN_STOCK)
        if status == SerialStatus.ISSUED:
            m.issue_date = date.today()
        self.session.flush()
        return Result.success(self._serial_to_domain(m))

    # ── Receipt ─────────────────────────────────────────────────

    def _receipt_to_domain(self, m: InventoryReceiptModel) -> InventoryReceipt:
        d = InventoryReceipt(
            receipt_code=m.receipt_code, receipt_date=m.receipt_date,
            warehouse_id=m.warehouse_id,
            supplier_id=m.supplier_id, supplier_invoice_ref=m.supplier_invoice_ref,
            reference_doc=m.reference_doc, description=m.description or "",
            is_posted=m.is_posted, posted_at=m.posted_at,
            gl_journal_ref=m.gl_journal_ref,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        if m.lines:
            d.lines = [self._receipt_line_to_domain(l) for l in m.lines]
        return d

    def _receipt_line_to_domain(self, m: InventoryReceiptLineModel) -> InventoryReceiptLine:
        d = InventoryReceiptLine(
            receipt_id=m.receipt_id, item_id=m.item_id, warehouse_id=m.warehouse_id,
            batch_id=m.batch_id, quantity=m.quantity, unit_price=m.unit_price,
            total_amount=m.total_amount, tax_amount=m.tax_amount,
            discount_amount=m.discount_amount, line_order=m.line_order,
            notes=m.notes or "",
        )
        d.id = m.id
        return d

    def create_receipt(self, receipt: InventoryReceipt) -> Result:
        m = InventoryReceiptModel(
            receipt_code=receipt.receipt_code, receipt_date=receipt.receipt_date,
            warehouse_id=receipt.warehouse_id,
            supplier_id=receipt.supplier_id, supplier_invoice_ref=receipt.supplier_invoice_ref,
            reference_doc=receipt.reference_doc, description=receipt.description,
            is_posted=False, created_by=receipt.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in receipt.lines:
            lm = InventoryReceiptLineModel(
                receipt_id=m.id, item_id=line.item_id, warehouse_id=line.warehouse_id or receipt.warehouse_id,
                batch_id=line.batch_id, quantity=line.quantity, unit_price=line.unit_price,
                total_amount=line.total_amount or (line.quantity * line.unit_price),
                tax_amount=line.tax_amount, discount_amount=line.discount_amount,
                line_order=line.line_order, notes=line.notes,
            )
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._receipt_to_domain(m))

    def get_receipt(self, receipt_id: int) -> Optional[InventoryReceipt]:
        m = self.session.get(InventoryReceiptModel, receipt_id)
        return self._receipt_to_domain(m) if m else None

    def get_receipt_line(self, receipt_line_id: int) -> Optional[InventoryReceiptLine]:
        from infrastructure.models.inventory_models import InventoryReceiptLineModel
        m = self.session.get(InventoryReceiptLineModel, receipt_line_id)
        return self._receipt_line_to_domain(m) if m else None

    def list_receipts(self, warehouse_id: Optional[int] = None,
                      date_from: Optional[date] = None, date_to: Optional[date] = None,
                      is_posted: Optional[bool] = None,
                      skip: int = 0, limit: int = 50) -> Tuple[List[InventoryReceipt], int]:
        q = select(InventoryReceiptModel)
        count_q = select(func.count()).select_from(InventoryReceiptModel)
        if warehouse_id:
            q = q.where(InventoryReceiptModel.warehouse_id == warehouse_id)
            count_q = count_q.where(InventoryReceiptModel.warehouse_id == warehouse_id)
        if date_from:
            q = q.where(InventoryReceiptModel.receipt_date >= date_from)
            count_q = count_q.where(InventoryReceiptModel.receipt_date >= date_from)
        if date_to:
            q = q.where(InventoryReceiptModel.receipt_date <= date_to)
            count_q = count_q.where(InventoryReceiptModel.receipt_date <= date_to)
        if is_posted is not None:
            q = q.where(InventoryReceiptModel.is_posted == is_posted)
            count_q = count_q.where(InventoryReceiptModel.is_posted == is_posted)
        total = self.session.execute(count_q).scalar() or 0
        q = q.order_by(desc(InventoryReceiptModel.receipt_date)).offset(skip).limit(limit)
        results = self.session.execute(q).scalars().all()
        return [self._receipt_to_domain(m) for m in results], total

    def post_receipt(self, receipt_id: int, gl_ref: Optional[str] = None) -> Result:
        m = self.session.get(InventoryReceiptModel, receipt_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        if m.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_RECEIPT_ALREADY_POSTED, receipt_id=receipt_id))
        m.is_posted = True
        m.posted_at = datetime.now(timezone.utc)
        m.gl_journal_ref = gl_ref
        self.session.flush()
        return Result.success(self._receipt_to_domain(m))

    # ── Issue ───────────────────────────────────────────────────

    def _issue_to_domain(self, m: InventoryIssueModel) -> InventoryIssue:
        d = InventoryIssue(
            issue_code=m.issue_code, issue_date=m.issue_date,
            warehouse_id=m.warehouse_id,
            department_id=m.department_id, customer_id=m.customer_id,
            recipient_name=m.recipient_name,
            reference_doc=m.reference_doc, description=m.description or "",
            is_posted=m.is_posted, posted_at=m.posted_at,
            gl_journal_ref=m.gl_journal_ref,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        if m.lines:
            d.lines = [self._issue_line_to_domain(l) for l in m.lines]
        return d

    def _issue_line_to_domain(self, m: InventoryIssueLineModel) -> InventoryIssueLine:
        d = InventoryIssueLine(
            issue_id=m.issue_id, item_id=m.item_id, warehouse_id=m.warehouse_id,
            batch_id=m.batch_id, quantity=m.quantity, unit_price=m.unit_price,
            total_amount=m.total_amount, tax_amount=m.tax_amount,
            discount_amount=m.discount_amount, line_order=m.line_order,
            cost_price=m.cost_price, cost_amount=m.cost_amount,
            notes=m.notes or "",
        )
        d.id = m.id
        return d

    def create_issue(self, issue: InventoryIssue) -> Result:
        m = InventoryIssueModel(
            issue_code=issue.issue_code, issue_date=issue.issue_date,
            warehouse_id=issue.warehouse_id,
            department_id=issue.department_id, customer_id=issue.customer_id,
            recipient_name=issue.recipient_name,
            reference_doc=issue.reference_doc, description=issue.description,
            is_posted=False, created_by=issue.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in issue.lines:
            lm = InventoryIssueLineModel(
                issue_id=m.id, item_id=line.item_id, warehouse_id=line.warehouse_id or issue.warehouse_id,
                batch_id=line.batch_id, quantity=line.quantity, unit_price=line.unit_price,
                total_amount=line.total_amount or (line.quantity * line.unit_price),
                tax_amount=line.tax_amount, discount_amount=line.discount_amount,
                line_order=line.line_order,
                cost_price=line.cost_price, cost_amount=line.cost_amount or (line.quantity * line.cost_price),
                notes=line.notes,
            )
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._issue_to_domain(m))

    def get_issue(self, issue_id: int) -> Optional[InventoryIssue]:
        m = self.session.get(InventoryIssueModel, issue_id)
        return self._issue_to_domain(m) if m else None

    def list_issues(self, warehouse_id: Optional[int] = None,
                    date_from: Optional[date] = None, date_to: Optional[date] = None,
                    is_posted: Optional[bool] = None,
                    skip: int = 0, limit: int = 50) -> Tuple[List[InventoryIssue], int]:
        q = select(InventoryIssueModel)
        count_q = select(func.count()).select_from(InventoryIssueModel)
        if warehouse_id:
            q = q.where(InventoryIssueModel.warehouse_id == warehouse_id)
            count_q = count_q.where(InventoryIssueModel.warehouse_id == warehouse_id)
        if date_from:
            q = q.where(InventoryIssueModel.issue_date >= date_from)
            count_q = count_q.where(InventoryIssueModel.issue_date >= date_from)
        if date_to:
            q = q.where(InventoryIssueModel.issue_date <= date_to)
            count_q = count_q.where(InventoryIssueModel.issue_date <= date_to)
        if is_posted is not None:
            q = q.where(InventoryIssueModel.is_posted == is_posted)
            count_q = count_q.where(InventoryIssueModel.is_posted == is_posted)
        total = self.session.execute(count_q).scalar() or 0
        q = q.order_by(desc(InventoryIssueModel.issue_date)).offset(skip).limit(limit)
        results = self.session.execute(q).scalars().all()
        return [self._issue_to_domain(m) for m in results], total

    def post_issue(self, issue_id: int, gl_ref: Optional[str] = None) -> Result:
        m = self.session.get(InventoryIssueModel, issue_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_NOT_FOUND, issue_id=issue_id))
        if m.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_ISSUE_ALREADY_POSTED, issue_id=issue_id))
        m.is_posted = True
        m.posted_at = datetime.now(timezone.utc)
        m.gl_journal_ref = gl_ref
        self.session.flush()
        return Result.success(self._issue_to_domain(m))

    # ── Transfer ────────────────────────────────────────────────

    def _transfer_to_domain(self, m: InventoryTransferModel) -> InventoryTransfer:
        d = InventoryTransfer(
            transfer_code=m.transfer_code, transfer_date=m.transfer_date,
            from_warehouse_id=m.from_warehouse_id, to_warehouse_id=m.to_warehouse_id,
            status=_REV_TRANSFER_STATUS.get(m.status, TransferStatus.DRAFT),
            reference_doc=m.reference_doc, description=m.description or "",
            is_posted=m.is_posted, posted_at=m.posted_at,
            gl_journal_ref=m.gl_journal_ref,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        if m.lines:
            d.lines = [self._transfer_line_to_domain(l) for l in m.lines]
        return d

    def _transfer_line_to_domain(self, m: InventoryTransferLineModel) -> InventoryTransferLine:
        d = InventoryTransferLine(
            transfer_id=m.transfer_id, item_id=m.item_id,
            quantity=m.quantity, unit_price=m.unit_price,
            total_amount=m.total_amount, line_order=m.line_order,
            notes=m.notes or "",
        )
        d.id = m.id
        return d

    def create_transfer(self, transfer: InventoryTransfer) -> Result:
        m = InventoryTransferModel(
            transfer_code=transfer.transfer_code, transfer_date=transfer.transfer_date,
            from_warehouse_id=transfer.from_warehouse_id, to_warehouse_id=transfer.to_warehouse_id,
            status=TransferStatusDB.DRAFT,
            reference_doc=transfer.reference_doc, description=transfer.description,
            is_posted=False, created_by=transfer.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in transfer.lines:
            lm = InventoryTransferLineModel(
                transfer_id=m.id, item_id=line.item_id,
                quantity=line.quantity, unit_price=line.unit_price,
                total_amount=line.total_amount or (line.quantity * line.unit_price),
                line_order=line.line_order, notes=line.notes,
            )
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._transfer_to_domain(m))

    def get_transfer(self, transfer_id: int) -> Optional[InventoryTransfer]:
        m = self.session.get(InventoryTransferModel, transfer_id)
        return self._transfer_to_domain(m) if m else None

    def list_transfers(self, from_warehouse_id: Optional[int] = None,
                       to_warehouse_id: Optional[int] = None,
                       status: Optional[str] = None,
                       skip: int = 0, limit: int = 50) -> Tuple[List[InventoryTransfer], int]:
        q = select(InventoryTransferModel)
        count_q = select(func.count()).select_from(InventoryTransferModel)
        if from_warehouse_id:
            q = q.where(InventoryTransferModel.from_warehouse_id == from_warehouse_id)
            count_q = count_q.where(InventoryTransferModel.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            q = q.where(InventoryTransferModel.to_warehouse_id == to_warehouse_id)
            count_q = count_q.where(InventoryTransferModel.to_warehouse_id == to_warehouse_id)
        if status:
            db_status = None
            for k, v in _TRANSFER_STATUS_MAP.items():
                if k.value == status or v.value == status:
                    db_status = v
                    break
            if db_status:
                q = q.where(InventoryTransferModel.status == db_status)
                count_q = count_q.where(InventoryTransferModel.status == db_status)
        total = self.session.execute(count_q).scalar() or 0
        q = q.order_by(desc(InventoryTransferModel.transfer_date)).offset(skip).limit(limit)
        results = self.session.execute(q).scalars().all()
        return [self._transfer_to_domain(m) for m in results], total

    def update_transfer_status(self, transfer_id: int, status: TransferStatus) -> Result:
        m = self.session.get(InventoryTransferModel, transfer_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        m.status = _TRANSFER_STATUS_MAP.get(status, TransferStatusDB.DRAFT)
        self.session.flush()
        return Result.success(self._transfer_to_domain(m))

    def post_transfer(self, transfer_id: int, gl_ref: Optional[str] = None) -> Result:
        m = self.session.get(InventoryTransferModel, transfer_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        if m.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_TRANSFER_ALREADY_POSTED, transfer_id=transfer_id))
        m.is_posted = True
        m.posted_at = datetime.now(timezone.utc)
        m.gl_journal_ref = gl_ref
        m.status = TransferStatusDB.COMPLETED
        self.session.flush()
        return Result.success(self._transfer_to_domain(m))

    # ── Stock Card ──────────────────────────────────────────────

    def _stock_card_to_domain(self, m: StockCardModel) -> StockCard:
        d = StockCard(
            item_id=m.item_id, warehouse_id=m.warehouse_id, period=m.period,
            opening_quantity=m.opening_quantity, opening_value=m.opening_value,
            receipt_quantity=m.receipt_quantity, receipt_value=m.receipt_value,
            issue_quantity=m.issue_quantity, issue_value=m.issue_value,
            closing_quantity=m.closing_quantity, closing_value=m.closing_value,
            unit_cost=m.unit_cost,
        )
        d.id = m.id
        return d

    def get_stock_card(self, item_id: int, warehouse_id: int, period: str) -> Optional[StockCard]:
        m = self.session.execute(
            select(StockCardModel).where(
                StockCardModel.item_id == item_id,
                StockCardModel.warehouse_id == warehouse_id,
                StockCardModel.period == period,
            )
        ).scalar_one_or_none()
        return self._stock_card_to_domain(m) if m else None

    def upsert_stock_card(self, card: StockCard) -> StockCard:
        existing = self.session.execute(
            select(StockCardModel).where(
                StockCardModel.item_id == card.item_id,
                StockCardModel.warehouse_id == card.warehouse_id,
                StockCardModel.period == card.period,
            )
        ).scalar_one_or_none()
        if existing:
            existing.opening_quantity = card.opening_quantity
            existing.opening_value = card.opening_value
            existing.receipt_quantity = card.receipt_quantity
            existing.receipt_value = card.receipt_value
            existing.issue_quantity = card.issue_quantity
            existing.issue_value = card.issue_value
            existing.closing_quantity = card.closing_quantity
            existing.closing_value = card.closing_value
            existing.unit_cost = card.unit_cost
            self.session.flush()
            return self._stock_card_to_domain(existing)
        m = StockCardModel(
            item_id=card.item_id, warehouse_id=card.warehouse_id, period=card.period,
            opening_quantity=card.opening_quantity, opening_value=card.opening_value,
            receipt_quantity=card.receipt_quantity, receipt_value=card.receipt_value,
            issue_quantity=card.issue_quantity, issue_value=card.issue_value,
            closing_quantity=card.closing_quantity, closing_value=card.closing_value,
            unit_cost=card.unit_cost,
        )
        self.session.add(m)
        self.session.flush()
        return self._stock_card_to_domain(m)

    def list_stock_cards(self, item_id: Optional[int] = None, warehouse_id: Optional[int] = None,
                         period_from: Optional[str] = None, period_to: Optional[str] = None) -> List[StockCard]:
        q = select(StockCardModel).order_by(StockCardModel.period)
        if item_id:
            q = q.where(StockCardModel.item_id == item_id)
        if warehouse_id:
            q = q.where(StockCardModel.warehouse_id == warehouse_id)
        if period_from:
            q = q.where(StockCardModel.period >= period_from)
        if period_to:
            q = q.where(StockCardModel.period <= period_to)
        results = self.session.execute(q).scalars().all()
        return [self._stock_card_to_domain(m) for m in results]

    # ── Check ───────────────────────────────────────────────────

    def _check_to_domain(self, m: InventoryCheckModel) -> InventoryCheck:
        d = InventoryCheck(
            check_code=m.check_code, check_date=m.check_date,
            warehouse_id=m.warehouse_id,
            status=_REV_INV_CHECK_STATUS.get(m.status, InventoryCheckStatus.DRAFT),
            reference_doc=m.reference_doc, notes=m.notes or "",
            created_by=m.created_by, approved_by=m.approved_by, approved_at=m.approved_at,
            created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        if m.lines:
            d.lines = [self._check_line_to_domain(l) for l in m.lines]
        return d

    def _check_line_to_domain(self, m: InventoryCheckLineModel) -> InventoryCheckLine:
        d = InventoryCheckLine(
            check_id=m.check_id, item_id=m.item_id, warehouse_id=m.warehouse_id,
            batch_id=m.batch_id,
            book_quantity=m.book_quantity, physical_quantity=m.physical_quantity,
            difference_quantity=m.difference_quantity,
            unit_price=m.unit_price, difference_value=m.difference_value,
            reason=m.reason, resolution=m.resolution,
        )
        d.id = m.id
        return d

    def create_check(self, check: InventoryCheck) -> Result:
        m = InventoryCheckModel(
            check_code=check.check_code, check_date=check.check_date,
            warehouse_id=check.warehouse_id,
            status=InventoryCheckStatusDB.DRAFT,
            reference_doc=check.reference_doc, notes=check.notes,
            created_by=check.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in check.lines:
            lm = InventoryCheckLineModel(
                check_id=m.id, item_id=line.item_id, warehouse_id=line.warehouse_id or check.warehouse_id,
                batch_id=line.batch_id,
                book_quantity=line.book_quantity, physical_quantity=line.physical_quantity,
                difference_quantity=line.difference_quantity,
                unit_price=line.unit_price, difference_value=line.difference_value,
                reason=line.reason, resolution=line.resolution,
            )
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._check_to_domain(m))

    def get_check(self, check_id: int) -> Optional[InventoryCheck]:
        m = self.session.get(InventoryCheckModel, check_id)
        return self._check_to_domain(m) if m else None

    def list_checks(self, warehouse_id: Optional[int] = None, status: Optional[str] = None,
                    skip: int = 0, limit: int = 50) -> Tuple[List[InventoryCheck], int]:
        q = select(InventoryCheckModel)
        count_q = select(func.count()).select_from(InventoryCheckModel)
        if warehouse_id:
            q = q.where(InventoryCheckModel.warehouse_id == warehouse_id)
            count_q = count_q.where(InventoryCheckModel.warehouse_id == warehouse_id)
        if status:
            db_status = None
            for k, v in _INV_CHECK_STATUS_MAP.items():
                if k.value == status or v.value == status:
                    db_status = v
                    break
            if db_status:
                q = q.where(InventoryCheckModel.status == db_status)
                count_q = count_q.where(InventoryCheckModel.status == db_status)
        total = self.session.execute(count_q).scalar() or 0
        q = q.order_by(desc(InventoryCheckModel.check_date)).offset(skip).limit(limit)
        results = self.session.execute(q).scalars().all()
        return [self._check_to_domain(m) for m in results], total

    def update_check_status(self, check_id: int, status: InventoryCheckStatus,
                            approved_by: Optional[str] = None) -> Result:
        m = self.session.get(InventoryCheckModel, check_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_CHECK_NOT_FOUND, check_id=check_id))
        if m.status == InventoryCheckStatusDB.APPROVED:
            return Result.failure(AccountError(ErrorCodes.INV_CHECK_ALREADY_APPROVED, check_id=check_id))
        m.status = _INV_CHECK_STATUS_MAP.get(status, InventoryCheckStatusDB.DRAFT)
        if status == InventoryCheckStatus.APPROVED and approved_by:
            m.approved_by = approved_by
            m.approved_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._check_to_domain(m))

    # ── Adjustment ──────────────────────────────────────────────

    def _adj_to_domain(self, m: InventoryAdjustmentModel) -> InventoryAdjustment:
        d = InventoryAdjustment(
            adjustment_code=m.adjustment_code, adjustment_date=m.adjustment_date,
            warehouse_id=m.warehouse_id,
            adjustment_type=_REV_ADJ_TYPE.get(m.adjustment_type, AdjustmentType.OTHER),
            reason=m.reason, reference_doc=m.reference_doc,
            is_posted=m.is_posted, posted_at=m.posted_at,
            gl_journal_ref=m.gl_journal_ref,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )
        d.id = m.id
        if m.lines:
            d.lines = [self._adj_line_to_domain(l) for l in m.lines]
        return d

    def _adj_line_to_domain(self, m: InventoryAdjustmentLineModel) -> InventoryAdjustmentLine:
        d = InventoryAdjustmentLine(
            adjustment_id=m.adjustment_id, item_id=m.item_id, warehouse_id=m.warehouse_id,
            batch_id=m.batch_id,
            quantity_change=m.quantity_change, unit_price=m.unit_price,
            total_amount=m.total_amount, line_order=m.line_order,
            notes=m.notes or "",
        )
        d.id = m.id
        return d

    def create_adjustment(self, adj: InventoryAdjustment) -> Result:
        m = InventoryAdjustmentModel(
            adjustment_code=adj.adjustment_code, adjustment_date=adj.adjustment_date,
            warehouse_id=adj.warehouse_id,
            adjustment_type=_ADJ_TYPE_MAP.get(adj.adjustment_type, AdjustmentTypeDB.OTHER),
            reason=adj.reason, reference_doc=adj.reference_doc,
            is_posted=False, created_by=adj.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in adj.lines:
            lm = InventoryAdjustmentLineModel(
                adjustment_id=m.id, item_id=line.item_id,
                warehouse_id=line.warehouse_id or adj.warehouse_id,
                batch_id=line.batch_id,
                quantity_change=line.quantity_change, unit_price=line.unit_price,
                total_amount=line.total_amount or (abs(line.quantity_change) * line.unit_price),
                line_order=line.line_order, notes=line.notes,
            )
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._adj_to_domain(m))

    def get_adjustment(self, adjustment_id: int) -> Optional[InventoryAdjustment]:
        m = self.session.get(InventoryAdjustmentModel, adjustment_id)
        return self._adj_to_domain(m) if m else None

    def list_adjustments(self, warehouse_id: Optional[int] = None,
                         adjustment_type: Optional[str] = None,
                         skip: int = 0, limit: int = 50) -> Tuple[List[InventoryAdjustment], int]:
        q = select(InventoryAdjustmentModel)
        count_q = select(func.count()).select_from(InventoryAdjustmentModel)
        if warehouse_id:
            q = q.where(InventoryAdjustmentModel.warehouse_id == warehouse_id)
            count_q = count_q.where(InventoryAdjustmentModel.warehouse_id == warehouse_id)
        if adjustment_type:
            db_val = None
            for k, v in _ADJ_TYPE_MAP.items():
                if k.value == adjustment_type or v.value == adjustment_type:
                    db_val = v
                    break
            if db_val:
                q = q.where(InventoryAdjustmentModel.adjustment_type == db_val)
                count_q = count_q.where(InventoryAdjustmentModel.adjustment_type == db_val)
        total = self.session.execute(count_q).scalar() or 0
        q = q.order_by(desc(InventoryAdjustmentModel.adjustment_date)).offset(skip).limit(limit)
        results = self.session.execute(q).scalars().all()
        return [self._adj_to_domain(m) for m in results], total

    def post_adjustment(self, adjustment_id: int, gl_ref: Optional[str] = None) -> Result:
        m = self.session.get(InventoryAdjustmentModel, adjustment_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.INV_ADJ_NOT_FOUND, adjustment_id=adjustment_id))
        if m.is_posted:
            return Result.failure(AccountError(ErrorCodes.INV_ADJ_ALREADY_POSTED, adjustment_id=adjustment_id))
        m.is_posted = True
        m.posted_at = datetime.now(timezone.utc)
        m.gl_journal_ref = gl_ref
        self.session.flush()
        return Result.success(self._adj_to_domain(m))

    # ── GL Posting Helpers ──────────────────────────────────────

    def get_item_stock_value(self, item_id: int, warehouse_id: int) -> Decimal:
        item = self.session.get(InventoryItemModel, item_id)
        if not item:
            return Decimal("0")
        return _vnd(item.current_stock * item.cost_price)

    def get_item_gl_accounts(self, item_id: int) -> dict:
        item = self.session.get(InventoryItemModel, item_id)
        if not item:
            return {}
        if item.gl_inventory_account and item.gl_receipt_account:
            return {
                "gl_inventory_account": item.gl_inventory_account,
                "gl_receipt_account": item.gl_receipt_account,
                "gl_issue_account": item.gl_issue_account,
                "gl_sales_account": item.gl_sales_account,
                "gl_cost_of_sales": item.gl_cost_of_sales,
                "gl_return_account": item.gl_return_account,
            }
        cat = self.session.get(InventoryCategoryModel, item.category_id) if item.category_id else None
        if cat:
            return {
                "gl_inventory_account": item.gl_inventory_account or cat.gl_inventory_account,
                "gl_receipt_account": item.gl_receipt_account or cat.gl_receipt_account,
                "gl_issue_account": item.gl_issue_account or cat.gl_issue_account,
                "gl_sales_account": item.gl_sales_account or cat.gl_sales_account,
                "gl_cost_of_sales": item.gl_cost_of_sales or cat.gl_cost_of_sales,
                "gl_return_account": item.gl_return_account or cat.gl_return_account,
            }
        return {}

    # ── Dashboard / Metrics ─────────────────────────────────────

    def get_dashboard(self) -> dict:
        total_items = self.session.execute(
            select(func.count()).select_from(InventoryItemModel).where(
                InventoryItemModel.status == InventoryStatusDB.ACTIVE
            )
        ).scalar() or 0
        total_warehouses = self.session.execute(
            select(func.count()).select_from(WarehouseModel).where(WarehouseModel.is_active == True)
        ).scalar() or 0
        total_stock_value = self.session.execute(
            select(func.coalesce(func.sum(
                InventoryItemModel.current_stock * InventoryItemModel.cost_price
            ), 0)).select_from(InventoryItemModel)
        ).scalar() or Decimal("0")
        low_stock_items = self.session.execute(
            select(func.count()).select_from(InventoryItemModel).where(
                and_(InventoryItemModel.current_stock <= InventoryItemModel.reorder_point,
                     InventoryItemModel.reorder_point > 0)
            )
        ).scalar() or 0
        expired_batches = self.session.execute(
            select(func.count()).select_from(InventoryBatchModel).where(
                InventoryBatchModel.status == BatchStatusDB.EXPIRED
            )
        ).scalar() or 0
        pending_checks = self.session.execute(
            select(func.count()).select_from(InventoryCheckModel).where(
                InventoryCheckModel.status.in_([InventoryCheckStatusDB.DRAFT, InventoryCheckStatusDB.IN_PROGRESS])
            )
        ).scalar() or 0
        return {
            "total_items": total_items,
            "total_warehouses": total_warehouses,
            "total_stock_value": _vnd(total_stock_value),
            "low_stock_items": low_stock_items,
            "expired_batches": expired_batches,
            "pending_checks": pending_checks,
        }
