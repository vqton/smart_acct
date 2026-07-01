import sys
sys.path.insert(0, "/home/projects/smart_acct")

import pytest
from datetime import datetime, date, timezone
from pydantic import ValidationError as PydanticValidationError
from domain import (
    Company, CompanyCreate, CompanyUpdate,
    FiscalYearConfig, FiscalYearCreate,
    NumberingRule, NumberingRuleUpdate,
    SetupChecklistItem,
    SetupSection, DocumentType,
    VASValidationError,
)


class TestCompany:
    def test_create_valid_company(self):
        c = Company(name="Công ty TNHH ABC", tax_code="1234567890")
        assert c.name == "Công ty TNHH ABC"
        assert c.tax_code == "1234567890"
        assert c.currency_code == "VND"
        assert c.fiscal_year_start_month == 1
        assert c.accounting_regime == "TT99"
        assert c.locale == "vi"
        assert c.is_active is True

    def test_rejects_empty_name(self):
        with pytest.raises(VASValidationError):
            Company(name="", tax_code="1234567890")

    def test_rejects_blank_name(self):
        with pytest.raises(VASValidationError):
            Company(name="   ")

    def test_rejects_invalid_tax_code_too_short(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", tax_code="12345")

    def test_rejects_invalid_tax_code_too_long(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", tax_code="123456789012345")

    def test_accepts_valid_tax_code(self):
        c = Company(name="Test", tax_code="1234567890")
        assert c.tax_code == "1234567890"

    def test_accepts_tax_code_14_digits(self):
        c = Company(name="Test", tax_code="12345678901234")
        assert c.tax_code == "12345678901234"

    def test_accepts_none_tax_code(self):
        c = Company(name="Test", tax_code=None)
        assert c.tax_code is None

    def test_rejects_invalid_fiscal_year_start_month_low(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", fiscal_year_start_month=0)

    def test_rejects_invalid_fiscal_year_start_month_high(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", fiscal_year_start_month=13)

    def test_accepts_valid_fiscal_year_start_month(self):
        c = Company(name="Test", fiscal_year_start_month=4)
        assert c.fiscal_year_start_month == 4

    def test_rejects_invalid_locale(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", locale="fr")

    def test_accepts_vi_locale(self):
        c = Company(name="Test", locale="vi")
        assert c.locale == "vi"

    def test_accepts_en_locale(self):
        c = Company(name="Test", locale="en")
        assert c.locale == "en"

    def test_rejects_empty_currency(self):
        with pytest.raises(VASValidationError):
            Company(name="Test", currency_code="")

    def test_company_default_timestamps(self):
        c = Company(name="Test")
        assert c.created_at is not None
        assert c.updated_at is None


class TestCompanyCreate:
    def test_valid_create_req(self):
        req = CompanyCreate(name="Test Co", tax_code="1234567890")
        assert req.name == "Test Co"
        assert req.tax_code == "1234567890"

    def test_rejects_empty_name(self):
        with pytest.raises(VASValidationError):
            CompanyCreate(name="")

    def test_rejects_invalid_tax_code(self):
        with pytest.raises(VASValidationError):
            CompanyCreate(name="Test", tax_code="abc")


class TestCompanyUpdate:
    def test_all_optional_fields(self):
        req = CompanyUpdate()
        data = req.model_dump(exclude_none=True)
        assert data == {}

    def test_partial_update(self):
        req = CompanyUpdate(name="New Name", phone="0909123456")
        data = req.model_dump(exclude_none=True)
        assert data["name"] == "New Name"
        assert data["phone"] == "0909123456"
        assert "tax_code" not in data


class TestFiscalYearConfig:
    def test_create_valid_fiscal_year(self):
        fy = FiscalYearConfig(
            company_id=1,
            fiscal_year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        assert fy.company_id == 1
        assert fy.fiscal_year == 2026
        assert fy.is_closed is False
        assert fy.is_current is False

    def test_rejects_start_after_end(self):
        with pytest.raises(VASValidationError):
            FiscalYearConfig(
                company_id=1,
                fiscal_year=2026,
                start_date=date(2026, 12, 31),
                end_date=date(2026, 1, 1),
            )

    def test_rejects_same_start_end(self):
        with pytest.raises(VASValidationError):
            FiscalYearConfig(
                company_id=1,
                fiscal_year=2026,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 1),
            )

    def test_marks_current(self):
        fy = FiscalYearConfig(
            company_id=1,
            fiscal_year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        assert fy.is_current is True

    def test_marks_closed(self):
        fy = FiscalYearConfig(
            company_id=1,
            fiscal_year=2025,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_closed=True,
        )
        assert fy.is_closed is True


class TestFiscalYearCreate:
    def test_valid_create(self):
        req = FiscalYearCreate(
            fiscal_year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        assert req.fiscal_year == 2026

    def test_rejects_invalid_range(self):
        with pytest.raises(VASValidationError):
            FiscalYearCreate(
                fiscal_year=2026,
                start_date=date(2026, 12, 31),
                end_date=date(2026, 1, 1),
            )


class TestNumberingRule:
    def test_create_valid_rule(self):
        rule = NumberingRule(
            company_id=1,
            document_type=DocumentType.AR_INVOICE,
            prefix="HD",
            next_number=1,
            pad_length=7,
            fiscal_year=2026,
        )
        assert rule.company_id == 1
        assert rule.document_type == DocumentType.AR_INVOICE
        assert rule.prefix == "HD"
        assert rule.next_number == 1
        assert rule.pad_length == 7

    def test_default_values(self):
        rule = NumberingRule(
            company_id=1,
            document_type=DocumentType.JOURNAL_ENTRY,
            fiscal_year=2026,
        )
        assert rule.prefix == ""
        assert rule.suffix == ""
        assert rule.next_number == 1
        assert rule.pad_length == 6

    def test_rejects_pad_length_zero(self):
        with pytest.raises((VASValidationError, PydanticValidationError)):
            NumberingRule(
                company_id=1,
                document_type=DocumentType.AR_INVOICE,
                fiscal_year=2026,
                pad_length=0,
            )

    def test_rejects_negative_next_number(self):
        with pytest.raises((VASValidationError, PydanticValidationError)):
            NumberingRule(
                company_id=1,
                document_type=DocumentType.AR_INVOICE,
                fiscal_year=2026,
                next_number=-1,
            )

    def test_all_document_types(self):
        for dt in DocumentType:
            rule = NumberingRule(
                company_id=1,
                document_type=dt,
                fiscal_year=2026,
            )
            assert rule.document_type == dt


class TestNumberingRuleUpdate:
    def test_all_optional(self):
        req = NumberingRuleUpdate()
        data = req.model_dump(exclude_none=True)
        assert data == {}

    def test_partial(self):
        req = NumberingRuleUpdate(prefix="INV", pad_length=8)
        data = req.model_dump(exclude_none=True)
        assert data["prefix"] == "INV"
        assert data["pad_length"] == 8


class TestSetupChecklistItem:
    def test_create_valid_item(self):
        item = SetupChecklistItem(
            company_id=1,
            section=SetupSection.COMPANY_INFO,
            label="Thông tin công ty",
            sort_order=1,
        )
        assert item.company_id == 1
        assert item.section == SetupSection.COMPANY_INFO
        assert item.label == "Thông tin công ty"
        assert item.is_completed is False
        assert item.sort_order == 1

    def test_marks_completed(self):
        item = SetupChecklistItem(
            company_id=1,
            section=SetupSection.COA,
            label="Hệ thống tài khoản",
            is_completed=True,
            sort_order=4,
        )
        assert item.is_completed is True

    def test_rejects_empty_label(self):
        with pytest.raises(VASValidationError):
            SetupChecklistItem(
                company_id=1,
                section=SetupSection.FISCAL_YEAR,
                label="",
                sort_order=2,
            )

    def test_all_sections(self):
        for section in SetupSection:
            item = SetupChecklistItem(
                company_id=1,
                section=section,
                label=f"Section {section.value}",
                sort_order=0,
            )
            assert item.section == section


class TestDocumentType:
    def test_enum_values(self):
        assert DocumentType.AR_INVOICE.value == "ar_invoice"
        assert DocumentType.AP_INVOICE.value == "ap_invoice"
        assert DocumentType.JOURNAL_ENTRY.value == "journal_entry"
        assert DocumentType.PAYMENT.value == "payment"
        assert DocumentType.RECEIPT.value == "receipt"

    def test_11_types(self):
        assert len(DocumentType) == 11


class TestSetupSection:
    def test_enum_values(self):
        assert SetupSection.COMPANY_INFO.value == "company_info"
        assert SetupSection.FISCAL_YEAR.value == "fiscal_year"
        assert SetupSection.USER_PERMISSIONS.value == "user_permissions"

    def test_13_sections(self):
        assert len(SetupSection) == 13
