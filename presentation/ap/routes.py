from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.ap import ap_bp, _get_session, _json_vendor, _json_invoice, _json_payment, _json_prepayment, _json_provision, _json_fct
from use_cases.ap import APUseCases
from domain import (
    VendorType, VendorGroup, VendorStatus,
    APInvoiceType, APInvoiceStatus, APInvoiceLine,
    APPaymentMethod, APPaymentStatus,
    PrepaymentStatus, FCTMethod, FCTStatus,
)


# ── Vendors ─────────────────────────────────────────────────────

@ap_bp.route("/vendors", methods=["POST"])
def create_vendor():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_vendor(
            vendor_code=data["vendor_code"],
            vendor_name=data["vendor_name"],
            vendor_type=VendorType(data.get("vendor_type", "enterprise")),
            vendor_group=VendorGroup(data.get("vendor_group", "domestic")),
            tax_code=data.get("tax_code"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            country=data.get("country", "VN"),
            contact_person=data.get("contact_person"),
            payment_terms=data.get("payment_terms", "net_30"),
            currency=data.get("currency", "VND"),
            bank_name=data.get("bank_name"),
            bank_account=data.get("bank_account"),
            bank_swift=data.get("bank_swift"),
            credit_limit=Decimal(str(data.get("credit_limit", "0"))),
            coa_code=data.get("coa_code"),
            foreign_ct_type=data.get("foreign_ct_type"),
            foreign_vat_rate=Decimal(str(data["foreign_vat_rate"])) if data.get("foreign_vat_rate") else None,
            foreign_cit_rate=Decimal(str(data["foreign_cit_rate"])) if data.get("foreign_cit_rate") else None,
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_vendor(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/vendors", methods=["GET"])
def list_vendors():
    session = _get_session()
    try:
        uc = APUseCases(session)
        search = request.args.get("search")
        vendor_type_raw = request.args.get("vendor_type")
        vendor_group_raw = request.args.get("vendor_group")
        status_raw = request.args.get("status")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        vendor_type = VendorType(vendor_type_raw) if vendor_type_raw else None
        vendor_group = VendorGroup(vendor_group_raw) if vendor_group_raw else None
        status = VendorStatus(status_raw) if status_raw else None
        vendors = uc.list_vendors(
            vendor_type=vendor_type, vendor_group=vendor_group,
            status=status, search=search, limit=limit, offset=offset,
        )
        return jsonify({"vendors": [_json_vendor(v) for v in vendors], "total": len(vendors)})
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        vendor = uc.get_vendor(vendor_id)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        return jsonify(_json_vendor(vendor))
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>", methods=["PUT"])
def update_vendor(vendor_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = APUseCases(session)
        updates = {}
        for field in ["vendor_name", "legal_name", "tax_code", "email", "phone", "address", "city",
                      "contact_person", "payment_terms", "currency", "bank_name", "bank_account",
                      "bank_swift", "credit_limit", "coa_code", "notes",
                      "foreign_ct_type", "foreign_vat_rate", "foreign_cit_rate",
                      "vendor_type", "vendor_group"]:
            if field in data:
                updates[field] = data[field]
        if "status" in data:
            updates["status"] = VendorStatus(data["status"])
        vendor = uc.update_vendor(vendor_id, **updates)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        session.commit()
        return jsonify(_json_vendor(vendor))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>", methods=["DELETE"])
def delete_vendor(vendor_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.delete_vendor(vendor_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Vendor deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>/suspend", methods=["POST"])
def suspend_vendor(vendor_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.suspend_vendor(vendor_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_vendor(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>/activate", methods=["POST"])
def activate_vendor(vendor_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.activate_vendor(vendor_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_vendor(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/vendors/<int:vendor_id>/block", methods=["POST"])
def block_vendor(vendor_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.block_vendor(vendor_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_vendor(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Invoices ────────────────────────────────────────────────────

@ap_bp.route("/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        lines_data = data.get("lines", [])
        lines = []
        for idx, line_data in enumerate(lines_data, start=1):
            lines.append(APInvoiceLine(
                line_number=idx,
                description=line_data["description"],
                quantity=Decimal(str(line_data["quantity"])),
                unit_price=Decimal(str(line_data["unit_price"])),
                line_amount=Decimal(str(line_data["line_amount"])),
                tax_rate=Decimal(str(line_data.get("tax_rate", "0.10"))),
                tax_amount=Decimal(str(line_data.get("tax_amount", "0"))),
                coa_code=line_data.get("coa_code"),
                po_line_number=line_data.get("po_line_number"),
                gr_line_number=line_data.get("gr_line_number"),
            ))
        result = uc.create_invoice(
            invoice_number=data["invoice_number"],
            vendor_id=data["vendor_id"],
            invoice_date=date.fromisoformat(data["invoice_date"]),
            due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            amount=Decimal(str(data["amount"])),
            lines=lines,
            invoice_type=APInvoiceType(data.get("invoice_type", "non_po")),
            discount_amount=Decimal(str(data.get("discount_amount", "0"))),
            discount_percent=Decimal(str(data["discount_percent"])) if data.get("discount_percent") else None,
            discount_date=date.fromisoformat(data["discount_date"]) if data.get("discount_date") else None,
            tax_amount=Decimal(str(data.get("tax_amount", "0"))),
            total_amount=Decimal(str(data["total_amount"])) if data.get("total_amount") else None,
            currency=data.get("currency", "VND"),
            fx_rate=Decimal(str(data["fx_rate"])) if data.get("fx_rate") else None,
            po_number=data.get("po_number"),
            gr_number=data.get("gr_number"),
            reference=data.get("reference"),
            description=data.get("description"),
            period=data.get("period"),
            coa_code=data.get("coa_code"),
            created_by=data.get("created_by"),
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


@ap_bp.route("/invoices", methods=["GET"])
def list_invoices():
    session = _get_session()
    try:
        uc = APUseCases(session)
        vendor_id = request.args.get("vendor_id", type=int)
        vendor_code = request.args.get("vendor_code")
        status_raw = request.args.get("status")
        period = request.args.get("period")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        status = APInvoiceStatus(status_raw) if status_raw else None
        invoices = uc.list_invoices(
            vendor_id=vendor_id, vendor_code=vendor_code,
            status=status, period=period, limit=limit, offset=offset,
        )
        return jsonify({"invoices": [_json_invoice(i) for i in invoices], "total": len(invoices)})
    finally:
        session.close()


@ap_bp.route("/invoices/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        invoice = uc.get_invoice(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(_json_invoice(invoice))
    finally:
        session.close()


@ap_bp.route("/invoices/<int:invoice_id>/approve", methods=["POST"])
def approve_invoice(invoice_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.approve_invoice(invoice_id, approved_by=data.get("approved_by"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/invoices/<int:invoice_id>/cancel", methods=["POST"])
def cancel_invoice(invoice_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.cancel_invoice(invoice_id, reason=data.get("reason"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_invoice(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/invoices/<int:invoice_id>/credit-note", methods=["POST"])
def create_credit_note(invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_credit_note(
            invoice_id=invoice_id,
            reason=data["reason"],
            amount=Decimal(str(data["amount"])),
            tax_adjustment=Decimal(str(data.get("tax_adjustment", "0"))),
            created_by=data.get("created_by"),
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


@ap_bp.route("/invoices/<int:invoice_id>/debit-note", methods=["POST"])
def create_debit_note(invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_debit_note(
            invoice_id=invoice_id,
            reason=data["reason"],
            amount=Decimal(str(data["amount"])),
            created_by=data.get("created_by"),
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


# ── Payments ────────────────────────────────────────────────────

@ap_bp.route("/invoices/<int:invoice_id>/payments", methods=["POST"])
def record_payment(invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.record_payment(
            invoice_id=invoice_id,
            payment_number=data["payment_number"],
            amount=Decimal(str(data["amount"])),
            payment_date=date.fromisoformat(data["payment_date"]),
            payment_method=APPaymentMethod(data.get("payment_method", "bank_transfer")),
            discount_taken=Decimal(str(data.get("discount_taken", "0"))),
            reference=data.get("reference"),
            notes=data.get("notes"),
            bank_account_id=data.get("bank_account_id"),
            created_by=data.get("created_by"),
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


@ap_bp.route("/invoices/<int:invoice_id>/payments", methods=["GET"])
def list_payments_for_invoice(invoice_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        payments = uc.get_payments_for_invoice(invoice_id)
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


@ap_bp.route("/payments", methods=["GET"])
def list_all_payments():
    session = _get_session()
    try:
        uc = APUseCases(session)
        vendor_id = request.args.get("vendor_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        from_arg = date.fromisoformat(date_from) if date_from else None
        to_arg = date.fromisoformat(date_to) if date_to else None
        payments = uc.list_payments(
            vendor_id=vendor_id, date_from=from_arg,
            date_to=to_arg, limit=limit, offset=offset,
        )
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


@ap_bp.route("/payments/proposal", methods=["POST"])
def create_payment_proposal():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_payment_proposal(
            vendor_ids=data["vendor_ids"],
            due_date_from=date.fromisoformat(data["due_date_from"]),
            due_date_to=date.fromisoformat(data["due_date_to"]),
            payment_method=APPaymentMethod(data.get("payment_method", "bank_transfer")),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data()), 201
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/payments/<int:payment_id>/approve", methods=["POST"])
def approve_payment(payment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.approve_payment_proposal(
            proposal_id=payment_id,
            approved_by=data.get("approved_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/payments/<int:payment_id>/execute", methods=["POST"])
def execute_payment(payment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.execute_payment(
            payment_id=payment_id,
            executed_by=data.get("executed_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Prepayments ─────────────────────────────────────────────────

@ap_bp.route("/prepayments", methods=["POST"])
def create_prepayment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_prepayment(
            vendor_id=data["vendor_id"],
            amount=Decimal(str(data["amount"])),
            payment_date=date.fromisoformat(data["payment_date"]),
            expected_invoice_date=date.fromisoformat(data["expected_invoice_date"]) if data.get("expected_invoice_date") else None,
            reference=data.get("reference"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_prepayment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/prepayments/<int:prepayment_id>/apply", methods=["POST"])
def apply_prepayment(prepayment_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.apply_prepayment(
            prepayment_id=prepayment_id,
            invoice_id=data["invoice_id"],
            amount=Decimal(str(data["amount"])),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Prepayment applied"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/prepayments", methods=["GET"])
def list_prepayments():
    session = _get_session()
    try:
        uc = APUseCases(session)
        vendor_id = request.args.get("vendor_id", type=int)
        if not vendor_id:
            return jsonify({"error": "vendor_id query parameter required"}), 400
        prepayments = uc.get_prepayments(vendor_id)
        return jsonify({"prepayments": [_json_prepayment(p) for p in prepayments], "total": len(prepayments)})
    finally:
        session.close()


# ── Aging & Reports ─────────────────────────────────────────────

@ap_bp.route("/aging", methods=["GET"])
def get_aging_report():
    session = _get_session()
    try:
        uc = APUseCases(session)
        vendor_id = request.args.get("vendor_id", type=int)
        as_of = request.args.get("as_of_date")
        as_of_date = date.fromisoformat(as_of) if as_of else None
        report = uc.get_aging_report(as_of_date=as_of_date, vendor_id=vendor_id)
        return jsonify({"aging": report})
    finally:
        session.close()


@ap_bp.route("/aging/snapshot", methods=["POST"])
def create_aging_snapshot():
    data = request.get_json() or {}
    period = data.get("period", date.today().strftime("%Y-%m"))
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_aging_snapshot(period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/aging/snapshot/<period>", methods=["GET"])
def get_aging_snapshot(period):
    session = _get_session()
    try:
        uc = APUseCases(session)
        snapshots = uc.get_aging_snapshots(period)
        return jsonify({"period": period, "snapshots": snapshots})
    finally:
        session.close()


@ap_bp.route("/provisions/calculate", methods=["POST"])
def create_provisions():
    data = request.get_json() or {}
    period = data.get("period", date.today().strftime("%Y-%m"))
    as_of_date = date.fromisoformat(data["as_of_date"]) if data.get("as_of_date") else date.today()
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.create_provisions(period, as_of_date)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/provisions/<period>", methods=["GET"])
def get_provisions(period):
    session = _get_session()
    try:
        uc = APUseCases(session)
        provisions = uc.get_provisions(period)
        return jsonify({"period": period, "provisions": [_json_provision(p) for p in provisions]})
    finally:
        session.close()


@ap_bp.route("/reports/balance", methods=["GET"])
def get_ap_balance():
    period = request.args.get("period", date.today().strftime("%Y-%m"))
    session = _get_session()
    try:
        uc = APUseCases(session)
        balance = uc.get_ap_balance(period)
        return jsonify(balance)
    finally:
        session.close()


@ap_bp.route("/reports/turnover", methods=["GET"])
def get_ap_turnover():
    period = request.args.get("period", date.today().strftime("%Y-%m"))
    session = _get_session()
    try:
        uc = APUseCases(session)
        turnover = uc.get_ap_turnover(period)
        return jsonify(turnover)
    finally:
        session.close()


@ap_bp.route("/reports/dpo", methods=["GET"])
def get_dpo():
    period = request.args.get("period", date.today().strftime("%Y-%m"))
    session = _get_session()
    try:
        uc = APUseCases(session)
        dpo = uc.get_dpo(period)
        return jsonify(dpo)
    finally:
        session.close()


# ── FCT (Foreign Contractor Tax) ────────────────────────────────

@ap_bp.route("/fct/calculate", methods=["POST"])
def calculate_fct():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = APUseCases(session)
        declaration = uc.calculate_fct(invoice_id=data["invoice_id"])
        if not declaration:
            return jsonify({"error": "Invoice not found"}), 404
        result = uc.save_fct_declaration(declaration)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_fct(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/fct/<int:fct_id>/remit", methods=["POST"])
def remit_fct(fct_id):
    session = _get_session()
    try:
        uc = APUseCases(session)
        result = uc.remit_fct(fct_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ap_bp.route("/fct/declarations", methods=["GET"])
def get_fct_declarations():
    period = request.args.get("period", date.today().strftime("%Y-%m"))
    session = _get_session()
    try:
        uc = APUseCases(session)
        declarations = uc.get_fct_declarations(period)
        return jsonify({"period": period, "declarations": [_json_fct(d) for d in declarations]})
    finally:
        session.close()
