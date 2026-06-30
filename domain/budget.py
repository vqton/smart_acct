from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, AccountError, Result, _quantize_vnd


class BudgetType(str, Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    CAPEX = "capex"
    CASH_FLOW = "cash_flow"
    BALANCE_SHEET = "balance_sheet"


class BudgetVersionStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"
    CONSOLIDATED = "consolidated"
    ARCHIVED = "archived"


class BudgetPeriodType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class BudgetControlLevel(str, Enum):
    NONE = "none"
    WARNING_ONLY = "warning_only"
    SOFT_BLOCK = "soft_block"
    HARD_BLOCK = "hard_block"


class BudgetDimensionType(str, Enum):
    COST_CENTER = "cost_center"
    DEPARTMENT = "department"
    PROJECT = "project"
    PRODUCT_LINE = "product_line"
    REGION = "region"
    CHANNEL = "channel"


class BudgetCategoryType(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    SEMI_VARIABLE = "semi_variable"
    DRIVER_BASED = "driver_based"


class AdjustmentType(str, Enum):
    VIREMENT = "virement"
    SUPPLEMENTARY = "supplementary"
    EMERGENCY = "emergency"
    REDUCTION = "reduction"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONALLY_APPROVED = "conditionally_approved"


class VarianceFlag(str, Enum):
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"


class KPIThreshold(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class OverrideStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    REVOKED = "revoked"


# ── Master Data Entities ──────────────────────────────────────────────────────

class BudgetStructure(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    fiscal_year: int
    name: str = Field(..., max_length=200)
    budget_types: List[BudgetType] = [BudgetType.REVENUE, BudgetType.EXPENSE]
    dimensions: List[BudgetDimensionType] = [BudgetDimensionType.COST_CENTER, BudgetDimensionType.DEPARTMENT]
    period_type: BudgetPeriodType = BudgetPeriodType.MONTHLY
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_STRUCTURE_NAME_EMPTY")
        return v.strip()

    @field_validator("fiscal_year")
    @classmethod
    def validate_fiscal_year(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise AccountError("BUDGET_INVALID_FISCAL_YEAR")
        return v


class BudgetDimension(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    structure_id: int
    dimension_type: BudgetDimensionType
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_DIM_CODE_EMPTY")
        return v.strip()


class BudgetCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    structure_id: int
    budget_type: BudgetType
    name: str = Field(..., max_length=200)
    category_type: BudgetCategoryType = BudgetCategoryType.VARIABLE
    gl_account_codes: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def validate_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_CATEGORY_NAME_EMPTY")
        return v.strip()


# ── Calendar & Period ─────────────────────────────────────────────────────────

class BudgetCalendarPhase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    calendar_id: int
    phase_name: str
    start_date: date
    end_date: date
    phase_order: int

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v < start:
            raise AccountError("BUDGET_INVALID_DATE_RANGE")
        return v


class BudgetCalendar(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    fiscal_year: int
    name: str = Field(..., max_length=200)
    phases: List[BudgetCalendarPhase] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def validate_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_CALENDAR_NAME_EMPTY")
        return v.strip()

    @field_validator("fiscal_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise AccountError("BUDGET_INVALID_FISCAL_YEAR")
        return v


class BudgetPeriod(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    calendar_id: int
    period_key: str = Field(..., max_length=20)
    period_type: BudgetPeriodType = BudgetPeriodType.MONTHLY
    start_date: date
    end_date: date
    is_open: bool = True

    @field_validator("period_key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_PERIOD_KEY_EMPTY")
        return v.strip()


# ── Template ──────────────────────────────────────────────────────────────────

class BudgetTemplateLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    template_id: int
    line_order: int = 0
    gl_account_code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    category_type: BudgetCategoryType = BudgetCategoryType.VARIABLE
    formula: Optional[str] = None
    is_required: bool = False
    default_amount: Decimal = Decimal("0")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_TEMPLATE_LINE_NAME_EMPTY")
        return v.strip()

    @field_validator("default_amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_AMOUNT")
        return _quantize_vnd(v)


class BudgetTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    budget_type: BudgetType
    lines: List[BudgetTemplateLine] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_TEMPLATE_NAME_EMPTY")
        return v.strip()


# ── Version & Plan ────────────────────────────────────────────────────────────

class BudgetVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    fiscal_year: int
    version_number: str = Field(..., max_length=20)
    label: str = Field(..., max_length=200)
    status: BudgetVersionStatus = BudgetVersionStatus.DRAFT
    parent_version_id: Optional[int] = None
    is_locked: bool = False
    notes: Optional[str] = Field(None, max_length=1000)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    @field_validator("fiscal_year")
    @classmethod
    def validate_fiscal_year(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise AccountError("BUDGET_INVALID_FISCAL_YEAR")
        return v

    @field_validator("version_number")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_VERSION_NUMBER_EMPTY")
        return v.strip()

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_VERSION_LABEL_EMPTY")
        return v.strip()


class BudgetPlanDriver(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    quantity: Decimal = Decimal("0")
    unit_rate: Decimal = Decimal("0")
    driver_name: Optional[str] = Field(None, max_length=100)

    @field_validator("quantity", "unit_rate")
    @classmethod
    def validate_non_negative(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_AMOUNT")
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def calc_amount(self) -> "BudgetPlanDriver":
        return self


class BudgetPlanLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_id: int
    gl_account_code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    category_type: BudgetCategoryType = BudgetCategoryType.VARIABLE
    amounts: Dict[str, Decimal] = Field(default_factory=dict)
    driver: Optional[BudgetPlanDriver] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("gl_account_code")
    @classmethod
    def validate_account(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_ACCOUNT_CODE_EMPTY")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_LINE_NAME_EMPTY")
        return v.strip()


class BudgetPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    version_id: int
    structure_id: int
    dimension_type: BudgetDimensionType
    dimension_code: str = Field(..., max_length=50)
    lines: List[BudgetPlanLine] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("dimension_code")
    @classmethod
    def validate_dim_code(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_DIM_CODE_EMPTY")
        return v.strip()

    def total_amount(self) -> Decimal:
        return sum(sum(amt for amt in line.amounts.values()) for line in self.lines)


# ── Approval Workflow ─────────────────────────────────────────────────────────

class BudgetApprovalStep(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    workflow_id: int
    step_order: int
    approver_role: str = Field(..., max_length=100)
    approver_name: Optional[str] = Field(None, max_length=200)
    min_approvers: int = 1
    status: ApprovalStatus = ApprovalStatus.PENDING
    comments: Optional[str] = Field(None, max_length=1000)
    acted_at: Optional[datetime] = None

    @field_validator("step_order")
    @classmethod
    def validate_order(cls, v: int) -> int:
        if v < 1:
            raise AccountError("BUDGET_INVALID_STEP_ORDER")
        return v


class BudgetApprovalWorkflow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_id: int
    steps: List[BudgetApprovalStep] = Field(default_factory=list)
    status: BudgetVersionStatus = BudgetVersionStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class BudgetApprovalLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    workflow_id: int
    step_id: int
    action: str = Field(..., max_length=50)
    actor: str = Field(..., max_length=200)
    comments: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Adjustment ────────────────────────────────────────────────────────────────

class BudgetAdjustmentLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    adjustment_id: int
    source_plan_line_id: Optional[int] = None
    target_plan_line_id: Optional[int] = None
    amount: Decimal = Decimal("0")
    period_key: Optional[str] = Field(None, max_length=20)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class BudgetAdjustment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    version_id: int
    adjustment_type: AdjustmentType
    reference: str = Field(..., max_length=50)
    reason: str = Field(..., max_length=1000)
    status: ApprovalStatus = ApprovalStatus.PENDING
    lines: List[BudgetAdjustmentLine] = Field(default_factory=list)
    created_by: str = Field(..., max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = Field(None, max_length=100)

    @field_validator("reference")
    @classmethod
    def validate_ref(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_ADJ_REF_EMPTY")
        return v.strip()

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if not v.strip():
            raise AccountError("BUDGET_ADJ_REASON_EMPTY")
        return v.strip()

    def net_change(self) -> Decimal:
        return sum(line.amount for line in self.lines)


# ── Execution & Control ───────────────────────────────────────────────────────

class BudgetCommitment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    source_type: str = Field(..., max_length=50)
    source_id: int
    amount: Decimal = Decimal("0")
    period_key: str = Field(..., max_length=20)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_AMOUNT")
        return _quantize_vnd(v)


class BudgetExecutionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_line_id: int
    budget_amount: Decimal = Decimal("0")
    actual_amount: Decimal = Decimal("0")
    commitment_amount: Decimal = Decimal("0")
    free_balance: Decimal = Decimal("0")
    utilization_pct: Decimal = Decimal("0")

    def calculate(self) -> "BudgetExecutionItem":
        self.free_balance = self.budget_amount - self.actual_amount - self.commitment_amount
        if self.budget_amount > Decimal("0"):
            util = (self.actual_amount + self.commitment_amount) / self.budget_amount * Decimal("100")
            self.utilization_pct = _quantize_vnd(util)
        return self


class BudgetControlRule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    structure_id: int
    gl_account_code: Optional[str] = Field(None, max_length=20)
    dimension_type: Optional[BudgetDimensionType] = None
    dimension_code: Optional[str] = Field(None, max_length=50)
    control_level: BudgetControlLevel = BudgetControlLevel.HARD_BLOCK
    warning_threshold_pct: Decimal = Decimal("80")
    soft_block_threshold_pct: Decimal = Decimal("90")
    hard_block_threshold_pct: Decimal = Decimal("100")
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("warning_threshold_pct", "soft_block_threshold_pct", "hard_block_threshold_pct")
    @classmethod
    def validate_pct(cls, v: Decimal) -> Decimal:
        if v < Decimal("0") or v > Decimal("1000"):
            raise AccountError("BUDGET_INVALID_THRESHOLD")
        return _quantize_vnd(v)


class BudgetOverride(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    control_rule_id: int
    override_code: str = Field(..., max_length=20)
    requested_by: str = Field(..., max_length=100)
    approved_by: Optional[str] = Field(None, max_length=100)
    reason: str = Field(..., max_length=500)
    status: OverrideStatus = OverrideStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    used_at: Optional[datetime] = None


class BudgetBlockLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    control_rule_id: int
    source_type: str = Field(..., max_length=50)
    source_id: int
    gl_account_code: str = Field(..., max_length=20)
    dimension_code: Optional[str] = Field(None, max_length=50)
    attempted_amount: Decimal = Decimal("0")
    utilization_pct: Decimal = Decimal("0")
    control_level: BudgetControlLevel
    was_blocked: bool = True
    override_id: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Consolidation ─────────────────────────────────────────────────────────────

class BudgetICTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    consolidation_id: int
    from_entity_code: str = Field(..., max_length=50)
    to_entity_code: str = Field(..., max_length=50)
    gl_account_code: str = Field(..., max_length=20)
    amount: Decimal = Decimal("0")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class BudgetConsolidationEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    consolidation_id: int
    entity_code: str = Field(..., max_length=50)
    entity_name: str = Field(..., max_length=200)
    version_id: int
    fx_rate: Decimal = Decimal("1")

    @field_validator("fx_rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0"):
            raise AccountError("BUDGET_INVALID_FX_RATE")
        return _quantize_vnd(v)


class BudgetConsolidation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    fiscal_year: int
    parent_entity_code: str = Field(..., max_length=50)
    status: BudgetVersionStatus = BudgetVersionStatus.DRAFT
    entities: List[BudgetConsolidationEntity] = Field(default_factory=list)
    ic_transactions: List[BudgetICTransaction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# ── Variance Analysis ─────────────────────────────────────────────────────────

class BudgetVarianceAnnotation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    variance_line_id: int
    annotation: str = Field(..., max_length=1000)
    created_by: str = Field(..., max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BudgetVarianceLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    report_id: int
    gl_account_code: str
    name: str
    budget_amount: Decimal = Decimal("0")
    actual_amount: Decimal = Decimal("0")
    variance_amount: Decimal = Decimal("0")
    variance_pct: Decimal = Decimal("0")
    flag: VarianceFlag = VarianceFlag.NEUTRAL
    annotations: List[BudgetVarianceAnnotation] = Field(default_factory=list)


class BudgetVarianceReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    fiscal_year: int
    version_id: int
    period_key: str = Field(..., max_length=20)
    dimension_type: Optional[BudgetDimensionType] = None
    dimension_code: Optional[str] = Field(None, max_length=50)
    lines: List[BudgetVarianceLine] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Dashboard & KPI ──────────────────────────────────────────────────────────

class BudgetKPIValue(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    kpi_id: int
    period_key: str = Field(..., max_length=20)
    actual_value: Decimal = Decimal("0")
    target_value: Decimal = Decimal("0")
    threshold: KPIThreshold = KPIThreshold.GREEN


class BudgetKPI(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    structure_id: int
    kpi_code: str = Field(..., max_length=50)
    kpi_name: str = Field(..., max_length=200)
    expression: str = Field(..., max_length=500)
    green_min: Decimal = Decimal("90")
    yellow_min: Decimal = Decimal("70")
    is_active: bool = True


class BudgetDashboard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fiscal_year: int
    kpis: List[BudgetKPIValue] = Field(default_factory=list)
    burn_rate: Decimal = Decimal("0")
    revenue_achievement: Decimal = Decimal("0")
    opex_utilization: Decimal = Decimal("0")
    capex_utilization: Decimal = Decimal("0")
    days_of_budget_left: Optional[int] = None
    ytd_variance: Decimal = Decimal("0")


# ── Revenue Budget ────────────────────────────────────────────────────────────

class RevenueSeasonality(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    revenue_line_id: int
    month: int
    weight_pct: Decimal = Decimal("0")

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise AccountError("BUDGET_INVALID_MONTH")
        return v

    @field_validator("weight_pct")
    @classmethod
    def validate_weight(cls, v: Decimal) -> Decimal:
        if v < Decimal("0") or v > Decimal("100"):
            raise AccountError("BUDGET_INVALID_WEIGHT")
        return _quantize_vnd(v)


class RevenueBudgetDriver(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    revenue_line_id: int
    sales_volume: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")
    growth_rate_pct: Decimal = Decimal("0")
    fx_rate: Decimal = Decimal("1")
    currency_code: str = "VND"

    @field_validator("sales_volume")
    @classmethod
    def validate_volume(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_VOLUME")
        return _quantize_vnd(v)

    @field_validator("unit_price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_PRICE")
        return _quantize_vnd(v)

    def calculated_revenue(self) -> Decimal:
        return _quantize_vnd(self.sales_volume * self.unit_price * self.fx_rate)


class RevenueBudgetLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    product_code: Optional[str] = Field(None, max_length=50)
    region_code: Optional[str] = Field(None, max_length=50)
    channel_code: Optional[str] = Field(None, max_length=50)
    driver: Optional[RevenueBudgetDriver] = None
    seasonality: List[RevenueSeasonality] = Field(default_factory=list)


# ── Expense Budget ────────────────────────────────────────────────────────────

class HeadcountBudget(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    expense_line_id: int
    fte_count: Decimal = Decimal("0")
    avg_cost_per_fte: Decimal = Decimal("0")
    si_employer_pct: Decimal = Decimal("23.5")
    si_employee_pct: Decimal = Decimal("10.5")

    @field_validator("fte_count")
    @classmethod
    def validate_fte(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_FTE")
        return _quantize_vnd(v)

    @field_validator("avg_cost_per_fte")
    @classmethod
    def validate_cost(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_COST")
        return _quantize_vnd(v)

    def total_labor_cost(self) -> Decimal:
        monthly = self.avg_cost_per_fte * self.fte_count
        annual = monthly * Decimal("12")
        employer_si = _quantize_vnd(annual * self.si_employer_pct / Decimal("100"))
        return _quantize_vnd(annual + employer_si)


class ExpenseBudgetLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    expense_category: str = Field(..., max_length=100)
    is_zero_based: bool = False
    headcount: Optional[HeadcountBudget] = None
    justification: Optional[str] = Field(None, max_length=1000)


# ── CAPEX & Cash Flow ─────────────────────────────────────────────────────────

class CAPEXRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    asset_type: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    estimated_cost: Decimal = Decimal("0")
    useful_life_years: int = 5
    expected_roi_pct: Decimal = Decimal("0")
    funding_source: str = Field(..., max_length=100)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = Field(None, max_length=100)
    approved_at: Optional[datetime] = None

    @field_validator("estimated_cost")
    @classmethod
    def validate_cost(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_COST")
        return _quantize_vnd(v)

    @field_validator("useful_life_years")
    @classmethod
    def validate_life(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise AccountError("BUDGET_INVALID_USEFUL_LIFE")
        return v


class CashFlowBudgetLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_line_id: int
    cash_flow_type: str = Field(..., max_length=50)
    period_key: str = Field(..., max_length=20)
    inflow_amount: Decimal = Decimal("0")
    outflow_amount: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")

    @field_validator("inflow_amount", "outflow_amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < Decimal("0"):
            raise AccountError("BUDGET_NEGATIVE_AMOUNT")
        return _quantize_vnd(v)


class CashFlowFinancing(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    cash_flow_line_id: int
    financing_type: str = Field(..., max_length=100)
    amount: Decimal = Decimal("0")
    is_additional: bool = True


# ── Audit Log ─────────────────────────────────────────────────────────────────

class BudgetAuditLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    action: str = Field(..., max_length=50)
    changes: Optional[Dict[str, Any]] = None
    actor: str = Field(..., max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
