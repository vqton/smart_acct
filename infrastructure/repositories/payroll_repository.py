from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from decimal import Decimal
from math import ceil
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.exc import IntegrityError

from domain.payroll import (
    Employee, EmployeeContract, EmployeeDependent, Timesheet,
    PayrollRun, PayrollLine, PayrollAdjustment, PITDeclaration,
    SIInsuranceRecord, SalaryPayment, PayrollCostAllocation,
    EmployeeStatus, ContractType, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, DeclarationStatus, DeclarationType, AdjustmentType,
    CostCenter, Region,
)
from domain.i18n import ErrorCodes
from domain.common import Result, VASValidationError
from infrastructure.models.payroll_models import (
    EmployeeModel, EmployeeContractModel, EmployeeDependentModel,
    TimesheetModel, PayrollRunModel, PayrollLineModel,
    PayrollAdjustmentModel, PITDeclarationModel, SIInsuranceRecordModel,
    SalaryPaymentModel, PayrollCostAllocationModel, PayrollAuditLogModel,
)


class PayrollRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Employee mappings ──────────────────────────────────────────

    def _employee_to_domain(self, m: EmployeeModel) -> Employee:
        e = Employee(
            employee_code=m.employee_code,
            full_name=m.full_name,
            date_of_birth=m.date_of_birth,
            gender=m.gender,
            id_number=m.id_number,
            id_issue_date=m.id_issue_date,
            id_issue_place=m.id_issue_place,
            tax_code=m.tax_code,
            si_book_number=m.si_book_number,
            bank_account=m.bank_account,
            bank_name=m.bank_name,
            department_id=m.department_id,
            department_name=m.department_name,
            position=m.position,
            region=Region(m.region) if m.region else Region.REGION_1,
            dependent_count=m.dependent_count or 0,
            status=EmployeeStatus(m.status) if m.status else EmployeeStatus.ACTIVE,
            start_date=m.start_date,
            termination_date=m.termination_date,
            created_at=m.created_at,
            updated_at=m.updated_at,
            created_by=m.created_by,
            updated_by=m.updated_by,
        )
        e.id = m.id
        return e

    def _employee_to_model(self, d: Employee) -> EmployeeModel:
        return EmployeeModel(
            employee_code=d.employee_code,
            full_name=d.full_name,
            date_of_birth=d.date_of_birth,
            gender=d.gender,
            id_number=d.id_number,
            id_issue_date=d.id_issue_date,
            id_issue_place=d.id_issue_place,
            tax_code=d.tax_code,
            si_book_number=d.si_book_number,
            bank_account=d.bank_account,
            bank_name=d.bank_name,
            department_id=d.department_id,
            department_name=d.department_name,
            position=d.position,
            region=d.region.value,
            dependent_count=d.dependent_count,
            status=d.status.value,
            start_date=d.start_date,
            termination_date=d.termination_date,
            created_at=d.created_at,
            updated_at=d.updated_at,
            created_by=d.created_by,
            updated_by=d.updated_by,
        )

    # ── Employee CRUD ──────────────────────────────────────────────

    def create_employee(self, employee: Employee) -> Result:
        existing_code = self.session.execute(
            select(EmployeeModel).where(EmployeeModel.employee_code == employee.employee_code)
        ).scalar_one_or_none()
        if existing_code:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_CODE_DUPLICATE, code=employee.employee_code,
            ))
        if employee.si_book_number:
            existing_si = self.session.execute(
                select(EmployeeModel).where(EmployeeModel.si_book_number == employee.si_book_number)
            ).scalar_one_or_none()
            if existing_si:
                return Result.failure(VASValidationError(
                    ErrorCodes.PR_SI_BOOK_DUPLICATE, si_book=employee.si_book_number,
                ))
        try:
            model = self._employee_to_model(employee)
            self.session.add(model)
            self.session.flush()
            return Result.success(self._employee_to_domain(model))
        except IntegrityError:
            self.session.rollback()
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_CODE_DUPLICATE, code=employee.employee_code,
            ))

    def get_employee(self, employee_id: int) -> Result:
        m = self.session.get(EmployeeModel, employee_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee_id),
            ))
        return Result.success(self._employee_to_domain(m))

    def get_employee_by_code(self, code: str) -> Result:
        m = self.session.execute(
            select(EmployeeModel).where(EmployeeModel.employee_code == code)
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=code,
            ))
        return Result.success(self._employee_to_domain(m))

    def update_employee(self, employee: Employee) -> Result:
        m = self.session.get(EmployeeModel, employee.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee.id),
            ))
        m.employee_code = employee.employee_code
        m.full_name = employee.full_name
        m.date_of_birth = employee.date_of_birth
        m.gender = employee.gender
        m.id_number = employee.id_number
        m.id_issue_date = employee.id_issue_date
        m.id_issue_place = employee.id_issue_place
        m.tax_code = employee.tax_code
        m.si_book_number = employee.si_book_number
        m.bank_account = employee.bank_account
        m.bank_name = employee.bank_name
        m.department_id = employee.department_id
        m.department_name = employee.department_name
        m.position = employee.position
        m.region = employee.region.value
        m.dependent_count = employee.dependent_count
        m.status = employee.status.value
        m.start_date = employee.start_date
        m.termination_date = employee.termination_date
        m.updated_by = employee.updated_by
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._employee_to_domain(m))

    def delete_employee(self, employee_id: int) -> Result:
        m = self.session.get(EmployeeModel, employee_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee_id),
            ))
        m.status = EmployeeStatus.TERMINATED.value
        m.termination_date = date.today()
        self.session.flush()
        return Result.success(None)

    def list_employees(self, filters: dict = None, page: int = 1, per_page: int = 20) -> Result:
        f = filters or {}
        stmt = select(EmployeeModel)
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(EmployeeModel.status == status_val)
        dept_id = f.get("department_id")
        if dept_id is not None:
            stmt = stmt.where(EmployeeModel.department_id == dept_id)
        search = f.get("search")
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    EmployeeModel.employee_code.ilike(pattern),
                    EmployeeModel.full_name.ilike(pattern),
                    EmployeeModel.tax_code.ilike(pattern),
                )
            )
        total = self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()
        stmt = stmt.order_by(EmployeeModel.employee_code)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        models = self.session.execute(stmt).scalars().all()
        return Result.success({
            "items": [self._employee_to_domain(m) for m in models],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": ceil(total / per_page) if total else 0,
        })

    # ── Contract mappings ──────────────────────────────────────────

    def _contract_to_domain(self, m: EmployeeContractModel) -> EmployeeContract:
        c = EmployeeContract(
            employee_id=m.employee_id,
            contract_type=ContractType(m.contract_type),
            start_date=m.start_date,
            end_date=m.end_date,
            base_salary=m.base_salary or Decimal("0"),
            position_allowance=m.position_allowance or Decimal("0"),
            meal_allowance=m.meal_allowance or Decimal("0"),
            phone_allowance=m.phone_allowance or Decimal("0"),
            transport_allowance=m.transport_allowance or Decimal("0"),
            housing_allowance=m.housing_allowance or Decimal("0"),
            responsibility_allowance=m.responsibility_allowance or Decimal("0"),
            other_allowance=m.other_allowance or Decimal("0"),
            is_active=m.is_active if m.is_active is not None else True,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
        )
        c.id = m.id
        return c

    def _contract_to_model(self, d: EmployeeContract) -> EmployeeContractModel:
        return EmployeeContractModel(
            employee_id=d.employee_id,
            contract_type=d.contract_type.value,
            start_date=d.start_date,
            end_date=d.end_date,
            base_salary=d.base_salary,
            position_allowance=d.position_allowance,
            meal_allowance=d.meal_allowance,
            phone_allowance=d.phone_allowance,
            transport_allowance=d.transport_allowance,
            housing_allowance=d.housing_allowance,
            responsibility_allowance=d.responsibility_allowance,
            other_allowance=d.other_allowance,
            is_active=d.is_active,
        )

    # ── Contract CRUD ──────────────────────────────────────────────

    def create_contract(self, contract: EmployeeContract) -> Result:
        if contract.is_active:
            existing_active = self.session.execute(
                select(EmployeeContractModel).where(
                    EmployeeContractModel.employee_id == contract.employee_id,
                    EmployeeContractModel.is_active.is_(True),
                )
            ).scalar_one_or_none()
            if existing_active:
                return Result.failure(VASValidationError(
                    ErrorCodes.PR_ACTIVE_CONTRACT_EXISTS,
                    employee_id=str(contract.employee_id),
                ))
        model = self._contract_to_model(contract)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._contract_to_domain(model))

    def get_contract(self, contract_id: int) -> Result:
        m = self.session.get(EmployeeContractModel, contract_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract_id),
            ))
        return Result.success(self._contract_to_domain(m))

    def get_active_contract(self, employee_id: int) -> Result:
        m = self.session.execute(
            select(EmployeeContractModel).where(
                EmployeeContractModel.employee_id == employee_id,
                EmployeeContractModel.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND,
                id=f"active_contract_{employee_id}",
            ))
        return Result.success(self._contract_to_domain(m))

    def list_employee_contracts(self, employee_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeContractModel)
            .where(EmployeeContractModel.employee_id == employee_id)
            .order_by(desc(EmployeeContractModel.start_date))
        ).scalars().all()
        return Result.success([self._contract_to_domain(m) for m in models])

    def update_contract(self, contract: EmployeeContract) -> Result:
        m = self.session.get(EmployeeContractModel, contract.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract.id),
            ))
        m.contract_type = contract.contract_type.value
        m.start_date = contract.start_date
        m.end_date = contract.end_date
        m.base_salary = contract.base_salary
        m.position_allowance = contract.position_allowance
        m.meal_allowance = contract.meal_allowance
        m.phone_allowance = contract.phone_allowance
        m.transport_allowance = contract.transport_allowance
        m.housing_allowance = contract.housing_allowance
        m.responsibility_allowance = contract.responsibility_allowance
        m.other_allowance = contract.other_allowance
        m.is_active = contract.is_active
        self.session.flush()
        return Result.success(self._contract_to_domain(m))

    def terminate_contract(self, contract_id: int) -> Result:
        m = self.session.get(EmployeeContractModel, contract_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract_id),
            ))
        m.is_active = False
        self.session.flush()
        return Result.success(self._contract_to_domain(m))

    # ── Dependent mappings ─────────────────────────────────────────

    def _dependent_to_domain(self, m: EmployeeDependentModel) -> EmployeeDependent:
        d = EmployeeDependent(
            employee_id=m.employee_id,
            full_name=m.full_name,
            relationship=m.relationship_type,
            date_of_birth=m.date_of_birth,
            tax_code=m.tax_code,
            from_date=m.from_date,
            to_date=m.to_date,
            is_active=m.is_active if m.is_active is not None else True,
        )
        d.id = m.id
        return d

    def _dependent_to_model(self, d: EmployeeDependent) -> EmployeeDependentModel:
        return EmployeeDependentModel(
            employee_id=d.employee_id,
            full_name=d.full_name,
            relationship_type=d.relationship,
            date_of_birth=d.date_of_birth,
            tax_code=d.tax_code,
            from_date=d.from_date,
            to_date=d.to_date,
            is_active=d.is_active,
        )

    # ── Dependent CRUD ─────────────────────────────────────────────

    def create_dependent(self, dependent: EmployeeDependent) -> Result:
        model = self._dependent_to_model(dependent)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._dependent_to_domain(model))

    def list_employee_dependents(self, employee_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeDependentModel)
            .where(EmployeeDependentModel.employee_id == employee_id)
            .order_by(EmployeeDependentModel.full_name)
        ).scalars().all()
        return Result.success([self._dependent_to_domain(m) for m in models])

    def update_dependent(self, dependent: EmployeeDependent) -> Result:
        m = self.session.get(EmployeeDependentModel, dependent.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_DEPENDENT_INVALID, id=str(dependent.id),
            ))
        m.full_name = dependent.full_name
        m.relationship_type = dependent.relationship
        m.date_of_birth = dependent.date_of_birth
        m.tax_code = dependent.tax_code
        m.from_date = dependent.from_date
        m.to_date = dependent.to_date
        m.is_active = dependent.is_active
        self.session.flush()
        return Result.success(self._dependent_to_domain(m))

    def deactivate_dependent(self, dependent_id: int) -> Result:
        m = self.session.get(EmployeeDependentModel, dependent_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_DEPENDENT_INVALID, id=str(dependent_id),
            ))
        m.is_active = False
        self.session.flush()
        return Result.success(None)

    # ── Timesheet mappings ─────────────────────────────────────────

    def _timesheet_to_domain(self, m: TimesheetModel) -> Timesheet:
        t = Timesheet(
            employee_id=m.employee_id,
            period_month=m.period_month,
            period_year=m.period_year,
            working_days=m.working_days or Decimal("0"),
            standard_days=m.standard_days or Decimal("26"),
            overtime_weekday_hours=m.overtime_weekday_hours or Decimal("0"),
            overtime_weekend_hours=m.overtime_weekend_hours or Decimal("0"),
            overtime_holiday_hours=m.overtime_holiday_hours or Decimal("0"),
            sick_leave_days=m.sick_leave_days or Decimal("0"),
            unpaid_leave_days=m.unpaid_leave_days or Decimal("0"),
            paid_leave_days=m.paid_leave_days or Decimal("0"),
            notes=m.notes,
            created_at=m.created_at,
        )
        t.id = m.id
        return t

    def _timesheet_to_model(self, d: Timesheet) -> TimesheetModel:
        return TimesheetModel(
            employee_id=d.employee_id,
            period_month=d.period_month,
            period_year=d.period_year,
            working_days=d.working_days,
            standard_days=d.standard_days,
            overtime_weekday_hours=d.overtime_weekday_hours,
            overtime_weekend_hours=d.overtime_weekend_hours,
            overtime_holiday_hours=d.overtime_holiday_hours,
            sick_leave_days=d.sick_leave_days,
            unpaid_leave_days=d.unpaid_leave_days,
            paid_leave_days=d.paid_leave_days,
            notes=d.notes,
        )

    # ── Timesheet CRUD ─────────────────────────────────────────────

    def upsert_timesheet(self, timesheet: Timesheet) -> Result:
        existing = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.employee_id == timesheet.employee_id,
                TimesheetModel.period_month == timesheet.period_month,
                TimesheetModel.period_year == timesheet.period_year,
            )
        ).scalar_one_or_none()
        if existing:
            existing.working_days = timesheet.working_days
            existing.standard_days = timesheet.standard_days
            existing.overtime_weekday_hours = timesheet.overtime_weekday_hours
            existing.overtime_weekend_hours = timesheet.overtime_weekend_hours
            existing.overtime_holiday_hours = timesheet.overtime_holiday_hours
            existing.sick_leave_days = timesheet.sick_leave_days
            existing.unpaid_leave_days = timesheet.unpaid_leave_days
            existing.paid_leave_days = timesheet.paid_leave_days
            existing.notes = timesheet.notes
            self.session.flush()
            return Result.success(self._timesheet_to_domain(existing))
        model = self._timesheet_to_model(timesheet)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._timesheet_to_domain(model))

    def get_timesheet(self, timesheet_id: int) -> Result:
        m = self.session.get(TimesheetModel, timesheet_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_TIMESHEET_EMPLOYEE_NOT_FOUND, id=str(timesheet_id),
            ))
        return Result.success(self._timesheet_to_domain(m))

    def get_employee_timesheet(self, employee_id: int, month: int, year: int) -> Result:
        m = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.employee_id == employee_id,
                TimesheetModel.period_month == month,
                TimesheetModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_TIMESHEET_MISSING,
                employee_id=str(employee_id),
                period=f"{month}/{year}",
            ))
        return Result.success(self._timesheet_to_domain(m))

    def list_period_timesheets(self, month: int, year: int) -> Result:
        models = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.period_month == month,
                TimesheetModel.period_year == year,
            )
        ).scalars().all()
        return Result.success([self._timesheet_to_domain(m) for m in models])

    # ── PayrollLine mappings ───────────────────────────────────────

    def _payroll_line_to_domain(self, m: PayrollLineModel) -> PayrollLine:
        pl = PayrollLine(
            payroll_run_id=m.payroll_run_id,
            employee_id=m.employee_id,
            employee_code=m.employee_code,
            employee_name=m.employee_name,
            base_salary=m.base_salary or Decimal("0"),
            working_days=m.working_days or Decimal("0"),
            standard_days=m.standard_days or Decimal("26"),
            prorated_salary=m.prorated_salary or Decimal("0"),
            overtime_amount=m.overtime_amount or Decimal("0"),
            allowances_total=m.allowances_total or Decimal("0"),
            bonus_amount=m.bonus_amount or Decimal("0"),
            gross_salary=m.gross_salary or Decimal("0"),
            si_base_salary=m.si_base_salary or Decimal("0"),
            employee_si=m.employee_si or Decimal("0"),
            employee_hi=m.employee_hi or Decimal("0"),
            employee_ui=m.employee_ui or Decimal("0"),
            advance_deduction=m.advance_deduction or Decimal("0"),
            other_deductions=m.other_deductions or Decimal("0"),
            exempt_income=m.exempt_income or Decimal("0"),
            personal_relief=m.personal_relief or Decimal("15500000"),
            dependent_relief=m.dependent_relief or Decimal("0"),
            additional_deductions=m.additional_deductions or Decimal("0"),
            taxable_income=m.taxable_income or Decimal("0"),
            pit_amount=m.pit_amount or Decimal("0"),
            net_pay=m.net_pay or Decimal("0"),
            employer_si=m.employer_si or Decimal("0"),
            employer_hi=m.employer_hi or Decimal("0"),
            employer_ui=m.employer_ui or Decimal("0"),
            employer_occ=m.employer_occ or Decimal("0"),
            kpcd=m.kpcd or Decimal("0"),
            payment_method=PaymentMethodPR(m.payment_method) if m.payment_method else PaymentMethodPR.BANK_TRANSFER,
            payment_status=PaymentStatus(m.payment_status) if m.payment_status else PaymentStatus.PENDING,
            payment_date=m.payment_date,
            bank_transaction_ref=m.bank_transaction_ref,
            notes=m.notes,
        )
        pl.id = m.id
        return pl

    def _payroll_line_to_model(self, d: PayrollLine, payroll_run_id: int) -> PayrollLineModel:
        return PayrollLineModel(
            payroll_run_id=payroll_run_id,
            employee_id=d.employee_id,
            employee_code=d.employee_code,
            employee_name=d.employee_name,
            base_salary=d.base_salary,
            working_days=d.working_days,
            standard_days=d.standard_days,
            prorated_salary=d.prorated_salary,
            overtime_amount=d.overtime_amount,
            allowances_total=d.allowances_total,
            bonus_amount=d.bonus_amount,
            gross_salary=d.gross_salary,
            si_base_salary=d.si_base_salary,
            employee_si=d.employee_si,
            employee_hi=d.employee_hi,
            employee_ui=d.employee_ui,
            advance_deduction=d.advance_deduction,
            other_deductions=d.other_deductions,
            exempt_income=d.exempt_income,
            personal_relief=d.personal_relief,
            dependent_relief=d.dependent_relief,
            additional_deductions=d.additional_deductions,
            taxable_income=d.taxable_income,
            pit_amount=d.pit_amount,
            net_pay=d.net_pay,
            employer_si=d.employer_si,
            employer_hi=d.employer_hi,
            employer_ui=d.employer_ui,
            employer_occ=d.employer_occ,
            kpcd=d.kpcd,
            payment_method=d.payment_method.value,
            payment_status=d.payment_status.value,
            payment_date=d.payment_date,
            bank_transaction_ref=d.bank_transaction_ref,
            notes=d.notes,
        )

    # ── PayrollRun mappings ────────────────────────────────────────

    def _payroll_run_to_domain(self, m: PayrollRunModel) -> PayrollRun:
        run = PayrollRun(
            period_month=m.period_month,
            period_year=m.period_year,
            status=PayrollRunStatus(m.status) if m.status else PayrollRunStatus.DRAFT,
            lines=[self._payroll_line_to_domain(l) for l in m.lines],
            total_gross=m.total_gross or Decimal("0"),
            total_employee_si=m.total_employee_si or Decimal("0"),
            total_employee_hi=m.total_employee_hi or Decimal("0"),
            total_employee_ui=m.total_employee_ui or Decimal("0"),
            total_pit=m.total_pit or Decimal("0"),
            total_advances=m.total_advances or Decimal("0"),
            total_other_deductions=m.total_other_deductions or Decimal("0"),
            total_net=m.total_net or Decimal("0"),
            total_employer_si=m.total_employer_si or Decimal("0"),
            total_employer_hi=m.total_employer_hi or Decimal("0"),
            total_employer_ui=m.total_employer_ui or Decimal("0"),
            total_employer_occ=m.total_employer_occ or Decimal("0"),
            total_kpcd=m.total_kpcd or Decimal("0"),
            computed_at=m.computed_at,
            approved_at=m.approved_at,
            approved_by=m.approved_by,
            paid_at=m.paid_at,
            notes=m.notes,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        run.id = m.id
        return run

    def _payroll_run_to_model(self, d: PayrollRun) -> PayrollRunModel:
        return PayrollRunModel(
            period_month=d.period_month,
            period_year=d.period_year,
            status=d.status.value,
            total_gross=d.total_gross,
            total_employee_si=d.total_employee_si,
            total_employee_hi=d.total_employee_hi,
            total_employee_ui=d.total_employee_ui,
            total_pit=d.total_pit,
            total_advances=d.total_advances,
            total_other_deductions=d.total_other_deductions,
            total_net=d.total_net,
            total_employer_si=d.total_employer_si,
            total_employer_hi=d.total_employer_hi,
            total_employer_ui=d.total_employer_ui,
            total_employer_occ=d.total_employer_occ,
            total_kpcd=d.total_kpcd,
            computed_at=d.computed_at,
            approved_at=d.approved_at,
            approved_by=d.approved_by,
            paid_at=d.paid_at,
            notes=d.notes,
            created_by=d.created_by,
        )

    # ── PayrollRun CRUD ────────────────────────────────────────────

    def create_payroll_run(self, run: PayrollRun) -> Result:
        existing = self.session.execute(
            select(PayrollRunModel).where(
                PayrollRunModel.period_month == run.period_month,
                PayrollRunModel.period_year == run.period_year,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_ALREADY_EXISTS,
                period=f"{run.period_month}/{run.period_year}",
            ))
        model = self._payroll_run_to_model(run)
        self.session.add(model)
        self.session.flush()
        for line in run.lines:
            line_model = self._payroll_line_to_model(line, model.id)
            self.session.add(line_model)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(model))

    def get_payroll_run(self, run_id: int) -> Result:
        m = self.session.get(PayrollRunModel, run_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run_id),
            ))
        return Result.success(self._payroll_run_to_domain(m))

    def get_payroll_run_by_period(self, month: int, year: int) -> Result:
        m = self.session.execute(
            select(PayrollRunModel).where(
                PayrollRunModel.period_month == month,
                PayrollRunModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND,
                period=f"{month}/{year}",
            ))
        return Result.success(self._payroll_run_to_domain(m))

    def list_payroll_runs(self, filters: dict = None) -> Result:
        f = filters or {}
        stmt = select(PayrollRunModel).order_by(
            desc(PayrollRunModel.period_year),
            desc(PayrollRunModel.period_month),
        )
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(PayrollRunModel.status == status_val)
        year_val = f.get("period_year")
        if year_val is not None:
            stmt = stmt.where(PayrollRunModel.period_year == year_val)
        month_val = f.get("period_month")
        if month_val is not None:
            stmt = stmt.where(PayrollRunModel.period_month == month_val)
        models = self.session.execute(stmt).scalars().all()
        return Result.success([self._payroll_run_to_domain(m) for m in models])

    def update_payroll_run_status(self, run_id: int, status: str, **extra) -> Result:
        m = self.session.get(PayrollRunModel, run_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run_id),
            ))
        m.status = status
        allowed_extra = {
            "computed_at", "approved_at", "approved_by",
            "paid_at", "notes", "total_gross", "total_employee_si",
            "total_employee_hi", "total_employee_ui", "total_pit",
            "total_advances", "total_other_deductions", "total_net",
            "total_employer_si", "total_employer_hi", "total_employer_ui",
            "total_employer_occ", "total_kpcd",
        }
        for k, v in extra.items():
            if k in allowed_extra:
                setattr(m, k, v)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(m))

    def save_payroll_lines(self, run_id: int, lines: List[PayrollLine]) -> Result:
        existing = self.session.execute(
            select(PayrollLineModel).where(PayrollLineModel.payroll_run_id == run_id)
        ).scalars().all()
        for line in existing:
            self.session.delete(line)
        self.session.flush()
        for line in lines:
            model = self._payroll_line_to_model(line, run_id)
            self.session.add(model)
        self.session.flush()
        return Result.success(None)

    # ── PayrollAdjustment mappings ─────────────────────────────────

    def _adjustment_to_domain(self, m: PayrollAdjustmentModel) -> PayrollAdjustment:
        a = PayrollAdjustment(
            payroll_run_id=m.payroll_run_id,
            employee_id=m.employee_id,
            adjustment_type=AdjustmentType(m.adjustment_type),
            amount=m.amount or Decimal("0"),
            delta_gross=m.delta_gross or Decimal("0"),
            delta_si_base=m.delta_si_base or Decimal("0"),
            delta_pit=m.delta_pit or Decimal("0"),
            delta_net=m.delta_net or Decimal("0"),
            reason=m.reason,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            status=PayrollRunStatus(m.status) if m.status else PayrollRunStatus.DRAFT,
            created_at=m.created_at,
            created_by=m.created_by,
        )
        a.id = m.id
        return a

    def _adjustment_to_model(self, d: PayrollAdjustment) -> PayrollAdjustmentModel:
        return PayrollAdjustmentModel(
            payroll_run_id=d.payroll_run_id,
            employee_id=d.employee_id,
            adjustment_type=d.adjustment_type.value,
            amount=d.amount,
            delta_gross=d.delta_gross,
            delta_si_base=d.delta_si_base,
            delta_pit=d.delta_pit,
            delta_net=d.delta_net,
            reason=d.reason,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
            status=d.status.value,
            created_by=d.created_by,
        )

    # ── PayrollAdjustment CRUD ─────────────────────────────────────

    def create_adjustment(self, adj: PayrollAdjustment) -> Result:
        model = self._adjustment_to_model(adj)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._adjustment_to_domain(model))

    def get_adjustment(self, adj_id: int) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj_id),
            ))
        return Result.success(self._adjustment_to_domain(m))

    def update_adjustment(self, adj: PayrollAdjustment) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj.id),
            ))
        m.adjustment_type = adj.adjustment_type.value
        m.amount = adj.amount
        m.delta_gross = adj.delta_gross
        m.delta_si_base = adj.delta_si_base
        m.delta_pit = adj.delta_pit
        m.delta_net = adj.delta_net
        m.reason = adj.reason
        m.approved_by = adj.approved_by
        m.approved_at = adj.approved_at
        m.status = adj.status.value
        self.session.flush()
        return Result.success(self._adjustment_to_domain(m))

    def list_run_adjustments(self, run_id: int) -> Result:
        models = self.session.execute(
            select(PayrollAdjustmentModel)
            .where(PayrollAdjustmentModel.payroll_run_id == run_id)
            .order_by(PayrollAdjustmentModel.created_at)
        ).scalars().all()
        return Result.success([self._adjustment_to_domain(m) for m in models])

    def approve_adjustment(self, adj_id: int, approved_by: str) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj_id),
            ))
        m.status = PayrollRunStatus.APPROVED.value
        m.approved_by = approved_by
        m.approved_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._adjustment_to_domain(m))

    # ── PITDeclaration mappings ────────────────────────────────────

    def _pit_declaration_to_domain(self, m: PITDeclarationModel) -> PITDeclaration:
        d = PITDeclaration(
            declaration_type=DeclarationType(m.declaration_type),
            period_month=m.period_month,
            period_quarter=m.period_quarter,
            period_year=m.period_year,
            submission_type=m.submission_type or "initial",
            status=DeclarationStatus(m.status) if m.status else DeclarationStatus.DRAFT,
            total_income=m.total_income or Decimal("0"),
            total_exempt_income=m.total_exempt_income or Decimal("0"),
            total_deductions=m.total_deductions or Decimal("0"),
            total_personal_relief=m.total_personal_relief or Decimal("0"),
            total_dependent_relief=m.total_dependent_relief or Decimal("0"),
            total_taxable_income=m.total_taxable_income or Decimal("0"),
            total_pit=m.total_pit or Decimal("0"),
            total_pit_withheld=m.total_pit_withheld or Decimal("0"),
            total_pit_paid=m.total_pit_paid or Decimal("0"),
            submission_date=m.submission_date,
            tax_authority_response=m.tax_authority_response,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        d.id = m.id
        return d

    def _pit_declaration_to_model(self, d: PITDeclaration) -> PITDeclarationModel:
        return PITDeclarationModel(
            declaration_type=d.declaration_type.value,
            period_month=d.period_month,
            period_quarter=d.period_quarter,
            period_year=d.period_year,
            submission_type=d.submission_type,
            status=d.status.value,
            total_income=d.total_income,
            total_exempt_income=d.total_exempt_income,
            total_deductions=d.total_deductions,
            total_personal_relief=d.total_personal_relief,
            total_dependent_relief=d.total_dependent_relief,
            total_taxable_income=d.total_taxable_income,
            total_pit=d.total_pit,
            total_pit_withheld=d.total_pit_withheld,
            total_pit_paid=d.total_pit_paid,
            submission_date=d.submission_date,
            tax_authority_response=d.tax_authority_response,
            created_by=d.created_by,
        )

    # ── PITDeclaration CRUD ────────────────────────────────────────

    def create_pit_declaration(self, decl: PITDeclaration) -> Result:
        model = self._pit_declaration_to_model(decl)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._pit_declaration_to_domain(model))

    def get_pit_declaration(self, decl_id: int) -> Result:
        m = self.session.get(PITDeclarationModel, decl_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PIT_DECLARATION_NOT_FOUND, id=str(decl_id),
            ))
        return Result.success(self._pit_declaration_to_domain(m))

    def update_pit_declaration(self, decl: PITDeclaration) -> Result:
        m = self.session.get(PITDeclarationModel, decl.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PIT_DECLARATION_NOT_FOUND, id=str(decl.id),
            ))
        m.declaration_type = decl.declaration_type.value
        m.period_month = decl.period_month
        m.period_quarter = decl.period_quarter
        m.period_year = decl.period_year
        m.submission_type = decl.submission_type
        m.status = decl.status.value
        m.total_income = decl.total_income
        m.total_exempt_income = decl.total_exempt_income
        m.total_deductions = decl.total_deductions
        m.total_personal_relief = decl.total_personal_relief
        m.total_dependent_relief = decl.total_dependent_relief
        m.total_taxable_income = decl.total_taxable_income
        m.total_pit = decl.total_pit
        m.total_pit_withheld = decl.total_pit_withheld
        m.total_pit_paid = decl.total_pit_paid
        m.submission_date = decl.submission_date
        m.tax_authority_response = decl.tax_authority_response
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._pit_declaration_to_domain(m))

    def list_pit_declarations(self, filters: dict = None) -> Result:
        f = filters or {}
        stmt = select(PITDeclarationModel).order_by(desc(PITDeclarationModel.created_at))
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(PITDeclarationModel.status == status_val)
        year_val = f.get("period_year")
        if year_val is not None:
            stmt = stmt.where(PITDeclarationModel.period_year == year_val)
        decl_type = f.get("declaration_type")
        if decl_type:
            stmt = stmt.where(PITDeclarationModel.declaration_type == decl_type)
        models = self.session.execute(stmt).scalars().all()
        return Result.success([self._pit_declaration_to_domain(m) for m in models])

    # ── SIInsuranceRecord mappings ─────────────────────────────────

    def _si_record_to_domain(self, m: SIInsuranceRecordModel) -> SIInsuranceRecord:
        r = SIInsuranceRecord(
            payroll_run_id=m.payroll_run_id,
            period_month=m.period_month,
            period_year=m.period_year,
            status=DeclarationStatus(m.status) if m.status else DeclarationStatus.DRAFT,
            total_si_base=m.total_si_base or Decimal("0"),
            total_employee_si=m.total_employee_si or Decimal("0"),
            total_employee_hi=m.total_employee_hi or Decimal("0"),
            total_employee_ui=m.total_employee_ui or Decimal("0"),
            total_employer_si=m.total_employer_si or Decimal("0"),
            total_employer_hi=m.total_employer_hi or Decimal("0"),
            total_employer_ui=m.total_employer_ui or Decimal("0"),
            total_employer_occ=m.total_employer_occ or Decimal("0"),
            total_kpcd=m.total_kpcd or Decimal("0"),
            total_payable=m.total_payable or Decimal("0"),
            submission_date=m.submission_date,
            confirmation_ref=m.confirmation_ref,
            payment_date=m.payment_date,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        r.id = m.id
        return r

    def _si_record_to_model(self, d: SIInsuranceRecord) -> SIInsuranceRecordModel:
        return SIInsuranceRecordModel(
            payroll_run_id=d.payroll_run_id,
            period_month=d.period_month,
            period_year=d.period_year,
            status=d.status.value,
            total_si_base=d.total_si_base,
            total_employee_si=d.total_employee_si,
            total_employee_hi=d.total_employee_hi,
            total_employee_ui=d.total_employee_ui,
            total_employer_si=d.total_employer_si,
            total_employer_hi=d.total_employer_hi,
            total_employer_ui=d.total_employer_ui,
            total_employer_occ=d.total_employer_occ,
            total_kpcd=d.total_kpcd,
            total_payable=d.total_payable,
            submission_date=d.submission_date,
            confirmation_ref=d.confirmation_ref,
            payment_date=d.payment_date,
            created_by=d.created_by,
        )

    # ── SI Record CRUD ─────────────────────────────────────────────

    def create_si_record(self, record: SIInsuranceRecord) -> Result:
        model = self._si_record_to_model(record)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._si_record_to_domain(model))

    def get_si_record(self, record_id: int) -> Result:
        m = self.session.get(SIInsuranceRecordModel, record_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, id=str(record_id),
            ))
        return Result.success(self._si_record_to_domain(m))

    def update_si_record(self, record: SIInsuranceRecord) -> Result:
        m = self.session.get(SIInsuranceRecordModel, record.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, id=str(record.id),
            ))
        m.period_month = record.period_month
        m.period_year = record.period_year
        m.status = record.status.value
        m.total_si_base = record.total_si_base
        m.total_employee_si = record.total_employee_si
        m.total_employee_hi = record.total_employee_hi
        m.total_employee_ui = record.total_employee_ui
        m.total_employer_si = record.total_employer_si
        m.total_employer_hi = record.total_employer_hi
        m.total_employer_ui = record.total_employer_ui
        m.total_employer_occ = record.total_employer_occ
        m.total_kpcd = record.total_kpcd
        m.total_payable = record.total_payable
        m.submission_date = record.submission_date
        m.confirmation_ref = record.confirmation_ref
        m.payment_date = record.payment_date
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._si_record_to_domain(m))

    def get_si_record_by_period(self, month: int, year: int) -> Result:
        m = self.session.execute(
            select(SIInsuranceRecordModel).where(
                SIInsuranceRecordModel.period_month == month,
                SIInsuranceRecordModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, period=f"{month}/{year}",
            ))
        return Result.success(self._si_record_to_domain(m))

    # ── SalaryPayment mappings ─────────────────────────────────────

    def _salary_payment_to_domain(self, m: SalaryPaymentModel) -> SalaryPayment:
        p = SalaryPayment(
            payroll_run_id=m.payroll_run_id,
            payment_date=m.payment_date,
            payment_method=PaymentMethodPR(m.payment_method),
            total_amount=m.total_amount or Decimal("0"),
            bank_transaction_ref=m.bank_transaction_ref,
            notes=m.notes,
            created_at=m.created_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        p.id = m.id
        return p

    def _salary_payment_to_model(self, d: SalaryPayment) -> SalaryPaymentModel:
        return SalaryPaymentModel(
            payroll_run_id=d.payroll_run_id,
            payment_date=d.payment_date,
            payment_method=d.payment_method.value,
            total_amount=d.total_amount,
            bank_transaction_ref=d.bank_transaction_ref,
            notes=d.notes,
            created_by=d.created_by,
        )

    # ── SalaryPayment CRUD ─────────────────────────────────────────

    def create_salary_payment(self, payment: SalaryPayment) -> Result:
        model = self._salary_payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._salary_payment_to_domain(model))

    def get_run_payments(self, run_id: int) -> Result:
        models = self.session.execute(
            select(SalaryPaymentModel)
            .where(SalaryPaymentModel.payroll_run_id == run_id)
            .order_by(SalaryPaymentModel.payment_date)
        ).scalars().all()
        return Result.success([self._salary_payment_to_domain(m) for m in models])

    # ── PayrollCostAllocation mappings ─────────────────────────────

    def _cost_allocation_to_domain(self, m: PayrollCostAllocationModel) -> PayrollCostAllocation:
        a = PayrollCostAllocation(
            payroll_run_id=m.payroll_run_id,
            cost_center=CostCenter(m.cost_center),
            total_salary_cost=m.total_salary_cost or Decimal("0"),
            total_employer_cost=m.total_employer_cost or Decimal("0"),
            total_cost=m.total_cost or Decimal("0"),
            gl_journal_entry_ref=m.gl_journal_entry_ref,
            created_at=m.created_at or datetime.now(timezone.utc),
        )
        a.id = m.id
        return a

    def _cost_allocation_to_model(self, d: PayrollCostAllocation) -> PayrollCostAllocationModel:
        return PayrollCostAllocationModel(
            payroll_run_id=d.payroll_run_id,
            cost_center=d.cost_center.value,
            total_salary_cost=d.total_salary_cost,
            total_employer_cost=d.total_employer_cost,
            total_cost=d.total_cost,
            gl_journal_entry_ref=d.gl_journal_entry_ref,
        )

    # ── Cost Allocation CRUD ───────────────────────────────────────

    def create_cost_allocation(self, alloc: PayrollCostAllocation) -> Result:
        model = self._cost_allocation_to_model(alloc)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cost_allocation_to_domain(model))

    def get_run_cost_allocations(self, run_id: int) -> Result:
        models = self.session.execute(
            select(PayrollCostAllocationModel)
            .where(PayrollCostAllocationModel.payroll_run_id == run_id)
            .order_by(PayrollCostAllocationModel.cost_center)
        ).scalars().all()
        return Result.success([self._cost_allocation_to_domain(m) for m in models])

    # ── Audit Log ──────────────────────────────────────────────────

    def log_audit(
        self,
        payroll_run_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        action: str = "",
        old_value: dict = None,
        new_value: dict = None,
        changed_by: str = None,
    ) -> Result:
        model = PayrollAuditLogModel(
            payroll_run_id=payroll_run_id,
            employee_id=employee_id,
            action=action,
            old_value=old_value or {},
            new_value=new_value or {},
            changed_by=changed_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success({
            "id": model.id,
            "action": model.action,
            "changed_at": model.changed_at,
        })

    def get_audit_logs(
        self,
        payroll_run_id: int = None,
        employee_id: int = None,
    ) -> Result:
        stmt = select(PayrollAuditLogModel).order_by(desc(PayrollAuditLogModel.changed_at))
        if payroll_run_id is not None:
            stmt = stmt.where(PayrollAuditLogModel.payroll_run_id == payroll_run_id)
        if employee_id is not None:
            stmt = stmt.where(PayrollAuditLogModel.employee_id == employee_id)
        models = self.session.execute(stmt).scalars().all()
        result = []
        for m in models:
            result.append({
                "id": m.id,
                "payroll_run_id": m.payroll_run_id,
                "employee_id": m.employee_id,
                "action": m.action,
                "old_value": m.old_value,
                "new_value": m.new_value,
                "changed_by": m.changed_by,
                "changed_at": m.changed_at,
            })
        return Result.success(result)

    # ── Aliases used by PayrollUseCases ────────────────────────────

    def create_run(self, run: PayrollRun) -> Result:
        return self.create_payroll_run(run)

    def get_run(self, run_id: int) -> Result:
        return self.get_payroll_run(run_id)

    def get_run_by_period(self, month: int, year: int) -> Result:
        return self.get_payroll_run_by_period(month, year)

    def update_run(self, run: PayrollRun) -> Result:
        m = self.session.get(PayrollRunModel, run.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run.id),
            ))
        m.period_month = run.period_month
        m.period_year = run.period_year
        m.status = run.status.value
        m.total_gross = run.total_gross
        m.total_employee_si = run.total_employee_si
        m.total_employee_hi = run.total_employee_hi
        m.total_employee_ui = run.total_employee_ui
        m.total_pit = run.total_pit
        m.total_advances = run.total_advances
        m.total_other_deductions = run.total_other_deductions
        m.total_net = run.total_net
        m.total_employer_si = run.total_employer_si
        m.total_employer_hi = run.total_employer_hi
        m.total_employer_ui = run.total_employer_ui
        m.total_employer_occ = run.total_employer_occ
        m.total_kpcd = run.total_kpcd
        m.computed_at = run.computed_at
        m.approved_at = run.approved_at
        m.approved_by = run.approved_by
        m.paid_at = run.paid_at
        m.notes = run.notes
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(m))

    def list_runs(self, filters: dict = None) -> Result:
        return self.list_payroll_runs(filters)

    def get_employees_for_period(self, month: int, year: int) -> List[dict]:
        employees = self.list_employees(
            filters={"status": EmployeeStatus.ACTIVE.value},
            page=1, per_page=10000,
        )
        emp_list = []
        if employees.is_success():
            data = employees.get_data()
            if isinstance(data, dict):
                emp_list = data.get("items", [])
        result = []
        for emp in emp_list:
            contract_result = self.get_active_contract(emp.id)
            contract = contract_result.get_data() if contract_result.is_success() else None
            ts_result = self.get_employee_timesheet(emp.id, month, year)
            timesheet = ts_result.get_data() if ts_result.is_success() else None
            result.append({
                "employee": emp,
                "contract": contract,
                "timesheet": timesheet,
            })
        return result

    def update_lines_payment_status(self, run_id: int, status: PaymentStatus) -> None:
        models = self.session.execute(
            select(PayrollLineModel).where(PayrollLineModel.payroll_run_id == run_id)
        ).scalars().all()
        for m in models:
            m.payment_status = status.value
        self.session.flush()

    # ── Query helpers ──────────────────────────────────────────────

    def get_employees_by_department(self, department_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeModel)
            .where(EmployeeModel.department_id == department_id)
            .order_by(EmployeeModel.employee_code)
        ).scalars().all()
        return Result.success([self._employee_to_domain(m) for m in models])

    def count_employees_by_status(self, status: str) -> int:
        count = self.session.execute(
            select(func.count()).where(EmployeeModel.status == status)
        ).scalar_one()
        return count

    def get_total_salary_by_department(self, month: int, year: int) -> Result:
        stmt = (
            select(
                EmployeeModel.department_id,
                EmployeeModel.department_name,
                func.coalesce(func.sum(PayrollLineModel.gross_salary), Decimal("0")).label("total_gross"),
                func.coalesce(func.sum(PayrollLineModel.employer_si + PayrollLineModel.employer_hi + PayrollLineModel.employer_ui + PayrollLineModel.employer_occ + PayrollLineModel.kpcd), Decimal("0")).label("total_employer_cost"),
                func.coalesce(func.sum(PayrollLineModel.net_pay), Decimal("0")).label("total_net"),
                func.count(PayrollLineModel.id.distinct()).label("employee_count"),
            )
            .join(PayrollLineModel, EmployeeModel.id == PayrollLineModel.employee_id)
            .join(PayrollRunModel, PayrollLineModel.payroll_run_id == PayrollRunModel.id)
            .where(
                PayrollRunModel.period_month == month,
                PayrollRunModel.period_year == year,
                EmployeeModel.department_id.isnot(None),
            )
            .group_by(EmployeeModel.department_id, EmployeeModel.department_name)
            .order_by(EmployeeModel.department_id)
        )
        rows = self.session.execute(stmt).all()
        result = []
        for row in rows:
            result.append({
                "department_id": row.department_id,
                "department_name": row.department_name,
                "total_gross": row.total_gross,
                "total_employer_cost": row.total_employer_cost,
                "total_net": row.total_net,
                "employee_count": row.employee_count,
            })
        return Result.success(result)

    def search_employees(self, query: str) -> Result:
        pattern = f"%{query}%"
        models = self.session.execute(
            select(EmployeeModel).where(
                or_(
                    EmployeeModel.employee_code.ilike(pattern),
                    EmployeeModel.full_name.ilike(pattern),
                    EmployeeModel.tax_code.ilike(pattern),
                )
            ).order_by(EmployeeModel.employee_code).limit(50)
        ).scalars().all()
        return Result.success([self._employee_to_domain(m) for m in models])
