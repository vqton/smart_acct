from flask import request, jsonify
from presentation import resolve_error
from presentation.tax import tax_bp, _get_session, _json_invoice
from use_cases.tax_use_cases import TaxUseCases
from domain import InvoiceType, InvoiceStatus, EInvoice
from datetime import date
from decimal import Decimal


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
