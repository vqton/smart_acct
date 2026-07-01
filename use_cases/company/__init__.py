import logging
from datetime import datetime, date, timezone
from typing import Any, Dict, List, Optional, Tuple

from domain.company import (
    Company, CompanyCreate, CompanyUpdate,
    FiscalYearConfig, FiscalYearCreate,
    NumberingRule, NumberingRuleUpdate,
    SetupChecklistItem, SetupSection, DocumentType,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.repositories.company_repository import CompanyRepository

logger = logging.getLogger(__name__)

DEFAULT_SETUP_SECTIONS = [
    (SetupSection.COMPANY_INFO, "Thông tin công ty", 1),
    (SetupSection.FISCAL_YEAR, "Năm tài chính", 2),
    (SetupSection.CURRENCY, "Tiền tệ hạch toán", 3),
    (SetupSection.COA, "Hệ thống tài khoản", 4),
    (SetupSection.OPENING_BALANCES, "Số dư đầu kỳ", 5),
    (SetupSection.DEPARTMENTS, "Phòng ban", 6),
    (SetupSection.WAREHOUSES, "Kho hàng", 7),
    (SetupSection.EMPLOYEES, "Nhân viên", 8),
    (SetupSection.CUSTOMERS, "Khách hàng", 9),
    (SetupSection.VENDORS, "Nhà cung cấp", 10),
    (SetupSection.TAX_RATES, "Thuế suất", 11),
    (SetupSection.NUMBERING_RULES, "Quy tắc đánh số", 12),
    (SetupSection.USER_PERMISSIONS, "Người dùng và phân quyền", 13),
]

DEFAULT_NUMBERING_RULES = [
    (DocumentType.AR_INVOICE, "HD", "", 1, 7),
    (DocumentType.AP_INVOICE, "HDM", "", 1, 7),
    (DocumentType.CASH_RECEIPT, "PT", "", 1, 7),
    (DocumentType.CASH_PAYMENT, "PC", "", 1, 7),
    (DocumentType.JOURNAL_ENTRY, "JV", "", 1, 6),
    (DocumentType.PURCHASE_ORDER, "PO", "", 1, 7),
    (DocumentType.SALES_ORDER, "SO", "", 1, 7),
    (DocumentType.INVENTORY_RECEIPT, "NK", "", 1, 7),
    (DocumentType.INVENTORY_ISSUE, "XK", "", 1, 7),
    (DocumentType.PAYMENT, "TT", "", 1, 7),
    (DocumentType.RECEIPT, "TH", "", 1, 7),
]


class CompanyUseCases:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_repo(self, session) -> CompanyRepository:
        return CompanyRepository(session)

    # ── UC-COMP-01: Create Company ───────────────────────────────────

    def create_company(self, req: CompanyCreate) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.create(req)
            if result.is_failure():
                session.rollback()
                return result

            company = result.get_data()

            # Auto-create current fiscal year
            current_year = datetime.now(timezone.utc).year
            fy_start = date(current_year, company.fiscal_year_start_month, 1)
            if company.fiscal_year_start_month == 1:
                fy_end = date(current_year, 12, 31)
            else:
                fy_end = date(current_year + 1, company.fiscal_year_start_month - 1, 1)

            from calendar import monthrange
            fy_end = fy_end.replace(day=monthrange(fy_end.year, fy_end.month)[1])

            fy_result = repo.create_fiscal_year(FiscalYearConfig(
                company_id=company.id,
                fiscal_year=current_year,
                start_date=fy_start,
                end_date=fy_end,
                is_current=True,
            ))
            if fy_result.is_failure():
                session.rollback()
                return fy_result

            # Auto-create default numbering rules
            for dt, prefix, suffix, next_num, pad in DEFAULT_NUMBERING_RULES:
                rule = NumberingRule(
                    company_id=company.id,
                    document_type=dt,
                    prefix=prefix,
                    suffix=suffix,
                    next_number=next_num,
                    pad_length=pad,
                    fiscal_year=current_year,
                )
                nr_result = repo.create_numbering_rule(rule)
                if nr_result.is_failure():
                    session.rollback()
                    return nr_result

            # Auto-create setup checklist
            for section, label, sort_order in DEFAULT_SETUP_SECTIONS:
                item = SetupChecklistItem(
                    company_id=company.id,
                    section=section,
                    label=label,
                    is_completed=False,
                    sort_order=sort_order,
                )
                sc_result = repo.create_setup_checklist_item(item)
                if sc_result.is_failure():
                    session.rollback()
                    return sc_result

            session.commit()
            return Result.success(company)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create company error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-02: Update Company ───────────────────────────────────

    def update_company(self, company_id: int, req: CompanyUpdate) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.update(company_id, req)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update company error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-03: Get Company ──────────────────────────────────────

    def get_company(self, company_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            company = repo.get_by_id(company_id)
            if not company:
                return Result.failure(VASValidationError(ErrorCodes.COMPANY_NOT_FOUND))
            session.close()
            return Result.success(self._company_to_dict(company))
        except Exception as e:
            logger.exception(f"Get company error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-04: Get Active Company ───────────────────────────────

    def get_active_company(self) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            company = repo.get_active()
            if not company:
                return Result.failure(VASValidationError(ErrorCodes.COMPANY_NOT_FOUND))
            session.close()
            return Result.success(self._company_to_dict(company))
        except Exception as e:
            logger.exception(f"Get active company error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-05: Create Fiscal Year ───────────────────────────────

    def create_fiscal_year(self, company_id: int, req: FiscalYearCreate) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            fy = FiscalYearConfig(
                company_id=company_id,
                fiscal_year=req.fiscal_year,
                start_date=req.start_date,
                end_date=req.end_date,
                is_current=req.is_current,
            )

            if req.is_current:
                current_fy = repo.get_current_fiscal_year(company_id)
                if current_fy and not current_fy.is_closed:
                    current_fy_closed = repo.close_fiscal_year(company_id, current_fy.fiscal_year)
                    if current_fy_closed.is_failure():
                        session.rollback()
                        return current_fy_closed

            result = repo.create_fiscal_year(fy)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create fiscal year error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-06: List Fiscal Years ────────────────────────────────

    def list_fiscal_years(self, company_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            years = repo.list_fiscal_years(company_id)
            session.close()
            return Result.success([{
                "id": y.id,
                "company_id": y.company_id,
                "fiscal_year": y.fiscal_year,
                "start_date": y.start_date.isoformat(),
                "end_date": y.end_date.isoformat(),
                "is_closed": y.is_closed,
                "is_current": y.is_current,
            } for y in years])
        except Exception as e:
            logger.exception(f"List fiscal years error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-07: Close Fiscal Year ────────────────────────────────

    def close_fiscal_year(self, company_id: int, fiscal_year: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.close_fiscal_year(company_id, fiscal_year)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Close fiscal year error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-08: Get Numbering Rule ───────────────────────────────

    def get_numbering_rule(self, company_id: int, document_type: DocumentType,
                           fiscal_year: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            rule = repo.get_numbering_rule(company_id, document_type, fiscal_year)
            if not rule:
                return Result.failure(VASValidationError(ErrorCodes.NUMBERING_RULE_NOT_FOUND))
            session.close()
            return Result.success(self._nr_to_dict(rule))
        except Exception as e:
            logger.exception(f"Get numbering rule error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    def list_numbering_rules(self, company_id: int,
                             document_type: Optional[DocumentType] = None,
                             fiscal_year: Optional[int] = None) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            rules = repo.list_numbering_rules(company_id, document_type, fiscal_year)
            session.close()
            return Result.success([self._nr_to_dict(r) for r in rules])
        except Exception as e:
            logger.exception(f"List numbering rules error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-09: Get Next Number ──────────────────────────────────

    def get_next_number(self, company_id: int, document_type: DocumentType,
                        fiscal_year: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.get_next_document_number(company_id, document_type, fiscal_year)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Get next number error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-10: Update Numbering Rule ────────────────────────────

    def update_numbering_rule(self, company_id: int, rule_id: int,
                              req: NumberingRuleUpdate) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.update_numbering_rule(company_id, rule_id, req)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update numbering rule error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── UC-COMP-11: Setup Checklist ──────────────────────────────────

    def get_setup_checklist(self, company_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            items = repo.get_setup_checklist(company_id)
            progress = repo.get_setup_progress(company_id)
            session.close()
            return Result.success({
                "items": [self._sc_to_dict(i) for i in items],
                "progress": progress.get_data() if progress.is_success() else {},
            })
        except Exception as e:
            logger.exception(f"Get setup checklist error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    def mark_setup_complete(self, company_id: int, section: SetupSection) -> Result:
        session = self._session_factory()
        try:
            repo = self._get_repo(session)
            result = repo.mark_setup_item_complete(company_id, section)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Mark setup complete error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.CANNOT_GET_DATA_FAILED))
        finally:
            session.close()

    # ── Helpers ──────────────────────────────────────────────────────

    def _company_to_dict(self, company: Company) -> dict:
        return {
            "id": company.id,
            "name": company.name,
            "tax_code": company.tax_code,
            "address": company.address,
            "phone": company.phone,
            "email": company.email,
            "website": company.website,
            "logo_url": company.logo_url,
            "business_reg_number": company.business_reg_number,
            "date_format": company.date_format,
            "currency_code": company.currency_code,
            "fiscal_year_start_month": company.fiscal_year_start_month,
            "accounting_regime": company.accounting_regime,
            "locale": company.locale,
            "is_active": company.is_active,
            "created_at": company.created_at.isoformat() if company.created_at else None,
            "updated_at": company.updated_at.isoformat() if company.updated_at else None,
        }

    def _nr_to_dict(self, rule: NumberingRule) -> dict:
        return {
            "id": rule.id,
            "company_id": rule.company_id,
            "document_type": rule.document_type.value if hasattr(rule.document_type, 'value') else rule.document_type,
            "prefix": rule.prefix,
            "suffix": rule.suffix,
            "next_number": rule.next_number,
            "pad_length": rule.pad_length,
            "fiscal_year": rule.fiscal_year,
        }

    def _sc_to_dict(self, item: SetupChecklistItem) -> dict:
        return {
            "id": item.id,
            "company_id": item.company_id,
            "section": item.section.value if hasattr(item.section, 'value') else item.section,
            "label": item.label,
            "is_completed": item.is_completed,
            "sort_order": item.sort_order,
        }
