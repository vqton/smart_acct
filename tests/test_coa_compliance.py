import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import AccountType, DCRDirection, AccountingRegime, AccountStatus
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus
from use_cases.coa_validate_use_case import COAValidateUseCase


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
        COAModel(code="1", name="Tài sản", account_type="asset",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="2", name="Nợ phải trả", account_type="liability",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="credit", level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="debit", level=2, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="credit", level=2, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="3311", name="Phải trả người bán", account_type="liability",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="credit", level=2, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for a in accounts:
        sess.add(a)


class TestCOACompliance:
    def test_run_compliance_scan_all_valid(self, session):
        uc = COAValidateUseCase(session)
        result = uc.run_compliance_scan()
        assert result.is_success()
        data = result.get_data()
        assert data["summary"]["total_accounts"] == 5
        assert data["summary"]["compliant"] == 5
        assert data["summary"]["non_compliant"] == 0
        assert data["summary"]["compliance_pct"] == 100

    def test_single_check_compliant(self, session):
        uc = COAValidateUseCase(session)
        result = uc.check_compliance("1111")
        assert result.is_success()
        data = result.get_data()
        assert data["compliant"] is True
        assert data["code"] == "1111"

    def test_single_check_non_existent(self, session):
        uc = COAValidateUseCase(session)
        result = uc.check_compliance("NONEXIST")
        assert result.is_failure()
        assert "ACCOUNT_NOT_FOUND" in str(result.error)

    def test_dcr_direction_mismatch_detected(self, session):
        acc = COAModel(code="9999", name="Test mismatch", account_type="asset",
                       regime=DBRegime.TT99_2025, vas_compliant=True,
                       drcr_direction="credit", level=1, status=DBStatus.ACTIVE,
                       currency="VND", unit="VND")
        session.add(acc)
        session.commit()

        uc = COAValidateUseCase(session)
        result = uc.check_compliance("9999")
        assert result.is_success()
        data = result.get_data()
        assert data["compliant"] is False
        assert any("COA_DCR_MISMATCH" in i for i in data["issues"])

    def test_scan_detects_dcr_mismatch(self, session):
        acc = COAModel(code="9998", name="Bad direction", account_type="liability",
                       regime=DBRegime.TT99_2025, vas_compliant=True,
                       drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                       currency="VND", unit="VND")
        session.add(acc)
        session.commit()

        uc = COAValidateUseCase(session)
        result = uc.run_compliance_scan()
        assert result.is_success()
        data = result.get_data()
        assert data["summary"]["non_compliant"] > 0

    def test_rules_checked_listed(self, session):
        uc = COAValidateUseCase(session)
        result = uc.run_compliance_scan()
        data = result.get_data()
        assert "code_format" in data["rules_checked"]
        assert "dcr_direction" in data["rules_checked"]
        assert "parent_exists" in data["rules_checked"]

    def test_validate_all_includes_dcr_check(self, session):
        acc = COAModel(code="9997", name="Wrong dir", account_type="revenue",
                       regime=DBRegime.TT99_2025, vas_compliant=True,
                       drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                       currency="VND", unit="VND")
        session.add(acc)
        session.commit()

        uc = COAValidateUseCase(session)
        result = uc.validate_all()
        assert result.is_success()
        data = result.get_data()
        assert data["invalid"] >= 1
