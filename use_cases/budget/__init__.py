from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import select, func as sqlfunc
from domain import (
    BudgetType, BudgetVersionStatus, BudgetPeriodType,
    BudgetControlLevel, BudgetDimensionType, BudgetCategoryType,
    ApprovalStatus, VarianceFlag, KPIThreshold,
)
from domain.budget import AdjustmentType as BudgetAdjustmentType
from domain import (
    BudgetStructure, BudgetDimension, BudgetCategory,
    BudgetCalendar, BudgetCalendarPhase, BudgetPeriod,
    BudgetTemplate, BudgetTemplateLine,
    BudgetVersion, BudgetPlan, BudgetPlanLine, BudgetPlanDriver,
    BudgetApprovalWorkflow, BudgetApprovalStep, BudgetApprovalLog,
    BudgetAdjustment, BudgetAdjustmentLine,
    BudgetCommitment, BudgetExecutionItem,
    BudgetControlRule, BudgetOverride, BudgetBlockLog,
    BudgetConsolidation, BudgetConsolidationEntity, BudgetICTransaction,
    BudgetVarianceReport, BudgetVarianceLine, BudgetVarianceAnnotation,
    BudgetKPI, BudgetKPIValue, BudgetDashboard,
    CAPEXRequest, CashFlowBudgetLine, CashFlowFinancing,
    RevenueBudgetLine, RevenueBudgetDriver, RevenueSeasonality,
    HeadcountBudget, ExpenseBudgetLine,
    Result, VASValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.budget_repository import BudgetRepository


class BudgetUseCases:
    def __init__(self, session: Session):
        self.session = session
        self.repo = BudgetRepository(session)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-01: Budget Master & Structure
    # ═══════════════════════════════════════════════════════════════

    def create_budget_structure(self, fiscal_year: int, name: str,
                                budget_types: Optional[List[BudgetType]] = None,
                                dimensions: Optional[List[BudgetDimensionType]] = None,
                                period_type: BudgetPeriodType = BudgetPeriodType.MONTHLY) -> Result:
        entity = BudgetStructure(
            fiscal_year=fiscal_year, name=name,
            budget_types=budget_types or [BudgetType.REVENUE, BudgetType.EXPENSE],
            dimensions=dimensions or [BudgetDimensionType.COST_CENTER, BudgetDimensionType.DEPARTMENT],
            period_type=period_type,
        )
        result = self.repo.create_structure(entity)
        if result.is_success():
            self.repo.log_audit("budget_structure", entity.id, "create", "system")
        return result

    def get_budget_structure(self, structure_id: int) -> Optional[BudgetStructure]:
        return self.repo.get_structure(structure_id)

    def get_budget_structure_by_year(self, fiscal_year: int) -> Optional[BudgetStructure]:
        return self.repo.get_structure_by_fiscal_year(fiscal_year)

    def list_budget_structures(self) -> List[BudgetStructure]:
        return self.repo.list_structures()

    def update_budget_structure(self, structure_id: int, **updates) -> Optional[BudgetStructure]:
        result = self.repo.update_structure(structure_id, **updates)
        if result:
            self.repo.log_audit("budget_structure", structure_id, "update", "system",
                                {"updates": list(updates.keys())})
        return result

    def create_budget_category(self, structure_id: int, budget_type: BudgetType,
                                name: str, category_type: BudgetCategoryType = BudgetCategoryType.VARIABLE,
                                gl_account_codes: Optional[List[str]] = None) -> Result:
        entity = BudgetCategory(
            structure_id=structure_id, budget_type=budget_type, name=name,
            category_type=category_type, gl_account_codes=gl_account_codes or [],
        )
        result = self.repo.create_category(entity)
        if result.is_success():
            self.repo.log_audit("budget_category", entity.id, "create", "system")
        return result

    def list_budget_categories(self, structure_id: int) -> List[BudgetCategory]:
        return self.repo.list_categories(structure_id)

    def create_budget_dimension(self, structure_id: int, dim_type: BudgetDimensionType,
                                code: str, name: str) -> Result:
        entity = BudgetDimension(structure_id=structure_id, dimension_type=dim_type, code=code, name=name)
        return self.repo.create_dimension(entity)

    def list_budget_dimensions(self, structure_id: int,
                               dim_type: Optional[BudgetDimensionType] = None) -> List[BudgetDimension]:
        return self.repo.list_dimensions(structure_id, dim_type)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-02: Budget Period & Calendar
    # ═══════════════════════════════════════════════════════════════

    def create_budget_calendar(self, fiscal_year: int, name: str,
                               phases: Optional[List[Dict]] = None) -> Result:
        cal_phases = []
        if phases:
            for ph in phases:
                cal_phases.append(BudgetCalendarPhase(
                    calendar_id=0, phase_name=ph["name"],
                    start_date=ph["start_date"], end_date=ph["end_date"],
                    phase_order=ph.get("order", 0),
                ))
        entity = BudgetCalendar(fiscal_year=fiscal_year, name=name, phases=cal_phases)
        result = self.repo.create_calendar(entity)
        if result.is_success():
            self._auto_create_periods(entity.id, fiscal_year)
            self.repo.log_audit("budget_calendar", entity.id, "create", "system")
        return result

    def _auto_create_periods(self, calendar_id: int, fiscal_year: int):
        months = [
            ("01", date(fiscal_year, 1, 1), date(fiscal_year, 1, 31)),
            ("02", date(fiscal_year, 2, 1), date(fiscal_year, 2, 28 if fiscal_year % 4 != 0 else 29)),
            ("03", date(fiscal_year, 3, 1), date(fiscal_year, 3, 31)),
            ("04", date(fiscal_year, 4, 1), date(fiscal_year, 4, 30)),
            ("05", date(fiscal_year, 5, 1), date(fiscal_year, 5, 31)),
            ("06", date(fiscal_year, 6, 1), date(fiscal_year, 6, 30)),
            ("07", date(fiscal_year, 7, 1), date(fiscal_year, 7, 31)),
            ("08", date(fiscal_year, 8, 1), date(fiscal_year, 8, 31)),
            ("09", date(fiscal_year, 9, 1), date(fiscal_year, 9, 30)),
            ("10", date(fiscal_year, 10, 1), date(fiscal_year, 10, 31)),
            ("11", date(fiscal_year, 11, 1), date(fiscal_year, 11, 30)),
            ("12", date(fiscal_year, 12, 1), date(fiscal_year, 12, 31)),
        ]
        for mm, start, end in months:
            p = BudgetPeriod(
                calendar_id=calendar_id, period_key=f"{fiscal_year}-{mm}",
                period_type=BudgetPeriodType.MONTHLY,
                start_date=start, end_date=end,
            )
            self.repo.create_period(p)

    def get_budget_calendar(self, fiscal_year: int) -> Optional[BudgetCalendar]:
        return self.repo.get_calendar_by_year(fiscal_year)

    def list_budget_periods(self, calendar_id: int) -> List[BudgetPeriod]:
        return self.repo.list_periods(calendar_id)

    def close_budget_period(self, period_id: int) -> Optional[BudgetPeriod]:
        return self.repo.close_period(period_id)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-03: Budget Template
    # ═══════════════════════════════════════════════════════════════

    def create_budget_template(self, name: str, budget_type: BudgetType,
                               lines: Optional[List[Dict]] = None,
                               description: Optional[str] = None) -> Result:
        template_lines = []
        if lines:
            for i, l in enumerate(lines):
                template_lines.append(BudgetTemplateLine(
                    template_id=0, line_order=l.get("order", i),
                    gl_account_code=l["gl_account_code"], name=l["name"],
                    category_type=BudgetCategoryType(l.get("category_type", "variable")),
                    formula=l.get("formula"), is_required=l.get("is_required", False),
                    default_amount=Decimal(str(l.get("default_amount", "0"))),
                    notes=l.get("notes"),
                ))
        entity = BudgetTemplate(
            name=name, description=description, budget_type=budget_type,
            lines=template_lines,
        )
        result = self.repo.create_template(entity)
        if result.is_success():
            self.repo.log_audit("budget_template", entity.id, "create", "system")
        return result

    def get_budget_template(self, template_id: int) -> Optional[BudgetTemplate]:
        return self.repo.get_template(template_id)

    def list_budget_templates(self, budget_type: Optional[BudgetType] = None) -> List[BudgetTemplate]:
        return self.repo.list_templates(budget_type)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-04: Budget Plan (Draft)
    # ═══════════════════════════════════════════════════════════════

    def create_budget_version(self, fiscal_year: int, label: str,
                              version_number: Optional[str] = None,
                              parent_version_id: Optional[int] = None,
                              created_by: Optional[str] = None) -> Result:
        vn = version_number or f"v{fiscal_year}.1"
        entity = BudgetVersion(
            fiscal_year=fiscal_year, version_number=vn, label=label,
            status=BudgetVersionStatus.DRAFT, parent_version_id=parent_version_id,
            created_by=created_by,
        )
        result = self.repo.create_version(entity)
        if result.is_success():
            self.repo.log_audit("budget_version", entity.id, "create", "system")
        return result

    def get_active_budget_version(self, fiscal_year: int) -> Optional[BudgetVersion]:
        return self.repo.get_active_version(fiscal_year)

    def list_budget_versions(self, fiscal_year: int) -> List[BudgetVersion]:
        return self.repo.list_versions(fiscal_year)

    def create_budget_plan(self, version_id: int, structure_id: int,
                           dimension_type: BudgetDimensionType, dimension_code: str,
                           lines: Optional[List[Dict]] = None,
                           created_by: Optional[str] = None) -> Result:
        plan_lines = []
        if lines:
            for l in lines:
                driver = None
                if l.get("driver"):
                    d = l["driver"]
                    driver = BudgetPlanDriver(
                        plan_line_id=0, quantity=Decimal(str(d.get("quantity", "0"))),
                        unit_rate=Decimal(str(d.get("unit_rate", "0"))),
                        driver_name=d.get("driver_name"),
                    )
                plan_lines.append(BudgetPlanLine(
                    plan_id=0, gl_account_code=l["gl_account_code"], name=l["name"],
                    category_type=BudgetCategoryType(l.get("category_type", "variable")),
                    amounts=l.get("amounts", {}), driver=driver, notes=l.get("notes"),
                ))
        entity = BudgetPlan(
            version_id=version_id, structure_id=structure_id,
            dimension_type=dimension_type, dimension_code=dimension_code,
            lines=plan_lines, created_by=created_by,
        )
        result = self.repo.create_plan(entity)
        if result.is_success():
            self.repo.log_audit("budget_plan", entity.id, "create", "system")
        return result

    def get_budget_plan(self, plan_id: int) -> Optional[BudgetPlan]:
        return self.repo.get_plan(plan_id)

    def get_budget_plan_by_dimension(self, version_id: int, dim_type: BudgetDimensionType,
                                     dim_code: str) -> Optional[BudgetPlan]:
        return self.repo.get_plan_by_dimension(version_id, dim_type, dim_code)

    def list_budget_plans(self, version_id: int) -> List[BudgetPlan]:
        return self.repo.list_plans(version_id)

    def update_budget_plan(self, plan_id: int, lines: List[Dict]) -> Optional[BudgetPlan]:
        plan = self.repo.get_plan(plan_id)
        if not plan:
            return None
        domain_lines = []
        for l in lines:
            driver = None
            if l.get("driver"):
                d = l["driver"]
                driver = BudgetPlanDriver(
                    plan_line_id=0, quantity=Decimal(str(d.get("quantity", "0"))),
                    unit_rate=Decimal(str(d.get("unit_rate", "0"))),
                    driver_name=d.get("driver_name"),
                )
            domain_lines.append(BudgetPlanLine(
                plan_id=0, gl_account_code=l["gl_account_code"], name=l["name"],
                category_type=BudgetCategoryType(l.get("category_type", "variable")),
                amounts=l.get("amounts", {}), driver=driver, notes=l.get("notes"),
            ))
        result = self.repo.update_plan_lines(plan_id, domain_lines)
        if result:
            self.repo.log_audit("budget_plan", plan_id, "update", "system")
        return result

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-05: Budget Approval Workflow
    # ═══════════════════════════════════════════════════════════════

    def submit_budget_for_approval(self, plan_id: int, steps: List[Dict],
                                   submitted_by: str) -> Result:
        plan = self.repo.get_plan(plan_id)
        if not plan:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_PLAN_NOT_FOUND))
        # Check version is Draft
        version = self.repo.get_version(plan.version_id)
        if version and version.is_locked:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_IN_LOCKED_WORKFLOW))
        # Update version status
        if version:
            self.repo.update_version_status(version.id, BudgetVersionStatus.PROPOSED)
        # Create workflow
        domain_steps = []
        for i, s in enumerate(steps):
            domain_steps.append(BudgetApprovalStep(
                workflow_id=0, step_order=i + 1,
                approver_role=s["role"], approver_name=s.get("name"),
                min_approvers=s.get("min_approvers", 1),
                status=ApprovalStatus.PENDING,
            ))
        workflow = BudgetApprovalWorkflow(plan_id=plan_id, steps=domain_steps,
                                          status=BudgetVersionStatus.PROPOSED)
        result = self.repo.create_workflow(workflow)
        if result.is_success():
            self.repo.log_audit("budget_workflow", workflow.id, "submit", submitted_by)
        return result

    def approve_budget(self, step_id: int, actor: str,
                       comments: Optional[str] = None) -> Result:
        step = self.repo.approve_step(step_id, actor, comments)
        if not step:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_WORKFLOW_NOT_FOUND))
        return Result.success(step)

    def reject_budget(self, step_id: int, actor: str, comments: str) -> Result:
        step = self.repo.reject_step(step_id, actor, comments)
        if not step:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_WORKFLOW_NOT_FOUND))
        return Result.success(step)

    def finalize_approval(self, workflow_id: int, plan_id: int, actor: str) -> Result:
        workflow = self.repo.get_workflow(workflow_id)
        if not workflow:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_WORKFLOW_NOT_FOUND))
        plan = self.repo.get_plan(plan_id)
        if not plan:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_PLAN_NOT_FOUND))
        self.repo.update_version_status(plan.version_id, BudgetVersionStatus.APPROVED)
        self.repo.log_audit("budget_workflow", workflow_id, "finalize_approval", actor)
        return Result.success({"workflow_id": workflow_id, "status": "approved"})

    def get_approval_workflow(self, plan_id: int) -> Optional[BudgetApprovalWorkflow]:
        return self.repo.get_workflow_by_plan(plan_id)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-06: Budget Versioning
    # ═══════════════════════════════════════════════════════════════

    def lock_budget_version(self, version_id: int) -> Optional[BudgetVersion]:
        result = self.repo.lock_version(version_id, True)
        if result:
            self.repo.log_audit("budget_version", version_id, "lock", "system")
        return result

    def unlock_budget_version(self, version_id: int, reason: str) -> Optional[BudgetVersion]:
        result = self.repo.lock_version(version_id, False)
        if result:
            self.repo.log_audit("budget_version", version_id, "unlock", "system",
                                {"reason": reason})
        return result

    def create_revised_version(self, parent_version_id: int, label: str,
                               created_by: Optional[str] = None) -> Result:
        parent = self.repo.get_version(parent_version_id)
        if not parent:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_VERSION_NOT_FOUND))
        parts = parent.version_number.split(".")
        if len(parts) == 2:
            new_vn = f"{parts[0]}.{int(parts[1]) + 1}"
        else:
            new_vn = f"{parent.version_number}.1"
        entity = BudgetVersion(
            fiscal_year=parent.fiscal_year, version_number=new_vn, label=label,
            status=BudgetVersionStatus.REVISED, parent_version_id=parent_version_id,
            created_by=created_by,
        )
        result = self.repo.create_version(entity)
        if result.is_success():
            self.repo.log_audit("budget_version", entity.id, "create_revised", created_by or "system")
        return result

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-07: Budget Adjustment (Virement & Supplementary)
    # ═══════════════════════════════════════════════════════════════

    def request_budget_adjustment(self, version_id: int, adjustment_type: BudgetAdjustmentType,
                                  reference: str, reason: str, lines: List[Dict],
                                  created_by: str) -> Result:
        adj_lines = []
        for l in lines:
            adj_lines.append(BudgetAdjustmentLine(
                adjustment_id=0,
                source_plan_line_id=l.get("source_plan_line_id"),
                target_plan_line_id=l.get("target_plan_line_id"),
                amount=Decimal(str(l.get("amount", "0"))),
                period_key=l.get("period_key"),
            ))
        net = sum(l.amount for l in adj_lines)
        if adjustment_type == BudgetAdjustmentType.VIREMENT and net != Decimal("0"):
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_ADJUST_MATERIALITY_EXCEEDED))
        entity = BudgetAdjustment(
            version_id=version_id, adjustment_type=adjustment_type,
            reference=reference, reason=reason, lines=adj_lines,
            created_by=created_by,
        )
        result = self.repo.create_adjustment(entity)
        if result.is_success():
            self.repo.log_audit("budget_adjustment", entity.id, "create", created_by)
        return result

    def approve_adjustment(self, adjustment_id: int, approved_by: str) -> Result:
        adj = self.repo.get_adjustment(adjustment_id)
        if not adj:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_ADJUSTMENT_NOT_FOUND))
        adj.status = ApprovalStatus.APPROVED
        for line in adj.lines:
            pk = line.period_key or "annual"
            amt = abs(line.amount)
            if line.source_plan_line_id and line.target_plan_line_id:
                # virement: source decreases, target increases
                src = self.repo.get_plan_line_amounts(line.source_plan_line_id)
                if src is not None:
                    new_amts = dict(src)
                    new_amts[pk] = max(new_amts.get(pk, sum(src.values())) - amt, Decimal("0"))
                    self.repo.update_plan_line_amounts(line.source_plan_line_id, new_amts)
                tgt = self.repo.get_plan_line_amounts(line.target_plan_line_id)
                if tgt is not None:
                    new_amts = dict(tgt)
                    new_amts[pk] = new_amts.get(pk, sum(tgt.values())) + amt
                    self.repo.update_plan_line_amounts(line.target_plan_line_id, new_amts)
            elif line.source_plan_line_id:
                # supplementary/increase: add amount to source line
                src = self.repo.get_plan_line_amounts(line.source_plan_line_id)
                if src is not None:
                    new_amts = dict(src)
                    new_amts[pk] = new_amts.get(pk, sum(src.values())) + amt
                    self.repo.update_plan_line_amounts(line.source_plan_line_id, new_amts)
            elif line.target_plan_line_id:
                # decrease: remove amount from target line
                tgt = self.repo.get_plan_line_amounts(line.target_plan_line_id)
                if tgt is not None:
                    new_amts = dict(tgt)
                    new_amts[pk] = max(new_amts.get(pk, sum(tgt.values())) - amt, Decimal("0"))
                    self.repo.update_plan_line_amounts(line.target_plan_line_id, new_amts)
        self.repo.log_audit("budget_adjustment", adjustment_id, "approve", approved_by)
        return Result.success(adj)

    @staticmethod
    def _adjust_amounts(amounts: Dict[str, Decimal], delta: Decimal, add: bool, period_key: str) -> Dict[str, Decimal]:
        result = dict(amounts)
        if period_key in result:
            result[period_key] = result[period_key] + delta if add else max(result[period_key] - delta, Decimal("0"))
        elif period_key and result:
            if add:
                result[period_key] = delta
        return result

    def list_adjustments(self, version_id: int) -> List[BudgetAdjustment]:
        return self.repo.list_adjustments(version_id)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-08: Budget Execution Monitoring
    # ═══════════════════════════════════════════════════════════════

    def _get_gl_actual(self, gl_account_code: str, period_key: Optional[str] = None) -> Decimal:
        from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel
        stmt = select(
            sqlfunc.coalesce(sqlfunc.sum(JournalLineModel.debit), 0),
            sqlfunc.coalesce(sqlfunc.sum(JournalLineModel.credit), 0),
        ).where(
            JournalLineModel.account_id == gl_account_code,
            JournalLineModel.journal_entry_id.in_(
                select(JournalEntryModel.id).where(JournalEntryModel.is_posted == True)
            )
        )
        if period_key:
            stmt = stmt.where(JournalLineModel.period == period_key)
        result = self.session.execute(stmt).one()
        return Decimal(str(result[1])) - Decimal(str(result[0]))

    def get_budget_execution(self, version_id: int,
                             dim_type: Optional[BudgetDimensionType] = None,
                             dim_code: Optional[str] = None) -> List[BudgetExecutionItem]:
        plans = self.repo.list_plans(version_id)
        results = []
        for plan in plans:
            if dim_type and dim_code:
                if plan.dimension_type != dim_type or plan.dimension_code != dim_code:
                    continue
            for line in plan.lines:
                commitments = self.repo.get_total_commitment(line.id)
                actual = self._get_gl_actual(line.gl_account_code)
                item = BudgetExecutionItem(
                    plan_line_id=line.id,
                    budget_amount=sum(Decimal(str(v)) for v in line.amounts.values()),
                    actual_amount=actual,
                    commitment_amount=commitments,
                )
                item.calculate()
                results.append(item)
        return results

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-09: Budget Control
    # ═══════════════════════════════════════════════════════════════

    def configure_budget_control(self, structure_id: int, gl_account_code: str,
                                 control_level: BudgetControlLevel,
                                 dimension_type: Optional[BudgetDimensionType] = None,
                                 dimension_code: Optional[str] = None,
                                 warning_pct: Decimal = Decimal("80"),
                                 soft_block_pct: Decimal = Decimal("90"),
                                 hard_block_pct: Decimal = Decimal("100")) -> Result:
        entity = BudgetControlRule(
            structure_id=structure_id, gl_account_code=gl_account_code,
            dimension_type=dimension_type, dimension_code=dimension_code,
            control_level=control_level,
            warning_threshold_pct=warning_pct,
            soft_block_threshold_pct=soft_block_pct,
            hard_block_threshold_pct=hard_block_pct,
        )
        return self.repo.create_control_rule(entity)

    def check_budget_available(self, structure_id: int, gl_account_code: str,
                               amount: Decimal, dimension_type: Optional[str] = None,
                               dimension_code: Optional[str] = None,
                               period_key: Optional[str] = None) -> Dict:
        rule = self.repo.find_control_rule(structure_id, gl_account_code,
                                           dimension_type, dimension_code)
        if not rule or rule.control_level == BudgetControlLevel.NONE:
            return {"status": "allow", "message": "No control rule"}
        structure = self.repo.get_structure(structure_id)
        if not structure:
            return {"status": "allow", "message": "Structure not found"}
        version = self.repo.get_active_version(structure.fiscal_year)
        if not version:
            return {"status": "allow", "message": "No approved budget version"}
        dim_type = BudgetDimensionType(dimension_type) if dimension_type else None
        plan = self.repo.get_plan_by_dimension(version.id, dim_type, dimension_code) if dim_type and dimension_code else None
        if not plan:
            return {"status": "allow", "message": "No plan for this dimension"}
        budget_amount = Decimal("0")
        for line in plan.lines:
            if line.gl_account_code == gl_account_code:
                budget_amount = sum(Decimal(str(v)) for v in line.amounts.values())
                break
        if budget_amount == Decimal("0"):
            return {"status": "allow", "message": "No budget for this account"}
        actual = self._get_gl_actual(gl_account_code, period_key)
        commitments = Decimal("0")
        for line in plan.lines:
            if line.gl_account_code == gl_account_code:
                commitments = self.repo.get_total_commitment(line.id)
                break
        consumed = actual + commitments + amount
        utilization = consumed / budget_amount * Decimal("100")
        if rule.control_level == BudgetControlLevel.HARD_BLOCK and utilization >= rule.hard_block_threshold_pct:
            return {"status": "block", "utilization_pct": float(utilization), "message": "Hard block exceeded"}
        if rule.control_level in (BudgetControlLevel.SOFT_BLOCK, BudgetControlLevel.HARD_BLOCK) and utilization >= rule.soft_block_threshold_pct:
            return {"status": "soft_block", "utilization_pct": float(utilization), "message": "Soft block exceeded"}
        if utilization >= rule.warning_threshold_pct:
            return {"status": "warning", "utilization_pct": float(utilization), "message": "Warning threshold exceeded"}
        return {"status": "allow", "utilization_pct": float(utilization), "message": "Budget available"}

    def generate_override_code(self, control_rule_id: int, requested_by: str,
                               reason: str, expires_in_hours: int = 24) -> Result:
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        entity = BudgetOverride(
            control_rule_id=control_rule_id, override_code=code,
            requested_by=requested_by, reason=reason,
            expires_at=expires_at,
        )
        return self.repo.create_override(entity)

    def list_control_rules(self, structure_id: int) -> List[BudgetControlRule]:
        return self.repo.list_control_rules(structure_id)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-10: Budget Consolidation
    # ═══════════════════════════════════════════════════════════════

    def consolidate_budget(self, fiscal_year: int, parent_entity_code: str,
                           entities: List[Dict]) -> Result:
        ent_list = []
        for e in entities:
            ent_list.append(BudgetConsolidationEntity(
                consolidation_id=0, entity_code=e["code"],
                entity_name=e["name"], version_id=e["version_id"],
                fx_rate=Decimal(str(e.get("fx_rate", "1"))),
            ))
        entity = BudgetConsolidation(
            fiscal_year=fiscal_year, parent_entity_code=parent_entity_code,
            entities=ent_list,
        )
        result = self.repo.create_consolidation(entity)
        if result.is_success():
            self.repo.log_audit("budget_consolidation", entity.id, "create", "system")
        return result

    def get_consolidation(self, consolidation_id: int) -> Optional[BudgetConsolidation]:
        return self.repo.get_consolidation(consolidation_id)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-11: Budget vs Actual Analysis
    # ═══════════════════════════════════════════════════════════════

    def run_variance_analysis(self, version_id: int, period_key: str) -> Optional[BudgetVarianceReport]:
        plans = self.repo.list_plans(version_id)
        lines = []
        for plan in plans:
            for pl in plan.lines:
                bgt = sum(Decimal(str(v)) for v in pl.amounts.values())
                actual = self._get_gl_actual(pl.gl_account_code, period_key)
                var_amt = actual - bgt
                var_pct = (var_amt / bgt * Decimal("100")) if bgt > Decimal("0") else Decimal("0")
                flag = VarianceFlag.NEUTRAL
                if var_amt > Decimal("0"):
                    flag = VarianceFlag.FAVORABLE
                elif var_amt < Decimal("0"):
                    flag = VarianceFlag.UNFAVORABLE
                lines.append(BudgetVarianceLine(
                    report_id=0, gl_account_code=pl.gl_account_code, name=pl.name,
                    budget_amount=bgt, actual_amount=actual,
                    variance_amount=var_amt, variance_pct=var_pct, flag=flag,
                ))
        return BudgetVarianceReport(
            fiscal_year=0, version_id=version_id, period_key=period_key,
            lines=lines,
        )

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-12: Budget Dashboard & KPI
    # ═══════════════════════════════════════════════════════════════

    def get_budget_dashboard(self, fiscal_year: int) -> Optional[BudgetDashboard]:
        structure = self.repo.get_structure_by_fiscal_year(fiscal_year)
        if not structure:
            return None
        version = self.repo.get_active_version(fiscal_year)
        if not version:
            return BudgetDashboard(fiscal_year=fiscal_year)
        plans = self.repo.list_plans(version.id)
        total_budget = Decimal("0")
        total_actual = Decimal("0")
        revenue_actual = Decimal("0")
        opex_actual = Decimal("0")
        capex_actual = Decimal("0")
        for plan in plans:
            for line in plan.lines:
                total_budget += sum(Decimal(str(v)) for v in line.amounts.values())
                actual = self._get_gl_actual(line.gl_account_code)
                total_actual += actual
                if plan.dimension_type == BudgetDimensionType.COST_CENTER:
                    opex_actual += actual
        rev_plans = [p for p in plans if p.dimension_type == BudgetDimensionType.PRODUCT_LINE]
        for p in rev_plans:
            for line in p.lines:
                revenue_actual += self._get_gl_actual(line.gl_account_code)
        total_rev_bgt = sum(
            sum(Decimal(str(v)) for v in line.amounts.values())
            for p in rev_plans for line in p.lines
        ) or Decimal("1")
        total_opex_bgt = total_budget or Decimal("1")
        return BudgetDashboard(
            fiscal_year=fiscal_year,
            revenue_achievement=revenue_actual / total_rev_bgt * Decimal("100"),
            opex_utilization=opex_actual / total_opex_bgt * Decimal("100"),
            capex_utilization=Decimal("0"),
            ytd_variance=total_actual - total_budget,
        )

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-13: Revenue Budget
    # ═══════════════════════════════════════════════════════════════

    def create_revenue_budget_line(self, plan_line_id: int, product_code: Optional[str] = None,
                                   region_code: Optional[str] = None,
                                   channel_code: Optional[str] = None,
                                   sales_volume: Optional[Decimal] = None,
                                   unit_price: Optional[Decimal] = None,
                                   growth_rate: Optional[Decimal] = None) -> Result:
        driver = None
        if sales_volume is not None:
            driver = RevenueBudgetDriver(
                revenue_line_id=0, sales_volume=sales_volume or Decimal("0"),
                unit_price=unit_price or Decimal("0"),
                growth_rate_pct=growth_rate or Decimal("0"),
            )
        entity = RevenueBudgetLine(
            plan_line_id=plan_line_id, product_code=product_code,
            region_code=region_code, channel_code=channel_code,
            driver=driver,
        )
        return Result.success(entity)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-14: Expense Budget
    # ═══════════════════════════════════════════════════════════════

    def create_headcount_budget(self, expense_line_id: int, fte_count: Decimal,
                                avg_cost_per_fte: Decimal) -> Result:
        entity = HeadcountBudget(
            expense_line_id=expense_line_id, fte_count=fte_count,
            avg_cost_per_fte=avg_cost_per_fte,
        )
        return Result.success(entity)

    # ═══════════════════════════════════════════════════════════════
    # UC-BUDGET-15: CAPEX & Cash Flow Budget
    # ═══════════════════════════════════════════════════════════════

    def create_capex_request(self, plan_line_id: int, asset_type: str, description: str,
                             estimated_cost: Decimal, useful_life_years: int,
                             expected_roi_pct: Decimal, funding_source: str) -> Result:
        entity = CAPEXRequest(
            plan_line_id=plan_line_id, asset_type=asset_type,
            description=description, estimated_cost=estimated_cost,
            useful_life_years=useful_life_years,
            expected_roi_pct=expected_roi_pct, funding_source=funding_source,
        )
        return Result.success(entity)
