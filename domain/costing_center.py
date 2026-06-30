from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, AccountError


class CostCenterType(str, Enum):
    cost = "cost"
    profit = "profit"
    investment = "investment"
    service = "service"
    admin = "admin"
    selling = "selling"
    production = "production"
    project = "project"
    virtual = "virtual"


class DriverType(str, Enum):
    quantity = "quantity"
    percentage = "percentage"
    rate = "rate"
    actual = "actual"


class AllocationMethod(str, Enum):
    direct = "direct"
    percentage = "percentage"
    proportional = "proportional"


class AllocationRunStatus(str, Enum):
    draft = "draft"
    posted = "posted"
    reversed = "reversed"


class CostObjectType(str, Enum):
    product = "product"
    project = "project"
    sales_order = "sales_order"
    campaign = "campaign"
    customer = "customer"
    department = "department"


class VarianceType(str, Enum):
    favorable = "favorable"
    unfavorable = "unfavorable"
    neutral = "neutral"


class RuleApprovalStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


# ── Cost Center ────────────────────────────────────────────────────────


class CostCenter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str = Field(..., max_length=20, pattern=r'^[A-Z0-9_-]+$')
    name: str = Field(..., max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    cost_center_type: CostCenterType = CostCenterType.cost
    parent_id: Optional[int] = None
    level: int = Field(default=1, ge=1, le=10)
    path: str = Field(default="", max_length=500)
    manager_employee_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    department_code: Optional[str] = Field(None, max_length=50)
    is_cost_collector: bool = True
    is_active: bool = True
    valid_from: date = Field(default_factory=lambda: date.today())
    valid_to: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_CENTER_CODE_EMPTY")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_CENTER_NAME_EMPTY")
        return v.strip()

    @model_validator(mode="after")
    def validate_dates(self) -> "CostCenter":
        if self.valid_to and self.valid_from and self.valid_to < self.valid_from:
            raise AccountError("COST_CENTER_INVALID_DATE")
        return self


class CostCenterCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., max_length=20, pattern=r'^[A-Z0-9_-]+$')
    name: str = Field(..., max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    cost_center_type: CostCenterType = CostCenterType.cost
    parent_id: Optional[int] = None
    manager_employee_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    department_code: Optional[str] = Field(None, max_length=50)
    is_cost_collector: bool = True
    is_active: bool = True
    valid_from: date = Field(default_factory=lambda: date.today())
    valid_to: Optional[date] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_CENTER_CODE_EMPTY")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_CENTER_NAME_EMPTY")
        return v.strip()


class CostCenterUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    cost_center_type: Optional[CostCenterType] = None
    manager_employee_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    department_code: Optional[str] = Field(None, max_length=50)
    is_cost_collector: Optional[bool] = None
    is_active: Optional[bool] = None
    valid_to: Optional[date] = None


# ── Cost Driver ────────────────────────────────────────────────────────


class CostDriver(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    driver_type: DriverType
    source_module: Optional[str] = Field(None, max_length=50)
    source_account_code: Optional[str] = Field(None, max_length=20)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    formula: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    created_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_DRIVER_CODE_EMPTY")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_DRIVER_NAME_EMPTY")
        return v.strip()


class CostDriverCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    driver_type: DriverType
    source_module: Optional[str] = Field(None, max_length=50)
    source_account_code: Optional[str] = Field(None, max_length=20)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    formula: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


# ── Allocation Rules ───────────────────────────────────────────────────


class CostAllocationRuleTarget(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    rule_id: int = 0
    target_cost_center_id: int
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    created_at: Optional[datetime] = None


class CostAllocationRule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    rule_code: str = Field(..., max_length=20)
    rule_name: str = Field(..., max_length=200)
    source_cost_center_id: int
    driver_id: int
    allocation_method: AllocationMethod
    targets: List[CostAllocationRuleTarget] = Field(default_factory=list)
    gl_debit_account_code: str = Field(..., max_length=20)
    gl_credit_account_code: str = Field(..., max_length=20)
    priority_order: int = Field(default=0, ge=0)
    effective_from: date
    effective_to: Optional[date] = None
    approval_status: RuleApprovalStatus = RuleApprovalStatus.draft
    approved_by: Optional[str] = Field(None, max_length=100)
    approved_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_by: str = Field(..., max_length=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("rule_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_RULE_CODE_EMPTY")
        return v.strip()

    @field_validator("rule_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_RULE_NAME_EMPTY")
        return v.strip()


class CostAllocationRuleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_code: str = Field(..., max_length=20)
    rule_name: str = Field(..., max_length=200)
    source_cost_center_id: int
    driver_id: int
    allocation_method: AllocationMethod
    targets: List[CostAllocationRuleTarget]
    gl_debit_account_code: str = Field(..., max_length=20)
    gl_credit_account_code: str = Field(..., max_length=20)
    priority_order: int = Field(default=0, ge=0)
    effective_from: date
    effective_to: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_by: str = Field(..., max_length=100)


class CostAllocationRuleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_name: Optional[str] = Field(None, max_length=200)
    driver_id: Optional[int] = None
    allocation_method: Optional[AllocationMethod] = None
    targets: Optional[List[CostAllocationRuleTarget]] = None
    gl_debit_account_code: Optional[str] = Field(None, max_length=20)
    gl_credit_account_code: Optional[str] = Field(None, max_length=20)
    priority_order: Optional[int] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


# ── Allocation Run ─────────────────────────────────────────────────────


class CostAllocationLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    run_id: Optional[int] = None
    source_cost_center_id: int
    target_cost_center_id: int
    rule_id: Optional[int] = None
    driver_id: Optional[int] = None
    gl_account_code: str = Field(..., max_length=20)
    original_amount: Decimal = Decimal("0")
    allocated_amount: Decimal = Decimal("0")
    driver_quantity: Optional[Decimal] = None
    driver_rate: Optional[Decimal] = None
    allocation_basis_description: Optional[str] = Field(None, max_length=500)


class CostAllocationRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    run_code: str
    period_key: str = Field(..., max_length=6, pattern=r'^\d{6}$')
    fiscal_year: int
    period_month: int = Field(..., ge=1, le=12)
    run_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_by: str = Field(..., max_length=100)
    status: AllocationRunStatus = AllocationRunStatus.draft
    total_allocated_amount: Decimal = Decimal("0")
    lines: List[CostAllocationLine] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: Optional[datetime] = None


# ── Cost Object ────────────────────────────────────────────────────────


class CostObject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    object_type: CostObjectType
    parent_object_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    external_ref_id: Optional[int] = None
    external_ref_type: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    custom_attributes: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_OBJECT_CODE_EMPTY")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("COST_OBJECT_NAME_EMPTY")
        return v.strip()


class CostObjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    object_type: CostObjectType
    parent_object_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    external_ref_id: Optional[int] = None
    external_ref_type: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    custom_attributes: Optional[Dict[str, Any]] = None


# ── Cost Accumulation ──────────────────────────────────────────────────


class CostAccumulation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    cost_object_id: int
    cost_center_id: int
    gl_account_code: str = Field(..., max_length=20)
    period_key: str = Field(..., max_length=6)
    direct_cost_amount: Decimal = Decimal("0")
    allocated_cost_amount: Decimal = Decimal("0")
    source_type: Optional[str] = Field(None, max_length=20)
    source_reference: Optional[str] = Field(None, max_length=50)
    created_at: Optional[datetime] = None

    @property
    def total_cost_amount(self) -> Decimal:
        return self.direct_cost_amount + self.allocated_cost_amount


# ── Budget / Actual / Variance ─────────────────────────────────────────


class CostCenterBudget(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    cost_center_id: int
    fiscal_year: int
    period_key: str = Field(..., max_length=6)
    gl_account_code: str = Field(..., max_length=20)
    budget_amount: Decimal = Decimal("0")
    revised_amount: Decimal = Decimal("0")
    budget_version_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)


class CostCenterActual(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    cost_center_id: int
    period_key: str = Field(..., max_length=6)
    gl_account_code: str = Field(..., max_length=20)
    actual_amount: Decimal = Decimal("0")
    commitment_amount: Decimal = Decimal("0")
    allocated_amount: Decimal = Decimal("0")
    source_reference: Optional[str] = Field(None, max_length=100)


class CostCenterVariance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    cost_center_id: int
    period_key: str = Field(..., max_length=6)
    gl_account_code: str = Field(..., max_length=20)
    budget_amount: Decimal = Decimal("0")
    actual_amount: Decimal = Decimal("0")
    variance_pct: Optional[Decimal] = None
    variance_type: Optional[VarianceType] = None
    annotation: Optional[str] = Field(None, max_length=1000)

    @property
    def variance_amount(self) -> Decimal:
        return self.budget_amount - self.actual_amount


# ── Audit Log ──────────────────────────────────────────────────────────


class CostingAuditLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    entity_type: str = Field(..., max_length=30)
    entity_id: int
    action: str = Field(..., max_length=30)
    changes: Optional[Dict[str, Any]] = None
    actor: str = Field(..., max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    created_at: Optional[datetime] = None


# ── Bulk Import Result ─────────────────────────────────────────────────


class BulkImportResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_rows: int = 0
    success_count: int = 0
    error_count: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# ── Accumulation Result ────────────────────────────────────────────────


class AccumulationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period_key: str
    total_lines: int = 0
    total_direct: Decimal = Decimal("0")
    total_allocated: Decimal = Decimal("0")


# ── Allocation Preview ─────────────────────────────────────────────────


class AllocationPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int
    rule_code: str
    source_cost_center_id: int
    source_amount: Decimal = Decimal("0")
    lines: List[CostAllocationLine] = Field(default_factory=list)
    total_allocated: Decimal = Decimal("0")
