from typing import Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from domain import Result, ChartError
from infrastructure.repositories.coa_repository import COARepository
from infrastructure.repositories.gl_repository import GLRepository
from infrastructure.models.gl_models import JournalLineModel, JournalEntryModel


class COAUsageUseCase:
    def __init__(self, session: Session):
        self.session = session
        self.repo = COARepository(session)
        self.gl = GLRepository(session)

    def check_usage(self, code: str) -> Result:
        account = self.repo.get_by_code(code)
        if not account:
            return Result.failure(ChartError(f"Account '{code}' not found"))

        balance = self.gl.get_account_balance(code)

        tx_count = self.session.execute(
            select(func.count(JournalLineModel.id)).where(
                JournalLineModel.account_id == code,
                JournalLineModel.journal_entry_id.in_(
                    select(JournalEntryModel.id).where(JournalEntryModel.is_posted == True)
                ),
            )
        ).scalar() or 0

        last_tx = self.session.execute(
            select(func.max(JournalEntryModel.transaction_date)).where(
                JournalEntryModel.id.in_(
                    select(JournalLineModel.journal_entry_id).where(
                        JournalLineModel.account_id == code
                    )
                )
            )
        ).scalar()

        return Result.success({
            "code": code,
            "name": account.name,
            "account_type": account.account_type.value,
            "status": account.status.value,
            "balance": str(balance["balance"]),
            "balance_type": balance["balance_type"],
            "total_debit": str(balance["total_debit"]),
            "total_credit": str(balance["total_credit"]),
            "transaction_count": tx_count,
            "last_transaction_date": last_tx.isoformat() if last_tx else None,
            "can_deactivate": tx_count == 0 and balance["balance"] == Decimal("0"),
            "can_delete": tx_count == 0 and balance["balance"] == Decimal("0"),
        })
