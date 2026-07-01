from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result


class ApprovalObjectType(str, Enum):
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


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ApprovalStrategy(str, Enum):
    ANY = "any"
    ALL = "all"
    SEQUENTIAL = "sequential"
    QUORUM = "quorum"


class WorkflowCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    object_type: ApprovalObjectType
    strategy: ApprovalStrategy
    quorum_percentage: Optional[Decimal] = None
    steps: List["StepCreate"] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.APPROVAL_NAME_EMPTY)
        return v.strip()

    @field_validator("quorum_percentage")
    @classmethod
    def validate_quorum(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and (v < Decimal("0") or v > Decimal("100")):
            raise VASValidationError(ErrorCodes.APPROVAL_INVALID_QUORUM)
        if v is not None:
            return v.quantize(Decimal("0.01"))
        return v


class StepCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    step_name: str = Field(..., max_length=200)
    approver_role: Optional[str] = Field(None, max_length=100)
    approver_user_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

    @field_validator("step_name")
    @classmethod
    def validate_step_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.APPROVAL_STEP_NAME_EMPTY)
        return v.strip()


class ApprovalWorkflow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    object_type: ApprovalObjectType
    strategy: ApprovalStrategy
    quorum_percentage: Optional[Decimal] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.APPROVAL_NAME_EMPTY)
        return v.strip()

    @field_validator("quorum_percentage")
    @classmethod
    def validate_quorum(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and (v < Decimal("0") or v > Decimal("100")):
            raise VASValidationError(ErrorCodes.APPROVAL_INVALID_QUORUM)
        if v is not None:
            return v.quantize(Decimal("0.01"))
        return v


class ApprovalStep(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    workflow_id: int
    step_order: int
    step_name: str
    approver_role: Optional[str] = None
    approver_user_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    is_active: bool = True

    @field_validator("step_name")
    @classmethod
    def validate_step_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.APPROVAL_STEP_NAME_EMPTY)
        return v.strip()

    @field_validator("step_order")
    @classmethod
    def validate_order(cls, v: int) -> int:
        if v < 1:
            raise VASValidationError(ErrorCodes.APPROVAL_INVALID_STEP_ORDER)
        return v


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    workflow_id: int
    object_type: ApprovalObjectType
    object_id: int
    object_reference: Optional[str] = None
    amount: Optional[Decimal] = None
    submitted_by: int
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ApprovalStatus = ApprovalStatus.PENDING
    current_step_order: int = 1


class ApprovalAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    request_id: int
    step_id: int
    step_order: int
    approver_id: int
    action: ApprovalStatus
    comments: Optional[str] = None
    acted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delegate_from: Optional[int] = None


class ApprovalDelegate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    delegate_to: int
    object_type: Optional[ApprovalObjectType] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True
