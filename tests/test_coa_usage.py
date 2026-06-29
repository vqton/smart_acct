import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import AccountType, DCRDirection
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel, AccountingPeriodModel
from use_cases.coa_usage_use_case import COAUsageUseCase


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    _seed(sess)
    sess.commit()
    yield sess
    sess.close()


def _seed(sess):
    accounts = [
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction=DCRDirection.DEBIT.value, level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction=DCRDirection.CREDIT.value, level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="3311", name="Phải trả người bán", account_type="liability",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction=DCRDirection.CREDIT.value, level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for a in accounts:
        sess.add(a)

    entry = JournalEntryModel(
        journal_number="JN-2026-0001",
        transaction_date=date(2026, 6, 1),
        description="Test entry",
        period="2026-01",
        is_posted=True,
        created_by="admin",
    )
    sess.add(entry)
    sess.flush()

    lines = [
        JournalLineModel(journal_entry_id=entry.id, account_id="1111", debit=10000, credit=0, description="Line 1", period="2026-01"),
        JournalLineModel(journal_entry_id=entry.id, account_id="5111", debit=0, credit=10000, description="Line 2", period="2026-01"),
    ]
    for l in lines:
        sess.add(l)


class TestCOAUsage:
    def test_check_usage_with_transactions(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("1111")
        assert result.is_success()
        data = result.get_data()
        assert data["code"] == "1111"
        assert data["transaction_count"] == 1
        assert data["can_deactivate"] is False
        assert data["can_delete"] is False

    def test_check_usage_no_transactions(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("3311")
        assert result.is_success()
        data = result.get_data()
        assert data["code"] == "3311"
        assert data["transaction_count"] == 0
        assert data["balance"] == "0.00"
        assert data["can_deactivate"] is True
        assert data["can_delete"] is True

    def test_check_usage_nonexistent_account(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("NONEXIST")
        assert result.is_failure()
        assert "ACCOUNT_NOT_FOUND" in str(result.error)

    def test_check_usage_returns_balance(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("1111")
        assert result.is_success()
        data = result.get_data()
        assert float(data["balance"]) > 0
        assert data["account_type"] == "asset"
        assert data["balance_type"] == "debit"

    def test_check_usage_returns_last_transaction_date(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("1111")
        assert result.is_success()
        data = result.get_data()
        assert data["last_transaction_date"] == "2026-06-01"

    def test_check_usage_revenue_account(self, session):
        uc = COAUsageUseCase(session)
        result = uc.check_usage("5111")
        assert result.is_success()
        data = result.get_data()
        assert data["account_type"] == "revenue"
        assert float(data["balance"]) > 0
