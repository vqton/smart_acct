from decimal import Decimal
from datetime import date, datetime, timezone
import pytest

from domain.ap import (
    Vendor, VendorType, VendorGroup, VendorStatus,
    APInvoice, APInvoiceType, APInvoiceStatus, APInvoiceLine,
    APPayment, APPaymentStatus, APPaymentMethod,
    APPaymentAllocation, VendorPrepayment, PrepaymentStatus,
    APProvision, ProvisionStatus,
    FCTDeclaration, FCTMethod, FCTStatus,
    IntercompanyInvoice,
)
from pydantic import ValidationError as PydanticValidationError
from domain.common import _quantize_vnd


class TestVendor:
    def test_create_valid_vendor(self):
        v = Vendor(vendor_code="V001", vendor_name="ABC Co Ltd")
        assert v.id is None
        assert v.vendor_code == "V001"
        assert v.vendor_name == "ABC Co Ltd"
        assert v.vendor_type == VendorType.ENTERPRISE
        assert v.status == VendorStatus.ACTIVE
        assert v.currency == "VND"
        assert v.payment_terms == "net_30"

    def test_vendor_with_full_fields(self):
        v = Vendor(
            vendor_code="V002", vendor_name="XYZ Corp",
            tax_code="0123456789", vendor_type=VendorType.FOREIGN,
            currency="USD", credit_limit=Decimal("500000000"),
            foreign_ct_type="deduction", foreign_vat_rate=Decimal("0.05"),
            foreign_cit_rate=Decimal("0.10"),
        )
        assert v.tax_code == "0123456789"
        assert v.foreign_ct_type == "deduction"
        assert v.credit_limit == Decimal("500000000.00")

    def test_vendor_credit_limit_quantize(self):
        v = Vendor(vendor_code="V003", vendor_name="Test", credit_limit=Decimal("1000000.555"))
        assert v.credit_limit == Decimal("1000000.56")

    def test_vendor_code_too_long(self):
        with pytest.raises(PydanticValidationError):
            Vendor(vendor_code="A" * 21, vendor_name="Test")


class TestAPInvoice:
    def test_create_valid_invoice(self):
        inv = APInvoice(
            invoice_number="INV-001",
            vendor_id=1,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("10000000"),
            total_amount=Decimal("11000000"),
            balance_due=Decimal("11000000"),
        )
        assert inv.invoice_number == "INV-001"
        assert inv.status == APInvoiceStatus.DRAFT
        assert inv.invoice_type == APInvoiceType.NON_PO
        assert inv.coa_code == "331"

    def test_invoice_with_vat(self):
        inv = APInvoice(
            invoice_number="INV-002",
            vendor_id=1,
            invoice_date=date(2026, 6, 15),
            due_date=date(2026, 7, 15),
            amount=Decimal("20000000"),
            tax_amount=Decimal("2000000"),
            total_amount=Decimal("22000000"),
            balance_due=Decimal("22000000"),
        )
        assert inv.tax_amount == Decimal("2000000.00")
        assert inv.total_amount == Decimal("22000000.00")

    def test_invoice_with_lines(self):
        lines = [
            APInvoiceLine(line_number=1, description="Item A", quantity=Decimal("10"),
                          unit_price=Decimal("100000"), line_amount=Decimal("1000000"),
                          tax_rate=Decimal("0.10"), tax_amount=Decimal("100000")),
            APInvoiceLine(line_number=2, description="Item B", quantity=Decimal("5"),
                          unit_price=Decimal("200000"), line_amount=Decimal("1000000"),
                          tax_rate=Decimal("0.08"), tax_amount=Decimal("80000")),
        ]
        inv = APInvoice(
            invoice_number="INV-003",
            vendor_id=1,
            invoice_date=date(2026, 6, 20),
            due_date=date(2026, 7, 20),
            amount=Decimal("2000000"),
            total_amount=Decimal("2180000"),
            balance_due=Decimal("2180000"),
            lines=lines,
        )
        assert len(inv.lines) == 2
        assert inv.lines[0].line_amount == Decimal("1000000.00")
        assert inv.lines[1].tax_rate == Decimal("0.08")

    def test_invoice_amounts_quantized(self):
        inv = APInvoice(
            invoice_number="INV-004",
            vendor_id=1,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("10000000.333"),
            total_amount=Decimal("11000000.555"),
            balance_due=Decimal("11000000.555"),
        )
        assert inv.amount == Decimal("10000000.33")
        assert inv.total_amount == Decimal("11000000.56")

    def test_invoice_status_transitions(self):
        assert APInvoiceStatus.DRAFT == "draft"
        assert APInvoiceStatus.SUBMITTED == "submitted"
        assert APInvoiceStatus.APPROVED == "approved"
        assert APInvoiceStatus.PAID_FULL == "paid_full"
        assert APInvoiceStatus.CANCELLED == "cancelled"

    def test_invoice_types(self):
        assert APInvoiceType.PO_BASED == "po_based"
        assert APInvoiceType.NON_PO == "non_po"
        assert APInvoiceType.PREPAYMENT == "prepayment"


class TestAPInvoiceLine:
    def test_create_line(self):
        line = APInvoiceLine(line_number=1, description="Service Fee",
                             quantity=Decimal("1"), unit_price=Decimal("5000000"),
                             line_amount=Decimal("5000000"), tax_rate=Decimal("0.10"),
                             tax_amount=Decimal("500000"), po_line_number=10)
        assert line.description == "Service Fee"
        assert line.po_line_number == 10
        assert line.line_amount == Decimal("5000000.00")

    def test_line_amount_quantized(self):
        line = APInvoiceLine(line_number=1, description="Test",
                             quantity=Decimal("3.333"), unit_price=Decimal("1000.555"),
                             line_amount=Decimal("3335.555"), tax_rate=Decimal("0.10"),
                             tax_amount=Decimal("333.555"))
        assert line.unit_price == Decimal("1000.56")
        assert line.quantity == Decimal("3.33")


class TestAPPayment:
    def test_create_valid_payment(self):
        p = APPayment(
            payment_number="PMT-001",
            vendor_id=1,
            payment_date=date(2026, 7, 1),
            amount=Decimal("11000000"),
            net_amount=Decimal("11000000"),
            payment_method=APPaymentMethod.BANK_TRANSFER,
        )
        assert p.payment_number == "PMT-001"
        assert p.status == APPaymentStatus.DRAFT

    def test_payment_with_discount(self):
        p = APPayment(
            payment_number="PMT-002",
            vendor_id=1,
            payment_date=date(2026, 7, 1),
            amount=Decimal("11000000"),
            discount_taken=Decimal("200000"),
            net_amount=Decimal("10800000"),
            payment_method=APPaymentMethod.BANK_TRANSFER,
        )
        assert p.discount_taken == Decimal("200000.00")
        assert p.net_amount == Decimal("10800000.00")

    def test_payment_methods(self):
        assert APPaymentMethod.CASH == "cash"
        assert APPaymentMethod.BANK_TRANSFER == "bank_transfer"
        assert APPaymentMethod.CHEQUE == "cheque"
        assert APPaymentMethod.CARD == "card"

    def test_payment_status_transitions(self):
        assert APPaymentStatus.DRAFT == "draft"
        assert APPaymentStatus.PROPOSED == "proposed"
        assert APPaymentStatus.APPROVED == "approved"
        assert APPaymentStatus.EXECUTED == "executed"
        assert APPaymentStatus.FAILED == "failed"


class TestAPPaymentAllocation:
    def test_create_allocation(self):
        alloc = APPaymentAllocation(ap_payment_id=1, ap_invoice_id=1, allocated_amount=Decimal("5000000"))
        assert alloc.allocated_amount == Decimal("5000000.00")
        assert alloc.is_adjustment is False


class TestVendorPrepayment:
    def test_create_prepayment(self):
        pp = VendorPrepayment(
            vendor_id=1, amount=Decimal("50000000"),
            unapplied_balance=Decimal("50000000"),
            payment_date=date(2026, 6, 1),
        )
        assert pp.status == PrepaymentStatus.PENDING
        assert pp.amount == Decimal("50000000.00")

    def test_prepayment_after_partial_apply(self):
        pp = VendorPrepayment(
            vendor_id=1, amount=Decimal("50000000"),
            unapplied_balance=Decimal("20000000"),
            payment_date=date(2026, 6, 1),
            status=PrepaymentStatus.PENDING,
        )
        assert pp.unapplied_balance == Decimal("20000000.00")


class TestAPProvision:
    def test_create_provision(self):
        pr = APProvision(
            vendor_id=1, period="2026-06",
            provision_percent=Decimal("0.30"), overdue_days=180,
            invoice_total=Decimal("100000000"),
            provision_amount=Decimal("30000000"),
        )
        assert pr.status == ProvisionStatus.ACTIVE
        assert pr.provision_amount == Decimal("30000000.00")

    def test_provision_circular_48_rates(self):
        for overdue_days, expected_pct in [(180, 0.30), (365, 0.50), (730, 0.70), (1095, 1.00)]:
            total = Decimal("100000000")
            pr = APProvision(
                vendor_id=1, period="2026-06",
                provision_percent=Decimal(str(expected_pct)),
                overdue_days=overdue_days,
                invoice_total=total,
                provision_amount=total * Decimal(str(expected_pct)),
            )
            assert pr.provision_percent == Decimal(str(expected_pct))


class TestFCTDeclaration:
    def test_create_fct_deduction(self):
        fct = FCTDeclaration(
            vendor_id=1, period="2026-06", invoice_id=1,
            fct_method=FCTMethod.DEDUCTION,
            vat_rate=Decimal("0.05"), cit_rate=Decimal("0.10"),
            gross_amount=Decimal("100000000"),
            vat_amount=Decimal("5000000"),
            cit_amount=Decimal("9500000"),
            net_amount=Decimal("85500000"),
            due_date=date(2026, 7, 1),
        )
        assert fct.fct_method == FCTMethod.DEDUCTION
        assert fct.vat_amount == Decimal("5000000.00")
        assert fct.net_amount == Decimal("85500000.00")
        assert fct.status == FCTStatus.PENDING

    def test_fct_methods(self):
        assert FCTMethod.DIRECT == "direct"
        assert FCTMethod.DEDUCTION == "deduction"
        assert FCTMethod.HYBRID == "hybrid"

    def test_fct_statuses(self):
        assert FCTStatus.PENDING == "pending"
        assert FCTStatus.DECLARED == "declared"
        assert FCTStatus.REMITTED == "remitted"


class TestIntercompanyInvoice:
    def test_create_ic_invoice(self):
        ic = IntercompanyInvoice(
            from_entity_code="HO", to_entity_code="BRANCH1",
            invoice_number="IC-001", invoice_date=date(2026, 6, 30),
            amount=Decimal("50000000"), description="Management fee",
        )
        assert ic.from_entity_code == "HO"
        assert ic.to_entity_code == "BRANCH1"
        assert ic.currency == "VND"

    def test_ic_amount_quantized(self):
        ic = IntercompanyInvoice(
            from_entity_code="A", to_entity_code="B",
            invoice_number="IC-002", invoice_date=date(2026, 6, 30),
            amount=Decimal("12345678.123"), description="Test",
        )
        assert ic.amount == Decimal("12345678.12")
