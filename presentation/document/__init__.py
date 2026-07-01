from typing import Optional
from flask import Blueprint, current_app

document_bp = Blueprint("document", __name__, url_prefix="/api/v1/documents")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


_doc_use_cases: Optional[object] = None


def _get_doc_use_cases():
    global _doc_use_cases
    if _doc_use_cases is None:
        from use_cases.document import DocumentUseCases
        _doc_use_cases = DocumentUseCases(session_factory=_get_session)
    return _doc_use_cases


from . import routes  # noqa: E402
