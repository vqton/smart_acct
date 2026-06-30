from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal

from domain import (
    Employee, EmployeeContract, Timesheet, PayrollRun, PayrollLine,
    PayrollAdjustment, PITDeclaration, SIInsuranceRecord, SalaryPayment,
    PayrollCostAllocation, PayrollCalculator,
    EmployeeStatus, ContractType, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, AdjustmentType, CostCenter,
    Result, ValidationError, VASValidationError,
)
from domain.payroll import DeclarationType as PayrollDeclarationType, DeclarationStatus as PayrollDeclarationStatus
from domain.i18n import ErrorCodes
from infrastructure.repositories.payroll_repository import PayrollRepository


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _calc_dependent_relief(dependent_count: int) -> Decimal:
    return _vnd(Decimal(str(dependent_count)) * Decimal("6200000"))


class PayrollUseCases:
    def __init__(self, session):
        self.repo = PayrollRepository(session)
        self._session = session

    # ── UC-PR-01: Employee Management ─────────────────────────────────

    def create_employee(self, employee: Employee) -> Result:
        try:
            employee.validate_code(employee.employee_code)
            employee.validate_name(employee.full_name)
        except VASValidationError as e:
            return Result.failure(e)
        existing = self.repo.get_employee_by_code(employee.employee_code)
        if existing.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_CODE_DUPLICATE,
                                                  code=employee.employee_code))
        result = self.repo.create_employee(employee)
        if result.is_success():
            self.repo.log_audit(
                action="EMPLOYEE_CREATED",
                employee_id=result.get_data().id,
                new_value={"employee_code": employee.employee_code, "full_name": employee.full_name},
                changed_by=employee.created_by,
            )
        return result

    def update_employee(self, employee: Employee) -> Result:
        existing = self.repo.get_employee(employee.id)
        if not existing:
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_NOT_FOUND,
                                                  employee_id=employee.id))
        result = self.repo.update_employee(employee)
        if result.is_success():
            self.repo.log_audit(
                action="EMPLOYEE_UPDATED",
                employee_id=employee.id,
                changed_by=employee.updated_by,
            )
        return result

    def get_employee(self, employee_id: int) -> Result:
        return self.repo.get_employee(employee_id)

    def list_employees(self, filters: dict = None, page: int = 1, per_page: int = 20) -> Result:
        return self.repo.list_employees(filters=filters, page=page, per_page=per_page)

    def terminate_employee(self, employee_id: int, termination_date: date, reason: str = None) -> Result:
        emp_result = self.repo.get_employee(employee_id)
        if not emp_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_NOT_FOUND,
                                                  employee_id=employee_id))
        emp = emp_result.get_data()
        emp.status = EmployeeStatus.TERMINATED
        emp.termination_date = termination_date
        result = self.repo.update_employee(emp)
        if result.is_success():
            active_contract_result = self.repo.get_active_contract(employee_id)
            if active_contract_result.is_success():
                active_contract = active_contract_result.get_data()
                active_contract.is_active = False
                self.repo.update_contract(active_contract)
            self.repo.log_audit(
                action="EMPLOYEE_TERMINATED",
                employee_id=employee_id,
                new_value={"termination_date": termination_date.isoformat(), "reason": reason},
                changed_by="system",
            )
        return result

    # ── UC-PR-02: Contract Management ─────────────────────────────────

    def create_contract(self, contract: EmployeeContract) -> Result:
        emp_result = self.repo.get_employee(contract.employee_id)
        if not emp_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_NOT_FOUND,
                                                  employee_id=contract.employee_id))
        if contract.is_active:
            existing_active = self.repo.get_active_contract(contract.employee_id)
            if existing_active.is_success():
                existing_active.get_data().is_active = False
                self.repo.update_contract(existing_active.get_data())
        result = self.repo.create_contract(contract)
        return result

    def update_contract(self, contract: EmployeeContract) -> Result:
        existing_result = self.repo.get_contract(contract.id)
        if not existing_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_CONTRACT_NOT_FOUND,
                                                  contract_id=contract.id))
        result = self.repo.update_contract(contract)
        return result

    def get_active_contract(self, employee_id: int) -> Result:
        return self.repo.get_active_contract(employee_id)

    def list_employee_contracts(self, employee_id: int) -> Result:
        return self.repo.list_employee_contracts(employee_id)

    # ── UC-PR-03: Timesheet Entry ─────────────────────────────────────

    def upsert_timesheet(self, timesheet: Timesheet) -> Result:
        emp_result = self.repo.get_employee(timesheet.employee_id)
        if not emp_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_TIMESHEET_EMPLOYEE_NOT_FOUND,
                                                  employee_id=timesheet.employee_id))
        result = self.repo.upsert_timesheet(timesheet)
        return result

    def get_employee_timesheet(self, employee_id: int, month: int, year: int) -> Result:
        return self.repo.get_employee_timesheet(employee_id, month, year)

    def list_period_timesheets(self, month: int, year: int) -> Result:
        return self.repo.list_period_timesheets(month, year)

    def batch_upsert_timesheets(self, timesheets: List[Timesheet]) -> Result:
        results = []
        for ts in timesheets:
            r = self.upsert_timesheet(ts)
            if r.is_success():
                results.append(r.get_data())
        return Result.success(results)

    # ── UC-PR-04: Payroll Computation ─────────────────────────────────

    def compute_payroll(self, month: int, year: int, created_by: str = None) -> Result:
        existing = self.repo.get_run_by_period(month, year)
        if existing.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_ALREADY_EXISTS,
                                                  month=month, year=year))
        employees = self.repo.get_employees_for_period(month, year)
        if not employees:
            return Result.success({"run_id": None, "lines": [], "message": "No active employees"})

        lines = []
        for emp_data in employees:
            emp = emp_data["employee"]
            contract = emp_data["contract"]
            timesheet = emp_data.get("timesheet")

            if not contract:
                continue

            working_days = timesheet.working_days if timesheet else Decimal("0")
            standard_days = timesheet.standard_days if timesheet else Decimal("26")
            overtime_hours = (timesheet.overtime_weekday_hours if timesheet else Decimal("0")
                              + (timesheet.overtime_weekend_hours if timesheet else Decimal("0")) * Decimal("1.5")
                              + (timesheet.overtime_holiday_hours if timesheet else Decimal("0")) * Decimal("2"))

            hourly_rate = contract.base_salary / (standard_days * 8) if standard_days > 0 else Decimal("0")
            overtime_amount = _vnd(overtime_hours * hourly_rate)
            allowances_total = contract.meal_allowance + contract.phone_allowance \
                + contract.transport_allowance + contract.housing_allowance + contract.other_allowance
            si_base_salary = PayrollCalculator.compute_si_base(
                contract.total_regular_income(), emp.region
            )
            dependent_relief = _calc_dependent_relief(emp.dependent_count)
            advance_deduction = Decimal("0")

            computed = PayrollCalculator.compute_full_payroll_line(
                base_salary=contract.base_salary,
                working_days=working_days,
                standard_days=standard_days,
                overtime_amount=overtime_amount,
                allowances_total=allowances_total,
                bonus_amount=Decimal("0"),
                si_base_salary=si_base_salary,
                exempt_income=Decimal("0"),
                dependent_relief_amount=dependent_relief,
                advance_deduction=advance_deduction,
                other_deductions=Decimal("0"),
            )

            line = PayrollLine(
                employee_id=emp.id,
                employee_code=emp.employee_code,
                employee_name=emp.full_name,
                base_salary=contract.base_salary,
                working_days=working_days,
                standard_days=standard_days,
                overtime_amount=computed["overtime_amount"],
                allowances_total=computed["allowances_total"],
                bonus_amount=computed["bonus_amount"],
                prorated_salary=computed["prorated_salary"],
                gross_salary=computed["gross_salary"],
                si_base_salary=computed["si_base_salary"],
                employee_si=computed["employee_si"],
                employee_hi=computed["employee_hi"],
                employee_ui=computed["employee_ui"],
                advance_deduction=computed["advance_deduction"],
                other_deductions=computed["other_deductions"],
                exempt_income=computed["exempt_income"],
                personal_relief=computed["personal_relief"],
                dependent_relief=computed["dependent_relief"],
                taxable_income=computed["taxable_income"],
                pit_amount=computed["pit_amount"],
                net_pay=computed["net_pay"],
                employer_si=computed["employer_si"],
                employer_hi=computed["employer_hi"],
                employer_ui=computed["employer_ui"],
                employer_occ=computed["employer_occ"],
                kpcd=computed["kpcd"],
                payment_method=PaymentMethodPR.BANK_TRANSFER,
                payment_status=PaymentStatus.PENDING,
            )
            lines.append(line)

        run = PayrollRun(
            period_month=month,
            period_year=year,
            status=PayrollRunStatus.COMPUTED,
            lines=lines,
            computed_at=datetime.now(timezone.utc),
            created_by=created_by,
        )
        run.compute_totals()

        result = self.repo.create_run(run)
        if result.is_success():
            self.repo.log_audit(
                action="PAYROLL_COMPUTED",
                payroll_run_id=result.get_data().id,
                new_value={"month": month, "year": year, "lines": len(lines)},
                changed_by=created_by,
            )
        return result

    def compute_single_employee(self, employee_id: int, month: int, year: int) -> Result:
        emp_result = self.repo.get_employee(employee_id)
        if not emp_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_NOT_FOUND,
                                                  employee_id=employee_id))
        emp = emp_result.get_data()
        contract_result = self.repo.get_active_contract(employee_id)
        if not contract_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_NO_ACTIVE_CONTRACT,
                                                  employee_id=employee_id))
        contract = contract_result.get_data()
        ts_result = self.repo.get_employee_timesheet(employee_id, month, year)
        timesheet = ts_result.get_data() if ts_result.is_success() else None

        working_days = timesheet.working_days if timesheet else Decimal("0")
        standard_days = timesheet.standard_days if timesheet else Decimal("26")
        overtime_hours = (timesheet.overtime_weekday_hours if timesheet else Decimal("0")
                          + (timesheet.overtime_weekend_hours if timesheet else Decimal("0")) * Decimal("1.5")
                          + (timesheet.overtime_holiday_hours if timesheet else Decimal("0")) * Decimal("2"))
        hourly_rate = contract.base_salary / (standard_days * 8) if standard_days > 0 else Decimal("0")
        overtime_amount = _vnd(overtime_hours * hourly_rate)
        allowances_total = contract.meal_allowance + contract.phone_allowance \
            + contract.transport_allowance + contract.housing_allowance + contract.other_allowance
        si_base_salary = PayrollCalculator.compute_si_base(
            contract.total_regular_income(), emp.region
        )
        dependent_relief = _calc_dependent_relief(emp.dependent_count)

        computed = PayrollCalculator.compute_full_payroll_line(
            base_salary=contract.base_salary,
            working_days=working_days,
            standard_days=standard_days,
            overtime_amount=overtime_amount,
            allowances_total=allowances_total,
            bonus_amount=Decimal("0"),
            si_base_salary=si_base_salary,
            exempt_income=Decimal("0"),
            dependent_relief_amount=dependent_relief,
            advance_deduction=Decimal("0"),
            other_deductions=Decimal("0"),
        )
        return Result.success({
            "employee_id": employee_id,
            "employee_code": emp.employee_code,
            "employee_name": emp.full_name,
            **computed,
        })

    # ── UC-PR-05: Payroll Review & Approval ───────────────────────────

    def get_payroll_run(self, run_id: int) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        return run_result

    def list_payroll_runs(self, filters: dict = None) -> Result:
        return self.repo.list_runs(filters=filters)

    def approve_payroll(self, run_id: int, approved_by: str) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()
        if run.status != PayrollRunStatus.COMPUTED:
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_ALREADY_APPROVED,
                                                  run_id=run_id, status=run.status.value))
        run.status = PayrollRunStatus.APPROVED
        run.approved_at = datetime.now(timezone.utc)
        run.approved_by = approved_by
        result = self.repo.update_run(run)
        if result.is_success():
            self.repo.log_audit(
                action="PAYROLL_APPROVED",
                payroll_run_id=run_id,
                new_value={"approved_by": approved_by},
                changed_by=approved_by,
            )
        return result

    def cancel_payroll(self, run_id: int, reason: str) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()
        if run.status not in (PayrollRunStatus.DRAFT, PayrollRunStatus.COMPUTED):
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  run_id=run_id, status=run.status.value))
        run.status = PayrollRunStatus.CANCELLED
        run.notes = reason
        result = self.repo.update_run(run)
        if result.is_success():
            self.repo.log_audit(
                action="PAYROLL_CANCELLED",
                payroll_run_id=run_id,
                new_value={"reason": reason},
                changed_by="system",
            )
        return result

    # ── UC-PR-06: Salary Payment ──────────────────────────────────────

    def process_payment(self, run_id: int, payment_date: date, payment_method: str,
                        bank_transaction_ref: str = None, created_by: str = None) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()
        if run.status != PayrollRunStatus.APPROVED:
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_APPROVED,
                                                  run_id=run_id, status=run.status.value))
        payment = SalaryPayment(
            payroll_run_id=run_id,
            payment_date=payment_date,
            payment_method=PaymentMethodPR(payment_method),
            total_amount=run.total_net,
            bank_transaction_ref=bank_transaction_ref,
            created_by=created_by,
        )
        payment_result = self.repo.create_salary_payment(payment)
        if not payment_result.is_success():
            return payment_result

        self.repo.update_lines_payment_status(run_id, PaymentStatus.PAID)
        run.status = PayrollRunStatus.PAID
        run.paid_at = datetime.now(timezone.utc)
        self.repo.update_run(run)
        self.repo.log_audit(
            action="PAYROLL_PAID",
            payroll_run_id=run_id,
            new_value={"payment_date": payment_date.isoformat(), "total": str(run.total_net)},
            changed_by=created_by,
        )
        return payment_result

    def get_run_payments(self, run_id: int) -> Result:
        return self.repo.get_run_payments(run_id)

    # ── UC-PR-07: Payroll Adjustments ─────────────────────────────────

    def create_adjustment(self, adj: PayrollAdjustment) -> Result:
        run_result = self.repo.get_run(adj.payroll_run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND,
                                                  run_id=adj.payroll_run_id))
        run = run_result.get_data()
        if run.status not in (PayrollRunStatus.COMPUTED, PayrollRunStatus.APPROVED):
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  run_id=adj.payroll_run_id))
        result = self.repo.create_adjustment(adj)
        if result.is_success():
            self.repo.log_audit(
                action="ADJUSTMENT_CREATED",
                payroll_run_id=adj.payroll_run_id,
                new_value={"employee_id": adj.employee_id, "amount": str(adj.amount),
                           "type": adj.adjustment_type.value},
                changed_by=adj.created_by,
            )
        return result

    def approve_adjustment(self, adj_id: int, approved_by: str) -> Result:
        adj_result = self.repo.get_adjustment(adj_id)
        if not adj_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_ADJUSTMENT_NOT_FOUND,
                                                  adjustment_id=adj_id))
        adj = adj_result.get_data()
        adj.approved_by = approved_by
        adj.approved_at = datetime.now(timezone.utc)
        adj.status = PayrollRunStatus.COMPUTED
        result = self.repo.update_adjustment(adj)
        if result.is_success():
            run_result = self.repo.get_run(adj.payroll_run_id)
            if run_result.is_success():
                run = run_result.get_data()
                run.status = PayrollRunStatus.ADJUSTMENT
                self.repo.update_run(run)
            self.repo.log_audit(
                action="ADJUSTMENT_APPROVED",
                payroll_run_id=adj.payroll_run_id,
                new_value={"adjustment_id": adj_id, "approved_by": approved_by},
                changed_by=approved_by,
            )
        return result

    def list_run_adjustments(self, run_id: int) -> Result:
        return self.repo.list_run_adjustments(run_id)

    # ── UC-PR-08: Payroll GL Posting ──────────────────────────────────

    def post_payroll_to_gl(self, run_id: int, allocations: List[dict]) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()
        if run.status not in (PayrollRunStatus.APPROVED, PayrollRunStatus.PAID):
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  run_id=run_id, status=run.status.value))

        journal_refs = []
        for alloc in allocations:
            cost_center = CostCenter(alloc.get("cost_center", CostCenter.ADMINISTRATION.value))
            pct = Decimal(str(alloc.get("percentage", 100)))
            factor = pct / Decimal("100")

            salary_cost = _vnd(run.total_gross * factor)
            employer_cost = _vnd(
                (run.total_employer_si + run.total_employer_hi
                 + run.total_employer_ui + run.total_employer_occ) * factor
            )
            pit_amount = _vnd(run.total_pit * factor)
            si_employee = _vnd(
                (run.total_employee_si + run.total_employee_hi + run.total_employee_ui) * factor
            )
            kpcd_amount = _vnd(run.total_kpcd * factor)

            coa = CostCenter(cost_center)
            lines = [
                {"account_id": coa.value, "debit": salary_cost, "credit": Decimal("0"),
                 "description": f"Payroll cost - period {run.period_month}/{run.period_year}"},
                {"account_id": "334", "debit": Decimal("0"), "credit": salary_cost,
                 "description": "Salary payable"},
                {"account_id": coa.value, "debit": employer_cost, "credit": Decimal("0"),
                 "description": "Employer SI cost"},
                {"account_id": "3383", "debit": Decimal("0"), "credit": _vnd(employer_cost * Decimal("0.14") / Decimal("0.185")),
                 "description": "Employer SI payable"},
                {"account_id": "3384", "debit": Decimal("0"), "credit": _vnd(employer_cost * Decimal("0.03") / Decimal("0.185")),
                 "description": "Employer HI payable"},
                {"account_id": "3385", "debit": Decimal("0"), "credit": _vnd(employer_cost * Decimal("0.01") / Decimal("0.185")),
                 "description": "Employer UI payable"},
                {"account_id": "3386", "debit": Decimal("0"), "credit": kpcd_amount,
                 "description": "KPCD payable"},
            ]

            cost_alloc = PayrollCostAllocation(
                payroll_run_id=run_id,
                cost_center=coa,
                total_salary_cost=salary_cost,
                total_employer_cost=employer_cost,
                total_cost=_vnd(salary_cost + employer_cost),
                gl_journal_entry_ref=f"PR-{run_id}-{cost_center.value}",
            )
            self.repo.create_cost_allocation(cost_alloc)
            journal_refs.append({
                "cost_center": cost_center.value,
                "salary_cost": salary_cost,
                "employer_cost": employer_cost,
                "journal_lines": lines,
            })

        return Result.success({"run_id": run_id, "allocations": journal_refs})

    # ── UC-PR-09: PIT Declaration ─────────────────────────────────────

    def generate_pit_declaration(self, period_month: int, period_year: int,
                                 declaration_type: str = "monthly") -> Result:
        run_result = self.repo.get_run_by_period(period_month, period_year)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND,
                                                  month=period_month, year=period_year))
        run = run_result.get_data()
        decl = PITDeclaration(
            declaration_type=PayrollDeclarationType(declaration_type),
            period_month=period_month,
            period_year=period_year,
            total_income=run.total_gross,
            total_deductions=run.total_employee_si + run.total_employee_hi + run.total_employee_ui,
            total_personal_relief=sum(l.personal_relief for l in run.lines),
            total_dependent_relief=sum(l.dependent_relief for l in run.lines),
            total_exempt_income=sum(l.exempt_income for l in run.lines),
            total_taxable_income=run.total_gross - run.total_employee_si - run.total_employee_hi
            - run.total_employee_ui - sum(l.exempt_income for l in run.lines)
            - sum(l.personal_relief for l in run.lines) - sum(l.dependent_relief for l in run.lines),
            total_pit=run.total_pit,
            total_pit_withheld=run.total_pit,
            submission_type="initial",
        )
        decl.total_taxable_income = max(Decimal("0"), decl.total_taxable_income).quantize(Decimal("0.01"))
        total_deductions = sum(l.additional_deductions for l in run.lines)
        decl.total_deductions += total_deductions
        result = self.repo.create_pit_declaration(decl)
        return result

    def get_pit_declaration(self, decl_id: int) -> Result:
        decl = self.repo.get_pit_declaration(decl_id)
        if not decl.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PIT_DECLARATION_NOT_FOUND,
                                                  declaration_id=decl_id))
        return decl

    def list_pit_declarations(self, filters: dict = None) -> Result:
        return self.repo.list_pit_declarations(filters=filters)

    # ── UC-PR-10: SI Insurance Records ────────────────────────────────

    def generate_si_record(self, month: int, year: int) -> Result:
        run_result = self.repo.get_run_by_period(month, year)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND,
                                                  month=month, year=year))
        run = run_result.get_data()
        record = SIInsuranceRecord(
            payroll_run_id=run.id,
            period_month=month,
            period_year=year,
            total_si_base=sum(l.si_base_salary for l in run.lines),
            total_employee_si=run.total_employee_si,
            total_employee_hi=run.total_employee_hi,
            total_employee_ui=run.total_employee_ui,
            total_employer_si=run.total_employer_si,
            total_employer_hi=run.total_employer_hi,
            total_employer_ui=run.total_employer_ui,
            total_employer_occ=run.total_employer_occ,
            total_kpcd=run.total_kpcd,
            total_payable=_vnd(run.total_employee_si + run.total_employee_hi + run.total_employee_ui
                               + run.total_employer_si + run.total_employer_hi + run.total_employer_ui
                               + run.total_employer_occ + run.total_kpcd),
        )
        result = self.repo.create_si_record(record)
        return result

    def get_si_record(self, record_id: int) -> Result:
        record = self.repo.get_si_record(record_id)
        if not record.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_SI_RECORD_NOT_FOUND,
                                                  record_id=record_id))
        return record

    def submit_si_record(self, record_id: int) -> Result:
        record_result = self.repo.get_si_record(record_id)
        if not record_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_SI_RECORD_NOT_FOUND,
                                                  record_id=record_id))
        record = record_result.get_data()
        record.status = PayrollDeclarationStatus.SUBMITTED
        record.submission_date = datetime.now(timezone.utc)
        result = self.repo.update_si_record(record)
        return result

    # ── UC-PR-11: Bank File Generation ────────────────────────────────

    def generate_bank_transfer_file(self, run_id: int, file_format: str = "csv") -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()

        bank_lines = [
            l for l in run.lines
            if l.payment_status == PaymentStatus.PENDING
            and l.payment_method == PaymentMethodPR.BANK_TRANSFER
        ]
        if not bank_lines:
            return Result.failure(ValidationError(ErrorCodes.PR_BANK_FILE_GENERATION_FAILED,
                                                  detail="No pending bank transfer lines"))

        if file_format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["bank_code", "account_number", "amount", "full_name"])
            for line in bank_lines:
                emp_result = self.repo.get_employee(line.employee_id)
                emp = emp_result.get_data() if emp_result.is_success() else None
                writer.writerow([(emp.bank_name or "") if emp else "",
                                 (emp.bank_account or "") if emp else "",
                                 str(line.net_pay), line.employee_name or ""])
            content = output.getvalue()
            output.close()
        else:
            lines_text = []
            for line in bank_lines:
                emp_result = self.repo.get_employee(line.employee_id)
                emp = emp_result.get_data() if emp_result.is_success() else None
                bank_account = emp.bank_account if emp else ""
                lines_text.append(f"{bank_account or ''}|{str(line.net_pay)}|{line.employee_name or ''}")
            content = "\n".join(lines_text)

        return Result.success({
            "file_content": content,
            "file_format": file_format,
            "record_count": len(bank_lines),
            "total_amount": str(sum(l.net_pay for l in bank_lines)),
        })

    # ── UC-PR-12: Payroll Reports ─────────────────────────────────────

    def get_payroll_summary(self, month: int, year: int) -> Result:
        run_result = self.repo.get_run_by_period(month, year)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND,
                                                  month=month, year=year))
        run = run_result.get_data()
        return Result.success({
            "period": f"{month}/{year}",
            "status": run.status.value,
            "employee_count": len(run.lines),
            "total_gross": run.total_gross,
            "total_deductions": _vnd(run.total_employee_si + run.total_employee_hi
                                     + run.total_employee_ui + run.total_pit
                                     + run.total_advances + run.total_other_deductions),
            "total_net": run.total_net,
            "total_employer_cost": _vnd(run.total_employer_si + run.total_employer_hi
                                        + run.total_employer_ui + run.total_employer_occ
                                        + run.total_kpcd),
            "total_pit": run.total_pit,
        })

    def get_employee_payslip(self, run_id: int, employee_id: int) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()
        line = next((l for l in run.lines if l.employee_id == employee_id), None)
        if not line:
            return Result.failure(ValidationError(ErrorCodes.PR_EMPLOYEE_NOT_FOUND,
                                                  employee_id=employee_id))
        return Result.success({
            "run_id": run_id,
            "period": f"{run.period_month}/{run.period_year}",
            "employee_id": employee_id,
            "employee_code": line.employee_code,
            "employee_name": line.employee_name,
            "base_salary": line.base_salary,
            "working_days": line.working_days,
            "prorated_salary": line.prorated_salary,
            "overtime_amount": line.overtime_amount,
            "allowances_total": line.allowances_total,
            "bonus_amount": line.bonus_amount,
            "gross_salary": line.gross_salary,
            "employee_si": line.employee_si,
            "employee_hi": line.employee_hi,
            "employee_ui": line.employee_ui,
            "pit_amount": line.pit_amount,
            "advance_deduction": line.advance_deduction,
            "other_deductions": line.other_deductions,
            "net_pay": line.net_pay,
            "employer_si": line.employer_si,
            "employer_hi": line.employer_hi,
            "employer_ui": line.employer_ui,
            "employer_occ": line.employer_occ,
            "kpcd": line.kpcd,
        })

    def get_department_summary(self, month: int, year: int, department_id: int = None) -> Result:
        run_result = self.repo.get_run_by_period(month, year)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND,
                                                  month=month, year=year))
        run = run_result.get_data()
        dept_lines = {}
        for line in run.lines:
            emp_result = self.repo.get_employee(line.employee_id)
            emp = emp_result.get_data() if emp_result.is_success() else None
            dept = emp.department_id if emp else None
            dept_name = emp.department_name if emp else "N/A"
            if department_id is not None and dept != department_id:
                continue
            key = dept or 0
            if key not in dept_lines:
                dept_lines[key] = {
                    "department_id": dept,
                    "department_name": dept_name,
                    "employee_count": 0,
                    "total_gross": Decimal("0"),
                    "total_net": Decimal("0"),
                    "total_pit": Decimal("0"),
                    "total_employer_cost": Decimal("0"),
                }
            dept_lines[key]["employee_count"] += 1
            dept_lines[key]["total_gross"] += line.gross_salary
            dept_lines[key]["total_net"] += line.net_pay
            dept_lines[key]["total_pit"] += line.pit_amount
            dept_lines[key]["total_employer_cost"] += (line.employer_si + line.employer_hi
                                                       + line.employer_ui + line.employer_occ + line.kpcd)
        result = [v for v in dept_lines.values()]
        for r in result:
            for k in ("total_gross", "total_net", "total_pit", "total_employer_cost"):
                r[k] = _vnd(r[k])
        return Result.success(result)

    def get_yearly_summary(self, year: int) -> Result:
        months = []
        for m in range(1, 13):
            run_result = self.repo.get_run_by_period(m, year)
            if run_result.is_success():
                run = run_result.get_data()
                months.append({
                    "month": m,
                    "status": run.status.value,
                    "employee_count": len(run.lines),
                    "total_gross": run.total_gross,
                    "total_net": run.total_net,
                    "total_pit": run.total_pit,
                    "total_employer_cost": _vnd(run.total_employer_si + run.total_employer_hi
                                                + run.total_employer_ui + run.total_employer_occ
                                                + run.total_kpcd),
                })
            else:
                months.append({
                    "month": m, "status": "not_computed", "employee_count": 0,
                    "total_gross": Decimal("0"), "total_net": Decimal("0"),
                    "total_pit": Decimal("0"), "total_employer_cost": Decimal("0"),
                })
        return Result.success({
            "year": year,
            "months": months,
            "year_total_gross": sum(m["total_gross"] for m in months),
            "year_total_net": sum(m["total_net"] for m in months),
            "year_total_pit": sum(m["total_pit"] for m in months),
        })

    # ── UC-PR-13: Year-End Reports ────────────────────────────────────

    def generate_yearly_pit_summary(self, year: int) -> Result:
        total_income = Decimal("0")
        total_exempt = Decimal("0")
        total_deductions = Decimal("0")
        total_personal_relief = Decimal("0")
        total_dependent_relief = Decimal("0")
        total_taxable = Decimal("0")
        total_pit = Decimal("0")
        employee_data = {}

        for m in range(1, 13):
            run_result = self.repo.get_run_by_period(m, year)
            if run_result.is_success():
                run = run_result.get_data()
                for line in run.lines:
                    eid = line.employee_id
                    if eid not in employee_data:
                        emp_result = self.repo.get_employee(eid)
                        emp = emp_result.get_data() if emp_result.is_success() else None
                        employee_data[eid] = {
                            "employee_code": line.employee_code or "",
                            "employee_name": line.employee_name or "",
                            "tax_code": emp.tax_code if emp else "",
                            "total_income": Decimal("0"),
                            "total_pit": Decimal("0"),
                        }
                    employee_data[eid]["total_income"] += line.gross_salary
                    employee_data[eid]["total_pit"] += line.pit_amount
                total_income += run.total_gross
                total_exempt += sum(l.exempt_income for l in run.lines)
                total_deductions += (run.total_employee_si + run.total_employee_hi + run.total_employee_ui)
                total_personal_relief += sum(l.personal_relief for l in run.lines)
                total_dependent_relief += sum(l.dependent_relief for l in run.lines)
                total_taxable += max(Decimal("0"), sum(l.taxable_income for l in run.lines))
                total_pit += run.total_pit

        decl = PITDeclaration(
            declaration_type=DeclarationType.ANNUAL,
            period_year=year,
            submission_type="finalization",
            status=PayrollDeclarationStatus.DRAFT,
            total_income=_vnd(total_income),
            total_exempt_income=_vnd(total_exempt),
            total_deductions=_vnd(total_deductions),
            total_personal_relief=_vnd(total_personal_relief),
            total_dependent_relief=_vnd(total_dependent_relief),
            total_taxable_income=_vnd(total_taxable),
            total_pit=_vnd(total_pit),
            total_pit_withheld=_vnd(total_pit),
        )
        result = self.repo.create_pit_declaration(decl)
        if result.is_success():
            return Result.success({
                "declaration": decl,
                "employees": list(employee_data.values()),
                "totals": {
                    "total_income": _vnd(total_income),
                    "total_pit": _vnd(total_pit),
                    "employee_count": len(employee_data),
                },
            })
        return result

    def generate_si_yearly_finalization(self, year: int) -> Result:
        total_si_base = Decimal("0")
        total_employee_si = Decimal("0")
        total_employee_hi = Decimal("0")
        total_employee_ui = Decimal("0")
        total_employer_si = Decimal("0")
        total_employer_hi = Decimal("0")
        total_employer_ui = Decimal("0")
        total_employer_occ = Decimal("0")
        total_kpcd = Decimal("0")

        for m in range(1, 13):
            run_result = self.repo.get_run_by_period(m, year)
            if run_result.is_success():
                run = run_result.get_data()
                total_si_base += sum(l.si_base_salary for l in run.lines)
                total_employee_si += run.total_employee_si
                total_employee_hi += run.total_employee_hi
                total_employee_ui += run.total_employee_ui
                total_employer_si += run.total_employer_si
                total_employer_hi += run.total_employer_hi
                total_employer_ui += run.total_employer_ui
                total_employer_occ += run.total_employer_occ
                total_kpcd += run.total_kpcd

        total_payable = _vnd(total_employee_si + total_employee_hi + total_employee_ui
                              + total_employer_si + total_employer_hi + total_employer_ui
                              + total_employer_occ + total_kpcd)

        record = SIInsuranceRecord(
            period_month=12,
            period_year=year,
            status=PayrollDeclarationStatus.DRAFT,
            total_si_base=_vnd(total_si_base),
            total_employee_si=_vnd(total_employee_si),
            total_employee_hi=_vnd(total_employee_hi),
            total_employee_ui=_vnd(total_employee_ui),
            total_employer_si=_vnd(total_employer_si),
            total_employer_hi=_vnd(total_employer_hi),
            total_employer_ui=_vnd(total_employer_ui),
            total_employer_occ=_vnd(total_employer_occ),
            total_kpcd=_vnd(total_kpcd),
            total_payable=total_payable,
        )
        result = self.repo.create_si_record(record)
        return result

    # ── UC-PR-14: Cost Allocation ─────────────────────────────────────

    def allocate_payroll_costs(self, run_id: int, cost_allocations: List[dict]) -> Result:
        run_result = self.repo.get_run(run_id)
        if not run_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.PR_PAYROLL_NOT_FOUND, run_id=run_id))
        run = run_result.get_data()

        total_pct = sum(Decimal(str(a.get("percentage", 0))) for a in cost_allocations)
        if total_pct != Decimal("100"):
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  detail=f"Percentages sum to {total_pct}, must be 100"))

        created = []
        for alloc in cost_allocations:
            pct = Decimal(str(alloc.get("percentage", 0))) / Decimal("100")
            cost_center = CostCenter(alloc.get("cost_center", CostCenter.ADMINISTRATION.value))
            salary_cost = _vnd(run.total_gross * pct)
            employer_cost = _vnd(
                (run.total_employer_si + run.total_employer_hi
                 + run.total_employer_ui + run.total_employer_occ) * pct
            )
            cost_alloc = PayrollCostAllocation(
                payroll_run_id=run_id,
                cost_center=cost_center,
                total_salary_cost=salary_cost,
                total_employer_cost=employer_cost,
                total_cost=_vnd(salary_cost + employer_cost),
            )
            r = self.repo.create_cost_allocation(cost_alloc)
            if r.is_success():
                created.append(cost_alloc)

        return Result.success({
            "run_id": run_id,
            "allocations": created,
            "count": len(created),
        })

    # ── UC-PR-15: Dashboard ───────────────────────────────────────────

    def get_dashboard(self, month: int, year: int) -> dict:
        employees = self.repo.list_employees(filters={}, page=1, per_page=10000)
        emp_list = []
        if employees.is_success():
            data = employees.get_data()
            if isinstance(data, dict):
                emp_list = data.get("items", [])
        active_count = sum(1 for e in emp_list if e.status == EmployeeStatus.ACTIVE)
        terminated_count = sum(1 for e in emp_list if e.status == EmployeeStatus.TERMINATED)
        departments = set()
        for e in emp_list:
            if e.department_id:
                departments.add(e.department_id)

        run_result = self.repo.get_run_by_period(month, year)
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_run_result = self.repo.get_run_by_period(prev_month, prev_year)

        if run_result.is_success():
            run = run_result.get_data()
            current = {
                "total_gross": run.total_gross,
                "total_net": run.total_net,
                "total_employer_cost": _vnd(
                    run.total_employer_si + run.total_employer_hi + run.total_employer_ui
                    + run.total_employer_occ + run.total_kpcd
                ),
                "total_pit": run.total_pit,
                "employee_count": len(run.lines),
            }
        else:
            current = {
                "total_gross": Decimal("0"), "total_net": Decimal("0"),
                "total_employer_cost": Decimal("0"), "total_pit": Decimal("0"),
                "employee_count": 0,
            }

        if prev_run_result.is_success():
            prev_run = prev_run_result.get_data()
            previous = {
                "total_gross": prev_run.total_gross,
                "total_net": prev_run.total_net,
            }
        else:
            previous = {
                "total_gross": Decimal("0"), "total_net": Decimal("0"),
            }

        gross_change = Decimal("0")
        if previous["total_gross"] > Decimal("0"):
            gross_change = _vnd(
                (current["total_gross"] - previous["total_gross"]) / previous["total_gross"] * Decimal("100")
            )

        return {
            "period": f"{month}/{year}",
            "employees": {
                "active": active_count,
                "terminated": terminated_count,
                "total": len(emp_list),
            },
            "departments": len(departments),
            "current": current,
            "previous_period": previous,
            "change": {
                "gross_change_pct": gross_change,
            },
        }
