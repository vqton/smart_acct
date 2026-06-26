from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, AccountStatus,
    Result
)
from infrastructure.repositories.coa_repository import COARepository


class COAValidateUseCase:
    def __init__(self, session: Session):
        self.repo = COARepository(session)

    def validate_code_format(self, code: str) -> dict:
        issues: List[str] = []
        clean = code.replace(".", "")

        if not clean.isdigit():
            issues.append("Account code must be numeric (only digits and dots allowed)")

        first_digit = code.split(".")[0]
        if not first_digit.isdigit() or int(first_digit) < 1 or int(first_digit) > 9:
            issues.append("First digit must be 1-9")

        if code.startswith("0"):
            issues.append("Account code cannot start with 0")

        parts = code.split(".")
        if len(parts) > 4:
            issues.append("Maximum 4 hierarchy levels allowed")

        if len(clean) > 6:
            issues.append("Maximum 6 digits allowed")

        return {"code": code, "valid": len(issues) == 0, "issues": issues}

    def validate_account(self, code: str) -> Result:
        account = self.repo.get_by_code(code)
        if not account:
            return Result.failure(ValueError(f"Account '{code}' not found"))

        issues: List[dict] = []

        fmt = self.validate_code_format(code)
        if not fmt["valid"]:
            issues.extend(fmt["issues"])

        if not account.vas_compliant:
            issues.append("Account is marked as non-compliant with VAS")

        if account.status == AccountStatus.CLOSED:
            issues.append("Account is closed — cannot be used in new transactions")

        parent_ok = True
        if account.parent_code:
            parent = self.repo.get_by_code(account.parent_code)
            if not parent:
                issues.append(f"Parent account '{account.parent_code}' does not exist")
                parent_ok = False
            elif parent.status != AccountStatus.ACTIVE:
                issues.append(f"Parent account '{account.parent_code}' is not active")

        if parent_ok and account.parent_code:
            expected_parent_level = account.level - 1
            stmt = text("SELECT code, level FROM chart_of_accounts WHERE code = :code")
            rs = self.repo.session.execute(stmt, {"code": account.parent_code}).fetchone()
            if rs and rs.level != expected_parent_level:
                issues.append(
                    f"Parent account level mismatch: got {rs.level}, expected {expected_parent_level}"
                )

        return Result.success({
            "code": code,
            "name": account.name,
            "valid": len(issues) == 0,
            "issues": issues,
        })

    def validate_all(self, regime: Optional[AccountingRegime] = None) -> Result:
        accounts = self.repo.list_all(regime=regime)
        results = []
        valid_count = 0
        invalid_count = 0

        for acc in accounts:
            r = self.validate_account(acc.code)
            data = r.get_data() if r.is_success() else {"code": acc.code, "valid": False, "issues": [str(r.error)]}
            results.append(data)
            if data["valid"]:
                valid_count += 1
            else:
                invalid_count += 1

        return Result.success({
            "total": len(accounts),
            "valid": valid_count,
            "invalid": invalid_count,
            "results": results,
        })

    def validate_tt99_compliance(self, account: ChartOfAccounts) -> List[str]:
        """Validate TT99/2025 specific rules"""
        issues: List[str] = []

        if account.regime != AccountingRegime.TT99_2025:
            return issues

        if account.account_type in (
            AccountType.CASH, AccountType.BANK,
            AccountType.ACCOUNT_RECEIVABLE,
        ):
            if account.level > 3:
                issues.append(f"TT99: {account.account_type.value} accounts max 3 levels")

        return issues

    def get_hierarchy_errors(self) -> Result:
        accounts = self.repo.list_all()
        errors = []

        for acc in accounts:
            if acc.parent_code:
                parent = self.repo.get_by_code(acc.parent_code)
                if not parent:
                    errors.append({
                        "code": acc.code,
                        "name": acc.name,
                        "issue": f"Parent '{acc.parent_code}' missing"
                    })
                elif parent.level != acc.level - 1:
                    errors.append({
                        "code": acc.code,
                        "name": acc.name,
                        "issue": f"Level gap: parent level={parent.level}, child level={acc.level}"
                    })

        return Result.success({"total_checked": len(accounts), "errors": errors})
