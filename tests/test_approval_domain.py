from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.approval import (
    ApprovalObjectType, ApprovalStatus, ApprovalStrategy,
    ApprovalWorkflow, ApprovalStep, ApprovalRequest,
    ApprovalAction, ApprovalDelegate, WorkflowCreate, StepCreate,
)
from domain.common import VASValidationError


class TestEnums:
    def test_approval_object_type_values(self):
        assert ApprovalObjectType.AR_INVOICE.value == "ar_invoice"
        assert ApprovalObjectType.AP_INVOICE.value == "ap_invoice"
        assert ApprovalObjectType.BUDGET_PLAN.value == "budget_plan"
        assert ApprovalObjectType.FA_DISPOSAL.value == "fa_disposal"

    def test_approval_status_values(self):
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"
        assert ApprovalStatus.CANCELLED.value == "cancelled"

    def test_approval_strategy_values(self):
        assert ApprovalStrategy.ANY.value == "any"
        assert ApprovalStrategy.ALL.value == "all"
        assert ApprovalStrategy.SEQUENTIAL.value == "sequential"
        assert ApprovalStrategy.QUORUM.value == "quorum"


class TestApprovalWorkflow:
    def test_valid_minimal(self):
        wf = ApprovalWorkflow(
            name="AP Invoice Approval",
            object_type=ApprovalObjectType.AP_INVOICE,
            strategy=ApprovalStrategy.SEQUENTIAL,
        )
        assert wf.name == "AP Invoice Approval"
        assert wf.object_type == ApprovalObjectType.AP_INVOICE
        assert wf.strategy == ApprovalStrategy.SEQUENTIAL
        assert wf.is_active is True
        assert wf.quorum_percentage is None

    def test_valid_all_fields(self):
        wf = ApprovalWorkflow(
            name="Budget Approval",
            description="3-step budget approval",
            object_type=ApprovalObjectType.BUDGET_PLAN,
            strategy=ApprovalStrategy.QUORUM,
            quorum_percentage=Decimal("66.67"),
        )
        assert wf.name == "Budget Approval"
        assert wf.quorum_percentage == Decimal("66.67")

    def test_name_empty_raises(self):
        with pytest.raises(VASValidationError) as exc:
            ApprovalWorkflow(
                name="   ",
                object_type=ApprovalObjectType.AP_INVOICE,
                strategy=ApprovalStrategy.SEQUENTIAL,
            )
        assert "APPROVAL_NAME_EMPTY" in str(exc.value.msgid)

    def test_invalid_quorum_raises(self):
        with pytest.raises(VASValidationError) as exc:
            ApprovalWorkflow(
                name="Test",
                object_type=ApprovalObjectType.AP_INVOICE,
                strategy=ApprovalStrategy.QUORUM,
                quorum_percentage=Decimal("150"),
            )
        assert "APPROVAL_INVALID_QUORUM" in str(exc.value.msgid)

    def test_negative_quorum_raises(self):
        with pytest.raises(VASValidationError) as exc:
            ApprovalWorkflow(
                name="Test",
                object_type=ApprovalObjectType.AP_INVOICE,
                strategy=ApprovalStrategy.QUORUM,
                quorum_percentage=Decimal("-10"),
            )
        assert "APPROVAL_INVALID_QUORUM" in str(exc.value.msgid)


class TestApprovalStep:
    def test_valid_step(self):
        s = ApprovalStep(
            workflow_id=1,
            step_order=1,
            step_name="Manager Review",
        )
        assert s.step_order == 1
        assert s.step_name == "Manager Review"
        assert s.is_active is True

    def test_valid_step_with_role(self):
        s = ApprovalStep(
            workflow_id=1,
            step_order=2,
            step_name="CFO Approval",
            approver_role="cfo",
            min_amount=Decimal("10000000"),
            max_amount=Decimal("100000000"),
        )
        assert s.approver_role == "cfo"
        assert s.min_amount == Decimal("10000000")
        assert s.max_amount == Decimal("100000000")

    def test_step_name_empty_raises(self):
        with pytest.raises(VASValidationError) as exc:
            ApprovalStep(
                workflow_id=1,
                step_order=1,
                step_name="",
            )
        assert "APPROVAL_STEP_NAME_EMPTY" in str(exc.value.msgid)

    def test_step_order_zero_raises(self):
        with pytest.raises(VASValidationError):
            ApprovalStep(
                workflow_id=1,
                step_order=0,
                step_name="Test",
            )


class TestApprovalRequest:
    def test_valid_request(self):
        req = ApprovalRequest(
            workflow_id=1,
            object_type=ApprovalObjectType.AR_INVOICE,
            object_id=100,
            submitted_by=42,
        )
        assert req.object_type == ApprovalObjectType.AR_INVOICE
        assert req.object_id == 100
        assert req.submitted_by == 42
        assert req.status == ApprovalStatus.PENDING
        assert req.current_step_order == 1

    def test_request_with_amount(self):
        req = ApprovalRequest(
            workflow_id=1,
            object_type=ApprovalObjectType.CASH_PAYMENT,
            object_id=200,
            object_reference="PMT-2026-001",
            amount=Decimal("50000000"),
            submitted_by=10,
        )
        assert req.object_reference == "PMT-2026-001"
        assert req.amount == Decimal("50000000")


class TestApprovalAction:
    def test_valid_action(self):
        action = ApprovalAction(
            request_id=1,
            step_id=1,
            step_order=1,
            approver_id=10,
            action=ApprovalStatus.APPROVED,
            comments="Approved",
        )
        assert action.action == ApprovalStatus.APPROVED
        assert action.comments == "Approved"

    def test_rejected_action(self):
        action = ApprovalAction(
            request_id=1,
            step_id=2,
            step_order=2,
            approver_id=20,
            action=ApprovalStatus.REJECTED,
            comments="Insufficient justification",
        )
        assert action.action == ApprovalStatus.REJECTED
        assert action.delegate_from is None


class TestApprovalDelegate:
    def test_valid_delegate(self):
        d = ApprovalDelegate(
            user_id=1,
            delegate_to=2,
            start_date=date(2026, 7, 1),
        )
        assert d.user_id == 1
        assert d.delegate_to == 2
        assert d.object_type is None
        assert d.is_active is True

    def test_delegate_with_object_type(self):
        d = ApprovalDelegate(
            user_id=1,
            delegate_to=2,
            object_type=ApprovalObjectType.AP_INVOICE,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 12, 31),
        )
        assert d.object_type == ApprovalObjectType.AP_INVOICE
        assert d.end_date == date(2026, 12, 31)


class TestWorkflowCreate:
    def test_valid_workflow_create(self):
        wc = WorkflowCreate(
            name="Test WF",
            object_type=ApprovalObjectType.AR_INVOICE,
            strategy=ApprovalStrategy.SEQUENTIAL,
            steps=[
                StepCreate(step_order=1, step_name="Manager"),
                StepCreate(step_order=2, step_name="Director"),
            ],
        )
        assert len(wc.steps) == 2

    def test_workflow_create_name_empty_raises(self):
        with pytest.raises(VASValidationError):
            WorkflowCreate(
                name="",
                object_type=ApprovalObjectType.AR_INVOICE,
                strategy=ApprovalStrategy.SEQUENTIAL,
            )
