from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.ar import ar_bp, _get_session, _json_customer, _json_invoice, _json_payment
from use_cases.ar import ARUseCases
from domain import CustomerType, CustomerGroup, CustomerStatus, ARInvoiceType, ARInvoiceStatus, ARPaymentMethod, InvoiceLine


# ── Customers ─────────────────────────────────────────────────────

@ar_bp.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = ARUseCases(session)
        result = uc.create_customer(
            customer_code=data["customer_code"],
            customer_name=data["customer_name"],
            customer_type=CustomerType(data.get("customer_type", "enterprise")),
            customer_group=CustomerGroup(data.get("customer_group", "domestic")),
            tax_code=data.get("tax_code"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            contact_person=data.get("contact_person"),
            credit_limit=Decimal(str(data["credit_limit"])) if data.get("credit_limit") else Decimal("0"),
            coa_account_code=data.get("coa_account_code"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_customer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/customers", methods=["GET"])
def list_customers():
    session = _get_session()
    try:
        uc = ARUseCases(session)
        search = request.args.get("search")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        customers = uc.list_customers(search=search, limit=limit, offset=offset)
        return jsonify({"customers": [_json_customer(c) for c in customers], "total": len(customers)})
    finally:
        session.close()


@ar_bp.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        customer = uc.get_customer(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(_json_customer(customer))
    finally:
        session.close()


@ar_bp.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = ARUseCases(session)
        # Build updates dict from allowed fields
        updates = {}
        for field in ["legal_name", "tax_code", "email", "phone", "address", "city",
                      "contact_person", "credit_limit", "outstanding_balance",
                      "coa_account_code", "notes"]:
            if field in data:
                updates[field] = data[field]
        if "status" in data:
            updates["status"] = CustomerStatus(data["status"])
        customer = uc.update_customer(customer_id, **updates)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        session.commit()
        return jsonify(_json_customer(customer))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    # Deletion is complex in AR - just return not implemented for now
    return jsonify({"error": "Customer deletion not implemented"}), 501


@ar_bp.route("/customers/<int:customer_id>/suspend", methods=["POST"])
def suspend_customer(customer_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        result = uc.suspend_customer(customer_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_customer(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/customers/<int:customer_id>/invoices", methods=["GET"])
def get_customer_invoices(customer_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        invoices = uc.list_invoices(customer_id=customer_id)
        return jsonify({"invoices": [_json_invoice(i) for i in invoices], "total": len(invoices)})
    finally:
        session.close()


# ── Invoices ──────────────────────────────────────────────────────

@ar_bp.route("/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = ARUseCases(session)
        lines_data = data.get("lines", [])
        lines = []
        for idx, line_data in enumerate(lines_data, start=1):
            lines.append(InvoiceLine(
                line_number=idx,
                description=line_data["description"],
                quantity=Decimal(str(line_data["quantity"])),
                unit_price=Decimal(str(line_data["unit_price"])),
                line_amount=Decimal(str(line_data["line_amount"])),
                tax_rate=Decimal(str(line_data.get("tax_rate", "0"))),
                tax_amount=Decimal(str(line_data.get("tax_amount", "0"))),
                coa_code=line_data.get("coa_code"),
            ))
        result = uc.create_invoice(
            invoice_number=data["invoice_number"],
            customer_id=data["customer_id"],
            customer_code=data["customer_code"],
            customer_name=data["customer_name"],
            issue_date=date.fromisoformat(data["issue_date"]),
            due_date=date.fromisoformat(data["due_date"]),
            amount=Decimal(str(data["amount"])),
            lines=lines,
            invoice_type=ARInvoiceType(data.get("invoice_type", "sales")),
            discount_amount=Decimal(str(data.get("discount_amount", "0"))),
            tax_amount=Decimal(str(data.get("tax_amount", "0"))),
            payment_terms_days=data.get("payment_terms_days", 30),
            reference=data.get("reference"),
            notes=data.get("notes"),
            period=data.get("period"),
            coa_code=data.get("coa_code"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/invoices", methods=["GET"])
def list_invoices():
    session = _get_session()
    try:
        uc = ARUseCases(session)
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        invoices = uc.list_invoices(limit=limit, offset=offset)
        return jsonify({"invoices": [_json_invoice(i) for i in invoices], "total": len(invoices)})
    finally:
        session.close()


@ar_bp.route("/invoices/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        invoice = uc.get_invoice(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(_json_invoice(invoice))
    finally:
        session.close()


@ar_bp.route("/invoices/<int:invoice_id>/issue", methods=["POST"])
def issue_invoice(invoice_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        result = uc.issue_invoice(invoice_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/invoices/<int:invoice_id>/cancel", methods=["POST"])
def cancel_invoice(invoice_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        result = uc.cancel_invoice(invoice_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ar_bp.route("/invoices/<int:invoice_id>/payments", methods=["POST"])
def record_payment(invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = ARUseCases(session)
        result = uc.record_payment(
            invoice_id=invoice_id,
            payment_number=data["payment_number"],
            amount=Decimal(str(data["amount"])),
            payment_date=date.fromisoformat(data["payment_date"]),
            payment_method=ARPaymentMethod(data.get("payment_method", "cash")),
            reference=data.get("reference"),
            notes=data.get("notes"),
            received_by=data.get("received_by"),
            bank_account_id=data.get("bank_account_id"),
            coa_code=data.get("coa_code"),
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


@ar_bp.route("/invoices/<int:invoice_id>/payments", methods=["GET"])
def list_payments(invoice_id):
    session = _get_session()
    try:
        uc = ARUseCases(session)
        payments = uc.get_payments_for_invoice(invoice_id)
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


# ── Aging & Reports ───────────────────────────────────────────────

@ar_bp.route("/aging-report", methods=["GET"])
def get_aging_report():
    session = _get_session()
    try:
        uc = ARUseCases(session)
        report = uc.get_aging_report()
        return jsonify({"aging": report})
    finally:
        session.close()


@ar_bp.route("/ar-balance", methods=["GET"])
def get_ar_balance():
    period = request.args.get("period", "current")
    session = _get_session()
    try:
        uc = ARUseCases(session)
        balance = uc.get_ar_balance_sheet(period)
        return jsonify(balance)
    finally:
        session.close()

