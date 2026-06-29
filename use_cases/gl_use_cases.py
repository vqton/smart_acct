from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal

from domain import JournalEntry, JournalLine, Result, ValidationError, DoubleEntryError
from infrastructure.repositories.gl_repository import GLRepository


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
        source_module: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        try:
            period = period or transaction_date.strftime("%Y-%m")
            entry = JournalEntry(
                journal_number=journal_number,
                transaction_date=transaction_date,
                description=description,
                period=period,
                source_module=source_module,
                created_by=created_by,
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
                    f"Double-entry violation: total debits {total_debit} != total credits {total_credit}"
                ))

            return self.repo.create_entry(entry)
        except ValidationError as e:
            return Result.failure(e)
        except DoubleEntryError as e:
            return Result.failure(e)

    def get_entry(self, entry_id: int) -> Result:
        entry = self.repo.get_entry(entry_id)
        if not entry:
            return Result.failure(ValidationError(f"Journal entry {entry_id} not found"))
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

    def post_entry(self, entry_id: int) -> Result:
        return self.repo.post_entry(entry_id)

    def get_account_balance(self, account_id: str, period: Optional[str] = None) -> dict:
        return self.repo.get_account_balance(account_id, period)

    # ── Period close ────────────────────────────────────────────────────

    def get_period(self, period: str) -> Result:
        p = self.repo.get_period(period)
        if not p:
            return Result.failure(ValidationError(f"Period {period} not found"))
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
            return Result.failure(ValidationError("No open period found"))
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
