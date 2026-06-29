from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, AccountStatus,
    Result, VASValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.coa_repository import COARepository


class COAValidateUseCase:
    def __init__(self, session: Session):
        self.repo = COARepository(session)

    def validate_code_format(self, code: str) -> dict:
        issues: List[str] = []
        clean = code.replace(".", "")

        if not clean.isdigit():
            issues.append(ErrorCodes.COA_CODE_NUMERIC)

        if not code[0].isdigit() or int(code[0]) < 1 or int(code[0]) > 9:
            issues.append(ErrorCodes.COA_FIRST_DIGIT_1_9)

        if code.startswith("0"):
            issues.append(ErrorCodes.COA_NO_START_ZERO)

        parts = code.split(".")
        if len(parts) > 4:
            issues.append(ErrorCodes.COA_MAX_LEVELS)

        if len(clean) > 6:
            issues.append(ErrorCodes.COA_MAX_DIGITS)

        return {"code": code, "valid": len(issues) == 0, "issues": issues}

    def validate_account(self, code: str) -> Result:
        account = self.repo.get_by_code(code)
        if not account:
            return Result.failure(VASValidationError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))

        issues: List[dict] = []

        fmt = self.validate_code_format(code)
        if not fmt["valid"]:
            issues.extend(fmt["issues"])

        if not account.vas_compliant:
            issues.append(ErrorCodes.COA_NON_COMPLIANT)

        if account.status == AccountStatus.CLOSED:
            issues.append(ErrorCodes.COA_CLOSED)

        parent_ok = True
        if account.parent_code:
            parent = self.repo.get_by_code(account.parent_code)
            if not parent:
                issues.append(ErrorCodes.COA_PARENT_MISSING)
                parent_ok = False
            elif parent.status != AccountStatus.ACTIVE:
                issues.append(ErrorCodes.COA_PARENT_INACTIVE)

        if parent_ok and account.parent_code:
            expected_parent_level = account.level - 1
            stmt = text("SELECT code, level FROM chart_of_accounts WHERE code = :code")
            rs = self.repo.session.execute(stmt, {"code": account.parent_code}).fetchone()
            if rs and rs.level != expected_parent_level:
                issues.append(ErrorCodes.COA_PARENT_LEVEL_MISMATCH)

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

            dcr_issues = self.validate_dcr_direction(acc)
            if dcr_issues:
                data["valid"] = False
                data["issues"].extend(dcr_issues)

            tt99_issues = self.validate_tt99_compliance(acc)
            if tt99_issues:
                data["valid"] = False
                data["issues"].extend(tt99_issues)

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

    def check_compliance(self, code: str) -> Result:
        """Run all compliance checks on a single account."""
        account = self.repo.get_by_code(code)
        if not account:
            return Result.failure(VASValidationError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))

        all_issues: List[str] = []

        fmt = self.validate_code_format(code)
        if not fmt["valid"]:
            all_issues.extend(fmt["issues"])

        all_issues.extend(self.validate_dcr_direction(account))
        all_issues.extend(self.validate_tt99_compliance(account))

        if account.parent_code:
            parent = self.repo.get_by_code(account.parent_code)
            if not parent:
                all_issues.append(ErrorCodes.COA_PARENT_MISSING)
            elif parent.level != account.level - 1:
                all_issues.append(ErrorCodes.COA_HIERARCHY_LEVEL_GAP)

        return Result.success({
            "code": code,
            "name": account.name,
            "compliant": len(all_issues) == 0,
            "issues": all_issues,
        })

    def run_compliance_scan(self) -> Result:
        """Full compliance scan of all accounts."""
        accounts = self.repo.list_all()
        results = []
        by_severity = {"error": 0, "warning": 0, "info": 0}

        rules_checked = [
            "code_format", "dcr_direction", "account_type",
            "hierarchy_levels", "parent_exists", "vas_compliant",
            "duplicate_codes", "missing_standard_accounts",
        ]

        seen_codes: set = set()
        dupes: set = set()
        for acc in accounts:
            if acc.code in seen_codes:
                dupes.add(acc.code)
            seen_codes.add(acc.code)

        for acc in accounts:
            entry = {
                "code": acc.code,
                "name": acc.name,
                "type": acc.account_type.value,
                "status": acc.status.value,
                "compliant": True,
                "issues": [],
            }

            fmt = self.validate_code_format(acc.code)
            if not fmt["valid"]:
                entry["compliant"] = False
                for i in fmt["issues"]:
                    entry["issues"].append({"rule": "code_format", "severity": "error", "message": i})
                    by_severity["error"] += 1

            dcr_issues = self.validate_dcr_direction(acc)
            for i in dcr_issues:
                entry["compliant"] = False
                entry["issues"].append({"rule": "dcr_direction", "severity": "error", "message": i})
                by_severity["error"] += 1

            tt99_issues = self.validate_tt99_compliance(acc)
            for i in tt99_issues:
                entry["compliant"] = False
                entry["issues"].append({"rule": "tt99_compliance", "severity": "warning", "message": i})
                by_severity["warning"] += 1

            if not acc.vas_compliant:
                entry["issues"].append({"rule": "vas_compliant", "severity": "warning", "message": ErrorCodes.COA_NON_COMPLIANT})
                by_severity["warning"] += 1

            if acc.code in dupes:
                entry["issues"].append({"rule": "duplicate_codes", "severity": "error", "message": ErrorCodes.COA_SCAN_DUPLICATE})
                by_severity["error"] += 1

            if acc.parent_code:
                parent = self.repo.get_by_code(acc.parent_code)
                if not parent:
                    entry["issues"].append({"rule": "parent_exists", "severity": "error", "message": ErrorCodes.COA_HIERARCHY_PARENT_MISSING})
                    by_severity["error"] += 1
                elif parent.level != acc.level - 1:
                    entry["issues"].append({"rule": "hierarchy_levels", "severity": "warning", "message": ErrorCodes.COA_HIERARCHY_LEVEL_GAP})
                    by_severity["warning"] += 1

            if not acc.name:
                entry["issues"].append({"rule": "missing_name", "severity": "warning", "message": ErrorCodes.COA_SCAN_NO_NAME})
                by_severity["warning"] += 1

            results.append(entry)

        compliant_count = sum(1 for r in results if r["compliant"])
        non_compliant_count = len(results) - compliant_count

        return Result.success({
            "summary": {
                "total_accounts": len(accounts),
                "compliant": compliant_count,
                "non_compliant": non_compliant_count,
                "compliance_pct": round(compliant_count / len(accounts) * 100, 2) if accounts else 100,
                "total_issues": sum(by_severity.values()),
                "by_severity": by_severity,
            },
            "rules_checked": rules_checked,
            "results": results,
        })

    def validate_dcr_direction(self, account: ChartOfAccounts) -> List[str]:
        """Check DCR direction matches account type convention."""
        issues: List[str] = []
        at = account.account_type.value

        debit_normal_keywords = {"asset", "cash", "bank", "inventory", "receivable",
                                 "prepaid", "investment", "deposit", "claim", "fixed",
                                 "intangible", "patent", "copyright", "goodwill",
                                 "expense", "vat", "cost", "provision"}
        credit_normal_keywords = {"liability", "equity", "capital", "retained",
                                  "revenue", "profit", "distribution", "surplus",
                                  "bond", "payable"}

        debit_words = [k for k in debit_normal_keywords if k in at]
        credit_words = [k for k in credit_normal_keywords if k in at]

        is_both = bool(debit_words) and bool(credit_words)

        expected = None
        if not is_both:
            if debit_words:
                expected = DCRDirection.DEBIT
            elif credit_words:
                expected = DCRDirection.CREDIT

        if expected and account.drcr_direction != expected:
            issues.append(ErrorCodes.COA_DCR_MISMATCH)
        return issues

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
                issues.append(ErrorCodes.COA_TT99_LEVEL)

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
                        "issue": ErrorCodes.COA_HIERARCHY_PARENT_MISSING
                    })
                elif parent.level != acc.level - 1:
                    errors.append({
                        "code": acc.code,
                        "name": acc.name,
                        "issue": ErrorCodes.COA_HIERARCHY_LEVEL_GAP
                    })

        return Result.success({"total_checked": len(accounts), "errors": errors})
