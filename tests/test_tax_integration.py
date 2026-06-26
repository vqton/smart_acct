from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from domain import (
    TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus, TaxPaymentStatus,
    InvoiceStatus, TaxAdjustmentType, TaxIncentiveType,
    TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive,
    EInvoice, InvoiceType, TaxSchedule,
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
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def repo(session):
    return TaxRepository(session)


@pytest.fixture
def uc(session):
    return TaxUseCases(session)


# ── TaxRepository: TaxDeclaration ───────────────────────────────────────

class TestTaxDeclaration:
    def test_create_declaration(self, repo, session):
        decl = TaxDeclaration(
            tax_type=TaxType.VAT_DEDUCTION,
            declaration_type=DeclarationType.ORIGINAL,
            form_code="01/GTGT",
            period_year=2025,
            period_month=3,
            created_by="test_user",
        )
        result = repo.create_declaration(decl)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.form_code == "01/GTGT"
        assert created.tax_type == TaxType.VAT_DEDUCTION
        assert created.status == DeclarationStatus.DRAFT
        assert created.period_month == 3

    def test_get_declaration(self, repo, session):
        decl = TaxDeclaration(tax_type=TaxType.CIT, form_code="03/TNDN", period_year=2025, period_quarter=1)
        result = repo.create_declaration(decl)
        decl_id = result.get_data().id
        got = repo.get_declaration(decl_id)
        assert got is not None
        assert got.tax_type == TaxType.CIT
        assert got.period_quarter == 1

    def test_get_declaration_not_found(self, repo, session):
        assert repo.get_declaration(9999) is None

    def test_list_declarations(self, repo, session):
        for i in range(3):
            d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=(i + 1) * 2, created_by=f"user{i}")
            repo.create_declaration(d)
        decls = repo.list_declarations()
        assert len(decls) == 3
        vat_decls = repo.list_declarations(tax_type=TaxType.VAT_DEDUCTION)
        assert len(vat_decls) == 3
        cit_decls = repo.list_declarations(tax_type=TaxType.CIT)
        assert len(cit_decls) == 0

    def test_update_declaration(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        result = repo.create_declaration(d)
        decl_id = result.get_data().id
        result = repo.update_declaration(decl_id, notes="Updated notes", total_revenue=Decimal("1000.00"))
        assert result.is_success()
        updated = result.get_data()
        assert updated.notes == "Updated notes"
        assert updated.total_revenue == Decimal("1000.00")

    def test_delete_declaration(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        result = repo.create_declaration(d)
        decl_id = result.get_data().id
        result = repo.delete_declaration(decl_id)
        assert result.is_success()
        assert repo.get_declaration(decl_id) is None


# ── TaxRepository: TaxLine ──────────────────────────────────────────────

class TestTaxLine:
    def test_create_line(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        line = TaxLine(
            declaration_id=decl.id,
            line_code="[21]",
            label="Doanh thu bán hàng hóa",
            amount=Decimal("50000000.00"),
            sort_order=10,
        )
        result = repo.create_line(line)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.line_code == "[21]"

    def test_list_lines(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        for i in range(3):
            repo.create_line(TaxLine(declaration_id=decl.id, line_code=f"[{i}]", label=f"Line {i}", sort_order=i))
        lines = repo.list_lines(decl.id)
        assert len(lines) == 3
        assert lines[0].sort_order == 0

    def test_get_line(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        result = repo.create_line(TaxLine(declaration_id=decl.id, line_code="[A]", label="Test"))
        line_id = result.get_data().id
        got = repo.get_line(line_id)
        assert got is not None
        assert got.line_code == "[A]"

    def test_update_line(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        result = repo.create_line(TaxLine(declaration_id=decl.id, line_code="[B]", label="Old"))
        line_id = result.get_data().id
        repo.update_line(line_id, amount=Decimal("999.00"))
        updated = repo.get_line(line_id)
        assert updated.amount == Decimal("999.00")

    def test_delete_line(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        result = repo.create_line(TaxLine(declaration_id=decl.id, line_code="[C]", label="Delete me"))
        line_id = result.get_data().id
        repo.delete_line(line_id)
        assert repo.get_line(line_id) is None


# ── TaxRepository: TaxPayment ───────────────────────────────────────────

class TestTaxPayment:
    def test_create_payment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        pmt = TaxPayment(
            declaration_id=decl.id,
            tax_type=TaxType.VAT_DEDUCTION,
            amount=Decimal("5000000.00"),
            payment_date=date(2025, 2, 20),
            due_date=date(2025, 1, 20),
            budget_account="1701",
        )
        result = repo.create_payment(pmt)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.amount == Decimal("5000000.00")
        assert created.payment_status == TaxPaymentStatus.PENDING

    def test_get_payment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        pmt = TaxPayment(declaration_id=decl.id, tax_type=TaxType.VAT_DEDUCTION, amount=Decimal("1000"), payment_date=date(2025,3,1), due_date=date(2025,2,20))
        pmt_id = repo.create_payment(pmt).get_data().id
        got = repo.get_payment(pmt_id)
        assert got is not None
        assert got.amount == Decimal("1000")

    def test_get_payment_not_found(self, repo, session):
        assert repo.get_payment(9999) is None

    def test_list_payments(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        for _ in range(2):
            repo.create_payment(TaxPayment(declaration_id=decl.id, tax_type=TaxType.VAT_DEDUCTION, amount=Decimal("500"), payment_date=date(2025,4,1), due_date=date(2025,3,20)))
        payments = repo.list_payments(declaration_id=decl.id)
        assert len(payments) == 2

    def test_update_payment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        pmt = TaxPayment(declaration_id=decl.id, tax_type=TaxType.VAT_DEDUCTION, amount=Decimal("1000"), payment_date=date(2025,3,1), due_date=date(2025,2,20))
        pmt_id = repo.create_payment(pmt).get_data().id
        repo.update_payment(pmt_id, payment_status=TaxPaymentStatus.PAID)
        updated = repo.get_payment(pmt_id)
        assert updated.payment_status == TaxPaymentStatus.PAID

    def test_delete_payment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        pmt = TaxPayment(declaration_id=decl.id, tax_type=TaxType.VAT_DEDUCTION, amount=Decimal("500"), payment_date=date(2025,4,1), due_date=date(2025,3,20))
        pmt_id = repo.create_payment(pmt).get_data().id
        repo.delete_payment(pmt_id)
        assert repo.get_payment(pmt_id) is None


# ── TaxRepository: TaxAdjustment ────────────────────────────────────────

class TestTaxAdjustment:
    def test_create_adjustment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        adj = TaxAdjustment(
            declaration_id=decl.id,
            adjustment_type=TaxAdjustmentType.CORRECTION,
            reason="Sai sót số liệu",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("1200000"),
            difference_amount=Decimal("200000"),
        )
        result = repo.create_adjustment(adj)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.difference_amount == Decimal("200000")

    def test_get_adjustment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        adj = TaxAdjustment(declaration_id=decl.id, adjustment_type=TaxAdjustmentType.CORRECTION, reason="fix", original_amount=Decimal("100"), adjusted_amount=Decimal("150"), difference_amount=Decimal("50"))
        adj_id = repo.create_adjustment(adj).get_data().id
        got = repo.get_adjustment(adj_id)
        assert got is not None
        assert got.declaration_id == decl.id

    def test_get_adjustment_not_found(self, repo, session):
        assert repo.get_adjustment(9999) is None

    def test_list_adjustments(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        for _ in range(2):
            repo.create_adjustment(TaxAdjustment(declaration_id=decl.id, adjustment_type=TaxAdjustmentType.CORRECTION, reason="fix", original_amount=Decimal("100"), adjusted_amount=Decimal("120"), difference_amount=Decimal("20")))
        adjustments = repo.list_adjustments(declaration_id=decl.id)
        assert len(adjustments) == 2

    def test_delete_adjustment(self, repo, session):
        d = TaxDeclaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=1)
        decl = repo.create_declaration(d).get_data()
        adj = TaxAdjustment(declaration_id=decl.id, adjustment_type=TaxAdjustmentType.CORRECTION, reason="fix", original_amount=Decimal("100"), adjusted_amount=Decimal("120"), difference_amount=Decimal("20"))
        adj_id = repo.create_adjustment(adj).get_data().id
        repo.delete_adjustment(adj_id)
        assert repo.get_adjustment(adj_id) is None


# ── TaxRepository: TaxIncentive ─────────────────────────────────────────

class TestTaxIncentive:
    def test_create_incentive(self, repo, session):
        inc = TaxIncentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
            code="UT_CNC",
            name="Ưu đãi công nghệ cao",
            legal_basis="Luật số 71/2024/QH15",
            rate_value=Decimal("10"),
            is_percentage=True,
            valid_from=date(2025, 1, 1),
        )
        result = repo.create_incentive(inc)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.code == "UT_CNC"

    def test_get_incentive(self, repo, session):
        inc = TaxIncentive(tax_type=TaxType.CIT, incentive_type=TaxIncentiveType.EXEMPTION, code="UT_A", name="A", legal_basis="Law", valid_from=date(2025,1,1))
        inc_id = repo.create_incentive(inc).get_data().id
        got = repo.get_incentive(inc_id)
        assert got is not None
        assert got.code == "UT_A"

    def test_list_incentives(self, repo, session):
        for code in ["UT_X", "UT_Y"]:
            repo.create_incentive(TaxIncentive(tax_type=TaxType.CIT, incentive_type=TaxIncentiveType.EXEMPTION, code=code, name=code, legal_basis="Law", valid_from=date(2025,1,1)))
        incentives = repo.list_incentives()
        assert len(incentives) == 2
        cit_incentives = repo.list_incentives(tax_type=TaxType.CIT)
        assert len(cit_incentives) == 2

    def test_delete_incentive(self, repo, session):
        inc = TaxIncentive(tax_type=TaxType.CIT, incentive_type=TaxIncentiveType.EXEMPTION, code="UT_Z", name="Z", legal_basis="Law", valid_from=date(2025,1,1))
        inc_id = repo.create_incentive(inc).get_data().id
        repo.delete_incentive(inc_id)
        assert repo.get_incentive(inc_id) is None


# ── TaxRepository: EInvoice ─────────────────────────────────────────────

class TestEInvoice:
    def test_create_invoice(self, repo, session):
        inv = EInvoice(
            invoice_number="000001",
            invoice_series="1C24TAA",
            invoice_date=date(2025, 1, 15),
            invoice_type=InvoiceType.SALES,
            seller_tax_code="1234567890",
            seller_name="Test Co",
            seller_address="Hanoi",
            subtotal=Decimal("10000000"),
            vat_rate=Decimal("0.1"),
            vat_amount=Decimal("1000000"),
            grand_total=Decimal("11000000"),
        )
        result = repo.create_invoice(inv)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.invoice_type == InvoiceType.SALES

    def test_get_invoice(self, repo, session):
        inv = EInvoice(invoice_number="000002", invoice_series="1C24TAA", invoice_date=date(2025,2,1),
                       invoice_type=InvoiceType.SALES, seller_tax_code="1234567890", seller_name="Test")
        result = repo.create_invoice(inv)
        inv_id = result.get_data().id
        got = repo.get_invoice(inv_id)
        assert got is not None
        assert got.invoice_number == "000002"

    def test_list_invoices(self, repo, session):
        for i in range(2):
            repo.create_invoice(EInvoice(invoice_number=f"00000{i+3}", invoice_series="1C24TAA",
                invoice_date=date(2025,3,1), invoice_type=InvoiceType.SALES,
                seller_tax_code="1234567890", seller_name="Test"))
        invs = repo.list_invoices()
        assert len(invs) == 2

    def test_update_invoice(self, repo, session):
        inv = EInvoice(invoice_number="000005", invoice_series="1C24TAA", invoice_date=date(2025,4,1),
                       invoice_type=InvoiceType.SALES, seller_tax_code="1234567890", seller_name="Test")
        inv_id = repo.create_invoice(inv).get_data().id
        repo.update_invoice(inv_id, status=InvoiceStatus.SIGNED, verification_code="ABC123")
        updated = repo.get_invoice(inv_id)
        assert updated.status == InvoiceStatus.SIGNED
        assert updated.verification_code == "ABC123"

    def test_delete_invoice(self, repo, session):
        inv = EInvoice(invoice_number="000006", invoice_series="1C24TAA", invoice_date=date(2025,5,1),
                       invoice_type=InvoiceType.SALES, seller_tax_code="1234567890", seller_name="Del")
        inv_id = repo.create_invoice(inv).get_data().id
        repo.delete_invoice(inv_id)
        assert repo.get_invoice(inv_id) is None


# ── TaxRepository: TaxSchedule ──────────────────────────────────────────

class TestTaxSchedule:
    def test_create_schedule(self, repo, session):
        sched = TaxSchedule(
            tax_type=TaxType.VAT_DEDUCTION,
            period_year=2025,
            period_month=3,
            due_date=date(2025, 4, 20),
        )
        result = repo.create_schedule(sched)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.status.value == "pending"

    def test_get_schedule(self, repo, session):
        sched = TaxSchedule(tax_type=TaxType.VAT_DEDUCTION, period_year=2025, period_month=1, due_date=date(2025,2,20))
        sched_id = repo.create_schedule(sched).get_data().id
        got = repo.get_schedule(sched_id)
        assert got is not None

    def test_list_schedule(self, repo, session):
        for m in [1, 2, 3]:
            sched = TaxSchedule(tax_type=TaxType.VAT_DEDUCTION, period_year=2025, period_month=m, due_date=date(2025, m + 1, 20))
            repo.create_schedule(sched)
        scheds = repo.list_schedule(year=2025)
        assert len(scheds) == 3
        vat_scheds = repo.list_schedule(year=2025, tax_type=TaxType.VAT_DEDUCTION)
        assert len(vat_scheds) == 3

    def test_get_upcoming_schedule(self, repo, session):
        from datetime import timedelta
        today = date.today()
        sched = TaxSchedule(tax_type=TaxType.VAT_DEDUCTION, period_year=today.year, period_month=today.month, due_date=today + timedelta(days=3))
        repo.create_schedule(sched)
        upcoming = repo.get_upcoming_schedule(days_ahead=10)
        assert len(upcoming) >= 1


# ── TaxUseCases: Integration ────────────────────────────────────────────

class TestTaxUseCases:
    def test_create_declaration_flow(self, uc, session):
        result = uc.create_declaration(
            tax_type=TaxType.VAT_DEDUCTION,
            form_code="01/GTGT",
            period_year=2025,
            period_month=3,
            created_by="tester",
        )
        assert result.is_success()
        decl = result.get_data()
        assert decl.status == DeclarationStatus.DRAFT

        result = uc.submit_declaration(decl.id)
        assert result.is_success()
        assert result.get_data().status == DeclarationStatus.SUBMITTED

    def test_calculate_vat_deduction(self, uc, session):
        result = uc.create_declaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=3)
        decl_id = result.get_data().id
        result = uc.calculate_vat(
            decl_id,
            method=VATCalculationMethod.DEDUCTION,
            output_lines=[{"amount": 10000000}],
            input_lines=[{"amount": 5000000}],
        )
        assert result.is_success()
        data = result.get_data()
        assert Decimal(data["total_payable"]) > 0

    def test_create_payment_flow(self, uc, session):
        result = uc.create_declaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=3)
        decl_id = result.get_data().id
        result = uc.create_payment(
            declaration_id=decl_id,
            amount=Decimal("5000000"),
            due_date=date(2025, 4, 20),
            payment_date=date(2025, 4, 15),
            tax_type=TaxType.VAT_DEDUCTION,
        )
        assert result.is_success()
        pmt = result.get_data()
        assert pmt.amount == Decimal("5000000")

    def test_create_adjustment_flow(self, uc, session):
        result = uc.create_declaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=3)
        decl_id = result.get_data().id
        result = uc.create_adjustment(
            declaration_id=decl_id,
            adjustment_type=TaxAdjustmentType.CORRECTION,
            reason="Data error",
            original_amount=Decimal("1000000"),
            adjusted_amount=Decimal("1200000"),
        )
        assert result.is_success()
        adj = result.get_data()
        assert adj.difference_amount == Decimal("200000")

    def test_create_line_flow(self, uc, session):
        result = uc.create_declaration(tax_type=TaxType.VAT_DEDUCTION, form_code="01/GTGT", period_year=2025, period_month=3)
        decl_id = result.get_data().id
        result = uc.create_line(
            declaration_id=decl_id,
            line_code="[21]",
            label="Doanh thu",
            amount=Decimal("10000000"),
            sort_order=10,
        )
        assert result.is_success()
        line = result.get_data()
        assert line.line_code == "[21]"
        lines = uc.list_lines(declaration_id=decl_id)
        assert len(lines) == 1

    def test_create_incentive_flow(self, uc, session):
        result = uc.create_incentive(
            tax_type=TaxType.CIT,
            incentive_type=TaxIncentiveType.PREFERENTIAL_RATE,
            code="UT_TEST",
            name="Test Incentive",
            legal_basis="Test Law",
            rate_value=Decimal("10"),
            valid_from=date(2025, 1, 1),
        )
        assert result.is_success()
        inc = result.get_data()
        assert inc.code == "UT_TEST"

    def test_invoice_lifecycle(self, uc, session):
        inv = EInvoice(
            invoice_number="INV001",
            invoice_series="1C24TAA",
            invoice_date=date(2025, 1, 15),
            invoice_type=InvoiceType.SALES,
            seller_tax_code="1234567890",
            seller_name="Test Co",
        )
        result = uc.create_invoice(inv)
        assert result.is_success()
        inv_id = result.get_data().id
        result = uc.update_invoice_status(inv_id, status=InvoiceStatus.SIGNED, verification_code="VC001")
        assert result.is_success()
        assert result.get_data().status == InvoiceStatus.SIGNED

    def test_schedule_generation(self, uc, session):
        result = uc.generate_schedule(year=2025)
        assert result.is_success()
        data = result.get_data()
        assert data["created"] > 0

    def test_due_reminders(self, uc, session):
        result = uc.generate_schedule(year=date.today().year)
        reminders = uc.get_due_reminders(days_ahead=365)
        assert len(reminders) > 0

    def test_get_summary(self, uc, session):
        result = uc.get_summary()
        assert result.is_success()
        data = result.get_data()
        assert "total_declarations" in data
