from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pydantic

from domain import (
    TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus, TaxPaymentStatus,
    InvoiceStatus, TaxAdjustmentType, TaxAdjustmentStatus, TaxIncentiveType, IncentiveStatus,
    TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive,
    EInvoice, InvoiceType, EInvoiceAdjustmentType, TaxSchedule, ScheduleStatus,
    ValidationError, EInvoiceLine, VASValidationError,
)
from infrastructure.models.coa_models import Base
from infrastructure.models.tax_models import (
    TaxDeclarationModel, TaxLineModel, TaxPaymentModel, TaxAdjustmentModel,
    TaxIncentiveModel, EInvoiceModel, TaxScheduleModel,
)
from infrastructure.repositories.tax_repository import TaxRepository
from use_cases.tax_use_cases import TaxUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield Session(engine)


@pytest.fixture
def repo(session):
    return TaxRepository(session)


@pytest.fixture
def uc(session):
    return TaxUseCases(session)


# ═══════════════════════════════════════════════════════════════════
# TaxDeclaration — period enforcement & boundaries
# ═══════════════════════════════════════════════════════════════════

class TestTaxDeclarationPeriodEnforcement:
    def test_requires_period_month_for_vat(self):
        with pytest.raises(ValidationError, match="period_month"):
            TaxDeclaration(
                tax_type=TaxType.VAT_DEDUCTION,
                declaration_type=DeclarationType.ORIGINAL,
                form_code="01/GTGT",
                period_year=2024,
                period_month=None,
                total_revenue=Decimal("1000000"),
                total_tax=Decimal("100000"),
            )

    def test_requires_period_quarter_for_cit(self):
        with pytest.raises(ValidationError, match="period_quarter"):
            TaxDeclaration(
                tax_type=TaxType.CIT,
                declaration_type=DeclarationType.ORIGINAL,
                form_code="03/TNDN",
                period_year=2024,
                period_quarter=None,
                total_revenue=Decimal("5000000"),
                total_tax=Decimal("1000000"),
            )

    def test_rejects_both_month_and_quarter(self):
        with pytest.raises(ValidationError, match="Cannot set both"):
            TaxDeclaration(
                tax_type=TaxType.VAT_DEDUCTION,
                declaration_type=DeclarationType.ORIGINAL,
                form_code="01/GTGT",
                period_year=2024,
                period_month=3,
                period_quarter=1,
                total_revenue=Decimal("1000000"),
            )

    def test_accepts_annual_type_no_period_fields(self):
        decl = TaxDeclaration(
            tax_type=TaxType.LICENSE,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="08/LIST",
            period_year=2024,
            total_revenue=Decimal("0"),
        )
        assert decl.period_month is None
        assert decl.period_quarter is None

    def test_accepts_pit_finalization_no_period_fields(self):
        decl = TaxDeclaration(
            tax_type=TaxType.PIT_FINALIZATION,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="05A/PIT",
            period_year=2024,
            total_revenue=Decimal("0"),
        )
        assert decl.period_month is None
        assert decl.period_quarter is None

    def test_accepts_foreign_contractor_with_quarter(self):
        decl = TaxDeclaration(
            tax_type=TaxType.FOREIGN_CONTRACTOR,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="01/FC",
            period_year=2024,
            period_quarter=2,
            total_revenue=Decimal("2000000"),
        )
        assert decl.period_quarter == 2

    def test_year_boundary_low(self):
        decl = TaxDeclaration(
            tax_type=TaxType.VAT_DEDUCTION,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="01/GTGT",
            period_year=2000,
            period_month=1,
            total_revenue=Decimal("0"),
        )
        assert decl.period_year == 2000

    def test_year_above_2100_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            TaxDeclaration(
                tax_type=TaxType.LICENSE,
                declaration_type=DeclarationType.ORIGINAL,
                form_code="08/LIST",
                period_year=2101,
                total_revenue=Decimal("0"),
            )

    def test_quantizes_total_revenue(self):
        decl = TaxDeclaration(
            tax_type=TaxType.VAT_DEDUCTION,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="01/GTGT",
            period_year=2024,
            period_month=6,
            total_revenue=Decimal("1000.456"),
        )
        assert decl.total_revenue == Decimal("1000.46")


# ═══════════════════════════════════════════════════════════════════
# TaxPayment — budget-tax cross validation
# ═══════════════════════════════════════════════════════════════════

class TestTaxPaymentBudgetMatching:
    def test_accepts_correct_vat_budget(self):
        TaxPayment(
            declaration_id=1,
            tax_type=TaxType.VAT_DEDUCTION,
            amount=Decimal("1000000"),
            payment_date=date(2024, 6, 30),
            due_date=date(2024, 7, 20),
            budget_account="1701",
            payment_method="bank",
            payment_status=TaxPaymentStatus.PENDING,
        )

    def test_rejects_budget_mismatch(self):
        with pytest.raises(ValidationError):
            TaxPayment(
                declaration_id=1,
                tax_type=TaxType.VAT_DEDUCTION,
                amount=Decimal("1000000"),
                payment_date=date(2024, 6, 30),
                due_date=date(2024, 7, 20),
                budget_account="1702",
                payment_method="bank",
                payment_status=TaxPaymentStatus.PENDING,
            )

    def test_accepts_correct_cit_budget(self):
        TaxPayment(
            declaration_id=1,
            tax_type=TaxType.CIT,
            amount=Decimal("2000000"),
            payment_date=date(2024, 6, 30),
            due_date=date(2024, 7, 20),
            budget_account="1702",
            payment_status=TaxPaymentStatus.PENDING,
        )

    def test_rejects_negative_amount(self):
        with pytest.raises(pydantic.ValidationError):
            TaxPayment(
                declaration_id=1,
                tax_type=TaxType.VAT_DEDUCTION,
                amount=Decimal("-1000"),
                payment_date=date(2024, 6, 30),
                due_date=date(2024, 7, 20),
                budget_account="1701",
                payment_status=TaxPaymentStatus.PENDING,
            )

    def test_rejects_zero_amount(self):
        with pytest.raises(pydantic.ValidationError):
            TaxPayment(
                declaration_id=1,
                tax_type=TaxType.VAT_DEDUCTION,
                amount=Decimal("0"),
                payment_date=date(2024, 6, 30),
                due_date=date(2024, 7, 20),
                budget_account="1701",
                payment_status=TaxPaymentStatus.PENDING,
            )

    def test_quantizes_amount(self):
        payment = TaxPayment(
            declaration_id=1,
            tax_type=TaxType.VAT_DEDUCTION,
            amount=Decimal("5000.123"),
            payment_date=date(2024, 6, 30),
            due_date=date(2024, 7, 20),
            budget_account="1701",
            payment_status=TaxPaymentStatus.PENDING,
        )
        assert payment.amount == Decimal("5000.12")

    def test_early_payment_accepted(self):
        TaxPayment(
            declaration_id=1,
            tax_type=TaxType.VAT_DEDUCTION,
            amount=Decimal("1000000"),
            payment_date=date(2024, 6, 15),
            due_date=date(2024, 7, 20),
            budget_account="1701",
            payment_status=TaxPaymentStatus.PENDING,
        )


# ═══════════════════════════════════════════════════════════════════
# TaxAdjustment — state transitions & edge cases
# ═══════════════════════════════════════════════════════════════════

class TestTaxAdjustmentEdgeCases:
    def test_cancellation_adjustment_type(self):
        adj = TaxAdjustment(
            declaration_id=1,
            adjustment_type=TaxAdjustmentType.CANCELLATION,
            reason="Duplicate filing",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("0"),
            status=TaxAdjustmentStatus.PENDING,
        )
        assert adj.adjustment_type == TaxAdjustmentType.CANCELLATION

    def test_zero_difference(self):
        adj = TaxAdjustment(
            declaration_id=1,
            adjustment_type=TaxAdjustmentType.CORRECTION,
            reason="No change needed",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("1000000"),
            status=TaxAdjustmentStatus.PENDING,
        )
        assert adj.difference_amount == Decimal("0")

    def test_adjustment_with_penalties(self):
        adj = TaxAdjustment(
            declaration_id=1,
            adjustment_type=TaxAdjustmentType.INCREASE,
            reason="Underreported revenue",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("1500000"),
            penalty_interest=Decimal("50000"),
            penalty=Decimal("100000"),
            status=TaxAdjustmentStatus.PENDING,
        )
        assert adj.penalty_interest == Decimal("50000")
        assert adj.penalty == Decimal("100000")

    def test_adjustment_reason_whitespace_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            TaxAdjustment(
                declaration_id=1,
                adjustment_type=TaxAdjustmentType.CORRECTION,
                reason="   ",
                original_amount=Decimal("1000000"),
                adjusted_amount=Decimal("1200000"),
                status=TaxAdjustmentStatus.PENDING,
            )

    def test_adjustment_reason_too_long(self):
        with pytest.raises(pydantic.ValidationError):
            TaxAdjustment(
                declaration_id=1,
                adjustment_type=TaxAdjustmentType.CORRECTION,
                reason="x" * 1001,
                original_amount=Decimal("1000000"),
                adjusted_amount=Decimal("1200000"),
                status=TaxAdjustmentStatus.PENDING,
            )


# ═══════════════════════════════════════════════════════════════════
# EInvoice & EInvoiceLine — full validation suite
# ═══════════════════════════════════════════════════════════════════

class TestEInvoiceEdgeCases:
    def test_rejects_invalid_seller_tax_code(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoice(
                invoice_number="INV001",
                invoice_series="1K24TQ",
                invoice_date=date(2024, 6, 15),
                seller_tax_code="123",
                seller_name="Test Co",
                subtotal=Decimal("1000000"),
            )

    def test_accepts_tax_code_with_branch(self):
        inv = EInvoice(
            invoice_number="INV002",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            seller_tax_code="0101234567-001",
            seller_name="Test Co Branch",
            subtotal=Decimal("2000000"),
        )
        assert inv.seller_tax_code == "0101234567-001"

    def test_vat_rate_boundary_zero(self):
        inv = EInvoice(
            invoice_number="INV003",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            seller_tax_code="0101234567",
            seller_name="Test Co",
            subtotal=Decimal("1000000"),
            vat_rate=Decimal("0"),
        )
        assert inv.vat_rate == Decimal("0")

    def test_vat_rate_boundary_one(self):
        inv = EInvoice(
            invoice_number="INV004",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            seller_tax_code="0101234567",
            seller_name="Test Co",
            subtotal=Decimal("1000000"),
            vat_rate=Decimal("1"),
        )
        assert inv.vat_rate == Decimal("1")

    def test_vat_rate_negative_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoice(
                invoice_number="INV005",
                invoice_series="1K24TQ",
                invoice_date=date(2024, 6, 15),
                seller_tax_code="0101234567",
                seller_name="Test Co",
                subtotal=Decimal("1000000"),
                vat_rate=Decimal("-0.1"),
            )

    def test_replacement_invoice_type(self):
        inv = EInvoice(
            invoice_number="INV006",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            invoice_type=InvoiceType.REPLACEMENT,
            seller_tax_code="0101234567",
            seller_name="Test Co",
            subtotal=Decimal("1500000"),
            adjustment_ref_id=5,
            adjustment_type=EInvoiceAdjustmentType.REPLACE,
        )
        assert inv.invoice_type == InvoiceType.REPLACEMENT

    def test_foreign_currency_invoice(self):
        inv = EInvoice(
            invoice_number="INV007",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            seller_tax_code="0101234567",
            seller_name="Test Co",
            subtotal=Decimal("10000"),
            currency="USD",
            exchange_rate=Decimal("25400"),
        )
        assert inv.currency == "USD"
        assert inv.exchange_rate == Decimal("25400")

    def test_invoice_with_discount(self):
        inv = EInvoice(
            invoice_number="INV008",
            invoice_series="1K24TQ",
            invoice_date=date(2024, 6, 15),
            seller_tax_code="0101234567",
            seller_name="Test Co",
            subtotal=Decimal("1000000"),
            discount_amount=Decimal("50000"),
            vat_rate=Decimal("0.1"),
        )
        assert inv.discount_amount == Decimal("50000")


class TestEInvoiceLineEdgeCases:
    def test_create_einvoice_line(self):
        line = EInvoiceLine(
            invoice_id=1,
            line_number=1,
            product_name="Máy tính xách tay",
            quantity=Decimal("2"),
            unit_price=Decimal("15000000"),
            vat_rate=Decimal("0.1"),
        )
        assert line.line_number == 1
        assert line.quantity == Decimal("2")

    def test_rejects_zero_quantity(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoiceLine(
                invoice_id=1,
                line_number=1,
                product_name="Test",
                quantity=Decimal("0"),
                unit_price=Decimal("1000"),
            )

    def test_rejects_negative_quantity(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoiceLine(
                invoice_id=1,
                line_number=1,
                product_name="Test",
                quantity=Decimal("-1"),
                unit_price=Decimal("1000"),
            )

    def test_rejects_negative_unit_price(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoiceLine(
                invoice_id=1,
                line_number=1,
                product_name="Test",
                quantity=Decimal("1"),
                unit_price=Decimal("-1000"),
            )

    def test_rejects_excessive_discount_rate(self):
        with pytest.raises(pydantic.ValidationError):
            EInvoiceLine(
                invoice_id=1,
                line_number=1,
                product_name="Test",
                quantity=Decimal("1"),
                unit_price=Decimal("1000"),
                discount_rate=Decimal("1.5"),
            )

    def test_quantizes_unit_price(self):
        line = EInvoiceLine(
            invoice_id=1,
            line_number=1,
            product_name="Test",
            quantity=Decimal("1"),
            unit_price=Decimal("1000.456"),
        )
        assert line.unit_price == Decimal("1000.46")

    def test_quantizes_vat_rate(self):
        line = EInvoiceLine(
            invoice_id=1,
            line_number=1,
            product_name="Test",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            vat_rate=Decimal("0.12345"),
        )
        assert line.vat_rate == Decimal("0.1234")


# ═══════════════════════════════════════════════════════════════════
# TaxIncentive — date range & code enforcement
# ═══════════════════════════════════════════════════════════════════

class TestTaxIncentiveEdgeCases:
    def test_rejects_valid_to_before_valid_from(self):
        with pytest.raises(ValidationError):
            TaxIncentive(
                tax_type=TaxType.CIT,
                incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
                code="UT_CNC",
                name="Khu công nghệ cao",
                legal_basis="Luật số 71/2014/QH13",
                rate_value=Decimal("10"),
                is_percentage=True,
                valid_from=date(2026, 6, 1),
                valid_to=date(2026, 1, 1),
            )

    def test_rejects_valid_to_equal_valid_from(self):
        with pytest.raises(ValidationError):
            TaxIncentive(
                tax_type=TaxType.CIT,
                incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
                code="UT_EQUAL",
                name="Test",
                legal_basis="Test law",
                rate_value=Decimal("10"),
                is_percentage=True,
                valid_from=date(2026, 6, 1),
                valid_to=date(2026, 6, 1),
            )

    def test_enforces_code_uppercase(self):
        incentive = TaxIncentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
            code="ut_cnc",
            name="Test",
            legal_basis="Test law",
            rate_value=Decimal("10"),
            is_percentage=True,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
        )
        assert incentive.code == "UT_CNC"

    def test_tax_credit_incentive_type(self):
        TaxIncentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.TAX_CREDIT,
            code="TC_01",
            name="Tax Credit",
            legal_basis="Law X",
            rate_value=Decimal("5000000"),
            is_percentage=False,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
        )


# ═══════════════════════════════════════════════════════════════════
# TaxSchedule — period & status edge cases
# ═══════════════════════════════════════════════════════════════════

class TestTaxScheduleEdgeCases:
    def test_schedule_with_quarter_period(self):
        schedule = TaxSchedule(
            tax_type=TaxType.CIT,
            period_year=2024,
            period_quarter=1,
            due_date=date(2024, 4, 30),
            status=ScheduleStatus.PENDING,
        )
        assert schedule.period_quarter == 1
        assert schedule.period_month is None

    def test_schedule_year_out_of_range(self):
        with pytest.raises(pydantic.ValidationError):
            TaxSchedule(
                tax_type=TaxType.VAT_DEDUCTION,
                period_year=1999,
                period_month=1,
                due_date=date(1999, 2, 20),
            )

    def test_schedule_with_assigned_user(self):
        schedule = TaxSchedule(
            tax_type=TaxType.VAT_DEDUCTION,
            period_year=2024,
            period_month=6,
            due_date=date(2024, 7, 20),
            assigned_to="accountant01",
            notes="Monthly VAT filing",
        )
        assert schedule.assigned_to == "accountant01"


# ═══════════════════════════════════════════════════════════════════
# Use Case — declaration state transitions
# ═══════════════════════════════════════════════════════════════════

class TestTaxUseCaseStateTransitions:
    def _create_decl(self, uc, period_month=6):
        return uc.create_declaration(
            tax_type=TaxType.VAT_DEDUCTION,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="01/GTGT",
            period_year=2024,
            period_month=period_month,
        )

    def test_submit_calculated_declaration(self, uc):
        result = self._create_decl(uc, 6)
        assert result.is_success()
        decl = result.get_data()

        submit_result = uc.update_declaration(decl.id, status=DeclarationStatus.SUBMITTED)
        assert submit_result.is_success()
        assert submit_result.get_data().status == DeclarationStatus.SUBMITTED

    def test_accept_declaration(self, uc):
        result = self._create_decl(uc, 7)
        decl = result.get_data()
        uc.update_declaration(decl.id, status=DeclarationStatus.SUBMITTED)
        accept_result = uc.update_declaration(decl.id, status=DeclarationStatus.ACCEPTED)
        assert accept_result.is_success()

    def test_reject_declaration(self, uc):
        result = self._create_decl(uc, 8)
        decl = result.get_data()
        uc.update_declaration(decl.id, status=DeclarationStatus.SUBMITTED)
        reject_result = uc.update_declaration(decl.id, status=DeclarationStatus.REJECTED,
                                              gdt_error_code="ERR_001")
        assert reject_result.is_success()

    def test_amend_accepted_declaration(self, uc):
        result = self._create_decl(uc, 9)
        decl = result.get_data()
        uc.update_declaration(decl.id, status=DeclarationStatus.SUBMITTED)
        uc.update_declaration(decl.id, status=DeclarationStatus.ACCEPTED)
        amend_result = uc.update_declaration(decl.id, status=DeclarationStatus.AMENDED)
        assert amend_result.is_success()

    def test_cancel_draft_declaration(self, uc):
        result = self._create_decl(uc, 10)
        decl = result.get_data()
        cancel_result = uc.update_declaration(decl.id, status=DeclarationStatus.CANCELLED)
        assert cancel_result.is_success()

    def test_submit_nonexistent_declaration(self, uc):
        result = uc.update_declaration(99999, status=DeclarationStatus.SUBMITTED)
        assert result.is_failure()

    def test_update_nonexistent_line(self, uc):
        result = uc.update_line(99999, label="Updated")
        assert result.is_failure()

    def test_delete_nonexistent_payment(self, uc):
        result = uc.delete_payment(99999)
        assert result.is_failure()


# ═══════════════════════════════════════════════════════════════════
# Multi-entity interactions
# ═══════════════════════════════════════════════════════════════════

class TestMultiEntityInteractions:
    def test_calculate_vat_deduction_empty_lines(self, uc, session):
        result = uc.create_declaration(
            tax_type=TaxType.VAT_DEDUCTION,
            form_code="01/GTGT",
            period_year=2024,
            period_month=6,
        )
        assert result.is_success()
        decl_id = result.get_data().id
        result = uc.calculate_vat(
            decl_id=decl_id,
            method=VATCalculationMethod.DEDUCTION,
            input_lines=[],
            output_lines=[],
        )
        assert result.is_success()
        data = result.get_data()
        assert Decimal(data["total_payable"]) == Decimal("0")

    def test_calculate_vat_direct_method(self, uc, session):
        result = uc.create_declaration(
            tax_type=TaxType.VAT_DIRECT,
            form_code="04/GTGT",
            period_year=2024,
            period_quarter=2,
        )
        assert result.is_success()
        decl_id = result.get_data().id
        result = uc.calculate_vat(
            decl_id=decl_id,
            method=VATCalculationMethod.DIRECT,
            output_lines=[{"amount": "100000000"}],
        )
        assert result.is_success()

    def test_calculate_vat_for_nonexistent_declaration(self, uc):
        result = uc.calculate_vat(decl_id=99999)
        assert result.is_failure()

    def test_get_due_reminders_no_upcoming(self, uc):
        reminders = uc.get_due_reminders(days_ahead=1)
        assert len(reminders) == 0
