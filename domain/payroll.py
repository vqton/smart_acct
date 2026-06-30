from typing import List, Optional, ClassVar, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


# ── Enums ──────────────────────────────────────────────────────────────

class ContractType(str, Enum):
    INDEFINITE = "indefinite"
    FIXED_TERM = "fixed_term"
    SEASONAL = "seasonal"
    PROBATION = "probation"


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    MATERNITY_LEAVE = "maternity_leave"
    LONG_TERM_SICK = "long_term_sick"


class Region(str, Enum):
    REGION_1 = "region_1"
    REGION_2 = "region_2"
    REGION_3 = "region_3"
    REGION_4 = "region_4"


class PayrollRunStatus(str, Enum):
    DRAFT = "draft"
    COMPUTED = "computed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    ADJUSTMENT = "adjustment"


class PaymentMethodPR(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    PARTIAL = "partial"


class DeclarationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ADJUSTED = "adjusted"


class DeclarationType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class AdjustmentType(str, Enum):
    RETROACTIVE_INCREASE = "retroactive_increase"
    CORRECTION = "correction"
    ONE_OFF_BONUS = "one_off_bonus"
    PENALTY = "penalty"
    BACK_PAY = "back_pay"


class CostCenter(str, Enum):
    DIRECT_LABOR = "622"
    PRODUCTION_OVERHEAD = "627"
    SELLING = "641"
    ADMINISTRATION = "642"
    CONSTRUCTION = "241"
    MACHINE_OPERATORS = "623"


# ── Constants ─────────────────────────────────────────────────────────

_REGIONAL_MINIMUM_WAGE: dict = {
    "region_1": Decimal("5310000"),
    "region_2": Decimal("4730000"),
    "region_3": Decimal("4140000"),
    "region_4": Decimal("3700000"),
}

_REFERENCE_LEVEL = Decimal("2530000")
_SI_MAX_BASE_MULTIPLIER = Decimal("20")
_STANDARD_WORKING_DAYS = Decimal("26")

_SI_RATES: dict = {
    "employee_retirement": Decimal("0.08"),
    "employee_health": Decimal("0.015"),
    "employee_unemployment": Decimal("0.01"),
    "employer_retirement": Decimal("0.14"),
    "employer_sickness": Decimal("0.03"),
    "employer_occupational": Decimal("0.005"),
    "employer_health": Decimal("0.03"),
    "employer_unemployment": Decimal("0.01"),
    "employer_union": Decimal("0.02"),
}

_PIT_PERSONAL_RELIEF = Decimal("15500000")
_PIT_DEPENDENT_RELIEF = Decimal("6200000")

_PIT_BRACKETS: List[Tuple[Decimal, Decimal, Decimal]] = [
    (Decimal("10000000"), Decimal("0.05"), Decimal("0")),
    (Decimal("30000000"), Decimal("0.10"), Decimal("500000")),
    (Decimal("60000000"), Decimal("0.20"), Decimal("3500000")),
    (Decimal("100000000"), Decimal("0.30"), Decimal("9500000")),
    (Decimal("999999999999"), Decimal("0.35"), Decimal("19500000")),
]


# ── Domain Entities ────────────────────────────────────────────────────

class Employee(BaseModel):
    id: Optional[int] = None
    employee_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    id_number: Optional[str] = None
    id_issue_date: Optional[date] = None
    id_issue_place: Optional[str] = None
    tax_code: Optional[str] = None
    si_book_number: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    position: Optional[str] = None
    region: Region = Region.REGION_1
    dependent_count: int = 0
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    start_date: date
    termination_date: Optional[date] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @field_validator("employee_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise VASValidationError(ErrorCodes.PR_EMPLOYEE_CODE_EMPTY)
        return stripped

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise VASValidationError(ErrorCodes.PR_EMPLOYEE_NAME_EMPTY)
        return stripped

    @field_validator("tax_code")
    @classmethod
    def validate_tax_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            val = v.strip()
            if len(val) not in (10, 13) or not val.isdigit():
                raise VASValidationError(ErrorCodes.PR_TAX_CODE_INVALID)
            return val
        return v

    @field_validator("id_number")
    @classmethod
    def validate_id_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            val = v.strip()
            if len(val) not in (9, 12) or not val.isdigit():
                raise VASValidationError(ErrorCodes.PR_ID_INVALID)
            return val
        return v

    @model_validator(mode="after")
    def check_termination_date(self) -> "Employee":
        if self.termination_date and self.start_date and self.termination_date <= self.start_date:
            raise VASValidationError(ErrorCodes.PR_CONTRACT_END_BEFORE_START)
        return self


class EmployeeContract(BaseModel):
    id: Optional[int] = None
    employee_id: int
    contract_type: ContractType
    start_date: date
    end_date: Optional[date] = None
    base_salary: Decimal = Decimal("0")
    position_allowance: Decimal = Decimal("0")
    meal_allowance: Decimal = Decimal("0")
    phone_allowance: Decimal = Decimal("0")
    transport_allowance: Decimal = Decimal("0")
    housing_allowance: Decimal = Decimal("0")
    responsibility_allowance: Decimal = Decimal("0")
    other_allowance: Decimal = Decimal("0")
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("base_salary", "position_allowance", "meal_allowance", "phone_allowance", "transport_allowance", "housing_allowance", "responsibility_allowance", "other_allowance")
    @classmethod
    def quantize_salary(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def check_dates(self) -> "EmployeeContract":
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise VASValidationError(ErrorCodes.PR_CONTRACT_END_BEFORE_START)
        if self.contract_type in (ContractType.FIXED_TERM, ContractType.SEASONAL) and not self.end_date:
            raise VASValidationError(ErrorCodes.PR_FIXED_TERM_NO_END_DATE)
        return self

    def total_regular_income(self) -> Decimal:
        return self.base_salary + self.position_allowance + self.responsibility_allowance


class EmployeeDependent(BaseModel):
    id: Optional[int] = None
    employee_id: int
    full_name: str = Field(..., max_length=100)
    relationship: str = Field(..., max_length=50)
    date_of_birth: Optional[date] = None
    tax_code: Optional[str] = None
    from_date: date
    to_date: Optional[date] = None
    is_active: bool = True

    @field_validator("tax_code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            val = v.strip()
            if len(val) not in (10, 13) or not val.isdigit():
                raise VASValidationError(ErrorCodes.PR_TAX_CODE_INVALID)
            return val
        return v


class Timesheet(BaseModel):
    id: Optional[int] = None
    employee_id: int
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2020, le=2100)
    working_days: Decimal = Decimal("0")
    standard_days: Decimal = _STANDARD_WORKING_DAYS
    overtime_weekday_hours: Decimal = Decimal("0")
    overtime_weekend_hours: Decimal = Decimal("0")
    overtime_holiday_hours: Decimal = Decimal("0")
    sick_leave_days: Decimal = Decimal("0")
    unpaid_leave_days: Decimal = Decimal("0")
    paid_leave_days: Decimal = Decimal("0")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("working_days")
    @classmethod
    def quantize_days(cls, v: Decimal) -> Decimal:
        return (v * Decimal("2")).quantize(Decimal("1")) / Decimal("2")

    @model_validator(mode="after")
    def check_limits(self) -> "Timesheet":
        if self.working_days > 31:
            raise VASValidationError(ErrorCodes.PR_OVERTIME_EXCEEDS_LIMIT)
        if self.sick_leave_days > self.standard_days:
            raise VASValidationError(ErrorCodes.PR_SI_SUSPENDED)
        return self


class PayrollLine(BaseModel):
    id: Optional[int] = None
    payroll_run_id: Optional[int] = None
    employee_id: int
    employee_code: Optional[str] = None
    employee_name: Optional[str] = None
    base_salary: Decimal = Decimal("0")
    working_days: Decimal = Decimal("0")
    standard_days: Decimal = _STANDARD_WORKING_DAYS
    prorated_salary: Decimal = Decimal("0")
    overtime_amount: Decimal = Decimal("0")
    allowances_total: Decimal = Decimal("0")
    bonus_amount: Decimal = Decimal("0")
    gross_salary: Decimal = Decimal("0")
    si_base_salary: Decimal = Decimal("0")
    employee_si: Decimal = Decimal("0")
    employee_hi: Decimal = Decimal("0")
    employee_ui: Decimal = Decimal("0")
    advance_deduction: Decimal = Decimal("0")
    other_deductions: Decimal = Decimal("0")
    exempt_income: Decimal = Decimal("0")
    personal_relief: Decimal = Decimal("0")
    dependent_relief: Decimal = Decimal("0")
    additional_deductions: Decimal = Decimal("0")
    taxable_income: Decimal = Decimal("0")
    pit_amount: Decimal = Decimal("0")
    net_pay: Decimal = Decimal("0")
    employer_si: Decimal = Decimal("0")
    employer_hi: Decimal = Decimal("0")
    employer_ui: Decimal = Decimal("0")
    employer_occ: Decimal = Decimal("0")
    kpcd: Decimal = Decimal("0")
    payment_method: PaymentMethodPR = PaymentMethodPR.BANK_TRANSFER
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_date: Optional[date] = None
    bank_transaction_ref: Optional[str] = None
    notes: Optional[str] = None

    _VND_FIELDS: ClassVar[set] = {
        "base_salary", "prorated_salary", "overtime_amount", "allowances_total",
        "bonus_amount", "gross_salary", "si_base_salary",
        "employee_si", "employee_hi", "employee_ui", "advance_deduction",
        "other_deductions", "exempt_income", "personal_relief", "dependent_relief",
        "additional_deductions", "taxable_income", "pit_amount", "net_pay",
        "employer_si", "employer_hi", "employer_ui", "employer_occ", "kpcd",
    }

    @field_validator(*tuple(_VND_FIELDS))
    @classmethod
    def quantize_vnd_fields(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class PayrollRun(BaseModel):
    id: Optional[int] = None
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2020, le=2100)
    status: PayrollRunStatus = PayrollRunStatus.DRAFT
    lines: List[PayrollLine] = []

    total_gross: Decimal = Decimal("0")
    total_employee_si: Decimal = Decimal("0")
    total_employee_hi: Decimal = Decimal("0")
    total_employee_ui: Decimal = Decimal("0")
    total_pit: Decimal = Decimal("0")
    total_advances: Decimal = Decimal("0")
    total_other_deductions: Decimal = Decimal("0")
    total_net: Decimal = Decimal("0")
    total_employer_si: Decimal = Decimal("0")
    total_employer_hi: Decimal = Decimal("0")
    total_employer_ui: Decimal = Decimal("0")
    total_employer_occ: Decimal = Decimal("0")
    total_kpcd: Decimal = Decimal("0")

    computed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

    _TOTAL_FIELDS: ClassVar[set] = {
        "total_gross", "total_employee_si", "total_employee_hi", "total_employee_ui",
        "total_pit", "total_advances", "total_other_deductions", "total_net",
        "total_employer_si", "total_employer_hi", "total_employer_ui",
        "total_employer_occ", "total_kpcd",
    }

    @field_validator(*tuple(_TOTAL_FIELDS))
    @classmethod
    def quantize_totals(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)

    def compute_totals(self) -> None:
        """Recompute all totals from lines."""
        self.total_gross = sum((l.gross_salary for l in self.lines), Decimal("0"))
        self.total_employee_si = sum((l.employee_si for l in self.lines), Decimal("0"))
        self.total_employee_hi = sum((l.employee_hi for l in self.lines), Decimal("0"))
        self.total_employee_ui = sum((l.employee_ui for l in self.lines), Decimal("0"))
        self.total_pit = sum((l.pit_amount for l in self.lines), Decimal("0"))
        self.total_advances = sum((l.advance_deduction for l in self.lines), Decimal("0"))
        self.total_other_deductions = sum((l.other_deductions for l in self.lines), Decimal("0"))
        self.total_net = sum((l.net_pay for l in self.lines), Decimal("0"))
        self.total_employer_si = sum((l.employer_si for l in self.lines), Decimal("0"))
        self.total_employer_hi = sum((l.employer_hi for l in self.lines), Decimal("0"))
        self.total_employer_ui = sum((l.employer_ui for l in self.lines), Decimal("0"))
        self.total_employer_occ = sum((l.employer_occ for l in self.lines), Decimal("0"))
        self.total_kpcd = sum((l.kpcd for l in self.lines), Decimal("0"))


class PayrollAdjustment(BaseModel):
    id: Optional[int] = None
    payroll_run_id: int
    employee_id: int
    adjustment_type: AdjustmentType
    amount: Decimal = Decimal("0")
    delta_gross: Decimal = Decimal("0")
    delta_si_base: Decimal = Decimal("0")
    delta_pit: Decimal = Decimal("0")
    delta_net: Decimal = Decimal("0")
    reason: str = Field(..., max_length=500)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    status: PayrollRunStatus = PayrollRunStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

    @field_validator("amount", "delta_gross", "delta_si_base", "delta_pit", "delta_net")
    @classmethod
    def quantize_deltas(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class PITDeclaration(BaseModel):
    id: Optional[int] = None
    declaration_type: DeclarationType
    period_month: Optional[int] = Field(default=None, ge=1, le=12)
    period_quarter: Optional[int] = Field(default=None, ge=1, le=4)
    period_year: int = Field(..., ge=2020, le=2100)
    submission_type: str = "initial"
    status: DeclarationStatus = DeclarationStatus.DRAFT
    total_income: Decimal = Decimal("0")
    total_exempt_income: Decimal = Decimal("0")
    total_deductions: Decimal = Decimal("0")
    total_personal_relief: Decimal = Decimal("0")
    total_dependent_relief: Decimal = Decimal("0")
    total_taxable_income: Decimal = Decimal("0")
    total_pit: Decimal = Decimal("0")
    total_pit_withheld: Decimal = Decimal("0")
    total_pit_paid: Decimal = Decimal("0")
    submission_date: Optional[datetime] = None
    tax_authority_response: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

    _PIT_VND_FIELDS: ClassVar[set] = {
        "total_income", "total_exempt_income", "total_deductions",
        "total_personal_relief", "total_dependent_relief",
        "total_taxable_income", "total_pit", "total_pit_withheld", "total_pit_paid",
    }

    @field_validator(*tuple(_PIT_VND_FIELDS))
    @classmethod
    def quantize_pit_fields(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class SIInsuranceRecord(BaseModel):
    id: Optional[int] = None
    payroll_run_id: Optional[int] = None
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2020, le=2100)
    status: DeclarationStatus = DeclarationStatus.DRAFT
    total_si_base: Decimal = Decimal("0")
    total_employee_si: Decimal = Decimal("0")
    total_employee_hi: Decimal = Decimal("0")
    total_employee_ui: Decimal = Decimal("0")
    total_employer_si: Decimal = Decimal("0")
    total_employer_hi: Decimal = Decimal("0")
    total_employer_ui: Decimal = Decimal("0")
    total_employer_occ: Decimal = Decimal("0")
    total_kpcd: Decimal = Decimal("0")
    total_payable: Decimal = Decimal("0")
    submission_date: Optional[datetime] = None
    confirmation_ref: Optional[str] = None
    payment_date: Optional[date] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

    _SI_VND_FIELDS: ClassVar[set] = {
        "total_si_base", "total_employee_si", "total_employee_hi", "total_employee_ui",
        "total_employer_si", "total_employer_hi", "total_employer_ui",
        "total_employer_occ", "total_kpcd", "total_payable",
    }

    @field_validator(*tuple(_SI_VND_FIELDS))
    @classmethod
    def quantize_si_fields(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class SalaryPayment(BaseModel):
    id: Optional[int] = None
    payroll_run_id: int
    payment_date: date
    payment_method: PaymentMethodPR
    total_amount: Decimal = Decimal("0")
    bank_transaction_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

    @field_validator("total_amount")
    @classmethod
    def quantize_amount(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


class PayrollCostAllocation(BaseModel):
    id: Optional[int] = None
    payroll_run_id: int
    cost_center: CostCenter
    total_salary_cost: Decimal = Decimal("0")
    total_employer_cost: Decimal = Decimal("0")
    total_cost: Decimal = Decimal("0")
    gl_journal_entry_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("total_salary_cost", "total_employer_cost", "total_cost")
    @classmethod
    def quantize_cost_fields(cls, v: Decimal) -> Decimal:
        return _quantize_vnd(v)


# ── Payroll Computation Engine ─────────────────────────────────────────

class PayrollCalculator:
    """Stateless payroll calculation engine (pure domain logic)."""

    @staticmethod
    def compute_si_base(
        regular_income: Decimal,
        region: Region,
        reference_level: Decimal = _REFERENCE_LEVEL,
    ) -> Decimal:
        min_wage = _REGIONAL_MINIMUM_WAGE[region.value]
        max_base = _SI_MAX_BASE_MULTIPLIER * reference_level
        return max(min_wage, min(regular_income, max_base)).quantize(Decimal("0.01"))

    @staticmethod
    def compute_gross_salary(
        base_salary: Decimal,
        working_days: Decimal,
        standard_days: Decimal = _STANDARD_WORKING_DAYS,
        overtime_amount: Decimal = Decimal("0"),
        allowances_total: Decimal = Decimal("0"),
        bonus_amount: Decimal = Decimal("0"),
    ) -> Decimal:
        ratio = working_days / standard_days if standard_days > 0 else Decimal("1")
        prorated = base_salary * ratio
        return (prorated + overtime_amount + allowances_total + bonus_amount).quantize(Decimal("0.01"))

    @staticmethod
    def compute_employee_insurance(si_base: Decimal) -> Tuple[Decimal, Decimal, Decimal]:
        si = (si_base * _SI_RATES["employee_retirement"]).quantize(Decimal("0.01"))
        hi = (si_base * _SI_RATES["employee_health"]).quantize(Decimal("0.01"))
        ui = (si_base * _SI_RATES["employee_unemployment"]).quantize(Decimal("0.01"))
        return si, hi, ui

    @staticmethod
    def compute_employer_insurance(si_base: Decimal) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        si_ret = (si_base * _SI_RATES["employer_retirement"]).quantize(Decimal("0.01"))
        sickness = (si_base * _SI_RATES["employer_sickness"]).quantize(Decimal("0.01"))
        occ = (si_base * _SI_RATES["employer_occupational"]).quantize(Decimal("0.01"))
        hi = (si_base * _SI_RATES["employer_health"]).quantize(Decimal("0.01"))
        ui = (si_base * _SI_RATES["employer_unemployment"]).quantize(Decimal("0.01"))
        kpcd = (si_base * _SI_RATES["employer_union"]).quantize(Decimal("0.01"))
        si_total = (si_ret + sickness + occ).quantize(Decimal("0.01"))
        return si_total, hi, ui, occ, kpcd

    @staticmethod
    def compute_taxable_income(
        gross_salary: Decimal,
        employee_si: Decimal,
        employee_hi: Decimal,
        employee_ui: Decimal,
        exempt_income: Decimal = Decimal("0"),
        personal_relief: Decimal = _PIT_PERSONAL_RELIEF,
        dependent_relief: Decimal = Decimal("0"),
        additional_deductions: Decimal = Decimal("0"),
    ) -> Decimal:
        insurance = employee_si + employee_hi + employee_ui
        taxable = gross_salary - exempt_income - insurance - personal_relief - dependent_relief - additional_deductions
        return max(Decimal("0"), taxable).quantize(Decimal("0.01"))

    @staticmethod
    def compute_pit(taxable_income: Decimal) -> Decimal:
        for max_income, rate, deduction in _PIT_BRACKETS:
            if taxable_income <= max_income:
                tax = (taxable_income * rate - deduction).quantize(Decimal("0.01"))
                return max(Decimal("0"), tax)
        return Decimal("0")

    @staticmethod
    def compute_net_pay(
        gross_salary: Decimal,
        employee_si: Decimal,
        employee_hi: Decimal,
        employee_ui: Decimal,
        pit_amount: Decimal,
        advance_deduction: Decimal = Decimal("0"),
        other_deductions: Decimal = Decimal("0"),
    ) -> Decimal:
        net = gross_salary - employee_si - employee_hi - employee_ui - pit_amount - advance_deduction - other_deductions
        return net.quantize(Decimal("0.01"))

    @classmethod
    def compute_full_payroll_line(
        cls,
        base_salary: Decimal,
        working_days: Decimal,
        standard_days: Decimal,
        overtime_amount: Decimal,
        allowances_total: Decimal,
        bonus_amount: Decimal,
        si_base_salary: Decimal,
        exempt_income: Decimal,
        dependent_relief_amount: Decimal,
        advance_deduction: Decimal,
        other_deductions: Decimal,
        additional_deductions: Decimal = Decimal("0"),
    ) -> dict:
        gross = cls.compute_gross_salary(
            base_salary, working_days, standard_days,
            overtime_amount, allowances_total, bonus_amount,
        )
        emp_si, emp_hi, emp_ui = cls.compute_employee_insurance(si_base_salary)
        taxable = cls.compute_taxable_income(
            gross, emp_si, emp_hi, emp_ui,
            exempt_income=exempt_income,
            dependent_relief=dependent_relief_amount,
            additional_deductions=additional_deductions,
        )
        pit = cls.compute_pit(taxable)
        net = cls.compute_net_pay(gross, emp_si, emp_hi, emp_ui, pit, advance_deduction, other_deductions)
        emp_si_total, emp_hi_total, emp_ui_total, occ, kpcd = cls.compute_employer_insurance(si_base_salary)

        return {
            "prorated_salary": (base_salary * working_days / standard_days).quantize(Decimal("0.01")) if standard_days > 0 else base_salary,
            "gross_salary": gross,
            "si_base_salary": si_base_salary,
            "employee_si": emp_si,
            "employee_hi": emp_hi,
            "employee_ui": emp_ui,
            "exempt_income": exempt_income,
            "personal_relief": _PIT_PERSONAL_RELIEF,
            "dependent_relief": dependent_relief_amount,
            "taxable_income": taxable,
            "pit_amount": pit,
            "net_pay": net,
            "employer_si": emp_si_total,
            "employer_hi": emp_hi_total,
            "employer_ui": emp_ui_total,
            "employer_occ": occ,
            "kpcd": kpcd,
            "advance_deduction": advance_deduction,
            "other_deductions": other_deductions,
            "allowances_total": allowances_total,
            "bonus_amount": bonus_amount,
            "overtime_amount": overtime_amount,
        }
