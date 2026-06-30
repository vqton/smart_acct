from decimal import Decimal
from datetime import date, datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    Employee, EmployeeContract, Timesheet, PayrollRun, PayrollLine,
    PayrollAdjustment, PITDeclaration, SIInsuranceRecord, SalaryPayment,
    PayrollCostAllocation, PayrollCalculator,
    EmployeeStatus, ContractType, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, AdjustmentType, CostCenter, Region,
)
from domain.payroll import DeclarationType as PayrollDeclarationType, DeclarationStatus as PayrollDeclarationStatus
from domain.common import Result, ValidationError, VASValidationError
from infrastructure.models.coa_models import Base
import infrastructure.models.payroll_models  # noqa: register tables
from use_cases.payroll import PayrollUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def uc(session):
    return PayrollUseCases(session)


# ── Helpers ──────────────────────────────────────────────────────────────

def _create_employee(uc, code="EMP001", name="Nguyen Van A", **kw):
    emp = Employee(
        employee_code=code,
        full_name=name,
        start_date=kw.get("start_date", date(2026, 1, 1)),
        region=kw.get("region", Region.REGION_1),
        department_id=kw.get("department_id", 1),
        department_name=kw.get("department_name", "Engineering"),
        position=kw.get("position", "Developer"),
        dependent_count=kw.get("dependent_count", 1),
        status=kw.get("status", EmployeeStatus.ACTIVE),
        tax_code=kw.get("tax_code", "1234567890"),
    )
    return uc.create_employee(emp)


def _create_contract(uc, employee_id, salary=Decimal("20000000"), **kw):
    contract = EmployeeContract(
        employee_id=employee_id,
        contract_type=kw.get("contract_type", ContractType.INDEFINITE),
        start_date=kw.get("start_date", date(2026, 1, 1)),
        base_salary=salary,
        position_allowance=kw.get("position_allowance", Decimal("0")),
        meal_allowance=kw.get("meal_allowance", Decimal("0")),
        phone_allowance=kw.get("phone_allowance", Decimal("0")),
        transport_allowance=kw.get("transport_allowance", Decimal("0")),
        housing_allowance=kw.get("housing_allowance", Decimal("0")),
        responsibility_allowance=kw.get("responsibility_allowance", Decimal("0")),
        other_allowance=kw.get("other_allowance", Decimal("0")),
        is_active=kw.get("is_active", True),
    )
    return uc.create_contract(contract)


def _create_timesheet(uc, employee_id, month=6, year=2026, working_days=26, **kw):
    ts = Timesheet(
        employee_id=employee_id,
        period_month=month,
        period_year=year,
        working_days=Decimal(str(working_days)),
        standard_days=kw.get("standard_days", Decimal("26")),
        overtime_weekday_hours=kw.get("overtime_weekday_hours", Decimal("0")),
        overtime_weekend_hours=kw.get("overtime_weekend_hours", Decimal("0")),
        overtime_holiday_hours=kw.get("overtime_holiday_hours", Decimal("0")),
        sick_leave_days=kw.get("sick_leave_days", Decimal("0")),
        unpaid_leave_days=kw.get("unpaid_leave_days", Decimal("0")),
        paid_leave_days=kw.get("paid_leave_days", Decimal("0")),
    )
    return uc.upsert_timesheet(ts)


def _create_full_employee(uc, code="EMP001", name="Nguyen Van A", salary=Decimal("20000000"), **kw):
    r = _create_employee(uc, code=code, name=name, **kw)
    assert r.is_success(), f"Failed to create employee: {r.get_error()}"
    emp = r.get_data()
    r2 = _create_contract(uc, emp.id, salary=salary, **{k: v for k, v in kw.items() if k in (
        "contract_type", "start_date", "position_allowance", "meal_allowance",
        "phone_allowance", "transport_allowance", "housing_allowance",
        "responsibility_allowance", "other_allowance",
    )})
    assert r2.is_success(), f"Failed to create contract: {r2.get_error()}"
    contract = r2.get_data()
    ts_kw = {k: v for k, v in kw.items() if k in (
        "working_days", "standard_days", "overtime_weekday_hours",
        "overtime_weekend_hours", "overtime_holiday_hours",
    )}
    if "working_days" not in ts_kw:
        ts_kw["working_days"] = 26
    r3 = _create_timesheet(uc, emp.id, **{**ts_kw, **{k: kw[k] for k in ("month", "year") if k in kw}})
    assert r3.is_success(), f"Failed to create timesheet"
    ts = r3.get_data()
    return emp, contract, ts


# ═══════════════════════════════════════════════════════════════════════
# Group 1: Employee CRUD (UC-PR-01)
# ═══════════════════════════════════════════════════════════════════════

class TestEmployeeCRUD:
    def test_create_employee(self, uc):
        r = _create_employee(uc)
        assert r.is_success()
        emp = r.get_data()
        assert emp.employee_code == "EMP001"
        assert emp.full_name == "Nguyen Van A"
        assert emp.status == EmployeeStatus.ACTIVE
        assert emp.id is not None

    def test_create_employee_duplicate_code(self, uc):
        r1 = _create_employee(uc, code="EMP001")
        assert r1.is_success()
        r2 = _create_employee(uc, code="EMP001")
        assert r2.is_failure()

    def test_get_employee(self, uc):
        r = _create_employee(uc)
        assert r.is_success()
        emp = r.get_data()
        r2 = uc.get_employee(emp.id)
        assert r2.is_success()
        assert r2.get_data().employee_code == "EMP001"

    def test_get_employee_by_code(self, uc):
        r = _create_employee(uc, code="EMP002")
        assert r.is_success()
        emp = uc.repo.get_employee_by_code("EMP002")
        assert emp.is_success()
        assert emp.get_data().full_name == "Nguyen Van A"

    def test_update_employee(self, uc):
        r = _create_employee(uc)
        assert r.is_success()
        emp = r.get_data()
        emp.full_name = "Tran Van B"
        emp.department_name = "Finance"
        r2 = uc.update_employee(emp)
        assert r2.is_success()
        updated = r2.get_data()
        assert updated.full_name == "Tran Van B"
        assert updated.department_name == "Finance"

    def test_list_employees(self, uc):
        _create_employee(uc, code="EMP001")
        _create_employee(uc, code="EMP002", name="Employee Two")
        r = uc.list_employees()
        assert r.is_success()
        data = r.get_data()
        assert isinstance(data, dict)
        assert data["total"] >= 2

    def test_list_employees_filter_by_status(self, uc):
        _create_employee(uc, code="ACTIVE1")
        _create_employee(uc, code="ACTIVE2")
        r = uc.list_employees(filters={"status": EmployeeStatus.ACTIVE.value})
        assert r.is_success()
        data = r.get_data()
        assert data["total"] >= 2

    def test_search_employees(self, uc):
        _create_employee(uc, code="EMP001", name="Nguyen Van A")
        _create_employee(uc, code="EMP002", name="Tran Van B")
        r = uc.list_employees(filters={"search": "Nguyen"})
        assert r.is_success()
        data = r.get_data()
        assert data["total"] >= 1

    def test_terminate_employee(self, uc):
        r = _create_employee(uc)
        assert r.is_success()
        emp = r.get_data()
        term_date = date(2026, 6, 30)
        r2 = uc.terminate_employee(emp.id, term_date, reason="Resigned")
        assert r2.is_success()
        r3 = uc.get_employee(emp.id)
        assert r3.is_success()
        terminated = r3.get_data()
        assert terminated.status == EmployeeStatus.TERMINATED
        assert terminated.termination_date == term_date


# ═══════════════════════════════════════════════════════════════════════
# Group 2: Contract CRUD (UC-PR-02)
# ═══════════════════════════════════════════════════════════════════════

class TestContractCRUD:
    def test_create_contract(self, uc):
        r = _create_employee(uc)
        assert r.is_success()
        emp = r.get_data()
        r2 = _create_contract(uc, emp.id)
        assert r2.is_success()
        c = r2.get_data()
        assert c.employee_id == emp.id
        assert c.base_salary == Decimal("20000000.00")
        assert c.is_active is True

    def test_get_active_contract(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        _create_contract(uc, emp.id)
        r2 = uc.get_active_contract(emp.id)
        assert r2.is_success()
        assert r2.get_data().employee_id == emp.id

    def test_list_employee_contracts(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        _create_contract(uc, emp.id)
        r2 = uc.list_employee_contracts(emp.id)
        assert r2.is_success()
        assert len(r2.get_data()) == 1

    def test_terminate_contract(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        r2 = _create_contract(uc, emp.id)
        c = r2.get_data()
        c.is_active = False
        r3 = uc.update_contract(c)
        assert r3.is_success()
        r4 = uc.get_active_contract(emp.id)
        assert r4.is_failure()


# ═══════════════════════════════════════════════════════════════════════
# Group 3: Timesheet CRUD (UC-PR-03)
# ═══════════════════════════════════════════════════════════════════════

class TestTimesheetCRUD:
    def test_upsert_timesheet(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        r2 = _create_timesheet(uc, emp.id)
        assert r2.is_success()
        ts = r2.get_data()
        assert ts.employee_id == emp.id
        assert ts.working_days == Decimal("26")
        assert ts.period_month == 6

    def test_upsert_timesheet_update(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        _create_timesheet(uc, emp.id, working_days=20)
        r2 = _create_timesheet(uc, emp.id, working_days=25)
        assert r2.is_success()
        assert r2.get_data().working_days == Decimal("25")

    def test_get_employee_timesheet(self, uc):
        r = _create_employee(uc)
        emp = r.get_data()
        _create_timesheet(uc, emp.id, month=6, year=2026)
        r2 = uc.get_employee_timesheet(emp.id, 6, 2026)
        assert r2.is_success()
        assert r2.get_data().period_month == 6

    def test_list_period_timesheets(self, uc):
        r1 = _create_employee(uc, code="EMP01")
        e1 = r1.get_data()
        r2 = _create_employee(uc, code="EMP02", name="Employee Two")
        e2 = r2.get_data()
        _create_timesheet(uc, e1.id, month=6, year=2026)
        _create_timesheet(uc, e2.id, month=6, year=2026)
        r3 = uc.list_period_timesheets(6, 2026)
        assert r3.is_success()
        assert len(r3.get_data()) == 2

    def test_batch_upsert_timesheets(self, uc):
        r1 = _create_employee(uc, code="EMP01")
        e1 = r1.get_data()
        r2 = _create_employee(uc, code="EMP02")
        e2 = r2.get_data()
        ts1 = Timesheet(employee_id=e1.id, period_month=6, period_year=2026, working_days=Decimal("26"))
        ts2 = Timesheet(employee_id=e2.id, period_month=6, period_year=2026, working_days=Decimal("22"))
        r3 = uc.batch_upsert_timesheets([ts1, ts2])
        assert r3.is_success()
        assert len(r3.get_data()) == 2


# ═══════════════════════════════════════════════════════════════════════
# Group 4: Payroll Computation (UC-PR-04)
# ═══════════════════════════════════════════════════════════════════════

class TestPayrollComputation:
    def test_compute_payroll(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026, created_by="admin")
        assert r.is_success()
        run = r.get_data()
        assert run.id is not None
        assert run.period_month == 6
        assert run.period_year == 2026
        assert run.status == PayrollRunStatus.COMPUTED
        assert len(run.lines) == 1
        line = run.lines[0]
        assert line.gross_salary == Decimal("20000000.00")
        assert line.employee_si == Decimal("1600000.00")
        assert line.employee_hi == Decimal("300000.00")
        assert line.employee_ui == Decimal("200000.00")
        assert line.personal_relief == Decimal("15500000.00")
        assert line.dependent_relief == Decimal("6200000.00")
        assert line.taxable_income == Decimal("0.00")
        assert line.pit_amount == Decimal("0.00")
        expected_net = (Decimal("20000000") - Decimal("1600000") - Decimal("300000") - Decimal("200000")).quantize(Decimal("0.01"))
        assert line.net_pay == expected_net
        assert run.total_gross == Decimal("20000000.00")
        assert run.total_net == expected_net

    def test_compute_payroll_duplicate_period(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        r2 = uc.compute_payroll(6, 2026)
        assert r2.is_failure()

    def test_compute_payroll_no_timesheet(self, uc):
        r = _create_employee(uc, code="EMP001")
        assert r.is_success()
        emp = r.get_data()
        _create_contract(uc, emp.id)
        r2 = uc.compute_payroll(6, 2026)
        assert r2.is_success()
        run = r2.get_data()
        assert len(run.lines) == 1
        assert run.lines[0].working_days == Decimal("0")

    def test_compute_payroll_partial_month(self, uc):
        _create_full_employee(uc, code="EMP001", salary=Decimal("20000000"), working_days=15)
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        line = run.lines[0]
        expected_prorated = (Decimal("20000000") * Decimal("15") / Decimal("26")).quantize(Decimal("0.01"))
        assert line.prorated_salary == expected_prorated
        assert line.working_days == Decimal("15")
        assert line.prorated_salary < Decimal("20000000")

    def test_compute_payroll_with_allowances(self, uc):
        r = _create_employee(uc, code="EMP001")
        emp = r.get_data()
        _create_contract(uc, emp.id, salary=Decimal("15000000"),
                         meal_allowance=Decimal("500000"),
                         phone_allowance=Decimal("200000"))
        _create_timesheet(uc, emp.id)
        r2 = uc.compute_payroll(6, 2026)
        assert r2.is_success()
        run = r2.get_data()
        line = run.lines[0]
        assert line.allowances_total == Decimal("700000.00")
        assert line.gross_salary == Decimal("15000000.00") + Decimal("700000.00")


# ═══════════════════════════════════════════════════════════════════════
# Group 5: Payroll Approval (UC-PR-05)
# ═══════════════════════════════════════════════════════════════════════

class TestPayrollApproval:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_approve_payroll(self, uc):
        run = self._setup_computed_run(uc)
        r = uc.approve_payroll(run.id, "manager")
        assert r.is_success()
        r2 = uc.get_payroll_run(run.id)
        assert r2.is_success()
        assert r2.get_data().status == PayrollRunStatus.APPROVED
        assert r2.get_data().approved_by == "manager"

    def test_approve_draft_run_fails(self, uc):
        r = _create_employee(uc, code="EMP001")
        emp = r.get_data()
        _create_contract(uc, emp.id)
        run = PayrollRun(period_month=6, period_year=2026, status=PayrollRunStatus.DRAFT)
        saved = uc.repo.create_run(run)
        assert saved.is_success()
        r2 = uc.approve_payroll(saved.get_data().id, "manager")
        assert r2.is_failure()

    def test_approve_already_approved_fails(self, uc):
        run = self._setup_computed_run(uc)
        r = uc.approve_payroll(run.id, "manager")
        assert r.is_success()
        r2 = uc.approve_payroll(run.id, "manager2")
        assert r2.is_failure()

    def test_cancel_payroll(self, uc):
        run = self._setup_computed_run(uc)
        r = uc.cancel_payroll(run.id, "Need to adjust")
        assert r.is_success()
        r2 = uc.get_payroll_run(run.id)
        assert r2.is_success()
        assert r2.get_data().status == PayrollRunStatus.CANCELLED


# ═══════════════════════════════════════════════════════════════════════
# Group 6: Salary Payment (UC-PR-06)
# ═══════════════════════════════════════════════════════════════════════

class TestSalaryPayment:
    def _setup_approved_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        r2 = uc.approve_payroll(run.id, "manager")
        assert r2.is_success()
        return uc.get_payroll_run(run.id).get_data()

    def test_process_payment(self, uc):
        run = self._setup_approved_run(uc)
        r = uc.process_payment(run.id, date(2026, 7, 5), "bank_transfer",
                               bank_transaction_ref="BANK123", created_by="admin")
        assert r.is_success()
        r2 = uc.get_payroll_run(run.id)
        assert r2.is_success()
        assert r2.get_data().status == PayrollRunStatus.PAID

    def test_payment_updates_line_status(self, uc):
        run = self._setup_approved_run(uc)
        r = uc.process_payment(run.id, date(2026, 7, 5), "bank_transfer")
        assert r.is_success()
        r2 = uc.repo.get_payroll_run(run.id)
        assert r2.is_success()
        for line in r2.get_data().lines:
            assert line.payment_status == PaymentStatus.PAID

    def test_payment_unapproved_run_fails(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        r2 = uc.process_payment(run.id, date(2026, 7, 5), "bank_transfer")
        assert r2.is_failure()

    def test_get_run_payments(self, uc):
        run = self._setup_approved_run(uc)
        uc.process_payment(run.id, date(2026, 7, 5), "bank_transfer")
        r = uc.get_run_payments(run.id)
        assert r.is_success()
        assert len(r.get_data()) >= 1


# ═══════════════════════════════════════════════════════════════════════
# Group 7: Payroll Adjustments (UC-PR-07)
# ═══════════════════════════════════════════════════════════════════════

class TestPayrollAdjustments:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_create_adjustment(self, uc):
        run = self._setup_computed_run(uc)
        emp_id = run.lines[0].employee_id
        adj = PayrollAdjustment(
            payroll_run_id=run.id,
            employee_id=emp_id,
            adjustment_type=AdjustmentType.ONE_OFF_BONUS,
            amount=Decimal("1000000"),
            delta_gross=Decimal("1000000"),
            delta_net=Decimal("900000"),
            reason="Performance bonus",
        )
        r = uc.create_adjustment(adj)
        assert r.is_success()
        assert r.get_data().id is not None

    def test_approve_adjustment(self, uc):
        run = self._setup_computed_run(uc)
        emp_id = run.lines[0].employee_id
        adj = PayrollAdjustment(
            payroll_run_id=run.id,
            employee_id=emp_id,
            adjustment_type=AdjustmentType.CORRECTION,
            amount=Decimal("500000"),
            delta_gross=Decimal("500000"),
            reason="Salary correction",
        )
        r = uc.create_adjustment(adj)
        assert r.is_success()
        adj_id = r.get_data().id
        r2 = uc.approve_adjustment(adj_id, "manager")
        assert r2.is_success()

    def test_list_run_adjustments(self, uc):
        run = self._setup_computed_run(uc)
        emp_id = run.lines[0].employee_id
        adj = PayrollAdjustment(
            payroll_run_id=run.id, employee_id=emp_id,
            adjustment_type=AdjustmentType.ONE_OFF_BONUS,
            amount=Decimal("1000000"), delta_gross=Decimal("1000000"),
            reason="Bonus",
        )
        uc.create_adjustment(adj)
        r = uc.list_run_adjustments(run.id)
        assert r.is_success()
        assert len(r.get_data()) == 1


# ═══════════════════════════════════════════════════════════════════════
# Group 8: PIT Declaration (UC-PR-09)
# ═══════════════════════════════════════════════════════════════════════

class TestPITDeclaration:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_generate_pit_declaration(self, uc):
        self._setup_computed_run(uc)
        r = uc.generate_pit_declaration(6, 2026, declaration_type="monthly")
        assert r.is_success()
        decl = r.get_data()
        assert decl.declaration_type == PayrollDeclarationType.MONTHLY
        assert decl.total_income == Decimal("20000000.00")
        assert decl.status == PayrollDeclarationStatus.DRAFT

    def test_get_pit_declaration(self, uc):
        self._setup_computed_run(uc)
        r = uc.generate_pit_declaration(6, 2026)
        assert r.is_success()
        decl = r.get_data()
        r2 = uc.get_pit_declaration(decl.id)
        assert r2.is_success()
        assert r2.get_data().id == decl.id

    def test_list_pit_declarations(self, uc):
        self._setup_computed_run(uc)
        uc.generate_pit_declaration(6, 2026)
        r = uc.list_pit_declarations(filters={"period_year": 2026})
        assert r.is_success()
        assert len(r.get_data()) >= 1

    def test_generate_pit_declaration_no_run_fails(self, uc):
        r = uc.generate_pit_declaration(6, 2026)
        assert r.is_failure()


# ═══════════════════════════════════════════════════════════════════════
# Group 9: SI Insurance Record (UC-PR-10)
# ═══════════════════════════════════════════════════════════════════════

class TestSIInsuranceRecord:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_generate_si_record(self, uc):
        self._setup_computed_run(uc)
        r = uc.generate_si_record(6, 2026)
        assert r.is_success()
        rec = r.get_data()
        assert rec.period_month == 6
        assert rec.period_year == 2026
        assert rec.total_si_base == Decimal("20000000.00")
        assert rec.status == PayrollDeclarationStatus.DRAFT

    def test_submit_si_record(self, uc):
        self._setup_computed_run(uc)
        r = uc.generate_si_record(6, 2026)
        assert r.is_success()
        rec = r.get_data()
        r2 = uc.submit_si_record(rec.id)
        assert r2.is_success()
        r3 = uc.get_si_record(rec.id)
        assert r3.is_success()
        assert r3.get_data().status == PayrollDeclarationStatus.SUBMITTED

    def test_get_si_record(self, uc):
        self._setup_computed_run(uc)
        r = uc.generate_si_record(6, 2026)
        assert r.is_success()
        rec = r.get_data()
        r2 = uc.get_si_record(rec.id)
        assert r2.is_success()
        assert r2.get_data().id == rec.id


# ═══════════════════════════════════════════════════════════════════════
# Group 10: GL Posting (UC-PR-08)
# ═══════════════════════════════════════════════════════════════════════

class TestGLPosting:
    def _setup_approved_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        r2 = uc.approve_payroll(run.id, "manager")
        assert r2.is_success()
        return uc.get_payroll_run(run.id).get_data()

    def test_post_payroll_to_gl(self, uc):
        run = self._setup_approved_run(uc)
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 100},
        ]
        r = uc.post_payroll_to_gl(run.id, allocations)
        assert r.is_success()
        result = r.get_data()
        assert result["run_id"] == run.id
        assert len(result["allocations"]) == 1
        alloc = result["allocations"][0]
        assert alloc["cost_center"] == CostCenter.ADMINISTRATION.value
        assert alloc["salary_cost"] == run.total_gross
        assert alloc["employer_cost"] > Decimal("0")

    def test_post_payroll_split_allocation(self, uc):
        run = self._setup_approved_run(uc)
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 60},
            {"cost_center": CostCenter.SELLING.value, "percentage": 40},
        ]
        r = uc.post_payroll_to_gl(run.id, allocations)
        assert r.is_success()
        result = r.get_data()
        assert len(result["allocations"]) == 2

    def test_post_payroll_on_draft_fails(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 100},
        ]
        r2 = uc.post_payroll_to_gl(run.id, allocations)
        assert r2.is_failure()


# ═══════════════════════════════════════════════════════════════════════
# Group 11: Reports (UC-PR-12)
# ═══════════════════════════════════════════════════════════════════════

class TestPayrollReports:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_get_payroll_summary(self, uc):
        self._setup_computed_run(uc)
        r = uc.get_payroll_summary(6, 2026)
        assert r.is_success()
        s = r.get_data()
        assert s["period"] == "6/2026"
        assert s["status"] == "computed"
        assert s["employee_count"] == 1
        assert s["total_gross"] == Decimal("20000000.00")

    def test_get_employee_payslip(self, uc):
        run = self._setup_computed_run(uc)
        emp_id = run.lines[0].employee_id
        r = uc.get_employee_payslip(run.id, emp_id)
        assert r.is_success()
        slip = r.get_data()
        assert slip["employee_id"] == emp_id
        assert slip["gross_salary"] == run.lines[0].gross_salary
        assert slip["net_pay"] == run.lines[0].net_pay

    def test_get_department_summary(self, uc):
        self._setup_computed_run(uc)
        r = uc.get_department_summary(6, 2026)
        assert r.is_success()
        data = r.get_data()
        assert len(data) >= 1
        assert data[0]["employee_count"] >= 1

    def test_get_yearly_summary(self, uc):
        _create_full_employee(uc, code="EMP001", working_days=26)
        uc.compute_payroll(6, 2026)
        r = uc.get_yearly_summary(2026)
        assert r.is_success()
        data = r.get_data()
        assert data["year"] == 2026
        assert len(data["months"]) == 12
        month6 = data["months"][5]
        assert month6["status"] == "computed"
        assert month6["total_gross"] == Decimal("20000000.00")
        for m in range(1, 13):
            if m != 6:
                assert data["months"][m-1]["status"] == "not_computed"


# ═══════════════════════════════════════════════════════════════════════
# Group 12: Dashboard (UC-PR-15)
# ═══════════════════════════════════════════════════════════════════════

class TestDashboard:
    def test_get_dashboard(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        dash = uc.get_dashboard(6, 2026)
        assert dash["period"] == "6/2026"
        assert dash["employees"]["active"] >= 1
        assert dash["current"]["total_gross"] == Decimal("20000000.00")
        assert dash["current"]["employee_count"] >= 1

    def test_get_dashboard_no_run(self, uc):
        _create_employee(uc, code="EMP001")
        dash = uc.get_dashboard(6, 2026)
        assert dash["period"] == "6/2026"
        assert dash["current"]["total_gross"] == Decimal("0")
        assert dash["current"]["employee_count"] == 0
        assert dash["employees"]["active"] >= 1


# ═══════════════════════════════════════════════════════════════════════
# Group 13: Compute Single Employee (UC-PR-04 extension)
# ═══════════════════════════════════════════════════════════════════════

class TestSingleEmployeeComputation:
    def test_compute_single_employee(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_single_employee(1, 6, 2026)
        assert r.is_success()
        data = r.get_data()
        assert data["gross_salary"] == Decimal("20000000.00")

    def test_compute_single_employee_no_contract_fails(self, uc):
        r = _create_employee(uc, code="EMP001")
        emp = r.get_data()
        r2 = uc.compute_single_employee(emp.id, 6, 2026)
        assert r2.is_failure()


# ═══════════════════════════════════════════════════════════════════════
# Group 14: Bank File Generation (UC-PR-11)
# ═══════════════════════════════════════════════════════════════════════

class TestBankFileGeneration:
    def _setup_approved_run_for_bank(self, uc):
        _create_full_employee(uc, code="EMP001", bank_account="1234567890",
                              bank_name="Vietcombank")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        run = r.get_data()
        uc.approve_payroll(run.id, "manager")
        return uc.get_payroll_run(run.id).get_data()

    def test_generate_bank_transfer_file_csv(self, uc):
        run = self._setup_approved_run_for_bank(uc)
        r = uc.generate_bank_transfer_file(run.id, file_format="csv")
        assert r.is_success()
        data = r.get_data()
        assert data["file_format"] == "csv"
        assert data["record_count"] >= 1

    def test_generate_bank_transfer_file_text(self, uc):
        run = self._setup_approved_run_for_bank(uc)
        r = uc.generate_bank_transfer_file(run.id, file_format="text")
        assert r.is_success()
        data = r.get_data()
        assert data["file_format"] == "text"
        assert data["record_count"] >= 1


# ═══════════════════════════════════════════════════════════════════════
# Group 15: Cost Allocation (UC-PR-14)
# ═══════════════════════════════════════════════════════════════════════

class TestCostAllocation:
    def _setup_computed_run(self, uc):
        _create_full_employee(uc, code="EMP001")
        r = uc.compute_payroll(6, 2026)
        assert r.is_success()
        return r.get_data()

    def test_allocate_payroll_costs(self, uc):
        run = self._setup_computed_run(uc)
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 100},
        ]
        r = uc.allocate_payroll_costs(run.id, allocations)
        assert r.is_success()
        result = r.get_data()
        assert result["count"] == 1

    def test_allocate_payroll_costs_split(self, uc):
        run = self._setup_computed_run(uc)
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 70},
            {"cost_center": CostCenter.SELLING.value, "percentage": 30},
        ]
        r = uc.allocate_payroll_costs(run.id, allocations)
        assert r.is_success()
        result = r.get_data()
        assert result["count"] == 2

    def test_allocate_payroll_costs_invalid_percentage(self, uc):
        run = self._setup_computed_run(uc)
        allocations = [
            {"cost_center": CostCenter.ADMINISTRATION.value, "percentage": 50},
        ]
        r = uc.allocate_payroll_costs(run.id, allocations)
        assert r.is_failure()


# ═══════════════════════════════════════════════════════════════════════
# Group 16: Payroll Calculator Domain Tests
# ═══════════════════════════════════════════════════════════════════════

class TestPayrollCalculator:
    def test_compute_si_base(self):
        si_base = PayrollCalculator.compute_si_base(
            Decimal("20000000"), Region.REGION_1,
        )
        assert si_base == Decimal("20000000.00")

    def test_compute_si_base_caps_at_max(self):
        max_base = Decimal("20") * Decimal("2530000")
        si_base = PayrollCalculator.compute_si_base(
            Decimal("100000000"), Region.REGION_1,
        )
        assert si_base == max_base.quantize(Decimal("0.01"))

    def test_compute_gross_salary(self):
        gross = PayrollCalculator.compute_gross_salary(
            Decimal("20000000"), Decimal("26"), Decimal("26"),
        )
        assert gross == Decimal("20000000.00")

    def test_compute_gross_salary_prorated(self):
        gross = PayrollCalculator.compute_gross_salary(
            Decimal("20000000"), Decimal("13"), Decimal("26"),
        )
        assert gross == Decimal("10000000.00")

    def test_compute_employee_insurance(self):
        si, hi, ui = PayrollCalculator.compute_employee_insurance(Decimal("20000000"))
        assert si == Decimal("1600000.00")
        assert hi == Decimal("300000.00")
        assert ui == Decimal("200000.00")

    def test_compute_employer_insurance(self):
        si, hi, ui, occ, kpcd = PayrollCalculator.compute_employer_insurance(Decimal("20000000"))
        expected_si = (Decimal("20000000") * Decimal("0.14")).quantize(Decimal("0.01"))
        expected_sickness = (Decimal("20000000") * Decimal("0.03")).quantize(Decimal("0.01"))
        expected_occ = (Decimal("20000000") * Decimal("0.005")).quantize(Decimal("0.01"))
        expected_hi = (Decimal("20000000") * Decimal("0.03")).quantize(Decimal("0.01"))
        expected_ui = (Decimal("20000000") * Decimal("0.01")).quantize(Decimal("0.01"))
        expected_kpcd = (Decimal("20000000") * Decimal("0.02")).quantize(Decimal("0.01"))
        expected_si_total = (expected_si + expected_sickness + expected_occ).quantize(Decimal("0.01"))
        assert si == expected_si_total
        assert hi == expected_hi
        assert ui == expected_ui
        assert occ == expected_occ
        assert kpcd == expected_kpcd

    def test_compute_pit_tax_free(self):
        pit = PayrollCalculator.compute_pit(Decimal("0"))
        assert pit == Decimal("0")

    def test_compute_pit_bracket_1(self):
        pit = PayrollCalculator.compute_pit(Decimal("8000000"))
        # 8M * 5% = 400K
        assert pit == Decimal("400000.00")

    def test_compute_pit_bracket_2(self):
        pit = PayrollCalculator.compute_pit(Decimal("20000000"))
        # 20M * 10% - 500K = 2M - 500K = 1.5M
        assert pit == Decimal("1500000.00")

    def test_compute_full_payroll_line(self):
        result = PayrollCalculator.compute_full_payroll_line(
            base_salary=Decimal("20000000"),
            working_days=Decimal("26"),
            standard_days=Decimal("26"),
            overtime_amount=Decimal("0"),
            allowances_total=Decimal("0"),
            bonus_amount=Decimal("0"),
            si_base_salary=Decimal("20000000"),
            exempt_income=Decimal("0"),
            dependent_relief_amount=Decimal("0"),
            advance_deduction=Decimal("0"),
            other_deductions=Decimal("0"),
        )
        assert result["gross_salary"] == Decimal("20000000.00")
        assert result["personal_relief"] == Decimal("15500000.00")
        # No dependent relief, so taxable > 0
        emp_si = Decimal("20000000") * Decimal("0.08")
        emp_hi = Decimal("20000000") * Decimal("0.015")
        emp_ui = Decimal("20000000") * Decimal("0.01")
        taxable = Decimal("20000000") - emp_si - emp_hi - emp_ui - Decimal("15500000")
        assert taxable > Decimal("0")
        assert result["taxable_income"] > Decimal("0")
        assert result["pit_amount"] > Decimal("0")
        assert result["net_pay"] < result["gross_salary"]
