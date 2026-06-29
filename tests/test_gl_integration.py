from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from domain import JournalEntry, JournalLine, Result, ValidationError, DoubleEntryError
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime, AccountStatus
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel, AccountingPeriodModel
from infrastructure.repositories.gl_repository import GLRepository
from use_cases.gl_use_cases import GLUseCases


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
        assert "Double-entry" in str(post_result.error)

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
        assert "closed" in str(result.error)

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
        assert "closed" in str(post_result.error)

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
        assert "closed" in str(update_result.error)


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
