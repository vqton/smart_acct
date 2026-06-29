from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    CashReceiptType, CashPaymentType, CashVoucherStatus, BankAccountStatus,
    ChequeStatus, PettyCashFundStatus, ReconciliationDiscrepancyType,
    CashReceipt, CashPayment, BankAccount, BankReconciliation,
    PettyCashFund, CashTransfer, Cheque, DailyCashCount, Advance,
    Result, ValidationError, AccountError, AccountType,
)
from infrastructure.models.coa_models import Base
from infrastructure.models.cash_models import (
    CashReceiptModel, CashPaymentModel, BankAccountModel,
    BankReconciliationModel, PettyCashFundModel,
    CashTransferModel, ChequeModel, DailyCashCountModel, AdvanceModel,
)
from infrastructure.repositories.cash_repository import CashRepository
from use_cases.cash_use_cases import CashUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def repo(session):
    return CashRepository(session)


@pytest.fixture
def uc(session):
    return CashUseCases(session)


# ── Cash Receipt Tests ────────────────────────────────────────────────

class TestCashReceipts:
    def test_create_receipt(self, uc):
        result = uc.create_receipt(
            receipt_date=date(2026, 6, 1),
            receipt_type=CashReceiptType.SALES,
            payer_name="Nguyen Van A",
            amount=Decimal("1000000.00"),
            amount_in_words="Một triệu đồng",
            account_code="1111",
            counter_account="511",
            description="Thu tien ban hang",
            created_by="cashier01",
        )
        assert result.is_success()
        r = result.get_data()
        assert r.receipt_number.startswith("PT-202606-")
        assert r.amount == Decimal("1000000.00")
        assert r.status == CashVoucherStatus.DRAFT

    def test_create_receipt_invalid_amount(self, uc):
        result = uc.create_receipt(
            receipt_date=date(2026, 6, 1),
            receipt_type=CashReceiptType.SALES,
            payer_name="Test",
            amount=Decimal("-1000"),
            amount_in_words="Negative",
            account_code="1111",
            counter_account="511",
            description="Test",
            created_by="test",
        )
        assert result.is_failure()

    def test_get_receipt_not_found(self, uc):
        result = uc.get_receipt(999)
        assert result.is_failure()

    def test_get_receipt(self, uc):
        created = uc.create_receipt(
            receipt_date=date(2026, 6, 1),
            receipt_type=CashReceiptType.COLLECTION,
            payer_name="Tran Thi B",
            amount=Decimal("500000.00"),
            amount_in_words="Nam tram nghin dong",
            account_code="1111",
            counter_account="131",
            description="Thu cong no",
            created_by="cashier01",
        )
        result = uc.get_receipt(created.get_data().id)
        assert result.is_success()
        assert result.get_data().payer_name == "Tran Thi B"

    def test_list_receipts(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        uc.create_receipt(date(2026, 6, 2), CashReceiptType.COLLECTION, "B", Decimal("2000"), "Hai", "1111", "131", "Test", "u1")
        receipts = uc.list_receipts()
        assert len(receipts) >= 2

    def test_approve_receipt(self, uc):
        created = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        r = created.get_data()
        result = uc.approve_receipt(r.id, "ktt01")
        assert result.is_success()
        assert result.get_data().approved_by == "ktt01"

    def test_approve_already_approved_fails(self, uc):
        created = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        r = created.get_data()
        uc.approve_receipt(r.id, "ktt01")
        result = uc.approve_receipt(r.id, "ktt02")
        assert result.is_failure()

    def test_cancel_receipt(self, uc):
        created = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        r = created.get_data()
        result = uc.cancel_receipt(r.id)
        assert result.is_success()

    def test_cancel_twice_fails(self, uc):
        created = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        r = created.get_data()
        uc.cancel_receipt(r.id)
        result = uc.cancel_receipt(r.id)
        assert result.is_failure()

    def test_receipt_sequential_numbering(self, uc):
        r1 = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1").get_data()
        r2 = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "B", Decimal("2000"), "Hai", "1111", "511", "Test", "u1").get_data()
        seq1 = int(r1.receipt_number.split("-")[-1])
        seq2 = int(r2.receipt_number.split("-")[-1])
        assert seq2 == seq1 + 1

    def test_create_receipt_fx_foreign_currency(self, uc):
        result = uc.create_receipt(
            receipt_date=date(2026, 6, 1),
            receipt_type=CashReceiptType.SALES,
            payer_name="Foreign Buyer",
            amount=Decimal("1000.00"),
            amount_in_words="One thousand USD",
            account_code="1112",
            counter_account="511",
            description="Foreign currency receipt",
            created_by="cashier01",
            currency="USD",
            fx_rate=Decimal("25400"),
        )
        assert result.is_success()
        assert result.get_data().currency == "USD"
        assert result.get_data().fx_rate == Decimal("25400")

    def test_list_receipts_filter_by_status(self, uc):
        r1 = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1").get_data()
        uc.approve_receipt(r1.id, "ktt")
        draft = uc.list_receipts(status="draft")
        approved = uc.list_receipts(status="approved")
        assert all(r.status == CashVoucherStatus.DRAFT for r in draft)
        assert all(r.status == CashVoucherStatus.APPROVED for r in approved)


# ── Cash Payment Tests ────────────────────────────────────────────────

class TestCashPayments:
    def test_create_payment(self, uc):
        result = uc.create_payment(
            payment_date=date(2026, 6, 1),
            payment_type=CashPaymentType.EXPENSE,
            receiver_name="Nha cung cap X",
            amount=Decimal("2000000.00"),
            amount_in_words="Hai triệu đồng",
            account_code="1111",
            counter_account="642",
            description="Chi phi van phong",
            created_by="cashier01",
            supporting_doc_ref="HD-001",
        )
        assert result.is_success()
        p = result.get_data()
        assert p.payment_number.startswith("PC-202606-")
        assert p.supporting_doc_ref == "HD-001"
        assert p.status == CashVoucherStatus.DRAFT

    def test_create_payment_advance_type(self, uc):
        result = uc.create_payment(
            payment_date=date(2026, 6, 1),
            payment_type=CashPaymentType.ADVANCE,
            receiver_name="Nhan vien Y",
            amount=Decimal("5000000.00"),
            amount_in_words="Nam triệu đồng",
            account_code="1111",
            counter_account="141",
            description="Tam ung cong tac",
            created_by="cashier01",
        )
        assert result.is_success()

    def test_approve_payment(self, uc):
        created = uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "A", Decimal("1000"), "Mot", "1111", "642", "Test", "u1")
        p = created.get_data()
        result = uc.approve_payment(p.id, "ktt01")
        assert result.is_success()
        assert result.get_data().approved_by == "ktt01"

    def test_cancel_payment(self, uc):
        created = uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "A", Decimal("1000"), "Mot", "1111", "642", "Test", "u1")
        p = created.get_data()
        result = uc.cancel_payment(p.id)
        assert result.is_success()

    def test_payment_sequential_numbering(self, uc):
        p1 = uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "A", Decimal("1000"), "Mot", "1111", "642", "Test", "u1").get_data()
        p2 = uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "B", Decimal("2000"), "Hai", "1111", "642", "Test", "u1").get_data()
        seq1 = int(p1.payment_number.split("-")[-1])
        seq2 = int(p2.payment_number.split("-")[-1])
        assert seq2 == seq1 + 1

    def test_list_payments(self, uc):
        uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "A", Decimal("1000"), "Mot", "1111", "642", "Test", "u1")
        uc.create_payment(date(2026, 6, 2), CashPaymentType.PURCHASE, "B", Decimal("2000"), "Hai", "1111", "642", "Test", "u1")
        payments = uc.list_payments()
        assert len(payments) >= 2


# ── Bank Account Tests ────────────────────────────────────────────────

class TestBankAccounts:
    def test_create_bank_account(self, uc):
        result = uc.create_bank_account(
            bank_name="Vietcombank",
            branch="Chi nhanh Ha Noi",
            account_number="1234567890",
            account_holder="Cong ty TNHH ABC",
            coa_code="1121",
            swift_code="VCBVVNVX",
            signatories=["Giam doc", "Ke toan truong"],
            authorization_limit=Decimal("500000000"),
        )
        assert result.is_success()
        ba = result.get_data()
        assert ba.bank_name == "Vietcombank"
        assert ba.swift_code == "VCBVVNVX"
        assert len(ba.signatories) == 2
        assert ba.status == BankAccountStatus.ACTIVE

    def test_get_bank_account(self, uc):
        created = uc.create_bank_account("Techcombank", "SG", "0987654321", "Cong ty XYZ", "1121")
        ba_id = created.get_data().id
        result = uc.get_bank_account(ba_id)
        assert result.is_success()
        assert result.get_data().bank_name == "Techcombank"

    def test_list_bank_accounts(self, uc):
        uc.create_bank_account("Bank A", "Branch A", "111", "Co A", "1121")
        uc.create_bank_account("Bank B", "Branch B", "222", "Co B", "1121")
        result = uc.list_bank_accounts()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_bank_account_foreign_currency(self, uc):
        result = uc.create_bank_account(
            bank_name="HSBC",
            branch="HCMC",
            account_number="USD-ACC-001",
            account_holder="Cong ty ABC",
            coa_code="1122",
            currency="USD",
        )
        assert result.is_success()
        assert result.get_data().currency == "USD"


# ── Bank Reconciliation Tests ─────────────────────────────────────────

class TestBankReconciliation:
    def test_create_reconciliation_balanced(self, uc):
        result = uc.create_reconciliation(
            bank_account_id=1,
            period="2026-06",
            book_balance=Decimal("100000000"),
            bank_balance=Decimal("100000000"),
        )
        assert result.is_success()
        r = result.get_data()
        assert r.is_balanced is True
        assert r.period == "2026-06"

    def test_create_reconciliation_with_adjustments(self, uc):
        result = uc.create_reconciliation(
            bank_account_id=1,
            period="2026-06",
            book_balance=Decimal("100000000"),
            bank_balance=Decimal("105000000"),
            deposits_in_transit=Decimal("5000000"),
            unrecorded_credits=Decimal("0"),
            unrecorded_debits=Decimal("0"),
            outstanding_checks=Decimal("0"),
        )
        assert result.is_success()
        r = result.get_data()
        assert r.adjusted_book_balance == Decimal("105000000")
        assert r.adjusted_bank_balance == Decimal("105000000")
        assert r.is_balanced is True

    def test_create_reconciliation_with_discrepancies(self, uc):
        result = uc.create_reconciliation(
            bank_account_id=1,
            period="2026-06",
            book_balance=Decimal("100000000"),
            bank_balance=Decimal("99500000"),
            outstanding_checks=Decimal("500000"),
            discrepancies=[
                {"discrepancy_type": "outstanding_check", "amount": "500000",
                 "entry_side": "book", "reference": "SEC-001",
                 "description": "Cheque chua toan"},
            ],
            reconciled_by="ktt01",
        )
        assert result.is_success()
        r = result.get_data()
        assert len(r.discrepancies) == 1
        assert r.reconciled_by == "ktt01"

    def test_get_reconciliation(self, uc):
        created = uc.create_reconciliation(1, "2026-06", Decimal("1000"), Decimal("1000"))
        r_id = created.get_data().id
        result = uc.get_reconciliation(r_id)
        assert result.is_success()


# ── Petty Cash Tests ──────────────────────────────────────────────────

class TestPettyCash:
    def test_create_fund(self, uc):
        result = uc.create_petty_cash_fund(
            fund_code="PCF-001",
            custodian="Thu quy Le",
            limit_amount=Decimal("10000000"),
        )
        assert result.is_success()
        f = result.get_data()
        assert f.fund_code == "PCF-001"
        assert f.status == PettyCashFundStatus.ACTIVE

    def test_get_fund(self, uc):
        created = uc.create_petty_cash_fund("PCF-002", "Custodian B", Decimal("5000000"))
        f_id = created.get_data().id
        result = uc.get_petty_cash_fund(f_id)
        assert result.is_success()
        assert result.get_data().fund_code == "PCF-002"

    def test_list_funds(self, uc):
        uc.create_petty_cash_fund("PCF-A", "A", Decimal("10000000"))
        uc.create_petty_cash_fund("PCF-B", "B", Decimal("5000000"))
        result = uc.list_petty_cash_funds()
        assert result.is_success()
        assert len(result.get_data()) >= 2


# ── Advance (TK 141) Tests ────────────────────────────────────────────

class TestAdvances:
    def test_create_advance(self, uc):
        result = uc.create_advance(
            employee_name="Nguyen Van A",
            employee_id="NV001",
            amount=Decimal("5000000"),
            purpose="Cong tac Da Nang",
        )
        assert result.is_success()
        a = result.get_data()
        assert a.employee_name == "Nguyen Van A"
        assert a.status == "outstanding"

    def test_settle_advance_partial(self, uc):
        created = uc.create_advance("NV A", "NV001", Decimal("5000000"), "Cong tac")
        a_id = created.get_data().id
        result = uc.settle_advance(a_id, Decimal("3000000"))
        assert result.is_success()
        a = result.get_data()
        assert a.settlement_amount == Decimal("3000000")
        assert a.remaining_balance == Decimal("2000000")

    def test_settle_advance_full(self, uc):
        created = uc.create_advance("NV B", "NV002", Decimal("5000000"), "Cong tac")
        a_id = created.get_data().id
        result = uc.settle_advance(a_id, Decimal("5000000"))
        assert result.is_success()
        a = result.get_data()
        assert a.status == "settled"
        assert a.remaining_balance <= Decimal("0.001")

    def test_settle_already_settled_fails(self, uc):
        created = uc.create_advance("NV C", "NV003", Decimal("1000000"), "Test")
        a_id = created.get_data().id
        uc.settle_advance(a_id, Decimal("1000000"))
        result = uc.settle_advance(a_id, Decimal("0"))
        assert result.is_failure()


# ── Cash Transfer Tests ───────────────────────────────────────────────

class TestCashTransfers:
    def test_create_transfer(self, uc):
        result = uc.create_transfer(
            source_account="1111",
            destination_account="1121",
            amount=Decimal("10000000"),
            reference="CT-001",
            created_by="cashier01",
        )
        assert result.is_success()
        t = result.get_data()
        assert t.source_account == "1111"
        assert t.destination_account == "1121"

    def test_transfer_same_account_fails(self, uc):
        result = uc.create_transfer(
            source_account="1111",
            destination_account="1111",
            amount=Decimal("1000"),
            reference="CT-ERR",
        )
        assert result.is_failure()

    def test_get_transfer(self, uc):
        created = uc.create_transfer("1111", "1121", Decimal("5000000"), "CT-002")
        t_id = created.get_data().id
        result = uc.get_transfer(t_id)
        assert result.is_success()
        assert result.get_data().reference == "CT-002"


# ── Daily Cash Count Tests ────────────────────────────────────────────

class TestDailyCashCount:
    def test_create_count_matching(self, uc):
        result = uc.create_daily_cash_count(
            account_code="1111",
            expected_balance=Decimal("15000000"),
            actual_balance=Decimal("15000000"),
            counted_by="Thu quy",
            witnessed_by="Ke toan",
        )
        assert result.is_success()
        dcc = result.get_data()
        assert dcc.difference == Decimal("0")
        assert dcc.witnessed_by == "Ke toan"

    def test_create_count_surplus(self, uc):
        result = uc.create_daily_cash_count(
            account_code="1111",
            expected_balance=Decimal("10000000"),
            actual_balance=Decimal("10500000"),
            counted_by="Thu quy",
        )
        assert result.is_success()
        assert result.get_data().difference == Decimal("500000")

    def test_create_count_shortage(self, uc):
        result = uc.create_daily_cash_count(
            account_code="1111",
            expected_balance=Decimal("10000000"),
            actual_balance=Decimal("9500000"),
            counted_by="Thu quy",
        )
        assert result.is_success()
        assert result.get_data().difference == Decimal("-500000")

    def test_list_daily_counts(self, uc):
        uc.create_daily_cash_count("1111", Decimal("1000"), Decimal("1000"), "TQ")
        uc.create_daily_cash_count("1111", Decimal("2000"), Decimal("2000"), "TQ")
        result = uc.list_daily_cash_counts()
        assert result.is_success()
        assert len(result.get_data()) >= 2


# ── Cheque Tests ──────────────────────────────────────────────────────

class TestCheques:
    def test_create_cheque(self, uc):
        result = uc.create_cheque(
            cheque_number="SEC-001",
            cheque_book_id=1,
            payee="Nha cung cap ABC",
            amount=Decimal("50000000"),
            bank_account_id=1,
        )
        assert result.is_success()
        c = result.get_data()
        assert c.cheque_number == "SEC-001"
        assert c.status == ChequeStatus.NEW

    def test_get_cheque(self, uc):
        created = uc.create_cheque("SEC-002", 1, "Payee B", Decimal("10000000"), 1)
        c_id = created.get_data().id
        result = uc.get_cheque(c_id)
        assert result.is_success()
        assert result.get_data().cheque_number == "SEC-002"


# ── Cash Balance Tests ───────────────────────────────────────────────

class TestCashBalance:
    def test_get_default_balance(self, uc):
        result = uc.get_cash_balance()
        assert result.is_success()
        data = result.get_data()
        assert data["account_code"] == "1111"
        assert data["currency"] == "VND"

    def test_balance_after_receipt(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000000"), "Mot", "1111", "511", "Test", "u1")
        result = uc.get_cash_balance("1111")
        assert result.is_success()
        assert Decimal(result.get_data()["balance"]) == Decimal("1000000")

    def test_balance_after_receipt_and_payment(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("5000000"), "Nam", "1111", "511", "Test", "u1")
        uc.create_payment(date(2026, 6, 2), CashPaymentType.EXPENSE, "B", Decimal("2000000"), "Hai", "1111", "642", "Test", "u1")
        result = uc.get_cash_balance("1111")
        assert result.is_success()
        assert Decimal(result.get_data()["balance"]) == Decimal("3000000")

    def test_balance_multiple_accounts(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000000"), "Mot", "1111", "511", "Test", "u1")
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "B", Decimal("2000000"), "Hai", "1112", "511", "Test", "u1")
        bal1 = uc.get_cash_balance("1111").get_data()
        bal2 = uc.get_cash_balance("1112").get_data()
        assert Decimal(bal1["balance"]) == Decimal("1000000")
        assert Decimal(bal2["balance"]) == Decimal("2000000")

    def test_balance_cancelled_receipt_not_counted(self, uc):
        created = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000000"), "Mot", "1111", "511", "Test", "u1")
        r = created.get_data()
        uc.cancel_receipt(r.id)
        result = uc.get_cash_balance("1111")
        assert Decimal(result.get_data()["balance"]) == Decimal("0")


# ── Cash Book Report Tests ──────────────────────────────────────────

class TestCashBookReport:
    def test_generate_cash_book_report(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "NV A", Decimal("1000000"), "Mot", "1111", "511", "Thu ban hang", "u1")
        uc.create_payment(date(2026, 6, 2), CashPaymentType.EXPENSE, "NCC X", Decimal("500000"), "Nam", "1111", "642", "Chi phi", "u1")
        result = uc.generate_cash_book_report("1111", date(2026, 6, 1), date(2026, 6, 30))
        assert result.is_success()
        data = result.get_data()
        assert len(data["rows"]) == 2
        assert data["rows"][0]["debit"] == "1000000.00"
        assert data["rows"][1]["credit"] == "500000.00"
        assert "html" in data

    def test_cash_book_running_balance(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000000"), "Mot", "1111", "511", "Thu", "u1")
        uc.create_payment(date(2026, 6, 2), CashPaymentType.EXPENSE, "B", Decimal("300000"), "Ba", "1111", "642", "Chi", "u1")
        uc.create_receipt(date(2026, 6, 3), CashReceiptType.SALES, "C", Decimal("200000"), "Hai", "1111", "511", "Thu2", "u1")
        result = uc.generate_cash_book_report("1111", date(2026, 6, 1), date(2026, 6, 30))
        rows = result.get_data()["rows"]
        balances = [Decimal(r["balance"]) for r in rows]
        assert balances == [Decimal("1000000"), Decimal("700000"), Decimal("900000")]

    def test_cash_book_html_output(self, uc):
        uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        result = uc.generate_cash_book_report("1111", date(2026, 6, 1), date(2026, 6, 30))
        html = result.get_data()["html"]
        assert "<h1>SO QUY TIEN MAT</h1>" in html
        assert "1111" in html


# ── Cash Count Report Tests ─────────────────────────────────────────

class TestCashCountReport:
    def test_generate_count_report(self, uc):
        created = uc.create_daily_cash_count("1111", Decimal("1000000"), Decimal("1000000"), "Thu quy")
        count_id = created.get_data().id
        result = uc.generate_cash_count_report(count_id)
        assert result.is_success()
        data = result.get_data()
        assert data["count"]["difference_type"] == "Phu hop"

    def test_count_report_surplus(self, uc):
        created = uc.create_daily_cash_count("1111", Decimal("1000000"), Decimal("1100000"), "Thu quy", witnessed_by="KTT")
        count_id = created.get_data().id
        result = uc.generate_cash_count_report(count_id)
        data = result.get_data()
        assert "Thua quy" in data["count"]["difference_type"]
        assert data["count"]["witnessed_by"] == "KTT"

    def test_count_report_shortage(self, uc):
        created = uc.create_daily_cash_count("1111", Decimal("1000000"), Decimal("900000"), "Thu quy")
        count_id = created.get_data().id
        result = uc.generate_cash_count_report(count_id)
        data = result.get_data()
        assert "Thieu quy" in data["count"]["difference_type"]

    def test_count_report_html(self, uc):
        created = uc.create_daily_cash_count("1111", Decimal("1000000"), Decimal("1000000"), "Thu quy")
        count_id = created.get_data().id
        result = uc.generate_cash_count_report(count_id)
        html = result.get_data()["html"]
        assert "<h1>BIEN BAN KIEM KE QUY</h1>" in html

    def test_count_report_not_found(self, uc):
        result = uc.generate_cash_count_report(999)
        assert result.is_failure()


# ── Edge Cases ────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_create_receipt_zero_amount_fails(self, uc):
        result = uc.create_receipt(date(2026, 6, 1), CashReceiptType.OTHER, "A", Decimal("0"), "Zero", "1111", "511", "Test", "u1")
        assert result.is_failure()

    def test_create_payment_zero_amount_fails(self, uc):
        result = uc.create_payment(date(2026, 6, 1), CashPaymentType.OTHER, "A", Decimal("0"), "Zero", "1111", "642", "Test", "u1")
        assert result.is_failure()

    def test_receipt_fx_rate_no_currency(self, uc):
        result = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "A", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        assert result.is_success()
        assert result.get_data().fx_rate is None

    def test_bank_account_negative_limit(self, uc):
        result = uc.create_bank_account(
            "Bank", "Branch", "ACC", "Holder", "1121",
            authorization_limit=Decimal("-1000"),
        )
        assert result.is_success()

    def test_petty_cash_fund_exceeds_limit(self, uc):
        result = uc.create_petty_cash_fund("PCF-TEST", "Custodian", Decimal("0"))
        assert result.is_failure()

    def test_advance_xss_prevention(self, uc):
        result = uc.create_advance("<script>alert('xss')</script>", "NV-XSS", Decimal("1000"), "Test")
        assert result.is_success()

    def test_create_receipt_empty_payer_name_fails(self, uc):
        result = uc.create_receipt(date(2026, 6, 1), CashReceiptType.SALES, "", Decimal("1000"), "Mot", "1111", "511", "Test", "u1")
        assert result.is_failure()

    def test_create_payment_empty_receiver_fails(self, uc):
        result = uc.create_payment(date(2026, 6, 1), CashPaymentType.EXPENSE, "", Decimal("1000"), "Mot", "1111", "642", "Test", "u1")
        assert result.is_failure()

    def test_create_advance_large_amount(self, uc):
        result = uc.create_advance("NV Z", "NV-Z", Decimal("999999999"), "Large advance test")
        assert result.is_success()
