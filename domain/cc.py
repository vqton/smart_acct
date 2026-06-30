from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, AccountError


class CCDCType(str, Enum):
    tool = "tool"
    equipment = "equipment"
    mold = "mold"
    jig = "jig"
    pattern = "pattern"
    container = "container"
    protective_gear = "protective_gear"
    instrument = "instrument"
    fixture = "fixture"
    other = "other"


class AllocationMethod(str, Enum):
    one_time = "one_time"
    two_time = "two_time"
    multi_period = "multi_period"


class CCDCStatus(str, Enum):
    in_stock = "in_stock"
    in_use = "in_use"
    damaged = "damaged"
    disposed = "disposed"
    transferred = "transferred"


class AllocationStatus(str, Enum):
    pending = "pending"
    partially_allocated = "partially_allocated"
    fully_allocated = "fully_allocated"


class TransactionType(str, Enum):
    receipt = "receipt"
    issuance = "issuance"
    return_to_stock = "return_to_stock"
    disposal = "disposal"
    transfer_out = "transfer_out"
    transfer_in = "transfer_in"


class InventoryStatus(str, Enum):
    draft = "draft"
    completed = "completed"
    resolved = "resolved"


class ResponsibilityType(str, Enum):
    user = "user"
    keeper = "keeper"
    manager = "manager"


class CCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None
    default_allocation_method: AllocationMethod = AllocationMethod.one_time
    default_useful_life_months: Optional[int] = None
    gl_asset_account: str = "153"
    gl_alloc_account: Optional[str] = None
    gl_expense_account: str = "627"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.CC_CODE_EMPTY)
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.CC_NAME_EMPTY)
        return v.strip()

    @field_validator("default_allocation_method")
    @classmethod
    def validate_allocation_method(cls, v: AllocationMethod) -> AllocationMethod:
        return v

    @field_validator("default_useful_life_months")
    @classmethod
    def validate_life(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 36):
            raise AccountError(ErrorCodes.CC_USEFUL_LIFE_RANGE_INVALID, months=v)
        return v


class CCDCItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    name: str
    category_id: int
    cc_type: CCDCType = CCDCType.tool
    status: CCDCStatus = CCDCStatus.in_stock
    allocation_method: AllocationMethod = AllocationMethod.one_time
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    unit: str = "cái"
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_cost: Decimal = Field(default=Decimal("0"))
    allocated_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    remaining_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    allocation_status: AllocationStatus = AllocationStatus.pending
    useful_life_months: Optional[int] = None
    allocation_start_period: Optional[str] = None
    department_id: Optional[int] = None
    employee_id: Optional[int] = None
    location: Optional[str] = None
    supplier: Optional[str] = None
    invoice_ref: Optional[str] = None
    purchase_date: Optional[date] = None
    in_use_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    responsibility_type: ResponsibilityType = ResponsibilityType.user
    responsible_person: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.CC_CODE_EMPTY)
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise AccountError(ErrorCodes.CC_NAME_EMPTY)
        return v.strip()

    @field_validator("total_cost")
    @classmethod
    def validate_total_cost(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError(ErrorCodes.CC_NEGATIVE_COST)
        return v

    @model_validator(mode="after")
    def validate_allocated(self) -> "CCDCItem":
        if self.allocated_amount > self.total_cost:
            raise AccountError(ErrorCodes.CC_ALLOCATION_EXCEEDS_COST)
        self.remaining_amount = self.total_cost - self.allocated_amount
        return self

    @model_validator(mode="after")
    def validate_dates(self) -> "CCDCItem":
        if self.purchase_date and self.in_use_date and self.in_use_date < self.purchase_date:
            raise AccountError(ErrorCodes.CC_IN_USE_BEFORE_PURCHASE)
        return self


class CCDCAllocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    allocation_method: AllocationMethod
    total_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    allocated_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    remaining_amount: Decimal = Field(default=Decimal("0"))
    start_period: str
    end_period: Optional[str] = None
    total_periods: Optional[int] = None
    amount_per_period: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    status: AllocationStatus = AllocationStatus.pending
    gl_account_credit: str = "153"
    gl_account_debit: str = "627"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("start_period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        import re
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise AccountError(ErrorCodes.CC_INVALID_PERIOD, period=v)
        return v


class CCDCAllocationLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    allocation_id: int
    item_id: int
    period: str
    planned_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    actual_amount: Decimal = Field(default=Decimal("0"))
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    gl_journal_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        import re
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise AccountError(ErrorCodes.CC_INVALID_PERIOD, period=v)
        return v


class CCDCTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    transaction_type: TransactionType
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    transaction_date: date
    period: str
    department_id: Optional[int] = None
    employee_id: Optional[int] = None
    reference_doc: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        import re
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise AccountError(ErrorCodes.CC_INVALID_PERIOD, period=v)
        return v


class CCDCTransfer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    from_department_id: Optional[int] = None
    to_department_id: Optional[int] = None
    from_employee_id: Optional[int] = None
    to_employee_id: Optional[int] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    transfer_date: date
    reason: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


class CCDCInventory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    inventory_date: date
    department_id: Optional[int] = None
    notes: Optional[str] = None
    status: InventoryStatus = InventoryStatus.draft
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    lines: List["CCDCInventoryLine"] = []


class CCDCInventoryLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    inventory_id: int = 0
    item_id: int
    book_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    physical_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    difference: Decimal = Field(default=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    difference_amount: Decimal = Field(default=Decimal("0"))
    reason: Optional[str] = None
    resolution: Optional[str] = None

    @model_validator(mode="after")
    def calc_diff(self) -> "CCDCInventoryLine":
        self.difference = self.physical_quantity - self.book_quantity
        self.difference_amount = self.difference * self.unit_price
        return self


class CCDCWriteOff(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    write_off_date: date
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    remaining_value: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    reason: str
    disposal_method: Optional[str] = None
    proceeds: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    loss_amount: Decimal = Field(default=Decimal("0"))
    approved_by: Optional[str] = None
    document_ref: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

    @model_validator(mode="after")
    def calc_loss(self) -> "CCDCWriteOff":
        self.loss_amount = self.remaining_value - self.proceeds
        if self.loss_amount < Decimal("0"):
            self.loss_amount = Decimal("0")
        return self


class CCDCSparePart(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: int
    code: str
    name: str
    quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    unit: str = "cái"
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_value: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    location: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def calc_total(self) -> "CCDCSparePart":
        self.total_value = self.unit_price * self.quantity
        return self


class CCDCImportLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    filename: str
    import_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_rows: int = 0
    success_count: int = 0
    error_count: int = 0
    errors: Optional[List[Dict[str, Any]]] = None
    created_by: Optional[str] = None
