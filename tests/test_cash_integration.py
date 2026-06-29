from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    CashReceiptType, CashPaymentType, CashVoucherStatus, BankAccountStatus,
    ChequeStatus, PettyCashFundStatus, ReconciliationDiscrepancyType,
    CashReceipt, CashPayment, BankAccount, BankReconciliation,
    PettyCashFund, CashTransfer, Cheque, DailyCashCount, Advance,
    BankStatement, BankTransaction, CashTransferStatus,
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
from presentation.cash_routes import cash_bp


class FakeDBManager:
    def __init__(self, engine):
        self._engine = engine

    def get_session(self):
        return Session(self._engine)

    def close(self):
        pass


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
        data = result.get_data()
        assert "period" in data


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
        data = result.get_data()
        assert data["count"]["difference_type"] == "Phu hop"

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


# ── Bank Statement Tests ─────────────────────────────────────────────

class TestBankStatements:
    def test_import_statement(self, uc):
        result = uc.import_bank_statement(
            bank_account_id=1,
            statement_date=date(2026, 6, 30),
            opening_balance=Decimal("100000000"),
            closing_balance=Decimal("105000000"),
            transactions=[
                {"transaction_date": "2026-06-01", "amount": "2000000", "is_debit": False, "reference": "DEP-001", "description": "Khach hang thanh toan"},
                {"transaction_date": "2026-06-15", "amount": "1000000", "is_debit": True, "reference": "WTH-001", "description": "Rut tien"},
                {"transaction_date": "2026-06-20", "amount": "4000000", "is_debit": False, "reference": "DEP-002", "description": "Chuyen khoan den"},
            ],
        )
        assert result.is_success()
        stmt = result.get_data()
        assert stmt.statement_date == date(2026, 6, 30)
        assert stmt.opening_balance == Decimal("100000000")
        assert stmt.closing_balance == Decimal("105000000")
        assert len(stmt.transactions) == 3

    def test_import_statement_running_balance_mismatch_fails(self, uc):
        result = uc.import_bank_statement(
            bank_account_id=1,
            statement_date=date(2026, 6, 30),
            opening_balance=Decimal("100000000"),
            closing_balance=Decimal("99999999"),
            transactions=[
                {"transaction_date": "2026-06-01", "amount": "5000000", "is_debit": False, "reference": "DEP-001", "description": "Deposit"},
            ],
        )
        assert result.is_failure()

    def test_import_duplicate_statement_fails(self, uc):
        uc.import_bank_statement(1, date(2026, 6, 30), Decimal("1000"), Decimal("2000"), [
            {"transaction_date": "2026-06-01", "amount": "1000", "is_debit": False, "reference": "R1", "description": "Dep"},
        ])
        result = uc.import_bank_statement(1, date(2026, 6, 30), Decimal("1000"), Decimal("2000"), [
            {"transaction_date": "2026-06-01", "amount": "1000", "is_debit": False, "reference": "R1", "description": "Dep"},
        ])
        assert result.is_failure()

    def test_get_statement(self, uc):
        created = uc.import_bank_statement(1, date(2026, 6, 30), Decimal("1000"), Decimal("1000"), [
            {"transaction_date": "2026-06-01", "amount": "500", "is_debit": False, "reference": "R1", "description": "Dep"},
            {"transaction_date": "2026-06-15", "amount": "500", "is_debit": True, "reference": "R2", "description": "Wth"},
        ])
        stmt_id = created.get_data().id
        result = uc.repo.get_statement(stmt_id)
        assert result is not None
        assert result.statement_date == date(2026, 6, 30)
        assert len(result.transactions) == 2

    def test_list_statements(self, uc):
        uc.import_bank_statement(1, date(2026, 5, 31), Decimal("0"), Decimal("5000"), [
            {"transaction_date": "2026-05-01", "amount": "5000", "is_debit": False, "reference": "M1", "description": "May deposit"},
        ])
        uc.import_bank_statement(1, date(2026, 6, 30), Decimal("5000"), Decimal("7000"), [
            {"transaction_date": "2026-06-01", "amount": "2000", "is_debit": False, "reference": "J1", "description": "June deposit"},
        ])
        stmts = uc.repo.list_statements(bank_account_id=1)
        assert len(stmts) >= 2

    def test_import_statement_invalid_data_fails(self, uc):
        result = uc.import_bank_statement(
            bank_account_id=1,
            statement_date=date(2026, 6, 30),
            opening_balance=Decimal("1000"),
            closing_balance=Decimal("2000"),
            transactions=[{"bad_key": "value"}],
        )
        assert result.is_failure()

    def test_parse_csv_vietcombank(self, uc):
        csv_lines = [
            "Ngay giao dich,Ngay hieu luc,So tien,Loai,Ma giao dich,Dien giai,_opening_balance,_closing_balance",
            "2026-06-01,2026-06-01,1000000,IN,DEP-001,Khach hang chuyen tien,10000000,10500000",
            "2026-06-15,2026-06-15,500000,OUT,WTH-001,Rut tien ATM,10000000,10500000",
        ]
        result = uc.parse_csv_statement(1, csv_lines, fmt="vietcombank")
        assert result.is_success()
        stmt = result.get_data()
        assert len(stmt.transactions) == 2

    def test_parse_csv_no_transactions_fails(self, uc):
        result = uc.parse_csv_statement(1, ["header1,header2"], fmt="vietcombank")
        assert result.is_failure()


# ── Cheque Lifecycle Tests ──────────────────────────────────────────

class TestChequeLifecycle:
    def test_issue_cheque(self, uc):
        created = uc.create_cheque("SEC-010", 1, "Payee", Decimal("10000000"), 1)
        c_id = created.get_data().id
        result = uc.issue_cheque(c_id, "NCC XYZ", Decimal("10000000"), 1)
        assert result.is_success()
        c = result.get_data()
        assert c.status == ChequeStatus.ISSUED
        assert c.payee == "NCC XYZ"

    def test_issue_twice_fails(self, uc):
        created = uc.create_cheque("SEC-011", 1, "Payee", Decimal("5000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "NCC", Decimal("5000000"), 1)
        result = uc.issue_cheque(c_id, "NCC2", Decimal("5000000"), 1)
        assert result.is_failure()

    def test_clear_cheque(self, uc):
        created = uc.create_cheque("SEC-020", 1, "Payee", Decimal("20000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "NCC", Decimal("20000000"), 1)
        result = uc.clear_cheque(c_id, date(2026, 7, 15))
        assert result.is_success()
        assert result.get_data().status == ChequeStatus.CLEARED
        assert result.get_data().cleared_date == date(2026, 7, 15)

    def test_clear_from_new_fails(self, uc):
        created = uc.create_cheque("SEC-021", 1, "Payee", Decimal("1000000"), 1)
        result = uc.clear_cheque(created.get_data().id, date(2026, 7, 15))
        assert result.is_failure()

    def test_cancel_cheque(self, uc):
        created = uc.create_cheque("SEC-030", 1, "Payee", Decimal("10000000"), 1)
        c_id = created.get_data().id
        result = uc.cancel_cheque(c_id, "Huy theo yeu cau")
        assert result.is_success()
        assert result.get_data().status == ChequeStatus.CANCELLED
        assert result.get_data().cancelled_reason == "Huy theo yeu cau"

    def test_cancel_cleared_fails(self, uc):
        created = uc.create_cheque("SEC-031", 1, "Payee", Decimal("1000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "NCC", Decimal("1000000"), 1)
        uc.clear_cheque(c_id, date(2026, 7, 15))
        result = uc.cancel_cheque(c_id, "Huy")
        assert result.is_failure()

    def test_stop_cheque(self, uc):
        created = uc.create_cheque("SEC-040", 1, "Payee", Decimal("10000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "NCC", Decimal("10000000"), 1)
        result = uc.stop_cheque(c_id, "Mat sec")
        assert result.is_success()
        assert result.get_data().status == ChequeStatus.STOPPED

    def test_bounce_cheque(self, uc):
        created = uc.create_cheque("SEC-050", 1, "Payee", Decimal("10000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "NCC", Decimal("10000000"), 1)
        result = uc.bounce_cheque(c_id, "Khong du tien")
        assert result.is_success()
        assert result.get_data().status == ChequeStatus.BOUNCED

    def test_get_stale_cheques(self, uc):
        from datetime import timedelta
        old_date = date.today() - timedelta(days=200)
        created = uc.create_cheque("SEC-060", 1, "Payee", Decimal("10000000"), 1)
        c_id = created.get_data().id
        uc.issue_cheque(c_id, "Old Payee", Decimal("10000000"), 1)
        result = uc.get_stale_cheques(days=180)
        assert result.is_success()
        data = result.get_data()
        assert "stale_cheques" in data

    def test_list_cheques(self, uc):
        uc.create_cheque("SEC-070", 1, "Payee A", Decimal("1000000"), 1)
        uc.create_cheque("SEC-071", 1, "Payee B", Decimal("2000000"), 1)
        cheques = uc.repo.list_cheques()
        assert len(cheques) >= 2

    def test_issue_nonexistent_fails(self, uc):
        result = uc.issue_cheque(999, "NCC", Decimal("1000"), 1)
        assert result.is_failure()

    def test_clear_nonexistent_fails(self, uc):
        result = uc.clear_cheque(999, date.today())
        assert result.is_failure()

    def test_cancel_nonexistent_fails(self, uc):
        result = uc.cancel_cheque(999, "reason")
        assert result.is_failure()


# ── Bank Balance Tests ──────────────────────────────────────────────

class TestBankBalance:
    def test_get_bank_balance(self, uc):
        uc.create_bank_account("Vietcombank", "HN", "12345", "Co ABC", "1121")
        result = uc.get_bank_balance(ba_id=1)
        assert result.is_success()
        data = result.get_data()
        assert data["bank_account_id"] == 1
        assert "current_balance" in data
        assert "bank_name" in data

    def test_get_bank_balance_nonexistent(self, uc):
        result = uc.get_bank_balance(ba_id=999)
        assert result.is_failure()

    def test_list_reconciliations(self, uc):
        uc.create_reconciliation(1, "2026-06", Decimal("1000"), Decimal("1000"))
        uc.create_reconciliation(1, "2026-07", Decimal("2000"), Decimal("2000"))
        recons = uc.repo.list_reconciliations(bank_account_id=1)
        assert len(recons) >= 2

    def test_suggest_matches(self, uc):
        uc.import_bank_statement(1, date(2026, 6, 30), Decimal("0"), Decimal("5000"), [
            {"transaction_date": "2026-06-15", "amount": "2000", "is_debit": False,
             "reference": "DEP-REF", "description": "Customer payment"},
        ])
        result = uc.suggest_matches(bank_account_id=1, period="2026-06")
        assert result.is_success()
        data = result.get_data()
        assert "suggestions" in data
        assert "unmatched_bank_transactions" in data


# ── Bank Book Report Tests ──────────────────────────────────────────

class TestBankBookReport:
    def test_generate_bank_book_report(self, uc):
        uc.create_bank_account("Vietcombank", "HN", "12345", "Co ABC", "1121")
        result = uc.generate_bank_book_report(
            bank_account_id=1,
            from_date=date(2026, 1, 1),
            to_date=date(2026, 12, 31),
        )
        assert result.is_success()
        data = result.get_data()
        assert data["bank_account_id"] == 1
        assert "rows" in data
        assert "opening_balance" in data

    def test_bank_book_report_nonexistent(self, uc):
        result = uc.generate_bank_book_report(999, date(2026, 1, 1), date(2026, 12, 31))
        assert result.is_failure()


# ── Reconciliation Report Tests ────────────────────────────────────

class TestReconciliationReport:
    def test_generate_reconciliation_report(self, uc):
        created = uc.create_reconciliation(1, "2026-06", Decimal("100000000"), Decimal("100000000"))
        r_id = created.get_data().id
        result = uc.generate_reconciliation_report(r_id)
        assert result.is_success()
        data = result.get_data()["data"]
        assert data["is_balanced"] is True
        assert data["period"] == "2026-06"

    def test_reconciliation_report_not_found(self, uc):
        result = uc.generate_reconciliation_report(999)
        assert result.is_failure()


# ── Flask Route Tests ────────────────────────────────────────────────


@pytest.fixture(scope="function")
def cash_client():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.db_manager = FakeDBManager(engine)
    app.register_blueprint(cash_bp, url_prefix="/api/v1/cash")
    return app.test_client()


class TestBankStatementRoutes:
    def test_import_statement(self, cash_client):
        resp = cash_client.post("/api/v1/cash/statements", json={
            "bank_account_id": 1,
            "statement_date": "2026-06-30",
            "opening_balance": "100000000",
            "closing_balance": "105000000",
            "transactions": [
                {"transaction_date": "2026-06-01", "amount": "2000000", "is_debit": False,
                 "reference": "DEP-001", "description": "Deposit"},
                {"transaction_date": "2026-06-15", "amount": "1000000", "is_debit": True,
                 "reference": "WTH-001", "description": "Withdrawal"},
                {"transaction_date": "2026-06-20", "amount": "4000000", "is_debit": False,
                 "reference": "DEP-002", "description": "Transfer in"},
            ],
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["statement_date"] == "2026-06-30"
        assert len(data["transactions"]) == 3

    def test_list_statements(self, cash_client):
        cash_client.post("/api/v1/cash/statements", json={
            "bank_account_id": 1, "statement_date": "2026-06-30",
            "opening_balance": "0", "closing_balance": "5000",
            "transactions": [
                {"transaction_date": "2026-06-01", "amount": "5000", "is_debit": False,
                 "reference": "R1", "description": "Dep"},
            ],
        })
        resp = cash_client.get("/api/v1/cash/statements")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] >= 1

    def test_get_statement(self, cash_client):
        created = cash_client.post("/api/v1/cash/statements", json={
            "bank_account_id": 1, "statement_date": "2026-06-30",
            "opening_balance": "0", "closing_balance": "2000",
            "transactions": [
                {"transaction_date": "2026-06-01", "amount": "2000", "is_debit": False,
                 "reference": "R1", "description": "Dep"},
            ],
        })
        stmt_id = created.get_json()["id"]
        resp = cash_client.get(f"/api/v1/cash/statements/{stmt_id}")
        assert resp.status_code == 200

    def test_import_statement_bad_request(self, cash_client):
        resp = cash_client.post("/api/v1/cash/statements", json={})
        assert resp.status_code == 400


class TestChequeRouteLifecycle:
    def test_create_and_issue(self, cash_client):
        created = cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-100", "cheque_book_id": 1, "payee": "NCC",
            "amount": "10000000", "bank_account_id": 1,
        })
        assert created.status_code == 201
        c_id = created.get_json()["id"]

        issued = cash_client.post(f"/api/v1/cash/cheques/{c_id}/issue", json={
            "payee": "NCC XYZ", "amount": "10000000", "bank_account_id": 1,
        })
        assert issued.status_code == 200
        assert issued.get_json()["status"] == "issued"

        cleared = cash_client.post(f"/api/v1/cash/cheques/{c_id}/clear", json={
            "cleared_date": "2026-07-15",
        })
        assert cleared.status_code == 200
        assert cleared.get_json()["status"] == "cleared"

    def test_cancel(self, cash_client):
        created = cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-200", "cheque_book_id": 1, "payee": "NCC",
            "amount": "5000000", "bank_account_id": 1,
        })
        c_id = created.get_json()["id"]
        resp = cash_client.post(f"/api/v1/cash/cheques/{c_id}/cancel", json={"reason": "Wrong payee"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "cancelled"

    def test_stop(self, cash_client):
        created = cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-300", "cheque_book_id": 1, "payee": "NCC",
            "amount": "5000000", "bank_account_id": 1,
        })
        c_id = created.get_json()["id"]
        cash_client.post(f"/api/v1/cash/cheques/{c_id}/issue", json={
            "payee": "NCC", "amount": "5000000", "bank_account_id": 1,
        })
        resp = cash_client.post(f"/api/v1/cash/cheques/{c_id}/stop", json={"reason": "Lost cheque"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "stopped"

    def test_bounce(self, cash_client):
        created = cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-400", "cheque_book_id": 1, "payee": "NCC",
            "amount": "5000000", "bank_account_id": 1,
        })
        c_id = created.get_json()["id"]
        cash_client.post(f"/api/v1/cash/cheques/{c_id}/issue", json={
            "payee": "NCC", "amount": "5000000", "bank_account_id": 1,
        })
        resp = cash_client.post(f"/api/v1/cash/cheques/{c_id}/bounce", json={"reason": "Insufficient funds"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "bounced"

    def test_list_cheques(self, cash_client):
        cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-500", "cheque_book_id": 1, "payee": "A",
            "amount": "1000000", "bank_account_id": 1,
        })
        cash_client.post("/api/v1/cash/cheques", json={
            "cheque_number": "SEC-501", "cheque_book_id": 1, "payee": "B",
            "amount": "2000000", "bank_account_id": 1,
        })
        resp = cash_client.get("/api/v1/cash/cheques")
        assert resp.status_code == 200
        assert resp.get_json()["total"] >= 2

    def test_stale(self, cash_client):
        resp = cash_client.get("/api/v1/cash/cheques/stale?days=180")
        assert resp.status_code == 200
        assert "stale_cheques" in resp.get_json()


class TestBankBalanceRoute:
    def test_get_balance(self, cash_client):
        cash_client.post("/api/v1/cash/bank-accounts", json={
            "bank_name": "VCB", "branch": "HN", "account_number": "123",
            "account_holder": "Co ABC", "coa_code": "1121",
        })
        resp = cash_client.get("/api/v1/cash/bank-accounts/1/balance")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["bank_account_id"] == 1

    def test_get_balance_not_found(self, cash_client):
        resp = cash_client.get("/api/v1/cash/bank-accounts/999/balance")
        assert resp.status_code == 404


class TestReconciliationRoutes:
    def test_list_reconciliations(self, cash_client):
        cash_client.post("/api/v1/cash/reconciliations", json={
            "bank_account_id": 1, "period": "2026-06",
            "book_balance": "100000000", "bank_balance": "100000000",
        })
        cash_client.post("/api/v1/cash/reconciliations", json={
            "bank_account_id": 1, "period": "2026-07",
            "book_balance": "200000000", "bank_balance": "200000000",
        })
        resp = cash_client.get("/api/v1/cash/reconciliations")
        assert resp.status_code == 200
        assert resp.get_json()["total"] >= 2

    def test_suggest_matches(self, cash_client):
        cash_client.post("/api/v1/cash/statements", json={
            "bank_account_id": 1, "statement_date": "2026-06-30",
            "opening_balance": "0", "closing_balance": "5000",
            "transactions": [
                {"transaction_date": "2026-06-15", "amount": "2000", "is_debit": False,
                 "reference": "DEP-REF", "description": "Payment"},
            ],
        })
        resp = cash_client.post("/api/v1/cash/reconciliations/suggest-matches", json={
            "bank_account_id": 1, "period": "2026-06",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "suggestions" in data

    def test_reconciliation_report(self, cash_client):
        created = cash_client.post("/api/v1/cash/reconciliations", json={
            "bank_account_id": 1, "period": "2026-06",
            "book_balance": "100000000", "bank_balance": "100000000",
        })
        r_id = created.get_json()["id"]
        resp = cash_client.get(f"/api/v1/cash/reconciliations/{r_id}/report")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["is_balanced"] is True

    def test_reconciliation_report_not_found(self, cash_client):
        resp = cash_client.get("/api/v1/cash/reconciliations/999/report")
        assert resp.status_code == 404


class TestBankBookReportRoute:
    def test_bank_book_report(self, cash_client):
        cash_client.post("/api/v1/cash/bank-accounts", json={
            "bank_name": "VCB", "branch": "HN", "account_number": "123",
            "account_holder": "Co ABC", "coa_code": "1121",
        })
        resp = cash_client.get("/api/v1/cash/reports/bank-book?bank_account_id=1&from_date=2026-01-01&to_date=2026-12-31")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["bank_account_id"] == 1
        assert "rows" in data

    def test_bank_book_report_missing_params(self, cash_client):
        resp = cash_client.get("/api/v1/cash/reports/bank-book")
        assert resp.status_code == 400
