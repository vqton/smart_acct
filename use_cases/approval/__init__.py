import logging
from decimal import Decimal
from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional, Tuple

from domain.approval import (
    ApprovalObjectType, ApprovalStatus, ApprovalStrategy,
    ApprovalWorkflow, ApprovalStep, ApprovalRequest,
    ApprovalAction, ApprovalDelegate, WorkflowCreate, StepCreate,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.repositories.approval_repository import ApprovalRepository

logger = logging.getLogger(__name__)


class ApprovalUseCases:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_repo(self, session):
        return ApprovalRepository(session)

    # ── UC-APPR-01: Create Workflow ─────────────────────────────

    def create_workflow(self, name: str, object_type: str, strategy: str,
                        steps: List[dict], description: Optional[str] = None,
                        quorum_percentage: Optional[Decimal] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            wf = ApprovalWorkflow(
                name=name,
                description=description,
                object_type=ApprovalObjectType(object_type),
                strategy=ApprovalStrategy(strategy),
                quorum_percentage=quorum_percentage,
            )
            created = repo.create_workflow(wf)
            for i, s in enumerate(steps):
                step = ApprovalStep(
                    workflow_id=created.id,
                    step_order=i + 1,
                    step_name=s.get("step_name", f"Step {i + 1}"),
                    approver_role=s.get("approver_role"),
                    approver_user_id=s.get("approver_user_id"),
                    min_amount=s.get("min_amount"),
                    max_amount=s.get("max_amount"),
                )
                repo.create_step(step)
            session.commit()
            result = repo.get_workflow_with_steps(created.id)
            return Result.success(result)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create workflow error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-02: Get Workflow ────────────────────────────────

    def get_workflow(self, workflow_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.get_workflow_with_steps(workflow_id)
            session.close()
            if not result:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
            return Result.success(result)
        except Exception as e:
            logger.exception(f"Get workflow error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-03: List Workflows ──────────────────────────────

    def list_workflows(self, object_type: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            workflows = repo.list_workflows(object_type)
            session.close()
            return Result.success({"items": workflows, "total": len(workflows)})
        except Exception as e:
            logger.exception(f"List workflows error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-04: Update Workflow ─────────────────────────────

    def update_workflow(self, workflow_id: int, updates: dict) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            existing = repo.get_workflow(workflow_id)
            if not existing:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))

            update_data = {}
            for k in ("name", "description", "object_type", "strategy", "quorum_percentage", "is_active"):
                if k in updates:
                    update_data[k] = updates[k]

            result = repo.update_workflow(workflow_id, update_data)
            if result.is_failure():
                session.rollback()
                return result

            if "steps" in updates and updates["steps"] is not None:
                repo.clear_steps(workflow_id)
                for i, s in enumerate(updates["steps"]):
                    step = ApprovalStep(
                        workflow_id=workflow_id,
                        step_order=i + 1,
                        step_name=s.get("step_name", f"Step {i + 1}"),
                        approver_role=s.get("approver_role"),
                        approver_user_id=s.get("approver_user_id"),
                        min_amount=s.get("min_amount"),
                        max_amount=s.get("max_amount"),
                    )
                    repo.create_step(step)

            session.commit()
            updated = repo.get_workflow_with_steps(workflow_id)
            return Result.success(updated)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update workflow error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-05: Delete / Deactivate Workflow ────────────────

    def delete_workflow(self, workflow_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.deactivate_workflow(workflow_id)
            if result.is_failure():
                return result
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete workflow error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-06: Submit Request ──────────────────────────────

    def submit_request(self, user_id: int, object_type: str, object_id: int,
                       object_reference: Optional[str] = None,
                       amount: Optional[Decimal] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)

            if repo.has_pending_request(object_type, object_id):
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_USER_HAS_PENDING))

            wf_data = repo.get_workflow_for_object_type(object_type, amount)
            if not wf_data:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))

            workflow = wf_data["workflow"]
            steps = wf_data["steps"]

            if not steps:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_NO_APPROVER))

            req = ApprovalRequest(
                workflow_id=workflow.id,
                object_type=ApprovalObjectType(object_type),
                object_id=object_id,
                object_reference=object_reference,
                amount=amount,
                submitted_by=user_id,
                current_step_order=steps[0].step_order,
            )
            created = repo.create_request(req)
            session.commit()

            detail = repo.get_request_detail(created.id)
            return Result.success(detail)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Submit request error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-07: Approve Step ────────────────────────────────

    def approve_step(self, request_id: int, approver_id: int,
                     comments: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            req = repo.get_request(request_id)
            if not req:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
            if req.status != ApprovalStatus.PENDING:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_ALREADY_FINALIZED))

            workflow = repo.get_workflow(req.workflow_id)
            if not workflow:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))

            steps = repo.get_steps_for_workflow(req.workflow_id)
            if not steps:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_NO_APPROVER))

            current_step = None
            for s in steps:
                if s.step_order == req.current_step_order:
                    current_step = s
                    break
            if not current_step:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WRONG_STEP))

            if repo.has_approver_acted(request_id, current_step.id, approver_id):
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_ALREADY_ACTED))

            action = ApprovalAction(
                request_id=request_id,
                step_id=current_step.id,
                step_order=current_step.step_order,
                approver_id=approver_id,
                action=ApprovalStatus.APPROVED,
                comments=comments,
            )
            repo.create_action(action)

            strategy = workflow.strategy
            if strategy == ApprovalStrategy.SEQUENTIAL:
                all_steps_done = True
                for s in steps:
                    if not s.is_active:
                        continue
                    actions_for_step = repo.get_approval_history(request_id)
                    step_actions = [a for a in actions_for_step if a["step_order"] == s.step_order]
                    if not step_actions:
                        all_steps_done = False
                        break
                if all_steps_done:
                    repo.update_request_status(request_id, ApprovalStatus.APPROVED)
                else:
                    next_order = current_step.step_order + 1
                    next_step_exists = any(s.step_order == next_order for s in steps)
                    if next_step_exists:
                        repo.update_request_status(request_id, ApprovalStatus.PENDING, next_order)
            elif strategy in (ApprovalStrategy.ANY, ApprovalStrategy.ALL):
                all_steps_done = True
                for s in steps:
                    if not s.is_active:
                        continue
                    actions_for_step = repo.get_approval_history(request_id)
                    step_actions = [a for a in actions_for_step if a["step_order"] == s.step_order]
                    if not step_actions:
                        all_steps_done = False
                        break
                if strategy == ApprovalStrategy.ANY and not all_steps_done:
                    repo.update_request_status(request_id, ApprovalStatus.APPROVED)
                elif strategy == ApprovalStrategy.ALL and all_steps_done:
                    repo.update_request_status(request_id, ApprovalStatus.APPROVED)
                elif all_steps_done:
                    repo.update_request_status(request_id, ApprovalStatus.APPROVED)
            else:
                all_steps_done = True
                for s in steps:
                    if not s.is_active:
                        continue
                    actions_for_step = repo.get_approval_history(request_id)
                    step_actions = [a for a in actions_for_step if a["step_order"] == s.step_order]
                    if not step_actions:
                        all_steps_done = False
                        break
                if all_steps_done:
                    repo.update_request_status(request_id, ApprovalStatus.APPROVED)

            session.commit()
            return Result.success(repo.get_request_detail(request_id))
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Approve step error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-08: Reject Step ─────────────────────────────────

    def reject_step(self, request_id: int, approver_id: int,
                    comments: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            req = repo.get_request(request_id)
            if not req:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
            if req.status != ApprovalStatus.PENDING:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_ALREADY_FINALIZED))

            steps = repo.get_steps_for_workflow(req.workflow_id)
            current_step = None
            for s in steps:
                if s.step_order == req.current_step_order:
                    current_step = s
                    break
            if not current_step:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WRONG_STEP))

            if repo.has_approver_acted(request_id, current_step.id, approver_id):
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_ALREADY_ACTED))

            action = ApprovalAction(
                request_id=request_id,
                step_id=current_step.id,
                step_order=current_step.step_order,
                approver_id=approver_id,
                action=ApprovalStatus.REJECTED,
                comments=comments,
            )
            repo.create_action(action)
            repo.update_request_status(request_id, ApprovalStatus.REJECTED)
            session.commit()
            return Result.success(repo.get_request_detail(request_id))
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Reject step error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-09: Get Pending Approvals ───────────────────────

    def get_pending_approvals(self, approver_id: int,
                              object_type: Optional[str] = None,
                              page: int = 1, per_page: int = 20) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            items, total = repo.get_pending_requests(
                approver_id, object_type, page, per_page,
            )
            session.close()
            return Result.success({
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
            })
        except Exception as e:
            logger.exception(f"Get pending approvals error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-10: Get My Submissions ──────────────────────────

    def get_my_submissions(self, user_id: int, status: Optional[str] = None,
                           page: int = 1, per_page: int = 20) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            items, total = repo.get_requests_by_submitter(user_id, status, page, per_page)
            session.close()
            return Result.success({
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
            })
        except Exception as e:
            logger.exception(f"Get my submissions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-11: Get Object Approval Status ─────────────────

    def get_object_approval_status(self, object_type: str, object_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            requests = repo.get_requests_by_object(object_type, object_id)
            session.close()
            if not requests:
                return Result.success({
                    "object_type": object_type,
                    "object_id": object_id,
                    "has_request": False,
                    "status": None,
                    "requests": [],
                })
            latest = requests[0]
            return Result.success({
                "object_type": object_type,
                "object_id": object_id,
                "has_request": True,
                "status": latest.status.value,
                "requests": [{
                    "id": r.id,
                    "status": r.status.value,
                    "submitted_at": r.submitted_at.isoformat(),
                    "current_step_order": r.current_step_order,
                } for r in requests],
            })
        except Exception as e:
            logger.exception(f"Get object approval status error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-12: Cancel Request ──────────────────────────────

    def cancel_request(self, request_id: int, user_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            req = repo.get_request(request_id)
            if not req:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
            if req.submitted_by != user_id:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_NOT_AUTHORIZED))
            result = repo.cancel_request(request_id)
            if result.is_failure():
                session.rollback()
                return result
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Cancel request error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-13: Get Request Detail ──────────────────────────

    def get_request_detail(self, request_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            detail = repo.get_request_detail(request_id)
            session.close()
            if not detail:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
            return Result.success(detail)
        except Exception as e:
            logger.exception(f"Get request detail error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-14: Set Delegation ──────────────────────────────

    def set_delegation(self, user_id: int, delegate_to: int,
                       object_type: Optional[str] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> Result:
        session = self._session_factory()
        try:
            if user_id == delegate_to:
                return Result.failure(VASValidationError(ErrorCodes.APPROVAL_DELEGATE_NOT_FOUND))
            repo = self._get_repo(session)
            delegation = ApprovalDelegate(
                user_id=user_id,
                delegate_to=delegate_to,
                object_type=ApprovalObjectType(object_type) if object_type else None,
                start_date=start_date or date.today(),
                end_date=end_date,
            )
            created = repo.create_delegation(delegation)
            session.commit()
            return Result.success({
                "id": created.id,
                "delegate_to": created.delegate_to,
                "object_type": created.object_type.value if created.object_type else None,
                "start_date": created.start_date.isoformat(),
                "end_date": created.end_date.isoformat() if created.end_date else None,
            })
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Set delegation error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_DELEGATE_NOT_FOUND))
        finally:
            session.close()

    # ── UC-APPR-15: Get Delegations ─────────────────────────────

    def get_delegations(self, user_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            delegations = repo.get_user_delegations(user_id)
            session.close()
            return Result.success(delegations)
        except Exception as e:
            logger.exception(f"Get delegations error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_DELEGATE_NOT_FOUND))
        finally:
            session.close()
