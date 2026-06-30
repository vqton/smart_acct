import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class InventoryTypeDB(str, enum.Enum):
    RAW_MATERIAL = "raw_material"
    MATERIAL = "material"
    SEMI_FINISHED = "semi_finished"
    FINISHED_GOOD = "finished_good"
    MERCHANDISE = "merchandise"
    PACKAGING = "packaging"
    FUEL = "fuel"
    SPARE_PART = "spare_part"
    EQUIPMENT = "equipment"
    WASTE = "waste"
    OTHER = "other"


class InventoryStatusDB(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class MovementTypeDB(str, enum.Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    RETURN_TO_SUPPLIER = "return_to_supplier"
    RETURN_FROM_CUSTOMER = "return_from_customer"
    ADJUSTMENT_INCREASE = "adjustment_increase"
    ADJUSTMENT_DECREASE = "adjustment_decrease"


class ValuationMethodDB(str, enum.Enum):
    SPECIFIC = "specific"
    FIFO = "fifo"
    LIFO = "lifo"
    WEIGHTED_AVERAGE = "weighted_average"
    MOVING_AVERAGE = "moving_average"
    STANDARD = "standard"
    RETAIL = "retail"


class CheckMethodDB(str, enum.Enum):
    PERIODIC = "periodic"
    PERPETUAL = "perpetual"


class InventoryCheckStatusDB(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class BatchStatusDB(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    QUARANTINED = "quarantined"
    DISPOSED = "disposed"


class SerialStatusDB(str, enum.Enum):
    IN_STOCK = "in_stock"
    ISSUED = "issued"
    RETURNED = "returned"
    SCRAPPED = "scrapped"
    QUARANTINED = "quarantined"


class AdjustmentTypeDB(str, enum.Enum):
    WRITE_OFF = "write_off"
    WRITE_ON = "write_on"
    DAMAGE = "damage"
    THEFT = "theft"
    DONATION = "donation"
    SAMPLE = "sample"
    ERROR_CORRECTION = "error_correction"
    REVALUATION = "revaluation"
    OTHER = "other"


class TransferStatusDB(str, enum.Enum):
    DRAFT = "draft"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InventoryCategoryModel(Base):
    __tablename__ = "inv_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("inv_categories.id"), nullable=True)
    inventory_type = Column(SAEnum(InventoryTypeDB), nullable=False)
    valuation_method = Column(SAEnum(ValuationMethodDB), nullable=False)
    gl_inventory_account = Column(String(20), nullable=False, server_default="152")
    gl_receipt_account = Column(String(20), nullable=False, server_default="331")
    gl_issue_account = Column(String(20), nullable=False, server_default="621")
    gl_sales_account = Column(String(20), nullable=False, server_default="632")
    gl_cost_of_sales = Column(String(20), nullable=False, server_default="632")
    gl_return_account = Column(String(20), nullable=False, server_default="521")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    children = relationship("InventoryCategoryModel", back_populates="parent", lazy="selectin",
                            cascade="all, delete-orphan")
    parent = relationship("InventoryCategoryModel", back_populates="children", remote_side=[id], lazy="selectin")
    items = relationship("InventoryItemModel", back_populates="category", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryCategoryModel(id={self.id}, code='{self.code}')>"


class WarehouseModel(Base):
    __tablename__ = "inv_warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False)
    address = Column(Text, nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    allow_negative_stock = Column(Boolean, default=False, nullable=False)
    check_method = Column(SAEnum(CheckMethodDB), nullable=False)
    gl_inventory_account = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<WarehouseModel(id={self.id}, code='{self.code}')>"


class InventoryItemModel(Base):
    __tablename__ = "inv_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("inv_categories.id"), nullable=False, index=True)
    default_warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=True)
    inventory_type = Column(SAEnum(InventoryTypeDB), nullable=False)
    status = Column(SAEnum(InventoryStatusDB), default=InventoryStatusDB.ACTIVE, nullable=False)
    valuation_method = Column(SAEnum(ValuationMethodDB), nullable=True)
    unit = Column(String(50), nullable=False, server_default="cái")
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    cost_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    selling_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    min_stock = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    max_stock = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reorder_point = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reorder_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_stock = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reserved_stock = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    available_stock = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    batch_tracking = Column(Boolean, default=False, nullable=False)
    serial_tracking = Column(Boolean, default=False, nullable=False)
    expiry_tracking = Column(Boolean, default=False, nullable=False)
    weight = Column(Numeric(18, 4), nullable=True)
    volume = Column(Numeric(18, 4), nullable=True)
    hs_code = Column(String(20), nullable=True)
    barcode = Column(String(100), nullable=True)
    tax_rate = Column(Numeric(5, 2), default=Decimal("10"), nullable=False)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    gl_inventory_account = Column(String(20), nullable=True)
    gl_receipt_account = Column(String(20), nullable=True)
    gl_issue_account = Column(String(20), nullable=True)
    gl_sales_account = Column(String(20), nullable=True)
    gl_cost_of_sales = Column(String(20), nullable=True)
    gl_return_account = Column(String(20), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    category = relationship("InventoryCategoryModel", back_populates="items", lazy="selectin")
    default_warehouse = relationship("WarehouseModel", lazy="selectin")
    batches = relationship("InventoryBatchModel", back_populates="item", lazy="selectin", cascade="all, delete-orphan")
    serials = relationship("SerialNumberModel", back_populates="item", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InventoryItemModel(id={self.id}, code='{self.code}')>"


class InventoryBatchModel(Base):
    __tablename__ = "inv_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=True)
    batch_code = Column(String(100), nullable=False)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    remaining_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unit_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    status = Column(SAEnum(BatchStatusDB), default=BatchStatusDB.ACTIVE, nullable=False)
    supplier_batch = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("InventoryItemModel", back_populates="batches", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<InventoryBatchModel(id={self.id}, batch='{self.batch_code}')>"


class SerialNumberModel(Base):
    __tablename__ = "inv_serials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("inv_batches.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=True)
    serial_code = Column(String(100), nullable=False)
    status = Column(SAEnum(SerialStatusDB), default=SerialStatusDB.IN_STOCK, nullable=False)
    receipt_date = Column(Date, nullable=True)
    issue_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("InventoryItemModel", back_populates="serials", lazy="selectin")
    batch = relationship("InventoryBatchModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<SerialNumberModel(id={self.id}, serial='{self.serial_code}')>"


class InventoryReceiptModel(Base):
    __tablename__ = "inv_receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_code = Column(String(50), unique=True, nullable=False, index=True)
    receipt_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False, index=True)
    supplier_id = Column(Integer, nullable=True)
    supplier_invoice_ref = Column(String(100), nullable=True)
    reference_doc = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    gl_journal_ref = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    warehouse = relationship("WarehouseModel", lazy="selectin")
    lines = relationship("InventoryReceiptLineModel", back_populates="receipt",
                         lazy="selectin", cascade="all, delete-orphan",
                         order_by="InventoryReceiptLineModel.line_order")

    def __repr__(self) -> str:
        return f"<InventoryReceiptModel(id={self.id}, code='{self.receipt_code}')>"


class InventoryReceiptLineModel(Base):
    __tablename__ = "inv_receipt_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("inv_receipts.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("inv_batches.id"), nullable=True)
    quantity = Column(Numeric(18, 2), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    discount_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    line_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    receipt = relationship("InventoryReceiptModel", back_populates="lines", lazy="selectin")
    item = relationship("InventoryItemModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")
    batch = relationship("InventoryBatchModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryReceiptLineModel(id={self.id}, item={self.item_id})>"


class InventoryIssueModel(Base):
    __tablename__ = "inv_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_code = Column(String(50), unique=True, nullable=False, index=True)
    issue_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False, index=True)
    department_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=True)
    recipient_name = Column(String(200), nullable=True)
    reference_doc = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    gl_journal_ref = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    warehouse = relationship("WarehouseModel", lazy="selectin")
    lines = relationship("InventoryIssueLineModel", back_populates="issue",
                         lazy="selectin", cascade="all, delete-orphan",
                         order_by="InventoryIssueLineModel.line_order")

    def __repr__(self) -> str:
        return f"<InventoryIssueModel(id={self.id}, code='{self.issue_code}')>"


class InventoryIssueLineModel(Base):
    __tablename__ = "inv_issue_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("inv_issues.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("inv_batches.id"), nullable=True)
    quantity = Column(Numeric(18, 2), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    discount_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    line_order = Column(Integer, default=0, nullable=False)
    cost_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    cost_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    notes = Column(Text, nullable=True)

    issue = relationship("InventoryIssueModel", back_populates="lines", lazy="selectin")
    item = relationship("InventoryItemModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")
    batch = relationship("InventoryBatchModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryIssueLineModel(id={self.id}, item={self.item_id})>"


class InventoryTransferModel(Base):
    __tablename__ = "inv_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_code = Column(String(50), unique=True, nullable=False, index=True)
    transfer_date = Column(Date, nullable=False)
    from_warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    to_warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    status = Column(SAEnum(TransferStatusDB), default=TransferStatusDB.DRAFT, nullable=False)
    reference_doc = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    gl_journal_ref = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    from_warehouse = relationship("WarehouseModel", foreign_keys=[from_warehouse_id], lazy="selectin")
    to_warehouse = relationship("WarehouseModel", foreign_keys=[to_warehouse_id], lazy="selectin")
    lines = relationship("InventoryTransferLineModel", back_populates="transfer",
                         lazy="selectin", cascade="all, delete-orphan",
                         order_by="InventoryTransferLineModel.line_order")

    def __repr__(self) -> str:
        return f"<InventoryTransferModel(id={self.id}, code='{self.transfer_code}')>"


class InventoryTransferLineModel(Base):
    __tablename__ = "inv_transfer_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(Integer, ForeignKey("inv_transfers.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False)
    quantity = Column(Numeric(18, 2), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    line_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    transfer = relationship("InventoryTransferModel", back_populates="lines", lazy="selectin")
    item = relationship("InventoryItemModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryTransferLineModel(id={self.id}, item={self.item_id})>"


class StockCardModel(Base):
    __tablename__ = "inv_stock_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)
    opening_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    opening_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    receipt_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    receipt_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    issue_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    issue_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    closing_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    closing_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unit_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    item = relationship("InventoryItemModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<StockCardModel(item={self.item_id}, wh={self.warehouse_id}, period='{self.period}')>"


class InventoryCheckModel(Base):
    __tablename__ = "inv_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_code = Column(String(50), unique=True, nullable=False, index=True)
    check_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False, index=True)
    status = Column(SAEnum(InventoryCheckStatusDB), default=InventoryCheckStatusDB.DRAFT, nullable=False)
    reference_doc = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    warehouse = relationship("WarehouseModel", lazy="selectin")
    lines = relationship("InventoryCheckLineModel", back_populates="check",
                         lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InventoryCheckModel(id={self.id}, code='{self.check_code}')>"


class InventoryCheckLineModel(Base):
    __tablename__ = "inv_check_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey("inv_checks.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("inv_batches.id"), nullable=True)
    book_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    physical_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    difference_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    difference_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reason = Column(String(500), nullable=True)
    resolution = Column(String(500), nullable=True)

    check = relationship("InventoryCheckModel", back_populates="lines", lazy="selectin")
    item = relationship("InventoryItemModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")
    batch = relationship("InventoryBatchModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryCheckLineModel(id={self.id}, item={self.item_id})>"


class InventoryAdjustmentModel(Base):
    __tablename__ = "inv_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    adjustment_code = Column(String(50), unique=True, nullable=False, index=True)
    adjustment_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False, index=True)
    adjustment_type = Column(SAEnum(AdjustmentTypeDB), nullable=False)
    reason = Column(Text, nullable=False)
    reference_doc = Column(String(100), nullable=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    gl_journal_ref = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    warehouse = relationship("WarehouseModel", lazy="selectin")
    lines = relationship("InventoryAdjustmentLineModel", back_populates="adjustment",
                         lazy="selectin", cascade="all, delete-orphan",
                         order_by="InventoryAdjustmentLineModel.line_order")

    def __repr__(self) -> str:
        return f"<InventoryAdjustmentModel(id={self.id}, code='{self.adjustment_code}')>"


class InventoryAdjustmentLineModel(Base):
    __tablename__ = "inv_adjustment_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    adjustment_id = Column(Integer, ForeignKey("inv_adjustments.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("inv_warehouses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("inv_batches.id"), nullable=True)
    quantity_change = Column(Numeric(18, 2), nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    line_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    adjustment = relationship("InventoryAdjustmentModel", back_populates="lines", lazy="selectin")
    item = relationship("InventoryItemModel", lazy="selectin")
    warehouse = relationship("WarehouseModel", lazy="selectin")
    batch = relationship("InventoryBatchModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InventoryAdjustmentLineModel(id={self.id}, item={self.item_id})>"
