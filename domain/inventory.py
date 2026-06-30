from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, AccountError


class InventoryType(str, Enum):
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


class InventoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class MovementType(str, Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    RETURN_TO_SUPPLIER = "return_to_supplier"
    RETURN_FROM_CUSTOMER = "return_from_customer"
    ADJUSTMENT_INCREASE = "adjustment_increase"
    ADJUSTMENT_DECREASE = "adjustment_decrease"


class ValuationMethod(str, Enum):
    SPECIFIC = "specific"
    FIFO = "fifo"
    LIFO = "lifo"
    WEIGHTED_AVERAGE = "weighted_average"
    MOVING_AVERAGE = "moving_average"
    STANDARD = "standard"
    RETAIL = "retail"


class CheckMethod(str, Enum):
    PERIODIC = "periodic"
    PERPETUAL = "perpetual"


class InventoryCheckStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class BatchStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    QUARANTINED = "quarantined"
    DISPOSED = "disposed"


class SerialStatus(str, Enum):
    IN_STOCK = "in_stock"
    ISSUED = "issued"
    RETURNED = "returned"
    SCRAPPED = "scrapped"
    QUARANTINED = "quarantined"


class AdjustmentType(str, Enum):
    WRITE_OFF = "write_off"
    WRITE_ON = "write_on"
    DAMAGE = "damage"
    THEFT = "theft"
    DONATION = "donation"
    SAMPLE = "sample"
    ERROR_CORRECTION = "error_correction"
    REVALUATION = "revaluation"
    OTHER = "other"


class TransferStatus(str, Enum):
    DRAFT = "draft"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InventoryCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    inventory_type: InventoryType = InventoryType.MERCHANDISE
    valuation_method: ValuationMethod = ValuationMethod.WEIGHTED_AVERAGE
    gl_inventory_account: str = "152"
    gl_receipt_account: str = "331"
    gl_issue_account: str = "621"
    gl_sales_account: str = "632"
    gl_cost_of_sales: str = "632"
    gl_return_account: str = "521"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_CATEGORY_CODE_EMPTY)
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_CATEGORY_NAME_EMPTY)
        return v.strip()


class Warehouse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    name: str
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool = True
    allow_negative_stock: bool = False
    check_method: CheckMethod = CheckMethod.PERPETUAL
    gl_inventory_account: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_WAREHOUSE_CODE_EMPTY)
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_WAREHOUSE_NAME_EMPTY)
        return v.strip()


class InventoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    name: str
    category_id: int
    default_warehouse_id: Optional[int] = None
    inventory_type: InventoryType = InventoryType.MERCHANDISE
    status: InventoryStatus = InventoryStatus.ACTIVE
    valuation_method: Optional[ValuationMethod] = None
    unit: str = "cái"
    unit_price: Decimal = Field(default=Decimal("0"))
    cost_price: Decimal = Field(default=Decimal("0"))
    selling_price: Decimal = Field(default=Decimal("0"))
    min_stock: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    max_stock: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    reorder_point: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    reorder_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    current_stock: Decimal = Field(default=Decimal("0"))
    reserved_stock: Decimal = Field(default=Decimal("0"))
    available_stock: Decimal = Field(default=Decimal("0"))
    batch_tracking: bool = False
    serial_tracking: bool = False
    expiry_tracking: bool = False
    weight: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    hs_code: Optional[str] = None
    barcode: Optional[str] = None
    tax_rate: Decimal = Field(default=Decimal("10"), ge=Decimal("0"), le=Decimal("100"))
    image_url: Optional[str] = None
    description: Optional[str] = None
    gl_inventory_account: Optional[str] = None
    gl_receipt_account: Optional[str] = None
    gl_issue_account: Optional[str] = None
    gl_sales_account: Optional[str] = None
    gl_cost_of_sales: Optional[str] = None
    gl_return_account: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_ITEM_CODE_EMPTY)
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_ITEM_NAME_EMPTY)
        return v.strip()

    @field_validator("cost_price")
    @classmethod
    def validate_cost_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError(ErrorCodes.INV_NEGATIVE_PRICE)
        return v

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError(ErrorCodes.INV_NEGATIVE_PRICE)
        return v

    @field_validator("selling_price")
    @classmethod
    def validate_selling_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError(ErrorCodes.INV_NEGATIVE_PRICE)
        return v

    @model_validator(mode="after")
    def validate_stock(self) -> "InventoryItem":
        if self.available_stock != (self.current_stock - self.reserved_stock):
            self.available_stock = self.current_stock - self.reserved_stock
        return self


class InventoryBatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    warehouse_id: Optional[int] = None
    batch_code: str
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    received_date: date
    quantity: Decimal = Field(default=Decimal("0"))
    remaining_quantity: Decimal = Field(default=Decimal("0"))
    unit_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    status: BatchStatus = BatchStatus.ACTIVE
    supplier_batch: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("batch_code")
    @classmethod
    def validate_batch_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_BATCH_CODE_EMPTY)
        return v.strip()

    @model_validator(mode="after")
    def validate_expiry(self) -> "InventoryBatch":
        if self.manufacturing_date and self.expiry_date and self.expiry_date < self.manufacturing_date:
            raise AccountError(ErrorCodes.INV_EXPIRY_BEFORE_MANUFACTURING)
        return self


class SerialNumber(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    batch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    serial_code: str
    status: SerialStatus = SerialStatus.IN_STOCK
    receipt_date: Optional[date] = None
    issue_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("serial_code")
    @classmethod
    def validate_serial(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_SERIAL_CODE_EMPTY)
        return v.strip()


class InventoryReceipt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    receipt_code: str
    receipt_date: date
    warehouse_id: int
    supplier_id: Optional[int] = None
    supplier_invoice_ref: Optional[str] = None
    reference_doc: Optional[str] = None
    description: Optional[str] = None
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    gl_journal_ref: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: List["InventoryReceiptLine"] = []

    @field_validator("receipt_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_RECEIPT_CODE_EMPTY)
        return v.strip()


class InventoryReceiptLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    receipt_id: int = 0
    item_id: int
    warehouse_id: int
    batch_id: Optional[int] = None
    quantity: Decimal = Field(default=Decimal("0"), gt=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    tax_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    line_order: int = 0
    notes: Optional[str] = None

    @model_validator(mode="after")
    def calc_total(self) -> "InventoryReceiptLine":
        self.total_amount = self.quantity * self.unit_price
        return self


class InventoryIssue(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    issue_code: str
    issue_date: date
    warehouse_id: int
    department_id: Optional[int] = None
    customer_id: Optional[int] = None
    recipient_name: Optional[str] = None
    reference_doc: Optional[str] = None
    description: Optional[str] = None
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    gl_journal_ref: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: List["InventoryIssueLine"] = []

    @field_validator("issue_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_ISSUE_CODE_EMPTY)
        return v.strip()


class InventoryIssueLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    issue_id: int = 0
    item_id: int
    warehouse_id: int
    batch_id: Optional[int] = None
    quantity: Decimal = Field(default=Decimal("0"), gt=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    tax_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    line_order: int = 0
    cost_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    cost_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    notes: Optional[str] = None

    @model_validator(mode="after")
    def calc_totals(self) -> "InventoryIssueLine":
        self.total_amount = self.quantity * self.unit_price
        self.cost_amount = self.quantity * self.cost_price
        return self


class InventoryTransfer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    transfer_code: str
    transfer_date: date
    from_warehouse_id: int
    to_warehouse_id: int
    status: TransferStatus = TransferStatus.DRAFT
    reference_doc: Optional[str] = None
    description: Optional[str] = None
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    gl_journal_ref: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: List["InventoryTransferLine"] = []

    @field_validator("transfer_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_TRANSFER_CODE_EMPTY)
        return v.strip()

    @model_validator(mode="after")
    def validate_warehouses(self) -> "InventoryTransfer":
        if self.from_warehouse_id == self.to_warehouse_id:
            raise AccountError(ErrorCodes.INV_TRANSFER_SAME_WAREHOUSE)
        return self


class InventoryTransferLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    transfer_id: int = 0
    item_id: int
    quantity: Decimal = Field(default=Decimal("0"), gt=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    line_order: int = 0
    notes: Optional[str] = None

    @model_validator(mode="after")
    def calc_total(self) -> "InventoryTransferLine":
        self.total_amount = self.quantity * self.unit_price
        return self


class StockCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    warehouse_id: int
    period: str
    opening_quantity: Decimal = Field(default=Decimal("0"))
    opening_value: Decimal = Field(default=Decimal("0"))
    receipt_quantity: Decimal = Field(default=Decimal("0"))
    receipt_value: Decimal = Field(default=Decimal("0"))
    issue_quantity: Decimal = Field(default=Decimal("0"))
    issue_value: Decimal = Field(default=Decimal("0"))
    closing_quantity: Decimal = Field(default=Decimal("0"))
    closing_value: Decimal = Field(default=Decimal("0"))
    unit_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))


class InventoryCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    check_code: str
    check_date: date
    warehouse_id: int
    status: InventoryCheckStatus = InventoryCheckStatus.DRAFT
    reference_doc: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: List["InventoryCheckLine"] = []

    @field_validator("check_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_CHECK_CODE_EMPTY)
        return v.strip()


class InventoryCheckLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    check_id: int = 0
    item_id: int
    warehouse_id: int
    batch_id: Optional[int] = None
    book_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    physical_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    difference_quantity: Decimal = Field(default=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    difference_value: Decimal = Field(default=Decimal("0"))
    reason: Optional[str] = None
    resolution: Optional[str] = None

    @model_validator(mode="after")
    def calc_diff(self) -> "InventoryCheckLine":
        self.difference_quantity = self.physical_quantity - self.book_quantity
        self.difference_value = self.difference_quantity * self.unit_price
        return self


class InventoryAdjustment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    adjustment_code: str
    adjustment_date: date
    warehouse_id: int
    adjustment_type: AdjustmentType = AdjustmentType.OTHER
    reason: str
    reference_doc: Optional[str] = None
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    gl_journal_ref: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: List["InventoryAdjustmentLine"] = []

    @field_validator("adjustment_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_ADJ_CODE_EMPTY)
        return v.strip()

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.INV_ADJ_REASON_EMPTY)
        return v.strip()


class InventoryAdjustmentLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    adjustment_id: int = 0
    item_id: int
    warehouse_id: int
    batch_id: Optional[int] = None
    quantity_change: Decimal = Field(default=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"))
    line_order: int = 0
    notes: Optional[str] = None

    @model_validator(mode="after")
    def calc_total(self) -> "InventoryAdjustmentLine":
        self.total_amount = abs(self.quantity_change) * self.unit_price
        return self


class InventoryConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    default_valuation_method: ValuationMethod = ValuationMethod.WEIGHTED_AVERAGE
    auto_post_gl: bool = True
    check_method: CheckMethod = CheckMethod.PERPETUAL
    allow_negative_stock: bool = False
    enable_batch_tracking: bool = False
    enable_serial_tracking: bool = False
    enable_expiry_tracking: bool = False
    receipt_number_prefix: str = "NK"
    issue_number_prefix: str = "XK"
    transfer_number_prefix: str = "CK"
    check_number_prefix: str = "KK"
    adjustment_number_prefix: str = "DC"
    updated_at: Optional[datetime] = None


class InventoryDashboard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_items: int = 0
    total_warehouses: int = 0
    total_stock_value: Decimal = Decimal("0")
    total_receipts_month: int = 0
    total_issues_month: int = 0
    low_stock_items: int = 0
    expired_batches: int = 0
    pending_checks: int = 0
    slow_moving_items: int = 0
    monthly_receipt_value: Decimal = Decimal("0")
    monthly_issue_value: Decimal = Decimal("0")
    stock_turnover_ratio: Decimal = Decimal("0")
