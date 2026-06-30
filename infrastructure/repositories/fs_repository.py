from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_

from domain import (
    FinancialStatement, FSLineItem, FSStatus, FinancialStatementType,
    FSAuditLog, FSAccountMapping, FSCashFlowMethod,
    FSConsolidationGroup, FSConsolidationMember,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError
from infrastructure.models.fs_models import (
    FSStatementModel, FSLineItemModel, FSAuditLogModel,
    FSAccountMappingModel, FSStatementTypeDB, FSStatusDB,
    FSCashFlowMethodDB, FSConsolidationGroupModel, FSConsolidationMemberModel,
)
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel
from infrastructure.models.coa_models import COAModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _domain_type_to_db(st: FinancialStatementType) -> FSStatementTypeDB:
    return FSStatementTypeDB(st.value)


def _db_to_domain_type(st: FSStatementTypeDB) -> FinancialStatementType:
    return FinancialStatementType(st.value)


def _domain_status_to_db(st: FSStatus) -> FSStatusDB:
    return FSStatusDB(st.value)


def _db_to_domain_status(st: FSStatusDB) -> FSStatus:
    return FSStatus(st.value)


class FSRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Mapping helpers ──────────────────────────────────────────────

    def _line_to_domain(self, m: FSLineItemModel) -> FSLineItem:
        return FSLineItem(
            id=m.id, fs_id=m.fs_id, ma_so=m.ma_so, ten_chi_tieu=m.ten_chi_tieu,
            so_thu_tu=m.so_thu_tu, parent_ma_so=m.parent_ma_so,
            current_year=m.current_year, previous_year=m.previous_year,
            is_subtotal=m.is_subtotal, is_calculated=m.is_calculated,
            calculation_formula=m.calculation_formula, thuyet_minh=m.thuyet_minh,
        )

    def _line_to_model(self, fs_id: int, d: FSLineItem) -> FSLineItemModel:
        return FSLineItemModel(
            fs_id=fs_id, ma_so=d.ma_so, ten_chi_tieu=d.ten_chi_tieu,
            so_thu_tu=d.so_thu_tu, parent_ma_so=d.parent_ma_so,
            current_year=d.current_year, previous_year=d.previous_year,
            is_subtotal=d.is_subtotal, is_calculated=d.is_calculated,
            calculation_formula=d.calculation_formula, thuyet_minh=d.thuyet_minh,
        )

    def _statement_to_domain(self, m: FSStatementModel) -> FinancialStatement:
        lines = [self._line_to_domain(l) for l in m.lines]
        fs = FinancialStatement(
            entity_id=m.entity_id, period=m.period,
            statement_type=_db_to_domain_type(m.statement_type),
            status=_db_to_domain_status(m.status),
            version=m.version,
            cash_flow_method=FSCashFlowMethod(m.cash_flow_method.value) if m.cash_flow_method else None,
            approved_by=m.approved_by, approval_date=m.approval_date,
            signed_by=m.signed_by, signed_date=m.signed_date,
            generated_by=m.generated_by, generated_at=m.generated_at,
            is_consolidated=m.is_consolidated,
            consolidation_group_id=m.consolidation_group_id,
            notes=m.notes, lines=lines,
            created_at=m.created_at, updated_at=m.updated_at,
        )
        fs.id = m.id
        return fs

    def _statement_to_model(self, d: FinancialStatement) -> FSStatementModel:
        return FSStatementModel(
            entity_id=d.entity_id, period=d.period,
            statement_type=_domain_type_to_db(d.statement_type),
            status=_domain_status_to_db(d.status),
            version=d.version,
            cash_flow_method=FSCashFlowMethodDB(d.cash_flow_method.value) if d.cash_flow_method else None,
            approved_by=d.approved_by, approval_date=d.approval_date,
            signed_by=d.signed_by, signed_date=d.signed_date,
            generated_by=d.generated_by, generated_at=d.generated_at,
            is_consolidated=d.is_consolidated,
            consolidation_group_id=d.consolidation_group_id,
            notes=d.notes,
        )

    # ── FS statement CRUD ───────────────────────────────────────────

    def create_statement(self, fs: FinancialStatement) -> Result:
        model = self._statement_to_model(fs)
        self.session.add(model)
        self.session.flush()

        for line in fs.lines:
            line_model = self._line_to_model(model.id, line)
            self.session.add(line_model)

        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._statement_to_domain(model))

    def get_statement(self, fs_id: int) -> Optional[FinancialStatement]:
        model = self.session.get(FSStatementModel, fs_id)
        return self._statement_to_domain(model) if model else None

    def list_statements(
        self,
        period: Optional[str] = None,
        statement_type: Optional[FinancialStatementType] = None,
        status: Optional[FSStatus] = None,
        entity_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[FinancialStatement]:
        stmt = select(FSStatementModel)
        if period:
            stmt = stmt.where(FSStatementModel.period == period)
        if statement_type:
            stmt = stmt.where(FSStatementModel.statement_type == _domain_type_to_db(statement_type))
        if status:
            stmt = stmt.where(FSStatementModel.status == _domain_status_to_db(status))
        if entity_id is not None:
            stmt = stmt.where(FSStatementModel.entity_id == entity_id)
        stmt = stmt.order_by(FSStatementModel.period.desc(), FSStatementModel.id.desc())
        stmt = stmt.limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().unique().all()
        return [self._statement_to_domain(m) for m in models]

    def update_statement_status(self, fs_id: int, status: FSStatus, user: str,
                                 reason: Optional[str] = None) -> Result:
        model = self.session.get(FSStatementModel, fs_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.FS_NOT_FOUND))

        current = _db_to_domain_status(model.status)
        if status not in FinancialStatement.VALID_TRANSITIONS.get(current, []):
            return Result.failure(ValidationError(
                ErrorCodes.FS_INVALID_TRANSITION,
                current=current.value, target=status.value,
            ))

        model.status = _domain_status_to_db(status)
        if status == FSStatus.APPROVED:
            model.approved_by = user
            model.approval_date = date.today()
        elif status == FSStatus.SIGNED:
            model.signed_by = user
            model.signed_date = date.today()

        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()

        log = FSAuditLogModel(fs_id=fs_id, action=status.value, user=user,
                               details=reason, version=model.version)
        self.session.add(log)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._statement_to_domain(model))

    def increment_version(self, fs_id: int) -> Result:
        model = self.session.get(FSStatementModel, fs_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.FS_NOT_FOUND))
        model.version += 1
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._statement_to_domain(model))

    def delete_statement(self, fs_id: int) -> Result:
        model = self.session.get(FSStatementModel, fs_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.FS_NOT_FOUND))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── Line items ───────────────────────────────────────────────────

    def update_line_items(self, fs_id: int, lines: List[FSLineItem]) -> Result:
        model = self.session.get(FSStatementModel, fs_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.FS_NOT_FOUND))
        self.session.query(FSLineItemModel).filter(FSLineItemModel.fs_id == fs_id).delete()
        for idx, line in enumerate(lines):
            lm = self._line_to_model(fs_id, line)
            lm.so_thu_tu = idx + 1
            self.session.add(lm)
        self.session.flush()
        return Result.success(None)

    # ── Audit log ────────────────────────────────────────────────────

    def log_audit(self, fs_id: int, action: str, user: str,
                   details: Optional[str] = None, version: int = 1):
        log = FSAuditLogModel(fs_id=fs_id, action=action, user=user,
                               details=details, version=version)
        self.session.add(log)
        self.session.flush()

    def get_audit_log(self, fs_id: int) -> List[Dict[str, Any]]:
        models = self.session.execute(
            select(FSAuditLogModel).where(FSAuditLogModel.fs_id == fs_id)
            .order_by(FSAuditLogModel.timestamp.asc())
        ).scalars().all()
        return [
            {"id": m.id, "fs_id": m.fs_id, "action": m.action,
             "user": m.user, "timestamp": m.timestamp.isoformat(),
             "details": m.details, "version": m.version}
            for m in models
        ]

    # ── Account mapping CRUD ─────────────────────────────────────────

    def create_mapping(self, mapping: FSAccountMapping) -> Result:
        existing = self.session.execute(
            select(FSAccountMappingModel).where(
                FSAccountMappingModel.account_code == mapping.account_code,
                FSAccountMappingModel.fs_ma_so == mapping.fs_ma_so,
                FSAccountMappingModel.statement_type == _domain_type_to_db(mapping.statement_type),
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.FS_MAPPING_ALREADY_EXISTS))
        model = FSAccountMappingModel(
            fs_ma_so=mapping.fs_ma_so, account_code=mapping.account_code,
            weight=mapping.weight, direction=mapping.direction,
            statement_type=_domain_type_to_db(mapping.statement_type),
        )
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        mapping.id = model.id
        return Result.success(mapping)

    def get_mappings(self, statement_type: Optional[FinancialStatementType] = None,
                     fs_ma_so: Optional[str] = None) -> List[FSAccountMapping]:
        stmt = select(FSAccountMappingModel)
        if statement_type:
            stmt = stmt.where(FSAccountMappingModel.statement_type == _domain_type_to_db(statement_type))
        if fs_ma_so:
            stmt = stmt.where(FSAccountMappingModel.fs_ma_so == fs_ma_so)
        models = self.session.execute(stmt).scalars().all()
        return [
            FSAccountMapping(
                id=m.id, fs_ma_so=m.fs_ma_so, account_code=m.account_code,
                weight=m.weight, direction=m.direction,
                statement_type=_db_to_domain_type(m.statement_type),
            )
            for m in models
        ]

    def delete_mapping(self, mapping_id: int) -> Result:
        model = self.session.get(FSAccountMappingModel, mapping_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.FS_MAPPING_NOT_FOUND))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def get_mapping_for_account(self, account_code: str,
                                 statement_type: FinancialStatementType) -> List[FSAccountMapping]:
        stmt = select(FSAccountMappingModel).where(
            FSAccountMappingModel.account_code == account_code,
            FSAccountMappingModel.statement_type == _domain_type_to_db(statement_type),
        )
        models = self.session.execute(stmt).scalars().all()
        return [
            FSAccountMapping(
                id=m.id, fs_ma_so=m.fs_ma_so, account_code=m.account_code,
                weight=m.weight, direction=m.direction,
                statement_type=_db_to_domain_type(m.statement_type),
            )
            for m in models
        ]

    # ── GL data aggregation ──────────────────────────────────────────

    def get_account_balance(self, account_id: str, period: Optional[str] = None) -> Decimal:
        stmt = select(
            func.coalesce(func.sum(JournalLineModel.debit), 0),
            func.coalesce(func.sum(JournalLineModel.credit), 0),
        ).where(
            JournalLineModel.account_id == account_id,
            JournalLineModel.journal_entry_id.in_(
                select(JournalEntryModel.id).where(JournalEntryModel.is_posted == True)
            )
        )
        if period:
            stmt = stmt.where(JournalLineModel.period == period)

        result = self.session.execute(stmt).one()
        total_debit = Decimal(str(result[0]))
        total_credit = Decimal(str(result[1]))

        account = self.session.execute(
            select(COAModel).where(COAModel.code == account_id)
        ).scalar_one_or_none()

        is_debit_normal = True
        if account:
            is_debit_normal = account.drcr_direction == "debit"

        if is_debit_normal:
            return _vnd(total_debit - total_credit)
        else:
            return _vnd(total_credit - total_debit)

    def get_trial_balance(self, period: str) -> Dict[str, Decimal]:
        posted_ids = select(JournalEntryModel.id).where(JournalEntryModel.is_posted == True)

        lines = self.session.execute(
            select(
                JournalLineModel.account_id,
                func.coalesce(func.sum(JournalLineModel.debit), 0),
                func.coalesce(func.sum(JournalLineModel.credit), 0),
            ).where(
                JournalLineModel.journal_entry_id.in_(posted_ids),
                JournalLineModel.period == period,
            ).group_by(JournalLineModel.account_id)
        ).all()

        result: Dict[str, Decimal] = {}
        for account_id, debit, credit in lines:
            total_debit = Decimal(str(debit))
            total_credit = Decimal(str(credit))

            account = self.session.execute(
                select(COAModel).where(COAModel.code == account_id)
            ).scalar_one_or_none()

            is_debit_normal = True
            if account:
                is_debit_normal = account.drcr_direction == "debit"

            if is_debit_normal:
                result[account_id] = _vnd(total_debit - total_credit)
            else:
                result[account_id] = _vnd(total_credit - total_debit)

        return result

    def get_prior_period_fs(self, period: str, statement_type: FinancialStatementType,
                             entity_id: int = 1) -> Optional[FinancialStatement]:
        stmt = select(FSStatementModel).where(
            FSStatementModel.period < period,
            FSStatementModel.statement_type == _domain_type_to_db(statement_type),
            FSStatementModel.entity_id == entity_id,
            FSStatementModel.status.in_([FSStatusDB.APPROVED, FSStatusDB.SIGNED]),
        ).order_by(FSStatementModel.period.desc()).limit(1)
        model = self.session.execute(stmt).scalars().first()
        return self._statement_to_domain(model) if model else None

    def is_period_closed(self, period: str) -> bool:
        from infrastructure.models.gl_models import AccountingPeriodModel
        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        return model.is_closed if model else False

    # ── Consolidation group CRUD ─────────────────────────────────────

    def create_consolidation_group(self, group: FSConsolidationGroup) -> Result:
        model = FSConsolidationGroupModel(
            name=group.name, parent_entity_id=group.parent_entity_id,
            consolidation_method=group.consolidation_method,
        )
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        group.id = model.id
        return Result.success(group)

    def get_consolidation_group(self, group_id: int) -> Optional[FSConsolidationGroup]:
        model = self.session.get(FSConsolidationGroupModel, group_id)
        if not model:
            return None
        return FSConsolidationGroup(
            id=model.id, name=model.name,
            parent_entity_id=model.parent_entity_id,
            consolidation_method=model.consolidation_method,
            created_at=model.created_at,
        )
