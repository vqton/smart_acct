import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import AccountType, DCRDirection
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus
from use_cases.coa_ifrs_use_case import COAIFRSUseCase
from use_cases.coa_use_cases import COAUseCases


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
                 drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="credit", level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for a in accounts:
        sess.add(a)


class TestIFRSMapping:
    def test_create_mapping(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.create_mapping(
            vas_account_code="1111",
            ifrs_account_code="IFRS_CASH_001",
            mapping_type="1:1",
            created_by="admin",
        )
        assert result.is_success()
        data = result.get_data()
        assert data["vas_account_code"] == "1111"
        assert data["ifrs_account_code"] == "IFRS_CASH_001"
        assert data["mapping_type"] == "1:1"

    def test_create_duplicate_mapping_fails(self, session):
        uc = COAIFRSUseCase(session)
        uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH_001")
        result = uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH_001")
        assert result.is_failure()

    def test_create_mapping_nonexistent_vas_fails(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.create_mapping(vas_account_code="NONEXIST", ifrs_account_code="IFRS_X")
        assert result.is_failure()

    def test_list_mappings(self, session):
        uc = COAIFRSUseCase(session)
        uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH")
        uc.create_mapping(vas_account_code="5111", ifrs_account_code="IFRS_REV")
        mappings = uc.list_mappings()
        assert len(mappings) == 2

    def test_list_mappings_filtered(self, session):
        uc = COAIFRSUseCase(session)
        uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH")
        uc.create_mapping(vas_account_code="5111", ifrs_account_code="IFRS_REV")
        mappings = uc.list_mappings(vas_account_code="1111")
        assert len(mappings) == 1
        assert mappings[0]["ifrs_account_code"] == "IFRS_CASH"

    def test_get_mapping(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH")
        m_id = result.get_data()["id"]
        fetched = uc.get_mapping(m_id)
        assert fetched.is_success()
        assert fetched.get_data()["vas_account_code"] == "1111"

    def test_get_mapping_not_found(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.get_mapping(9999)
        assert result.is_failure()

    def test_delete_mapping(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH")
        m_id = result.get_data()["id"]
        del_result = uc.delete_mapping(m_id)
        assert del_result.is_success()
        assert uc.get_mapping(m_id).is_failure()

    def test_delete_mapping_not_found(self, session):
        uc = COAIFRSUseCase(session)
        result = uc.delete_mapping(9999)
        assert result.is_failure()

    def test_coverage(self, session):
        uc = COAIFRSUseCase(session)
        coverage = uc.get_coverage()
        assert coverage["total_vas_accounts"] == 2
        assert coverage["mapped_accounts"] == 0
        assert coverage["coverage_percent"] == 0.0

        uc.create_mapping(vas_account_code="1111", ifrs_account_code="IFRS_CASH")
        coverage = uc.get_coverage()
        assert coverage["mapped_accounts"] == 1
        assert coverage["coverage_percent"] == 50.0
        assert len(coverage["unmapped"]) == 1
