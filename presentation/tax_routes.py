from flask import Blueprint, request, jsonify, current_app
from datetime import date
from decimal import Decimal

from use_cases.tax_use_cases import TaxUseCases
from domain import (
    TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus,
    TaxPaymentStatus, InvoiceStatus, TaxAdjustmentType, TaxIncentiveType,
    InvoiceType, EInvoice,
)
from infrastructure.database import DatabaseError
from presentation import resolve_error

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


# ════════════════════════════════════════════════════
# TaxDeclaration
# ════════════════════════════════════════════════════

@tax_bp.route("/declarations", methods=["POST"])
def create_declaration():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_declaration(
            tax_type=TaxType(data["tax_type"]),
            form_code=data["form_code"],
            period_year=data["period_year"],
            declaration_type=DeclarationType(data.get("declaration_type", "original")),
            period_month=data.get("period_month"),
            period_quarter=data.get("period_quarter"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_declaration(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/declarations", methods=["GET"])
def list_declarations():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        tax_type = request.args.get("tax_type")
        period_year = request.args.get("period_year")
        status = request.args.get("status")
        decl_type = request.args.get("declaration_type")

        declarations = uc.list_declarations(
            tax_type=TaxType(tax_type) if tax_type else None,
            period_year=int(period_year) if period_year else None,
            status=DeclarationStatus(status) if status else None,
            declaration_type=DeclarationType(decl_type) if decl_type else None,
        )
        return jsonify({
            "declarations": [_json_declaration(d) for d in declarations],
            "total": len(declarations),
        })
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>", methods=["GET"])
def get_declaration(decl_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_declaration(decl_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_declaration(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>", methods=["PUT"])
def update_declaration(decl_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        allowed = {"status", "notes", "total_revenue", "total_tax", "total_payable", "net_payable"}
        kwargs = {k: v for k, v in data.items() if k in allowed}
        result = uc.update_declaration(decl_id, **kwargs)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_declaration(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>", methods=["DELETE"])
def delete_declaration(decl_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_declaration(decl_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Declaration {decl_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>/submit", methods=["POST"])
def submit_declaration(decl_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.submit_declaration(decl_id, gdt_reference=data.get("gdt_reference"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_declaration(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>/calculate", methods=["POST"])
def calculate_vat(decl_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        method = VATCalculationMethod(data.get("method", "deduction"))
        result = uc.calculate_vat(
            decl_id,
            method=method,
            input_lines=data.get("input_lines"),
            output_lines=data.get("output_lines"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# TaxLine
# ════════════════════════════════════════════════════

@tax_bp.route("/declarations/<int:decl_id>/lines", methods=["POST"])
def create_line(decl_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_line(
            declaration_id=decl_id,
            line_code=data["line_code"],
            label=data["label"],
            amount=Decimal(str(data.get("amount", 0))),
            is_calculated=data.get("is_calculated", True),
            parent_line_id=data.get("parent_line_id"),
            sort_order=data.get("sort_order", 0),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_line(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/declarations/<int:decl_id>/lines", methods=["GET"])
def list_lines(decl_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        lines = uc.list_lines(declaration_id=decl_id)
        return jsonify({"lines": [_json_line(l) for l in lines], "total": len(lines)})
    finally:
        session.close()


@tax_bp.route("/lines/<int:line_id>", methods=["GET"])
def get_line(line_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_line(line_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_line(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/lines/<int:line_id>", methods=["PUT"])
def update_line(line_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_line(line_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_line(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/lines/<int:line_id>", methods=["DELETE"])
def delete_line(line_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_line(line_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Line {line_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# TaxPayment
# ════════════════════════════════════════════════════

@tax_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_payment(
            declaration_id=data["declaration_id"],
            amount=Decimal(str(data["amount"])),
            due_date=date.fromisoformat(data["due_date"]),
            payment_date=date.fromisoformat(data["payment_date"]),
            tax_type=TaxType(data["tax_type"]),
            budget_account=data.get("budget_account", "1701"),
            payment_method=data.get("payment_method", "etax"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/payments", methods=["GET"])
def list_payments():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        decl_id = request.args.get("declaration_id", type=int)
        payments = uc.list_payments(declaration_id=decl_id)
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_payment(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["PUT"])
def update_payment(payment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_payment(payment_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Payment {payment_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# TaxAdjustment
# ════════════════════════════════════════════════════

@tax_bp.route("/adjustments", methods=["POST"])
def create_adjustment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_adjustment(
            declaration_id=data["declaration_id"],
            adjustment_type=TaxAdjustmentType(data["adjustment_type"]),
            reason=data["reason"],
            original_amount=Decimal(str(data["original_amount"])),
            adjusted_amount=Decimal(str(data["adjusted_amount"])),
            supplemental_declaration_id=data.get("supplemental_declaration_id"),
            penalty_interest=Decimal(str(data.get("penalty_interest", 0))),
            penalty=Decimal(str(data.get("penalty", 0))),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/adjustments", methods=["GET"])
def list_adjustments():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        decl_id = request.args.get("declaration_id", type=int)
        adjustments = uc.list_adjustments(declaration_id=decl_id)
        return jsonify({
            "adjustments": [_json_adjustment(a) for a in adjustments],
            "total": len(adjustments),
        })
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["GET"])
def get_adjustment(adj_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_adjustment(adj_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_adjustment(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["PUT"])
def update_adjustment(adj_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_adjustment(adj_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["DELETE"])
def delete_adjustment(adj_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_adjustment(adj_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Adjustment {adj_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# TaxIncentive
# ════════════════════════════════════════════════════

@tax_bp.route("/incentives", methods=["POST"])
def create_incentive():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_incentive(
            tax_type=TaxType(data["tax_type"]),
            incentive_type=TaxIncentiveType(data["incentive_type"]),
            code=data["code"],
            name=data["name"],
            legal_basis=data["legal_basis"],
            rate_value=Decimal(str(data.get("rate_value", 0))),
            is_percentage=data.get("is_percentage", True),
            valid_from=date.fromisoformat(data["valid_from"]),
            valid_to=date.fromisoformat(data["valid_to"]) if data.get("valid_to") else None,
            max_duration_months=data.get("max_duration_months"),
            eligibility_condition=data.get("eligibility_condition"),
            requires_approval=data.get("requires_approval", False),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_incentive(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/incentives", methods=["GET"])
def list_incentives():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        tax_type = request.args.get("tax_type")
        incentives = uc.list_incentives(
            tax_type=TaxType(tax_type) if tax_type else None,
        )
        return jsonify({
            "incentives": [_json_incentive(i) for i in incentives],
            "total": len(incentives),
        })
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["GET"])
def get_incentive(incentive_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_incentive(incentive_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_incentive(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["PUT"])
def update_incentive(incentive_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_incentive(incentive_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_incentive(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["DELETE"])
def delete_incentive(incentive_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_incentive(incentive_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Incentive {incentive_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# EInvoice
# ════════════════════════════════════════════════════

@tax_bp.route("/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        invoice = EInvoice(
            invoice_number=data["invoice_number"],
            invoice_series=data["invoice_series"],
            invoice_date=date.fromisoformat(data["invoice_date"]),
            invoice_type=InvoiceType(data.get("invoice_type", "sales")),
            seller_tax_code=data["seller_tax_code"],
            seller_name=data["seller_name"],
            seller_address=data.get("seller_address"),
            buyer_tax_code=data.get("buyer_tax_code"),
            buyer_name=data.get("buyer_name"),
            buyer_address=data.get("buyer_address"),
            buyer_id=data.get("buyer_id"),
            subtotal=Decimal(str(data.get("subtotal", 0))),
            discount_amount=Decimal(str(data.get("discount_amount", 0))),
            vat_rate=Decimal(str(data.get("vat_rate", 0))),
            vat_amount=Decimal(str(data.get("vat_amount", 0))),
            grand_total=Decimal(str(data.get("grand_total", 0))),
            currency=data.get("currency", "VND"),
            created_by=data.get("created_by"),
        )
        result = uc.create_invoice(invoice)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/invoices", methods=["GET"])
def list_invoices():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        status_str = request.args.get("status")
        status_enum = InvoiceStatus(status_str) if status_str else None
        invoices = uc.list_invoices(status=status_enum)
        return jsonify({
            "invoices": [_json_invoice(i) for i in invoices],
            "total": len(invoices),
        })
    finally:
        session.close()


@tax_bp.route("/invoices/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_invoice(invoice_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_invoice(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/invoices/<int:invoice_id>", methods=["PUT"])
def update_invoice(invoice_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_invoice(invoice_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/invoices/<int:invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_invoice(invoice_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Invoice {invoice_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/invoices/<int:invoice_id>/status", methods=["PUT"])
def update_invoice_status(invoice_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        status = InvoiceStatus(data["status"])
        result = uc.update_invoice_status(
            invoice_id, status=status,
            verification_code=data.get("verification_code"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# TaxSchedule
# ════════════════════════════════════════════════════

@tax_bp.route("/schedule", methods=["GET"])
def get_schedule():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        year = request.args.get("year", type=int)
        tax_type_str = request.args.get("tax_type")
        schedules = uc.get_tax_schedule(
            year=year or date.today().year,
            tax_type=TaxType(tax_type_str) if tax_type_str else None,
        )
        return jsonify({
            "schedules": [_json_schedule(s) for s in schedules],
            "total": len(schedules),
        })
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["GET"])
def get_schedule_item(schedule_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_schedule(schedule_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_schedule(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_schedule(schedule_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_schedule(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_schedule(schedule_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Schedule {schedule_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# Schedule Generation
# ════════════════════════════════════════════════════

@tax_bp.route("/schedule/generate", methods=["POST"])
def generate_schedule():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        year = data.get("year", date.today().year)
        result = uc.generate_schedule(year=year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

# ════════════════════════════════════════════════════
# Reminders
# ════════════════════════════════════════════════════

@tax_bp.route("/reminders", methods=["GET"])
def get_reminders():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        days = request.args.get("days", 7, type=int)
        reminders = uc.get_due_reminders(days_ahead=days)
        return jsonify({
            "reminders": [_json_schedule(r) for r in reminders],
            "total": len(reminders),
        })
    finally:
        session.close()

# ════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════

@tax_bp.route("/summary", methods=["GET"])
def summary():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_summary()
        return jsonify(result.get_data())
    finally:
        session.close()
