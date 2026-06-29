from typing import Optional, List
from sqlalchemy.orm import Session

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, AccountStatus,
    Result, ChartError, ValidationError, VASValidationError
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.coa_repository import COARepository


class COAUseCases:
    def __init__(self, session: Session):
        self.repo = COARepository(session)

    def create_account(
        self,
        code: str,
        name: str,
        account_type: AccountType,
        drcr_direction: DCRDirection,
        regime: AccountingRegime = AccountingRegime.TT99_2025,
        parent_code: Optional[str] = None,
        description: Optional[str] = None,
        currency: str = "VND",
        unit: str = "VND",
    ) -> Result:
        level = len(code.split("."))
        try:
            account = ChartOfAccounts(
                code=code,
                name=name,
                account_type=account_type,
                regime=regime,
                drcr_direction=drcr_direction,
                level=level,
                parent_code=parent_code,
                description=description,
                currency=currency,
                unit=unit,
            )
        except VASValidationError as e:
            return Result.failure(e)

        return self.repo.create(account)

    def get_account(self, code: str) -> Result:
        account = self.repo.get_by_code(code)
        if not account:
            return Result.failure(ChartError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))
        return Result.success(account)

    def list_accounts(
        self,
        regime: Optional[AccountingRegime] = None,
        status: Optional[AccountStatus] = None,
        account_type: Optional[AccountType] = None,
    ) -> List[ChartOfAccounts]:
        return self.repo.list_all(regime=regime, status=status, account_type=account_type)

    def search_accounts(self, query: str) -> List[ChartOfAccounts]:
        return self.repo.search(query)

    def update_account(self, code: str, **kwargs) -> Result:
        return self.repo.update(code, **kwargs)

    def delete_account(self, code: str) -> Result:
        return self.repo.delete(code)

    def get_account_hierarchy(self, code: str) -> Result:
        root = self.repo.get_by_code(code)
        if not root:
            return Result.failure(ChartError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))

        children = self.repo.list_all(parent_code=code)
        result = {
            "account": {
                "code": root.code,
                "name": root.name,
                "level": root.level,
                "account_type": root.account_type.value,
                "drcr_direction": root.drcr_direction.value,
                "status": root.status.value,
            },
            "children": [
                {
                    "code": c.code,
                    "name": c.name,
                    "level": c.level,
                    "account_type": c.account_type.value,
                    "drcr_direction": c.drcr_direction.value,
                    "status": c.status.value,
                }
                for c in children
            ],
        }
        return Result.success(result)

    def bulk_create(self, accounts: List[ChartOfAccounts]) -> Result:
        created: List[ChartOfAccounts] = []
        errors: List[dict] = []

        for account in accounts:
            r = self.repo.create(account)
            if r.is_success():
                created.append(r.get_data())
            else:
                errors.append({"code": account.code, "error": str(r.error)})

        return Result.success({"created": [c.code for c in created], "errors": errors})

    def get_summary(self) -> Result:
        all_accounts = self.repo.list_all()
        total = len(all_accounts)
        active = sum(1 for a in all_accounts if a.status == AccountStatus.ACTIVE)
        suspended = sum(1 for a in all_accounts if a.status == AccountStatus.SUSPENDED)
        closed = sum(1 for a in all_accounts if a.status == AccountStatus.CLOSED)

        type_counts: dict = {}
        for a in all_accounts:
            t = a.account_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return Result.success({
            "total": total,
            "active": active,
            "suspended": suspended,
            "closed": closed,
            "by_type": type_counts,
            "regime": AccountingRegime.TT99_2025.value,
        })
