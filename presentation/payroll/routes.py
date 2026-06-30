from datetime import date, datetime
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.payroll import (
    payroll_bp, _get_session,
    _json_employee, _json_contract, _json_dependent, _json_timesheet,
    _json_payroll_run, _json_payroll_line, _json_adjustment,
    _json_pit_declaration, _json_si_record, _json_salary_payment,
    _json_cost_allocation,
)
from use_cases.payroll import PayrollUseCases
from domain import (
    Employee, EmployeeContract, EmployeeDependent, Timesheet, PayrollLine,
    PayrollAdjustment, PayrollRun,
    EmployeeStatus, ContractType, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, DeclarationType, DeclarationStatus, AdjustmentType,
    Region,
)


# ── Employee ──────────────────────────────────────────────────────────

@payroll_bp.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        emp = Employee(
            employee_code=data["employee_code"],
            full_name=data["full_name"],
            date_of_birth=date.fromisoformat(data["date_of_birth"]) if data.get("date_of_birth") else None,
            gender=data.get("gender"),
            id_number=data.get("id_number"),
            id_issue_date=date.fromisoformat(data["id_issue_date"]) if data.get("id_issue_date") else None,
            id_issue_place=data.get("id_issue_place"),
            tax_code=data.get("tax_code"),
            si_book_number=data.get("si_book_number"),
            bank_account=data.get("bank_account"),
            bank_name=data.get("bank_name"),
            department_id=data.get("department_id"),
            department_name=data.get("department_name"),
            position=data.get("position"),
            region=Region(data.get("region", "region_1")),
            dependent_count=data.get("dependent_count", 0),
            status=EmployeeStatus(data.get("status", "active")),
            start_date=date.fromisoformat(data["start_date"]),
            termination_date=date.fromisoformat(data["termination_date"]) if data.get("termination_date") else None,
            created_by=data.get("created_by"),
        )
        result = uc.create_employee(emp)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_employee(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/employees", methods=["GET"])
def list_employees():
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        filters = {}
        status = request.args.get("status")
        if status:
            filters["status"] = status
        dept = request.args.get("department_id")
        if dept:
            filters["department_id"] = int(dept)
        search = request.args.get("search")
        if search:
            filters["search"] = search
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        result = uc.list_employees(filters=filters, page=page, per_page=per_page)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        data = result.get_data()
        return jsonify({
            "employees": [_json_employee(e) for e in data["items"]],
            "total": data["total"],
            "page": data["page"],
            "per_page": data["per_page"],
            "pages": data["pages"],
        })
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_employee(employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_employee(result.get_data()))
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_employee(employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        emp = result.get_data()
        for field in ("full_name", "employee_code", "gender", "id_number", "id_issue_place",
                      "tax_code", "si_book_number", "bank_account", "bank_name",
                      "department_name", "position"):
            if field in data:
                setattr(emp, field, data[field])
        if "date_of_birth" in data:
            emp.date_of_birth = date.fromisoformat(data["date_of_birth"])
        if "id_issue_date" in data:
            emp.id_issue_date = date.fromisoformat(data["id_issue_date"])
        if "start_date" in data:
            emp.start_date = date.fromisoformat(data["start_date"])
        if "termination_date" in data:
            emp.termination_date = date.fromisoformat(data["termination_date"]) if data["termination_date"] else None
        if "department_id" in data:
            emp.department_id = data["department_id"]
        if "dependent_count" in data:
            emp.dependent_count = data["dependent_count"]
        if "region" in data:
            emp.region = Region(data["region"])
        if "status" in data:
            emp.status = EmployeeStatus(data["status"])
        if "updated_by" in data:
            emp.updated_by = data["updated_by"]
        result = uc.update_employee(emp)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_employee(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>", methods=["DELETE"])
def terminate_employee(employee_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        termination_date = date.fromisoformat(data["termination_date"]) if data.get("termination_date") else date.today()
        result = uc.terminate_employee(employee_id, termination_date, reason=data.get("reason"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Employee terminated"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Contracts ─────────────────────────────────────────────────────────

@payroll_bp.route("/employees/<int:employee_id>/contracts", methods=["POST"])
def create_contract(employee_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        contract = EmployeeContract(
            employee_id=employee_id,
            contract_type=ContractType(data["contract_type"]),
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            base_salary=Decimal(str(data.get("base_salary", "0"))),
            position_allowance=Decimal(str(data.get("position_allowance", "0"))),
            meal_allowance=Decimal(str(data.get("meal_allowance", "0"))),
            phone_allowance=Decimal(str(data.get("phone_allowance", "0"))),
            transport_allowance=Decimal(str(data.get("transport_allowance", "0"))),
            housing_allowance=Decimal(str(data.get("housing_allowance", "0"))),
            responsibility_allowance=Decimal(str(data.get("responsibility_allowance", "0"))),
            other_allowance=Decimal(str(data.get("other_allowance", "0"))),
            is_active=data.get("is_active", True),
        )
        result = uc.create_contract(contract)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_contract(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>/contracts", methods=["GET"])
def list_contracts(employee_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.list_employee_contracts(employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        contracts = result.get_data()
        return jsonify({"contracts": [_json_contract(c) for c in contracts], "total": len(contracts)})
    finally:
        session.close()


@payroll_bp.route("/contracts/<int:contract_id>", methods=["GET"])
def get_contract(contract_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.repo.get_contract(contract_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_contract(result.get_data()))
    finally:
        session.close()


@payroll_bp.route("/contracts/<int:contract_id>", methods=["PUT"])
def update_contract(contract_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.repo.get_contract(contract_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        c = result.get_data()
        for field in ("base_salary", "position_allowance", "meal_allowance", "phone_allowance",
                      "transport_allowance", "housing_allowance", "responsibility_allowance",
                      "other_allowance"):
            if field in data:
                setattr(c, field, Decimal(str(data[field])))
        if "contract_type" in data:
            c.contract_type = ContractType(data["contract_type"])
        if "start_date" in data:
            c.start_date = date.fromisoformat(data["start_date"])
        if "end_date" in data:
            c.end_date = date.fromisoformat(data["end_date"]) if data["end_date"] else None
        if "is_active" in data:
            c.is_active = data["is_active"]
        result = uc.update_contract(c)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_contract(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Dependents ────────────────────────────────────────────────────────

@payroll_bp.route("/employees/<int:employee_id>/dependents", methods=["GET"])
def list_dependents(employee_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.repo.list_employee_dependents(employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        dependents = result.get_data()
        return jsonify({"dependents": [_json_dependent(d) for d in dependents], "total": len(dependents)})
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>/dependents", methods=["POST"])
def create_dependent(employee_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        dep = EmployeeDependent(
            employee_id=employee_id,
            full_name=data["full_name"],
            relationship=data["relationship"],
            date_of_birth=date.fromisoformat(data["date_of_birth"]) if data.get("date_of_birth") else None,
            tax_code=data.get("tax_code"),
            from_date=date.fromisoformat(data["from_date"]),
            to_date=date.fromisoformat(data["to_date"]) if data.get("to_date") else None,
            is_active=data.get("is_active", True),
        )
        result = uc.repo.create_dependent(dep)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_dependent(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Timesheets ────────────────────────────────────────────────────────

@payroll_bp.route("/timesheets", methods=["POST"])
def upsert_timesheet():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        ts = Timesheet(
            employee_id=data["employee_id"],
            period_month=int(data.get("period_month", 1)),
            period_year=int(data.get("period_year", date.today().year)),
            working_days=Decimal(str(data.get("working_days", "0"))),
            standard_days=Decimal(str(data.get("standard_days", "26"))),
            overtime_weekday_hours=Decimal(str(data.get("overtime_weekday_hours", "0"))),
            overtime_weekend_hours=Decimal(str(data.get("overtime_weekend_hours", "0"))),
            overtime_holiday_hours=Decimal(str(data.get("overtime_holiday_hours", "0"))),
            sick_leave_days=Decimal(str(data.get("sick_leave_days", "0"))),
            unpaid_leave_days=Decimal(str(data.get("unpaid_leave_days", "0"))),
            paid_leave_days=Decimal(str(data.get("paid_leave_days", "0"))),
            notes=data.get("notes"),
        )
        result = uc.upsert_timesheet(ts)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_timesheet(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/timesheets/batch", methods=["POST"])
def batch_upsert_timesheets():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({"error": "Array of timesheets required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        timesheets = []
        for item in data:
            timesheets.append(Timesheet(
                employee_id=item["employee_id"],
                period_month=int(item.get("period_month", 1)),
                period_year=int(item.get("period_year", date.today().year)),
                working_days=Decimal(str(item.get("working_days", "0"))),
                standard_days=Decimal(str(item.get("standard_days", "26"))),
                overtime_weekday_hours=Decimal(str(item.get("overtime_weekday_hours", "0"))),
                overtime_weekend_hours=Decimal(str(item.get("overtime_weekend_hours", "0"))),
                overtime_holiday_hours=Decimal(str(item.get("overtime_holiday_hours", "0"))),
                sick_leave_days=Decimal(str(item.get("sick_leave_days", "0"))),
                unpaid_leave_days=Decimal(str(item.get("unpaid_leave_days", "0"))),
                paid_leave_days=Decimal(str(item.get("paid_leave_days", "0"))),
                notes=item.get("notes"),
            ))
        result = uc.batch_upsert_timesheets(timesheets)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"timesheets": [_json_timesheet(t) for t in result.get_data()], "count": len(result.get_data())}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/timesheets", methods=["GET"])
def list_timesheets():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"error": "month and year query params required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.list_period_timesheets(month, year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        sheets = result.get_data()
        return jsonify({"timesheets": [_json_timesheet(t) for t in sheets], "total": len(sheets)})
    finally:
        session.close()


@payroll_bp.route("/employees/<int:employee_id>/timesheet", methods=["GET"])
def get_employee_timesheet(employee_id):
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"error": "month and year query params required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_employee_timesheet(employee_id, month, year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_timesheet(result.get_data()))
    finally:
        session.close()


# ── Payroll Runs ──────────────────────────────────────────────────────

@payroll_bp.route("/runs/compute", methods=["POST"])
def compute_payroll():
    data = request.get_json() or {}
    month = data.get("month")
    year = data.get("year")
    if not month or not year:
        return jsonify({"error": "month and year required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.compute_payroll(int(month), int(year), created_by=data.get("created_by"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        data_resp = result.get_data()
        if isinstance(data_resp, PayrollRun):
            session.commit()
            return jsonify(_json_payroll_run(data_resp)), 201
        session.commit()
        return jsonify(data_resp), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs", methods=["GET"])
def list_payroll_runs():
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        filters = {}
        status = request.args.get("status")
        if status:
            filters["status"] = status
        month = request.args.get("month", type=int)
        if month:
            filters["period_month"] = month
        year = request.args.get("year", type=int)
        if year:
            filters["period_year"] = year
        result = uc.list_payroll_runs(filters=filters)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        runs = result.get_data()
        return jsonify({"runs": [_json_payroll_run(r) for r in runs], "total": len(runs)})
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>", methods=["GET"])
def get_payroll_run(run_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_payroll_run(run_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_payroll_run(result.get_data()))
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/approve", methods=["POST"])
def approve_payroll_run(run_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.approve_payroll(run_id, approved_by=data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payroll_run(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/cancel", methods=["POST"])
def cancel_payroll_run(run_id):
    data = request.get_json() or {}
    reason = data.get("reason", "Cancelled")
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.cancel_payroll(run_id, reason)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payroll_run(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/pay", methods=["POST"])
def process_payment(run_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        payment_date = date.fromisoformat(data["payment_date"]) if data.get("payment_date") else date.today()
        result = uc.process_payment(
            run_id=run_id,
            payment_date=payment_date,
            payment_method=data.get("payment_method", "bank_transfer"),
            bank_transaction_ref=data.get("bank_transaction_ref"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_salary_payment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/post-gl", methods=["POST"])
def post_payroll_to_gl(run_id):
    data = request.get_json() or {}
    allocations = data.get("allocations", [])
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.post_payroll_to_gl(run_id, allocations)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/allocate", methods=["POST"])
def allocate_costs(run_id):
    data = request.get_json() or {}
    cost_allocations = data.get("cost_allocations", [])
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.allocate_payroll_costs(run_id, cost_allocations)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        data_resp = result.get_data()
        data_resp["allocations"] = [_json_cost_allocation(a) for a in data_resp.get("allocations", [])]
        return jsonify(data_resp)
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Adjustments ───────────────────────────────────────────────────────

@payroll_bp.route("/runs/<int:run_id>/adjustments", methods=["POST"])
def create_adjustment(run_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        adj = PayrollAdjustment(
            payroll_run_id=run_id,
            employee_id=data["employee_id"],
            adjustment_type=AdjustmentType(data["adjustment_type"]),
            amount=Decimal(str(data.get("amount", "0"))),
            delta_gross=Decimal(str(data.get("delta_gross", "0"))),
            delta_si_base=Decimal(str(data.get("delta_si_base", "0"))),
            delta_pit=Decimal(str(data.get("delta_pit", "0"))),
            delta_net=Decimal(str(data.get("delta_net", "0"))),
            reason=data["reason"],
            created_by=data.get("created_by"),
        )
        result = uc.create_adjustment(adj)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/runs/<int:run_id>/adjustments", methods=["GET"])
def list_adjustments(run_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.list_run_adjustments(run_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        adjustments = result.get_data()
        return jsonify({"adjustments": [_json_adjustment(a) for a in adjustments], "total": len(adjustments)})
    finally:
        session.close()


@payroll_bp.route("/adjustments/<int:adjustment_id>/approve", methods=["POST"])
def approve_adjustment(adjustment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.approve_adjustment(adjustment_id, approved_by=data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── PIT Declarations ──────────────────────────────────────────────────

@payroll_bp.route("/pit-declarations/generate", methods=["POST"])
def generate_pit_declaration():
    data = request.get_json() or {}
    month = data.get("month")
    year = data.get("year")
    if not month or not year:
        return jsonify({"error": "month and year required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.generate_pit_declaration(
            period_month=int(month),
            period_year=int(year),
            declaration_type=data.get("declaration_type", "monthly"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_pit_declaration(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/pit-declarations", methods=["GET"])
def list_pit_declarations():
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        filters = {}
        status = request.args.get("status")
        if status:
            filters["status"] = status
        year = request.args.get("year", type=int)
        if year:
            filters["period_year"] = year
        result = uc.list_pit_declarations(filters=filters)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        decls = result.get_data()
        return jsonify({"declarations": [_json_pit_declaration(d) for d in decls], "total": len(decls)})
    finally:
        session.close()


@payroll_bp.route("/pit-declarations/<int:declaration_id>", methods=["GET"])
def get_pit_declaration(declaration_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_pit_declaration(declaration_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_pit_declaration(result.get_data()))
    finally:
        session.close()


# ── SI Records ─────────────────────────────────────────────────────────

@payroll_bp.route("/si-records/generate", methods=["POST"])
def generate_si_record():
    data = request.get_json() or {}
    month = data.get("month")
    year = data.get("year")
    if not month or not year:
        return jsonify({"error": "month and year required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.generate_si_record(int(month), int(year))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_si_record(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@payroll_bp.route("/si-records/<int:record_id>", methods=["GET"])
def get_si_record(record_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_si_record(record_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_si_record(result.get_data()))
    finally:
        session.close()


@payroll_bp.route("/si-records/<int:record_id>/submit", methods=["POST"])
def submit_si_record(record_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.submit_si_record(record_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_si_record(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Payments ──────────────────────────────────────────────────────────

@payroll_bp.route("/runs/<int:run_id>/payments", methods=["GET"])
def list_run_payments(run_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_run_payments(run_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        payments = result.get_data()
        return jsonify({"payments": [_json_salary_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


# ── Bank File ─────────────────────────────────────────────────────────

@payroll_bp.route("/runs/<int:run_id>/bank-file", methods=["GET"])
def generate_bank_file(run_id):
    file_format = request.args.get("format", "csv")
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.generate_bank_transfer_file(run_id, file_format)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


# ── Payslip ───────────────────────────────────────────────────────────

@payroll_bp.route("/runs/<int:run_id>/payslip/<int:employee_id>", methods=["GET"])
def get_payslip(run_id, employee_id):
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_employee_payslip(run_id, employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        data_resp = result.get_data()
        for k in ("base_salary", "prorated_salary", "overtime_amount", "allowances_total",
                  "bonus_amount", "gross_salary", "employee_si", "employee_hi", "employee_ui",
                  "pit_amount", "advance_deduction", "other_deductions", "net_pay",
                  "employer_si", "employer_hi", "employer_ui", "employer_occ", "kpcd"):
            if k in data_resp:
                data_resp[k] = str(data_resp[k])
        return jsonify(data_resp)
    finally:
        session.close()


# ── Reports ───────────────────────────────────────────────────────────

@payroll_bp.route("/reports/summary", methods=["GET"])
def payroll_summary():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"error": "month and year query params required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_payroll_summary(month, year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        data_resp = result.get_data()
        for k in ("total_gross", "total_deductions", "total_net", "total_employer_cost", "total_pit"):
            if k in data_resp:
                if isinstance(data_resp[k], Decimal):
                    data_resp[k] = str(data_resp[k])
        return jsonify(data_resp)
    finally:
        session.close()


@payroll_bp.route("/reports/department-summary", methods=["GET"])
def department_summary():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"error": "month and year query params required"}), 400
    department_id = request.args.get("department_id", type=int)
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_department_summary(month, year, department_id=department_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        departments = result.get_data()
        for dept in departments:
            for k in ("total_gross", "total_net", "total_pit", "total_employer_cost"):
                if k in dept:
                    dept[k] = str(dept[k])
        return jsonify({"departments": departments})
    finally:
        session.close()


@payroll_bp.route("/reports/yearly-summary", methods=["GET"])
def yearly_summary():
    year = request.args.get("year", type=int)
    if not year:
        return jsonify({"error": "year query param required"}), 400
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        result = uc.get_yearly_summary(year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        data_resp = result.get_data()
        for month_data in data_resp.get("months", []):
            for k in ("total_gross", "total_net", "total_pit", "total_employer_cost"):
                if k in month_data:
                    month_data[k] = str(month_data[k])
        for k in ("year_total_gross", "year_total_net", "year_total_pit"):
            if k in data_resp:
                data_resp[k] = str(data_resp[k])
        return jsonify(data_resp)
    finally:
        session.close()


# ── Dashboard ─────────────────────────────────────────────────────────

@payroll_bp.route("/dashboard", methods=["GET"])
def dashboard():
    month = request.args.get("month", type=int) or date.today().month
    year = request.args.get("year", type=int) or date.today().year
    session = _get_session()
    try:
        uc = PayrollUseCases(session)
        data_resp = uc.get_dashboard(month, year)
        current = data_resp.get("current", {})
        for k in ("total_gross", "total_net", "total_employer_cost", "total_pit"):
            if k in current:
                current[k] = str(current[k])
        prev = data_resp.get("previous_period", {})
        for k in ("total_gross", "total_net"):
            if k in prev:
                prev[k] = str(prev[k])
        change = data_resp.get("change", {})
        if "gross_change_pct" in change:
            change["gross_change_pct"] = str(change["gross_change_pct"])
        return jsonify(data_resp)
    finally:
        session.close()
