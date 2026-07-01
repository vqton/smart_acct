from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal

from domain import (
    JournalEntry, JournalLine, JournalType, SubsidiaryType, SubsidiaryLedger, CorrectionMethod,
    Result, ValidationError, DoubleEntryError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.gl_repository import GLRepository


def _parse_journal_type(raw: Optional[str]) -> JournalType:
    if not raw:
        return JournalType.GENERAL
    try:
        return JournalType(raw)
    except ValueError:
        raise ValidationError(ErrorCodes.JOURNAL_TYPE_INVALID, journal_type=raw)


class GLUseCases:
    def __init__(self, session):
        self.repo = GLRepository(session)

    def create_entry(
        self,
        journal_number: str,
        transaction_date: date,
        description: str,
        lines: List[dict],
        period: Optional[str] = None,
        journal_type: Optional[str] = None,
        source_module: Optional[str] = None,
        created_by: Optional[str] = None,
        auto_number: bool = False,
        approved_by: Optional[str] = None,
        ref_journal_number: Optional[str] = None,
    ) -> Result:
        try:
            period = period or transaction_date.strftime("%Y-%m")
            jt = _parse_journal_type(journal_type)

            if auto_number or not journal_number:
                journal_number = self.repo.get_next_journal_number(jt, period)

            entry = JournalEntry(
                journal_number=journal_number,
                journal_type=jt,
                transaction_date=transaction_date,
                description=description,
                period=period,
                source_module=source_module,
                created_by=created_by,
                approved_by=approved_by,
                ref_journal_number=ref_journal_number,
            )

            for line_data in lines:
                line = JournalLine(
                    journal_entry_id=0,
                    account_id=line_data["account_id"],
                    debit=Decimal(str(line_data.get("debit", 0))),
                    credit=Decimal(str(line_data.get("credit", 0))),
                    description=line_data.get("description"),
                    vat_rate=Decimal(str(line_data["vat_rate"])) if line_data.get("vat_rate") else None,
                    line_type=line_data.get("line_type", "regular"),
                    is_taxable=line_data.get("is_taxable", False),
                    tax_code=line_data.get("tax_code"),
                    period=period,
                )
                entry.lines.append(line)

            total_debit = sum(l.debit for l in entry.lines)
            total_credit = sum(l.credit for l in entry.lines)
            if abs(total_debit - total_credit) > Decimal("0.001"):
                return Result.failure(DoubleEntryError(
                    ErrorCodes.DOUBLE_ENTRY_DEBIT_CREDIT, debit=total_debit, credit=total_credit
                ))

            return self.repo.create_entry(entry)
        except ValidationError as e:
            return Result.failure(e)
        except DoubleEntryError as e:
            return Result.failure(e)

    def get_entry(self, entry_id: int) -> Result:
        entry = self.repo.get_entry(entry_id)
        if not entry:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=entry_id))
        return Result.success(entry)

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
        return self.repo.list_entries(
            period=period,
            is_posted=is_posted,
            account_id=account_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )

    def update_entry(self, entry_id: int, **kwargs) -> Result:
        return self.repo.update_entry(entry_id, **kwargs)

    def delete_entry(self, entry_id: int) -> Result:
        return self.repo.delete_entry(entry_id)

    def reverse_entry(
        self, entry_id: int, correction_method: str = "red_storno",
        description: Optional[str] = None,
    ) -> Result:
        """Create a reversal/correction entry per TT99 Art.18."""
        original_result = self.repo.get_entry(entry_id)
        if not original_result:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=entry_id))

        if not original_result.is_posted:
            return Result.failure(ValidationError(ErrorCodes.CANNOT_REVERSE_UNPOSTED, entry_id=entry_id))

        try:
            cm = CorrectionMethod(correction_method)
        except ValueError:  
            return Result.failure(ValidationError(ErrorCodes.INVALID_CORRECTION_METHOD, method=correction_method))

        new_lines = []
        for line in original_result.lines:
            if cm == CorrectionMethod.RED_STORNO:
                new_lines.append({
                    "account_id": line.account_id,
                    "debit": float(line.credit),
                    "credit": float(line.debit),
                    "description": line.description,
                })
            else:
                new_lines.append({
                    "account_id": line.account_id,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                    "description": line.description,
                })

        correction_desc = description or f"{'Red storno' if cm == CorrectionMethod.RED_STORNO else 'Bổ sung'} correction for {original_result.journal_number}"

        return self.create_entry(
            journal_number="",
            transaction_date=date.today(),
            description=correction_desc,
            lines=new_lines,
            period=original_result.period,
            journal_type="adjustment",
            auto_number=True,
            approved_by="system",
            ref_journal_number=original_result.journal_number,
        )

    def post_entry(
        self, entry_id: int,
        subsidiary_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        entity_name: Optional[str] = None,
        doc_ref: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> Result:
        result = self.repo.post_entry(entry_id)
        if result.is_failure():
            return result
        if subsidiary_type is not None and entity_id is not None:
            entry = result.get_data()
            sub_result = self.repo.post_to_subsidiary_ledger(
                journal_entry_id=entry.id or entry_id,
                lines=[JournalLine(
                    journal_entry_id=l.journal_entry_id,
                    account_id=l.account_id, debit=l.debit, credit=l.credit,
                    description=l.description, period=l.period,
                ) for l in entry.lines],
                subsidiary_type=subsidiary_type,
                entity_id=entity_id,
                entity_name=entity_name or "",
                doc_ref=doc_ref or entry.journal_number,
                doc_type=doc_type or "JV",
                period=entry.period,
                transaction_date=entry.transaction_date,
            )
            if sub_result.is_failure():
                return sub_result
        return result

    def get_account_balance(self, account_id: str, period: Optional[str] = None) -> dict:
        return self.repo.get_account_balance(account_id, period)

    # ── Journal Type Sequence ─────────────────────────────────────────

    def get_next_journal_number(self, journal_type: Optional[str] = None, period: Optional[str] = None) -> Result:
        try:
            jt = _parse_journal_type(journal_type)
            period = period or date.today().strftime("%Y-%m")
            number = self.repo.get_next_journal_number(jt, period)
            return Result.success({"journal_number": number})
        except ValidationError as e:
            return Result.failure(e)

    def get_journal_sequence(self, journal_type: str, fiscal_year: int) -> Result:
        try:
            jt = _parse_journal_type(journal_type)
            seq = self.repo.get_journal_sequence(jt, fiscal_year)
            if not seq:
                return Result.failure(ValidationError(ErrorCodes.JOURNAL_SEQUENCE_NOT_FOUND, journal_type=journal_type, fiscal_year=str(fiscal_year)))
            return Result.success(seq)
        except ValidationError as e:
            return Result.failure(e)

    def list_journal_sequences(self, fiscal_year: Optional[int] = None) -> List[dict]:
        return self.repo.list_journal_sequences(fiscal_year)

    # ── Subsidiary Ledger ───────────────────────────────────────────

    def post_to_subsidiary(
        self, journal_entry_id: int, subsidiary_type: str,
        entity_id: int, entity_name: str,
        doc_ref: str, doc_type: str,
    ) -> Result:
        """Post journal entry lines to subsidiary ledger after posting."""
        entry = self.repo.get_entry(journal_entry_id)
        if not entry:
            return Result.failure(ValidationError(ErrorCodes.JOURNAL_ENTRY_NOT_FOUND, entry_id=journal_entry_id))
        if not entry.is_posted:
            return Result.failure(ValidationError("Entry must be posted before posting to subsidiary ledger"))

        result = self.repo.post_to_subsidiary_ledger(
            journal_entry_id=entry.id,
            lines=[JournalLine(
                journal_entry_id=l.journal_entry_id,
                account_id=l.account_id, debit=l.debit, credit=l.credit,
                description=l.description, period=l.period,
            ) for l in entry.lines],
            subsidiary_type=subsidiary_type,
            entity_id=entity_id,
            entity_name=entity_name,
            doc_ref=doc_ref,
            doc_type=doc_type,
            period=entry.period,
            transaction_date=entry.transaction_date,
        )
        return result

    def get_subsidiary_ledger(
        self, subsidiary_type: str, entity_id: Optional[int] = None,
        period: Optional[str] = None, account_code: Optional[str] = None,
        limit: int = 100, offset: int = 0,
    ) -> List[SubsidiaryLedger]:
        try:
            SubsidiaryType(subsidiary_type)
        except ValueError:
            raise ValidationError(ErrorCodes.SUBSIDIARY_TYPE_INVALID, subsidiary_type=subsidiary_type)
        return self.repo.get_subsidiary_ledger(
            subsidiary_type, entity_id, period, account_code, limit, offset,
        )

    def get_subsidiary_summary(self, subsidiary_type: str, period: str) -> List[dict]:
        try:
            SubsidiaryType(subsidiary_type)
        except ValueError:
            raise ValidationError(ErrorCodes.SUBSIDIARY_TYPE_INVALID, subsidiary_type=subsidiary_type)
        return self.repo.get_subsidiary_summary(subsidiary_type, period)

    # ── Period close ────────────────────────────────────────────────────

    def get_period(self, period: str) -> Result:
        p = self.repo.get_period(period)
        if not p:
            return Result.failure(ValidationError(ErrorCodes.PERIOD_NOT_FOUND, period=period))
        return Result.success(p)

    def close_period(self, period: str, closed_by: str, notes: Optional[str] = None,
                     force: bool = False) -> Result:
        return self.repo.close_period(period, closed_by, notes, force)

    def reopen_period(self, period: str, reopened_by: str = "system",
                      reason: str = "") -> Result:
        return self.repo.reopen_period(period, reopened_by, reason or None)

    def get_period_audit_log(self, period: str) -> List[dict]:
        return self.repo.get_period_audit_log(period)

    def list_periods(self, status: Optional[str] = None) -> List[dict]:
        return self.repo.list_periods(status)

    def create_period(self, period: str, type_: str = "monthly",
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> Result:
        return self.repo.create_period(period, type_, start_date, end_date)

    def get_current_period(self) -> Result:
        p = self.repo.get_current_period()
        if not p:
            return Result.failure(ValidationError(ErrorCodes.NO_OPEN_PERIOD))
        return Result.success(p)

    def is_period_closed(self, period: str) -> bool:
        return self.repo.is_period_closed(period)

    def carry_forward(self, period: str, closed_by: str = "system") -> Result:
        return self.repo.carry_forward(period, closed_by)

    # ── Financial statements ────────────────────────────────────────────

    def generate_balance_sheet(self, period: str) -> dict:
        return self.repo.generate_balance_sheet(period)

    def generate_income_statement(self, period: str) -> dict:
        return self.repo.generate_income_statement(period)
