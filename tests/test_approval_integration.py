from decimal import Decimal
from datetime import date, datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.approval import (
    ApprovalObjectType, ApprovalStatus, ApprovalStrategy,
    ApprovalWorkflow, ApprovalStep, ApprovalRequest,
)
from infrastructure.models.coa_models import Base
from use_cases.approval import ApprovalUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def uc(session):
    return ApprovalUseCases(lambda: session)


def _create_workflow(uc, name="Test WF", object_type="ar_invoice",
                     strategy="sequential", steps=None):
    if steps is None:
        steps = [
            {"step_name": "Manager Review", "approver_role": "manager"},
            {"step_name": "Director Review", "approver_role": "director"},
        ]
    return uc.create_workflow(
        name=name,
        object_type=object_type,
        strategy=strategy,
        steps=steps,
    )


class TestWorkflowCRUD:
    def test_create_workflow(self, uc):
        result = _create_workflow(uc)
        assert result.is_success()
        data = result.get_data()
        assert data["name"] == "Test WF"
        assert data["object_type"] == "ar_invoice"
        assert len(data["steps"]) == 2

    def test_create_workflow_with_quorum(self, uc):
        result = uc.create_workflow(
            name="Quorum WF",
            object_type="ap_invoice",
            strategy="quorum",
            quorum_percentage=Decimal("66.67"),
            steps=[{"step_name": "Step 1", "approver_role": "manager"}],
        )
        assert result.is_success()
        data = result.get_data()
        assert data["strategy"] == "quorum"
        assert data["quorum_percentage"] == 66.67

    def test_get_workflow(self, uc):
        created = _create_workflow(uc).get_data()
        result = uc.get_workflow(created["id"])
        assert result.is_success()
        data = result.get_data()
        assert data["name"] == "Test WF"

    def test_get_workflow_not_found(self, uc):
        result = uc.get_workflow(999)
        assert result.is_failure()

    def test_list_workflows(self, uc):
        _create_workflow(uc, name="WF1", object_type="ar_invoice")
        _create_workflow(uc, name="WF2", object_type="ap_invoice")
        result = uc.list_workflows()
        assert result.is_success()
        data = result.get_data()
        assert data["total"] >= 2

    def test_list_workflows_by_type(self, uc):
        _create_workflow(uc, name="AR WF", object_type="ar_invoice")
        _create_workflow(uc, name="AP WF", object_type="ap_invoice")
        result = uc.list_workflows(object_type="ar_invoice")
        assert result.is_success()
        data = result.get_data()
        for item in data["items"]:
            assert item["object_type"] == "ar_invoice"

    def test_update_workflow(self, uc):
        created = _create_workflow(uc).get_data()
        result = uc.update_workflow(created["id"], {"name": "Updated WF"})
        assert result.is_success()
        data = result.get_data()
        assert data["name"] == "Updated WF"

    def test_update_workflow_not_found(self, uc):
        result = uc.update_workflow(999, {"name": "Nope"})
        assert result.is_failure()

    def test_delete_workflow(self, uc):
        created = _create_workflow(uc).get_data()
        result = uc.delete_workflow(created["id"])
        assert result.is_success()
        wf = uc.get_workflow(created["id"]).get_data()
        assert wf["is_active"] is False


class TestApprovalRequest:
    def test_submit_request(self, uc):
        _create_workflow(uc).get_data()
        result = uc.submit_request(
            user_id=1,
            object_type="ar_invoice",
            object_id=100,
            object_reference="INV-001",
        )
        assert result.is_success()
        data = result.get_data()
        assert data["status"] == "pending"
        assert data["submitted_by"] == 1

    def test_submit_request_with_amount(self, uc):
        _create_workflow(uc).get_data()
        result = uc.submit_request(
            user_id=1,
            object_type="ar_invoice",
            object_id=101,
            amount=Decimal("50000000"),
        )
        assert result.is_success()

    def test_duplicate_submission_fails(self, uc):
        _create_workflow(uc).get_data()
        uc.submit_request(user_id=1, object_type="ar_invoice", object_id=100)
        result = uc.submit_request(user_id=2, object_type="ar_invoice", object_id=100)
        assert result.is_failure()

    def test_submit_no_workflow_fails(self, uc):
        result = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=999,
        )
        assert result.is_failure()

    def test_get_request_detail(self, uc):
        _create_workflow(uc).get_data()
        created = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()
        result = uc.get_request_detail(created["id"])
        assert result.is_success()
        data = result.get_data()
        assert data["id"] == created["id"]

    def test_get_request_detail_not_found(self, uc):
        result = uc.get_request_detail(999)
        assert result.is_failure()


class TestApprovalActions:
    def test_approve_step(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.approve_step(request_id=req["id"], approver_id=10,
                                 comments="Approved by manager")
        assert result.is_success()
        data = result.get_data()
        assert data["status"] == "pending"
        assert len(data["history"]) == 1

    def test_full_sequential_approval(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        uc.approve_step(req["id"], approver_id=10, comments="Manager approved")
        result = uc.approve_step(req["id"], approver_id=20, comments="Director approved")
        assert result.is_success()
        data = result.get_data()
        assert data["status"] == "approved"
        assert len(data["history"]) == 2

    def test_reject_step(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.reject_step(request_id=req["id"], approver_id=10,
                                comments="Not approved")
        assert result.is_success()
        data = result.get_data()
        assert data["status"] == "rejected"

    def test_approve_already_rejected_fails(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()
        uc.reject_step(req["id"], approver_id=10)
        result = uc.approve_step(req["id"], approver_id=20)
        assert result.is_failure()

    def test_duplicate_approve_fails(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()
        uc.approve_step(req["id"], approver_id=10)
        result = uc.approve_step(req["id"], approver_id=10)
        assert result.is_failure()


class TestPendingApprovals:
    def test_get_pending_approvals(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.get_pending_approvals(approver_id=10)
        assert result.is_success()
        data = result.get_data()
        assert len(data["items"]) >= 1

    def test_get_my_submissions(self, uc):
        _create_workflow(uc).get_data()
        uc.submit_request(user_id=1, object_type="ar_invoice", object_id=100)
        uc.submit_request(user_id=1, object_type="ar_invoice", object_id=101)

        result = uc.get_my_submissions(user_id=1)
        assert result.is_success()
        data = result.get_data()
        assert data["total"] >= 2

    def test_get_my_submissions_with_status(self, uc):
        _create_workflow(uc).get_data()
        uc.submit_request(user_id=1, object_type="ar_invoice", object_id=100)
        result = uc.get_my_submissions(user_id=1, status="pending")
        assert result.is_success()


class TestApprovalStatus:
    def test_get_object_status(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.get_object_approval_status("ar_invoice", 100)
        assert result.is_success()
        data = result.get_data()
        assert data["has_request"] is True
        assert data["status"] == "pending"

    def test_get_object_status_no_request(self, uc):
        result = uc.get_object_approval_status("ar_invoice", 999)
        assert result.is_success()
        data = result.get_data()
        assert data["has_request"] is False


class TestCancelRequest:
    def test_cancel_own_request(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.cancel_request(req["id"], user_id=1)
        assert result.is_success()

    def test_cancel_others_request_fails(self, uc):
        _create_workflow(uc).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()

        result = uc.cancel_request(req["id"], user_id=2)
        assert result.is_failure()

    def test_cancel_approved_request_fails(self, uc):
        _create_workflow(uc, steps=[{"step_name": "Only Step", "approver_role": "manager"}]).get_data()
        req = uc.submit_request(
            user_id=1, object_type="ar_invoice", object_id=100,
        ).get_data()
        uc.approve_step(req["id"], approver_id=10)
        result = uc.cancel_request(req["id"], user_id=1)
        assert result.is_failure()


class TestDelegations:
    def test_set_delegation(self, uc):
        result = uc.set_delegation(
            user_id=1,
            delegate_to=2,
            start_date=date(2026, 7, 1),
        )
        assert result.is_success()
        data = result.get_data()
        assert data["delegate_to"] == 2

    def test_set_delegation_with_object_type(self, uc):
        result = uc.set_delegation(
            user_id=1,
            delegate_to=2,
            object_type="ap_invoice",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 12, 31),
        )
        assert result.is_success()

    def test_set_delegation_self_fails(self, uc):
        result = uc.set_delegation(
            user_id=1,
            delegate_to=1,
            start_date=date(2026, 7, 1),
        )
        assert result.is_failure()

    def test_get_delegations(self, uc):
        uc.set_delegation(user_id=1, delegate_to=2, start_date=date(2026, 7, 1))
        uc.set_delegation(user_id=3, delegate_to=1, start_date=date(2026, 7, 1))

        result = uc.get_delegations(1)
        assert result.is_success()
        data = result.get_data()
        assert len(data["outgoing"]) >= 1
        assert len(data["incoming"]) >= 1
