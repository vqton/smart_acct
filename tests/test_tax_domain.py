import sys
sys.path.insert(0, "/home/projects/smart_acct")

import pytest
from datetime import date, datetime
from decimal import Decimal
from pydantic import ValidationError as PydanticValidationError
from domain import (
    TaxType, DeclarationType, DeclarationStatus, TaxPaymentStatus,
    InvoiceStatus, TaxAdjustmentType, TaxIncentiveType,
    TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive,
    EInvoice, EInvoiceLine, TaxSchedule,
    VASValidationError,
)


class TestTaxType:
    def test_values(self):
        values = [e.value for e in TaxType]
        assert "vat_deduction" in values
        assert "cit" in values
        assert "pit" in values
        assert "license" in values
        assert "foreign_contractor" in values

    def test_vat_deduction_member(self):
        assert TaxType.VAT_DEDUCTION.value == "vat_deduction"

    def test_cit_member(self):
        assert TaxType.CIT.value == "cit"


class TestDeclarationType:
    def test_values(self):
        values = [e.value for e in DeclarationType]
        assert "original" in values
        assert "supplemental" in values
        assert "finalization" in values


class TestDeclarationStatus:
    def test_values(self):
        values = [e.value for e in DeclarationStatus]
        assert "draft" in values
        assert "submitted" in values
        assert "accepted" in values
        assert "rejected" in values
        assert "amended" in values


class TestInvoiceStatus:
    def test_values(self):
        values = [e.value for e in InvoiceStatus]
        assert "created" in values
        assert "signed" in values
        assert "sent" in values
        assert "cancelled" in values
        assert "replaced" in values
        assert "adjusted" in values


class TestTaxDeclaration:
    def test_create_valid_dedaration(self):
        decl = TaxDeclaration(
            tax_type=TaxType.VAT_DEDUCTION,
            form_code="01/GTGT",
            period_year=2026,
            period_month=4,
        )
        assert decl.tax_type == TaxType.VAT_DEDUCTION
        assert decl.form_code == "01/GTGT"
        assert decl.period_year == 2026
        assert decl.period_month == 4
        assert decl.declaration_type == DeclarationType.ORIGINAL
        assert decl.status == DeclarationStatus.DRAFT

    def test_create_cit_declaration(self):
        decl = TaxDeclaration(
            tax_type=TaxType.CIT,
            form_code="03/TNDN",
            period_year=2026,
            declaration_type=DeclarationType.FINALIZATION,
        )
        assert decl.tax_type == TaxType.CIT
        assert decl.form_code == "03/TNDN"
        assert decl.declaration_type == DeclarationType.FINALIZATION

    def test_create_pit_declaration(self):
        decl = TaxDeclaration(
            tax_type=TaxType.PIT,
            form_code="02/KK-TNCN",
            period_year=2026,
            period_quarter=1,
        )
        assert decl.tax_type == TaxType.PIT
        assert decl.period_quarter == 1

    def test_rejects_invalid_year(self):
        with pytest.raises(PydanticValidationError):
            TaxDeclaration(
                tax_type=TaxType.VAT_DEDUCTION,
                form_code="01/GTGT",
                period_year=1999,
            )

    def test_rejects_empty_form_code(self):
        with pytest.raises(VASValidationError):
            TaxDeclaration(
                tax_type=TaxType.VAT_DEDUCTION,
                form_code="",
                period_year=2026,
            )

    def test_rejects_invalid_month(self):
        with pytest.raises(PydanticValidationError):
            TaxDeclaration(
                tax_type=TaxType.VAT_DEDUCTION,
                form_code="01/GTGT",
                period_year=2026,
                period_month=13,
            )

    def test_supplemental_declaration(self):
        decl = TaxDeclaration(
            tax_type=TaxType.VAT_DEDUCTION,
            form_code="01/GTGT",
            period_year=2025,
            period_month=11,
            declaration_type=DeclarationType.SUPPLEMENTAL,
            status=DeclarationStatus.AMENDED,
        )
        assert decl.declaration_type == DeclarationType.SUPPLEMENTAL
        assert decl.status == DeclarationStatus.AMENDED


class TestTaxPayment:
    def test_create_valid_payment(self):
        payment = TaxPayment(
            declaration_id=1,
            tax_type=TaxType.CIT,
            amount=Decimal("50000000"),
            payment_date=date(2026, 3, 31),
            due_date=date(2026, 3, 31),
            budget_account="1702",
        )
        assert payment.amount == Decimal("50000000")
        assert payment.budget_account == "1702"
        assert payment.payment_status == TaxPaymentStatus.PENDING
        assert payment.payment_method == "etax"

    def test_rejects_negative_amount(self):
        with pytest.raises(PydanticValidationError):
            TaxPayment(
                declaration_id=1,
                tax_type=TaxType.VAT_DEDUCTION,
                amount=Decimal("-1000"),
                payment_date=date(2026, 4, 20),
                due_date=date(2026, 4, 20),
                budget_account="1701",
            )

    def test_rejects_invalid_budget_account(self):
        with pytest.raises(VASValidationError):
            TaxPayment(
                declaration_id=1,
                tax_type=TaxType.VAT_DEDUCTION,
                amount=Decimal("1000000"),
                payment_date=date(2026, 4, 20),
                due_date=date(2026, 4, 20),
                budget_account="9999",
            )


class TestTaxAdjustment:
    def test_create_adjustment(self):
        adj = TaxAdjustment(
            original_declaration_id=1,
            supplemental_declaration_id=2,
            adjustment_type=TaxAdjustmentType.INCREASE,
            reason="Khai bổ sung hóa đơn đầu vào quên kê khai tháng 11",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("1500000"),
        )
        assert adj.difference == Decimal("500000")
        assert adj.approval_status == "pending"
        assert adj.adjustment_type == TaxAdjustmentType.INCREASE

    def test_decrease_adjustment(self):
        adj = TaxAdjustment(
            original_declaration_id=1,
            supplemental_declaration_id=3,
            adjustment_type=TaxAdjustmentType.DECREASE,
            reason="Điều chỉnh giảm do hủy hóa đơn",
            original_amount=Decimal("2000000"),
            adjusted_amount=Decimal("1000000"),
        )
        assert adj.difference == Decimal("-1000000")

    def test_rejects_empty_reason(self):
        with pytest.raises((VASValidationError, PydanticValidationError)):
            TaxAdjustment(
                original_declaration_id=1,
                supplemental_declaration_id=2,
                adjustment_type=TaxAdjustmentType.CORRECTION,
                reason="",
                original_amount=Decimal("1000000"),
                adjusted_amount=Decimal("1000000"),
            )


class TestEInvoice:
    def test_create_valid_invoice(self):
        inv = EInvoice(
            invoice_number="0000001",
            invoice_series="1C26TAA",
            invoice_date=date(2026, 6, 1),
            seller_tax_code="0101234567",
            seller_name="Công ty TNHH ABC",
            buyer_name="Công ty XYZ",
            subtotal=Decimal("10000000"),
            vat_rate=Decimal("10"),
            vat_amount=Decimal("1000000"),
            grand_total=Decimal("11000000"),
        )
        assert inv.invoice_number == "0000001"
        assert inv.seller_tax_code == "0101234567"
        assert inv.grand_total == Decimal("11000000")
        assert inv.status == InvoiceStatus.CREATED
        assert inv.currency == "VND"

    def test_create_with_buyer_tax_code(self):
        inv = EInvoice(
            invoice_number="0000002",
            invoice_series="1C26TAA",
            invoice_date=date(2026, 6, 15),
            seller_tax_code="0101234567",
            seller_name="Công ty TNHH ABC",
            buyer_tax_code="0207654321",
            buyer_name="Công ty TNHH XYZ",
            subtotal=Decimal("5000000"),
            vat_rate=Decimal("8"),
            vat_amount=Decimal("400000"),
            grand_total=Decimal("5400000"),
        )
        assert inv.buyer_tax_code == "0207654321"

    def test_adjustment_invoice(self):
        inv = EInvoice(
            invoice_number="ADJ001",
            invoice_series="1C26TAA",
            invoice_date=date(2026, 7, 1),
            invoice_type="adjustment",
            seller_tax_code="0101234567",
            seller_name="Công ty TNHH ABC",
            buyer_tax_code="0207654321",
            buyer_name="Công ty TNHH XYZ",
            subtotal=Decimal("-1000000"),
            vat_rate=Decimal("10"),
            vat_amount=Decimal("-100000"),
            grand_total=Decimal("-1100000"),
            adjustment_ref_id=1,
            adjustment_type="decrease",
            adjustment_reason="Hàng bán bị trả lại",
            original_invoice_ref="0000001",
        )
        assert inv.invoice_type == "adjustment"
        assert inv.adjustment_type == "decrease"
        assert inv.original_invoice_ref == "0000001"

    def test_rejects_empty_seller_tax_code(self):
        with pytest.raises(PydanticValidationError):
            EInvoice(
                invoice_number="0000003",
                invoice_series="1C26TAA",
                invoice_date=date(2026, 6, 1),
                seller_tax_code="",
                seller_name="Test Co",
                subtotal=Decimal("1000000"),
                grand_total=Decimal("1000000"),
            )

    def test_vat_rate_validation(self):
        with pytest.raises(PydanticValidationError):
            EInvoice(
                invoice_number="0000004",
                invoice_series="1C26TAA",
                invoice_date=date(2026, 6, 1),
                seller_tax_code="0101234567",
                seller_name="Test Co",
                subtotal=Decimal("1000000"),
                vat_rate=Decimal("150"),
                grand_total=Decimal("1000000"),
            )


class TestTaxIncentive:
    def test_create_incentive(self):
        inc = TaxIncentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
            code="UT_CNC",
            name="Thuế suất ưu đãi công nghệ cao",
            legal_basis="Luật Thuế TNDN 67/2025/QH15 Điều 15",
            rate_value=Decimal("10"),
            valid_from=date(2026, 1, 1),
        )
        assert inc.code == "UT_CNC"
        assert inc.rate_value == Decimal("10")
        assert inc.is_percentage is True
        assert inc.status == "active"

    def test_tax_holiday_incentive(self):
        inc = TaxIncentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.TAX_HOLIDAY,
            code="UT_MD4",
            name="Miễn thuế 4 năm",
            legal_basis="Luật 67/2025 Điều 17",
            rate_value=Decimal("100"),
            valid_from=date(2026, 1, 1),
            valid_to=date(2029, 12, 31),
            max_duration_months=48,
        )
        assert inc.incentive_type == TaxIncentiveType.TAX_HOLIDAY
        assert inc.max_duration_months == 48


class TestTaxLine:
    def test_create_line(self):
        line = TaxLine(
            declaration_id=1,
            line_code="[21]",
            label="Doanh thu bán hàng hóa",
            amount=Decimal("100000000"),
        )
        assert line.line_code == "[21]"
        assert line.amount == Decimal("100000000")
        assert line.is_calculated is True

    def test_manual_line(self):
        line = TaxLine(
            declaration_id=1,
            line_code="[22]",
            label="Điều chỉnh tăng doanh thu",
            amount=Decimal("5000000"),
            is_calculated=False,
            sort_order=5,
        )
        assert line.is_calculated is False
        assert line.sort_order == 5

    def test_rejects_empty_line_code(self):
        with pytest.raises((VASValidationError, PydanticValidationError)):
            TaxLine(
                declaration_id=1,
                line_code="",
                label="Test",
                amount=Decimal("0"),
            )
