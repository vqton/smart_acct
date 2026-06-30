from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from domain.costing_center import (
    CostCenterType, DriverType, AllocationMethod, AllocationRunStatus,
    CostObjectType, VarianceType, RuleApprovalStatus,
    CostCenter, CostCenterCreate, CostCenterUpdate,
    CostDriver, CostDriverCreate,
    CostAllocationRuleTarget, CostAllocationRule, CostAllocationRuleCreate, CostAllocationRuleUpdate,
    CostAllocationLine, CostAllocationRun,
    CostObject, CostObjectCreate,
    CostAccumulation,
    CostCenterBudget, CostCenterActual, CostCenterVariance,
    CostingAuditLog, BulkImportResult, AccumulationResult, AllocationPreview,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, AccountError
from infrastructure.repositories.costing_center_repository import CostingCenterRepository
from infrastructure.models.gl_models import AccountingPeriodModel, JournalEntryModel, JournalLineModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _period_key_to_gl(pk: str) -> str:
    if len(pk) == 6:
        return f"{pk[:4]}-{pk[4:]}"
    return pk


class CostingCenterUseCases:
    def __init__(self, session: Session):
        self.repo = CostingCenterRepository(session)
        self._session = session

    def _validate_period_open(self, period_key: str) -> None:
        gl_period = _period_key_to_gl(period_key)
        p = self._session.query(AccountingPeriodModel).filter(
            AccountingPeriodModel.period == gl_period
        ).first()
        if p and p.is_closed:
            raise VASValidationError(ErrorCodes.COST_PERIOD_CLOSED, period=gl_period)

    def _get_cost_center_or_fail(self, cc_id: int) -> CostCenter:
        cc = self.repo.get_cost_center(cc_id)
        if not cc:
            raise VASValidationError(ErrorCodes.COST_CENTER_NOT_FOUND, cost_center_id=cc_id)
        return cc

    def _get_driver_or_fail(self, driver_id: int) -> CostDriver:
        d = self.repo.get_driver(driver_id)
        if not d:
            raise VASValidationError(ErrorCodes.COST_DRIVER_CODE_DUPLICATE, driver_id=driver_id)
        return d

    def _get_rule_or_fail(self, rule_id: int) -> CostAllocationRule:
        r = self.repo.get_rule(rule_id)
        if not r:
            raise VASValidationError(ErrorCodes.COST_RULE_NOT_FOUND, rule_id=rule_id)
        return r

    def _get_run_or_fail(self, run_id: int) -> CostAllocationRun:
        r = self.repo.get_allocation_run(run_id)
        if not r:
            raise VASValidationError(ErrorCodes.COST_RUN_NOT_FOUND, run_id=run_id)
        return r

    def _get_cost_object_or_fail(self, obj_id: int) -> CostObject:
        o = self.repo.get_cost_object(obj_id)
        if not o:
            raise VASValidationError(ErrorCodes.COST_OBJECT_NOT_FOUND, cost_object_id=obj_id)
        return o

    # ── UC-CC-01: Cost Center Hierarchy Management ─────────────────────

    def create_cost_center(self, data: dict) -> Result:
        try:
            cc_create = CostCenterCreate(**data)
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            cc = self.repo.create_cost_center(cc_create)
            self.repo.log_audit("CostCenter", cc.id, "CREATE", actor=data.get("created_by", "system"))
            return Result.success(cc)
        except VASValidationError as e:
            return Result.failure(e)

    def get_cost_center(self, cost_center_id: int) -> Result:
        try:
            cc = self._get_cost_center_or_fail(cost_center_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(cc)

    def update_cost_center(self, cost_center_id: int, data: dict) -> Result:
        try:
            self._get_cost_center_or_fail(cost_center_id)
            cc_update = CostCenterUpdate(**data)
        except VASValidationError as e:
            return Result.failure(e)
        try:
            cc = self.repo.update_cost_center(cost_center_id, cc_update)
            self.repo.log_audit("CostCenter", cost_center_id, "UPDATE", actor=data.get("updated_by", "system"))
            return Result.success(cc)
        except VASValidationError as e:
            return Result.failure(e)

    def deactivate_cost_center(self, cost_center_id: int, actor: str = "system") -> Result:
        try:
            self.repo.deactivate_cost_center(cost_center_id)
            self.repo.log_audit("CostCenter", cost_center_id, "DEACTIVATE", actor=actor)
            return Result.success({"id": cost_center_id, "is_active": False})
        except VASValidationError as e:
            return Result.failure(e)

    def move_cost_center(self, cost_center_id: int, new_parent_id: int, actor: str = "system") -> Result:
        try:
            cc = self.repo.move_cost_center(cost_center_id, new_parent_id)
            self.repo.log_audit("CostCenter", cost_center_id, "MOVE",
                                changes={"new_parent_id": new_parent_id}, actor=actor)
            return Result.success(cc)
        except VASValidationError as e:
            return Result.failure(e)

    def list_cost_centers(self, parent_id: Optional[int] = None, active_only: bool = True) -> Result:
        return Result.success(self.repo.list_cost_centers(parent_id=parent_id, active_only=active_only))

    def get_cost_center_tree(self, root_id: Optional[int] = None) -> Result:
        return Result.success(self.repo.get_cost_center_tree(root_id=root_id))

    def bulk_import_cost_centers(self, rows: List[dict], actor: str = "system") -> Result:
        result = self.repo.bulk_import_cost_centers(rows)
        self.repo.log_audit("CostCenter", 0, "BULK_IMPORT",
                            changes={"total": result.total_rows, "success": result.success_count,
                                     "errors": result.error_count}, actor=actor)
        return Result.success(result)

    # ── UC-CC-02: Cost Driver Management ────────────────────────────────

    def create_driver(self, data: dict) -> Result:
        try:
            driver = CostDriverCreate(**data)
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            d = self.repo.create_driver(driver)
            self.repo.log_audit("CostDriver", d.id, "CREATE", actor=data.get("created_by", "system"))
            return Result.success(d)
        except VASValidationError as e:
            return Result.failure(e)

    def get_driver(self, driver_id: int) -> Result:
        try:
            d = self._get_driver_or_fail(driver_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(d)

    def update_driver(self, driver_id: int, data: dict) -> Result:
        try:
            existing = self._get_driver_or_fail(driver_id)
            merged = {
                "code": existing.code,
                "name": existing.name,
                "driver_type": existing.driver_type.value if hasattr(existing.driver_type, 'value') else existing.driver_type,
                "source_module": existing.source_module,
                "source_account_code": existing.source_account_code,
                "unit_of_measure": existing.unit_of_measure,
                "formula": existing.formula,
                "is_active": existing.is_active,
            }
            merged.update(data)
            driver = CostDriverCreate(**merged)
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            d = self.repo.update_driver(driver_id, driver)
            self.repo.log_audit("CostDriver", driver_id, "UPDATE", actor=data.get("updated_by", "system"))
            return Result.success(d)
        except VASValidationError as e:
            return Result.failure(e)

    def delete_driver(self, driver_id: int, actor: str = "system") -> Result:
        try:
            self.repo.delete_driver(driver_id)
            self.repo.log_audit("CostDriver", driver_id, "DELETE", actor=actor)
            return Result.success({"id": driver_id, "deleted": True})
        except VASValidationError as e:
            return Result.failure(e)

    def list_drivers(self, active_only: bool = True) -> Result:
        return Result.success(self.repo.list_drivers(active_only=active_only))

    # ── UC-CC-03: Allocation Rule Configuration ─────────────────────────

    def create_rule(self, data: dict) -> Result:
        try:
            source = self._get_cost_center_or_fail(data.get("source_cost_center_id", 0))
            self._get_driver_or_fail(data.get("driver_id", 0))
            if not source.is_cost_collector:
                return Result.failure(AccountError(ErrorCodes.COST_CENTER_INACTIVE, cost_center_id=source.id))
            targets_data = data.pop("targets", [])
            target_cc_ids = [t.get("target_cost_center_id") for t in targets_data if t.get("target_cost_center_id")]
            rule = CostAllocationRuleCreate(
                targets=[CostAllocationRuleTarget(**t) for t in targets_data],
                **data,
            )
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            if self.repo.detect_circular_allocation(rule.source_cost_center_id, target_cc_ids):
                return Result.failure(AccountError(ErrorCodes.COST_ALLOCATION_CIRCULAR))
            r = self.repo.create_rule(rule)
            self.repo.log_audit("AllocationRule", r.id, "CREATE", actor=data.get("created_by", "system"))
            return Result.success(r)
        except VASValidationError as e:
            return Result.failure(e)

    def get_rule(self, rule_id: int) -> Result:
        try:
            r = self._get_rule_or_fail(rule_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(r)

    def update_rule(self, rule_id: int, data: dict) -> Result:
        try:
            self._get_rule_or_fail(rule_id)
            targets_data = data.pop("targets", None)
            targets = [CostAllocationRuleTarget(**t) for t in targets_data] if targets_data else None
            rule = CostAllocationRuleUpdate(
                targets=targets,
                **data,
            )
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            r = self.repo.update_rule(rule_id, rule)
            self.repo.log_audit("AllocationRule", rule_id, "UPDATE", actor=data.get("updated_by", "system"))
            return Result.success(r)
        except VASValidationError as e:
            return Result.failure(e)

    def approve_rule(self, rule_id: int, approved_by: str) -> Result:
        try:
            self._get_rule_or_fail(rule_id)
            r = self.repo.approve_rule(rule_id, approved_by)
            self.repo.log_audit("AllocationRule", rule_id, "APPROVE", actor=approved_by)
            return Result.success(r)
        except VASValidationError as e:
            return Result.failure(e)

    def archive_rule(self, rule_id: int, actor: str = "system") -> Result:
        try:
            self._get_rule_or_fail(rule_id)
            self.repo.archive_rule(rule_id)
            self.repo.log_audit("AllocationRule", rule_id, "ARCHIVE", actor=actor)
            return Result.success({"id": rule_id, "archived": True})
        except VASValidationError as e:
            return Result.failure(e)

    def list_rules(self, source_cc_id: Optional[int] = None,
                   status: Optional[str] = None,
                   period_key: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_rules(source_cc_id=source_cc_id, status=status, period_key=period_key))

    def get_allocation_preview(self, rule_id: int, period_key: str) -> Result:
        try:
            rule = self._get_rule_or_fail(rule_id)
            if rule.approval_status != RuleApprovalStatus.approved:
                return Result.failure(AccountError(ErrorCodes.COST_RULE_NOT_APPROVED, rule_id=rule_id))
        except VASValidationError as e:
            return Result.failure(e)

        source_amount = self.repo.get_driver_value(rule.driver_id, rule.source_cost_center_id, period_key)
        if source_amount <= Decimal("0"):
            return Result.success(AllocationPreview(
                rule_id=rule.id, rule_code=rule.rule_code,
                source_cost_center_id=rule.source_cost_center_id,
                source_amount=source_amount,
                lines=[], total_allocated=Decimal("0"),
            ))

        total_driver = Decimal("0")
        driver_values: Dict[int, Decimal] = {}
        for t in rule.targets:
            dv = self.repo.get_driver_value(rule.driver_id, t.target_cost_center_id, period_key)
            driver_values[t.target_cost_center_id] = dv
            total_driver += dv

        lines = []
        total_allocated = Decimal("0")
        for t in rule.targets:
            if rule.allocation_method == AllocationMethod.direct:
                amt = source_amount / Decimal(max(len(rule.targets), 1))
            elif rule.allocation_method == AllocationMethod.percentage:
                pct = t.percentage or Decimal("0")
                amt = _vnd(source_amount * pct / Decimal("100"))
            else:
                dv = driver_values.get(t.target_cost_center_id, Decimal("0"))
                if total_driver > 0:
                    amt = _vnd(source_amount * dv / total_driver)
                else:
                    amt = _vnd(source_amount / Decimal(max(len(rule.targets), 1)))

            total_allocated += amt
            lines.append(CostAllocationLine(
                source_cost_center_id=rule.source_cost_center_id,
                target_cost_center_id=t.target_cost_center_id,
                rule_id=rule.id,
                driver_id=rule.driver_id,
                gl_account_code=rule.gl_debit_account_code,
                original_amount=source_amount,
                allocated_amount=amt,
                driver_quantity=dv if rule.allocation_method == AllocationMethod.proportional else None,
                driver_rate=_vnd(amt / dv) if rule.allocation_method == AllocationMethod.proportional and dv > 0 else None,
                allocation_basis_description=f"{rule.allocation_method.value} allocation",
            ))

        return Result.success(AllocationPreview(
            rule_id=rule.id, rule_code=rule.rule_code,
            source_cost_center_id=rule.source_cost_center_id,
            source_amount=source_amount,
            lines=lines, total_allocated=total_allocated,
        ))

    # ── UC-CC-04: Allocation Execution ──────────────────────────────────

    def execute_allocation(self, period_key: str, run_by: str, dry_run: bool = False) -> Result:
        try:
            self._validate_period_open(period_key)
        except VASValidationError as e:
            return Result.failure(e)

        existing = self.repo.get_allocation_run_by_period(period_key)
        if existing and existing.status == AllocationRunStatus.posted and not dry_run:
            return Result.failure(AccountError(ErrorCodes.COST_RUN_ALREADY_POSTED, run_id=existing.id))

        rules = self.repo.get_active_rules_for_period(period_key)
        if not rules:
            return Result.failure(AccountError(ErrorCodes.COST_NO_RULES_FOR_PERIOD, period_key=period_key))

        if dry_run:
            previews = []
            for rule in rules:
                preview = self.get_allocation_preview(rule.id, period_key)
                if preview.is_success():
                    previews.append(preview.get_data())
            return Result.success({"period_key": period_key, "rule_count": len(rules), "previews": previews})

        run = self.repo.create_allocation_run(period_key, run_by)
        all_lines: List[CostAllocationLine] = []
        total_allocated = Decimal("0")

        for rule in rules:
            if rule.approval_status != RuleApprovalStatus.approved:
                continue
            source_amount = self.repo.get_driver_value(rule.driver_id, rule.source_cost_center_id, period_key)
            if source_amount <= Decimal("0"):
                continue

            total_driver = Decimal("0")
            driver_values: Dict[int, Decimal] = {}
            for t in rule.targets:
                dv = self.repo.get_driver_value(rule.driver_id, t.target_cost_center_id, period_key)
                driver_values[t.target_cost_center_id] = dv
                total_driver += dv

            for t in rule.targets:
                if rule.allocation_method == AllocationMethod.direct:
                    amt = _vnd(source_amount / Decimal(max(len(rule.targets), 1)))
                elif rule.allocation_method == AllocationMethod.percentage:
                    pct = t.percentage or Decimal("0")
                    amt = _vnd(source_amount * pct / Decimal("100"))
                else:
                    dv = driver_values.get(t.target_cost_center_id, Decimal("0"))
                    amt = _vnd(source_amount * dv / total_driver) if total_driver > 0 else Decimal("0")

                total_allocated += amt
                all_lines.append(CostAllocationLine(
                    source_cost_center_id=rule.source_cost_center_id,
                    target_cost_center_id=t.target_cost_center_id,
                    rule_id=rule.id,
                    driver_id=rule.driver_id,
                    gl_account_code=rule.gl_debit_account_code,
                    original_amount=source_amount,
                    allocated_amount=amt,
                    driver_quantity=driver_values.get(t.target_cost_center_id) if rule.allocation_method == AllocationMethod.proportional else None,
                    driver_rate=_vnd(amt / driver_values[t.target_cost_center_id]) if rule.allocation_method == AllocationMethod.proportional and driver_values.get(t.target_cost_center_id, Decimal("0")) > 0 else None,
                    allocation_basis_description=f"Rule {rule.rule_code} - {rule.allocation_method.value}",
                ))

        self.repo.save_allocation_lines(run.id, all_lines)
        run.total_allocated_amount = total_allocated
        self._session.flush()

        self.repo.log_audit("AllocationRun", run.id, "EXECUTE",
                            changes={"period_key": period_key, "total_allocated": str(total_allocated),
                                     "lines": len(all_lines)}, actor=run_by)
        return Result.success(self.repo.get_allocation_run(run.id))

    def post_allocation_run(self, run_id: int, posted_by: str) -> Result:
        try:
            run = self._get_run_or_fail(run_id)
            if run.status == AllocationRunStatus.posted:
                return Result.failure(AccountError(ErrorCodes.COST_RUN_ALREADY_POSTED, run_id=run_id))
        except VASValidationError as e:
            return Result.failure(e)

        try:
            self._validate_period_open(run.period_key)
        except VASValidationError as e:
            return Result.failure(e)

        lines = self.repo.get_allocation_lines(run_id)
        if not lines:
            return Result.failure(AccountError(ErrorCodes.COST_NO_RULES_FOR_PERIOD, period_key=run.period_key))

        gl_period = _period_key_to_gl(run.period_key)

        for line in lines:
            if line.allocated_amount <= Decimal("0"):
                continue
            y, m = int(run.period_key[:4]), int(run.period_key[4:])
            je = JournalEntryModel(
                journal_number=f"CC-ALLOC-{run.period_key}-{run.id}-{line.id}",
                transaction_date=date(y, m, 1),
                description=f"CC allocation: {run.run_code} line {line.id}",
                period=gl_period,
                is_posted=True,
                posted_date=datetime.now(timezone.utc),
                source_module="costing_center",
                created_by=posted_by,
                created_at=datetime.now(timezone.utc),
            )
            self._session.add(je)
            self._session.flush()

            debit = JournalLineModel(
                journal_entry_id=je.id,
                account_id=line.gl_account_code,
                debit=line.allocated_amount,
                credit=Decimal("0"),
                period=gl_period,
                description=f"Allocation to CC {line.target_cost_center_id}",
            )
            self._session.add(debit)

            source_cc = self.repo.get_cost_center(line.source_cost_center_id)
            credit_acct = source_cc.gl_account_code if source_cc and source_cc.gl_account_code else line.gl_account_code
            credit_line = JournalLineModel(
                journal_entry_id=je.id,
                account_id=credit_acct,
                debit=Decimal("0"),
                credit=line.allocated_amount,
                period=gl_period,
                description=f"Allocation from CC {line.source_cost_center_id}",
            )
            self._session.add(credit_line)

        self.repo._set_run_status(run_id, AllocationRunStatus.posted)
        self._session.flush()

        self.repo.log_audit("AllocationRun", run_id, "POST", actor=posted_by)
        return Result.success(self.repo.get_allocation_run(run_id))

    def reverse_allocation_run(self, run_id: int, reversed_by: str) -> Result:
        try:
            run = self._get_run_or_fail(run_id)
            if run.status != AllocationRunStatus.posted:
                return Result.failure(AccountError(ErrorCodes.COST_RUN_NOT_FOUND, run_id=run_id))
        except VASValidationError as e:
            return Result.failure(e)

        try:
            self._validate_period_open(run.period_key)
        except VASValidationError as e:
            return Result.failure(e)

        lines = self.repo.get_allocation_lines(run_id)
        gl_period = _period_key_to_gl(run.period_key)

        for line in lines:
            if line.allocated_amount <= Decimal("0"):
                continue
            y, m = int(run.period_key[:4]), int(run.period_key[4:])
            je = JournalEntryModel(
                journal_number=f"CC-REV-{run.period_key}-{run.id}-{line.id}",
                transaction_date=date(y, m, 1),
                description=f"CC allocation reversal: {run.run_code} line {line.id}",
                period=gl_period,
                is_posted=True,
                posted_date=datetime.now(timezone.utc),
                source_module="costing_center",
                created_by=reversed_by,
                created_at=datetime.now(timezone.utc),
            )
            self._session.add(je)
            self._session.flush()

            source_cc = self.repo.get_cost_center(line.source_cost_center_id)
            credit_acct = source_cc.gl_account_code if source_cc and source_cc.gl_account_code else line.gl_account_code

            reverse_debit = JournalLineModel(
                journal_entry_id=je.id,
                account_id=credit_acct,
                debit=line.allocated_amount,
                credit=Decimal("0"),
                period=gl_period,
                description=f"Reverse allocation from CC {line.source_cost_center_id}",
            )
            self._session.add(reverse_debit)

            reverse_credit = JournalLineModel(
                journal_entry_id=je.id,
                account_id=line.gl_account_code,
                debit=Decimal("0"),
                credit=line.allocated_amount,
                period=gl_period,
                description=f"Reverse allocation to CC {line.target_cost_center_id}",
            )
            self._session.add(reverse_credit)

        self.repo._set_run_status(run_id, AllocationRunStatus.reversed)
        self._session.flush()

        self.repo.log_audit("AllocationRun", run_id, "REVERSE", actor=reversed_by)
        return Result.success(self.repo.get_allocation_run(run_id))

    def get_allocation_run(self, run_id: int) -> Result:
        try:
            run = self._get_run_or_fail(run_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(run)

    def list_allocation_runs(self, period_key: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_allocation_runs(period_key=period_key))

    def get_allocation_matrix(self, period_key: str) -> Result:
        return Result.success(self.repo.get_allocation_matrix(period_key))

    # ── UC-CC-05: Cost Object Management ────────────────────────────────

    def create_cost_object(self, data: dict) -> Result:
        try:
            obj = CostObjectCreate(**data)
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            o = self.repo.create_cost_object(obj)
            self.repo.log_audit("CostObject", o.id, "CREATE", actor=data.get("created_by", "system"))
            return Result.success(o)
        except VASValidationError as e:
            return Result.failure(e)

    def get_cost_object(self, cost_object_id: int) -> Result:
        try:
            o = self._get_cost_object_or_fail(cost_object_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(o)

    def update_cost_object(self, cost_object_id: int, data: dict) -> Result:
        try:
            existing = self._get_cost_object_or_fail(cost_object_id)
            merged = {
                "code": existing.code,
                "name": existing.name,
                "object_type": existing.object_type.value if hasattr(existing.object_type, 'value') else existing.object_type,
                "parent_object_id": existing.parent_object_id,
                "gl_account_code": existing.gl_account_code,
                "external_ref_id": existing.external_ref_id,
                "external_ref_type": existing.external_ref_type,
                "is_active": existing.is_active,
                "custom_attributes": existing.custom_attributes,
            }
            merged.update(data)
            obj = CostObjectCreate(**merged)
        except (VASValidationError, ValueError) as e:
            return Result.failure(e)
        try:
            o = self.repo.update_cost_object(cost_object_id, obj)
            self.repo.log_audit("CostObject", cost_object_id, "UPDATE", actor=data.get("updated_by", "system"))
            return Result.success(o)
        except VASValidationError as e:
            return Result.failure(e)

    def delete_cost_object(self, cost_object_id: int, actor: str = "system") -> Result:
        try:
            self._get_cost_object_or_fail(cost_object_id)
            self.repo.delete_cost_object(cost_object_id)
            self.repo.log_audit("CostObject", cost_object_id, "DELETE", actor=actor)
            return Result.success({"id": cost_object_id, "deleted": True})
        except VASValidationError as e:
            return Result.failure(e)

    def list_cost_objects(self, object_type: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_cost_objects(object_type=object_type))

    # ── UC-CC-06: Cost Accumulation ─────────────────────────────────────

    def accumulate_costs(self, period_key: str) -> Result:
        try:
            result = self.repo.accumulate_costs(period_key)
            self.repo.log_audit("CostAccumulation", 0, "ACCUMULATE",
                                changes={"period_key": period_key, "total_lines": result.total_lines},
                                actor="system")
            return Result.success(result)
        except VASValidationError as e:
            return Result.failure(e)

    def get_accumulated_costs(self, cost_object_id: int, period_key: str) -> Result:
        return Result.success(self.repo.get_accumulated_costs(cost_object_id, period_key))

    # ── UC-CC-07: Budget Integration ────────────────────────────────────

    def sync_budget(self, period_key: str) -> Result:
        count = self.repo.sync_budget_data(period_key)
        self.repo.log_audit("CostCenterBudget", 0, "SYNC",
                            changes={"period_key": period_key, "lines_synced": count}, actor="system")
        return Result.success({"period_key": period_key, "lines_synced": count})

    def get_budget(self, cost_center_id: int, period_key: str) -> Result:
        try:
            self._get_cost_center_or_fail(cost_center_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(self.repo.get_budget(cost_center_id, period_key))

    # ── UC-CC-08: Variance Analysis ─────────────────────────────────────

    def compute_variance(self, cost_center_id: int, period_key: str) -> Result:
        try:
            self._get_cost_center_or_fail(cost_center_id)
        except VASValidationError as e:
            return Result.failure(e)
        variances = self.repo.compute_variance(cost_center_id, period_key)
        return Result.success(variances)

    def get_cc_pl(self, cost_center_id: int, period_key: str) -> Result:
        try:
            self._get_cost_center_or_fail(cost_center_id)
        except VASValidationError as e:
            return Result.failure(e)
        return Result.success(self.repo.get_cc_pl(cost_center_id, period_key))

    # ── UC-CC-09: GL Integration ────────────────────────────────────────

    def validate_cost_center_for_je(self, cost_center_id: int, gl_account_code: str) -> Result:
        try:
            cc = self._get_cost_center_or_fail(cost_center_id)
            if not cc.is_active:
                return Result.failure(AccountError(ErrorCodes.COST_CENTER_INACTIVE, cost_center_id=cost_center_id))
            if cc.gl_account_code and cc.gl_account_code != gl_account_code:
                pass
            return Result.success(True)
        except VASValidationError as e:
            return Result.failure(e)

    # ── UC-CC-10: Cost Center P&L Report ────────────────────────────────

    def report_cc_pl(self, cost_center_id: int, period_key: str, include_children: bool = False) -> Result:
        try:
            cc = self._get_cost_center_or_fail(cost_center_id)
        except VASValidationError as e:
            return Result.failure(e)

        if include_children:
            tree = self.repo.get_cost_center_tree(root_id=cost_center_id)
            child_ids = self._collect_child_ids(tree)
            reports = []
            for cid in [cost_center_id] + child_ids:
                reports.append(self.repo.get_cc_pl(cid, period_key))
            return Result.success({"cost_center_id": cost_center_id, "period_key": period_key,
                                   "include_children": True, "reports": reports})

        return Result.success(self.repo.get_cc_pl(cost_center_id, period_key))

    def _collect_child_ids(self, tree: List[Dict]) -> List[int]:
        ids = []
        for node in tree:
            ids.append(node["id"])
            ids.extend(self._collect_child_ids(node.get("children", [])))
        return ids

    # ── UC-CC-11: Allocation Summary Report ──────────────────────────────

    def report_allocation_summary(self, period_key: str) -> Result:
        matrix = self.repo.get_allocation_matrix(period_key)
        runs = self.repo.list_allocation_runs(period_key=period_key)
        total_allocated = sum(
            _vnd(Decimal(str(r.total_allocated_amount))) for r in runs if r.total_allocated_amount
        )
        return Result.success({
            "period_key": period_key,
            "runs": runs,
            "matrix": matrix,
            "total_allocated": str(total_allocated),
            "rules_executed": sum(len(r.lines) for r in runs),
        })

    # ── UC-CC-12: Import/Export ──────────────────────────────────────────

    def export_cost_centers(self, active_only: bool = True) -> Result:
        ccs = self.repo.list_cost_centers(active_only=active_only)
        rows = []
        for cc in ccs:
            parent = self.repo.get_cost_center(cc.parent_id) if cc.parent_id else None
            rows.append({
                "code": cc.code, "name": cc.name, "type": cc.cost_center_type.value,
                "parent_code": parent.code if parent else "",
                "level": cc.level, "path": cc.path,
                "is_active": cc.is_active, "is_cost_collector": cc.is_cost_collector,
                "gl_account_code": cc.gl_account_code or "",
                "department_code": cc.department_code or "",
                "valid_from": cc.valid_from.isoformat(),
                "valid_to": cc.valid_to.isoformat() if cc.valid_to else "",
            })
        return Result.success(rows)

    def export_cost_objects(self, object_type: Optional[str] = None) -> Result:
        objs = self.repo.list_cost_objects(object_type=object_type)
        rows = []
        for o in objs:
            rows.append({
                "code": o.code, "name": o.name, "object_type": o.object_type.value,
                "gl_account_code": o.gl_account_code or "",
                "is_active": o.is_active,
            })
        return Result.success(rows)

    # ── UC-CC-13: Audit Trail ───────────────────────────────────────────

    def get_audit_logs(self, entity_type: Optional[str] = None,
                        entity_id: Optional[int] = None,
                        limit: int = 100, offset: int = 0) -> Result:
        return Result.success(self.repo.get_audit_logs(
            entity_type=entity_type, entity_id=entity_id, limit=limit, offset=offset))

    # ── UC-CC-14: Dashboard & KPIs ──────────────────────────────────────

    def dashboard_summary(self) -> Result:
        ccs = self.repo.list_cost_centers(active_only=False)
        active_ccs = [c for c in ccs if c.is_active]
        rules = self.repo.list_rules()
        approved_rules = [r for r in rules if r.approval_status == RuleApprovalStatus.approved]
        cost_collectors = [c for c in active_ccs if c.is_cost_collector]
        rules_covering_ccs = set()
        for r in approved_rules:
            rules_covering_ccs.add(r.source_cost_center_id)
            for t in r.targets:
                rules_covering_ccs.add(t.target_cost_center_id)

        total_ccs = len(ccs)
        active_count = len(active_ccs)
        rule_coverage = round(len(rules_covering_ccs) / max(len(cost_collectors), 1) * 100, 1)
        unallocated_ccs = len([c for c in cost_collectors if c.id not in rules_covering_ccs])

        return Result.success({
            "total_cost_centers": total_ccs,
            "active_cost_centers": active_count,
            "total_rules": len(rules),
            "approved_rules": len(approved_rules),
            "cost_collectors": len(cost_collectors),
            "rule_coverage_pct": rule_coverage,
            "unallocated_cost_centers": unallocated_ccs,
            "max_depth": max(c.level for c in ccs) if ccs else 0,
            "by_type": {t.value: len([c for c in ccs if c.cost_center_type == t]) for t in CostCenterType},
        })

    # ── UC-CC-15: Self-Service ──────────────────────────────────────────

    def get_manager_cost_centers(self, employee_id: int) -> Result:
        all_ccs = self.repo.list_cost_centers(active_only=True)
        managed = [c for c in all_ccs if c.manager_employee_id == employee_id]
        return Result.success(managed)

    def get_manager_dashboard(self, employee_id: int, period_key: str) -> Result:
        managed = self.repo.list_cost_centers(active_only=True)
        my_ccs = [c for c in managed if c.manager_employee_id == employee_id]
        reports = []
        for cc in my_ccs:
            pl = self.repo.get_cc_pl(cc.id, period_key)
            reports.append(pl)
        return Result.success({
            "employee_id": employee_id,
            "period_key": period_key,
            "managed_cost_centers": len(my_ccs),
            "reports": reports,
        })
