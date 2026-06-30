from typing import Optional
from decimal import Decimal
from flask import Blueprint, current_app

payroll_bp = Blueprint("payroll", __name__, url_prefix="/api/v1/payroll")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_employee(e) -> dict:
    return {
        "id": e.id,
        "employee_code": e.employee_code,
        "full_name": e.full_name,
        "date_of_birth": e.date_of_birth.isoformat() if e.date_of_birth else None,
        "gender": e.gender,
        "id_number": e.id_number,
        "id_issue_date": e.id_issue_date.isoformat() if e.id_issue_date else None,
        "id_issue_place": e.id_issue_place,
        "tax_code": e.tax_code,
        "si_book_number": e.si_book_number,
        "bank_account": e.bank_account,
        "bank_name": e.bank_name,
        "department_id": e.department_id,
        "department_name": e.department_name,
        "position": e.position,
        "region": e.region.value,
        "dependent_count": e.dependent_count,
        "status": e.status.value,
        "start_date": e.start_date.isoformat(),
        "termination_date": e.termination_date.isoformat() if e.termination_date else None,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        "created_by": e.created_by,
        "updated_by": e.updated_by,
    }


def _json_contract(c) -> dict:
    return {
        "id": c.id,
        "employee_id": c.employee_id,
        "contract_type": c.contract_type.value,
        "start_date": c.start_date.isoformat(),
        "end_date": c.end_date.isoformat() if c.end_date else None,
        "base_salary": str(c.base_salary),
        "position_allowance": str(c.position_allowance),
        "meal_allowance": str(c.meal_allowance),
        "phone_allowance": str(c.phone_allowance),
        "transport_allowance": str(c.transport_allowance),
        "housing_allowance": str(c.housing_allowance),
        "responsibility_allowance": str(c.responsibility_allowance),
        "other_allowance": str(c.other_allowance),
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_dependent(d) -> dict:
    return {
        "id": d.id,
        "employee_id": d.employee_id,
        "full_name": d.full_name,
        "relationship": d.relationship,
        "date_of_birth": d.date_of_birth.isoformat() if d.date_of_birth else None,
        "tax_code": d.tax_code,
        "from_date": d.from_date.isoformat(),
        "to_date": d.to_date.isoformat() if d.to_date else None,
        "is_active": d.is_active,
    }


def _json_timesheet(t) -> dict:
    return {
        "id": t.id,
        "employee_id": t.employee_id,
        "period_month": t.period_month,
        "period_year": t.period_year,
        "working_days": str(t.working_days),
        "standard_days": str(t.standard_days),
        "overtime_weekday_hours": str(t.overtime_weekday_hours),
        "overtime_weekend_hours": str(t.overtime_weekend_hours),
        "overtime_holiday_hours": str(t.overtime_holiday_hours),
        "sick_leave_days": str(t.sick_leave_days),
        "unpaid_leave_days": str(t.unpaid_leave_days),
        "paid_leave_days": str(t.paid_leave_days),
        "notes": t.notes,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _json_payroll_line(l) -> dict:
    return {
        "id": l.id,
        "payroll_run_id": l.payroll_run_id,
        "employee_id": l.employee_id,
        "employee_code": l.employee_code,
        "employee_name": l.employee_name,
        "base_salary": str(l.base_salary),
        "working_days": str(l.working_days),
        "standard_days": str(l.standard_days),
        "prorated_salary": str(l.prorated_salary),
        "overtime_amount": str(l.overtime_amount),
        "allowances_total": str(l.allowances_total),
        "bonus_amount": str(l.bonus_amount),
        "gross_salary": str(l.gross_salary),
        "si_base_salary": str(l.si_base_salary),
        "employee_si": str(l.employee_si),
        "employee_hi": str(l.employee_hi),
        "employee_ui": str(l.employee_ui),
        "advance_deduction": str(l.advance_deduction),
        "other_deductions": str(l.other_deductions),
        "exempt_income": str(l.exempt_income),
        "personal_relief": str(l.personal_relief),
        "dependent_relief": str(l.dependent_relief),
        "additional_deductions": str(l.additional_deductions),
        "taxable_income": str(l.taxable_income),
        "pit_amount": str(l.pit_amount),
        "net_pay": str(l.net_pay),
        "employer_si": str(l.employer_si),
        "employer_hi": str(l.employer_hi),
        "employer_ui": str(l.employer_ui),
        "employer_occ": str(l.employer_occ),
        "kpcd": str(l.kpcd),
        "payment_method": l.payment_method.value,
        "payment_status": l.payment_status.value,
        "payment_date": l.payment_date.isoformat() if l.payment_date else None,
        "bank_transaction_ref": l.bank_transaction_ref,
        "notes": l.notes,
    }


def _json_payroll_run(r) -> dict:
    return {
        "id": r.id,
        "period_month": r.period_month,
        "period_year": r.period_year,
        "status": r.status.value,
        "lines": [_json_payroll_line(l) for l in r.lines] if r.lines else [],
        "total_gross": str(r.total_gross),
        "total_employee_si": str(r.total_employee_si),
        "total_employee_hi": str(r.total_employee_hi),
        "total_employee_ui": str(r.total_employee_ui),
        "total_pit": str(r.total_pit),
        "total_advances": str(r.total_advances),
        "total_other_deductions": str(r.total_other_deductions),
        "total_net": str(r.total_net),
        "total_employer_si": str(r.total_employer_si),
        "total_employer_hi": str(r.total_employer_hi),
        "total_employer_ui": str(r.total_employer_ui),
        "total_employer_occ": str(r.total_employer_occ),
        "total_kpcd": str(r.total_kpcd),
        "computed_at": r.computed_at.isoformat() if r.computed_at else None,
        "approved_at": r.approved_at.isoformat() if r.approved_at else None,
        "approved_by": r.approved_by,
        "paid_at": r.paid_at.isoformat() if r.paid_at else None,
        "notes": r.notes,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "created_by": r.created_by,
    }


def _json_adjustment(a) -> dict:
    return {
        "id": a.id,
        "payroll_run_id": a.payroll_run_id,
        "employee_id": a.employee_id,
        "adjustment_type": a.adjustment_type.value,
        "amount": str(a.amount),
        "delta_gross": str(a.delta_gross),
        "delta_si_base": str(a.delta_si_base),
        "delta_pit": str(a.delta_pit),
        "delta_net": str(a.delta_net),
        "reason": a.reason,
        "approved_by": a.approved_by,
        "approved_at": a.approved_at.isoformat() if a.approved_at else None,
        "status": a.status.value,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "created_by": a.created_by,
    }


def _json_pit_declaration(d) -> dict:
    return {
        "id": d.id,
        "declaration_type": d.declaration_type.value,
        "period_month": d.period_month,
        "period_quarter": d.period_quarter,
        "period_year": d.period_year,
        "submission_type": d.submission_type,
        "status": d.status.value,
        "total_income": str(d.total_income),
        "total_exempt_income": str(d.total_exempt_income),
        "total_deductions": str(d.total_deductions),
        "total_personal_relief": str(d.total_personal_relief),
        "total_dependent_relief": str(d.total_dependent_relief),
        "total_taxable_income": str(d.total_taxable_income),
        "total_pit": str(d.total_pit),
        "total_pit_withheld": str(d.total_pit_withheld),
        "total_pit_paid": str(d.total_pit_paid),
        "submission_date": d.submission_date.isoformat() if d.submission_date else None,
        "tax_authority_response": d.tax_authority_response,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        "created_by": d.created_by,
    }


def _json_si_record(r) -> dict:
    return {
        "id": r.id,
        "payroll_run_id": r.payroll_run_id,
        "period_month": r.period_month,
        "period_year": r.period_year,
        "status": r.status.value,
        "total_si_base": str(r.total_si_base),
        "total_employee_si": str(r.total_employee_si),
        "total_employee_hi": str(r.total_employee_hi),
        "total_employee_ui": str(r.total_employee_ui),
        "total_employer_si": str(r.total_employer_si),
        "total_employer_hi": str(r.total_employer_hi),
        "total_employer_ui": str(r.total_employer_ui),
        "total_employer_occ": str(r.total_employer_occ),
        "total_kpcd": str(r.total_kpcd),
        "total_payable": str(r.total_payable),
        "submission_date": r.submission_date.isoformat() if r.submission_date else None,
        "confirmation_ref": r.confirmation_ref,
        "payment_date": r.payment_date.isoformat() if r.payment_date else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "created_by": r.created_by,
    }


def _json_salary_payment(p) -> dict:
    return {
        "id": p.id,
        "payroll_run_id": p.payroll_run_id,
        "payment_date": p.payment_date.isoformat(),
        "payment_method": p.payment_method.value,
        "total_amount": str(p.total_amount),
        "bank_transaction_ref": p.bank_transaction_ref,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "created_by": p.created_by,
    }


def _json_cost_allocation(ca) -> dict:
    return {
        "id": ca.id,
        "payroll_run_id": ca.payroll_run_id,
        "cost_center": ca.cost_center.value,
        "total_salary_cost": str(ca.total_salary_cost),
        "total_employer_cost": str(ca.total_employer_cost),
        "total_cost": str(ca.total_cost),
        "gl_journal_entry_ref": ca.gl_journal_entry_ref,
        "created_at": ca.created_at.isoformat() if ca.created_at else None,
    }


from . import routes  # noqa: E402
