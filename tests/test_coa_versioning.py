import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import AccountType, DCRDirection
from infrastructure.models.coa_models import Base, COAModel
from use_cases.coa_versioning_use_case import COAVersioningUseCase
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
        COAModel(code="1", name="Tài sản", account_type="asset",
                 regime="tt99_2025", vas_compliant=True,
                 drcr_direction="debit", level=1, status="active",
                 currency="VND", unit="VND"),
        COAModel(code="2", name="Nợ phải trả", account_type="liability",
                 regime="tt99_2025", vas_compliant=True,
                 drcr_direction="credit", level=1, status="active",
                 currency="VND", unit="VND"),
    ]
    for a in accounts:
        sess.add(a)


class TestVersioning:
    def test_create_snapshot(self, session):
        uc = COAVersioningUseCase(session)
        result = uc.create_snapshot(created_by="admin", notes="Initial version")
        assert result.is_success()
        data = result.get_data()
        assert data["account_count"] == 2
        assert data["created_by"] == "admin"
        assert data["id"] is not None

    def test_list_versions(self, session):
        uc = COAVersioningUseCase(session)
        uc.create_snapshot(created_by="admin")
        uc.create_snapshot(created_by="user1")
        versions = uc.list_versions()
        assert len(versions) == 2

    def test_get_version(self, session):
        uc = COAVersioningUseCase(session)
        result = uc.create_snapshot(created_by="admin")
        v_id = result.get_data()["id"]
        fetched = uc.get_version(v_id)
        assert fetched.is_success()
        data = fetched.get_data()
        assert data["id"] == v_id
        assert len(data["snapshot"]) == 2

    def test_get_version_not_found(self, session):
        uc = COAVersioningUseCase(session)
        result = uc.get_version(9999)
        assert result.is_failure()

    def test_diff_no_changes(self, session):
        uc = COAVersioningUseCase(session)
        v1 = uc.create_snapshot(created_by="admin").get_data()["id"]
        v2 = uc.create_snapshot(created_by="admin").get_data()["id"]
        result = uc.diff_versions(v1, v2)
        assert result.is_success()
        data = result.get_data()
        assert data["added_count"] == 0
        assert data["removed_count"] == 0
        assert data["changed_count"] == 0

    def test_diff_with_changes(self, session):
        uc = COAVersioningUseCase(session)
        v1 = uc.create_snapshot(created_by="admin").get_data()["id"]

        uc_repo = COAUseCases(session)
        uc_repo.create_account(code="3", name="Vốn chủ sở hữu",
                               account_type=AccountType.EQUITY,
                               drcr_direction=DCRDirection.CREDIT)
        uc_repo.delete_account("2")

        v2 = uc.create_snapshot(created_by="admin").get_data()["id"]
        result = uc.diff_versions(v1, v2)
        assert result.is_success()
        data = result.get_data()
        assert data["added_count"] == 1
        assert data["removed_count"] == 1
        assert data["changed_count"] == 0

    def test_diff_version_not_found(self, session):
        uc = COAVersioningUseCase(session)
        v1 = uc.create_snapshot().get_data()["id"]
        result = uc.diff_versions(v1, 9999)
        assert result.is_failure()

    def test_auto_snapshot(self, session):
        uc = COAVersioningUseCase(session)
        result = uc.auto_snapshot(created_by="tester")
        assert result.is_success()
        assert result.get_data()["account_count"] == 2
