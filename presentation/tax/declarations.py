from flask import request, jsonify
from presentation import resolve_error
from presentation.tax import tax_bp, _get_session, _json_declaration, _json_line
from use_cases.tax import TaxUseCases
from domain import TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus
from datetime import date
from decimal import Decimal


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
