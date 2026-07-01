import logging
from decimal import Decimal
from datetime import datetime, timezone, date
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from domain.approval import (
    ApprovalObjectType, ApprovalStatus, ApprovalStrategy,
    ApprovalWorkflow, ApprovalStep, ApprovalRequest,
    ApprovalAction, ApprovalDelegate, WorkflowCreate, StepCreate,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result
from infrastructure.models.approval_models import (
    ApprovalWorkflowModel, ApprovalStepModel, ApprovalRequestModel,
    ApprovalActionModel, ApprovalDelegateModel,
    ApprovalObjectTypeDB, ApprovalStatusDB, ApprovalStrategyDB,
)

logger = logging.getLogger(__name__)


class ApprovalRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Workflow CRUD ─────────────────────────────────────────────

    def create_workflow(self, workflow: ApprovalWorkflow) -> ApprovalWorkflow:
        model = ApprovalWorkflowModel(
            name=workflow.name,
            description=workflow.description,
            object_type=workflow.object_type.value,
            strategy=workflow.strategy.value,
            quorum_percentage=workflow.quorum_percentage,
            is_active=workflow.is_active,
        )
        self.session.add(model)
        self.session.flush()
        return self._workflow_to_domain(model)

    def create_step(self, step: ApprovalStep) -> ApprovalStep:
        model = ApprovalStepModel(
            workflow_id=step.workflow_id,
            step_order=step.step_order,
            step_name=step.step_name,
            approver_role=step.approver_role,
            approver_user_id=step.approver_user_id,
            min_amount=step.min_amount,
            max_amount=step.max_amount,
            is_active=step.is_active,
        )
        self.session.add(model)
        self.session.flush()
        return self._step_to_domain(model)

    def get_workflow(self, workflow_id: int) -> Optional[ApprovalWorkflow]:
        model = self.session.query(ApprovalWorkflowModel).filter(
            ApprovalWorkflowModel.id == workflow_id
        ).first()
        return self._workflow_to_domain(model) if model else None

    def get_workflow_with_steps(self, workflow_id: int) -> Optional[dict]:
        model = self.session.query(ApprovalWorkflowModel).filter(
            ApprovalWorkflowModel.id == workflow_id
        ).first()
        if not model:
            return None
        return self._workflow_with_steps(model)

    def list_workflows(self, object_type: Optional[str] = None, include_inactive: bool = False) -> List[dict]:
        query = self.session.query(ApprovalWorkflowModel)
        if object_type:
            query = query.filter(ApprovalWorkflowModel.object_type == object_type)
        if not include_inactive:
            query = query.filter(ApprovalWorkflowModel.is_active.is_(True))
        models = query.order_by(ApprovalWorkflowModel.name).all()
        return [self._workflow_with_steps(m) for m in models]

    def update_workflow(self, workflow_id: int, updates: dict) -> Result:
        model = self.session.query(ApprovalWorkflowModel).filter(
            ApprovalWorkflowModel.id == workflow_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        for key, value in updates.items():
            if hasattr(model, key) and value is not None:
                if key in ("object_type", "strategy"):
                    setattr(model, key, value.value if hasattr(value, 'value') else value)
                else:
                    setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._workflow_to_domain(model))

    def deactivate_workflow(self, workflow_id: int) -> Result:
        model = self.session.query(ApprovalWorkflowModel).filter(
            ApprovalWorkflowModel.id == workflow_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND))
        model.is_active = False
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(None)

    # ── Steps ─────────────────────────────────────────────────────

    def get_steps_for_workflow(self, workflow_id: int) -> List[ApprovalStep]:
        models = self.session.query(ApprovalStepModel).filter(
            ApprovalStepModel.workflow_id == workflow_id,
            ApprovalStepModel.is_active.is_(True),
        ).order_by(ApprovalStepModel.step_order).all()
        return [self._step_to_domain(m) for m in models]

    def clear_steps(self, workflow_id: int) -> None:
        self.session.query(ApprovalStepModel).filter(
            ApprovalStepModel.workflow_id == workflow_id
        ).delete()
        self.session.flush()

    # ── Request CRUD ──────────────────────────────────────────────

    def create_request(self, req: ApprovalRequest) -> ApprovalRequest:
        model = ApprovalRequestModel(
            workflow_id=req.workflow_id,
            object_type=req.object_type.value,
            object_id=req.object_id,
            object_reference=req.object_reference,
            amount=req.amount,
            submitted_by=req.submitted_by,
            status=req.status.value,
            current_step_order=req.current_step_order,
        )
        self.session.add(model)
        self.session.flush()
        return self._request_to_domain(model)

    def get_request(self, request_id: int) -> Optional[ApprovalRequest]:
        model = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.id == request_id
        ).first()
        return self._request_to_domain(model) if model else None

    def get_request_detail(self, request_id: int) -> Optional[dict]:
        model = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.id == request_id
        ).first()
        if not model:
            return None
        actions = self.get_approval_history(request_id)
        return {
            **self._request_to_dict(model),
            "history": actions,
        }

    def get_requests_by_object(self, object_type: str, object_id: int) -> List[ApprovalRequest]:
        models = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.object_type == object_type,
            ApprovalRequestModel.object_id == object_id,
        ).order_by(ApprovalRequestModel.submitted_at.desc()).all()
        return [self._request_to_domain(m) for m in models]

    def has_pending_request(self, object_type: str, object_id: int) -> bool:
        return self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.object_type == object_type,
            ApprovalRequestModel.object_id == object_id,
            ApprovalRequestModel.status == "pending",
        ).first() is not None

    def get_pending_requests(
        self, user_id: int, object_type: Optional[str] = None,
        page: int = 1, per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        query = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.status == "pending",
        )
        if object_type:
            query = query.filter(ApprovalRequestModel.object_type == object_type)
        total = query.count()
        if page > 1:
            query = query.offset((page - 1) * per_page)
        models = query.order_by(ApprovalRequestModel.submitted_at.desc()).limit(per_page).all()
        items = []
        for m in models:
            req_data = self._request_to_dict(m)
            actions = self.session.query(ApprovalActionModel).filter(
                ApprovalActionModel.request_id == m.id
            ).all()
            acted_step_orders = {a.step_order for a in actions if a.approver_id == user_id}
            current_steps = self.session.query(ApprovalStepModel).filter(
                ApprovalStepModel.workflow_id == m.workflow_id,
                ApprovalStepModel.step_order == m.current_step_order,
                ApprovalStepModel.is_active.is_(True),
            ).all()
            is_for_user = False
            for s in current_steps:
                if m.current_step_order not in acted_step_orders:
                    if s.approver_user_id == user_id:
                        is_for_user = True
                        break
                    if s.approver_role:
                        is_for_user = True
                        break
            if is_for_user:
                items.append(req_data)
        return items, total

    def get_requests_by_submitter(
        self, user_id: int, status: Optional[str] = None,
        page: int = 1, per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        query = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.submitted_by == user_id,
        )
        if status:
            query = query.filter(ApprovalRequestModel.status == status)
        total = query.count()
        if page > 1:
            query = query.offset((page - 1) * per_page)
        models = query.order_by(ApprovalRequestModel.submitted_at.desc()).limit(per_page).all()
        return [self._request_to_dict(m) for m in models], total

    def update_request_status(self, request_id: int, status: ApprovalStatus,
                               current_step_order: Optional[int] = None) -> None:
        model = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.id == request_id
        ).first()
        if model:
            model.status = status.value if hasattr(status, 'value') else status
            if current_step_order is not None:
                model.current_step_order = current_step_order
            self.session.flush()

    def cancel_request(self, request_id: int) -> Result:
        model = self.session.query(ApprovalRequestModel).filter(
            ApprovalRequestModel.id == request_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_REQUEST_NOT_FOUND))
        if model.status != "pending":
            return Result.failure(VASValidationError(ErrorCodes.APPROVAL_ALREADY_FINALIZED))
        model.status = "cancelled"
        self.session.flush()
        return Result.success(None)

    def get_workflow_for_object_type(
        self, object_type: str, amount: Optional[Decimal] = None,
    ) -> Optional[dict]:
        model = self.session.query(ApprovalWorkflowModel).filter(
            ApprovalWorkflowModel.object_type == object_type,
            ApprovalWorkflowModel.is_active.is_(True),
        ).first()
        if not model:
            return None
        steps = self.get_steps_for_workflow(model.id)
        if amount is not None:
            filtered = []
            for s in steps:
                if s.min_amount is not None and amount < s.min_amount:
                    filtered.append(s)
                    continue
                if s.max_amount is not None and amount > s.max_amount:
                    continue
                filtered.append(s)
            steps = filtered
        return {
            "workflow": self._workflow_to_domain(model),
            "steps": steps,
        }

    # ── Actions ───────────────────────────────────────────────────

    def create_action(self, action: ApprovalAction) -> ApprovalAction:
        model = ApprovalActionModel(
            request_id=action.request_id,
            step_id=action.step_id,
            step_order=action.step_order,
            approver_id=action.approver_id,
            action=action.action.value,
            comments=action.comments,
            delegate_from=action.delegate_from,
        )
        self.session.add(model)
        self.session.flush()
        return self._action_to_domain(model)

    def get_approval_history(self, request_id: int) -> List[dict]:
        models = self.session.query(ApprovalActionModel).filter(
            ApprovalActionModel.request_id == request_id
        ).order_by(ApprovalActionModel.step_order, ApprovalActionModel.acted_at).all()
        return [self._action_to_dict(m) for m in models]

    def has_approver_acted(self, request_id: int, step_id: int, approver_id: int) -> bool:
        return self.session.query(ApprovalActionModel).filter(
            ApprovalActionModel.request_id == request_id,
            ApprovalActionModel.step_id == step_id,
            ApprovalActionModel.approver_id == approver_id,
        ).first() is not None

    # ── Delegations ───────────────────────────────────────────────

    def create_delegation(self, delegation: ApprovalDelegate) -> ApprovalDelegate:
        model = ApprovalDelegateModel(
            user_id=delegation.user_id,
            delegate_to=delegation.delegate_to,
            object_type=delegation.object_type.value if delegation.object_type else None,
            start_date=delegation.start_date,
            end_date=delegation.end_date,
            is_active=delegation.is_active,
        )
        self.session.add(model)
        self.session.flush()
        return self._delegate_to_domain(model)

    def get_active_delegations(self, user_id: int) -> List[ApprovalDelegate]:
        today = date.today()
        models = self.session.query(ApprovalDelegateModel).filter(
            ApprovalDelegateModel.user_id == user_id,
            ApprovalDelegateModel.is_active.is_(True),
            ApprovalDelegateModel.start_date <= today,
            or_(
                ApprovalDelegateModel.end_date.is_(None),
                ApprovalDelegateModel.end_date >= today,
            ),
        ).all()
        return [self._delegate_to_domain(m) for m in models]

    def get_my_delegations(self, user_id: int) -> List[ApprovalDelegate]:
        models = self.session.query(ApprovalDelegateModel).filter(
            ApprovalDelegateModel.delegate_to == user_id,
            ApprovalDelegateModel.is_active.is_(True),
        ).all()
        return [self._delegate_to_domain(m) for m in models]

    def get_user_delegations(self, user_id: int) -> List[dict]:
        outgoing = []
        models = self.session.query(ApprovalDelegateModel).filter(
            ApprovalDelegateModel.user_id == user_id,
        ).all()
        for m in models:
            d = self._delegate_to_domain(m)
            outgoing.append({
                "id": d.id,
                "delegate_to": d.delegate_to,
                "object_type": d.object_type.value if d.object_type else None,
                "start_date": d.start_date.isoformat(),
                "end_date": d.end_date.isoformat() if d.end_date else None,
                "is_active": d.is_active,
            })
        incoming = []
        models2 = self.session.query(ApprovalDelegateModel).filter(
            ApprovalDelegateModel.delegate_to == user_id,
        ).all()
        for m in models2:
            d = self._delegate_to_domain(m)
            incoming.append({
                "id": d.id,
                "from_user": d.user_id,
                "object_type": d.object_type.value if d.object_type else None,
                "start_date": d.start_date.isoformat(),
                "end_date": d.end_date.isoformat() if d.end_date else None,
                "is_active": d.is_active,
            })
        return {"outgoing": outgoing, "incoming": incoming}

    # ── Helpers ───────────────────────────────────────────────────

    def _workflow_to_domain(self, m: ApprovalWorkflowModel) -> ApprovalWorkflow:
        return ApprovalWorkflow(
            id=m.id,
            name=m.name,
            description=m.description,
            object_type=ApprovalObjectType(m.object_type),
            strategy=ApprovalStrategy(m.strategy),
            quorum_percentage=m.quorum_percentage,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    def _step_to_domain(self, m: ApprovalStepModel) -> ApprovalStep:
        return ApprovalStep(
            id=m.id,
            workflow_id=m.workflow_id,
            step_order=m.step_order,
            step_name=m.step_name,
            approver_role=m.approver_role,
            approver_user_id=m.approver_user_id,
            min_amount=m.min_amount,
            max_amount=m.max_amount,
            is_active=m.is_active,
        )

    def _request_to_domain(self, m: ApprovalRequestModel) -> ApprovalRequest:
        return ApprovalRequest(
            id=m.id,
            workflow_id=m.workflow_id,
            object_type=ApprovalObjectType(m.object_type),
            object_id=m.object_id,
            object_reference=m.object_reference,
            amount=m.amount,
            submitted_by=m.submitted_by,
            submitted_at=m.submitted_at,
            status=ApprovalStatus(m.status),
            current_step_order=m.current_step_order,
        )

    def _action_to_domain(self, m: ApprovalActionModel) -> ApprovalAction:
        return ApprovalAction(
            id=m.id,
            request_id=m.request_id,
            step_id=m.step_id,
            step_order=m.step_order,
            approver_id=m.approver_id,
            action=ApprovalStatus(m.action),
            comments=m.comments,
            acted_at=m.acted_at,
            delegate_from=m.delegate_from,
        )

    def _delegate_to_domain(self, m: ApprovalDelegateModel) -> ApprovalDelegate:
        return ApprovalDelegate(
            id=m.id,
            user_id=m.user_id,
            delegate_to=m.delegate_to,
            object_type=ApprovalObjectType(m.object_type) if m.object_type else None,
            start_date=m.start_date,
            end_date=m.end_date,
            is_active=m.is_active,
        )

    def _workflow_with_steps(self, m: ApprovalWorkflowModel) -> dict:
        steps = self.get_steps_for_workflow(m.id)
        return {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "object_type": m.object_type,
            "strategy": m.strategy,
            "quorum_percentage": float(m.quorum_percentage) if m.quorum_percentage else None,
            "is_active": m.is_active,
            "steps": [{
                "id": s.id,
                "step_order": s.step_order,
                "step_name": s.step_name,
                "approver_role": s.approver_role,
                "approver_user_id": s.approver_user_id,
                "min_amount": float(s.min_amount) if s.min_amount else None,
                "max_amount": float(s.max_amount) if s.max_amount else None,
                "is_active": s.is_active,
            } for s in steps],
            "created_at": m.created_at.isoformat(),
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }

    def _request_to_dict(self, m: ApprovalRequestModel) -> dict:
        return {
            "id": m.id,
            "workflow_id": m.workflow_id,
            "object_type": m.object_type,
            "object_id": m.object_id,
            "object_reference": m.object_reference,
            "amount": float(m.amount) if m.amount else None,
            "submitted_by": m.submitted_by,
            "submitted_at": m.submitted_at.isoformat(),
            "status": m.status,
            "current_step_order": m.current_step_order,
        }

    def _action_to_dict(self, m: ApprovalActionModel) -> dict:
        return {
            "id": m.id,
            "request_id": m.request_id,
            "step_id": m.step_id,
            "step_order": m.step_order,
            "approver_id": m.approver_id,
            "action": m.action,
            "comments": m.comments,
            "acted_at": m.acted_at.isoformat(),
            "delegate_from": m.delegate_from,
        }
