from typing import Optional, List, Dict
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc

from domain import (
    JournalEntry, JournalLine, JournalType, JournalTypeSequence,
    SubsidiaryType, SubsidiaryLedger,
    Result, ValidationError, DoubleEntryError,
    AccountType, DCRDirection, JOURNAL_TYPE_PREFIX_MAP,
)
from infrastructure.models.gl_models import (
    JournalEntryModel, JournalLineModel, AccountingPeriodModel,
    PeriodAuditLogModel, PeriodType, JournalTypeSequenceModel,
    SubsidiaryLedgerModel,
)
from infrastructure.models.coa_models import COAModel
from infrastructure.models.tax_models import TaxDeclarationModel, DeclarationStatusDB
from domain.i18n import ErrorCodes


class GLRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Domain mapping helpers ──────────────────────────────────────────

    def _entry_to_domain(self, model: JournalEntryModel) -> JournalEntry:
        jt = JournalType.GENERAL
        if model.journal_type:
            try:
                jt = JournalType(model.journal_type)
            except ValueError:
                jt = JournalType.GENERAL

        entry = JournalEntry(
            journal_number=model.journal_number,
            journal_type=jt,
            transaction_date=model.transaction_date,
            description=model.description,
            is_posted=model.is_posted,
            posted_date=model.posted_date.date() if model.posted_date else None,
            period=model.period,
            source_module=model.source_module,
            created_by=model.created_by,
            approved_by=model.approved_by,
            is_approved=model.is_approved,
            approval_date=model.approval_date.date() if model.approval_date else None,
            correction_method=model.correction_method,
            ref_journal_number=model.ref_journal_number,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        entry.id = model.id
        entry.lines = [self._line_to_domain(l) for l in model.lines]
        return entry

    def _line_to_domain(self, model: JournalLineModel) -> JournalLine:
        line = JournalLine(
            id=model.id,
            journal_entry_id=model.journal_entry_id,
            account_id=model.account_id,
            debit=model.debit,
            credit=model.credit,
            description=model.description,
            vat_rate=model.vat_rate,
            line_type=model.line_type,
            is_taxable=model.is_taxable,
            tax_code=model.tax_code,
            period=model.period,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        return line

    def _line_to_model(self, entry_id: int, line: JournalLine) -> JournalLineModel:
        return JournalLineModel(
            journal_entry_id=entry_id,
            account_id=line.account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
            vat_rate=line.vat_rate,
            line_type=line.line_type,
            is_taxable=line.is_taxable,
            tax_code=line.tax_code,
            period=line.period,
        )

    def _entry_to_model(self, entry: JournalEntry) -> JournalEntryModel:
        return JournalEntryModel(
            journal_number=entry.journal_number,
            journal_type=entry.journal_type.value if entry.journal_type else "general",
            transaction_date=entry.transaction_date,
            description=entry.description,
            period=entry.period,
            is_posted=entry.is_posted,
            posted_date=entry.posted_date,
            source_module=entry.source_module,
            created_by=entry.created_by,
            approved_by=entry.approved_by,
            is_approved=entry.is_approved,
            approval_date=entry.approval_date,
            correction_method=entry.correction_method.value if entry.correction_method else None,
            ref_journal_number=entry.ref_journal_number,
        )

    # ── JournalEntry CRUD ───────────────────────────────────────────────

    def create_entry(self, entry: JournalEntry) -> Result:
        existing = self.session.execute(
            select(JournalEntryModel).where(JournalEntryModel.journal_number == entry.journal_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS, type="Journal entry", id=entry.journal_number))

        if self.is_period_closed(entry.period):
            return Result.failure(ValidationError(ErrorCodes.PERIOD_CLOSED_OP, period=entry.period, action="create journal entry"))

        model = self._entry_to_model(entry)
        self.session.add(model)
        self.session.flush()

        for line in entry.lines:
            line_model = self._line_to_model(model.id, line)
            self.session.add(line_model)

        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._entry_to_domain(model))

    def get_entry(self, entry_id: int) -> Optional[JournalEntry]:
        model = self.session.get(JournalEntryModel, entry_id)
        return self._entry_to_domain(model) if model else None

    def get_entry_by_number(self, journal_number: str) -> Optional[JournalEntry]:
        model = self.session.execute(
            select(JournalEntryModel).where(JournalEntryModel.journal_number == journal_number)
        ).scalar_one_or_none()
        return self._entry_to_domain(model) if model else None

    def list_entries(
        self,
        period: Optional[str] = None,
        is_posted: Optional[bool] = None,
        account_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        stmt = select(JournalEntryModel)
        if period:
            stmt = stmt.where(JournalEntryModel.period == period)
        if is_posted is not None:
            stmt = stmt.where(JournalEntryModel.is_posted == is_posted)
        if from_date:
            stmt = stmt.where(JournalEntryModel.transaction_date >= from_date)
        if to_date:
            stmt = stmt.where(JournalEntryModel.transaction_date <= to_date)
        if account_id:
            stmt = stmt.join(JournalLineModel).where(JournalLineModel.account_id == account_id)

        stmt = stmt.order_by(JournalEntryModel.transaction_date.desc(), JournalEntryModel.id.desc())
        stmt = stmt.limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().unique().all()
        return [self._entry_to_domain(m) for m in models]

    def update_entry(self, entry_id: int, **kwargs) -> Result:
        model = self.session.get(JournalEntryModel, entry_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=entry_id))

        if model.is_posted:
            return Result.failure(ValidationError(ErrorCodes.CANNOT_UPDATE_POSTED, type="journal entry"))

        if self.is_period_closed(model.period):
            return Result.failure(ValidationError(ErrorCodes.PERIOD_CLOSED_OP, period=model.period, action="update journal entry"))

        allowed = {"description", "period", "source_module", "approved_by", "is_approved", "correction_method", "ref_journal_number"}
        for key, value in kwargs.items():
            if key not in allowed:
                return Result.failure(ValidationError(ErrorCodes.FIELD_CANNOT_BE_UPDATED, field=key))
            setattr(model, key, value)

        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._entry_to_domain(model))

    def delete_entry(self, entry_id: int) -> Result:
        model = self.session.get(JournalEntryModel, entry_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=entry_id))

        if model.is_posted:
            return Result.failure(ValidationError(ErrorCodes.CANNOT_DELETE_POSTED, type="journal entry"))

        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── Journal Type Sequence ──────────────────────────────────────────

    def get_or_create_sequence(self, journal_type: JournalType, fiscal_year: int) -> JournalTypeSequenceModel:
        seq = self.session.execute(
            select(JournalTypeSequenceModel).where(
                JournalTypeSequenceModel.journal_type == journal_type.value,
                JournalTypeSequenceModel.fiscal_year == fiscal_year,
            )
        ).scalar_one_or_none()

        if not seq:
            prefix = JOURNAL_TYPE_PREFIX_MAP.get(journal_type, "JV")
            seq = JournalTypeSequenceModel(
                journal_type=journal_type.value,
                fiscal_year=fiscal_year,
                last_sequence=0,
                prefix=prefix,
            )
            self.session.add(seq)
            self.session.flush()
        return seq

    def get_next_journal_number(self, journal_type: JournalType, period: str) -> str:
        parts = period.split("-")
        year = int(parts[0]) if parts[0].isdigit() else date.today().year
        seq = self.get_or_create_sequence(journal_type, year)
        seq.last_sequence += 1
        self.session.flush()
        prefix = JOURNAL_TYPE_PREFIX_MAP.get(journal_type, "JV")
        return f"{prefix}{year}{str(seq.last_sequence).zfill(6)}"

    def get_journal_sequence(self, journal_type: JournalType, fiscal_year: int) -> Optional[dict]:
        seq = self.session.execute(
            select(JournalTypeSequenceModel).where(
                JournalTypeSequenceModel.journal_type == journal_type.value,
                JournalTypeSequenceModel.fiscal_year == fiscal_year,
            )
        ).scalar_one_or_none()
        if not seq:
            return None
        return {
            "id": seq.id,
            "journal_type": seq.journal_type,
            "fiscal_year": seq.fiscal_year,
            "last_sequence": seq.last_sequence,
            "prefix": seq.prefix,
        }

    def list_journal_sequences(self, fiscal_year: Optional[int] = None) -> List[dict]:
        stmt = select(JournalTypeSequenceModel)
        if fiscal_year:
            stmt = stmt.where(JournalTypeSequenceModel.fiscal_year == fiscal_year)
        stmt = stmt.order_by(JournalTypeSequenceModel.journal_type)
        models = self.session.execute(stmt).scalars().all()
        return [
            {
                "id": s.id,
                "journal_type": s.journal_type,
                "fiscal_year": s.fiscal_year,
                "last_sequence": s.last_sequence,
                "prefix": s.prefix,
            }
            for s in models
        ]

    # ── Subsidiary Ledger ───────────────────────────────────────────

    def _subsidiary_to_domain(self, model: SubsidiaryLedgerModel) -> SubsidiaryLedger:
        st = SubsidiaryType.AR
        try:
            st = SubsidiaryType(model.subsidiary_type)
        except ValueError:
            pass
        return SubsidiaryLedger(
            id=model.id,
            subsidiary_type=st,
            account_code=model.account_code,
            entity_id=model.entity_id,
            entity_name=model.entity_name,
            transaction_date=model.transaction_date,
            doc_ref=model.doc_ref,
            doc_type=model.doc_type,
            description=model.description,
            debit=model.debit,
            credit=model.credit,
            balance=model.balance,
            period=model.period,
            journal_entry_id=model.journal_entry_id,
            created_at=model.created_at,
        )

    def create_subsidiary_entry(self, entry: SubsidiaryLedger) -> Result:
        model = SubsidiaryLedgerModel(
            subsidiary_type=entry.subsidiary_type.value if hasattr(entry.subsidiary_type, 'value') else str(entry.subsidiary_type),
            account_code=entry.account_code,
            entity_id=entry.entity_id,
            entity_name=entry.entity_name,
            transaction_date=entry.transaction_date,
            doc_ref=entry.doc_ref,
            doc_type=entry.doc_type,
            description=entry.description,
            debit=entry.debit,
            credit=entry.credit,
            balance=entry.balance,
            period=entry.period,
            journal_entry_id=entry.journal_entry_id,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._subsidiary_to_domain(model))

    def post_to_subsidiary_ledger(
        self, journal_entry_id: int, lines: List[JournalLineModel],
        subsidiary_type: str, entity_id: int, entity_name: str,
        doc_ref: str, doc_type: str, period: str, transaction_date: date,
    ) -> Result:
        """Post journal lines to subsidiary ledger, computing running balance."""
        try:
            st = SubsidiaryType(subsidiary_type)
        except ValueError:
            return Result.failure(ValidationError(ErrorCodes.SUBSIDIARY_TYPE_INVALID, subsidiary_type=subsidiary_type))

        for line in lines:
            last_balance = Decimal("0")
            last_entry = self.session.execute(
                select(SubsidiaryLedgerModel)
                .where(
                    SubsidiaryLedgerModel.subsidiary_type == st.value,
                    SubsidiaryLedgerModel.entity_id == entity_id,
                    SubsidiaryLedgerModel.account_code == line.account_id,
                )
                .order_by(desc(SubsidiaryLedgerModel.id))
                .limit(1)
            ).scalar_one_or_none()
            if last_entry:
                last_balance = last_entry.balance

            new_balance = last_balance + line.debit - line.credit
            sl = SubsidiaryLedger(
                subsidiary_type=st,
                account_code=line.account_id,
                entity_id=entity_id,
                entity_name=entity_name,
                transaction_date=transaction_date,
                doc_ref=doc_ref,
                doc_type=doc_type,
                description=line.description or f"Auto-post from JE #{journal_entry_id}",
                debit=line.debit,
                credit=line.credit,
                balance=new_balance,
                period=period,
                journal_entry_id=journal_entry_id,
            )
            sl = self.create_subsidiary_entry(sl)
            if sl.is_failure():
                return sl

        return Result.success(None)

    def get_subsidiary_ledger(
        self, subsidiary_type: str, entity_id: Optional[int] = None,
        period: Optional[str] = None, account_code: Optional[str] = None,
        limit: int = 100, offset: int = 0,
    ) -> List[SubsidiaryLedger]:
        stmt = select(SubsidiaryLedgerModel).where(
            SubsidiaryLedgerModel.subsidiary_type == subsidiary_type,
        )
        if entity_id is not None:
            stmt = stmt.where(SubsidiaryLedgerModel.entity_id == entity_id)
        if period:
            stmt = stmt.where(SubsidiaryLedgerModel.period == period)
        if account_code:
            stmt = stmt.where(SubsidiaryLedgerModel.account_code == account_code)
        stmt = stmt.order_by(SubsidiaryLedgerModel.transaction_date.asc(), SubsidiaryLedgerModel.id.asc())
        stmt = stmt.limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._subsidiary_to_domain(m) for m in models]

    def get_subsidiary_summary(
        self, subsidiary_type: str, period: str,
    ) -> List[dict]:
        """Get opening/closing balance per entity for a subsidiary type."""
        from sqlalchemy import text
        sql = text("""
            SELECT
                entity_id,
                entity_name,
                account_code,
                MIN(s.transaction_date) AS first_date,
                MAX(s.transaction_date) AS last_date,
                SUM(s.debit) AS total_debit,
                SUM(s.credit) AS total_credit,
                (
                    SELECT COALESCE(balance, 0)
                    FROM subsidiary_ledger b
                    WHERE b.subsidiary_type = s.subsidiary_type
                      AND b.entity_id = s.entity_id
                      AND b.account_code = s.account_code
                      AND b.id = (
                          SELECT MAX(b2.id)
                          FROM subsidiary_ledger b2
                          WHERE b2.subsidiary_type = s.subsidiary_type
                            AND b2.entity_id = s.entity_id
                            AND b2.account_code = s.account_code
                            AND b2.period = s.period
                      )
                ) AS closing_balance
            FROM subsidiary_ledger s
            WHERE s.subsidiary_type = :stype AND s.period = :period
            GROUP BY s.entity_id, s.entity_name, s.account_code, s.subsidiary_type
            ORDER BY s.entity_name
        """)
        rows = self.session.execute(sql, {"stype": subsidiary_type, "period": period}).fetchall()
        def _fmt_date(d):
            if d is None:
                return None
            if hasattr(d, 'isoformat'):
                return d.isoformat()
            return str(d)

        return [
            {
                "entity_id": r.entity_id,
                "entity_name": r.entity_name,
                "account_code": r.account_code,
                "first_date": _fmt_date(r.first_date),
                "last_date": _fmt_date(r.last_date),
                "total_debit": str(r.total_debit),
                "total_credit": str(r.total_credit),
                "closing_balance": str(r.closing_balance),
            }
            for r in rows
        ]

    # ── Posting ─────────────────────────────────────────────────────────

    def post_entry(self, entry_id: int) -> Result:
        model = self.session.get(JournalEntryModel, entry_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=entry_id))

        if model.is_posted:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_POSTED, type="Journal entry", id=entry_id))

        if self.is_period_closed(model.period):
            return Result.failure(ValidationError(ErrorCodes.PERIOD_CLOSED_OP, period=model.period, action="post journal entry"))

        lines = self.session.execute(
            select(JournalLineModel).where(JournalLineModel.journal_entry_id == entry_id)
        ).scalars().all()

        total_debit = sum(l.debit for l in lines)
        total_credit = sum(l.credit for l in lines)
        if abs(total_debit - total_credit) > 0.001:
            return Result.failure(DoubleEntryError(
                ErrorCodes.DOUBLE_ENTRY_DEBIT_CREDIT, debit=total_debit, credit=total_credit
            ))

        for line in lines:
            account = self.session.execute(
                select(COAModel).where(COAModel.code == line.account_id)
            ).scalar_one_or_none()
            if not account:
                return Result.failure(ValidationError(ErrorCodes.ACCOUNT_NOT_FOUND, code=line.account_id))

        model.is_posted = True
        model.posted_date = datetime.now(timezone.utc)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._entry_to_domain(model))

    # ── Account balances ────────────────────────────────────────────────

    def get_account_balance(self, account_id: str, period: Optional[str] = None) -> dict:
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
            is_debit_normal = account.drcr_direction == DCRDirection.DEBIT.value

        if is_debit_normal:
            balance = total_debit - total_credit
        else:
            balance = total_credit - total_debit

        return {
            "account_id": account_id,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance": balance,
            "balance_type": "debit" if balance > 0 else "credit" if balance < 0 else "zero",
        }

    def count(self) -> int:
        return self.session.execute(
            select(func.count()).select_from(JournalEntryModel)
        ).scalar()

    # ── Period validation helpers ──────────────────────────────────────

    def _count_unposted_entries(self, period: str) -> int:
        return self.session.execute(
            select(func.count()).select_from(JournalEntryModel).where(
                JournalEntryModel.period == period,
                JournalEntryModel.is_posted == False,
            )
        ).scalar() or 0

    def _has_unbalanced_entries(self, period: str) -> bool:
        entries = self.session.execute(
            select(JournalEntryModel).where(JournalEntryModel.period == period)
        ).scalars().all()
        for entry in entries:
            lines = self.session.execute(
                select(JournalLineModel).where(JournalLineModel.journal_entry_id == entry.id)
            ).scalars().all()
            if lines:
                total_debit = sum(l.debit for l in lines)
                total_credit = sum(l.credit for l in lines)
                if abs(total_debit - total_credit) > Decimal("0.001"):
                    return True
        return False

    # ── Period audit log ───────────────────────────────────────────────

    def _log_audit(self, period: str, event_type: str, user: str, details: Optional[str] = None):
        log = PeriodAuditLogModel(
            period=period,
            event_type=event_type,
            user=user,
            details=details,
        )
        self.session.add(log)

    def get_period_audit_log(self, period: str) -> List[dict]:
        models = self.session.execute(
            select(PeriodAuditLogModel).where(
                PeriodAuditLogModel.period == period
            ).order_by(PeriodAuditLogModel.created_at.asc())
        ).scalars().all()
        return [
            {
                "id": m.id,
                "period": m.period,
                "event_type": m.event_type,
                "user": m.user,
                "details": m.details,
                "created_at": m.created_at.isoformat(),
            }
            for m in models
        ]

    # ── Period close ────────────────────────────────────────────────────

    def get_period(self, period: str) -> Optional[dict]:
        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        if not model:
            return None
        return self._period_to_dict(model)

    def _auto_create_period(self, period: str) -> AccountingPeriodModel:
        """Auto-create a period with computed metadata from the period string."""
        from calendar import monthrange
        model = AccountingPeriodModel(period=period)
        parts = period.split("-")
        try:
            if len(parts) == 2 and parts[1].isdigit():
                year = int(parts[0])
                month = int(parts[1])
                if 1 <= month <= 12:
                    model.type = PeriodType.MONTHLY
                    model.start_date = date(year, month, 1)
                    _, last_day = monthrange(year, month)
                    model.end_date = date(year, month, last_day)
                    model.parent_period = str(year)
            elif len(parts) == 1 and parts[0].isdigit():
                year = int(parts[0])
                model.type = PeriodType.YEARLY
                model.start_date = date(year, 1, 1)
                model.end_date = date(year, 12, 31)
        except (ValueError, OverflowError):
            pass
        self.session.add(model)
        self.session.flush()
        return model

    def close_period(self, period: str, closed_by: str, notes: Optional[str] = None,
                     force: bool = False) -> Result:
        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()

        if model and model.is_closed:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_ALREADY_CLOSED, period=period))

        if not model:
            model = self._auto_create_period(period)
            self._log_audit(period, "PERIOD_CREATE", closed_by, "Auto-created on close")

        if not force:
            unposted = self._count_unposted_entries(period)
            if unposted > 0:
                return Result.failure(ValidationError(
                    f"Period {period} has {unposted} unposted journal entr{'y' if unposted == 1 else 'ies'}. "
                    "Post or remove them before closing, or use force=true."
                ))
            if self._has_unbalanced_entries(period):
                return Result.failure(ValidationError(
                    f"Period {period} has unbalanced journal entries. "
                    "Fix them before closing, or use force=true."
                ))

        model.is_closed = True
        model.closed_by = closed_by
        model.closed_at = datetime.now(timezone.utc)
        model.notes = notes
        model.is_current = False
        self.session.flush()
        event = "PERIOD_FORCE_CLOSE" if force else "PERIOD_CLOSE"
        detail = notes or f"Period closed{' (forced)' if force else ''}"
        self._log_audit(period, event, closed_by, detail)
        return Result.success(self.get_period(period))

    def _has_tax_declarations_blocking_reopen(self, period: str) -> bool:
        """Check if any submitted/accepted tax declarations exist for this period."""
        parts = period.split("-")
        year = int(parts[0]) if parts[0].isdigit() else 0
        blocked_statuses = (DeclarationStatusDB.SUBMITTED, DeclarationStatusDB.ACCEPTED)
        stmt = select(func.count()).select_from(TaxDeclarationModel).where(
            TaxDeclarationModel.period_year == year,
            TaxDeclarationModel.status.in_(blocked_statuses),
        )
        if len(parts) == 2 and parts[1].isdigit():
            month = int(parts[1])
            if 1 <= month <= 12:
                stmt = stmt.where(TaxDeclarationModel.period_month == month)
            else:
                return False
        elif len(parts) == 2 and parts[1].startswith("Q") and len(parts[1]) == 2:
            q = int(parts[1][1])
            if 1 <= q <= 4:
                stmt = stmt.where(TaxDeclarationModel.period_quarter == q)
            else:
                return False
        count = self.session.execute(stmt).scalar() or 0
        return count > 0

    def reopen_period(self, period: str, reopened_by: str = "system",
                      reason: Optional[str] = None) -> Result:
        if not reason:
            return Result.failure(ValidationError(ErrorCodes.REOPEN_REASON_REQUIRED))

        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        if not model:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_NOT_FOUND, period=period))
        if not model.is_closed:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_NOT_CLOSED, period=period))

        if self._has_tax_declarations_blocking_reopen(period):
            return Result.failure(ValidationError(
                f"Period {period} has submitted/accepted tax declarations. "
                "Cannot reopen until declarations are cancelled or amended."
            ))

        model.is_closed = False
        model.closed_by = None
        model.closed_at = None
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self._log_audit(period, "PERIOD_REOPEN", reopened_by, reason)

        if model.end_date:
            subsequent = self.session.execute(
                select(AccountingPeriodModel).where(
                    AccountingPeriodModel.start_date > model.end_date,
                    AccountingPeriodModel.is_closed == False,
                )
            ).scalars().all()
            for s in subsequent:
                s.needs_reconciliation = True
            if subsequent:
                self.session.flush()

        return Result.success(self.get_period(period))

    def list_periods(self, status: Optional[str] = None) -> List[dict]:
        stmt = select(AccountingPeriodModel).order_by(AccountingPeriodModel.period.desc())
        if status == "open":
            stmt = stmt.where(AccountingPeriodModel.is_closed == False)
        elif status == "closed":
            stmt = stmt.where(AccountingPeriodModel.is_closed == True)
        models = self.session.execute(stmt).scalars().all()
        return [self._period_to_dict(m) for m in models]

    def _period_to_dict(self, model: AccountingPeriodModel) -> dict:
        has_entries = self.session.execute(
            select(func.count()).select_from(JournalEntryModel).where(
                JournalEntryModel.period == model.period
            )
        ).scalar() > 0
        return {
            "id": model.id,
            "period": model.period,
            "type": model.type.value if model.type else "monthly",
            "start_date": model.start_date.isoformat() if model.start_date else None,
            "end_date": model.end_date.isoformat() if model.end_date else None,
            "is_closed": model.is_closed,
            "closed_by": model.closed_by,
            "closed_at": model.closed_at.isoformat() if model.closed_at else None,
            "notes": model.notes,
            "is_current": model.is_current,
            "needs_reconciliation": model.needs_reconciliation,
            "parent_period": model.parent_period,
            "has_entries": has_entries,
        }

    def create_period(self, period: str, type_: str = "monthly",
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> Result:
        existing = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_ALREADY_EXISTS, period=period))

        if start_date and end_date:
            overlap = self.session.execute(
                select(AccountingPeriodModel).where(
                    AccountingPeriodModel.start_date <= end_date,
                    AccountingPeriodModel.end_date >= start_date,
                ).limit(1)
            ).scalar_one_or_none()
            if overlap:
                return Result.failure(ValidationError(ErrorCodes.PERIOD_OVERLAP, period=period))

        model = AccountingPeriodModel(period=period)
        try:
            model.type = PeriodType(type_)
        except ValueError:
            return Result.failure(ValidationError(ErrorCodes.INVALID_PERIOD_TYPE, type=type_))
        model.start_date = start_date
        model.end_date = end_date
        self.session.add(model)
        self.session.flush()
        self._log_audit(period, "PERIOD_CREATE", "system", "Period created explicitly")
        return Result.success(self.get_period(period))

    def get_current_period(self) -> Optional[dict]:
        model = self.session.execute(
            select(AccountingPeriodModel).where(
                AccountingPeriodModel.is_current == True,
                AccountingPeriodModel.is_closed == False
            )
        ).scalar_one_or_none()
        if model:
            return self.get_period(model.period)
        model = self.session.execute(
            select(AccountingPeriodModel).where(
                AccountingPeriodModel.is_closed == False
            ).order_by(AccountingPeriodModel.period.desc())
        ).scalar_one_or_none()
        return self.get_period(model.period) if model else None

    def is_period_closed(self, period: str) -> bool:
        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        return model.is_closed if model else False

    # ── Year-end carry forward ─────────────────────────────────────────

    def carry_forward(self, period: str, closed_by: str = "system") -> Result:
        """Execute year-end carry forward: close revenue/expense to retained earnings,
        create opening balances for next year."""
        model = self.session.execute(
            select(AccountingPeriodModel).where(AccountingPeriodModel.period == period)
        ).scalar_one_or_none()
        if not model:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_NOT_FOUND, period=period))
        if model.is_closed:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_ALREADY_CLOSED, period=period))

        parts = period.split("-")
        year = int(parts[0]) if parts[0].isdigit() else 0
        if len(parts) == 2 and parts[1].isdigit():
            month = int(parts[1])
            if month != 12:
                return Result.failure(ValidationError(
                    f"Carry forward only supported for year-end (December/YYYY-12), got {period}"
                ))
        elif len(parts) != 1:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_FORMAT_INVALID, period=period))

        revenue_accounts = self.session.execute(
            select(COAModel.code).where(COAModel.account_type == "revenue")
        ).scalars().all()
        expense_accounts = self.session.execute(
            select(COAModel.code).where(COAModel.account_type == "expense")
        ).scalars().all()

        total_revenue = Decimal("0")
        revenue_lines: List[dict] = []
        for code in revenue_accounts:
            bal = self.get_account_balance(code, period)
            if bal["balance"] > 0:
                total_revenue += bal["balance"]
                revenue_lines.append({"account_id": code, "amount": bal["balance"]})

        total_expenses = Decimal("0")
        expense_lines: List[dict] = []
        for code in expense_accounts:
            bal = self.get_account_balance(code, period)
            if bal["balance"] > 0:
                total_expenses += bal["balance"]
                expense_lines.append({"account_id": code, "amount": bal["balance"]})

        net_income = total_revenue - total_expenses

        next_year = year + 1
        next_period_str = f"{next_year}-01"

        closing_lines: List[JournalLine] = []
        for rl in revenue_lines:
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=rl["account_id"],
                debit=Decimal("0"),
                credit=rl["amount"],
                period=period,
            ))

        pnl_account_id = "9111"
        closing_lines.append(JournalLine(
            journal_entry_id=0,
            account_id=pnl_account_id,
            debit=total_revenue,
            credit=Decimal("0"),
            period=period,
        ))

        closing_lines.append(JournalLine(
            journal_entry_id=0,
            account_id=pnl_account_id,
            debit=Decimal("0"),
            credit=total_expenses,
            period=period,
        ))
        for el in expense_lines:
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=el["account_id"],
                debit=el["amount"],
                credit=Decimal("0"),
                period=period,
            ))

        retained_account = "4211"
        if net_income >= 0:
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=pnl_account_id,
                debit=net_income,
                credit=Decimal("0"),
                period=period,
            ))
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=retained_account,
                debit=Decimal("0"),
                credit=net_income,
                period=period,
            ))
        else:
            loss = -net_income
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=retained_account,
                debit=loss,
                credit=Decimal("0"),
                period=period,
            ))
            closing_lines.append(JournalLine(
                journal_entry_id=0,
                account_id=pnl_account_id,
                debit=Decimal("0"),
                credit=loss,
                period=period,
            ))

        total_debit = sum(l.debit for l in closing_lines)
        total_credit = sum(l.credit for l in closing_lines)
        if abs(total_debit - total_credit) > Decimal("0.001"):
            return Result.failure(ValidationError(
                f"Closing entry unbalanced: debit={total_debit}, credit={total_credit}"
            ))

        je_model = JournalEntryModel(
            journal_number=f"JV{year}9999",
            transaction_date=model.end_date or date(year, 12, 31),
            description=f"Year-end closing entries for {year}",
            period=period,
            is_posted=True,
        )
        self.session.add(je_model)
        self.session.flush()

        for i, line in enumerate(closing_lines, start=1):
            line_model = JournalLineModel(
                journal_entry_id=je_model.id,
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                period=line.period,
            )
            self.session.add(line_model)

        next_period = self._auto_create_period(next_period_str)
        next_period.is_current = True

        model.is_closed = True
        model.closed_by = closed_by
        model.closed_at = datetime.now(timezone.utc)
        self.session.flush()

        self._log_audit(period, "PERIOD_CARRY_FORWARD", closed_by,
                        f"Year-end close {year}: revenue={total_revenue}, expenses={total_expenses}, "
                        f"net_income={net_income}. Next period: {next_period_str}")

        return Result.success({
            "period": period,
            "closed": True,
            "closing_entry": je_model.journal_number,
            "total_revenue": str(total_revenue),
            "total_expenses": str(total_expenses),
            "net_income": str(net_income),
            "next_period": next_period_str,
        })

    # ── Financial statements ─────────────────────────────────────────────

    def _balance_by_type(self, period: str, dcrr_direction: str) -> Decimal:
        """Get net balance for all accounts with given DCR direction."""
        stmt = select(
            func.coalesce(func.sum(JournalLineModel.debit), 0),
            func.coalesce(func.sum(JournalLineModel.credit), 0),
        ).where(
            JournalLineModel.period == period,
            JournalLineModel.journal_entry_id.in_(
                select(JournalEntryModel.id).where(JournalEntryModel.is_posted == True)
            ),
            JournalLineModel.account_id.in_(
                select(COAModel.code).where(COAModel.drcr_direction == dcrr_direction)
            ),
        )
        result = self.session.execute(stmt).one()
        total_debit = Decimal(str(result[0]))
        total_credit = Decimal(str(result[1]))

        if dcrr_direction == DCRDirection.DEBIT.value:
            return total_debit - total_credit
        return total_credit - total_debit

    def _account_balances_by_type(self, period: str, account_type: str) -> Dict[str, Decimal]:
        """Get account-level balances for a given account type."""
        accounts = self.session.execute(
            select(COAModel).where(COAModel.account_type == account_type)
        ).scalars().all()

        result = {}
        for acc in accounts:
            bal = self.get_account_balance(acc.code, period)
            if bal["balance"] != 0:
                result[acc.code] = bal["balance"]
        return result

    def generate_balance_sheet(self, period: str) -> dict:
        assets = self._account_balances_by_type(period, "asset")
        liabilities = self._account_balances_by_type(period, "liability")
        equity = self._account_balances_by_type(period, "equity")

        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        total_equity = sum(equity.values())

        return {
            "period": period,
            "statement_type": "balance_sheet",
            "assets": {k: str(v) for k, v in sorted(assets.items())},
            "liabilities": {k: str(v) for k, v in sorted(liabilities.items())},
            "equity": {k: str(v) for k, v in sorted(equity.items())},
            "total_assets": str(total_assets),
            "total_liabilities": str(total_liabilities),
            "total_equity": str(total_equity),
        }

    def generate_income_statement(self, period: str) -> dict:
        revenue = self._account_balances_by_type(period, "revenue")
        expenses = self._account_balances_by_type(period, "expense")

        total_revenue = sum(revenue.values())
        total_expenses = sum(expenses.values())
        net_income = total_revenue - total_expenses

        return {
            "period": period,
            "statement_type": "income_statement",
            "revenue": {k: str(v) for k, v in sorted(revenue.items())},
            "expenses": {k: str(v) for k, v in sorted(expenses.items())},
            "total_revenue": str(total_revenue),
            "total_expenses": str(total_expenses),
            "net_income": str(net_income),
        }

    def generate_trial_balance(self, period: str) -> dict:
        """Bảng cân đối số phát sinh — Trial Balance per TT99."""
        accounts = self.session.execute(
            select(COAModel).order_by(COAModel.code)
        ).scalars().all()

        rows = []
        total_opening_debit = Decimal("0")
        total_opening_credit = Decimal("0")
        total_period_debit = Decimal("0")
        total_period_credit = Decimal("0")
        total_closing_debit = Decimal("0")
        total_closing_credit = Decimal("0")

        for acc in accounts:
            bal = self.get_account_balance(acc.code, period)
            account_is_debit_normal = acc.drcr_direction == DCRDirection.DEBIT.value
            debit_total = bal["total_debit"]
            credit_total = bal["total_credit"]
            closing_balance = bal["balance"]
            opening_balance = closing_balance - debit_total + credit_total

            opening_dr = opening_balance if account_is_debit_normal and opening_balance > 0 else Decimal("0")
            opening_cr = -opening_balance if account_is_debit_normal and opening_balance < 0 else (opening_balance if not account_is_debit_normal and opening_balance > 0 else Decimal("0"))
            if not account_is_debit_normal and opening_balance > 0:
                opening_cr = opening_balance
            elif not account_is_debit_normal and opening_balance < 0:
                opening_dr = -opening_balance

            closing_dr = closing_balance if account_is_debit_normal and closing_balance > 0 else Decimal("0")
            closing_cr = -closing_balance if account_is_debit_normal and closing_balance < 0 else (closing_balance if not account_is_debit_normal and closing_balance > 0 else Decimal("0"))
            if not account_is_debit_normal and closing_balance > 0:
                closing_cr = closing_balance
            elif not account_is_debit_normal and closing_balance < 0:
                closing_dr = -closing_balance

            total_opening_debit += opening_dr
            total_opening_credit += opening_cr
            total_period_debit += debit_total
            total_period_credit += credit_total
            total_closing_debit += closing_dr
            total_closing_credit += closing_cr

            rows.append({
                "account_code": acc.code,
                "account_name": acc.name,
                "account_type": acc.account_type,
                "opening_debit": str(opening_dr),
                "opening_credit": str(opening_cr),
                "period_debit": str(debit_total),
                "period_credit": str(credit_total),
                "closing_debit": str(closing_dr),
                "closing_credit": str(closing_cr),
            })

        return {
            "period": period,
            "statement_type": "trial_balance",
            "rows": rows,
            "account_count": len(rows),
            "total_opening_debit": str(total_opening_debit),
            "total_opening_credit": str(total_opening_credit),
            "total_period_debit": str(total_period_debit),
            "total_period_credit": str(total_period_credit),
            "total_closing_debit": str(total_closing_debit),
            "total_closing_credit": str(total_closing_credit),
        }

    def generate_cash_flow(self, period: str, method: str = "direct") -> dict:
        """B03-DN Cash Flow Statement using direct or indirect method."""
        from sqlalchemy import func, text

        if method == "direct":
            cash_type = DCRDirection.DEBIT.value

            cash_inflow_sql = text("""
                SELECT
                    jl.account_id,
                    COALESCE(SUM(jl.debit), 0) AS total
                FROM journal_lines jl
                JOIN journal_entries je ON je.id = jl.journal_entry_id
                WHERE je.is_posted = TRUE
                  AND je.period = :period
                  AND jl.account_id IN ('1111', '1112', '1121', '1122')
                  AND jl.debit > 0
                GROUP BY jl.account_id
            """)
            cash_outflow_sql = text("""
                SELECT
                    jl.account_id,
                    COALESCE(SUM(jl.credit), 0) AS total
                FROM journal_lines jl
                JOIN journal_entries je ON je.id = jl.journal_entry_id
                WHERE je.is_posted = TRUE
                  AND je.period = :period
                  AND jl.account_id IN ('1111', '1112', '1121', '1122')
                  AND jl.credit > 0
                GROUP BY jl.account_id
            """)

            inflow_rows = self.session.execute(cash_inflow_sql, {"period": period}).fetchall()
            outflow_rows = self.session.execute(cash_outflow_sql, {"period": period}).fetchall()

            total_inflow = sum(Decimal(str(r.total)) for r in inflow_rows)
            total_outflow = sum(Decimal(str(r.total)) for r in outflow_rows)

            op_inflow = self.session.execute(text("""
                SELECT COALESCE(SUM(jl.debit), 0)
                FROM journal_lines jl
                JOIN journal_entries je ON je.id = jl.journal_entry_id
                WHERE je.is_posted = TRUE AND je.period = :period
                  AND jl.account_id IN ('1111', '1112', '1121', '1122')
                  AND jl.debit > 0
                  AND je.journal_type IN ('sales', 'cash_receipt')
            """), {"period": period}).scalar() or 0

            op_outflow = self.session.execute(text("""
                SELECT COALESCE(SUM(jl.credit), 0)
                FROM journal_lines jl
                JOIN journal_entries je ON je.id = jl.journal_entry_id
                WHERE je.is_posted = TRUE AND je.period = :period
                  AND jl.account_id IN ('1111', '1112', '1121', '1122')
                  AND jl.credit > 0
                  AND je.journal_type IN ('purchase', 'cash_payment')
            """), {"period": period}).scalar() or 0

            inv_inflow = total_inflow - Decimal(str(op_inflow))
            inv_outflow = Decimal("0")
            fin_inflow = Decimal("0")
            fin_outflow = total_outflow - Decimal(str(op_outflow))

            net_operating = Decimal(str(op_inflow)) - Decimal(str(op_outflow))
            net_investing = inv_inflow - inv_outflow
            net_financing = fin_inflow - fin_outflow
            net_change = net_operating + net_investing + net_financing

            return {
                "period": period,
                "method": "direct",
                "statement_type": "cash_flow",
                "operating": {
                    "inflow": str(op_inflow),
                    "outflow": str(op_outflow),
                    "net": str(net_operating),
                },
                "investing": {
                    "inflow": str(inv_inflow),
                    "outflow": str(inv_outflow),
                    "net": str(net_investing),
                },
                "financing": {
                    "inflow": str(fin_inflow),
                    "outflow": str(fin_outflow),
                    "net": str(net_financing),
                },
                "net_change": str(net_change),
            }

        return {
            "period": period,
            "method": method,
            "statement_type": "cash_flow",
            "error": "Indirect method not yet implemented",
        }
