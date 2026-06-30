from decimal import Decimal
from datetime import date, datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    CustomerType, CustomerGroup, CustomerStatus,
    ARInvoiceType, ARInvoiceStatus, ARPaymentMethod,
    Customer, InvoiceLine, ARInvoice, ARPayment,
)
from domain.ar import WriteOffRequestStatus
from infrastructure.models.coa_models import Base
from use_cases.ar import ARUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def uc(session):
    return ARUseCases(session)


def _create_customer(uc, code="CUST001", name="Test Customer", **kw):
    return uc.create_customer(
        customer_code=code, customer_name=name,
        tax_code=kw.get("tax_code", "1234567890"),
        email=kw.get("email", "a@b.com"),
        phone=kw.get("phone", "0900000000"),
        address=kw.get("address", "123 Street"),
        city=kw.get("city", "HCM"),
        credit_limit=kw.get("credit_limit", Decimal("100000000")),
        customer_type=kw.get("customer_type", CustomerType.ENTERPRISE),
        customer_group=kw.get("customer_group", CustomerGroup.DOMESTIC),
    )


def _create_invoice(uc, customer, invoice_number="INV001", amount=Decimal("5000000"), **kw):
    return uc.create_invoice(
        invoice_number=invoice_number,
        customer_id=customer.id,
        customer_code=customer.customer_code,
        customer_name=customer.customer_name,
        issue_date=kw.get("issue_date", date(2026, 6, 1)),
        due_date=kw.get("due_date", date(2026, 7, 1)),
        amount=amount,
        lines=kw.get("lines") or [
            InvoiceLine(line_number=1, description="Hang hoa",
                       quantity=Decimal("1"), unit_price=amount,
                       line_amount=amount)
        ],
        invoice_type=kw.get("invoice_type", ARInvoiceType.SALES),
        tax_amount=kw.get("tax_amount", Decimal("0")),
        discount_amount=kw.get("discount_amount", Decimal("0")),
        period=kw.get("period", "2026-06"),
        coa_code=kw.get("coa_code"),
    )


# ── Customer Tests ────────────────────────────────────────────────

class TestCustomerCRUD:
    def test_create_customer(self, uc):
        result = _create_customer(uc)
        assert result.is_success()
        c = result.get_data()
        assert c.customer_code == "CUST001"
        assert c.customer_name == "Test Customer"
        assert c.status == CustomerStatus.ACTIVE
        assert c.credit_limit == Decimal("100000000.00")

    def test_create_customer_with_vip_group(self, uc):
        result = _create_customer(uc, code="VIP001", name="VIP Customer",
                                   customer_group=CustomerGroup.VIP,
                                   credit_limit=Decimal("500000000"))
        assert result.is_success()
        assert result.get_data().customer_group == CustomerGroup.VIP

    def test_create_customer_government(self, uc):
        result = _create_customer(uc, code="GOVT001", name="Govt Agency",
                                   customer_type=CustomerType.GOVERNMENT,
                                   customer_group=CustomerGroup.GOVT)
        assert result.is_success()
        assert result.get_data().customer_type == CustomerType.GOVERNMENT

    def test_duplicate_customer_code_fails(self, uc):
        _create_customer(uc, code="CUST001")
        result = _create_customer(uc, code="CUST001", name="Duplicate")
        assert result.is_failure()

    def test_get_customer(self, uc):
        created = _create_customer(uc, code="CUST002")
        customer = uc.get_customer(created.get_data().id)
        assert customer is not None
        assert customer.customer_code == "CUST002"

    def test_get_customer_not_found(self, uc):
        assert uc.get_customer(999) is None

    def test_get_customer_by_code(self, uc):
        _create_customer(uc, code="BYCODE")
        customer = uc.get_customer_by_code("BYCODE")
        assert customer is not None
        assert customer.customer_name == "Test Customer"

    def test_get_customer_by_code_not_found(self, uc):
        assert uc.get_customer_by_code("NONEXIST") is None

    def test_list_customers(self, uc):
        _create_customer(uc, code="CUST_A")
        _create_customer(uc, code="CUST_B")
        customers = uc.list_customers(limit=10)
        assert len(customers) >= 2

    def test_list_customers_with_search(self, uc):
        _create_customer(uc, code="FINDME", name="Target Customer")
        _create_customer(uc, code="OTHER", name="Other Company")
        results = uc.list_customers(search="Target")
        assert len(results) >= 1
        assert results[0].customer_code == "FINDME"

    def test_list_customers_with_search_by_code(self, uc):
        _create_customer(uc, code="SEARCH01")
        results = uc.list_customers(search="SEARCH")
        assert len(results) >= 1

    def test_update_customer(self, uc):
        created = _create_customer(uc, code="UPDATE01")
        updated = uc.update_customer(created.get_data().id,
                                      customer_name="Updated Name",
                                      email="new@example.com")
        assert updated is not None
        assert updated.customer_name == "Updated Name"
        assert updated.email == "new@example.com"

    def test_suspend_customer(self, uc):
        created = _create_customer(uc, code="SUSPEND01")
        result = uc.suspend_customer(created.get_data().id)
        assert result.is_success()
        assert result.get_data().status == CustomerStatus.SUSPENDED

    def test_suspend_nonexistent_customer(self, uc):
        result = uc.suspend_customer(999)
        assert result.is_failure()

    def test_delete_customer_no_open_ar(self, uc):
        created = _create_customer(uc, code="DELETE01")
        result = uc.delete_customer(created.get_data().id)
        assert result.is_success()

    def test_delete_customer_with_open_ar_fails(self, uc):
        created = _create_customer(uc, code="HASINV")
        inv = _create_invoice(uc, created.get_data())
        assert inv.is_success()
        result = uc.delete_customer(created.get_data().id)
        assert result.is_failure()

    def test_credit_limit_check_approved(self, uc):
        created = _create_customer(uc, code="CREDLIM01",
                                    credit_limit=Decimal("10000000"))
        check = uc.check_credit_limit(created.get_data().id, Decimal("5000000"))
        assert check["approved"] is True

    def test_credit_limit_check_exceeded(self, uc):
        created = _create_customer(uc, code="CREDLIM02",
                                    credit_limit=Decimal("10000000"))
        check = uc.check_credit_limit(created.get_data().id, Decimal("15000000"))
        assert check["approved"] is False

    def test_credit_limit_near_limit_warns(self, uc):
        created = _create_customer(uc, code="CREDLIM03",
                                    credit_limit=Decimal("10000000"))
        check = uc.check_credit_limit(created.get_data().id, Decimal("8000000"))
        assert check["approved"] is True
        assert check["warning"] is not None
        assert "80" in check["warning"]

    def test_credit_limit_override_active(self, uc):
        created = uc.create_customer(
            customer_code="CREDOVR", customer_name="Override Test",
            credit_limit=Decimal("10000000"),
            credit_limit_override=True,
            credit_limit_override_expires=date(2099, 12, 31),
        )
        assert created.is_success()
        check = uc.check_credit_limit(created.get_data().id, Decimal("15000000"))
        assert check["approved"] is True
        assert "override" in check.get("warning", "").lower()

    def test_credit_limit_override_expired(self, uc):
        created = uc.create_customer(
            customer_code="CREDEXP", customer_name="Expired Override",
            credit_limit=Decimal("10000000"),
            credit_limit_override=True,
            credit_limit_override_expires=date(2020, 12, 31),
        )
        assert created.is_success()
        check = uc.check_credit_limit(created.get_data().id, Decimal("15000000"))
        assert check["approved"] is False

    def test_credit_limit_zero_no_check(self, uc):
        created = _create_customer(uc, code="NOCHECK",
                                    credit_limit=Decimal("0"))
        check = uc.check_credit_limit(created.get_data().id, Decimal("999999999"))
        assert check["approved"] is True


# ── Invoice Tests ─────────────────────────────────────────────────

class TestARInvoiceCRUD:
    def test_create_invoice_draft(self, uc):
        cust = _create_customer(uc, code="INV_CUST")
        result = _create_invoice(uc, cust.get_data())
        assert result.is_success()
        inv = result.get_data()
        assert inv.status == ARInvoiceStatus.DRAFT
        assert inv.balance_due == Decimal("5000000.00")
        assert inv.payment_terms_days == 30

    def test_create_invoice_with_lines(self, uc):
        cust = _create_customer(uc, code="INV_LINES")
        lines = [
            InvoiceLine(line_number=1, description="SP A",
                       quantity=Decimal("2"), unit_price=Decimal("200000"),
                       line_amount=Decimal("400000")),
            InvoiceLine(line_number=2, description="SP B",
                       quantity=Decimal("3"), unit_price=Decimal("100000"),
                       line_amount=Decimal("300000")),
        ]
        result = uc.create_invoice(
            invoice_number="INV_MULTI", customer_id=cust.get_data().id,
            customer_code=cust.get_data().customer_code,
            customer_name=cust.get_data().customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("700000"), lines=lines,
            tax_amount=Decimal("70000"), total_amount=Decimal("770000"),
        )
        assert result.is_success()
        assert len(result.get_data().lines) == 2

    def test_duplicate_invoice_number_fails(self, uc):
        cust = _create_customer(uc, code="DUPINV")
        _create_invoice(uc, cust.get_data(), invoice_number="DUP001")
        result = _create_invoice(uc, cust.get_data(), invoice_number="DUP001")
        assert result.is_failure()

    def test_get_invoice(self, uc):
        cust = _create_customer(uc, code="GETINV")
        created = _create_invoice(uc, cust.get_data(), invoice_number="GET001")
        inv = uc.get_invoice(created.get_data().id)
        assert inv is not None
        assert inv.invoice_number == "GET001"

    def test_get_invoice_by_number(self, uc):
        cust = _create_customer(uc, code="BYNUM")
        _create_invoice(uc, cust.get_data(), invoice_number="NUM001")
        inv = uc.get_invoice_by_number("NUM001")
        assert inv is not None
        assert inv.customer_code == cust.get_data().customer_code

    def test_get_invoice_not_found(self, uc):
        assert uc.get_invoice(999) is None

    def test_list_invoices(self, uc):
        cust = _create_customer(uc, code="LISTINV")
        _create_invoice(uc, cust.get_data(), invoice_number="LST001")
        _create_invoice(uc, cust.get_data(), invoice_number="LST002")
        invoices = uc.list_invoices(limit=10)
        assert len(invoices) >= 2

    def test_list_invoices_filter_by_customer(self, uc):
        c1 = _create_customer(uc, code="CUST_A")
        c2 = _create_customer(uc, code="CUST_B")
        _create_invoice(uc, c1.get_data(), invoice_number="F001")
        _create_invoice(uc, c2.get_data(), invoice_number="F002")
        invoices = uc.list_invoices(customer_id=c1.get_data().id)
        assert len(invoices) == 1
        assert invoices[0].invoice_number == "F001"

    def test_list_invoices_filter_by_period(self, uc):
        cust = _create_customer(uc, code="PERIOD")
        _create_invoice(uc, cust.get_data(), invoice_number="P001", period="2026-06")
        _create_invoice(uc, cust.get_data(), invoice_number="P002", period="2026-07")
        invoices = uc.list_invoices(period="2026-06")
        assert len(invoices) >= 1
        assert all(i.period == "2026-06" for i in invoices)

    def test_issue_invoice(self, uc):
        cust = _create_customer(uc, code="ISSUE")
        created = _create_invoice(uc, cust.get_data(), invoice_number="ISS001")
        result = uc.issue_invoice(created.get_data().id)
        assert result.is_success()
        assert result.get_data().status == ARInvoiceStatus.ISSUED

    def test_issue_already_issued_fails(self, uc):
        cust = _create_customer(uc, code="ISSAGAIN")
        created = _create_invoice(uc, cust.get_data(), invoice_number="ISS002")
        uc.issue_invoice(created.get_data().id)
        result = uc.issue_invoice(created.get_data().id)
        assert result.is_failure()

    def test_cancel_invoice(self, uc):
        cust = _create_customer(uc, code="CANCEL")
        created = _create_invoice(uc, cust.get_data(), invoice_number="CAN001")
        result = uc.cancel_invoice(created.get_data().id)
        assert result.is_success()
        assert result.get_data().status == ARInvoiceStatus.CANCELLED

    def test_cancel_paid_invoice_fails(self, uc):
        cust = _create_customer(uc, code="CANPAID")
        created = _create_invoice(uc, cust.get_data(), invoice_number="CAN002",
                                   amount=Decimal("1000000"))
        inv_id = created.get_data().id
        uc.issue_invoice(inv_id)
        uc.record_payment(invoice_id=inv_id, payment_number="P001",
                          amount=Decimal("1000000"), payment_date=date(2026, 6, 15),
                          payment_method=ARPaymentMethod.BANK_TRANSFER)
        result = uc.cancel_invoice(inv_id)
        assert result.is_failure()

    def test_debit_note_create(self, uc):
        cust = _create_customer(uc, code="DEBIT")
        result = uc.create_invoice(
            invoice_number="DN001", customer_id=cust.get_data().id,
            customer_code=cust.get_data().customer_code,
            customer_name=cust.get_data().customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("200000"), invoice_type=ARInvoiceType.DEBIT_NOTE,
            lines=[InvoiceLine(line_number=1, description="Debit note adjustment",
                              quantity=Decimal("1"), unit_price=Decimal("200000"),
                              line_amount=Decimal("200000"))],
        )
        assert result.is_success()
        assert result.get_data().invoice_type == ARInvoiceType.DEBIT_NOTE

    def test_credit_note_create(self, uc):
        cust = _create_customer(uc, code="CREDIT")
        result = uc.create_invoice(
            invoice_number="CN001", customer_id=cust.get_data().id,
            customer_code=cust.get_data().customer_code,
            customer_name=cust.get_data().customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("-500000"), invoice_type=ARInvoiceType.CREDIT_NOTE,
            lines=[InvoiceLine(line_number=1, description="Credit note",
                              quantity=Decimal("-1"), unit_price=Decimal("500000"),
                              line_amount=Decimal("-500000"))],
            total_amount=Decimal("-500000"),
        )
        assert result.is_success()
        assert result.get_data().invoice_type == ARInvoiceType.CREDIT_NOTE
        assert result.get_data().balance_due == Decimal("-500000.00")


# ── Payment Tests ─────────────────────────────────────────────────

class TestARPayment:
    def test_record_full_payment(self, uc):
        cust = _create_customer(uc, code="PAYFULL")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY001",
                               amount=Decimal("5000000"))
        uc.issue_invoice(inv.get_data().id)
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT001",
            amount=Decimal("5000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.BANK_TRANSFER,
        )
        assert result.is_success()
        assert result.get_data().amount == Decimal("5000000.00")

    def test_partial_payment(self, uc):
        cust = _create_customer(uc, code="PARTIAL")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY002",
                               amount=Decimal("10000000"))
        uc.issue_invoice(inv.get_data().id)
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT002",
            amount=Decimal("3000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.CASH,
        )
        assert result.is_success()
        invoice = uc.get_invoice(inv.get_data().id)
        assert invoice.status == ARInvoiceStatus.PARTIALLY_PAID
        assert invoice.paid_amount == Decimal("3000000.00")
        assert invoice.balance_due == Decimal("7000000.00")

    def test_multiple_partial_payments(self, uc):
        cust = _create_customer(uc, code="MULTIPMT")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY003",
                               amount=Decimal("10000000"))
        uc.issue_invoice(inv.get_data().id)
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_A",
                          amount=Decimal("2000000"), payment_date=date(2026, 6, 10),
                          payment_method=ARPaymentMethod.CASH)
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_B",
                          amount=Decimal("3000000"), payment_date=date(2026, 6, 20),
                          payment_method=ARPaymentMethod.BANK_TRANSFER)
        invoice = uc.get_invoice(inv_id)
        assert invoice.paid_amount == Decimal("5000000.00")
        assert invoice.balance_due == Decimal("5000000.00")
        assert invoice.status == ARInvoiceStatus.PARTIALLY_PAID

    def test_full_payment_marks_paid(self, uc):
        cust = _create_customer(uc, code="FULLPAID")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY004",
                               amount=Decimal("5000000"))
        uc.issue_invoice(inv.get_data().id)
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_F1",
                          amount=Decimal("2000000"), payment_date=date(2026, 6, 10),
                          payment_method=ARPaymentMethod.CASH)
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_F2",
                          amount=Decimal("3000000"), payment_date=date(2026, 6, 20),
                          payment_method=ARPaymentMethod.BANK_TRANSFER)
        invoice = uc.get_invoice(inv_id)
        assert invoice.status == ARInvoiceStatus.PAID
        assert invoice.balance_due == Decimal("0.00")

    def test_overpayment_rejected(self, uc):
        cust = _create_customer(uc, code="OVERPAY")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY005",
                               amount=Decimal("2000000"))
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT_OVR",
            amount=Decimal("3000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.CASH,
        )
        assert result.is_failure()

    def test_zero_payment_rejected(self, uc):
        cust = _create_customer(uc, code="ZEROPMT")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY006")
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT_ZERO",
            amount=Decimal("0"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.CASH,
        )
        assert result.is_failure()

    def test_get_payments_for_invoice(self, uc):
        cust = _create_customer(uc, code="GETPMT")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY007",
                               amount=Decimal("5000000"))
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_G1",
                          amount=Decimal("2000000"), payment_date=date(2026, 6, 15),
                          payment_method=ARPaymentMethod.CASH)
        payments = uc.get_payments_for_invoice(inv_id)
        assert len(payments) >= 1

    def test_list_payments_by_customer(self, uc):
        cust = _create_customer(uc, code="LSTPMT")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY008",
                               amount=Decimal("5000000"))
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_L1",
                          amount=Decimal("5000000"), payment_date=date(2026, 6, 15),
                          payment_method=ARPaymentMethod.BANK_TRANSFER)
        payments = uc.list_payments(customer_code="LSTPMT")
        assert len(payments) >= 1

    def test_list_payments_date_range(self, uc):
        cust = _create_customer(uc, code="DATERNG")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY009",
                               amount=Decimal("3000000"))
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_D1",
                          amount=Decimal("3000000"), payment_date=date(2026, 6, 15),
                          payment_method=ARPaymentMethod.CASH)
        payments = uc.list_payments(date_from=date(2026, 6, 1),
                                    date_to=date(2026, 6, 30))
        assert len(payments) >= 1
        payments_out = uc.list_payments(date_from=date(2025, 1, 1),
                                        date_to=date(2025, 1, 31))
        assert len(payments_out) == 0

    def test_payment_with_cheque_method(self, uc):
        cust = _create_customer(uc, code="CHEQUE")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PAY010",
                               amount=Decimal("1000000"))
        uc.issue_invoice(inv.get_data().id)
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT_CHQ",
            amount=Decimal("1000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.CHEQUE,
        )
        assert result.is_success()


# ── Aging & Reports ───────────────────────────────────────────────

class TestARAging:
    def test_aging_report_empty(self, uc):
        report = uc.get_aging_report()
        assert isinstance(report, list)
        assert len(report) == 0

    def test_aging_report_with_overdue(self, uc):
        cust = _create_customer(uc, code="AGING01")
        _create_invoice(uc, cust.get_data(), invoice_number="AGE001",
                         amount=Decimal("10000000"),
                         due_date=date(2026, 1, 1))
        report = uc.get_aging_report(as_of_date=date(2026, 6, 1))
        assert len(report) >= 1
        entry = report[0]
        assert entry["customer_code"] == "AGING01"
        assert entry["total_outstanding"] > 0
        assert entry["days_past_due_oldest"] >= 150

    def test_aging_report_current_only(self, uc):
        cust = _create_customer(uc, code="AGING02")
        _create_invoice(uc, cust.get_data(), invoice_number="AGE002",
                         amount=Decimal("5000000"),
                         due_date=date(2026, 7, 1))
        report = uc.get_aging_report(as_of_date=date(2026, 6, 15))
        assert len(report) >= 1
        entry = report[0]
        assert entry["total_outstanding"] == Decimal("5000000.00")

    def test_aging_report_multiple_customers(self, uc):
        c1 = _create_customer(uc, code="MULTI_A")
        c2 = _create_customer(uc, code="MULTI_B")
        _create_invoice(uc, c1.get_data(), invoice_number="MAGE01",
                         amount=Decimal("3000000"),
                         due_date=date(2026, 1, 1))
        _create_invoice(uc, c2.get_data(), invoice_number="MAGE02",
                         amount=Decimal("7000000"),
                         due_date=date(2026, 5, 1))
        report = uc.get_aging_report(as_of_date=date(2026, 6, 1))
        assert len(report) == 2

    def test_aging_snapshot_create_and_retrieve(self, uc):
        cust = _create_customer(uc, code="SNAP01")
        _create_invoice(uc, cust.get_data(), invoice_number="SNP001",
                         amount=Decimal("10000000"),
                         due_date=date(2026, 1, 1))
        result = uc.create_aging_snapshot("2026-06")
        assert result.is_success()
        data = result.get_data()
        assert data["period"] == "2026-06"
        assert data["snapshots"] >= 1
        snapshots = uc.get_aging_snapshots("2026-06")
        assert len(snapshots) >= 1
        assert snapshots[0].locked is True

    def test_ar_balance_sheet(self, uc):
        cust = _create_customer(uc, code="BALSHT")
        _create_invoice(uc, cust.get_data(), invoice_number="BAL001",
                         amount=Decimal("5000000"), period="2026-06")
        result = uc.get_ar_balance_sheet("2026-06")
        assert result["period"] == "2026-06"
        assert result["receivables"] >= Decimal("5000000")


# ── Dunning Tests ─────────────────────────────────────────────────

class TestARDunning:
    def test_advance_dunning_empty(self, uc):
        result = uc.advance_dunning(as_of_date=date(2026, 6, 1))
        assert result.is_success()
        assert result.get_data()["count"] == 0

    def test_advance_dunning_level_1(self, uc):
        cust = _create_customer(uc, code="DUN01")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="DUN001",
                               amount=Decimal("10000000"),
                               due_date=date(2026, 6, 5))
        uc.issue_invoice(inv.get_data().id)
        result = uc.advance_dunning(as_of_date=date(2026, 6, 10))
        assert result.is_success()
        assert result.get_data()["count"] >= 1
        lvl = result.get_data()["processed"][0]["dunning_level"]
        assert lvl == 1, f"Expected dunning level 1 (5 days overdue), got {lvl}"

    def test_advance_dunning_escalates_to_level_2(self, uc):
        cust = _create_customer(uc, code="DUN02")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="DUN002",
                               amount=Decimal("5000000"),
                               due_date=date(2026, 5, 1))
        uc.issue_invoice(inv.get_data().id)
        # First run gets to level 1
        uc.advance_dunning(as_of_date=date(2026, 5, 10))
        # Second run should escalate
        result = uc.advance_dunning(as_of_date=date(2026, 6, 1))
        assert result.is_success()
        if result.get_data()["count"] > 0:
            assert result.get_data()["processed"][0]["dunning_level"] >= 2

    def test_manual_dunning(self, uc):
        cust = _create_customer(uc, code="MANDUN")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="DUN003",
                               amount=Decimal("3000000"),
                               due_date=date(2026, 5, 1))
        uc.issue_invoice(inv.get_data().id)
        result = uc.manual_dunning(inv.get_data().id, dunning_method="phone",
                                    notes="Called customer", performed_by="NV001")
        assert result.is_success()
        assert result.get_data()["dunning_level"] == 1

    def test_dunning_max_level_reached(self, uc):
        cust = _create_customer(uc, code="MAXDUN")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="DUN004",
                               amount=Decimal("10000000"),
                               due_date=date(2026, 1, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        for _ in range(5):
            try:
                uc.manual_dunning(inv_id, dunning_method="email")
            except Exception:
                break
        result = uc.manual_dunning(inv_id)
        assert result.is_failure()

    def test_get_dunning_logs(self, uc):
        cust = _create_customer(uc, code="DUNLOG")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="DUN005",
                               amount=Decimal("5000000"),
                               due_date=date(2026, 5, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        uc.advance_dunning(as_of_date=date(2026, 6, 1))
        logs = uc.get_dunning_logs(inv_id)
        assert len(logs) >= 1


# ── Bad Debt Tests ────────────────────────────────────────────────

class TestBadDebt:
    def test_create_provision_no_overdue(self, uc):
        result = uc.create_bad_debt_provision("2026-06")
        assert result.is_success()
        assert result.get_data()["provisions"] == 0

    def test_create_provision_with_overdue(self, uc):
        cust = _create_customer(uc, code="PROV01")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="PROV001",
                               amount=Decimal("10000000"),
                               due_date=date(2025, 1, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        for _ in range(5):
            try:
                uc.manual_dunning(inv_id, dunning_method="email")
            except Exception:
                break
        result = uc.create_bad_debt_provision("2026-06")
        assert result.is_success()

    def test_get_provisions(self, uc):
        provisions = uc.get_provisions("2026-06")
        assert isinstance(provisions, list)

    def test_write_off_request_flow(self, uc):
        cust = _create_customer(uc, code="WROFF01")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="WROFF001",
                               amount=Decimal("5000000"),
                               due_date=date(2025, 1, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        req = uc.create_write_off_request(
            invoice_id=inv_id, reason="Customer bankrupt",
            created_by="NV001", supporting_docs="docs/bankruptcy.pdf",
        )
        assert req.is_success()

    def test_list_write_off_requests(self, uc):
        cust = _create_customer(uc, code="WROFF02")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="WROFF002",
                               amount=Decimal("3000000"),
                               due_date=date(2025, 1, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        uc.create_write_off_request(invoice_id=inv_id, reason="Cannot pay")
        reqs = uc.get_write_off_requests()
        assert len(reqs) >= 1

    def test_approve_write_off_marks_invoice(self, uc):
        cust = _create_customer(uc, code="WROFF03")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="WROFF003",
                               amount=Decimal("4000000"),
                               due_date=date(2025, 1, 1))
        inv_id = inv.get_data().id
        uc.issue_invoice(inv_id)
        req = uc.create_write_off_request(invoice_id=inv_id, reason="No recovery")
        assert req.is_success()
        result = uc.approve_write_off(req.get_data().id, approval_by="Manager",
                                       approval_notes="Approved per policy")
        assert result.is_success()
        invoice = uc.get_invoice(inv_id)
        assert invoice.status == ARInvoiceStatus.WRITTEN_OFF
        assert invoice.balance_due == Decimal("0")

    def test_reject_write_off(self, uc):
        cust = _create_customer(uc, code="WROFF04")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="WROFF004",
                               amount=Decimal("2000000"))
        inv_id = inv.get_data().id
        req = uc.create_write_off_request(invoice_id=inv_id,
                                           reason="Customer disputed")
        assert req.is_success()
        result = uc.reject_write_off(req.get_data().id, approval_by="Manager",
                                      reason="Need more evidence")
        assert result.is_success()
        invoice = uc.get_invoice(inv_id)
        assert invoice.status != ARInvoiceStatus.WRITTEN_OFF

    def test_write_off_paid_invoice_fails(self, uc):
        cust = _create_customer(uc, code="WROFF05")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="WROFF005",
                               amount=Decimal("1000000"))
        inv_id = inv.get_data().id
        uc.record_payment(invoice_id=inv_id, payment_number="PMT_WO",
                          amount=Decimal("1000000"), payment_date=date(2026, 6, 15),
                          payment_method=ARPaymentMethod.CASH)
        result = uc.create_write_off_request(invoice_id=inv_id, reason="Already paid")
        assert result.is_failure()

    def test_approve_nonexistent_write_off(self, uc):
        result = uc.approve_write_off(999, approval_by="Manager")
        assert result.is_failure()

    def test_reject_nonexistent_write_off(self, uc):
        result = uc.reject_write_off(999, approval_by="Manager")
        assert result.is_failure()


# ── CEI & ECL Tests ───────────────────────────────────────────────

class TestCEIAndECL:
    def test_cei_report_single_period(self, uc):
        cust = _create_customer(uc, code="CEI01")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="CEI001",
                               amount=Decimal("10000000"), period="2026-06")
        # No collection → ending AR = beginning AR + sales → CEI = 0
        uc.issue_invoice(inv.get_data().id)
        reports = uc.get_cei_report(["2026-06"])
        assert len(reports) == 1
        assert reports[0]["period"] == "2026-06"
        assert reports[0]["cei"] == Decimal("0.00")

    def test_cei_report_multiple_periods(self, uc):
        cust = _create_customer(uc, code="CEI02")
        _create_invoice(uc, cust.get_data(), invoice_number="CEI002",
                         amount=Decimal("10000000"), period="2026-05")
        _create_invoice(uc, cust.get_data(), invoice_number="CEI003",
                         amount=Decimal("20000000"), period="2026-06")
        reports = uc.get_cei_report(["2026-05", "2026-06"])
        assert len(reports) == 2

    def test_ecl_stage_1(self, uc):
        cust = _create_customer(uc, code="ECL01")
        inv = _create_invoice(uc, cust.get_data(), invoice_number="ECL001",
                               amount=Decimal("10000000"),
                               due_date=date(2026, 7, 1))
        uc.issue_invoice(inv.get_data().id)
        result = uc.calculate_ecl(cust.get_data().id,
                                   reporting_date=date(2026, 6, 15))
        assert result["stage"] == "stage_1"
        assert result["ecl"] >= Decimal("0")

    def test_ecl_stage_2(self, uc):
        cust = _create_customer(uc, code="ECL02")
        # Overdue 120 days → bucket_91_180 → stage_2
        inv = _create_invoice(uc, cust.get_data(), invoice_number="ECL002",
                               amount=Decimal("50000000"),
                               due_date=date(2026, 2, 15))
        uc.issue_invoice(inv.get_data().id)
        result = uc.calculate_ecl(cust.get_data().id,
                                   reporting_date=date(2026, 6, 15))
        assert result["stage"] == "stage_2", f"Expected stage_2, got {result['stage']}"
        assert result["ecl"] > Decimal("0")

    def test_ecl_no_data(self, uc):
        result = uc.calculate_ecl(999)
        assert result["stage"] == "stage_1"
        assert result["ecl"] == Decimal("0")


# ── FIFO Allocation Tests ─────────────────────────────────────────

class TestFIFOAllocation:
    def test_fifo_allocation_oldest_first(self, uc):
        cust = _create_customer(uc, code="FIFO01")
        c = cust.get_data()
        inv1 = _create_invoice(uc, c, invoice_number="FIFO001",
                                amount=Decimal("3000000"),
                                due_date=date(2026, 1, 1))
        inv2 = _create_invoice(uc, c, invoice_number="FIFO002",
                                amount=Decimal("5000000"),
                                due_date=date(2026, 3, 1))
        inv1_id = inv1.get_data().id
        inv2_id = inv2.get_data().id
        uc.issue_invoice(inv1_id)
        uc.issue_invoice(inv2_id)
        # Pay 4M — FIFO should allocate 3M to inv1 (oldest, full) and 1M to inv2
        result = uc.record_payment(
            invoice_id=inv1_id, payment_number="FIFO_PMT",
            amount=Decimal("4000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.BANK_TRANSFER,
            auto_allocate=True,
        )
        assert result.is_success(), f"Payment failed: {result.error}"
        i1 = uc.get_invoice(inv1_id)
        i2 = uc.get_invoice(inv2_id)
        # inv1 (oldest, due 2026-01-01) should be fully paid first
        assert i1.status == ARInvoiceStatus.PAID, f"inv1 should be PAID, got {i1.status}"
        assert i1.balance_due == Decimal("0"), f"inv1 balance_due should be 0, got {i1.balance_due}"
        # inv2 should have 1M allocated
        assert i2.paid_amount == Decimal("1000000.00"), f"inv2 paid_amount should be 1M, got {i2.paid_amount}"
        assert i2.balance_due == Decimal("4000000.00"), f"inv2 balance_due should be 4M, got {i2.balance_due}"


# ── Route Registration ────────────────────────────────────────────

class TestARRoutes:
    def test_routes_registered(self):
        from presentation.ar import ar_bp
        assert ar_bp is not None
        assert ar_bp.name == "ar"
