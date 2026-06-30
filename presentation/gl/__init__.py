from flask import Blueprint, current_app

gl_bp = Blueprint("gl", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_line(line) -> dict:
    return {
        "id": line.id,
        "account_id": line.account_id,
        "debit": str(line.debit),
        "credit": str(line.credit),
        "description": line.description,
        "vat_rate": str(line.vat_rate) if line.vat_rate else None,
        "line_type": line.line_type,
        "is_taxable": line.is_taxable,
        "tax_code": line.tax_code,
    }


def _json_entry(entry) -> dict:
    return {
        "id": entry.id,
        "journal_number": entry.journal_number,
        "journal_type": entry.journal_type.value if hasattr(entry, 'journal_type') and entry.journal_type else "general",
        "transaction_date": entry.transaction_date.isoformat(),
        "description": entry.description,
        "period": entry.period,
        "is_posted": entry.is_posted,
        "posted_date": entry.posted_date.isoformat() if entry.posted_date else None,
        "source_module": entry.source_module,
        "created_by": entry.created_by,
        "approved_by": entry.approved_by,
        "is_approved": entry.is_approved,
        "approval_date": entry.approval_date.isoformat() if entry.approval_date else None,
        "correction_method": entry.correction_method.value if hasattr(entry, 'correction_method') and entry.correction_method else None,
        "ref_journal_number": entry.ref_journal_number,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        "lines": [_json_line(l) for l in entry.lines],
    }


from . import entries, periods, sequences, subsidiary, reports  # noqa: E402
