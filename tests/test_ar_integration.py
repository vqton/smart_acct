from decimal import Decimal
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    CustomerType, CustomerGroup, CustomerStatus,
    ARInvoiceType, ARInvoiceStatus, ARPaymentMethod,
    Customer, InvoiceLine, ARInvoice, ARPayment,
)
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


# ── Customer Tests ────────────────────────────────────────────────

class TestCustomers:
    def test_create_customer(self, uc):
        result = uc.create_customer(
            customer_code="CUST001",
            customer_name="Cong ty TNHH ABC",
            customer_type=CustomerType.ENTERPRISE,
            customer_group=CustomerGroup.DOMESTIC,
            tax_code="1234567890",
            email="abc@example.com",
            phone="0901234567",
            address="123 Nguyen Hue, Q1",
            city="HCM",
            contact_person="Nguyen Van A",
            credit_limit=Decimal("50000000"),
        )
        assert result.is_success()
        c = result.get_data()
        assert c.customer_code == "CUST001"
        assert c.customer_name == "Cong ty TNHH ABC"
        assert c.status == CustomerStatus.ACTIVE
        assert c.credit_limit == Decimal("50000000.00")

    def test_create_customer_duplicate_code(self, uc):
        uc.create_customer(
            customer_code="CUST001", customer_name="ABC",
            tax_code="111", email="a@b.com", phone="090", address="a", city="HCM"
        )
        result = uc.create_customer(
            customer_code="CUST001", customer_name="ABC2",
            tax_code="222", email="b@b.com", phone="091", address="b", city="HN"
        )
        assert result.is_failure()

    def test_get_customer(self, uc):
        created = uc.create_customer(
            customer_code="CUST002", customer_name="XYZ",
            tax_code="333", email="c@d.com", phone="092", address="c", city="DN"
        )
        assert created.is_success()
        customer = uc.get_customer(created.get_data().id)
        assert customer is not None
        assert customer.customer_code == "CUST002"

    def test_get_customer_not_found(self, uc):
        customer = uc.get_customer(999)
        assert customer is None

    def test_list_customers(self, uc):
        uc.create_customer(
            customer_code="CUST003", customer_name="AAA",
            tax_code="444", email="d@e.com", phone="093", address="d", city="HCM"
        )
        uc.create_customer(
            customer_code="CUST004", customer_name="BBB",
            tax_code="555", email="e@f.com", phone="094", address="e", city="HN"
        )
        customers = uc.list_customers(limit=10)
        assert len(customers) >= 2
        assert any(c.customer_code == "CUST003" for c in customers)
        assert any(c.customer_code == "CUST004" for c in customers)

    def test_update_customer(self, uc):
        created = uc.create_customer(
            customer_code="CUST005", customer_name="Old Name",
            tax_code="666", email="f@g.com", phone="095", address="f", city="HCM"
        )
        assert created.is_success()
        updated = uc.update_customer(created.get_data().id, customer_name="New Name", email="new@example.com")
        assert updated is not None
        assert updated.customer_name == "New Name"
        assert updated.email == "new@example.com"

    def test_suspend_customer(self, uc):
        created = uc.create_customer(
            customer_code="CUST006", customer_name="Suspend Me",
            tax_code="777", email="g@h.com", phone="096", address="g", city="HN"
        )
        assert created.is_success()
        result = uc.suspend_customer(created.get_data().id)
        assert result.is_success()
        assert result.get_data().status == CustomerStatus.SUSPENDED

    def test_suspend_customer_not_found(self, uc):
        result = uc.suspend_customer(999)
        assert result.is_failure()


# ── Invoice Tests ─────────────────────────────────────────────────

class TestARInvoices:
    def test_create_invoice(self, uc):
        created = uc.create_customer(
            customer_code="CUST007", customer_name="Invoice Test",
            tax_code="888", email="h@i.com", phone="097", address="h", city="HCM"
        )
        assert created.is_success()
        customer = created.get_data()
        result = uc.create_invoice(
            invoice_number="INV001",
            customer_id=customer.id,
            customer_code=customer.customer_code,
            customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("5000000"),
            lines=[
                InvoiceLine(line_number=1, description="Hang hoa A", quantity=Decimal("10"),
                            unit_price=Decimal("500000"), line_amount=Decimal("5000000"))
            ],
        )
        assert result.is_success()
        inv = result.get_data()
        assert inv.invoice_number == "INV001"
        assert inv.status == ARInvoiceStatus.DRAFT
        assert inv.balance_due == Decimal("5000000.00")

    def test_list_invoices(self, uc):
        # Setup
        created = uc.create_customer(customer_code="CUST008", customer_name="List Test",
            tax_code="999", email="i@j.com", phone="098", address="i", city="HN")
        assert created.is_success()
        customer = created.get_data()
        uc.create_invoice(
            invoice_number="INV002", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("1000000"), lines=[InvoiceLine(line_number=1, description="Test",
                quantity=Decimal("1"), unit_price=Decimal("1000000"), line_amount=Decimal("1000000"))]
        )
        invoices = uc.list_invoices(limit=10)
        assert len(invoices) >= 1
        assert any(i.invoice_number == "INV002" for i in invoices)

    def test_issue_invoice(self, uc):
        created = uc.create_customer(customer_code="CUST009", customer_name="Issue Test",
            tax_code="000", email="j@k.com", phone="099", address="j", city="HCM")
        assert created.is_success()
        customer = created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV003", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("2000000"), lines=[InvoiceLine(line_number=1, description="Issued",
                quantity=Decimal("1"), unit_price=Decimal("2000000"), line_amount=Decimal("2000000"))]
        )
        assert inv.is_success()
        result = uc.issue_invoice(inv.get_data().id)
        assert result.is_success()
        assert result.get_data().status == ARInvoiceStatus.ISSUED

    def test_cancel_invoice(self, uc):
        created = uc.create_customer(customer_code="CUST010", customer_name="Cancel Test",
            tax_code="111", email="k@l.com", phone="012", address="k", city="HN")
        assert created.is_success()
        customer = created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV004", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("3000000"), lines=[InvoiceLine(line_number=1, description="Cancelled",
                quantity=Decimal("1"), unit_price=Decimal("3000000"), line_amount=Decimal("3000000"))]
        )
        assert inv.is_success()
        result = uc.cancel_invoice(inv.get_data().id)
        assert result.is_success()
        assert result.get_data().status == ARInvoiceStatus.CANCELLED

    def test_get_invoice(self, uc):
        created = uc.create_customer(customer_code="CUST011", customer_name="Get Test",
            tax_code="222", email="l@m.com", phone="013", address="l", city="HCM")
        assert created.is_success()
        customer = created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV005", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("4000000"), lines=[InvoiceLine(line_number=1, description="Found",
                quantity=Decimal("1"), unit_price=Decimal("4000000"), line_amount=Decimal("4000000"))]
        )
        assert inv.is_success()
        fetched = uc.get_invoice(inv.get_data().id)
        assert fetched is not None
        assert fetched.invoice_number == "INV005"

    def test_get_invoice_not_found(self, uc):
        assert uc.get_invoice(999) is None


# ── Payment Tests ─────────────────────────────────────────────────

class TestARPayments:
    def test_record_payment(self, uc):
        # Setup: create customer and invoice
        customer_created = uc.create_customer(customer_code="CUST012", customer_name="Payment Test",
            tax_code="333", email="m@n.com", phone="014", address="m", city="HN")
        assert customer_created.is_success()
        customer = customer_created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV006", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("5000000"), lines=[InvoiceLine(line_number=1, description="To Pay",
                quantity=Decimal("1"), unit_price=Decimal("5000000"), line_amount=Decimal("5000000"))]
        )
        assert inv.is_success()
        result = uc.record_payment(
            invoice_id=inv.get_data().id,
            payment_number="PMT001",
            amount=Decimal("5000000"),
            payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.BANK_TRANSFER,
        )
        assert result.is_success()
        p = result.get_data()
        assert p.payment_number == "PMT001"
        assert p.amount == Decimal("5000000.00")

    def test_get_payments_for_invoice(self, uc):
        customer_created = uc.create_customer(customer_code="CUST013", customer_name="Payment List",
            tax_code="444", email="n@o.com", phone="015", address="n", city="HCM")
        customer = customer_created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV007", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("3000000"), lines=[InvoiceLine(line_number=1, description="Payment List",
                quantity=Decimal("1"), unit_price=Decimal("3000000"), line_amount=Decimal("3000000"))]
        )
        assert inv.is_success()
        invoice = inv.get_data()
        uc.record_payment(
            invoice_id=invoice.id, payment_number="PMT002", amount=Decimal("3000000"),
            payment_date=date(2026, 6, 15), payment_method=ARPaymentMethod.CASH,
        )
        payments = uc.get_payments_for_invoice(invoice.id)
        assert len(payments) == 1
        assert payments[0].payment_number == "PMT002"

    def test_overpayment_rejected(self, uc):
        customer_created = uc.create_customer(customer_code="CUST014", customer_name="Overpay",
            tax_code="555", email="o@p.com", phone="016", address="o", city="HN")
        customer = customer_created.get_data()
        inv = uc.create_invoice(
            invoice_number="INV008", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 6, 1), due_date=date(2026, 7, 1),
            amount=Decimal("2000000"), lines=[InvoiceLine(line_number=1, description="Overpay",
                quantity=Decimal("1"), unit_price=Decimal("2000000"), line_amount=Decimal("2000000"))]
        )
        assert inv.is_success()
        result = uc.record_payment(
            invoice_id=inv.get_data().id, payment_number="PMT003",
            amount=Decimal("3000000"), payment_date=date(2026, 6, 15),
            payment_method=ARPaymentMethod.CASH,
        )
        assert result.is_failure()


# ── Aging & Reports ───────────────────────────────────────────────

class TestARAging:
    def test_aging_report_empty(self, uc):
        report = uc.get_aging_report()
        assert isinstance(report, list)

    def test_aging_report_with_data(self, uc):
        # Create customer with overdue invoice
        customer_created = uc.create_customer(customer_code="CUST015", customer_name="Aging",
            tax_code="666", email="p@q.com", phone="017", address="p", city="HCM")
        customer = customer_created.get_data()
        uc.create_invoice(
            invoice_number="INV009", customer_id=customer.id,
            customer_code=customer.customer_code, customer_name=customer.customer_name,
            issue_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
            amount=Decimal("10000000"), lines=[InvoiceLine(line_number=1, description="Overdue",
                quantity=Decimal("1"), unit_price=Decimal("10000000"), line_amount=Decimal("10000000"))]
        )
        report = uc.get_aging_report(as_of_date=date(2026, 6, 1))
        assert isinstance(report, list)
        # Should have at least the overdue entry if engine picks it up

    def test_ar_balance_sheet(self, uc):
        result = uc.get_ar_balance_sheet("2026-05")
        assert "period" in result
        assert result["period"] == "2026-05"


# ── Route Integration (basic smoke) ─────────────────────────────

class TestARRoutes:
    def test_routes_registered(self):
        # Ensure the route module is importable and ar_bp is registered
        from presentation.ar import ar_bp
        assert ar_bp is not None
        assert ar_bp.name == "ar"
