import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from infrastructure.models.coa_models import Base


class BudgetTypeDB(str, enum.Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    CAPEX = "capex"
    CASH_FLOW = "cash_flow"
    BALANCE_SHEET = "balance_sheet"


class BudgetVersionStatusDB(str, enum.Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"
    CONSOLIDATED = "consolidated"
    ARCHIVED = "archived"


class BudgetPeriodTypeDB(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class BudgetControlLevelDB(str, enum.Enum):
    NONE = "none"
    WARNING_ONLY = "warning_only"
    SOFT_BLOCK = "soft_block"
    HARD_BLOCK = "hard_block"


class BudgetDimensionTypeDB(str, enum.Enum):
    COST_CENTER = "cost_center"
    DEPARTMENT = "department"
    PROJECT = "project"
    PRODUCT_LINE = "product_line"
    REGION = "region"
    CHANNEL = "channel"


class BudgetCategoryTypeDB(str, enum.Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    SEMI_VARIABLE = "semi_variable"
    DRIVER_BASED = "driver_based"


class AdjustmentTypeDB(str, enum.Enum):
    VIREMENT = "virement"
    SUPPLEMENTARY = "supplementary"
    EMERGENCY = "emergency"
    REDUCTION = "reduction"


class ApprovalStatusDB(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONALLY_APPROVED = "conditionally_approved"


class OverrideStatusDB(str, enum.Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    REVOKED = "revoked"


# ── Master Data ───────────────────────────────────────────────────────────────

class BudgetStructureModel(Base):
    __tablename__ = "budget_structures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    budget_types = Column(JSON, nullable=False, default=lambda: ["revenue", "expense"])
    dimensions = Column(JSON, nullable=False, default=lambda: ["cost_center", "department"])
    period_type = Column(String(20), default="monthly")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_budget_structures_fy", "fiscal_year"),
    )


class BudgetDimensionModel(Base):
    __tablename__ = "budget_dimensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    structure_id = Column(Integer, ForeignKey("budget_structures.id"), nullable=False)
    dimension_type = Column(String(50), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_budget_dimensions_structure", "structure_id", "dimension_type", "code", unique=True),
    )


class BudgetCategoryModel(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    structure_id = Column(Integer, ForeignKey("budget_structures.id"), nullable=False)
    budget_type = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    category_type = Column(String(20), default="variable")
    gl_account_codes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Calendar & Period ─────────────────────────────────────────────────────────

class BudgetCalendarModel(Base):
    __tablename__ = "budget_calendars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_year = Column(Integer, nullable=False, index=True, unique=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    phases = relationship("BudgetCalendarPhaseModel", backref="calendar", lazy="selectin")


class BudgetCalendarPhaseModel(Base):
    __tablename__ = "budget_calendar_phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_id = Column(Integer, ForeignKey("budget_calendars.id"), nullable=False)
    phase_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    phase_order = Column(Integer, nullable=False)


class BudgetPeriodModel(Base):
    __tablename__ = "budget_periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_id = Column(Integer, ForeignKey("budget_calendars.id"), nullable=False)
    period_key = Column(String(20), nullable=False)
    period_type = Column(String(20), default="monthly")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_open = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_budget_periods_calendar_key", "calendar_id", "period_key", unique=True),
    )


# ── Templates ─────────────────────────────────────────────────────────────────

class BudgetTemplateModel(Base):
    __tablename__ = "budget_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    budget_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    lines = relationship("BudgetTemplateLineModel", backref="template", lazy="selectin")


class BudgetTemplateLineModel(Base):
    __tablename__ = "budget_template_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("budget_templates.id"), nullable=False)
    line_order = Column(Integer, default=0)
    gl_account_code = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    category_type = Column(String(20), default="variable")
    formula = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False)
    default_amount = Column(Numeric(18, 2), default=Decimal("0"))
    notes = Column(String(500), nullable=True)

    __table_args__ = (
        Index("ix_budget_template_lines_template", "template_id", "line_order"),
    )


# ── Versions & Plans ──────────────────────────────────────────────────────────

class BudgetVersionModel(Base):
    __tablename__ = "budget_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    version_number = Column(String(20), nullable=False)
    label = Column(String(200), nullable=False)
    status = Column(String(30), default="draft")
    parent_version_id = Column(Integer, ForeignKey("budget_versions.id"), nullable=True)
    is_locked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_budget_versions_fy_status", "fiscal_year", "status"),
    )


class BudgetPlanModel(Base):
    __tablename__ = "budget_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("budget_versions.id"), nullable=False)
    structure_id = Column(Integer, ForeignKey("budget_structures.id"), nullable=False)
    dimension_type = Column(String(50), nullable=False)
    dimension_code = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_budget_plans_version_dim", "version_id", "dimension_type", "dimension_code"),
    )

    lines = relationship("BudgetPlanLineModel", backref="plan", lazy="selectin", cascade="all, delete-orphan")


class BudgetPlanLineModel(Base):
    __tablename__ = "budget_plan_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("budget_plans.id"), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    category_type = Column(String(20), default="variable")
    amounts = Column(JSON, default=dict)
    notes = Column(String(500), nullable=True)

    drivers = relationship("BudgetPlanDriverModel", backref="line", lazy="selectin", cascade="all, delete-orphan")


class BudgetPlanDriverModel(Base):
    __tablename__ = "budget_plan_drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_line_id = Column(Integer, ForeignKey("budget_plan_lines.id"), nullable=False)
    quantity = Column(Numeric(18, 2), default=Decimal("0"))
    unit_rate = Column(Numeric(18, 2), default=Decimal("0"))
    driver_name = Column(String(100), nullable=True)


# ── Approval Workflow ─────────────────────────────────────────────────────────

class BudgetApprovalWorkflowModel(Base):
    __tablename__ = "budget_approval_workflows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("budget_plans.id"), nullable=False)
    status = Column(String(30), default="draft")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    steps = relationship("BudgetApprovalStepModel", backref="workflow", lazy="selectin", cascade="all, delete-orphan")


class BudgetApprovalStepModel(Base):
    __tablename__ = "budget_approval_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("budget_approval_workflows.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    approver_role = Column(String(100), nullable=False)
    approver_name = Column(String(200), nullable=True)
    min_approvers = Column(Integer, default=1)
    status = Column(String(30), default="pending")
    comments = Column(Text, nullable=True)
    acted_at = Column(DateTime(timezone=True), nullable=True)


class BudgetApprovalLogModel(Base):
    __tablename__ = "budget_approval_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("budget_approval_workflows.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("budget_approval_steps.id"), nullable=True)
    action = Column(String(50), nullable=False)
    actor = Column(String(200), nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Adjustments ───────────────────────────────────────────────────────────────

class BudgetAdjustmentModel(Base):
    __tablename__ = "budget_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("budget_versions.id"), nullable=False)
    adjustment_type = Column(String(30), nullable=False)
    reference = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default="pending")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(100), nullable=True)

    lines = relationship("BudgetAdjustmentLineModel", backref="adjustment", lazy="selectin", cascade="all, delete-orphan")


class BudgetAdjustmentLineModel(Base):
    __tablename__ = "budget_adjustment_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    adjustment_id = Column(Integer, ForeignKey("budget_adjustments.id"), nullable=False)
    source_plan_line_id = Column(Integer, ForeignKey("budget_plan_lines.id"), nullable=True)
    target_plan_line_id = Column(Integer, ForeignKey("budget_plan_lines.id"), nullable=True)
    amount = Column(Numeric(18, 2), default=Decimal("0"))
    period_key = Column(String(20), nullable=True)


# ── Execution & Control ───────────────────────────────────────────────────────

class BudgetCommitmentModel(Base):
    __tablename__ = "budget_commitments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_line_id = Column(Integer, ForeignKey("budget_plan_lines.id"), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    amount = Column(Numeric(18, 2), default=Decimal("0"))
    period_key = Column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_budget_commitments_source", "source_type", "source_id"),
    )


class BudgetControlRuleModel(Base):
    __tablename__ = "budget_control_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    structure_id = Column(Integer, ForeignKey("budget_structures.id"), nullable=False)
    gl_account_code = Column(String(20), nullable=True)
    dimension_type = Column(String(50), nullable=True)
    dimension_code = Column(String(50), nullable=True)
    control_level = Column(String(20), default="hard_block")
    warning_threshold_pct = Column(Numeric(5, 2), default=Decimal("80"))
    soft_block_threshold_pct = Column(Numeric(5, 2), default=Decimal("90"))
    hard_block_threshold_pct = Column(Numeric(5, 2), default=Decimal("100"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BudgetOverrideModel(Base):
    __tablename__ = "budget_overrides"

    id = Column(Integer, primary_key=True, autoincrement=True)
    control_rule_id = Column(Integer, ForeignKey("budget_control_rules.id"), nullable=False)
    override_code = Column(String(20), nullable=False)
    requested_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    reason = Column(String(500), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)


class BudgetBlockLogModel(Base):
    __tablename__ = "budget_block_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    control_rule_id = Column(Integer, ForeignKey("budget_control_rules.id"), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    dimension_code = Column(String(50), nullable=True)
    attempted_amount = Column(Numeric(18, 2), default=Decimal("0"))
    utilization_pct = Column(Numeric(5, 2), default=Decimal("0"))
    control_level = Column(String(20), nullable=False)
    was_blocked = Column(Boolean, default=True)
    override_id = Column(Integer, ForeignKey("budget_overrides.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Consolidation ─────────────────────────────────────────────────────────────

class BudgetConsolidationModel(Base):
    __tablename__ = "budget_consolidations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_year = Column(Integer, nullable=False)
    parent_entity_code = Column(String(50), nullable=False)
    status = Column(String(30), default="draft")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    entities = relationship("BudgetConsolidationEntityModel", backref="consolidation", lazy="selectin", cascade="all, delete-orphan")


class BudgetConsolidationEntityModel(Base):
    __tablename__ = "budget_consolidation_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consolidation_id = Column(Integer, ForeignKey("budget_consolidations.id"), nullable=False)
    entity_code = Column(String(50), nullable=False)
    entity_name = Column(String(200), nullable=False)
    version_id = Column(Integer, ForeignKey("budget_versions.id"), nullable=False)
    fx_rate = Column(Numeric(10, 4), default=Decimal("1"))


class BudgetICTransactionModel(Base):
    __tablename__ = "budget_ic_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consolidation_id = Column(Integer, ForeignKey("budget_consolidations.id"), nullable=False)
    from_entity_code = Column(String(50), nullable=False)
    to_entity_code = Column(String(50), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    amount = Column(Numeric(18, 2), default=Decimal("0"))


# ── Audit Log ─────────────────────────────────────────────────────────────────

class BudgetAuditLogModel(Base):
    __tablename__ = "budget_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    changes = Column(JSON, nullable=True)
    actor = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_budget_audit_logs_entity", "entity_type", "entity_id"),
    )
