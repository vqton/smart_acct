from flask import Blueprint, current_app, request

ap_bp = Blueprint("ap", __name__, url_prefix="/api/v1/ap")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()

# ── JSON serializers ──────────────────────────────────────────

def _json_vendor(v):
    return {
        "id": v.id, "vendor_code": v.vendor_code, "vendor_name": v.vendor_name,
        "legal_name": v.legal_name, "tax_code": v.tax_code,
        "vendor_type": v.vendor_type.value, "vendor_group": v.vendor_group.value,
        "status": v.status.value, "email": v.email, "phone": v.phone,
        "address": v.address, "city": v.city, "country": v.country,
        "contact_person": v.contact_person, "payment_terms": v.payment_terms,
        "currency": v.currency, "bank_name": v.bank_name,
        "bank_account": v.bank_account, "bank_swift": v.bank_swift,
        "credit_limit": str(v.credit_limit), "coa_code": v.coa_code,
        "foreign_ct_type": v.foreign_ct_type,
        "foreign_vat_rate": float(v.foreign_vat_rate) if v.foreign_vat_rate else None,
        "foreign_cit_rate": float(v.foreign_cit_rate) if v.foreign_cit_rate else None,
        "notes": v.notes,
        "created_at": v.created_at.isoformat() if v.created_at else None,
        "updated_at": v.updated_at.isoformat() if v.updated_at else None,
    }

def _json_invoice(inv):
    return {
        "id": inv.id, "invoice_number": inv.invoice_number,
        "vendor_id": inv.vendor_id, "vendor_code": inv.vendor_code,
        "vendor_name": inv.vendor_name,
        "invoice_type": inv.invoice_type.value, "status": inv.status.value,
        "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
        "discount_date": inv.discount_date.isoformat() if inv.discount_date else None,
        "discount_percent": float(inv.discount_percent) if inv.discount_percent else None,
        "amount": str(inv.amount), "discount_amount": str(inv.discount_amount),
        "tax_amount": str(inv.tax_amount), "total_amount": str(inv.total_amount),
        "paid_amount": str(inv.paid_amount), "balance_due": str(inv.balance_due),
        "currency": inv.currency, "fx_rate": float(inv.fx_rate) if inv.fx_rate else None,
        "po_number": inv.po_number, "gr_number": inv.gr_number,
        "reference": inv.reference, "description": inv.description,
        "period": inv.period, "coa_code": inv.coa_code,
        "created_by": inv.created_by, "approved_by": inv.approved_by,
        "approved_at": inv.approved_at.isoformat() if inv.approved_at else None,
        "lines": [_json_invoice_line(l) for l in inv.lines] if inv.lines else [],
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }

def _json_invoice_line(l):
    return {
        "id": l.id, "line_number": l.line_number, "description": l.description,
        "quantity": str(l.quantity), "unit_price": str(l.unit_price),
        "line_amount": str(l.line_amount), "tax_rate": str(l.tax_rate),
        "tax_amount": str(l.tax_amount), "coa_code": l.coa_code,
        "po_line_number": l.po_line_number, "gr_line_number": l.gr_line_number,
    }

def _json_payment(p):
    return {
        "id": p.id, "payment_number": p.payment_number,
        "vendor_id": p.vendor_id,
        "payment_date": p.payment_date.isoformat() if p.payment_date else None,
        "amount": str(p.amount), "discount_taken": str(p.discount_taken),
        "net_amount": str(p.net_amount),
        "payment_method": p.payment_method.value if hasattr(p.payment_method, 'value') else p.payment_method,
        "bank_account_id": p.bank_account_id, "reference": p.reference,
        "status": p.status.value if hasattr(p.status, 'value') else p.status,
        "is_batch_payment": p.is_batch_payment, "batch_id": p.batch_id,
        "approval_by": p.approval_by,
        "approval_at": p.approval_at.isoformat() if p.approval_at else None,
        "notes": p.notes, "created_by": p.created_by,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

def _json_prepayment(pp):
    return {
        "id": pp.id, "vendor_id": pp.vendor_id, "amount": str(pp.amount),
        "unapplied_balance": str(pp.unapplied_balance),
        "payment_date": pp.payment_date.isoformat() if pp.payment_date else None,
        "expected_invoice_date": pp.expected_invoice_date.isoformat() if pp.expected_invoice_date else None,
        "reference": pp.reference, "status": pp.status.value if hasattr(pp.status, 'value') else pp.status,
        "created_by": pp.created_by,
        "created_at": pp.created_at.isoformat() if pp.created_at else None,
    }

def _json_provision(pr):
    return {
        "id": pr.id, "vendor_id": pr.vendor_id, "period": pr.period,
        "provision_percent": float(pr.provision_percent),
        "overdue_days": pr.overdue_days,
        "invoice_total": str(pr.invoice_total),
        "provision_amount": str(pr.provision_amount),
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
    }

def _json_fct(f):
    return {
        "id": f.id, "vendor_id": f.vendor_id, "period": f.period,
        "invoice_id": f.invoice_id,
        "fct_method": f.fct_method.value if hasattr(f.fct_method, 'value') else f.fct_method,
        "vat_rate": float(f.vat_rate), "cit_rate": float(f.cit_rate),
        "gross_amount": str(f.gross_amount), "vat_amount": str(f.vat_amount),
        "cit_amount": str(f.cit_amount), "net_amount": str(f.net_amount),
        "status": f.status.value if hasattr(f.status, 'value') else f.status,
        "declared_at": f.declared_at.isoformat() if f.declared_at else None,
        "remitted_at": f.remitted_at.isoformat() if f.remitted_at else None,
        "due_date": f.due_date.isoformat() if f.due_date else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


from . import routes  # noqa: E402
