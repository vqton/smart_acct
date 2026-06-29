from flask import Blueprint, current_app, jsonify, request

ar_bp = Blueprint("ar", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_customer(c):
    return {
        "id": c.id,
        "customer_code": c.customer_code,
        "customer_name": c.customer_name,
        "legal_name": c.legal_name,
        "tax_code": c.tax_code,
        "customer_type": c.customer_type.value,
        "customer_group": c.customer_group.value,
        "status": c.status.value,
        "email": c.email,
        "phone": c.phone,
        "address": c.address,
        "city": c.city,
        "country": c.country,
        "contact_person": c.contact_person,
        "credit_limit": str(c.credit_limit),
        "outstanding_balance": str(c.outstanding_balance),
        "coa_account_code": c.coa_account_code,
        "notes": c.notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_invoice_line(l):
    return {
        "id": l.id,
        "line_number": l.line_number,
        "description": l.description,
        "quantity": str(l.quantity),
        "unit_price": str(l.unit_price),
        "line_amount": str(l.line_amount),
        "tax_rate": str(l.tax_rate),
        "tax_amount": str(l.tax_amount),
        "coa_code": l.coa_code,
    }


def _json_invoice(inv):
    return {
        "id": inv.id,
        "invoice_number": inv.invoice_number,
        "customer_id": inv.customer_id,
        "customer_code": inv.customer_code,
        "customer_name": inv.customer_name,
        "invoice_type": inv.invoice_type.value,
        "status": inv.status.value,
        "issue_date": inv.issue_date.isoformat(),
        "due_date": inv.due_date.isoformat(),
        "amount": str(inv.amount),
        "discount_amount": str(inv.discount_amount),
        "tax_amount": str(inv.tax_amount),
        "total_amount": str(inv.total_amount),
        "paid_amount": str(inv.paid_amount),
        "written_off_amount": str(inv.written_off_amount),
        "balance_due": str(inv.balance_due),
        "payment_terms_days": inv.payment_terms_days,
        "reference": inv.reference,
        "notes": inv.notes,
        "period": inv.period,
        "posted_at": inv.posted_at.isoformat() if inv.posted_at else None,
        "posted_by": inv.posted_by,
        "coa_code": inv.coa_code,
        "einvoice_id": inv.einvoice_id,
        "lines": [_json_invoice_line(l) for l in inv.lines],
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


def _json_payment(p):
    return {
        "id": p.id,
        "payment_number": p.payment_number,
        "invoice_id": p.invoice_id,
        "payment_date": p.payment_date.isoformat(),
        "amount": str(p.amount),
        "payment_method": p.payment_method.value,
        "reference": p.reference,
        "notes": p.notes,
        "received_by": p.received_by,
        "bank_account_id": p.bank_account_id,
        "coa_code": p.coa_code,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


from . import routes  # noqa: E402

