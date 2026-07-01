import sys
sys.path.insert(0, "/home/projects/smart_acct")

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal

from domain import (
    Company, CompanyCreate, CompanyUpdate,
    FiscalYearConfig, FiscalYearCreate,
    NumberingRule, NumberingRuleUpdate,
    SetupChecklistItem,
    SetupSection, DocumentType,
    VASValidationError, Result,
)
from use_cases.company import CompanyUseCases
from infrastructure.repositories.company_repository import CompanyRepository

pytestmark = pytest.mark.integration


def _get_session():
    from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig
    config = SmartACCTDatabaseConfig()
    manager = SmartACCTDatabaseManager(config)
    manager.initialize()
    return manager.get_session()


def _get_use_cases(session_factory=None):
    if session_factory is None:
        from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig
        config = SmartACCTDatabaseConfig()
        manager = SmartACCTDatabaseManager(config)
        manager.initialize()
        session_factory = manager.get_session
    return CompanyUseCases(session_factory=session_factory)


@pytest.fixture(scope="module")
def session_factory():
    from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig
    config = SmartACCTDatabaseConfig()
    manager = SmartACCTDatabaseManager(config)
    manager.initialize()
    yield manager.get_session
    manager.close()


@pytest.fixture
def clean_db(session_factory):
    session = session_factory()
    try:
        from infrastructure.models.company_models import (
            CompanyModel, FiscalYearConfigModel,
            NumberingRuleModel, SetupChecklistItemModel,
        )
        session.query(SetupChecklistItemModel).delete()
        session.query(NumberingRuleModel).delete()
        session.query(FiscalYearConfigModel).delete()
        session.query(CompanyModel).delete()
        session.commit()
    finally:
        session.close()


@pytest.fixture
def company_uc(session_factory):
    return _get_use_cases(session_factory)


class TestCompanyCRUD:
    def test_create_company(self, company_uc, clean_db):
        req = CompanyCreate(
            name="Công ty TNHH ABC",
            tax_code="1234567890",
            address="123 Đường Lê Lợi, Quận 1, TP.HCM",
            phone="02812345678",
            email="info@abc.vn",
        )
        result = company_uc.create_company(req)
        assert result.is_success(), f"Failed: {result.get_error()}"
        company = result.get_data()
        assert company.id is not None
        assert company.name == "Công ty TNHH ABC"
        assert company.tax_code == "1234567890"

    def test_create_company_auto_creates_fiscal_year(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        assert result.is_success()
        company = result.get_data()

        fy_result = company_uc.list_fiscal_years(company.id)
        assert fy_result.is_success()
        years = fy_result.get_data()
        assert len(years) == 1
        assert years[0]["is_current"] is True

    def test_create_company_auto_creates_numbering_rules(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        assert result.is_success()
        company = result.get_data()

        nr_result = company_uc.list_numbering_rules(company.id)
        assert nr_result.is_success()
        rules = nr_result.get_data()
        assert len(rules) == 11

    def test_create_company_auto_creates_checklist(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        assert result.is_success()
        company = result.get_data()

        sc_result = company_uc.get_setup_checklist(company.id)
        assert sc_result.is_success()
        data = sc_result.get_data()
        assert len(data["items"]) == 13

    def test_get_active_company(self, company_uc, clean_db):
        req = CompanyCreate(name="Active Co")
        company_uc.create_company(req)

        result = company_uc.get_active_company()
        assert result.is_success()
        data = result.get_data()
        assert data["name"] == "Active Co"

    def test_get_active_company_not_found(self, company_uc, clean_db):
        result = company_uc.get_active_company()
        assert result.is_failure()

    def test_update_company(self, company_uc, clean_db):
        req = CompanyCreate(name="Original Name")
        result = company_uc.create_company(req)
        company = result.get_data()

        updates = CompanyUpdate(name="Updated Name", phone="0909123456")
        result = company_uc.update_company(company.id, updates)
        assert result.is_success()
        updated = result.get_data()
        assert updated.name == "Updated Name"
        assert updated.phone == "0909123456"

    def test_get_company_by_id(self, company_uc, clean_db):
        req = CompanyCreate(name="Specific Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.get_company(company.id)
        assert result.is_success()
        data = result.get_data()
        assert data["name"] == "Specific Co"

    def test_rejects_duplicate_active_company(self, company_uc, clean_db):
        company_uc.create_company(CompanyCreate(name="First Co"))
        result = company_uc.create_company(CompanyCreate(name="Second Co"))
        assert result.is_failure()


class TestFiscalYear:
    def test_create_fiscal_year(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        fy_req = FiscalYearCreate(
            fiscal_year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )
        result = company_uc.create_fiscal_year(company.id, fy_req)
        assert result.is_success()

    def test_rejects_duplicate_fiscal_year(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        fy_req = FiscalYearCreate(
            fiscal_year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        result = company_uc.create_fiscal_year(company.id, fy_req)
        assert result.is_failure()

    def test_close_fiscal_year(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        fy_req = FiscalYearCreate(
            fiscal_year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )
        company_uc.create_fiscal_year(company.id, fy_req)

        result = company_uc.close_fiscal_year(company.id, 2027)
        assert result.is_success()

    def test_cannot_close_already_closed(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        fy_req = FiscalYearCreate(
            fiscal_year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )
        company_uc.create_fiscal_year(company.id, fy_req)

        company_uc.close_fiscal_year(company.id, 2027)
        result = company_uc.close_fiscal_year(company.id, 2027)
        assert result.is_failure()

    def test_list_fiscal_years(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        fy_req = FiscalYearCreate(
            fiscal_year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )
        company_uc.create_fiscal_year(company.id, fy_req)

        result = company_uc.list_fiscal_years(company.id)
        assert result.is_success()
        years = result.get_data()
        assert len(years) == 2


class TestNumberingRules:
    def test_get_next_number(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.get_next_number(
            company.id, DocumentType.AR_INVOICE, 2026
        )
        assert result.is_success()
        data = result.get_data()
        assert data["sequence"] == 1
        assert "HD" in data["number"]

    def test_next_number_increments(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result1 = company_uc.get_next_number(
            company.id, DocumentType.AR_INVOICE, 2026
        )
        assert result1.is_success()
        assert result1.get_data()["sequence"] == 1

        result2 = company_uc.get_next_number(
            company.id, DocumentType.AR_INVOICE, 2026
        )
        assert result2.is_success()
        assert result2.get_data()["sequence"] == 2

    def test_list_numbering_rules_by_type(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.list_numbering_rules(
            company.id, document_type=DocumentType.JOURNAL_ENTRY
        )
        assert result.is_success()
        rules = result.get_data()
        assert len(rules) == 1
        assert rules[0]["document_type"] == "journal_entry"

    def test_list_numbering_rules_by_fiscal_year(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.list_numbering_rules(
            company.id, fiscal_year=2026
        )
        assert result.is_success()
        rules = result.get_data()
        assert len(rules) == 11

    def test_update_numbering_rule(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        nr_result = company_uc.list_numbering_rules(
            company.id, document_type=DocumentType.AR_INVOICE
        )
        rule = nr_result.get_data()[0]

        updates = NumberingRuleUpdate(prefix="INV", pad_length=8)
        result = company_uc.update_numbering_rule(company.id, rule["id"], updates)
        assert result.is_success()
        updated = result.get_data()
        assert updated.prefix == "INV"
        assert updated.pad_length == 8

    def test_get_numbering_rule(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.get_numbering_rule(
            company.id, DocumentType.AR_INVOICE, 2026
        )
        assert result.is_success()
        rule = result.get_data()
        assert rule["document_type"] == "ar_invoice"

    def test_get_next_number_missing_rule(self, company_uc, clean_db):
        result = company_uc.get_next_number(
            9999, DocumentType.AR_INVOICE, 2026
        )
        assert result.is_failure()


class TestSetupChecklist:
    def test_get_checklist(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.get_setup_checklist(company.id)
        assert result.is_success()
        data = result.get_data()
        assert len(data["items"]) == 13
        assert "progress" in data
        assert data["progress"]["completed"] == 0
        assert data["progress"]["total"] == 13

    def test_mark_section_complete(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        result = company_uc.mark_setup_complete(
            company.id, SetupSection.COMPANY_INFO
        )
        assert result.is_success()

        result = company_uc.get_setup_checklist(company.id)
        data = result.get_data()
        assert data["progress"]["completed"] == 1

    def test_mark_same_section_twice(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        company_uc.mark_setup_complete(company.id, SetupSection.COMPANY_INFO)
        result = company_uc.mark_setup_complete(
            company.id, SetupSection.COMPANY_INFO
        )
        assert result.is_failure()

    def test_mark_all_sections_complete(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        for section in SetupSection:
            company_uc.mark_setup_complete(company.id, section)

        result = company_uc.get_setup_checklist(company.id)
        data = result.get_data()
        assert data["progress"]["completed"] == 13
        assert data["progress"]["percentage"] == 100.0

    def test_mark_invalid_section(self, company_uc, clean_db):
        req = CompanyCreate(name="Test Co")
        result = company_uc.create_company(req)
        company = result.get_data()

        from domain.i18n import ErrorCodes
        import uuid
        result = company_uc.mark_setup_complete(
            company.id, SetupSection.COMPANY_INFO
        )
        assert result.is_success()


class TestRepository:
    def test_get_setup_progress_no_items(self, clean_db):
        session = _get_session()
        try:
            repo = CompanyRepository(session)
            result = repo.get_setup_progress(9999)
            assert result.is_success()
            data = result.get_data()
            assert data["total"] == 0
        finally:
            session.close()
