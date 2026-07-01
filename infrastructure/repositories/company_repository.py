import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from domain.company import (
    Company, CompanyCreate, CompanyUpdate,
    FiscalYearConfig, FiscalYearCreate,
    NumberingRule, NumberingRuleUpdate,
    SetupChecklistItem, SetupSection, DocumentType,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result
from infrastructure.models.company_models import (
    CompanyModel, FiscalYearConfigModel, NumberingRuleModel,
    SetupChecklistItemModel,
    CompDocumentTypeDB, SetupSectionDB,
)

logger = logging.getLogger(__name__)


class CompanyRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Company CRUD ─────────────────────────────────────────────────

    def create(self, company: CompanyCreate) -> Result:
        existing = self.session.query(CompanyModel).filter(
            CompanyModel.is_active.is_(True)
        ).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.COMPANY_ALREADY_EXISTS))

        model = CompanyModel(
            name=company.name,
            tax_code=company.tax_code,
            address=company.address,
            phone=company.phone,
            email=company.email,
            website=company.website,
            business_reg_number=company.business_reg_number,
            date_format=company.date_format,
            currency_code=company.currency_code,
            fiscal_year_start_month=company.fiscal_year_start_month,
            accounting_regime=company.accounting_regime,
            locale=company.locale,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, company_id: int) -> Optional[Company]:
        model = self.session.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        return self._model_to_domain(model) if model else None

    def get_active(self) -> Optional[Company]:
        model = self.session.query(CompanyModel).filter(
            CompanyModel.is_active.is_(True)
        ).first()
        return self._model_to_domain(model) if model else None

    def list(self) -> List[Company]:
        models = self.session.query(CompanyModel).order_by(CompanyModel.id).all()
        return [self._model_to_domain(m) for m in models]

    def update(self, company_id: int, updates: CompanyUpdate) -> Result:
        model = self.session.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.COMPANY_NOT_FOUND))
        update_data = updates.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def delete(self, company_id: int) -> Result:
        model = self.session.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.COMPANY_NOT_FOUND))
        model.is_active = False
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(None)

    # ── Fiscal Year CRUD ────────────────────────────────────────────

    def create_fiscal_year(self, fy: FiscalYearConfig) -> Result:
        existing = self.session.query(FiscalYearConfigModel).filter(
            and_(
                FiscalYearConfigModel.company_id == fy.company_id,
                FiscalYearConfigModel.fiscal_year == fy.fiscal_year,
            )
        ).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.FISCAL_YEAR_EXISTS))

        overlap = self.session.query(FiscalYearConfigModel).filter(
            FiscalYearConfigModel.company_id == fy.company_id,
            or_(
                and_(
                    FiscalYearConfigModel.start_date <= fy.start_date,
                    FiscalYearConfigModel.end_date > fy.start_date,
                ),
                and_(
                    FiscalYearConfigModel.start_date < fy.end_date,
                    FiscalYearConfigModel.end_date >= fy.end_date,
                ),
                and_(
                    FiscalYearConfigModel.start_date >= fy.start_date,
                    FiscalYearConfigModel.end_date <= fy.end_date,
                ),
            ),
        ).first()
        if overlap:
            return Result.failure(VASValidationError(ErrorCodes.FISCAL_YEAR_OVERLAP))

        model = FiscalYearConfigModel(
            company_id=fy.company_id,
            fiscal_year=fy.fiscal_year,
            start_date=fy.start_date,
            end_date=fy.end_date,
            is_closed=fy.is_closed,
            is_current=fy.is_current,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fy_model_to_domain(model))

    def get_fiscal_year(self, company_id: int, fiscal_year: int) -> Optional[FiscalYearConfig]:
        model = self.session.query(FiscalYearConfigModel).filter(
            and_(
                FiscalYearConfigModel.company_id == company_id,
                FiscalYearConfigModel.fiscal_year == fiscal_year,
            )
        ).first()
        return self._fy_model_to_domain(model) if model else None

    def list_fiscal_years(self, company_id: int) -> List[FiscalYearConfig]:
        models = self.session.query(FiscalYearConfigModel).filter(
            FiscalYearConfigModel.company_id == company_id
        ).order_by(FiscalYearConfigModel.fiscal_year.desc()).all()
        return [self._fy_model_to_domain(m) for m in models]

    def close_fiscal_year(self, company_id: int, fiscal_year: int) -> Result:
        model = self.session.query(FiscalYearConfigModel).filter(
            and_(
                FiscalYearConfigModel.company_id == company_id,
                FiscalYearConfigModel.fiscal_year == fiscal_year,
            )
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.FISCAL_YEAR_NOT_FOUND))
        if model.is_closed:
            return Result.failure(VASValidationError(ErrorCodes.FISCAL_YEAR_ALREADY_CLOSED))
        model.is_closed = True
        if model.is_current:
            model.is_current = False
        self.session.flush()
        return Result.success(self._fy_model_to_domain(model))

    def get_current_fiscal_year(self, company_id: int) -> Optional[FiscalYearConfig]:
        model = self.session.query(FiscalYearConfigModel).filter(
            and_(
                FiscalYearConfigModel.company_id == company_id,
                FiscalYearConfigModel.is_current.is_(True),
            )
        ).first()
        if not model:
            model = self.session.query(FiscalYearConfigModel).filter(
                FiscalYearConfigModel.company_id == company_id
            ).order_by(FiscalYearConfigModel.fiscal_year.desc()).first()
        return self._fy_model_to_domain(model) if model else None

    # ── Numbering Rules CRUD ────────────────────────────────────────

    def create_numbering_rule(self, rule: NumberingRule) -> Result:
        existing = self.session.query(NumberingRuleModel).filter(
            and_(
                NumberingRuleModel.company_id == rule.company_id,
                NumberingRuleModel.document_type == CompDocumentTypeDB(rule.document_type.value),
                NumberingRuleModel.fiscal_year == rule.fiscal_year,
            )
        ).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.NUMBERING_RULE_DUPLICATE))

        model = NumberingRuleModel(
            company_id=rule.company_id,
            document_type=CompDocumentTypeDB(rule.document_type.value),
            prefix=rule.prefix,
            suffix=rule.suffix,
            next_number=rule.next_number,
            pad_length=rule.pad_length,
            fiscal_year=rule.fiscal_year,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._nr_model_to_domain(model))

    def get_numbering_rule(self, company_id: int, document_type: DocumentType,
                           fiscal_year: int) -> Optional[NumberingRule]:
        model = self.session.query(NumberingRuleModel).filter(
            and_(
                NumberingRuleModel.company_id == company_id,
                NumberingRuleModel.document_type == CompDocumentTypeDB(document_type.value),
                NumberingRuleModel.fiscal_year == fiscal_year,
            )
        ).first()
        return self._nr_model_to_domain(model) if model else None

    def get_next_document_number(self, company_id: int, document_type: DocumentType,
                                 fiscal_year: int) -> Result:
        model = self.session.query(NumberingRuleModel).filter(
            and_(
                NumberingRuleModel.company_id == company_id,
                NumberingRuleModel.document_type == CompDocumentTypeDB(document_type.value),
                NumberingRuleModel.fiscal_year == fiscal_year,
            )
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.NUMBERING_RULE_NOT_FOUND))

        current_number = model.next_number
        model.next_number += 1
        self.session.flush()

        padded = str(current_number).zfill(model.pad_length)
        formatted = f"{model.prefix}{padded}{model.suffix}"
        return Result.success({
            "number": formatted,
            "sequence": current_number,
        })

    def list_numbering_rules(self, company_id: int,
                             document_type: Optional[DocumentType] = None,
                             fiscal_year: Optional[int] = None) -> List[NumberingRule]:
        query = self.session.query(NumberingRuleModel).filter(
            NumberingRuleModel.company_id == company_id
        )
        if document_type is not None:
            query = query.filter(NumberingRuleModel.document_type == CompDocumentTypeDB(document_type.value))
        if fiscal_year is not None:
            query = query.filter(NumberingRuleModel.fiscal_year == fiscal_year)
        models = query.order_by(NumberingRuleModel.document_type).all()
        return [self._nr_model_to_domain(m) for m in models]

    def update_numbering_rule(self, company_id: int, rule_id: int,
                              updates: NumberingRuleUpdate) -> Result:
        model = self.session.query(NumberingRuleModel).filter(
            and_(
                NumberingRuleModel.id == rule_id,
                NumberingRuleModel.company_id == company_id,
            )
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.NUMBERING_RULE_NOT_FOUND))
        update_data = updates.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(model, key, value)
        self.session.flush()
        return Result.success(self._nr_model_to_domain(model))

    def reset_numbering_sequence(self, company_id: int, document_type: DocumentType,
                                 fiscal_year: int, start_from: int) -> Result:
        model = self.session.query(NumberingRuleModel).filter(
            and_(
                NumberingRuleModel.company_id == company_id,
                NumberingRuleModel.document_type == CompDocumentTypeDB(document_type.value),
                NumberingRuleModel.fiscal_year == fiscal_year,
            )
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.NUMBERING_RULE_NOT_FOUND))
        model.next_number = start_from
        self.session.flush()
        return Result.success(self._nr_model_to_domain(model))

    # ── Setup Checklist CRUD ────────────────────────────────────────

    def create_setup_checklist_item(self, item: SetupChecklistItem) -> Result:
        existing = self.session.query(SetupChecklistItemModel).filter(
            and_(
                SetupChecklistItemModel.company_id == item.company_id,
                SetupChecklistItemModel.section == SetupSectionDB(item.section.value),
            )
        ).first()
        if existing:
            existing.is_completed = item.is_completed
            existing.sort_order = item.sort_order
            self.session.flush()
            return Result.success(self._sc_model_to_domain(existing))

        model = SetupChecklistItemModel(
            company_id=item.company_id,
            section=SetupSectionDB(item.section.value),
            label=item.label,
            is_completed=item.is_completed,
            sort_order=item.sort_order,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._sc_model_to_domain(model))

    def get_setup_checklist(self, company_id: int) -> List[SetupChecklistItem]:
        models = self.session.query(SetupChecklistItemModel).filter(
            SetupChecklistItemModel.company_id == company_id
        ).order_by(SetupChecklistItemModel.sort_order).all()
        return [self._sc_model_to_domain(m) for m in models]

    def get_setup_progress(self, company_id: int) -> Result:
        items = self.session.query(SetupChecklistItemModel).filter(
            SetupChecklistItemModel.company_id == company_id
        ).all()
        if not items:
            return Result.success({"completed": 0, "total": 0, "percentage": 0.0})
        total = len(items)
        completed = sum(1 for i in items if i.is_completed)
        percentage = round((completed / total) * 100, 1)
        return Result.success({
            "completed": completed,
            "total": total,
            "percentage": percentage,
        })

    def mark_setup_item_complete(self, company_id: int, section: SetupSection) -> Result:
        model = self.session.query(SetupChecklistItemModel).filter(
            and_(
                SetupChecklistItemModel.company_id == company_id,
                SetupChecklistItemModel.section == SetupSectionDB(section.value),
            )
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.SETUP_SECTION_NOT_FOUND))
        if model.is_completed:
            return Result.failure(VASValidationError(ErrorCodes.SETUP_ITEM_ALREADY_COMPLETE))
        model.is_completed = True
        self.session.flush()
        return Result.success(self._sc_model_to_domain(model))

    def get_setup_item(self, company_id: int, section: SetupSection) -> Optional[SetupChecklistItem]:
        model = self.session.query(SetupChecklistItemModel).filter(
            and_(
                SetupChecklistItemModel.company_id == company_id,
                SetupChecklistItemModel.section == SetupSectionDB(section.value),
            )
        ).first()
        return self._sc_model_to_domain(model) if model else None

    # ── Model ↔ Domain mappers ──────────────────────────────────────

    def _model_to_domain(self, model: CompanyModel) -> Company:
        return Company(
            id=model.id,
            name=model.name,
            tax_code=model.tax_code,
            address=model.address,
            phone=model.phone,
            email=model.email,
            website=model.website,
            logo_url=model.logo_url,
            business_reg_number=model.business_reg_number,
            date_format=model.date_format,
            currency_code=model.currency_code,
            fiscal_year_start_month=model.fiscal_year_start_month,
            accounting_regime=model.accounting_regime,
            locale=model.locale,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _fy_model_to_domain(self, model: FiscalYearConfigModel) -> FiscalYearConfig:
        return FiscalYearConfig(
            id=model.id,
            company_id=model.company_id,
            fiscal_year=model.fiscal_year,
            start_date=model.start_date,
            end_date=model.end_date,
            is_closed=model.is_closed,
            is_current=model.is_current,
        )

    def _nr_model_to_domain(self, model: NumberingRuleModel) -> NumberingRule:
        return NumberingRule(
            id=model.id,
            company_id=model.company_id,
            document_type=DocumentType(model.document_type.value if hasattr(model.document_type, 'value') else model.document_type),
            prefix=model.prefix,
            suffix=model.suffix,
            next_number=model.next_number,
            pad_length=model.pad_length,
            fiscal_year=model.fiscal_year,
        )

    def _sc_model_to_domain(self, model: SetupChecklistItemModel) -> SetupChecklistItem:
        return SetupChecklistItem(
            id=model.id,
            company_id=model.company_id,
            section=SetupSection(model.section.value if hasattr(model.section, 'value') else model.section),
            label=model.label,
            is_completed=model.is_completed,
            sort_order=model.sort_order,
        )
