import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class EmployeeModel(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    id_number = Column(String(20), nullable=True)
    id_issue_date = Column(Date, nullable=True)
    id_issue_place = Column(String(100), nullable=True)
    tax_code = Column(String(20), nullable=True, index=True)
    si_book_number = Column(String(50), nullable=True, unique=True)
    bank_account = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    department_id = Column(Integer, nullable=True)
    department_name = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    region = Column(String(20), default="region_1")
    dependent_count = Column(Integer, default=0)
    status = Column(String(30), default="active")
    start_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

    contracts = relationship("EmployeeContractModel", back_populates="employee")
    dependents = relationship("EmployeeDependentModel", back_populates="employee")
    timesheets = relationship("TimesheetModel", back_populates="employee")
    payroll_lines = relationship("PayrollLineModel", back_populates="employee")
    adjustments = relationship("PayrollAdjustmentModel", back_populates="employee")

    def __repr__(self) -> str:
        return f"<EmployeeModel(id={self.id}, code='{self.employee_code}', name='{self.full_name}')>"


class EmployeeContractModel(Base):
    __tablename__ = "employee_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    contract_type = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    base_salary = Column(Numeric(18, 2), default=Decimal("0"))
    position_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    meal_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    phone_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    transport_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    housing_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    responsibility_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    other_allowance = Column(Numeric(18, 2), default=Decimal("0"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))

    employee = relationship("EmployeeModel", back_populates="contracts")

    def __repr__(self) -> str:
        return (
            f"<EmployeeContractModel(id={self.id}, employee_id={self.employee_id}, "
            f"type='{self.contract_type}')>"
        )


class EmployeeDependentModel(Base):
    __tablename__ = "employee_dependents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    tax_code = Column(String(20), nullable=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    employee = relationship("EmployeeModel", back_populates="dependents")

    def __repr__(self) -> str:
        return (
            f"<EmployeeDependentModel(id={self.id}, employee_id={self.employee_id}, "
            f"name='{self.full_name}', rel='{self.relationship_type}')>"
        )


class TimesheetModel(Base):
    __tablename__ = "timesheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    period_month = Column(Integer, nullable=False)
    period_year = Column(Integer, nullable=False)
    working_days = Column(Numeric(5, 1), default=Decimal("0"))
    standard_days = Column(Numeric(5, 1), default=Decimal("26"))
    overtime_weekday_hours = Column(Numeric(8, 1), default=Decimal("0"))
    overtime_weekend_hours = Column(Numeric(8, 1), default=Decimal("0"))
    overtime_holiday_hours = Column(Numeric(8, 1), default=Decimal("0"))
    sick_leave_days = Column(Numeric(5, 1), default=Decimal("0"))
    unpaid_leave_days = Column(Numeric(5, 1), default=Decimal("0"))
    paid_leave_days = Column(Numeric(5, 1), default=Decimal("0"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    employee = relationship("EmployeeModel", back_populates="timesheets")

    __table_args__ = (
        UniqueConstraint("employee_id", "period_month", "period_year", name="uq_timesheet_employee_period"),
    )

    def __repr__(self) -> str:
        return (
            f"<TimesheetModel(id={self.id}, employee_id={self.employee_id}, "
            f"period={self.period_month}/{self.period_year})>"
        )


class PayrollRunModel(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period_month = Column(Integer, nullable=False)
    period_year = Column(Integer, nullable=False)
    status = Column(String(30), default="draft")
    total_gross = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_si = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_hi = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_ui = Column(Numeric(18, 2), default=Decimal("0"))
    total_pit = Column(Numeric(18, 2), default=Decimal("0"))
    total_advances = Column(Numeric(18, 2), default=Decimal("0"))
    total_other_deductions = Column(Numeric(18, 2), default=Decimal("0"))
    total_net = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_si = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_hi = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_ui = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_occ = Column(Numeric(18, 2), default=Decimal("0"))
    total_kpcd = Column(Numeric(18, 2), default=Decimal("0"))
    computed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)

    lines = relationship("PayrollLineModel", back_populates="payroll_run", cascade="all, delete-orphan")
    adjustments = relationship("PayrollAdjustmentModel", back_populates="payroll_run", cascade="all, delete-orphan")
    salary_payments = relationship("SalaryPaymentModel", back_populates="payroll_run")
    cost_allocations = relationship("PayrollCostAllocationModel", back_populates="payroll_run", cascade="all, delete-orphan")
    audit_logs = relationship("PayrollAuditLogModel", back_populates="payroll_run", cascade="all, delete-orphan")
    si_insurance_records = relationship("SIInsuranceRecordModel", back_populates="payroll_run")

    __table_args__ = (
        UniqueConstraint("period_month", "period_year", name="uq_payroll_run_period"),
    )

    def __repr__(self) -> str:
        return (
            f"<PayrollRunModel(id={self.id}, period={self.period_month}/{self.period_year}, "
            f"status='{self.status}')>"
        )


class PayrollLineModel(Base):
    __tablename__ = "payroll_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee_code = Column(String(20), nullable=True)
    employee_name = Column(String(100), nullable=True)
    base_salary = Column(Numeric(18, 2), default=Decimal("0"))
    working_days = Column(Numeric(5, 1), default=Decimal("0"))
    standard_days = Column(Numeric(5, 1), default=Decimal("26"))
    prorated_salary = Column(Numeric(18, 2), default=Decimal("0"))
    overtime_amount = Column(Numeric(18, 2), default=Decimal("0"))
    allowances_total = Column(Numeric(18, 2), default=Decimal("0"))
    bonus_amount = Column(Numeric(18, 2), default=Decimal("0"))
    gross_salary = Column(Numeric(18, 2), default=Decimal("0"))
    si_base_salary = Column(Numeric(18, 2), default=Decimal("0"))
    employee_si = Column(Numeric(18, 2), default=Decimal("0"))
    employee_hi = Column(Numeric(18, 2), default=Decimal("0"))
    employee_ui = Column(Numeric(18, 2), default=Decimal("0"))
    advance_deduction = Column(Numeric(18, 2), default=Decimal("0"))
    other_deductions = Column(Numeric(18, 2), default=Decimal("0"))
    exempt_income = Column(Numeric(18, 2), default=Decimal("0"))
    personal_relief = Column(Numeric(18, 2), default=Decimal("15500000"))
    dependent_relief = Column(Numeric(18, 2), default=Decimal("0"))
    additional_deductions = Column(Numeric(18, 2), default=Decimal("0"))
    taxable_income = Column(Numeric(18, 2), default=Decimal("0"))
    pit_amount = Column(Numeric(18, 2), default=Decimal("0"))
    net_pay = Column(Numeric(18, 2), default=Decimal("0"))
    employer_si = Column(Numeric(18, 2), default=Decimal("0"))
    employer_hi = Column(Numeric(18, 2), default=Decimal("0"))
    employer_ui = Column(Numeric(18, 2), default=Decimal("0"))
    employer_occ = Column(Numeric(18, 2), default=Decimal("0"))
    kpcd = Column(Numeric(18, 2), default=Decimal("0"))
    payment_method = Column(String(30), default="bank_transfer")
    payment_status = Column(String(30), default="pending")
    payment_date = Column(Date, nullable=True)
    bank_transaction_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    payroll_run = relationship("PayrollRunModel", back_populates="lines")
    employee = relationship("EmployeeModel", back_populates="payroll_lines")

    __table_args__ = (
        UniqueConstraint("payroll_run_id", "employee_id", name="uq_payroll_line_employee"),
    )

    def __repr__(self) -> str:
        return (
            f"<PayrollLineModel(id={self.id}, run_id={self.payroll_run_id}, "
            f"employee_id={self.employee_id})>"
        )


class PayrollAdjustmentModel(Base):
    __tablename__ = "payroll_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    adjustment_type = Column(String(50), nullable=False)
    amount = Column(Numeric(18, 2), default=Decimal("0"))
    delta_gross = Column(Numeric(18, 2), default=Decimal("0"))
    delta_si_base = Column(Numeric(18, 2), default=Decimal("0"))
    delta_pit = Column(Numeric(18, 2), default=Decimal("0"))
    delta_net = Column(Numeric(18, 2), default=Decimal("0"))
    reason = Column(String(500), nullable=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    status = Column(String(30), default="draft")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)

    payroll_run = relationship("PayrollRunModel", back_populates="adjustments")
    employee = relationship("EmployeeModel", back_populates="adjustments")

    def __repr__(self) -> str:
        return (
            f"<PayrollAdjustmentModel(id={self.id}, run_id={self.payroll_run_id}, "
            f"type='{self.adjustment_type}')>"
        )


class PITDeclarationModel(Base):
    __tablename__ = "pit_declarations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    declaration_type = Column(String(20), nullable=False)
    period_month = Column(Integer, nullable=True)
    period_quarter = Column(Integer, nullable=True)
    period_year = Column(Integer, nullable=False)
    submission_type = Column(String(30), default="initial")
    status = Column(String(30), default="draft")
    total_income = Column(Numeric(18, 2), default=Decimal("0"))
    total_exempt_income = Column(Numeric(18, 2), default=Decimal("0"))
    total_deductions = Column(Numeric(18, 2), default=Decimal("0"))
    total_personal_relief = Column(Numeric(18, 2), default=Decimal("0"))
    total_dependent_relief = Column(Numeric(18, 2), default=Decimal("0"))
    total_taxable_income = Column(Numeric(18, 2), default=Decimal("0"))
    total_pit = Column(Numeric(18, 2), default=Decimal("0"))
    total_pit_withheld = Column(Numeric(18, 2), default=Decimal("0"))
    total_pit_paid = Column(Numeric(18, 2), default=Decimal("0"))
    submission_date = Column(DateTime, nullable=True)
    tax_authority_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PITDeclarationModel(id={self.id}, type='{self.declaration_type}', "
            f"period={self.period_month}/{self.period_year})>"
        )


class SIInsuranceRecordModel(Base):
    __tablename__ = "si_insurance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=True)
    period_month = Column(Integer, nullable=False)
    period_year = Column(Integer, nullable=False)
    status = Column(String(30), default="draft")
    total_si_base = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_si = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_hi = Column(Numeric(18, 2), default=Decimal("0"))
    total_employee_ui = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_si = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_hi = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_ui = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_occ = Column(Numeric(18, 2), default=Decimal("0"))
    total_kpcd = Column(Numeric(18, 2), default=Decimal("0"))
    total_payable = Column(Numeric(18, 2), default=Decimal("0"))
    submission_date = Column(DateTime, nullable=True)
    confirmation_ref = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)

    payroll_run = relationship("PayrollRunModel", back_populates="si_insurance_records")

    __table_args__ = (
        UniqueConstraint("period_month", "period_year", name="uq_si_insurance_period"),
    )

    def __repr__(self) -> str:
        return (
            f"<SIInsuranceRecordModel(id={self.id}, "
            f"period={self.period_month}/{self.period_year}, status='{self.status}')>"
        )


class SalaryPaymentModel(Base):
    __tablename__ = "salary_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(30), nullable=False)
    total_amount = Column(Numeric(18, 2), default=Decimal("0"))
    bank_transaction_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=True)

    payroll_run = relationship("PayrollRunModel", back_populates="salary_payments")

    def __repr__(self) -> str:
        return (
            f"<SalaryPaymentModel(id={self.id}, run_id={self.payroll_run_id}, "
            f"date={self.payment_date})>"
        )


class PayrollCostAllocationModel(Base):
    __tablename__ = "payroll_cost_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    cost_center = Column(String(10), nullable=False)
    total_salary_cost = Column(Numeric(18, 2), default=Decimal("0"))
    total_employer_cost = Column(Numeric(18, 2), default=Decimal("0"))
    total_cost = Column(Numeric(18, 2), default=Decimal("0"))
    gl_journal_entry_ref = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    payroll_run = relationship("PayrollRunModel", back_populates="cost_allocations")

    def __repr__(self) -> str:
        return (
            f"<PayrollCostAllocationModel(id={self.id}, run_id={self.payroll_run_id}, "
            f"cost_center='{self.cost_center}')>"
        )


class PayrollAuditLogModel(Base):
    __tablename__ = "payroll_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    action = Column(String(50), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    changed_by = Column(String(100), nullable=True)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    payroll_run = relationship("PayrollRunModel", back_populates="audit_logs")

    def __repr__(self) -> str:
        return (
            f"<PayrollAuditLogModel(id={self.id}, action='{self.action}', "
            f"run_id={self.payroll_run_id})>"
        )
