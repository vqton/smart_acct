from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from infrastructure.models.coa_models import Base


class ApprovalObjectTypeDB(str, enum.Enum):
    AR_INVOICE = "ar_invoice"
    AP_INVOICE = "ap_invoice"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"
    BUDGET_PLAN = "budget_plan"
    BUDGET_ADJUSTMENT = "budget_adjustment"
    FINANCIAL_STATEMENT = "financial_statement"
    PAYROLL_RUN = "payroll_run"
    INVENTORY_CHECK = "inventory_check"
    FA_DISPOSAL = "fa_disposal"
    TREASURY_BATCH = "treasury_batch"
    COSTING_RULE = "costing_rule"
    ADVANCE = "advance"
    EXPENSE = "expense"


class ApprovalStatusDB(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ApprovalStrategyDB(str, enum.Enum):
    ANY = "any"
    ALL = "all"
    SEQUENTIAL = "sequential"
    QUORUM = "quorum"


class ApprovalWorkflowModel(Base):
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    object_type = Column(String(50), nullable=False, index=True)
    strategy = Column(String(20), nullable=False, default="sequential")
    quorum_percentage = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    steps = relationship("ApprovalStepModel", back_populates="workflow", lazy="selectin",
                         cascade="all, delete-orphan",
                         order_by="ApprovalStepModel.step_order")

    def __repr__(self) -> str:
        return f"<ApprovalWorkflowModel(id={self.id}, name='{self.name}')>"


class ApprovalStepModel(Base):
    __tablename__ = "approval_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("approval_workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    approver_role = Column(String(100), nullable=True)
    approver_user_id = Column(Integer, nullable=True)
    min_amount = Column(Numeric(18, 2), nullable=True)
    max_amount = Column(Numeric(18, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    workflow = relationship("ApprovalWorkflowModel", back_populates="steps")

    __table_args__ = (
        Index("ix_approval_steps_workflow_order", "workflow_id", "step_order"),
    )

    def __repr__(self) -> str:
        return f"<ApprovalStepModel(id={self.id}, step={self.step_order}, name='{self.step_name}')>"


class ApprovalRequestModel(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("approval_workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    object_type = Column(String(50), nullable=False, index=True)
    object_id = Column(Integer, nullable=False)
    object_reference = Column(String(200), nullable=True)
    amount = Column(Numeric(18, 2), nullable=True)
    submitted_by = Column(Integer, nullable=False, index=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    current_step_order = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_approval_requests_object", "object_type", "object_id"),
        Index("ix_approval_requests_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ApprovalRequestModel(id={self.id}, type='{self.object_type}', obj={self.object_id}, status='{self.status}')>"


class ApprovalActionModel(Base):
    __tablename__ = "approval_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("approval_steps.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    approver_id = Column(Integer, nullable=False, index=True)
    action = Column(String(20), nullable=False)
    comments = Column(Text, nullable=True)
    acted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    delegate_from = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_approval_actions_request_step", "request_id", "step_order"),
        Index("ix_approval_actions_approver", "approver_id"),
    )

    def __repr__(self) -> str:
        return f"<ApprovalActionModel(request={self.request_id}, step={self.step_order}, action='{self.action}')>"


class ApprovalDelegateModel(Base):
    __tablename__ = "approval_delegates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    delegate_to = Column(Integer, nullable=False, index=True)
    object_type = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ApprovalDelegateModel(user={self.user_id}->{self.delegate_to})>"
