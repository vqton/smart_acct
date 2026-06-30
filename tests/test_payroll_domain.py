from datetime import date, datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError as PydanticValidationError

from domain.payroll import (
    ContractType, EmployeeStatus, Region, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, DeclarationStatus, DeclarationType, AdjustmentType, CostCenter,
    Employee, EmployeeContract, EmployeeDependent, Timesheet, PayrollLine,
    PayrollRun, PayrollAdjustment, PITDeclaration, SIInsuranceRecord,
    SalaryPayment, PayrollCostAllocation, PayrollCalculator,
)
from domain.common import VASValidationError
from domain.i18n import ErrorCodes


# ── Enum Tests ──────────────────────────────────────────────────────────────

class TestPayrollEnums:
    def test_contract_type_values(self):
        assert ContractType.INDEFINITE.value == "indefinite"
        assert ContractType.FIXED_TERM.value == "fixed_term"
        assert ContractType.SEASONAL.value == "seasonal"
        assert ContractType.PROBATION.value == "probation"

    def test_employee_status_values(self):
        assert EmployeeStatus.ACTIVE.value == "active"
        assert EmployeeStatus.TERMINATED.value == "terminated"
        assert EmployeeStatus.SUSPENDED.value == "suspended"
        assert EmployeeStatus.MATERNITY_LEAVE.value == "maternity_leave"
        assert EmployeeStatus.LONG_TERM_SICK.value == "long_term_sick"

    def test_region_values(self):
        assert Region.REGION_1.value == "region_1"
        assert Region.REGION_2.value == "region_2"
        assert Region.REGION_3.value == "region_3"
        assert Region.REGION_4.value == "region_4"

    def test_payroll_run_status_values(self):
        assert PayrollRunStatus.DRAFT.value == "draft"
        assert PayrollRunStatus.COMPUTED.value == "computed"
        assert PayrollRunStatus.APPROVED.value == "approved"
        assert PayrollRunStatus.PAID.value == "paid"
        assert PayrollRunStatus.CANCELLED.value == "cancelled"
        assert PayrollRunStatus.ADJUSTMENT.value == "adjustment"

    def test_payment_method_values(self):
        assert PaymentMethodPR.CASH.value == "cash"
        assert PaymentMethodPR.BANK_TRANSFER.value == "bank_transfer"

    def test_payment_status_values(self):
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PAID.value == "paid"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.PARTIAL.value == "partial"

    def test_declaration_status_values(self):
        assert DeclarationStatus.DRAFT.value == "draft"
        assert DeclarationStatus.SUBMITTED.value == "submitted"
        assert DeclarationStatus.ACCEPTED.value == "accepted"
        assert DeclarationStatus.REJECTED.value == "rejected"
        assert DeclarationStatus.ADJUSTED.value == "adjusted"

    def test_declaration_type_values(self):
        assert DeclarationType.MONTHLY.value == "monthly"
        assert DeclarationType.QUARTERLY.value == "quarterly"
        assert DeclarationType.ANNUAL.value == "annual"

    def test_adjustment_type_values(self):
        assert AdjustmentType.RETROACTIVE_INCREASE.value == "retroactive_increase"
        assert AdjustmentType.CORRECTION.value == "correction"
        assert AdjustmentType.ONE_OFF_BONUS.value == "one_off_bonus"
        assert AdjustmentType.PENALTY.value == "penalty"
        assert AdjustmentType.BACK_PAY.value == "back_pay"

    def test_cost_center_values(self):
        assert CostCenter.DIRECT_LABOR.value == "622"
        assert CostCenter.PRODUCTION_OVERHEAD.value == "627"
        assert CostCenter.SELLING.value == "641"
        assert CostCenter.ADMINISTRATION.value == "642"
        assert CostCenter.CONSTRUCTION.value == "241"
        assert CostCenter.MACHINE_OPERATORS.value == "623"


# ── Employee Tests ─────────────────────────────────────────────────────────

class TestEmployee:
    def test_create_valid_employee(self):
        emp = Employee(
            employee_code="NV001",
            full_name="Nguyen Van A",
            start_date=date(2025, 1, 1),
            tax_code="1234567890",
            id_number="123456789",
        )
        assert emp.employee_code == "NV001"
        assert emp.full_name == "Nguyen Van A"
        assert emp.start_date == date(2025, 1, 1)
        assert emp.tax_code == "1234567890"
        assert emp.id_number == "123456789"
        assert emp.region == Region.REGION_1
        assert emp.dependent_count == 0

    def test_employee_code_empty_raises_error(self):
        with pytest.raises(PydanticValidationError):
            Employee(employee_code="", full_name="Test", start_date=date(2025, 1, 1))

    def test_employee_name_empty_raises_error(self):
        with pytest.raises(VASValidationError):
            Employee(employee_code="NV001", full_name="", start_date=date(2025, 1, 1))

    def test_tax_code_invalid_too_short(self):
        with pytest.raises(VASValidationError):
            Employee(
                employee_code="NV001", full_name="Test",
                start_date=date(2025, 1, 1),
                tax_code="12345",
            )

    def test_tax_code_invalid_too_long(self):
        with pytest.raises(VASValidationError):
            Employee(
                employee_code="NV001", full_name="Test",
                start_date=date(2025, 1, 1),
                tax_code="12345678901234",
            )

    def test_tax_code_valid_10_digits(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
            tax_code="1234567890",
        )
        assert emp.tax_code == "1234567890"

    def test_tax_code_valid_13_digits(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
            tax_code="1234567890123",
        )
        assert emp.tax_code == "1234567890123"

    def test_tax_code_none_allowed(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
            tax_code=None,
        )
        assert emp.tax_code is None

    def test_id_number_valid_9_digits(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
            id_number="123456789",
        )
        assert emp.id_number == "123456789"

    def test_id_number_valid_12_digits(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
            id_number="123456789012",
        )
        assert emp.id_number == "123456789012"

    def test_id_number_invalid(self):
        with pytest.raises(VASValidationError):
            Employee(
                employee_code="NV001", full_name="Test",
                start_date=date(2025, 1, 1),
                id_number="12345678",
            )

    def test_termination_before_start_raises_error(self):
        with pytest.raises(VASValidationError):
            Employee(
                employee_code="NV001", full_name="Test",
                start_date=date(2025, 6, 1),
                termination_date=date(2025, 5, 31),
            )

    def test_default_status_is_active(self):
        emp = Employee(
            employee_code="NV001", full_name="Test",
            start_date=date(2025, 1, 1),
        )
        assert emp.status == EmployeeStatus.ACTIVE


# ── EmployeeContract Tests ─────────────────────────────────────────────────

class TestEmployeeContract:
    def test_create_valid_contract(self):
        c = EmployeeContract(
            employee_id=1,
            contract_type=ContractType.INDEFINITE,
            start_date=date(2025, 1, 1),
            base_salary=Decimal("10000000"),
            position_allowance=Decimal("2000000"),
            meal_allowance=Decimal("500000"),
        )
        assert c.employee_id == 1
        assert c.contract_type == ContractType.INDEFINITE
        assert c.base_salary == Decimal("10000000.00")
        assert c.position_allowance == Decimal("2000000.00")
        assert c.meal_allowance == Decimal("500000.00")
        assert c.is_active is True
        assert c.end_date is None

    def test_fixed_term_requires_end_date(self):
        with pytest.raises(VASValidationError):
            EmployeeContract(
                employee_id=1,
                contract_type=ContractType.FIXED_TERM,
                start_date=date(2025, 1, 1),
            )

    def test_seasonal_requires_end_date(self):
        with pytest.raises(VASValidationError):
            EmployeeContract(
                employee_id=1,
                contract_type=ContractType.SEASONAL,
                start_date=date(2025, 1, 1),
            )

    def test_end_date_before_start_raises_error(self):
        with pytest.raises(VASValidationError):
            EmployeeContract(
                employee_id=1,
                contract_type=ContractType.INDEFINITE,
                start_date=date(2025, 6, 1),
                end_date=date(2025, 5, 31),
            )

    def test_total_regular_income(self):
        c = EmployeeContract(
            employee_id=1,
            contract_type=ContractType.INDEFINITE,
            start_date=date(2025, 1, 1),
            base_salary=Decimal("10000000"),
            position_allowance=Decimal("2000000"),
            responsibility_allowance=Decimal("1000000"),
        )
        expected = Decimal("10000000") + Decimal("2000000") + Decimal("1000000")
        assert c.total_regular_income() == expected

    def test_default_is_active_true(self):
        c = EmployeeContract(
            employee_id=1,
            contract_type=ContractType.INDEFINITE,
            start_date=date(2025, 1, 1),
        )
        assert c.is_active is True


# ── EmployeeDependent Tests ────────────────────────────────────────────────

class TestEmployeeDependent:
    def test_create_valid_dependent(self):
        d = EmployeeDependent(
            employee_id=1,
            full_name="Nguyen Thi B",
            relationship="Spouse",
            date_of_birth=date(1990, 5, 10),
            tax_code="1234567890",
            from_date=date(2025, 1, 1),
        )
        assert d.full_name == "Nguyen Thi B"
        assert d.relationship == "Spouse"
        assert d.tax_code == "1234567890"
        assert d.is_active is True

    def test_tax_code_validation(self):
        with pytest.raises(VASValidationError):
            EmployeeDependent(
                employee_id=1,
                full_name="Nguyen Thi C",
                relationship="Child",
                tax_code="invalid",
                from_date=date(2025, 1, 1),
            )


# ── Timesheet Tests ────────────────────────────────────────────────────────

class TestTimesheet:
    def test_create_valid_timesheet(self):
        t = Timesheet(
            employee_id=1,
            period_month=6,
            period_year=2026,
            working_days=Decimal("26"),
            sick_leave_days=Decimal("2"),
        )
        assert t.employee_id == 1
        assert t.period_month == 6
        assert t.period_year == 2026
        assert t.working_days == Decimal("26")
        assert t.sick_leave_days == Decimal("2")
        assert t.overtime_weekday_hours == Decimal("0")

    def test_working_days_exceeds_max(self):
        with pytest.raises(VASValidationError):
            Timesheet(
                employee_id=1,
                period_month=6,
                period_year=2026,
                working_days=Decimal("32"),
            )

    def test_sick_leave_exceeds_standard(self):
        with pytest.raises(VASValidationError):
            Timesheet(
                employee_id=1,
                period_month=6,
                period_year=2026,
                working_days=Decimal("20"),
                sick_leave_days=Decimal("27"),
            )

    def test_overtime_hours_default_zero(self):
        t = Timesheet(
            employee_id=1,
            period_month=6,
            period_year=2026,
            working_days=Decimal("26"),
        )
        assert t.overtime_weekday_hours == Decimal("0")
        assert t.overtime_weekend_hours == Decimal("0")
        assert t.overtime_holiday_hours == Decimal("0")

    def test_days_quantized_to_half(self):
        t = Timesheet(
            employee_id=1,
            period_month=6,
            period_year=2026,
            working_days=Decimal("3.7"),
        )
        assert t.working_days == Decimal("3.5")


# ── PayrollLine Tests ──────────────────────────────────────────────────────

class TestPayrollLine:
    def test_default_values(self):
        pl = PayrollLine(employee_id=1)
        assert pl.base_salary == Decimal("0")
        assert pl.working_days == Decimal("0")
        assert pl.standard_days == Decimal("26")
        assert pl.gross_salary == Decimal("0")
        assert pl.net_pay == Decimal("0")
        assert pl.taxable_income == Decimal("0")
        assert pl.pit_amount == Decimal("0")

    def test_vnd_fields_quantized(self):
        pl = PayrollLine(
            employee_id=1,
            base_salary=Decimal("10000000.123"),
            gross_salary=Decimal("15000000.456"),
            net_pay=Decimal("12000000.789"),
        )
        assert pl.base_salary == Decimal("10000000.12")
        assert pl.gross_salary == Decimal("15000000.46")
        assert pl.net_pay == Decimal("12000000.79")

    def test_payment_defaults(self):
        pl = PayrollLine(employee_id=1)
        assert pl.payment_method == PaymentMethodPR.BANK_TRANSFER
        assert pl.payment_status == PaymentStatus.PENDING
        assert pl.payment_date is None


# ── PayrollRun Tests ───────────────────────────────────────────────────────

class TestPayrollRun:
    def test_create_run_with_lines(self):
        line1 = PayrollLine(employee_id=1, gross_salary=Decimal("10000000"), net_pay=Decimal("8000000"))
        line2 = PayrollLine(employee_id=2, gross_salary=Decimal("15000000"), net_pay=Decimal("12000000"))
        run = PayrollRun(
            period_month=6,
            period_year=2026,
            lines=[line1, line2],
        )
        assert run.period_month == 6
        assert run.period_year == 2026
        assert len(run.lines) == 2

    def test_compute_totals(self):
        line1 = PayrollLine(
            employee_id=1,
            gross_salary=Decimal("10000000"),
            employee_si=Decimal("800000"),
            employee_hi=Decimal("150000"),
            employee_ui=Decimal("100000"),
            pit_amount=Decimal("500000"),
            advance_deduction=Decimal("200000"),
            other_deductions=Decimal("100000"),
            net_pay=Decimal("8250000"),
            employer_si=Decimal("1750000"),
            employer_hi=Decimal("300000"),
            employer_ui=Decimal("100000"),
            employer_occ=Decimal("50000"),
            kpcd=Decimal("200000"),
        )
        line2 = PayrollLine(
            employee_id=2,
            gross_salary=Decimal("20000000"),
            employee_si=Decimal("1600000"),
            employee_hi=Decimal("300000"),
            employee_ui=Decimal("200000"),
            pit_amount=Decimal("1500000"),
            advance_deduction=Decimal("0"),
            other_deductions=Decimal("0"),
            net_pay=Decimal("16400000"),
            employer_si=Decimal("3500000"),
            employer_hi=Decimal("600000"),
            employer_ui=Decimal("200000"),
            employer_occ=Decimal("100000"),
            kpcd=Decimal("400000"),
        )
        run = PayrollRun(
            period_month=6,
            period_year=2026,
            lines=[line1, line2],
        )
        run.compute_totals()
        assert run.total_gross == Decimal("30000000.00")
        assert run.total_employee_si == Decimal("2400000.00")
        assert run.total_employee_hi == Decimal("450000.00")
        assert run.total_employee_ui == Decimal("300000.00")
        assert run.total_pit == Decimal("2000000.00")
        assert run.total_advances == Decimal("200000.00")
        assert run.total_other_deductions == Decimal("100000.00")
        assert run.total_net == Decimal("24650000.00")
        assert run.total_employer_si == Decimal("5250000.00")
        assert run.total_employer_hi == Decimal("900000.00")
        assert run.total_employer_ui == Decimal("300000.00")
        assert run.total_employer_occ == Decimal("150000.00")
        assert run.total_kpcd == Decimal("600000.00")

    def test_status_defaults_to_draft(self):
        run = PayrollRun(period_month=6, period_year=2026)
        assert run.status == PayrollRunStatus.DRAFT

    def test_invalid_period_month(self):
        with pytest.raises(PydanticValidationError):
            PayrollRun(period_month=0, period_year=2026)

    def test_invalid_period_year(self):
        with pytest.raises(PydanticValidationError):
            PayrollRun(period_month=6, period_year=2019)


# ── PayrollAdjustment Tests ────────────────────────────────────────────────

class TestPayrollAdjustment:
    def test_create_adjustment(self):
        adj = PayrollAdjustment(
            payroll_run_id=1,
            employee_id=1,
            adjustment_type=AdjustmentType.CORRECTION,
            amount=Decimal("500000"),
            reason="Sai so lieu luong co ban",
        )
        assert adj.payroll_run_id == 1
        assert adj.adjustment_type == AdjustmentType.CORRECTION
        assert adj.amount == Decimal("500000.00")
        assert adj.status == PayrollRunStatus.DRAFT

    def test_reason_required(self):
        with pytest.raises(PydanticValidationError):
            PayrollAdjustment(
                payroll_run_id=1,
                employee_id=1,
                adjustment_type=AdjustmentType.CORRECTION,
            )


# ── PITDeclaration Tests ───────────────────────────────────────────────────

class TestPITDeclaration:
    def test_create_declaration(self):
        decl = PITDeclaration(
            declaration_type=DeclarationType.MONTHLY,
            period_month=6,
            period_year=2026,
        )
        assert decl.declaration_type == DeclarationType.MONTHLY
        assert decl.period_month == 6
        assert decl.period_year == 2026
        assert decl.submission_type == "initial"

    def test_default_status_draft(self):
        decl = PITDeclaration(
            declaration_type=DeclarationType.QUARTERLY,
            period_quarter=2,
            period_year=2026,
        )
        assert decl.status == DeclarationStatus.DRAFT


# ── SIInsuranceRecord Tests ────────────────────────────────────────────────

class TestSIInsuranceRecord:
    def test_create_record(self):
        rec = SIInsuranceRecord(
            period_month=6,
            period_year=2026,
            total_si_base=Decimal("50000000"),
            total_employee_si=Decimal("4000000"),
        )
        assert rec.period_month == 6
        assert rec.period_year == 2026
        assert rec.total_si_base == Decimal("50000000.00")
        assert rec.total_employee_si == Decimal("4000000.00")

    def test_default_status(self):
        rec = SIInsuranceRecord(period_month=6, period_year=2026)
        assert rec.status == DeclarationStatus.DRAFT


# ── SalaryPayment Tests ────────────────────────────────────────────────────

class TestSalaryPayment:
    def test_create_payment(self):
        sp = SalaryPayment(
            payroll_run_id=1,
            payment_date=date(2026, 7, 5),
            payment_method=PaymentMethodPR.BANK_TRANSFER,
            total_amount=Decimal("50000000"),
        )
        assert sp.payroll_run_id == 1
        assert sp.payment_date == date(2026, 7, 5)
        assert sp.payment_method == PaymentMethodPR.BANK_TRANSFER
        assert sp.total_amount == Decimal("50000000.00")


# ── PayrollCostAllocation Tests ────────────────────────────────────────────

class TestPayrollCostAllocation:
    def test_create_allocation(self):
        alloc = PayrollCostAllocation(
            payroll_run_id=1,
            cost_center=CostCenter.ADMINISTRATION,
            total_salary_cost=Decimal("30000000"),
            total_employer_cost=Decimal("6000000"),
            total_cost=Decimal("36000000"),
        )
        assert alloc.payroll_run_id == 1
        assert alloc.cost_center == CostCenter.ADMINISTRATION
        assert alloc.total_salary_cost == Decimal("30000000.00")
        assert alloc.total_employer_cost == Decimal("6000000.00")
        assert alloc.total_cost == Decimal("36000000.00")


# ── PayrollCalculator Tests ────────────────────────────────────────────────

class TestPayrollCalculator:
    def test_compute_si_base_minimum(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("1000000"),
            region=Region.REGION_1,
        )
        assert result == Decimal("5310000.00")

    def test_compute_si_base_maximum(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("100000000"),
            region=Region.REGION_1,
        )
        expected_max = Decimal("20") * Decimal("2530000")
        assert result == expected_max.quantize(Decimal("0.01"))

    def test_compute_si_base_normal(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("20000000"),
            region=Region.REGION_1,
        )
        assert result == Decimal("20000000.00")

    def test_compute_si_base_region_2(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("1000000"),
            region=Region.REGION_2,
        )
        assert result == Decimal("4730000.00")

    def test_compute_si_base_region_3(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("1000000"),
            region=Region.REGION_3,
        )
        assert result == Decimal("4140000.00")

    def test_compute_si_base_region_4(self):
        result = PayrollCalculator.compute_si_base(
            regular_income=Decimal("1000000"),
            region=Region.REGION_4,
        )
        assert result == Decimal("3700000.00")

    def test_compute_gross_salary_full_month(self):
        result = PayrollCalculator.compute_gross_salary(
            base_salary=Decimal("10000000"),
            working_days=Decimal("26"),
            standard_days=Decimal("26"),
        )
        assert result == Decimal("10000000.00")

    def test_compute_gross_salary_partial_month(self):
        result = PayrollCalculator.compute_gross_salary(
            base_salary=Decimal("10000000"),
            working_days=Decimal("20"),
            standard_days=Decimal("26"),
        )
        expected = (Decimal("10000000") * Decimal("20") / Decimal("26")).quantize(Decimal("0.01"))
        assert result == expected

    def test_compute_gross_salary_with_overtime_and_allowances(self):
        result = PayrollCalculator.compute_gross_salary(
            base_salary=Decimal("10000000"),
            working_days=Decimal("26"),
            standard_days=Decimal("26"),
            overtime_amount=Decimal("1000000"),
            allowances_total=Decimal("2000000"),
            bonus_amount=Decimal("500000"),
        )
        assert result == Decimal("13500000.00")

    def test_compute_employee_insurance(self):
        si, hi, ui = PayrollCalculator.compute_employee_insurance(Decimal("10000000"))
        assert si == Decimal("800000.00")
        assert hi == Decimal("150000.00")
        assert ui == Decimal("100000.00")

    def test_compute_employer_insurance(self):
        si_total, hi, ui, occ, kpcd = PayrollCalculator.compute_employer_insurance(
            Decimal("10000000")
        )
        expected_si = (Decimal("10000000") * Decimal("0.14")).quantize(Decimal("0.01"))
        expected_sickness = (Decimal("10000000") * Decimal("0.03")).quantize(Decimal("0.01"))
        expected_occ = (Decimal("10000000") * Decimal("0.005")).quantize(Decimal("0.01"))
        assert si_total == (expected_si + expected_sickness + expected_occ).quantize(Decimal("0.01"))
        assert hi == Decimal("300000.00")
        assert ui == Decimal("100000.00")
        assert occ == Decimal("50000.00")
        assert kpcd == Decimal("200000.00")

    def test_compute_taxable_income_no_dependents(self):
        result = PayrollCalculator.compute_taxable_income(
            gross_salary=Decimal("30000000"),
            employee_si=Decimal("800000"),
            employee_hi=Decimal("150000"),
            employee_ui=Decimal("100000"),
        )
        expected = Decimal("30000000") - Decimal("1050000") - Decimal("15500000")
        assert result == expected.quantize(Decimal("0.01"))

    def test_compute_taxable_income_with_dependents(self):
        result = PayrollCalculator.compute_taxable_income(
            gross_salary=Decimal("30000000"),
            employee_si=Decimal("800000"),
            employee_hi=Decimal("150000"),
            employee_ui=Decimal("100000"),
            dependent_relief=Decimal("6200000"),
        )
        expected = Decimal("30000000") - Decimal("1050000") - Decimal("15500000") - Decimal("6200000")
        assert result == expected.quantize(Decimal("0.01"))

    def test_compute_taxable_income_below_zero(self):
        result = PayrollCalculator.compute_taxable_income(
            gross_salary=Decimal("10000000"),
            employee_si=Decimal("800000"),
            employee_hi=Decimal("150000"),
            employee_ui=Decimal("100000"),
        )
        assert result == Decimal("0")

    def test_compute_taxable_income_with_additional_deductions(self):
        result = PayrollCalculator.compute_taxable_income(
            gross_salary=Decimal("30000000"),
            employee_si=Decimal("800000"),
            employee_hi=Decimal("150000"),
            employee_ui=Decimal("100000"),
            additional_deductions=Decimal("2000000"),
        )
        expected = Decimal("30000000") - Decimal("1050000") - Decimal("15500000") - Decimal("2000000")
        assert result == expected.quantize(Decimal("0.01"))

    def test_compute_pit_bracket_1(self):
        tax = PayrollCalculator.compute_pit(Decimal("8000000"))
        assert tax == (Decimal("8000000") * Decimal("0.05")).quantize(Decimal("0.01"))

    def test_compute_pit_bracket_2(self):
        tax = PayrollCalculator.compute_pit(Decimal("20000000"))
        expected = (Decimal("20000000") * Decimal("0.10") - Decimal("500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_bracket_3(self):
        tax = PayrollCalculator.compute_pit(Decimal("50000000"))
        expected = (Decimal("50000000") * Decimal("0.20") - Decimal("3500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_bracket_4(self):
        tax = PayrollCalculator.compute_pit(Decimal("80000000"))
        expected = (Decimal("80000000") * Decimal("0.30") - Decimal("9500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_bracket_5(self):
        tax = PayrollCalculator.compute_pit(Decimal("200000000"))
        expected = (Decimal("200000000") * Decimal("0.35") - Decimal("19500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_zero(self):
        tax = PayrollCalculator.compute_pit(Decimal("0"))
        assert tax == Decimal("0")

    def test_compute_pit_edge_100m(self):
        tax = PayrollCalculator.compute_pit(Decimal("100000000"))
        expected = (Decimal("100000000") * Decimal("0.30") - Decimal("9500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_edge_60m(self):
        tax = PayrollCalculator.compute_pit(Decimal("60000000"))
        expected = (Decimal("60000000") * Decimal("0.20") - Decimal("3500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_edge_30m(self):
        tax = PayrollCalculator.compute_pit(Decimal("30000000"))
        expected = (Decimal("30000000") * Decimal("0.10") - Decimal("500000")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_pit_edge_10m(self):
        tax = PayrollCalculator.compute_pit(Decimal("10000000"))
        expected = (Decimal("10000000") * Decimal("0.05")).quantize(Decimal("0.01"))
        assert tax == expected

    def test_compute_net_pay(self):
        net = PayrollCalculator.compute_net_pay(
            gross_salary=Decimal("20000000"),
            employee_si=Decimal("1600000"),
            employee_hi=Decimal("300000"),
            employee_ui=Decimal("200000"),
            pit_amount=Decimal("500000"),
        )
        expected = Decimal("20000000") - Decimal("1600000") - Decimal("300000") - Decimal("200000") - Decimal("500000")
        assert net == expected.quantize(Decimal("0.01"))

    def test_compute_net_pay_with_deductions(self):
        net = PayrollCalculator.compute_net_pay(
            gross_salary=Decimal("20000000"),
            employee_si=Decimal("1600000"),
            employee_hi=Decimal("300000"),
            employee_ui=Decimal("200000"),
            pit_amount=Decimal("500000"),
            advance_deduction=Decimal("1000000"),
            other_deductions=Decimal("500000"),
        )
        expected = Decimal("20000000") - Decimal("1600000") - Decimal("300000") - Decimal("200000") - Decimal("500000") - Decimal("1000000") - Decimal("500000")
        assert net == expected.quantize(Decimal("0.01"))

    def test_compute_full_payroll_line(self):
        result = PayrollCalculator.compute_full_payroll_line(
            base_salary=Decimal("20000000"),
            working_days=Decimal("26"),
            standard_days=Decimal("26"),
            overtime_amount=Decimal("1000000"),
            allowances_total=Decimal("2000000"),
            bonus_amount=Decimal("500000"),
            si_base_salary=Decimal("20000000"),
            exempt_income=Decimal("0"),
            dependent_relief_amount=Decimal("6200000"),
            advance_deduction=Decimal("500000"),
            other_deductions=Decimal("200000"),
        )
        expected_gross = Decimal("23500000.00")
        assert result["gross_salary"] == expected_gross
        assert result["si_base_salary"] == Decimal("20000000.00")
        expected_emp_si = (Decimal("20000000") * Decimal("0.08")).quantize(Decimal("0.01"))
        expected_emp_hi = (Decimal("20000000") * Decimal("0.015")).quantize(Decimal("0.01"))
        expected_emp_ui = (Decimal("20000000") * Decimal("0.01")).quantize(Decimal("0.01"))
        assert result["employee_si"] == expected_emp_si
        assert result["employee_hi"] == expected_emp_hi
        assert result["employee_ui"] == expected_emp_ui
        assert result["personal_relief"] == Decimal("15500000.00")
        assert result["dependent_relief"] == Decimal("6200000.00")
        taxable = Decimal("23500000") - expected_emp_si - expected_emp_hi - expected_emp_ui - Decimal("15500000") - Decimal("6200000")
        if taxable < 0:
            taxable = Decimal("0")
        assert result["taxable_income"] == taxable
        assert result["pit_amount"] == Decimal("0")
        expected_net = Decimal("23500000") - expected_emp_si - expected_emp_hi - expected_emp_ui - Decimal("0") - Decimal("500000") - Decimal("200000")
        assert result["net_pay"] == expected_net.quantize(Decimal("0.01"))
        expected_emp_si_total = (Decimal("20000000") * Decimal("0.14") + Decimal("20000000") * Decimal("0.03") + Decimal("20000000") * Decimal("0.005")).quantize(Decimal("0.01"))
        expected_emp_hi_total = (Decimal("20000000") * Decimal("0.03")).quantize(Decimal("0.01"))
        expected_emp_ui_total = (Decimal("20000000") * Decimal("0.01")).quantize(Decimal("0.01"))
        expected_occ = (Decimal("20000000") * Decimal("0.005")).quantize(Decimal("0.01"))
        expected_kpcd = (Decimal("20000000") * Decimal("0.02")).quantize(Decimal("0.01"))
        assert result["employer_si"] == expected_emp_si_total
        assert result["employer_hi"] == expected_emp_hi_total
        assert result["employer_ui"] == expected_emp_ui_total
        assert result["employer_occ"] == expected_occ
        assert result["kpcd"] == expected_kpcd

    def test_compute_full_payroll_line_positive_pit(self):
        result = PayrollCalculator.compute_full_payroll_line(
            base_salary=Decimal("50000000"),
            working_days=Decimal("26"),
            standard_days=Decimal("26"),
            overtime_amount=Decimal("0"),
            allowances_total=Decimal("0"),
            bonus_amount=Decimal("0"),
            si_base_salary=Decimal("50000000"),
            exempt_income=Decimal("0"),
            dependent_relief_amount=Decimal("0"),
            advance_deduction=Decimal("0"),
            other_deductions=Decimal("0"),
        )
        assert result["gross_salary"] == Decimal("50000000.00")
        assert result["employee_si"] == Decimal("4000000.00")
        assert result["employee_hi"] == Decimal("750000.00")
        assert result["employee_ui"] == Decimal("500000.00")
        insurance = Decimal("4000000") + Decimal("750000") + Decimal("500000")
        taxable = Decimal("50000000") - insurance - Decimal("15500000")
        assert result["taxable_income"] == taxable
        expected_pit = taxable * Decimal("0.10") - Decimal("500000")
        assert result["pit_amount"] == expected_pit.quantize(Decimal("0.01"))
        net = Decimal("50000000") - insurance - result["pit_amount"]
        assert result["net_pay"] == net.quantize(Decimal("0.01"))


# ── Run tests if executed directly ─────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__])
