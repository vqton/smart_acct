from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from domain import (
    JournalEntry, JournalLine, JournalType, JournalTypeSequence,
    SubsidiaryType, SubsidiaryLedger, CorrectionMethod,
    Result, ValidationError, DoubleEntryError,
    JOURNAL_TYPE_PREFIX_MAP, JOURNAL_PREFIX_TYPE_MAP,
)
from use_cases.gl.templates import (
    generate_journal_template, generate_s01_ledger, generate_subsidiary_template,
    JOURNAL_TYPE_TEMPLATE_MAP, TEMPLATE_NAMES, TEMPLATE_NAMES_EN,
)
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime, AccountStatus
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel, AccountingPeriodModel, JournalTypeSequenceModel
from infrastructure.repositories.gl_repository import GLRepository
from use_cases.gl import GLUseCases


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    _seed_accounts(sess)
    sess.commit()
    yield sess
    sess.close()


def _seed_accounts(sess):
    accounts = [
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Cash"),
        COAModel(code="1121", name="Tiền gửi ngân hàng", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Bank deposit"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Sales revenue"),
        COAModel(code="3331", name="Thuế GTGT phải nộp", account_type="liability",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="VAT payable"),
        COAModel(code="6411", name="Chi phí bán hàng", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Selling expenses"),
        COAModel(code="4111", name="Vốn đầu tư", account_type="equity",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Owner equity"),
        COAModel(code="9111", name="Xác định kết quả kinh doanh", account_type="intermediate",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="P/L summary"),
        COAModel(code="4211", name="Lợi nhuận sau thuế chưa phân phối", account_type="equity",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Retained earnings"),
        COAModel(code="1311", name="Phải thu khách hàng", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="AR - Customers"),
        COAModel(code="3311", name="Phải trả người bán", account_type="liability",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="AP - Suppliers"),
        COAModel(code="1521", name="Nguyên vật liệu chính", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND", description="Raw materials"),
    ]
    for acc in accounts:
        sess.add(acc)


class TestGLRepository:
    def test_create_entry(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000001",
            transaction_date=date(2024, 1, 15),
            description="Test journal entry",
            period="2024-01",
        )
        line1 = JournalLine(
            journal_entry_id=0, account_id="1111",
            debit=Decimal("1000.00"), credit=Decimal("0.00"),
            description="Cash payment", period="2024-01",
        )
        line2 = JournalLine(
            journal_entry_id=0, account_id="5111",
            debit=Decimal("0.00"), credit=Decimal("1000.00"),
            description="Revenue recognition", period="2024-01",
        )
        entry.lines = [line1, line2]

        result = repo.create_entry(entry)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.journal_number == "JV000001"
        assert len(created.lines) == 2

    def test_create_duplicate_entry_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000002",
            transaction_date=date(2024, 1, 15),
            description="First entry",
            period="2024-01",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("500.00"), credit=Decimal("0.00"), period="2024-01"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("500.00"), period="2024-01"),
            ],
        )
        repo.create_entry(entry)
        dup = JournalEntry(
            journal_number="JV000002",
            transaction_date=date(2024, 1, 16),
            description="Duplicate",
            period="2024-01",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100.00"), credit=Decimal("0.00"), period="2024-01"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("100.00"), period="2024-01"),
            ],
        )
        result = repo.create_entry(dup)
        assert result.is_failure()

    def test_get_entry(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000003",
            transaction_date=date(2024, 2, 1),
            description="Get test",
            period="2024-02",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1121",
                            debit=Decimal("2000.00"), credit=Decimal("0.00"), period="2024-02"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("2000.00"), period="2024-02"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        fetched = repo.get_entry(created.id)
        assert fetched is not None
        assert fetched.journal_number == "JV000003"
        assert len(fetched.lines) == 2

    def test_get_entry_not_found(self, session):
        repo = GLRepository(session)
        assert repo.get_entry(99999) is None

    def test_delete_unposted_entry(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000004",
            transaction_date=date(2024, 3, 1),
            description="Delete me",
            period="2024-03",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("300.00"), credit=Decimal("0.00"), period="2024-03"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("300.00"), period="2024-03"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        del_result = repo.delete_entry(created.id)
        assert del_result.is_success()
        assert repo.get_entry(created.id) is None

    def test_delete_posted_entry_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000005",
            transaction_date=date(2024, 3, 1),
            description="Posted entry",
            period="2024-03",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("300.00"), credit=Decimal("0.00"), period="2024-03"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("300.00"), period="2024-03"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()
        repo.post_entry(created.id)

        del_result = repo.delete_entry(created.id)
        assert del_result.is_failure()


class TestGLPosting:
    def test_post_entry_balances(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000010",
            transaction_date=date(2024, 4, 1),
            description="Balanced entry",
            period="2024-04",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("1000.00"), credit=Decimal("0.00"), period="2024-04"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("1000.00"), period="2024-04"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        post_result = repo.post_entry(created.id)
        error_msg = str(post_result.error) if post_result.is_failure() else ""
        assert post_result.is_success(), f"Post failed: {error_msg}"
        posted = post_result.get_data()
        assert posted.is_posted is True
        assert posted.posted_date is not None

    def test_post_unbalanced_entry_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000011",
            transaction_date=date(2024, 4, 1),
            description="Unbalanced entry",
            period="2024-04",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("1000.00"), credit=Decimal("0.00"), period="2024-04"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("900.00"), period="2024-04"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        post_result = repo.post_entry(created.id)
        assert post_result.is_failure()
        assert "DOUBLE_ENTRY_DEBIT_CREDIT" in str(post_result.error)

    def test_double_post_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000012",
            transaction_date=date(2024, 4, 1),
            description="Double post",
            period="2024-04",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("500.00"), credit=Decimal("0.00"), period="2024-04"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("500.00"), period="2024-04"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        repo.post_entry(created.id)
        post_result = repo.post_entry(created.id)
        assert post_result.is_failure()

    def test_post_with_invalid_account_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000013",
            transaction_date=date(2024, 4, 1),
            description="Invalid account",
            period="2024-04",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("500.00"), credit=Decimal("0.00"), period="2024-04"),
                JournalLine(journal_entry_id=0, account_id="NONEXIST",
                            debit=Decimal("0.00"), credit=Decimal("500.00"), period="2024-04"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        post_result = repo.post_entry(created.id)
        assert post_result.is_failure()


class TestGLUseCases:
    def test_create_entry_use_case(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV000020",
            transaction_date=date(2024, 5, 1),
            description="Via use case",
            lines=[
                {"account_id": "1111", "debit": "1500.00", "credit": "0.00"},
                {"account_id": "5111", "debit": "0.00", "credit": "1500.00"},
            ],
            period="2024-05",
            created_by="test_user",
        )
        assert result.is_success()
        entry = result.get_data()
        assert entry.journal_number == "JV000020"
        assert entry.created_by == "test_user"
        assert len(entry.lines) == 2

    def test_create_unbalanced_use_case_fails(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV000021",
            transaction_date=date(2024, 5, 1),
            description="Unbalanced via use case",
            lines=[
                {"account_id": "1111", "debit": "1000.00", "credit": "0.00"},
                {"account_id": "5111", "debit": "0.00", "credit": "900.00"},
            ],
            period="2024-05",
        )
        assert result.is_failure()

    def test_list_entries(self, session):
        uc = GLUseCases(session)
        uc.create_entry(
            journal_number="JV000030",
            transaction_date=date(2024, 6, 1),
            description="Entry A",
            lines=[{"account_id": "1111", "debit": "100.00", "credit": "0.00"},
                   {"account_id": "5111", "debit": "0.00", "credit": "100.00"}],
            period="2024-06",
        )
        uc.create_entry(
            journal_number="JV000031",
            transaction_date=date(2024, 6, 15),
            description="Entry B",
            lines=[{"account_id": "1121", "debit": "200.00", "credit": "0.00"},
                   {"account_id": "5111", "debit": "0.00", "credit": "200.00"}],
            period="2024-06",
        )

        entries = uc.list_entries(period="2024-06")
        assert len(entries) == 2

    def test_full_lifecycle(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV000040",
            transaction_date=date(2024, 7, 1),
            description="Full lifecycle test",
            lines=[
                {"account_id": "1111", "debit": "5000.00", "credit": "0.00", "description": "Cash out"},
                {"account_id": "5111", "debit": "0.00", "credit": "5000.00", "description": "Revenue"},
            ],
            period="2024-07",
            created_by="tester",
        )
        assert result.is_success()
        entry_id = result.get_data().id

        fetched = uc.get_entry(entry_id)
        assert fetched.is_success()
        assert fetched.get_data().description == "Full lifecycle test"

        post_result = uc.post_entry(entry_id)
        assert post_result.is_success()
        assert post_result.get_data().is_posted

        posted = uc.get_entry(entry_id)
        assert posted.is_success()
        assert posted.get_data().is_posted

    def test_update_unposted_entry(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000050",
            transaction_date=date(2024, 8, 1),
            description="Original description",
            period="2024-08",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100.00"), credit=Decimal("0.00"), period="2024-08"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("100.00"), period="2024-08"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()

        update_result = repo.update_entry(created.id, description="Updated description")
        assert update_result.is_success()
        assert update_result.get_data().description == "Updated description"

    def test_update_posted_entry_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000051",
            transaction_date=date(2024, 8, 1),
            description="Posted entry",
            period="2024-08",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100.00"), credit=Decimal("0.00"), period="2024-08"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("100.00"), period="2024-08"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()
        repo.post_entry(created.id)

        update_result = repo.update_entry(created.id, description="Should fail")
        assert update_result.is_failure()


class TestGLBalances:
    def test_get_account_balance(self, session):
        repo = GLRepository(session)
        entry1 = JournalEntry(
            journal_number="JV000060",
            transaction_date=date(2024, 9, 1),
            description="Sale 1",
            period="2024-09",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("1000.00"), credit=Decimal("0.00"), period="2024-09"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("1000.00"), period="2024-09"),
            ],
        )
        result1 = repo.create_entry(entry1)
        repo.post_entry(result1.get_data().id)

        entry2 = JournalEntry(
            journal_number="JV000061",
            transaction_date=date(2024, 9, 15),
            description="Sale 2",
            period="2024-09",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("500.00"), credit=Decimal("0.00"), period="2024-09"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0.00"), credit=Decimal("500.00"), period="2024-09"),
            ],
        )
        result2 = repo.create_entry(entry2)
        repo.post_entry(result2.get_data().id)

        balance = repo.get_account_balance("1111", "2024-09")
        assert balance["total_debit"] == Decimal("1500")
        assert balance["total_credit"] == Decimal("0")
        assert balance["balance"] == Decimal("1500")

        rev_balance = repo.get_account_balance("5111", "2024-09")
        assert rev_balance["total_debit"] == Decimal("0")
        assert rev_balance["total_credit"] == Decimal("1500")
        assert rev_balance["balance"] == Decimal("1500")


class TestPeriodClose:
    def test_close_period(self, session):
        repo = GLRepository(session)
        result = repo.close_period("2024-10", closed_by="admin", notes="Month-end close")
        assert result.is_success()
        p = result.get_data()
        assert p["period"] == "2024-10"
        assert p["is_closed"] is True
        assert p["closed_by"] == "admin"

    def test_close_twice_fails(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-10", closed_by="admin")
        result = repo.close_period("2024-10", closed_by="admin")
        assert result.is_failure()

    def test_reopen_period(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-11", closed_by="admin")
        result = repo.reopen_period("2024-11", reason="Error correction")
        assert result.is_success()
        p = result.get_data()
        assert p["is_closed"] is False

    def test_reopen_not_closed_fails(self, session):
        repo = GLRepository(session)
        result = repo.reopen_period("2024-12", reason="Test")
        assert result.is_failure()

    def test_reopen_without_reason_fails(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-09", closed_by="admin")
        result = repo.reopen_period("2024-09", reopened_by="admin")
        assert result.is_failure()
        assert "reason" in str(result.error).lower()

    def test_reopen_flags_downstream_periods(self, session):
        repo = GLRepository(session)
        p1 = repo._auto_create_period("2024-01")
        p1.start_date = date(2024, 1, 1)
        p1.end_date = date(2024, 1, 31)
        p2 = repo._auto_create_period("2024-02")
        p2.start_date = date(2024, 2, 1)
        p2.end_date = date(2024, 2, 28)
        p3 = repo._auto_create_period("2024-03")
        p3.start_date = date(2024, 3, 1)
        p3.end_date = date(2024, 3, 31)
        session.flush()
        repo.close_period("2024-01", closed_by="admin")
        repo.reopen_period("2024-01", reason="Correction")
        assert session.get(AccountingPeriodModel, p2.id).needs_reconciliation is True
        assert session.get(AccountingPeriodModel, p3.id).needs_reconciliation is True

    def test_is_period_closed(self, session):
        repo = GLRepository(session)
        assert repo.is_period_closed("2024-13") is False
        repo.close_period("2024-13", closed_by="admin")
        assert repo.is_period_closed("2024-13") is True

    def test_list_periods(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-01", closed_by="admin")
        repo.close_period("2024-02", closed_by="admin")
        periods = repo.list_periods()
        assert len(periods) == 2

    def test_list_periods_status_filter_open(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-01", closed_by="admin")
        repo.close_period("2024-02", closed_by="admin")
        open_periods = repo.list_periods(status="open")
        assert all(p["is_closed"] is False for p in open_periods)

    def test_list_periods_status_filter_closed(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-01", closed_by="admin")
        repo.close_period("2024-02", closed_by="admin")
        closed_periods = repo.list_periods(status="closed")
        assert all(p["is_closed"] for p in closed_periods)
        assert len(closed_periods) == 2

    def test_list_periods_has_entries_flag(self, session):
        repo = GLRepository(session)
        p_no_entries = repo._auto_create_period("2025-12")
        session.flush()
        result_no = repo.get_period("2025-12")
        assert result_no["has_entries"] is False
        entry = JournalEntry(
            journal_number="JV099999",
            transaction_date=date(2025, 12, 1),
            description="Has entries test",
            period="2025-12",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111", debit=1000, credit=0),
                JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=1000),
            ],
        )
        repo.create_entry(entry)
        result_yes = repo.get_period("2025-12")
        assert result_yes["has_entries"] is True

    def test_create_period_overlap_fails(self, session):
        repo = GLRepository(session)
        result1 = repo.create_period(
            "2025-06", type_="monthly",
            start_date=date(2025, 6, 1), end_date=date(2025, 6, 30),
        )
        assert result1.is_success()
        result2 = repo.create_period(
            "2025-06-alt", type_="monthly",
            start_date=date(2025, 6, 15), end_date=date(2025, 7, 15),
        )
        assert result2.is_failure()
        assert "overlap" in str(result2.error).lower()
        result3 = repo.create_period(
            "2025-07", type_="monthly",
            start_date=date(2025, 7, 1), end_date=date(2025, 7, 31),
        )
        assert result3.is_success()

    def test_close_fails_if_unposted_entries(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000080",
            transaction_date=date(2024, 1, 1),
            description="Unposted",
            period="2024-01",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100"), credit=Decimal("0"), period="2024-01"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("100"), period="2024-01"),
            ],
        )
        repo.create_entry(entry)
        result = repo.close_period("2024-01", closed_by="admin")
        assert result.is_failure()
        assert "unposted" in str(result.error)

    def test_close_fails_if_unbalanced_entries(self, session):
        from infrastructure.models.gl_models import JournalLineModel
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000081",
            transaction_date=date(2024, 3, 1),
            description="Will be unbalanced",
            period="2024-03",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100"), credit=Decimal("0"), period="2024-03"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("100"), period="2024-03"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()
        repo.post_entry(created.id)
        line = session.execute(
            select(JournalLineModel).where(JournalLineModel.journal_entry_id == created.id)
        ).scalars().first()
        line.credit = Decimal("90")
        session.flush()
        result = repo.close_period("2024-03", closed_by="admin")
        assert result.is_failure()
        assert "unbalanced" in str(result.error)

    def test_force_close_skips_validation(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000082",
            transaction_date=date(2024, 4, 1),
            description="Unposted but forced",
            period="2024-04",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100"), credit=Decimal("0"), period="2024-04"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("100"), period="2024-04"),
            ],
        )
        repo.create_entry(entry)
        result = repo.close_period("2024-04", closed_by="admin", force=True)
        assert result.is_success()
        assert result.get_data()["is_closed"] is True

    def test_close_after_posting_all_entries_succeeds(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000083",
            transaction_date=date(2024, 5, 1),
            description="Will be posted",
            period="2024-05",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("200"), credit=Decimal("0"), period="2024-05"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("200"), period="2024-05"),
            ],
        )
        result = repo.create_entry(entry)
        repo.post_entry(result.get_data().id)
        result = repo.close_period("2024-05", closed_by="admin")
        assert result.is_success()
        assert result.get_data()["is_closed"] is True

    def test_create_entry_in_closed_period_fails(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-06", closed_by="admin")
        entry = JournalEntry(
            journal_number="JV000070",
            transaction_date=date(2024, 6, 1),
            description="Should fail",
            period="2024-06",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100"), credit=Decimal("0"), period="2024-06"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("100"), period="2024-06"),
            ],
        )
        result = repo.create_entry(entry)
        assert result.is_failure()
        assert result.error.msgid == ErrorCodes.PERIOD_CLOSED_OP

    def test_post_entry_in_closed_period_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000071",
            transaction_date=date(2024, 7, 1),
            description="Will be blocked",
            period="2024-07",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("200"), credit=Decimal("0"), period="2024-07"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("200"), period="2024-07"),
            ],
        )
        result = repo.create_entry(entry)
        assert result.is_success()
        entry_id = result.get_data().id
        repo.close_period("2024-07", closed_by="admin", force=True)
        post_result = repo.post_entry(entry_id)
        assert post_result.is_failure()
        assert post_result.error.msgid == ErrorCodes.PERIOD_CLOSED_OP

    def test_update_entry_in_closed_period_fails(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000072",
            transaction_date=date(2024, 8, 1),
            description="Will be blocked",
            period="2024-08",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("300"), credit=Decimal("0"), period="2024-08"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("300"), period="2024-08"),
            ],
        )
        result = repo.create_entry(entry)
        assert result.is_success()
        entry_id = result.get_data().id
        repo.close_period("2024-08", closed_by="admin", force=True)
        update_result = repo.update_entry(entry_id, description="Should fail")
        assert update_result.is_failure()
        assert update_result.error.msgid == ErrorCodes.PERIOD_CLOSED_OP


class TestPeriodAuditLog:
    def test_close_creates_audit_log(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-09", closed_by="admin", notes="Month-end")
        logs = repo.get_period_audit_log("2024-09")
        assert len(logs) == 2  # CREATE + CLOSE
        assert logs[0]["event_type"] == "PERIOD_CREATE"
        assert logs[1]["event_type"] == "PERIOD_CLOSE"
        assert logs[1]["user"] == "admin"

    def test_reopen_creates_audit_log(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-10", closed_by="admin")
        repo.reopen_period("2024-10", reopened_by="chief", reason="Error discovered")
        logs = repo.get_period_audit_log("2024-10")
        events = [l["event_type"] for l in logs]
        assert events == ["PERIOD_CREATE", "PERIOD_CLOSE", "PERIOD_REOPEN"]

    def test_create_period_audit_log(self, session):
        repo = GLRepository(session)
        repo.create_period("2025-01", "monthly")
        logs = repo.get_period_audit_log("2025-01")
        assert len(logs) == 1
        assert logs[0]["event_type"] == "PERIOD_CREATE"

    def test_audit_log_empty_for_new_period(self, session):
        repo = GLRepository(session)
        logs = repo.get_period_audit_log("2099-01")
        assert logs == []

    def test_audit_log_multiple_events(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-11", closed_by="admin")
        repo.reopen_period("2024-11", reopened_by="admin", reason="Correction")
        repo.close_period("2024-11", closed_by="admin", notes="Re-closed")
        logs = repo.get_period_audit_log("2024-11")
        assert len(logs) == 4  # CREATE + CLOSE + REOPEN + CLOSE


class TestFinancialStatements:
    def _seed_gl_data(self, repo):
        e1 = repo.create_entry(JournalEntry(
            journal_number="JV000100", transaction_date=date(2024, 12, 1),
            description="Revenue", period="2024-12",
            lines=[JournalLine(journal_entry_id=0, account_id="1111",
                               debit=Decimal("10000"), credit=Decimal("0"), period="2024-12"),
                   JournalLine(journal_entry_id=0, account_id="5111",
                               debit=Decimal("0"), credit=Decimal("10000"), period="2024-12")],
        ))
        repo.post_entry(e1.get_data().id)

        e2 = repo.create_entry(JournalEntry(
            journal_number="JV000101", transaction_date=date(2024, 12, 15),
            description="Expense", period="2024-12",
            lines=[JournalLine(journal_entry_id=0, account_id="6411",
                               debit=Decimal("3000"), credit=Decimal("0"), period="2024-12"),
                   JournalLine(journal_entry_id=0, account_id="1111",
                               debit=Decimal("0"), credit=Decimal("3000"), period="2024-12")],
        ))
        repo.post_entry(e2.get_data().id)

        e3 = repo.create_entry(JournalEntry(
            journal_number="JV000102", transaction_date=date(2024, 12, 20),
            description="Owner investment", period="2024-12",
            lines=[JournalLine(journal_entry_id=0, account_id="1111",
                               debit=Decimal("50000"), credit=Decimal("0"), period="2024-12"),
                   JournalLine(journal_entry_id=0, account_id="4111",
                               debit=Decimal("0"), credit=Decimal("50000"), period="2024-12")],
        ))
        repo.post_entry(e3.get_data().id)

    def test_balance_sheet(self, session):
        repo = GLRepository(session)
        self._seed_gl_data(repo)
        bs = repo.generate_balance_sheet("2024-12")
        assert bs["statement_type"] == "balance_sheet"
        assert Decimal(bs["total_assets"]) == Decimal("57000")
        assert Decimal(bs["total_equity"]) == Decimal("50000")

    def test_income_statement(self, session):
        repo = GLRepository(session)
        self._seed_gl_data(repo)
        is_ = repo.generate_income_statement("2024-12")
        assert is_["statement_type"] == "income_statement"
        assert Decimal(is_["total_revenue"]) == Decimal("10000")
        assert Decimal(is_["total_expenses"]) == Decimal("3000")
        assert Decimal(is_["net_income"]) == Decimal("7000")

    def test_carry_forward_success(self, session):
        repo = GLRepository(session)
        repo._auto_create_period("2024-12")
        session.flush()
        self._seed_gl_data(repo)
        result = repo.carry_forward("2024-12", closed_by="admin")
        assert result.is_success()
        data = result.get_data()
        assert data["closed"] is True
        assert Decimal(data["total_revenue"]) == Decimal("10000")
        assert Decimal(data["total_expenses"]) == Decimal("3000")
        assert Decimal(data["net_income"]) == Decimal("7000")
        assert data["next_period"] == "2025-01"
        assert repo.is_period_closed("2024-12") is True
        next_p = repo.get_period("2025-01")
        assert next_p is not None
        assert next_p["is_closed"] is False

    def test_carry_forward_non_december_fails(self, session):
        repo = GLRepository(session)
        p = repo._auto_create_period("2024-06")
        session.flush()
        result = repo.carry_forward("2024-06")
        assert result.is_failure()
        assert "December" in str(result.error) or "year-end" in str(result.error).lower()

    def test_carry_forward_already_closed_fails(self, session):
        repo = GLRepository(session)
        repo.close_period("2024-12", closed_by="admin")
        result = repo.carry_forward("2024-12")
        assert result.is_failure()

    def test_carry_forward_creates_closing_entry(self, session):
        repo = GLRepository(session)
        repo._auto_create_period("2024-12")
        session.flush()
        self._seed_gl_data(repo)
        result = repo.carry_forward("2024-12", closed_by="admin")
        assert result.is_success()
        entries = repo.list_entries(period="2024-12")
        closing_entries = [e for e in entries if e.journal_number == "JV20249999"]
        assert len(closing_entries) == 1
        assert closing_entries[0].is_posted is True


class TestJournalType:
    def test_default_journal_type(self):
        entry = JournalEntry(
            journal_number="JV000200", transaction_date=date(2024, 1, 1),
            description="Default type", period="2024-01",
            lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                   JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
        )
        assert entry.journal_type == JournalType.GENERAL

    def test_explicit_journal_type(self):
        entry = JournalEntry(
            journal_number="SJ202400001", journal_type=JournalType.SALES,
            transaction_date=date(2024, 1, 1), description="Sales journal", period="2024-01",
            lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                   JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
        )
        assert entry.journal_type == JournalType.SALES
        assert entry.journal_number.startswith("SJ")

    def test_prefix_mismatch_raises_error(self):
        with pytest.raises(ValidationError):
            JournalEntry(
                journal_number="SJ202400001", journal_type=JournalType.GENERAL,
                transaction_date=date(2024, 1, 1), description="Mismatch", period="2024-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
            )

    def test_invalid_prefix_raises_error(self):
        with pytest.raises(ValidationError):
            JournalEntry(
                journal_number="XX202400001",
                transaction_date=date(2024, 1, 1), description="Invalid prefix", period="2024-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
            )

    def test_empty_journal_number_raises_error(self):
        with pytest.raises(Exception):
            JournalEntry(
                journal_number="",
                transaction_date=date(2024, 1, 1), description="Empty", period="2024-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
            )

    def test_all_journal_type_prefixes(self):
        for jt in JournalType:
            prefix = JOURNAL_TYPE_PREFIX_MAP[jt]
            number = f"{prefix}2026000001"
            entry = JournalEntry(
                journal_number=number, journal_type=jt,
                transaction_date=date(2024, 1, 1), description=f"Test {jt.value}", period="2024-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
            )
            assert entry.journal_number == number
            assert entry.journal_type == jt

    def test_enum_values(self):
        assert JournalType.GENERAL.value == "general"
        assert JournalType.SALES.value == "sales"
        assert JournalType.PURCHASE.value == "purchase"
        assert JournalType.CASH_RECEIPT.value == "cash_receipt"
        assert JournalType.CASH_PAYMENT.value == "cash_payment"
        assert JournalType.CLOSING.value == "closing"

    def test_prefix_map_consistency(self):
        assert JOURNAL_TYPE_PREFIX_MAP[JournalType.GENERAL] == "JV"
        assert JOURNAL_TYPE_PREFIX_MAP[JournalType.SALES] == "SJ"
        assert JOURNAL_PREFIX_TYPE_MAP["JV"] == JournalType.GENERAL
        assert JOURNAL_PREFIX_TYPE_MAP["SJ"] == JournalType.SALES
        assert JOURNAL_PREFIX_TYPE_MAP["FA"] == JournalType.FIXED_ASSET

    def test_create_entry_with_journal_type(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="SJ202400001", journal_type=JournalType.SALES,
            transaction_date=date(2024, 1, 1), description="Sales entry", period="2024-01",
            lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=500, credit=0, period="2024-01"),
                   JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=500, period="2024-01")],
        )
        result = repo.create_entry(entry)
        assert result.is_success()
        created = result.get_data()
        assert created.journal_type == JournalType.SALES
        assert created.journal_number == "SJ202400001"

    def test_create_entry_with_purchase_type(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="PJ202400001", journal_type=JournalType.PURCHASE,
            transaction_date=date(2024, 2, 1), description="Purchase entry", period="2024-02",
            lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=300, credit=0, period="2024-02"),
                   JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=300, period="2024-02")],
        )
        result = repo.create_entry(entry)
        assert result.is_success()
        created = result.get_data()
        assert created.journal_type == JournalType.PURCHASE
        assert created.journal_number.startswith("PJ")


class TestJournalTypeSequence:
    def test_get_or_create_sequence(self, session):
        repo = GLRepository(session)
        seq = repo.get_or_create_sequence(JournalType.SALES, 2026)
        assert seq.id is not None
        assert seq.journal_type == "sales"
        assert seq.fiscal_year == 2026
        assert seq.last_sequence == 0
        assert seq.prefix == "SJ"

    def test_get_or_create_sequence_reuses_existing(self, session):
        repo = GLRepository(session)
        seq1 = repo.get_or_create_sequence(JournalType.GENERAL, 2026)
        seq1.last_sequence = 5
        session.flush()
        seq2 = repo.get_or_create_sequence(JournalType.GENERAL, 2026)
        assert seq2.id == seq1.id
        assert seq2.last_sequence == 5

    def test_get_next_journal_number(self, session):
        repo = GLRepository(session)
        number = repo.get_next_journal_number(JournalType.SALES, "2026-01")
        assert number == "SJ2026000001"
        number2 = repo.get_next_journal_number(JournalType.SALES, "2026-01")
        assert number2 == "SJ2026000002"

    def test_get_next_journal_number_separate_types(self, session):
        repo = GLRepository(session)
        sales_num = repo.get_next_journal_number(JournalType.SALES, "2026-01")
        assert sales_num == "SJ2026000001"
        purchase_num = repo.get_next_journal_number(JournalType.PURCHASE, "2026-01")
        assert purchase_num == "PJ2026000001"
        assert sales_num != purchase_num

    def test_get_next_journal_number_separate_years(self, session):
        repo = GLRepository(session)
        n1 = repo.get_next_journal_number(JournalType.GENERAL, "2026-01")
        assert n1 == "JV2026000001"
        n2 = repo.get_next_journal_number(JournalType.GENERAL, "2027-01")
        assert n2 == "JV2027000001"

    def test_sequence_resets_per_year(self, session):
        repo = GLRepository(session)
        repo.get_next_journal_number(JournalType.GENERAL, "2026-12")
        repo.get_next_journal_number(JournalType.GENERAL, "2026-12")
        n3 = repo.get_next_journal_number(JournalType.GENERAL, "2027-01")
        assert n3 == "JV2027000001"

    def test_get_journal_sequence(self, session):
        repo = GLRepository(session)
        repo.get_next_journal_number(JournalType.PURCHASE, "2026-01")
        seq = repo.get_journal_sequence(JournalType.PURCHASE, 2026)
        assert seq is not None
        assert seq["journal_type"] == "purchase"
        assert seq["last_sequence"] >= 1

    def test_get_journal_sequence_not_found(self, session):
        repo = GLRepository(session)
        seq = repo.get_journal_sequence(JournalType.CLOSING, 2099)
        assert seq is None

    def test_list_journal_sequences(self, session):
        repo = GLRepository(session)
        repo.get_next_journal_number(JournalType.GENERAL, "2026-01")
        repo.get_next_journal_number(JournalType.SALES, "2026-01")
        seqs = repo.list_journal_sequences(2026)
        assert len(seqs) >= 2

    def test_list_journal_sequences_filtered(self, session):
        repo = GLRepository(session)
        repo.get_next_journal_number(JournalType.GENERAL, "2026-01")
        repo.get_next_journal_number(JournalType.SALES, "2027-01")
        seqs_2026 = repo.list_journal_sequences(2026)
        seqs_2027 = repo.list_journal_sequences(2027)
        all_seqs = repo.list_journal_sequences()
        assert len(seqs_2026) >= 1
        assert len(seqs_2027) >= 1
        assert len(all_seqs) >= len(seqs_2026) + len(seqs_2027)


class TestJournalTypeUseCase:
    def test_create_entry_with_journal_type(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="SJ202400002",
            transaction_date=date(2024, 6, 1),
            description="Sales via use case",
            journal_type="sales",
            lines=[{"account_id": "1111", "debit": "2000.00", "credit": "0.00"},
                   {"account_id": "5111", "debit": "0.00", "credit": "2000.00"}],
            period="2024-06",
        )
        assert result.is_success()
        entry = result.get_data()
        assert entry.journal_type == JournalType.SALES

    def test_create_entry_auto_number(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="",
            transaction_date=date(2026, 3, 15),
            description="Auto-numbered",
            journal_type="sales",
            lines=[{"account_id": "1111", "debit": "1000.00", "credit": "0.00"},
                   {"account_id": "5111", "debit": "0.00", "credit": "1000.00"}],
            period="2026-03",
            auto_number=True,
        )
        assert result.is_success()
        entry = result.get_data()
        assert entry.journal_number.startswith("SJ2026")

    def test_get_next_journal_number_use_case(self, session):
        uc = GLUseCases(session)
        result = uc.get_next_journal_number("purchase", "2026-04")
        assert result.is_success()
        data = result.get_data()
        assert "journal_number" in data
        assert data["journal_number"].startswith("PJ2026")

    def test_get_journal_sequence_use_case(self, session):
        uc = GLUseCases(session)
        uc.get_next_journal_number("sales", "2026-05")
        result = uc.get_journal_sequence("sales", 2026)
        assert result.is_success()
        seq = result.get_data()
        assert seq["journal_type"] == "sales"

    def test_invalid_journal_type_use_case(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="XX000001",
            transaction_date=date(2024, 1, 1),
            description="Invalid type",
            journal_type="invalid_type",
            lines=[{"account_id": "1111", "debit": "100.00", "credit": "0.00"},
                   {"account_id": "5111", "debit": "0.00", "credit": "100.00"}],
        )
        assert result.is_failure()

    def test_approved_by_field(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000300", journal_type=JournalType.GENERAL,
            transaction_date=date(2024, 1, 1), description="Approved entry", period="2024-01",
            approved_by="chief_accountant", is_approved=True,
            lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=100, credit=0, period="2024-01"),
                   JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=100, period="2024-01")],
        )
        result = repo.create_entry(entry)
        assert result.is_success()
        created = result.get_data()
        assert created.approved_by == "chief_accountant"
        assert created.is_approved is True


class TestSubsidiaryLedger:
    def test_subsidiary_type_enum(self):
        assert SubsidiaryType.AR.value == "ar"
        assert SubsidiaryType.AP.value == "ap"
        assert SubsidiaryType.INVENTORY.value == "inv"

    def test_create_subsidiary_entry(self, session):
        repo = GLRepository(session)
        sl = SubsidiaryLedger(
            subsidiary_type=SubsidiaryType.AR,
            account_code="1111",
            entity_id=1,
            entity_name="Customer A",
            transaction_date=date(2024, 1, 15),
            doc_ref="INV-001",
            doc_type="invoice",
            description="Test AR entry",
            debit=Decimal("1000.00"),
            credit=Decimal("0.00"),
            balance=Decimal("1000.00"),
            period="2024-01",
        )
        result = repo.create_subsidiary_entry(sl)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.subsidiary_type == SubsidiaryType.AR
        assert created.entity_name == "Customer A"
        assert created.balance == Decimal("1000.00")

    def test_get_subsidiary_ledger(self, session):
        repo = GLRepository(session)
        sl = SubsidiaryLedger(
            subsidiary_type=SubsidiaryType.AP,
            account_code="1111",
            entity_id=2,
            entity_name="Vendor X",
            transaction_date=date(2024, 2, 1),
            doc_ref="PO-001", doc_type="purchase",
            description="Test AP entry",
            debit=Decimal("0.00"), credit=Decimal("500.00"),
            balance=Decimal("500.00"), period="2024-02",
        )
        repo.create_subsidiary_entry(sl)
        entries = repo.get_subsidiary_ledger("ap")
        assert len(entries) == 1
        assert entries[0].entity_name == "Vendor X"

    def test_get_subsidiary_ledger_filtered(self, session):
        repo = GLRepository(session)
        for i in range(3):
            sl = SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AR,
                account_code="1111",
                entity_id=i + 1,
                entity_name=f"Customer {i + 1}",
                transaction_date=date(2024, 1, 1),
                doc_ref=f"INV-00{i + 1}", doc_type="invoice",
                description=f"Entry {i}",
                debit=Decimal("100"), credit=Decimal("0"),
                balance=Decimal("100"), period="2024-01",
            )
            repo.create_subsidiary_entry(sl)
        entries = repo.get_subsidiary_ledger("ar", entity_id=2)
        assert len(entries) == 1
        assert entries[0].entity_name == "Customer 2"

    def test_get_subsidiary_ledger_by_period(self, session):
        repo = GLRepository(session)
        for p in ["2024-01", "2024-02"]:
            sl = SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AR,
                account_code="1111", entity_id=1,
                entity_name="Customer A",
                transaction_date=date(2024, int(p.split("-")[1]), 1),
                doc_ref=f"INV-{p}", doc_type="invoice",
                description=f"Entry {p}",
                debit=Decimal("100"), credit=Decimal("0"),
                balance=Decimal("100"), period=p,
            )
            repo.create_subsidiary_entry(sl)
        entries = repo.get_subsidiary_ledger("ar", period="2024-02")
        assert len(entries) == 1

    def test_post_to_subsidiary_ledger(self, session):
        repo = GLRepository(session)
        entry = JournalEntry(
            journal_number="JV000400",
            transaction_date=date(2024, 3, 1),
            description="Subsidiary test",
            period="2024-03",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("1000"), credit=Decimal("0"), period="2024-03"),
                JournalLine(journal_entry_id=0, account_id="5111",
                            debit=Decimal("0"), credit=Decimal("1000"), period="2024-03"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()
        repo.post_entry(created.id)

        sl_result = repo.post_to_subsidiary_ledger(
            journal_entry_id=created.id,
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("1000"), credit=Decimal("0"), period="2024-03"),
            ],
            subsidiary_type="ar",
            entity_id=100,
            entity_name="AR Customer",
            doc_ref="SJ202400001",
            doc_type="sales_invoice",
            period="2024-03",
            transaction_date=date(2024, 3, 1),
        )
        assert sl_result.is_success()
        entries = repo.get_subsidiary_ledger("ar", entity_id=100)
        assert len(entries) == 1
        assert entries[0].balance == Decimal("1000")
    def test_subsidiary_running_balance(self, session):
        repo = GLRepository(session)
        for i, (dr, cr, exp_bal) in enumerate([(500, 0, 500), (0, 200, 300), (300, 0, 600)]):
            sl = SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AR,
                account_code="1111", entity_id=1,
                entity_name="Customer A",
                transaction_date=date(2024, 1, i + 1),
                doc_ref=f"TXN-00{i + 1}", doc_type="transaction",
                description=f"Entry {i + 1}",
                debit=Decimal(dr), credit=Decimal(cr),
                balance=Decimal(exp_bal),
                period="2024-01",
            )
            repo.create_subsidiary_entry(sl)

        entries_before = repo.get_subsidiary_ledger("ar", entity_id=1)
        assert entries_before[-1].balance == Decimal("600")

        entry = JournalEntry(
            journal_number="JV000401",
            transaction_date=date(2024, 1, 4),
            description="Subsidiary balance test",
            period="2024-01",
            lines=[
                JournalLine(journal_entry_id=0, account_id="1111",
                            debit=Decimal("100"), credit=Decimal("0"), period="2024-01"),
            ],
        )
        result = repo.create_entry(entry)
        created = result.get_data()
        repo.post_entry(created.id)
        sl_result = repo.post_to_subsidiary_ledger(
            journal_entry_id=created.id,
            lines=[JournalLine(journal_entry_id=0, account_id="1111",
                              debit=Decimal("100"), credit=Decimal("0"), period="2024-01")],
            subsidiary_type="ar",
            entity_id=1,
            entity_name="Customer A",
            doc_ref="INV-004",
            doc_type="invoice",
            period="2024-01",
            transaction_date=date(2024, 1, 4),
        )
        assert sl_result.is_success()
        entries = repo.get_subsidiary_ledger("ar", entity_id=1)
        last_entry = entries[-1]
        assert last_entry.balance == Decimal("700")

    def test_subsidiary_summary(self, session):
        repo = GLRepository(session)
        for i in range(2):
            sl = SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AP,
                account_code="1111", entity_id=5,
                entity_name="Vendor Y",
                transaction_date=date(2024, 4, i + 1),
                doc_ref=f"PO-00{i + 1}", doc_type="purchase",
                description=f"Purchase {i + 1}",
                debit=Decimal("0"), credit=Decimal("100"),
                balance=Decimal("100"), period="2024-04",
            )
            repo.create_subsidiary_entry(sl)
        summary = repo.get_subsidiary_summary("ap", "2024-04")
        assert len(summary) >= 1
        row = [r for r in summary if r["entity_id"] == 5][0]
        assert Decimal(row["total_credit"]) == Decimal("200")

    def test_subsidiary_use_case_lifecycle(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV000500",
            transaction_date=date(2024, 5, 1),
            description="Subsidiary use case",
            lines=[{"account_id": "1111", "debit": "2000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "2000"}],
            period="2024-05",
        )
        assert result.is_success()
        entry = result.get_data()
        uc.post_entry(entry.id)

        sl_result = uc.post_to_subsidiary(
            journal_entry_id=entry.id,
            subsidiary_type="ar",
            entity_id=10,
            entity_name="UseCase Customer",
            doc_ref="UC-INV-001",
            doc_type="invoice",
        )
        assert sl_result.is_success()
        entries = uc.get_subsidiary_ledger("ar", entity_id=10)
        assert len(entries) == 2

    def test_invalid_subsidiary_type(self, session):
        uc = GLUseCases(session)
        with pytest.raises(ValidationError):
            uc.get_subsidiary_ledger("invalid_type")


class TestJournalTemplates:
    def test_generate_journal_template(self):
        entries = [
            JournalEntry(
                journal_number="JV2026000001", journal_type=JournalType.GENERAL,
                transaction_date=date(2026, 1, 15), description="Test entry", period="2026-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=1000, credit=0, period="2026-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=1000, period="2026-01")],
            ),
        ]
        result = generate_journal_template("S03c-DN", entries, "2026-01", "Test Co")
        assert result["template_code"] == "S03c-DN"
        assert result["company_name"] == "Test Co"
        assert result["row_count"] == 2
        assert result["debit_total"] != "0"

    def test_generate_journal_template_empty_entries(self):
        result = generate_journal_template("S03c-DN", [], "2026-01")
        assert result["row_count"] == 0
        assert result["debit_total"] == "0"

    def test_generate_s01_ledger(self):
        entries = [
            JournalEntry(
                journal_number="JV2026000001", journal_type=JournalType.GENERAL,
                transaction_date=date(2026, 1, 15), description="Test", period="2026-01",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=500, credit=0, period="2026-01"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=500, period="2026-01")],
            ),
        ]
        result = generate_s01_ledger("1111", "Tiền mặt", entries, "2026-01", Decimal("1000"), "Test Co")
        assert result["template_code"] == "S01-DN"
        assert result["account_code"] == "1111"
        assert result["account_name"] == "Tiền mặt"
        assert result["opening_balance"] != "0"
        assert result["row_count"] == 1

    def test_generate_s01_ledger_no_matching_lines(self):
        entries = [
            JournalEntry(
                journal_number="JV2026000001", journal_type=JournalType.GENERAL,
                transaction_date=date(2026, 1, 15), description="Test", period="2026-01",
                lines=[JournalLine(journal_entry_id=0, account_id="5111", debit=500, credit=0, period="2026-01"),
                       JournalLine(journal_entry_id=0, account_id="1111", debit=0, credit=500, period="2026-01")],
            ),
        ]
        result = generate_s01_ledger("2222", "Không có", entries, "2026-01")
        assert result["row_count"] == 0

    def test_generate_subsidiary_template(self):
        entries = [
            SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AR, account_code="131",
                entity_id=1, entity_name="Customer A",
                transaction_date=date(2026, 1, 15),
                doc_ref="INV-001", doc_type="invoice",
                description="Sale", debit=Decimal("1000"), credit=Decimal("0"),
                balance=Decimal("1000"), period="2026-01",
            ),
        ]
        result = generate_subsidiary_template("S06-DN", "ar", entries, "2026-01", "Test Co")
        assert result["template_code"] == "S06-DN"
        assert result["entity_count"] == 1
        assert result["entities"][0]["entity_name"] == "Customer A"

    def test_generate_subsidiary_template_multi_entity(self):
        entries = [
            SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AP, account_code="331",
                entity_id=1, entity_name="Vendor X",
                transaction_date=date(2026, 1, 15),
                doc_ref="PO-001", doc_type="purchase",
                description="Buy", debit=Decimal("0"), credit=Decimal("500"),
                balance=Decimal("500"), period="2026-01",
            ),
            SubsidiaryLedger(
                subsidiary_type=SubsidiaryType.AP, account_code="331",
                entity_id=2, entity_name="Vendor Y",
                transaction_date=date(2026, 1, 20),
                doc_ref="PO-002", doc_type="purchase",
                description="Buy 2", debit=Decimal("0"), credit=Decimal("300"),
                balance=Decimal("300"), period="2026-01",
            ),
        ]
        result = generate_subsidiary_template("S05-DN", "ap", entries, "2026-01")
        assert result["entity_count"] == 2

    def test_journal_type_template_map(self):
        assert JOURNAL_TYPE_TEMPLATE_MAP[JournalType.GENERAL] == "S03c-DN"
        assert JOURNAL_TYPE_TEMPLATE_MAP[JournalType.SALES] == "S03b2-DN"
        assert JOURNAL_TYPE_TEMPLATE_MAP[JournalType.PURCHASE] == "S03b1-DN"
        assert JOURNAL_TYPE_TEMPLATE_MAP[JournalType.CASH_RECEIPT] == "S03a1-DN"
        assert JOURNAL_TYPE_TEMPLATE_MAP[JournalType.CASH_PAYMENT] == "S03a2-DN"

    def test_template_names_completeness(self):
        for code in ["S03c-DN", "S03a1-DN", "S03a2-DN", "S03b1-DN", "S03b2-DN", "S01-DN", "S05-DN", "S06-DN"]:
            assert code in TEMPLATE_NAMES
            assert code in TEMPLATE_NAMES_EN

    def test_generate_specialized_template_s03a1(self):
        entries = [
            JournalEntry(
                journal_number="CR2026000001", journal_type=JournalType.CASH_RECEIPT,
                transaction_date=date(2026, 3, 10), description="Cash receipt", period="2026-03",
                lines=[JournalLine(journal_entry_id=0, account_id="1111", debit=2000, credit=0, period="2026-03"),
                       JournalLine(journal_entry_id=0, account_id="5111", debit=0, credit=2000, period="2026-03")],
            ),
        ]
        result = generate_journal_template("S03a1-DN", entries, "2026-03", "Test Co", counterparty="Nguyen Van A")
        assert result["template_code"] == "S03a1-DN"
        assert result["counterparty_label"] == "Người nộp"
        assert result["counterparty_label_en"] == "Payer"
        assert result["row_count"] == 2
        assert result["rows"][0]["counterparty"] == "Nguyen Van A"

    def test_generate_specialized_template_s03a2(self):
        entries = [
            JournalEntry(
                journal_number="CP2026000001", journal_type=JournalType.CASH_PAYMENT,
                transaction_date=date(2026, 3, 10), description="Cash payment", period="2026-03",
                lines=[JournalLine(journal_entry_id=0, account_id="6411", debit=1500, credit=0, period="2026-03"),
                       JournalLine(journal_entry_id=0, account_id="1111", debit=0, credit=1500, period="2026-03")],
            ),
        ]
        result = generate_journal_template("S03a2-DN", entries, "2026-03", "Test Co", counterparty="Tran Thi B")
        assert result["counterparty_label"] == "Người nhận"
        assert result["rows"][0]["counterparty"] == "Tran Thi B"

    def test_generate_specialized_template_s03b1(self):
        result = generate_journal_template("S03b1-DN", [], "2026-03")
        assert result["counterparty_label"] == "Nhà cung cấp"

    def test_generate_specialized_template_s03b2(self):
        result = generate_journal_template("S03b2-DN", [], "2026-03")
        assert result["counterparty_label"] == "Khách hàng"


class TestAutoSubsidiaryPost:
    def test_post_with_subsidiary_auto_posts(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV006000", transaction_date=date(2026, 6, 1),
            description="Auto-subsidiary test",
            lines=[{"account_id": "1111", "debit": "3000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "3000"}],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        post_result = uc.post_entry(
            entry.id, subsidiary_type="ar", entity_id=50,
            entity_name="Auto Customer", doc_ref="AUTO-INV-001", doc_type="invoice",
        )
        assert post_result.is_success()

        sub_entries = uc.get_subsidiary_ledger("ar", entity_id=50)
        assert len(sub_entries) == 2

    def test_post_with_subsidiary_combined_accounts(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV006001", transaction_date=date(2026, 6, 1),
            description="Multi-line subsidiary",
            lines=[{"account_id": "1111", "debit": "5000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "4000"},
                   {"account_id": "3331", "debit": "0", "credit": "1000"}],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        post_result = uc.post_entry(
            entry.id, subsidiary_type="ar", entity_id=51,
            entity_name="Multi Customer", doc_ref="AUTO-INV-002", doc_type="invoice",
        )
        assert post_result.is_success()

        sub_entries = uc.get_subsidiary_ledger("ar", entity_id=51)
        assert len(sub_entries) == 3

    def test_post_without_subsidiary_does_not_post(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV006002", transaction_date=date(2026, 6, 1),
            description="No subsidiary",
            lines=[{"account_id": "1111", "debit": "1000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "1000"}],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        uc.post_entry(entry.id)
        sub_entries = uc.get_subsidiary_ledger("ar", entity_id=1)
        assert len(sub_entries) == 0

    def test_post_with_subsidiary_balance_tracking(self, session):
        uc = GLUseCases(session)
        def create_and_post(jn, amount, entity, desc):
            r = uc.create_entry(
                journal_number=jn, transaction_date=date(2026, 7, 1),
                description=desc,
                lines=[{"account_id": "1111", "debit": str(amount), "credit": "0"},
                       {"account_id": "5111", "debit": "0", "credit": str(amount)}],
                period="2026-07",
            )
            e = r.get_data()
            uc.post_entry(e.id, subsidiary_type="ar", entity_id=entity,
                          entity_name="Bal Test", doc_ref=jn, doc_type="inv")
            return e

        create_and_post("JV006010", 1000, 60, "Entry 1")
        create_and_post("JV006011", 500, 60, "Entry 2")
        sub = uc.get_subsidiary_ledger("ar", entity_id=60)
        assert len(sub) == 4

    def test_auto_detect_from_line_entity_id(self, session):
        """Lines with entity_id set auto-post to subsidiary ledger."""
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV009010", transaction_date=date(2026, 6, 1),
            description="Auto-detect AR",
            lines=[
                {"account_id": "1311", "debit": "2000", "credit": "0",
                 "entity_id": 100, "entity_name": "Khách hàng A"},
                {"account_id": "5111", "debit": "0", "credit": "2000"},
            ],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        # Post without manual override — should auto-detect
        post_result = uc.post_entry(entry.id)
        assert post_result.is_success()

        sub = uc.get_subsidiary_ledger("ar", entity_id=100)
        assert len(sub) == 1
        assert sub[0].debit == Decimal("2000")
        assert sub[0].entity_name == "Khách hàng A"

    def test_auto_detect_multiple_subsidiary_types(self, session):
        """Lines with different subsidiary entity_ids post to correct sub-ledgers."""
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV009011", transaction_date=date(2026, 6, 1),
            description="Multi subsidiary types",
            lines=[
                {"account_id": "1311", "debit": "1500", "credit": "0",
                 "entity_id": 200, "entity_name": "KH B"},
                {"account_id": "3311", "debit": "0", "credit": "1500",
                 "entity_id": 300, "entity_name": "NCC C"},
            ],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        post_result = uc.post_entry(entry.id)
        assert post_result.is_success()

        ar_subs = uc.get_subsidiary_ledger("ar", entity_id=200)
        assert len(ar_subs) == 1
        assert ar_subs[0].debit == Decimal("1500")

        ap_subs = uc.get_subsidiary_ledger("ap", entity_id=300)
        assert len(ap_subs) == 1
        assert ap_subs[0].credit == Decimal("1500")

    def test_auto_detect_skipped_when_manual_override(self, session):
        """Manual override takes precedence over line-level auto-detect."""
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV009012", transaction_date=date(2026, 6, 1),
            description="Override test",
            lines=[
                {"account_id": "1311", "debit": "3000", "credit": "0",
                 "entity_id": 400, "entity_name": "KH D"},
                {"account_id": "5111", "debit": "0", "credit": "3000"},
            ],
            period="2026-06",
        )
        assert result.is_success()
        entry = result.get_data()

        # Manual override with different entity — should post ALL lines to entity 999
        uc.post_entry(entry.id, subsidiary_type="ar", entity_id=999,
                      entity_name="Override Entity", doc_ref="OVR", doc_type="inv")

        # Check override entity got the entry, NOT entity 400 from line
        override_subs = uc.get_subsidiary_ledger("ar", entity_id=999)
        assert len(override_subs) == 2  # Both lines posted

        original_subs = uc.get_subsidiary_ledger("ar", entity_id=400)
        assert len(original_subs) == 0  # Auto-detect skipped


class TestReversalEntry:
    def test_red_storno_reversal(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV007000", transaction_date=date(2026, 7, 1),
            description="Original entry for storno",
            lines=[{"account_id": "1111", "debit": "1000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "1000"}],
            period="2026-07",
        )
        assert result.is_success()
        entry = result.get_data()

        post_result = uc.post_entry(entry.id)
        assert post_result.is_success()

        rev_result = uc.reverse_entry(entry.id, correction_method="red_storno")
        error_msg = str(rev_result.error) if rev_result.is_failure() else ""
        assert rev_result.is_success(), f"Reverse failed: {error_msg}"
        rev = rev_result.get_data()
        assert rev.ref_journal_number == "JV007000"
        assert rev.journal_type == JournalType.ADJUSTMENT

    def test_additional_correction(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV007001", transaction_date=date(2026, 7, 1),
            description="Original entry for additional",
            lines=[{"account_id": "1111", "debit": "500", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "500"}],
            period="2026-07",
        )
        assert result.is_success()
        entry = result.get_data()
        uc.post_entry(entry.id)

        rev_result = uc.reverse_entry(entry.id, correction_method="additional",
                                      description="Additional correction")
        error_msg = str(rev_result.error) if rev_result.is_failure() else ""
        assert rev_result.is_success(), f"Reverse failed: {error_msg}"
        rev = rev_result.get_data()
        for i, line in enumerate(entry.lines):
            rl = rev.lines[i]
            assert rl.debit == line.debit
            assert rl.credit == line.credit

    def test_reverse_unposted_entry_fails(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV007002", transaction_date=date(2026, 7, 1),
            description="Unposted entry",
            lines=[{"account_id": "1111", "debit": "100", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "100"}],
            period="2026-07",
        )
        assert result.is_success()
        entry = result.get_data()

        rev_result = uc.reverse_entry(entry.id)
        assert rev_result.is_failure()
        assert "CANNOT_REVERSE_UNPOSTED" in str(rev_result.error)

    def test_reverse_nonexistent_entry_fails(self, session):
        uc = GLUseCases(session)
        rev_result = uc.reverse_entry(99999)
        assert rev_result.is_failure()
        assert "JOURNAL_ENTRY_NOT_FOUND" in str(rev_result.error)

    def test_invalid_correction_method_fails(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV007003", transaction_date=date(2026, 7, 1),
            description="Valid entry",
            lines=[{"account_id": "1111", "debit": "200", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "200"}],
            period="2026-07",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        rev_result = uc.reverse_entry(entry.id, correction_method="INVALID")
        assert rev_result.is_failure()
        assert "INVALID_CORRECTION_METHOD" in str(rev_result.error)

    def test_red_storno_swaps_debit_credit(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV007004", transaction_date=date(2026, 7, 1),
            description="Entry with mixed accounts",
            lines=[{"account_id": "1111", "debit": "1000", "credit": "0"},
                   {"account_id": "6411", "debit": "500", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "1500"}],
            period="2026-07",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        rev_result = uc.reverse_entry(entry.id, correction_method="red_storno")
        error_msg = str(rev_result.error) if rev_result.is_failure() else ""
        assert rev_result.is_success(), f"Reverse failed: {error_msg}"
        rev = rev_result.get_data()
        assert rev.lines[0].debit == Decimal("0") and rev.lines[0].credit == Decimal("1000")


class TestReportingEngine:
    def test_trial_balance_basic(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV008000", transaction_date=date(2026, 8, 1),
            description="TB test",
            lines=[{"account_id": "1111", "debit": "5000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "5000"}],
            period="2026-08",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        tb = uc.generate_trial_balance("2026-08")
        assert tb["statement_type"] == "trial_balance"
        assert tb["account_count"] >= 2
        assert Decimal(tb["total_period_debit"]) == Decimal(tb["total_period_credit"])
        assert Decimal(tb["total_period_debit"]) >= Decimal("5000")

    def test_trial_balance_empty_period(self, session):
        uc = GLUseCases(session)
        tb = uc.generate_trial_balance("2026-09")
        assert tb["statement_type"] == "trial_balance"
        assert tb["account_count"] >= 8

    def test_cash_flow_direct_empty(self, session):
        uc = GLUseCases(session)
        cf = uc.generate_cash_flow("2026-08", method="direct")
        assert cf["statement_type"] == "cash_flow"
        assert cf["method"] == "direct"
        assert "operating" in cf
        assert "investing" in cf
        assert "financing" in cf

    def test_cash_flow_with_cash_entry(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="CR2026080001", transaction_date=date(2026, 8, 15),
            description="Cash receipt",
            lines=[{"account_id": "1111", "debit": "10000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "10000"}],
            period="2026-08",
            journal_type="cash_receipt",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        cf = uc.generate_cash_flow("2026-08", method="direct")
        assert Decimal(cf["operating"]["inflow"]) >= Decimal("10000")

    def test_balance_sheet_basic(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV008001", transaction_date=date(2026, 8, 1),
            description="BS test",
            lines=[{"account_id": "1111", "debit": "20000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "20000"}],
            period="2026-08",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        bs = uc.generate_balance_sheet("2026-08")
        assert bs["statement_type"] == "balance_sheet"
        assert "assets" in bs
        assert "liabilities" in bs
        assert "equity" in bs

    def test_income_statement_basic(self, session):
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number="JV008002", transaction_date=date(2026, 8, 1),
            description="IS test",
            lines=[{"account_id": "1111", "debit": "30000", "credit": "0"},
                   {"account_id": "5111", "debit": "0", "credit": "30000"}],
            period="2026-08",
        )
        entry = result.get_data()
        uc.post_entry(entry.id)

        is_ = uc.generate_income_statement("2026-08")
        assert is_["statement_type"] == "income_statement"
        assert "revenue" in is_
        assert "expenses" in is_
        assert "net_income" in is_

    def test_cash_flow_indirect_not_impl(self, session):
        uc = GLUseCases(session)
        cf = uc.generate_cash_flow("2026-08", method="indirect")
        assert "error" in cf
