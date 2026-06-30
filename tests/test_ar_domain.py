from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.ar import (
    CustomerType, CustomerGroup, CustomerStatus,
    ARInvoiceType, ARInvoiceStatus, ARPaymentMethod,
    ARAllocationStatus, ARDunningLevel, WriteOffRequestStatus,
    Customer, InvoiceLine, ARInvoice, ARPayment,
    ARPaymentAllocation, GLAllocation, ARAgingSnapshot,
    ARDunningLog, BadDebtProvision, BadDebtWriteOffRequest,
    CEIReport,
)
from domain.common import AccountError


class TestAREnums:
    def test_customer_type_values(self):
        assert CustomerType.INDIVIDUAL.value == "individual"
        assert CustomerType.ENTERPRISE.value == "enterprise"
        assert CustomerType.GOVERNMENT.value == "government"
        assert CustomerType.FOREIGN.value == "foreign"

    def test_customer_group_values(self):
        assert CustomerGroup.DOMESTIC.value == "domestic"
        assert CustomerGroup.EXPORT.value == "export"
        assert CustomerGroup.GOVT.value == "govt"
        assert CustomerGroup.VIP.value == "vip"

    def test_customer_status_values(self):
        assert CustomerStatus.ACTIVE.value == "active"
        assert CustomerStatus.SUSPENDED.value == "suspended"
        assert CustomerStatus.BLOCKED.value == "blocked"
        assert CustomerStatus.ARCHIVED.value == "archived"

    def test_invoice_type_values(self):
        assert ARInvoiceType.SALES.value == "sales"
        assert ARInvoiceType.CREDIT_NOTE.value == "credit_note"
        assert ARInvoiceType.DEBIT_NOTE.value == "debit_note"

    def test_invoice_status_values(self):
        assert ARInvoiceStatus.DRAFT.value == "draft"
        assert ARInvoiceStatus.ISSUED.value == "issued"
        assert ARInvoiceStatus.PARTIALLY_PAID.value == "partially_paid"
        assert ARInvoiceStatus.PAID.value == "paid"
        assert ARInvoiceStatus.OVERDUE.value == "overdue"
        assert ARInvoiceStatus.CANCELLED.value == "cancelled"
        assert ARInvoiceStatus.WRITTEN_OFF.value == "written_off"

    def test_payment_method_values(self):
        assert ARPaymentMethod.CASH.value == "cash"
        assert ARPaymentMethod.BANK_TRANSFER.value == "bank_transfer"
        assert ARPaymentMethod.CHEQUE.value == "cheque"
        assert ARPaymentMethod.CREDIT_CARD.value == "credit_card"
        assert ARPaymentMethod.OFFLINE.value == "offline"


class TestCustomer:
    def test_valid_minimal(self):
        c = Customer(customer_code="KH001", customer_name="Nguyen Van A")
        assert c.customer_code == "KH001"
        assert c.customer_name == "Nguyen Van A"
        assert c.customer_type == CustomerType.ENTERPRISE
        assert c.customer_group == CustomerGroup.DOMESTIC
        assert c.status == CustomerStatus.ACTIVE
        assert c.country == "VN"
        assert c.credit_limit == Decimal("0")
        assert c.outstanding_balance == Decimal("0")

    def test_valid_all_fields(self):
        c = Customer(
            customer_code="KH002", customer_name="Cong ty TNHH ABC",
            legal_name="ABC Co., Ltd", tax_code="1234567890",
            customer_type=CustomerType.ENTERPRISE,
            customer_group=CustomerGroup.VIP,
            email="abc@example.com", phone="0909123456",
            address="123 Nguyen Hue", city="HCM",
            contact_person="Nguyen Van B",
            credit_limit=Decimal("100000000"),
            credit_limit_override=True,
            credit_limit_override_expires=date(2026, 12, 31),
            credit_rating="AAA",
            notes="Khach hang quan trong",
        )
        assert c.legal_name == "ABC Co., Ltd"
        assert c.tax_code == "1234567890"
        assert c.credit_limit == Decimal("100000000.00")
        assert c.credit_limit_override is True
        assert c.credit_rating == "AAA"

    def test_credit_limit_quantized(self):
        c = Customer(customer_code="KH003", customer_name="Test",
                      credit_limit=Decimal("50000.123"))
        assert c.credit_limit == Decimal("50000.12")

    def test_outstanding_balance_quantized(self):
        c = Customer(customer_code="KH004", customer_name="Test",
                      outstanding_balance=Decimal("100.456"))
        assert c.outstanding_balance == Decimal("100.46")


class TestInvoiceLine:
    def test_valid_minimal(self):
        line = InvoiceLine(
            line_number=1, description="Hang hoa A",
            quantity=Decimal("10"), unit_price=Decimal("50000"),
            line_amount=Decimal("500000"),
        )
        assert line.line_number == 1
        assert line.tax_rate == Decimal("0")
        assert line.tax_amount == Decimal("0")

    def test_valid_with_tax(self):
        line = InvoiceLine(
            line_number=1, description="Hang hoa B",
            quantity=Decimal("5"), unit_price=Decimal("100000"),
            line_amount=Decimal("500000"),
            tax_rate=Decimal("0.1"), tax_amount=Decimal("50000"),
            coa_code="511",
        )
        assert line.tax_rate == Decimal("0.10")
        assert line.coa_code == "511"

    def test_amounts_quantized(self):
        line = InvoiceLine(
            line_number=1, description="Test",
            quantity=Decimal("3.333"), unit_price=Decimal("100.123"),
            line_amount=Decimal("333.999"),
        )
        assert isinstance(line.quantity, Decimal)
        assert isinstance(line.unit_price, Decimal)


class TestARInvoice:
    def test_valid_minimal(self):
        inv = ARInvoice(
            invoice_number="INV001", customer_id=1,
            customer_code="KH001", customer_name="Test",
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("1000000"),
            total_amount=Decimal("1000000"),
            balance_due=Decimal("1000000"),
        )
        assert inv.invoice_type == ARInvoiceType.SALES
        assert inv.status == ARInvoiceStatus.DRAFT
        assert inv.dunning_level == 0
        assert inv.payment_terms_days == 30

    def test_valid_with_lines(self):
        line = InvoiceLine(
            line_number=1, description="SP A",
            quantity=Decimal("2"), unit_price=Decimal("500000"),
            line_amount=Decimal("1000000"),
        )
        inv = ARInvoice(
            invoice_number="INV002", customer_id=1,
            customer_code="KH001", customer_name="Test",
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("1000000"),
            tax_amount=Decimal("100000"),
            total_amount=Decimal("1100000"),
            paid_amount=Decimal("0"),
            written_off_amount=Decimal("0"),
            balance_due=Decimal("1100000"),
            discount_amount=Decimal("0"),
            lines=[line],
        )
        assert len(inv.lines) == 1
        assert inv.lines[0].description == "SP A"
        assert inv.total_amount == Decimal("1100000.00")

    def test_amounts_quantized(self):
        inv = ARInvoice(
            invoice_number="INV003", customer_id=1,
            customer_code="KH001", customer_name="Test",
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("1000.123"),
            total_amount=Decimal("1100.456"),
            balance_due=Decimal("1100.456"),
        )
        assert inv.amount == Decimal("1000.12")

    def test_debit_note_type(self):
        inv = ARInvoice(
            invoice_number="DN001", customer_id=1,
            customer_code="KH001", customer_name="Test",
            invoice_type=ARInvoiceType.DEBIT_NOTE,
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("500000"),
            total_amount=Decimal("550000"),
            balance_due=Decimal("550000"),
        )
        assert inv.invoice_type == ARInvoiceType.DEBIT_NOTE

    def test_credit_note_type(self):
        inv = ARInvoice(
            invoice_number="CN001", customer_id=1,
            customer_code="KH001", customer_name="Test",
            invoice_type=ARInvoiceType.CREDIT_NOTE,
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("-500000"),
            total_amount=Decimal("-500000"),
            balance_due=Decimal("-500000"),
        )
        assert inv.invoice_type == ARInvoiceType.CREDIT_NOTE

    def test_paid_status_fields(self):
        inv = ARInvoice(
            invoice_number="INV004", customer_id=1,
            customer_code="KH001", customer_name="Test",
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("2000000"),
            total_amount=Decimal("2000000"),
            paid_amount=Decimal("2000000"),
            balance_due=Decimal("0"),
        )
        assert inv.paid_amount == Decimal("2000000.00")
        assert inv.balance_due == Decimal("0.00")


class TestARPayment:
    def test_valid_minimal(self):
        p = ARPayment(
            payment_number="PMT001", invoice_id=1,
            payment_date=date(2026, 6, 15),
            amount=Decimal("1000000"),
            payment_method=ARPaymentMethod.CASH,
        )
        assert p.amount_applied == Decimal("0")
        assert p.amount_unapplied == Decimal("0")

    def test_valid_bank_transfer(self):
        p = ARPayment(
            payment_number="PMT002", invoice_id=1,
            payment_date=date(2026, 6, 15),
            amount=Decimal("5000000"),
            payment_method=ARPaymentMethod.BANK_TRANSFER,
            bank_account_id=1,
            coa_code="112",
            received_by="NV001",
        )
        assert p.bank_account_id == 1
        assert p.received_by == "NV001"

    def test_amounts_quantized(self):
        p = ARPayment(
            payment_number="PMT003", invoice_id=1,
            payment_date=date(2026, 6, 15),
            amount=Decimal("1000.456"),
            payment_method=ARPaymentMethod.CREDIT_CARD,
        )
        assert p.amount == Decimal("1000.46")


class TestARPaymentAllocation:
    def test_valid(self):
        a = ARPaymentAllocation(
            ar_payment_id=1, ar_invoice_id=1,
            allocated_amount=Decimal("500000"),
        )
        assert a.is_adjustment is False
        assert a.allocated_amount == Decimal("500000.00")

    def test_adjustment_flag(self):
        a = ARPaymentAllocation(
            ar_payment_id=1, ar_invoice_id=1,
            allocated_amount=Decimal("100000"),
            is_adjustment=True,
        )
        assert a.is_adjustment is True

    def test_amount_quantized(self):
        a = ARPaymentAllocation(
            ar_payment_id=1, ar_invoice_id=1,
            allocated_amount=Decimal("100.456"),
        )
        assert a.allocated_amount == Decimal("100.46")


class TestARAgingSnapshot:
    def test_valid(self):
        s = ARAgingSnapshot(
            period="2026-06",
            customer_id=1, customer_code="KH001",
            customer_name="Test",
            total_outstanding=Decimal("5000000"),
        )
        assert s.current_amount == Decimal("0")
        assert s.locked is False
        assert s.bucket_1_30 == Decimal("0")

    def test_with_buckets(self):
        s = ARAgingSnapshot(
            period="2026-06", customer_id=1,
            customer_code="KH001", customer_name="Test",
            current_amount=Decimal("1000000"),
            bucket_1_30=Decimal("2000000"),
            bucket_31_60=Decimal("3000000"),
            total_outstanding=Decimal("6000000"),
        )
        assert s.current_amount == Decimal("1000000.00")
        assert s.bucket_1_30 == Decimal("2000000.00")
        assert s.total_outstanding == Decimal("6000000.00")

    def test_locked_flag(self):
        s = ARAgingSnapshot(
            period="2026-06", customer_id=1,
            customer_code="KH001", customer_name="Test",
            total_outstanding=Decimal("0"),
            locked=True,
        )
        assert s.locked is True


class TestARDunningLog:
    def test_valid(self):
        log = ARDunningLog(
            ar_invoice_id=1, dunning_level=1,
            dunning_date=date(2026, 6, 15),
        )
        assert log.dunning_method == "email"

    def test_with_all_fields(self):
        log = ARDunningLog(
            ar_invoice_id=1, dunning_level=3,
            dunning_date=date(2026, 6, 15),
            dunning_method="phone",
            notes="Called customer, promised payment next week",
            performed_by="NV001",
        )
        assert log.dunning_method == "phone"
        assert log.performed_by == "NV001"


class TestBadDebtProvision:
    def test_valid(self):
        p = BadDebtProvision(
            customer_id=1, ar_invoice_id=1,
            period="2026-06",
            invoice_amount=Decimal("10000000"),
            provision_amount=Decimal("2000000"),
        )
        assert p.provision_percent == Decimal("0")
        assert p.is_written_off is False

    def test_with_percent(self):
        p = BadDebtProvision(
            customer_id=1, ar_invoice_id=1,
            period="2026-06", provision_percent=Decimal("0.2"),
            invoice_amount=Decimal("10000000"),
            provision_amount=Decimal("2000000"),
        )
        assert p.provision_percent == Decimal("0.20")
        assert p.invoice_amount == Decimal("10000000.00")

    def test_written_off_flag(self):
        p = BadDebtProvision(
            customer_id=1, ar_invoice_id=1,
            period="2026-06",
            invoice_amount=Decimal("5000000"),
            provision_amount=Decimal("5000000"),
            is_written_off=True,
        )
        assert p.is_written_off is True


class TestBadDebtWriteOffRequest:
    def test_valid(self):
        req = BadDebtWriteOffRequest(
            ar_invoice_id=1, customer_id=1,
            reason="Customer bankrupt",
        )
        assert req.status == WriteOffRequestStatus.PENDING_APPROVAL

    def test_with_all_fields(self):
        req = BadDebtWriteOffRequest(
            ar_invoice_id=1, customer_id=1,
            reason="Customer cannot be contacted",
            supporting_docs="docs/bankruptcy.pdf",
            created_by="NV001",
        )
        assert req.supporting_docs == "docs/bankruptcy.pdf"

    def test_approved_status(self):
        req = BadDebtWriteOffRequest(
            ar_invoice_id=1, customer_id=1,
            reason="Write off", status=WriteOffRequestStatus.APPROVED,
            approval_by="Manager",
        )
        assert req.status == WriteOffRequestStatus.APPROVED
        assert req.approval_by == "Manager"


class TestCEIReport:
    def test_valid(self):
        r = CEIReport(period="2026-06")
        assert r.beginning_ar == Decimal("0")
        assert r.cei == Decimal("0")
        assert r.dso == Decimal("0")
        assert r.days_in_period == 30

    def test_with_values(self):
        r = CEIReport(
            period="2026-06",
            beginning_ar=Decimal("10000000"),
            credit_sales=Decimal("50000000"),
            ending_ar=Decimal("8000000"),
            bad_debt=Decimal("500000"),
            cei=Decimal("95"),
            dso=Decimal("25"),
            days_in_period=30,
        )
        assert r.cei == Decimal("95.00")
        assert r.dso == Decimal("25.00")
