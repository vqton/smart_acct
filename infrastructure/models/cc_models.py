import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class CCDCTypeDB(str, enum.Enum):
    TOOL = "tool"
    EQUIPMENT = "equipment"
    MOLD = "mold"
    JIG = "jig"
    PATTERN = "pattern"
    CONTAINER = "container"
    PROTECTIVE_GEAR = "protective_gear"
    INSTRUMENT = "instrument"
    FIXTURE = "fixture"
    OTHER = "other"


class AllocationMethodDB(str, enum.Enum):
    ONE_TIME = "one_time"
    TWO_TIME = "two_time"
    MULTI_PERIOD = "multi_period"


class CCDCStatusDB(str, enum.Enum):
    IN_STOCK = "in_stock"
    IN_USE = "in_use"
    DAMAGED = "damaged"
    DISPOSED = "disposed"
    TRANSFERRED = "transferred"


class AllocationStatusDB(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_ALLOCATED = "partially_allocated"
    FULLY_ALLOCATED = "fully_allocated"


class TransactionTypeDB(str, enum.Enum):
    RECEIPT = "receipt"
    ISSUANCE = "issuance"
    RETURN_TO_STOCK = "return_to_stock"
    DISPOSAL = "disposal"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


class CCInventoryStatusDB(str, enum.Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    RESOLVED = "resolved"


class ResponsibilityTypeDB(str, enum.Enum):
    USER = "user"
    KEEPER = "keeper"
    MANAGER = "manager"


class CCategoryModel(Base):
    __tablename__ = "cc_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    default_allocation_method = Column(SAEnum(AllocationMethodDB), default=AllocationMethodDB.ONE_TIME, nullable=False)
    default_useful_life_months = Column(Integer, nullable=True)
    gl_asset_account = Column(String(20), default="153", nullable=False)
    gl_alloc_account = Column(String(20), nullable=True)
    gl_expense_account = Column(String(20), default="627", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    items = relationship("CCDCItemModel", back_populates="category", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCategoryModel(id={self.id}, code='{self.code}')>"


class CCDCItemModel(Base):
    __tablename__ = "cc_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("cc_categories.id"), nullable=False, index=True)
    cc_type = Column(SAEnum(CCDCTypeDB), default=CCDCTypeDB.TOOL, nullable=False)
    status = Column(SAEnum(CCDCStatusDB), default=CCDCStatusDB.IN_STOCK, nullable=False)
    allocation_method = Column(SAEnum(AllocationMethodDB), default=AllocationMethodDB.ONE_TIME, nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("1"), nullable=False)
    unit = Column(String(50), default="cái", nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocated_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    remaining_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocation_status = Column(SAEnum(AllocationStatusDB), default=AllocationStatusDB.PENDING, nullable=False)
    useful_life_months = Column(Integer, nullable=True)
    allocation_start_period = Column(String(7), nullable=True)
    department_id = Column(Integer, nullable=True)
    employee_id = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    supplier = Column(String(300), nullable=True)
    invoice_ref = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    in_use_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    responsibility_type = Column(SAEnum(ResponsibilityTypeDB), default=ResponsibilityTypeDB.USER, nullable=False)
    responsible_person = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    category = relationship("CCategoryModel", back_populates="items", lazy="selectin")
    allocations = relationship("CCDCAllocationModel", back_populates="item", lazy="selectin",
                               cascade="all, delete-orphan")
    transactions = relationship("CCDCTransactionModel", back_populates="item", lazy="selectin",
                                cascade="all, delete-orphan")
    transfers = relationship("CCDCTransferModel", back_populates="item", lazy="selectin",
                             cascade="all, delete-orphan")
    inventory_lines = relationship("CCDCInventoryLineModel", back_populates="item", lazy="selectin")
    write_offs = relationship("CCDCWriteOffModel", back_populates="item", lazy="selectin",
                              cascade="all, delete-orphan")
    spare_parts = relationship("CCDCSparePartModel", back_populates="item", lazy="selectin",
                               cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CCDCItemModel(id={self.id}, code='{self.code}')>"


class CCDCAllocationModel(Base):
    __tablename__ = "cc_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    allocation_method = Column(SAEnum(AllocationMethodDB), nullable=False)
    total_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocated_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    remaining_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    start_period = Column(String(7), nullable=False)
    end_period = Column(String(7), nullable=True)
    total_periods = Column(Integer, nullable=True)
    amount_per_period = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    status = Column(SAEnum(AllocationStatusDB), default=AllocationStatusDB.PENDING, nullable=False)
    gl_account_credit = Column(String(20), default="153", nullable=False)
    gl_account_debit = Column(String(20), default="627", nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    item = relationship("CCDCItemModel", back_populates="allocations", lazy="selectin")
    lines = relationship("CCDCAllocationLineModel", back_populates="allocation", lazy="selectin",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CCDCAllocationModel(id={self.id}, item={self.item_id})>"


class CCDCAllocationLineModel(Base):
    __tablename__ = "cc_allocation_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    allocation_id = Column(Integer, ForeignKey("cc_allocations.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)
    planned_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    actual_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    gl_journal_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    allocation = relationship("CCDCAllocationModel", back_populates="lines", lazy="selectin")
    item = relationship("CCDCItemModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCAllocationLineModel(id={self.id}, period='{self.period}')>"


class CCDCTransactionModel(Base):
    __tablename__ = "cc_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    transaction_type = Column(SAEnum(TransactionTypeDB), nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("1"), nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    period = Column(String(7), nullable=False, index=True)
    department_id = Column(Integer, nullable=True)
    employee_id = Column(Integer, nullable=True)
    reference_doc = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("CCDCItemModel", back_populates="transactions", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCTransactionModel(id={self.id}, type='{self.transaction_type}')>"


class CCDCTransferModel(Base):
    __tablename__ = "cc_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    from_department_id = Column(Integer, nullable=True)
    to_department_id = Column(Integer, nullable=True)
    from_employee_id = Column(Integer, nullable=True)
    to_employee_id = Column(Integer, nullable=True)
    from_location = Column(String(200), nullable=True)
    to_location = Column(String(200), nullable=True)
    quantity = Column(Numeric(18, 2), default=Decimal("1"), nullable=False)
    transfer_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("CCDCItemModel", back_populates="transfers", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCTransferModel(id={self.id}, item={self.item_id})>"


class CCDCInventoryModel(Base):
    __tablename__ = "cc_inventories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_date = Column(Date, nullable=False, index=True)
    department_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SAEnum(CCInventoryStatusDB), default=CCInventoryStatusDB.DRAFT, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    lines = relationship("CCDCInventoryLineModel", back_populates="inventory",
                         lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CCDCInventoryModel(id={self.id}, date='{self.inventory_date}')>"


class CCDCInventoryLineModel(Base):
    __tablename__ = "cc_inventory_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(Integer, ForeignKey("cc_inventories.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    book_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    physical_quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    difference = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    difference_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reason = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)

    inventory = relationship("CCDCInventoryModel", back_populates="lines", lazy="selectin")
    item = relationship("CCDCItemModel", back_populates="inventory_lines", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCInventoryLineModel(id={self.id}, inventory={self.inventory_id})>"


class CCDCWriteOffModel(Base):
    __tablename__ = "cc_write_offs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    write_off_date = Column(Date, nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("1"), nullable=False)
    remaining_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reason = Column(Text, nullable=False)
    disposal_method = Column(String(100), nullable=True)
    proceeds = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    loss_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    approved_by = Column(String(100), nullable=True)
    document_ref = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("CCDCItemModel", back_populates="write_offs", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCWriteOffModel(id={self.id}, item={self.item_id})>"


class CCDCSparePartModel(Base):
    __tablename__ = "cc_spare_parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("cc_items.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(300), nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unit = Column(String(50), default="cái", nullable=False)
    unit_price = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = relationship("CCDCItemModel", back_populates="spare_parts", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CCDCSparePartModel(id={self.id}, code='{self.code}')>"


class CCDCImportLogModel(Base):
    __tablename__ = "cc_import_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(300), nullable=False)
    import_type = Column(String(50), nullable=False)
    import_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total_rows = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    errors = Column(JSON, nullable=True)
    created_by = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<CCDCImportLogModel(id={self.id}, file='{self.filename}')>"
