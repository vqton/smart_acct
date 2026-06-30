import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal

from infrastructure.models.coa_models import Base


class CostCenterTypeDB(str, enum.Enum):
    COST = "cost"
    PROFIT = "profit"
    INVESTMENT = "investment"
    SERVICE = "service"
    ADMIN = "admin"
    SELLING = "selling"
    PRODUCTION = "production"
    PROJECT = "project"
    VIRTUAL = "virtual"


class DriverTypeDB(str, enum.Enum):
    QUANTITY = "quantity"
    PERCENTAGE = "percentage"
    RATE = "rate"
    ACTUAL = "actual"


class AllocationMethodDB(str, enum.Enum):
    DIRECT = "direct"
    PERCENTAGE = "percentage"
    PROPORTIONAL = "proportional"


class AllocationRunStatusDB(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class CostObjectTypeDB(str, enum.Enum):
    PRODUCT = "product"
    PROJECT = "project"
    SALES_ORDER = "sales_order"
    CAMPAIGN = "campaign"
    CUSTOMER = "customer"
    DEPARTMENT = "department"


class VarianceTypeDB(str, enum.Enum):
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"


class RuleApprovalStatusDB(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class CostCenterModel(Base):
    __tablename__ = "cost_centers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=True)
    cost_center_type = Column(SAEnum(CostCenterTypeDB), nullable=False, default=CostCenterTypeDB.COST)
    parent_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    path = Column(String(500), nullable=False, default="")
    manager_employee_id = Column(Integer, nullable=True)
    gl_account_code = Column(String(20), nullable=True)
    department_code = Column(String(50), nullable=True)
    is_cost_collector = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    children = relationship("CostCenterModel", backref="parent", remote_side=[id], lazy="joined")


class CostDriverModel(Base):
    __tablename__ = "cost_drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    driver_type = Column(SAEnum(DriverTypeDB), nullable=False)
    source_module = Column(String(50), nullable=True)
    source_account_code = Column(String(20), nullable=True)
    unit_of_measure = Column(String(50), nullable=True)
    formula = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class CostAllocationRuleModel(Base):
    __tablename__ = "cost_allocation_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_code = Column(String(20), nullable=False, unique=True, index=True)
    rule_name = Column(String(200), nullable=False)
    source_cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("cost_drivers.id"), nullable=True)
    allocation_method = Column(SAEnum(AllocationMethodDB), nullable=False)
    gl_debit_account_code = Column(String(20), nullable=False)
    gl_credit_account_code = Column(String(20), nullable=False)
    priority_order = Column(Integer, nullable=False, default=0)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    approval_status = Column(SAEnum(RuleApprovalStatusDB), nullable=False, default=RuleApprovalStatusDB.DRAFT)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    targets = relationship("CostAllocationRuleTargetModel", backref="rule", lazy="joined", cascade="all, delete-orphan")


class CostAllocationRuleTargetModel(Base):
    __tablename__ = "cost_allocation_rule_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("cost_allocation_rules.id"), nullable=False)
    target_cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    target_cc = relationship("CostCenterModel", lazy="joined")


class CostAllocationRunModel(Base):
    __tablename__ = "cost_allocation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_code = Column(String(30), nullable=False, unique=True)
    period_key = Column(String(6), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)
    run_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    run_by = Column(String(100), nullable=False)
    status = Column(SAEnum(AllocationRunStatusDB), nullable=False, default=AllocationRunStatusDB.DRAFT)
    total_allocated_amount = Column(Numeric(18, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    lines = relationship("CostAllocationLineModel", backref="run", lazy="joined", cascade="all, delete-orphan")


class CostAllocationLineModel(Base):
    __tablename__ = "cost_allocation_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("cost_allocation_runs.id"), nullable=False)
    source_cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    target_cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("cost_allocation_rules.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("cost_drivers.id"), nullable=True)
    gl_account_code = Column(String(20), nullable=False)
    original_amount = Column(Numeric(18, 2), nullable=False, default=0)
    allocated_amount = Column(Numeric(18, 2), nullable=False, default=0)
    driver_quantity = Column(Numeric(18, 2), nullable=True)
    driver_rate = Column(Numeric(18, 2), nullable=True)
    allocation_basis_description = Column(String(500), nullable=True)


class CostObjectModel(Base):
    __tablename__ = "cost_objects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    object_type = Column(SAEnum(CostObjectTypeDB), nullable=False)
    parent_object_id = Column(Integer, ForeignKey("cost_objects.id"), nullable=True)
    gl_account_code = Column(String(20), nullable=True)
    external_ref_id = Column(Integer, nullable=True)
    external_ref_type = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    custom_attributes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    children = relationship("CostObjectModel", backref="parent_obj", remote_side=[id])


class CostAccumulationModel(Base):
    __tablename__ = "cost_accumulations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_object_id = Column(Integer, ForeignKey("cost_objects.id"), nullable=False)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    period_key = Column(String(6), nullable=False)
    direct_cost_amount = Column(Numeric(18, 2), nullable=False, default=0)
    allocated_cost_amount = Column(Numeric(18, 2), nullable=False, default=0)
    source_type = Column(String(20), nullable=True)
    source_reference = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("cost_object_id", "cost_center_id", "gl_account_code", "period_key", name="uq_cost_acc"),
    )


class CostCenterBudgetModel(Base):
    __tablename__ = "cost_center_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    period_key = Column(String(6), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    budget_amount = Column(Numeric(18, 2), nullable=False, default=0)
    revised_amount = Column(Numeric(18, 2), nullable=False, default=0)
    budget_version_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("cost_center_id", "period_key", "gl_account_code", name="uq_cost_budget"),
    )


class CostCenterActualModel(Base):
    __tablename__ = "cost_center_actuals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    period_key = Column(String(6), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    actual_amount = Column(Numeric(18, 2), nullable=False, default=0)
    commitment_amount = Column(Numeric(18, 2), nullable=False, default=0)
    allocated_amount = Column(Numeric(18, 2), nullable=False, default=0)
    source_reference = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("cost_center_id", "period_key", "gl_account_code", name="uq_cost_actual"),
    )


class CostCenterVarianceModel(Base):
    __tablename__ = "cost_center_variances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=False)
    period_key = Column(String(6), nullable=False)
    gl_account_code = Column(String(20), nullable=False)
    budget_amount = Column(Numeric(18, 2), nullable=False, default=0)
    actual_amount = Column(Numeric(18, 2), nullable=False, default=0)
    variance_pct = Column(Numeric(5, 2), nullable=True)
    variance_type = Column(SAEnum(VarianceTypeDB), nullable=True)
    annotation = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("cost_center_id", "period_key", "gl_account_code", name="uq_cost_variance"),
    )


class CostingAuditLogModel(Base):
    __tablename__ = "costing_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(30), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(30), nullable=False)
    changes = Column(JSON, nullable=True)
    actor = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
