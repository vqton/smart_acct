from flask import Blueprint

approval_bp = Blueprint("approval", __name__, template_folder="../../templates/approval")

from presentation.approval import routes


def serialize_workflow(wf: dict) -> dict:
    return {
        "id": wf.get("id"),
        "name": wf.get("name"),
        "description": wf.get("description"),
        "object_type": wf.get("object_type"),
        "strategy": wf.get("strategy"),
        "quorum_percentage": wf.get("quorum_percentage"),
        "is_active": wf.get("is_active", True),
        "steps": wf.get("steps", []),
        "created_at": wf.get("created_at"),
        "updated_at": wf.get("updated_at"),
    }


def serialize_request(req: dict) -> dict:
    return {
        "id": req.get("id"),
        "workflow_id": req.get("workflow_id"),
        "object_type": req.get("object_type"),
        "object_id": req.get("object_id"),
        "object_reference": req.get("object_reference"),
        "amount": req.get("amount"),
        "submitted_by": req.get("submitted_by"),
        "submitted_at": req.get("submitted_at"),
        "status": req.get("status"),
        "current_step_order": req.get("current_step_order"),
        "history": req.get("history", []),
    }
