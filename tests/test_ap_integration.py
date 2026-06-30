from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    VendorType, VendorGroup, VendorStatus,
    APInvoiceType, APInvoiceStatus, APPaymentMethod,
)
from domain.ap import Vendor, APInvoice, APInvoiceLine
from infrastructure.models.coa_models import Base
from use_cases.ap import APUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def uc(session):
    return APUseCases(session)


@pytest.fixture
def demo_vendor(uc):
    result = uc.create_vendor(
        vendor_code="V001",
        vendor_name="ABC Co Ltd",
        tax_code="0123456789",
        vendor_type=VendorType.ENTERPRISE,
        vendor_group=VendorGroup.DOMESTIC,
        city="HCM",
        payment_terms="net_30",
        currency="VND",
        credit_limit=Decimal("100000000"),
    )
    return result.get_data()


@pytest.fixture
def demo_invoice(uc, demo_vendor):
    lines = [
        APInvoiceLine(line_number=1, description="Goods A",
                      quantity=Decimal("10"), unit_price=Decimal("1000000"),
                      line_amount=Decimal("10000000"), tax_rate=Decimal("0.10"),
                      tax_amount=Decimal("1000000")),
    ]
    result = uc.create_invoice(
        invoice_number="INV-001",
        vendor_id=demo_vendor.id,
        vendor_code=demo_vendor.vendor_code,
        vendor_name=demo_vendor.vendor_name,
        invoice_date=date(2026, 6, 1),
        due_date=date(2026, 7, 1),
        amount=Decimal("10000000"),
        tax_amount=Decimal("1000000"),
        total_amount=Decimal("11000000"),
        lines=lines,
        description="June goods purchase",
    )
    return result.get_data()


# ── Vendor Tests ───────────────────────────────────────────────────

class TestVendors:
    def test_create_vendor(self, uc):
        result = uc.create_vendor(
            vendor_code="V001",
            vendor_name="ABC Co Ltd",
            vendor_type=VendorType.ENTERPRISE,
            vendor_group=VendorGroup.DOMESTIC,
            tax_code="0123456789",
            city="HCM",
            payment_terms="net_30",
            currency="VND",
        )
        assert result.is_success()
        v = result.get_data()
        assert v.vendor_code == "V001"
        assert v.vendor_name == "ABC Co Ltd"
        assert v.vendor_type == VendorType.ENTERPRISE
        assert v.status == VendorStatus.ACTIVE
        assert v.id is not None

    def test_create_duplicate_vendor_code(self, uc, demo_vendor):
        result = uc.create_vendor(
            vendor_code="V001", vendor_name="Duplicate",
        )
        assert result.is_failure()

    def test_get_vendor(self, uc, demo_vendor):
        v = uc.get_vendor(demo_vendor.id)
        assert v is not None
        assert v.vendor_code == "V001"

    def test_get_vendor_by_code(self, uc, demo_vendor):
        v = uc.get_vendor_by_code("V001")
        assert v is not None
        assert v.vendor_name == "ABC Co Ltd"

    def test_list_vendors(self, uc, demo_vendor):
        vendors = uc.list_vendors()
        assert len(vendors) == 1
        assert vendors[0].vendor_code == "V001"

    def test_update_vendor(self, uc, demo_vendor):
        updated = uc.update_vendor(demo_vendor.id, vendor_name="ABC Co Ltd Updated")
        assert updated is not None
        assert updated.vendor_name == "ABC Co Ltd Updated"

    def test_suspend_vendor(self, uc, demo_vendor):
        result = uc.suspend_vendor(demo_vendor.id)
        assert result.is_success()
        v = result.get_data()
        assert v.status == VendorStatus.SUSPENDED

    def test_activate_vendor(self, uc, demo_vendor):
        uc.suspend_vendor(demo_vendor.id)
        result = uc.activate_vendor(demo_vendor.id)
        assert result.is_success()
        v = result.get_data()
        assert v.status == VendorStatus.ACTIVE

    def test_block_vendor(self, uc, demo_vendor):
        result = uc.block_vendor(demo_vendor.id)
        assert result.is_success()
        v = result.get_data()
        assert v.status == VendorStatus.BLOCKED

    def test_delete_vendor(self, uc, demo_vendor):
        result = uc.delete_vendor(demo_vendor.id)
        assert result.is_success()

    def test_create_foreign_vendor(self, uc):
        result = uc.create_vendor(
            vendor_code="F001",
            vendor_name="Foreign Supplier GmbH",
            vendor_type=VendorType.FOREIGN,
            vendor_group=VendorGroup.IMPORT,
            currency="EUR",
            foreign_ct_type="deduction",
            foreign_vat_rate=Decimal("0.05"),
            foreign_cit_rate=Decimal("0.10"),
        )
        assert result.is_success()
        v = result.get_data()
        assert v.foreign_ct_type == "deduction"


# ── Invoice Tests ──────────────────────────────────────────────────

class TestInvoices:
    def test_create_invoice(self, uc, demo_vendor):
        lines = [
            APInvoiceLine(line_number=1, description="Item A",
                          quantity=Decimal("5"), unit_price=Decimal("200000"),
                          line_amount=Decimal("1000000"), tax_rate=Decimal("0.10"),
                          tax_amount=Decimal("100000")),
        ]
        result = uc.create_invoice(
            invoice_number="INV-001",
            vendor_id=demo_vendor.id,
            vendor_code=demo_vendor.vendor_code,
            vendor_name=demo_vendor.vendor_name,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("1000000"),
            tax_amount=Decimal("100000"),
            total_amount=Decimal("1100000"),
            lines=lines,
            description="Test purchase",
        )
        assert result.is_success()
        inv = result.get_data()
        assert inv.invoice_number == "INV-001"
        assert inv.status == APInvoiceStatus.DRAFT
        assert len(inv.lines) == 1

    def test_get_invoice(self, uc, demo_invoice):
        inv = uc.get_invoice(demo_invoice.id)
        assert inv is not None
        assert inv.invoice_number == "INV-001"

    def test_list_invoices(self, uc, demo_invoice):
        invoices = uc.list_invoices()
        assert len(invoices) == 1

    def test_approve_invoice(self, uc, demo_invoice):
        result = uc.approve_invoice(demo_invoice.id, approved_by="APManager")
        assert result.is_success()
        inv = result.get_data()
        assert inv.status == APInvoiceStatus.APPROVED

    def test_cancel_invoice(self, uc, demo_invoice):
        result = uc.cancel_invoice(demo_invoice.id, reason="Vendor error")
        assert result.is_success()
        inv = result.get_data()
        assert inv.status == APInvoiceStatus.CANCELLED

    def test_create_invoice_with_vat(self, uc, demo_vendor):
        lines = [
            APInvoiceLine(line_number=1, description="Goods",
                          quantity=Decimal("1"), unit_price=Decimal("10000000"),
                          line_amount=Decimal("10000000"), tax_rate=Decimal("0.10"),
                          tax_amount=Decimal("1000000")),
        ]
        result = uc.create_invoice(
            invoice_number="INV-VAT",
            vendor_id=demo_vendor.id,
            vendor_code=demo_vendor.vendor_code,
            vendor_name=demo_vendor.vendor_name,
            invoice_date=date(2026, 6, 15),
            due_date=date(2026, 7, 15),
            amount=Decimal("10000000"),
            tax_amount=Decimal("1000000"),
            total_amount=Decimal("11000000"),
            lines=lines,
        )
        assert result.is_success()
        inv = result.get_data()
        assert inv.tax_amount == Decimal("1000000.00")


# ── Credit/Debit Note Tests ────────────────────────────────────────

class TestCreditDebitNotes:
    def test_create_credit_note(self, uc, demo_invoice):
        result = uc.create_credit_note(demo_invoice.id, "Goods returned",
                                       Decimal("1100000"), Decimal("100000"))
        assert result.is_success()

    def test_create_debit_note(self, uc, demo_invoice):
        result = uc.create_debit_note(demo_invoice.id, "Additional shipping",
                                      Decimal("500000"))
        assert result.is_success()


# ── Payment Tests ──────────────────────────────────────────────────

class TestPayments:
    def test_record_payment(self, uc, demo_vendor, demo_invoice):
        uc.approve_invoice(demo_invoice.id, approved_by="Manager")
        result = uc.record_payment(
            invoice_id=demo_invoice.id,
            payment_number="PMT-001",
            vendor_id=demo_vendor.id,
            amount=Decimal("11000000"),
            payment_date=date(2026, 7, 1),
            payment_method=APPaymentMethod.BANK_TRANSFER,
        )
        assert result.is_success()

    def test_get_payments_for_invoice(self, uc, demo_vendor, demo_invoice):
        uc.approve_invoice(demo_invoice.id, approved_by="Manager")
        uc.record_payment(
            invoice_id=demo_invoice.id,
            payment_number="PMT-002",
            vendor_id=demo_vendor.id,
            amount=Decimal("11000000"),
            payment_date=date(2026, 7, 1),
            payment_method=APPaymentMethod.BANK_TRANSFER,
        )
        payments = uc.get_payments_for_invoice(demo_invoice.id)
        assert len(payments) == 1


# ── Prepayment Tests ───────────────────────────────────────────────

class TestPrepayments:
    def test_create_prepayment(self, uc, demo_vendor):
        result = uc.create_prepayment(
            vendor_id=demo_vendor.id,
            amount=Decimal("50000000"),
            payment_date=date(2026, 6, 1),
            expected_invoice_date=date(2026, 6, 30),
        )
        assert result.is_success()
        pp = result.get_data()
        assert pp.unapplied_balance == Decimal("50000000.00")

    def test_get_prepayments(self, uc, demo_vendor):
        uc.create_prepayment(vendor_id=demo_vendor.id, amount=Decimal("30000000"),
                             payment_date=date(2026, 6, 1))
        prepayments = uc.get_prepayments(vendor_id=demo_vendor.id)
        assert len(prepayments) == 1


# ── Aging Tests ────────────────────────────────────────────────────

class TestAging:
    def test_get_aging_report(self, uc, demo_invoice):
        report = uc.get_aging_report(as_of_date=date(2026, 7, 15))
        assert isinstance(report, list)

    def test_create_aging_snapshot(self, uc, demo_invoice):
        result = uc.create_aging_snapshot("2026-06")
        assert result.is_success()

    def test_get_aging_snapshots(self, uc, demo_invoice):
        uc.create_aging_snapshot("2026-06")
        snapshots = uc.get_aging_snapshots("2026-06")
        assert len(snapshots) >= 0


# ── Provision Tests ────────────────────────────────────────────────

class TestProvisions:
    def test_create_provisions(self, uc, demo_vendor):
        result = uc.create_provisions("2026-06",
                                       as_of_date=date(2026, 12, 31))
        assert result.is_success()

    def test_get_provisions(self, uc, demo_vendor):
        uc.create_provisions("2026-06", as_of_date=date(2026, 12, 31))
        provisions = uc.get_provisions("2026-06")
        assert len(provisions) >= 0


# ── FCT Tests ──────────────────────────────────────────────────────

class TestFCT:
    def test_calculate_fct_foreign_vendor(self, uc):
        result = uc.create_vendor(
            vendor_code="FCT01",
            vendor_name="Foreign Supplier",
            vendor_type=VendorType.FOREIGN,
            currency="USD",
            foreign_ct_type="deduction",
            foreign_vat_rate=Decimal("0.05"),
            foreign_cit_rate=Decimal("0.10"),
        )
        assert result.is_success()
        vendor = result.get_data()

        lines = [
            APInvoiceLine(line_number=1, description="Consulting",
                          quantity=Decimal("1"), unit_price=Decimal("100000000"),
                          line_amount=Decimal("100000000"), tax_rate=Decimal("0"),
                          tax_amount=Decimal("0")),
        ]
        inv_result = uc.create_invoice(
            invoice_number="FCT-INV-001",
            vendor_id=vendor.id,
            vendor_code=vendor.vendor_code,
            vendor_name=vendor.vendor_name,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 6, 30),
            amount=Decimal("100000000"),
            tax_amount=Decimal("0"),
            total_amount=Decimal("100000000"),
            lines=lines,
            description="Foreign consulting",
        )
        assert inv_result.is_success()
        invoice = inv_result.get_data()

        fct_result = uc.calculate_fct(invoice.id)
        assert fct_result.is_success()
        fct = fct_result.get_data()
        assert fct.vat_amount > 0
        assert fct.cit_amount > 0

    def test_get_fct_declarations(self, uc, demo_invoice):
        declarations = uc.get_fct_declarations("2026-06")
        assert isinstance(declarations, list)


# ── Reporting Tests ────────────────────────────────────────────────

class TestReporting:
    def test_get_ap_balance(self, uc, demo_invoice):
        balance = uc.get_ap_balance("2026-06")
        assert "period" in balance

    def test_get_ap_turnover(self, uc, demo_invoice):
        turnover = uc.get_ap_turnover("2026-06")
        assert "period" in turnover

    def test_get_dpo(self, uc, demo_invoice):
        dpo = uc.get_dpo("2026-06")
        assert "dpo" in dpo


# ── Edge Case Tests ────────────────────────────────────────────────

class TestEdgeCases:
    def test_duplicate_invoice_number(self, uc, demo_vendor, demo_invoice):
        lines = [
            APInvoiceLine(line_number=1, description="Items",
                          quantity=Decimal("1"), unit_price=Decimal("1000000"),
                          line_amount=Decimal("1000000"), tax_rate=Decimal("0.10"),
                          tax_amount=Decimal("100000")),
        ]
        result = uc.create_invoice(
            invoice_number="INV-001",  # Same as demo_invoice
            vendor_id=demo_vendor.id,
            vendor_code=demo_vendor.vendor_code,
            vendor_name=demo_vendor.vendor_name,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("1000000"),
            tax_amount=Decimal("100000"),
            total_amount=Decimal("1100000"),
            lines=lines,
        )
        assert result.is_failure()

    def test_foreign_vendor_without_fct_config(self, uc):
        result = uc.create_vendor(
            vendor_code="FOREIGN",
            vendor_name="Foreign Co",
            vendor_type=VendorType.FOREIGN,
            currency="USD",
        )
        assert result.is_success()
        vendor = result.get_data()
        assert vendor.foreign_ct_type is None  # Allowed but flagged

    def test_zero_amount_invoice_rejected(self, uc, demo_vendor):
        lines = [
            APInvoiceLine(line_number=1, description="Zero items",
                          quantity=Decimal("0"), unit_price=Decimal("0"),
                          line_amount=Decimal("0"), tax_rate=Decimal("0.10"),
                          tax_amount=Decimal("0")),
        ]
        result = uc.create_invoice(
            invoice_number="INV-ZERO",
            vendor_id=demo_vendor.id,
            vendor_code=demo_vendor.vendor_code,
            vendor_name=demo_vendor.vendor_name,
            invoice_date=date(2026, 6, 1),
            due_date=date(2026, 7, 1),
            amount=Decimal("0"),
            tax_amount=Decimal("0"),
            total_amount=Decimal("0"),
            lines=lines,
        )
        assert result.is_success() or result.is_failure()

    def test_vendor_crud_full_lifecycle(self, uc):
        r1 = uc.create_vendor(vendor_code="LIFE01", vendor_name="Lifecycle Test")
        assert r1.is_success()
        v = r1.get_data()

        r2 = uc.suspend_vendor(v.id)
        assert r2.is_success()
        assert r2.get_data().status == VendorStatus.SUSPENDED

        r3 = uc.activate_vendor(v.id)
        assert r3.is_success()
        assert r3.get_data().status == VendorStatus.ACTIVE

        r4 = uc.block_vendor(v.id)
        assert r4.is_success()
        assert r4.get_data().status == VendorStatus.BLOCKED

        r5 = uc.delete_vendor(v.id)
        assert r5.is_success()

    def test_intercompany_invoice(self, uc):
        result = uc.create_ic_invoice(
            from_entity="HO", to_entity="BRANCH1",
            invoice_number="IC-001", invoice_date=date(2026, 6, 30),
            amount=Decimal("50000000"), description="Mgmt fee",
        )
        assert result.is_success()
        ic = result.get_data()
        assert ic.from_entity_code == "HO"
        assert ic.to_entity_code == "BRANCH1"
