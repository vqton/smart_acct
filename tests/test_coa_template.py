import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import AccountType, DCRDirection
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus
from use_cases.coa_template_use_case import COATemplateUseCase


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


class TestCOATemplate:
    def test_list_templates(self, session):
        uc = COATemplateUseCase(session)
        templates = uc.list_templates()
        assert len(templates) >= 2
        tids = [t["id"] for t in templates]
        assert "tt99_2025_standard" in tids
        assert "tt133_2016_standard" in tids

    def test_preview_template_valid(self, session):
        uc = COATemplateUseCase(session)
        result = uc.preview_template("tt99_2025_standard")
        assert result.is_success()
        data = result.get_data()
        assert data["name"].startswith("Standard COA")
        assert len(data["accounts"]) > 0

    def test_preview_template_not_found(self, session):
        uc = COATemplateUseCase(session)
        result = uc.preview_template("nonexistent")
        assert result.is_failure()

    def test_apply_template(self, session):
        uc = COATemplateUseCase(session)
        result = uc.apply_template("tt133_2016_standard")
        assert result.is_success()
        data = result.get_data()
        assert data["created_count"] > 0

        accounts = uc.repo.list_all()
        assert len(accounts) == data["created_count"]

    def test_apply_template_clear_existing(self, session):
        uc = COATemplateUseCase(session)
        acc = COAModel(code="9999", name="Old account", account_type="asset",
                       regime=DBRegime.TT99_2025, vas_compliant=True,
                       drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                       currency="VND", unit="VND")
        session.add(acc)
        session.commit()

        result = uc.apply_template("tt99_2025_standard", clear_existing=True)
        assert result.is_success()
        data = result.get_data()
        assert data["created_count"] > 0

        accounts = uc.repo.list_all()
        assert all(a.code != "9999" for a in accounts)

    def test_apply_template_merge(self, session):
        uc = COATemplateUseCase(session)
        result = uc.apply_template("tt99_2025_standard")
        assert result.is_success()
        result2 = uc.apply_template("tt99_2025_standard")
        assert result2.is_success()
        data2 = result2.get_data()
        assert data2["created_count"] == 0
        assert data2["error_count"] > 0

    def test_template_account_types_valid(self, session):
        uc = COATemplateUseCase(session)
        for tid in ["tt99_2025_standard", "tt133_2016_standard"]:
            result = uc.preview_template(tid)
            assert result.is_success()
            data = result.get_data()
            for a in data["accounts"]:
                assert a["account_type"] in [t.value for t in AccountType]
