from flask import Blueprint, current_app

tax_bp = Blueprint("tax", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_declaration(decl) -> dict:
    return {
        "id": decl.id,
        "tax_type": decl.tax_type.value,
        "declaration_type": decl.declaration_type.value,
        "form_code": decl.form_code,
        "period_year": decl.period_year,
        "period_month": decl.period_month,
        "period_quarter": decl.period_quarter,
        "status": decl.status.value,
        "total_revenue": str(decl.total_revenue),
        "total_tax": str(decl.total_tax),
        "total_deduction": str(decl.total_deduction),
        "total_exemption": str(decl.total_exemption),
        "total_payable": str(decl.total_payable),
        "previous_adjustment": str(decl.previous_adjustment),
        "late_interest": str(decl.late_interest),
        "penalty": str(decl.penalty),
        "net_payable": str(decl.net_payable),
        "submission_deadline": decl.submission_deadline.isoformat() if decl.submission_deadline else None,
        "submitted_date": decl.submitted_date.isoformat() if decl.submitted_date else None,
        "accepted_date": decl.accepted_date.isoformat() if decl.accepted_date else None,
        "gdt_reference": decl.gdt_reference,
        "gdt_error_code": decl.gdt_error_code,
        "etax_submission_id": decl.etax_submission_id,
        "submission_method": decl.submission_method,
        "notes": decl.notes,
        "created_by": decl.created_by,
        "created_at": decl.created_at.isoformat() if decl.created_at else None,
        "updated_at": decl.updated_at.isoformat() if decl.updated_at else None,
    }


def _json_payment(pmt) -> dict:
    return {
        "id": pmt.id,
        "declaration_id": pmt.declaration_id,
        "tax_type": pmt.tax_type.value,
        "amount": str(pmt.amount),
        "payment_date": pmt.payment_date.isoformat() if pmt.payment_date else None,
        "due_date": pmt.due_date.isoformat() if pmt.due_date else None,
        "budget_account": pmt.budget_account,
        "payment_method": pmt.payment_method,
        "payment_status": pmt.payment_status.value,
        "gdt_payment_code": pmt.gdt_payment_code,
        "bank_reference": pmt.bank_reference,
        "penalty_interest": str(pmt.penalty_interest),
        "notes": pmt.notes,
        "created_at": pmt.created_at.isoformat() if pmt.created_at else None,
    }


def _json_adjustment(adj) -> dict:
    return {
        "id": adj.id,
        "declaration_id": adj.declaration_id,
        "adjustment_type": adj.adjustment_type.value,
        "supplemental_declaration_id": adj.supplemental_declaration_id,
        "reason": adj.reason,
        "original_amount": str(adj.original_amount),
        "adjusted_amount": str(adj.adjusted_amount),
        "difference_amount": str(adj.difference_amount),
        "penalty_interest": str(adj.penalty_interest),
        "penalty": str(adj.penalty),
        "status": adj.status.value,
        "review_notes": adj.review_notes,
        "reviewed_by": adj.reviewed_by,
        "reviewed_at": adj.reviewed_at.isoformat() if adj.reviewed_at else None,
        "created_by": adj.created_by,
        "created_at": adj.created_at.isoformat() if adj.created_at else None,
        "updated_at": adj.updated_at.isoformat() if adj.updated_at else None,
    }


def _json_incentive(inc) -> dict:
    return {
        "id": inc.id,
        "tax_type": inc.tax_type.value,
        "incentive_type": inc.incentive_type.value,
        "code": inc.code,
        "name": inc.name,
        "legal_basis": inc.legal_basis,
        "rate_value": str(inc.rate_value),
        "is_percentage": inc.is_percentage,
        "valid_from": inc.valid_from.isoformat() if inc.valid_from else None,
        "valid_to": inc.valid_to.isoformat() if inc.valid_to else None,
        "max_duration_months": inc.max_duration_months,
        "eligibility_condition": inc.eligibility_condition,
        "requires_approval": inc.requires_approval,
        "status": inc.status.value,
        "created_at": inc.created_at.isoformat() if inc.created_at else None,
        "updated_at": inc.updated_at.isoformat() if inc.updated_at else None,
    }


def _json_line(line) -> dict:
    return {
        "id": line.id,
        "declaration_id": line.declaration_id,
        "line_code": line.line_code,
        "label": line.label,
        "amount": str(line.amount),
        "is_calculated": line.is_calculated,
        "parent_line_id": line.parent_line_id,
        "sort_order": line.sort_order,
        "notes": line.notes,
        "created_at": line.created_at.isoformat() if line.created_at else None,
        "updated_at": line.updated_at.isoformat() if line.updated_at else None,
    }


def _json_schedule(sched) -> dict:
    return {
        "id": sched.id,
        "tax_type": sched.tax_type.value,
        "period_year": sched.period_year,
        "period_month": sched.period_month,
        "period_quarter": sched.period_quarter,
        "due_date": sched.due_date.isoformat() if sched.due_date else None,
        "reminder_days_before": sched.reminder_days_before,
        "status": sched.status.value,
        "assigned_to": sched.assigned_to,
        "notes": sched.notes,
        "created_at": sched.created_at.isoformat() if sched.created_at else None,
        "updated_at": sched.updated_at.isoformat() if sched.updated_at else None,
    }


def _json_invoice(inv) -> dict:
    return {
        "id": inv.id,
        "invoice_number": inv.invoice_number,
        "invoice_series": inv.invoice_series,
        "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
        "invoice_type": inv.invoice_type.value,
        "seller_tax_code": inv.seller_tax_code,
        "seller_name": inv.seller_name,
        "seller_address": inv.seller_address,
        "buyer_tax_code": inv.buyer_tax_code,
        "buyer_name": inv.buyer_name,
        "buyer_address": inv.buyer_address,
        "buyer_id": inv.buyer_id,
        "subtotal": str(inv.subtotal),
        "discount_amount": str(inv.discount_amount),
        "vat_rate": str(inv.vat_rate),
        "vat_amount": str(inv.vat_amount),
        "grand_total": str(inv.grand_total),
        "currency": inv.currency,
        "exchange_rate": str(inv.exchange_rate),
        "payment_method": inv.payment_method,
        "status": inv.status.value,
        "verification_code": inv.verification_code,
        "gdt_transaction_id": inv.gdt_transaction_id,
        "signed_file_url": inv.signed_file_url,
        "digital_signature": inv.digital_signature,
        "adjustment_ref_id": inv.adjustment_ref_id,
        "adjustment_type": inv.adjustment_type.value if inv.adjustment_type else None,
        "adjustment_reason": inv.adjustment_reason,
        "original_invoice_ref": inv.original_invoice_ref,
        "created_by": inv.created_by,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


from . import declarations, payments, invoices, schedule  # noqa: E402
