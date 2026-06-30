from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_, desc, delete
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
    BudgetAuditLog,
    Result, VASValidationError,
    BudgetType, BudgetVersionStatus, BudgetPeriodType,
    BudgetControlLevel, BudgetDimensionType, BudgetCategoryType,
    ApprovalStatus, KPIThreshold,
)
from domain.budget import AdjustmentType as BudgetAdjustmentType
from domain.i18n import ErrorCodes
from infrastructure.models.budget_models import (
    BudgetStructureModel, BudgetDimensionModel, BudgetCategoryModel,
    BudgetCalendarModel, BudgetCalendarPhaseModel, BudgetPeriodModel,
    BudgetTemplateModel, BudgetTemplateLineModel,
    BudgetVersionModel, BudgetPlanModel, BudgetPlanLineModel, BudgetPlanDriverModel,
    BudgetApprovalWorkflowModel, BudgetApprovalStepModel, BudgetApprovalLogModel,
    BudgetAdjustmentModel, BudgetAdjustmentLineModel,
    BudgetCommitmentModel, BudgetControlRuleModel,
    BudgetOverrideModel, BudgetBlockLogModel,
    BudgetConsolidationModel, BudgetConsolidationEntityModel, BudgetICTransactionModel,
    BudgetAuditLogModel,
)


class BudgetRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Domain↔DB mapping helpers ─────────────────────────────────────

    @staticmethod
    def _structure_to_domain(m: BudgetStructureModel) -> BudgetStructure:
        return BudgetStructure(
            id=m.id, fiscal_year=m.fiscal_year, name=m.name,
            budget_types=[BudgetType(t) for t in (m.budget_types or [])] if m.budget_types else [BudgetType.REVENUE, BudgetType.EXPENSE],
            dimensions=[BudgetDimensionType(d) for d in (m.dimensions or [])] if m.dimensions else [BudgetDimensionType.COST_CENTER],
            period_type=BudgetPeriodType(m.period_type) if m.period_type else BudgetPeriodType.MONTHLY,
            is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at,
        )

    @staticmethod
    def _dimension_to_domain(m: BudgetDimensionModel) -> BudgetDimension:
        return BudgetDimension(
            id=m.id, structure_id=m.structure_id,
            dimension_type=BudgetDimensionType(m.dimension_type),
            code=m.code, name=m.name, is_active=m.is_active, created_at=m.created_at,
        )

    @staticmethod
    def _category_to_domain(m: BudgetCategoryModel) -> BudgetCategory:
        return BudgetCategory(
            id=m.id, structure_id=m.structure_id,
            budget_type=BudgetType(m.budget_type), name=m.name,
            category_type=BudgetCategoryType(m.category_type) if m.category_type else BudgetCategoryType.VARIABLE,
            gl_account_codes=m.gl_account_codes or [],
            is_active=m.is_active, created_at=m.created_at,
        )

    @staticmethod
    def _calendar_to_domain(m: BudgetCalendarModel) -> BudgetCalendar:
        phases = [BudgetCalendarPhase(
            id=p.id, calendar_id=p.calendar_id, phase_name=p.phase_name,
            start_date=p.start_date, end_date=p.end_date, phase_order=p.phase_order,
        ) for p in (m.phases or [])]
        return BudgetCalendar(id=m.id, fiscal_year=m.fiscal_year, name=m.name,
                              phases=phases, is_active=m.is_active, created_at=m.created_at)

    @staticmethod
    def _period_to_domain(m: BudgetPeriodModel) -> BudgetPeriod:
        return BudgetPeriod(
            id=m.id, calendar_id=m.calendar_id, period_key=m.period_key,
            period_type=BudgetPeriodType(m.period_type) if m.period_type else BudgetPeriodType.MONTHLY,
            start_date=m.start_date, end_date=m.end_date, is_open=m.is_open,
        )

    @staticmethod
    def _version_to_domain(m: BudgetVersionModel) -> BudgetVersion:
        return BudgetVersion(
            id=m.id, fiscal_year=m.fiscal_year, version_number=m.version_number, label=m.label,
            status=BudgetVersionStatus(m.status) if m.status else BudgetVersionStatus.DRAFT,
            parent_version_id=m.parent_version_id, is_locked=m.is_locked,
            notes=m.notes, created_by=m.created_by,
            created_at=m.created_at, updated_at=m.updated_at, approved_at=m.approved_at,
        )

    @staticmethod
    def _plan_to_domain(m: BudgetPlanModel) -> BudgetPlan:
        lines = []
        for lm in (m.lines or []):
            driver = None
            if lm.drivers and len(lm.drivers) > 0:
                d = lm.drivers[0]
                driver = BudgetPlanDriver(id=d.id, plan_line_id=d.plan_line_id,
                                          quantity=d.quantity or Decimal("0"),
                                          unit_rate=d.unit_rate or Decimal("0"),
                                          driver_name=d.driver_name)
            amounts = {}
            if lm.amounts:
                amounts = {k: Decimal(str(v)) for k, v in lm.amounts.items()}
            lines.append(BudgetPlanLine(
                id=lm.id, plan_id=lm.plan_id, gl_account_code=lm.gl_account_code,
                name=lm.name,
                category_type=BudgetCategoryType(lm.category_type) if lm.category_type else BudgetCategoryType.VARIABLE,
                amounts=amounts, driver=driver, notes=lm.notes,
            ))
        return BudgetPlan(
            id=m.id, version_id=m.version_id, structure_id=m.structure_id,
            dimension_type=BudgetDimensionType(m.dimension_type), dimension_code=m.dimension_code,
            lines=lines, notes=m.notes, created_by=m.created_by,
            created_at=m.created_at, updated_at=m.updated_at,
        )

    @staticmethod
    def _workflow_to_domain(m: BudgetApprovalWorkflowModel) -> BudgetApprovalWorkflow:
        steps = [BudgetApprovalStep(
            id=s.id, workflow_id=s.workflow_id, step_order=s.step_order,
            approver_role=s.approver_role, approver_name=s.approver_name,
            min_approvers=s.min_approvers or 1,
            status=ApprovalStatus(s.status) if s.status else ApprovalStatus.PENDING,
            comments=s.comments, acted_at=s.acted_at,
        ) for s in (m.steps or [])]
        return BudgetApprovalWorkflow(
            id=m.id, plan_id=m.plan_id, steps=steps,
            status=BudgetVersionStatus(m.status) if m.status else BudgetVersionStatus.DRAFT,
            created_at=m.created_at, completed_at=m.completed_at,
        )

    @staticmethod
    def _adjustment_to_domain(m: BudgetAdjustmentModel) -> BudgetAdjustment:
        lines = [BudgetAdjustmentLine(
            id=l.id, adjustment_id=l.adjustment_id,
            source_plan_line_id=l.source_plan_line_id, target_plan_line_id=l.target_plan_line_id,
            amount=l.amount or Decimal("0"), period_key=l.period_key,
        ) for l in (m.lines or [])]
        return BudgetAdjustment(
            id=m.id, version_id=m.version_id,
            adjustment_type=BudgetAdjustmentType(m.adjustment_type), reference=m.reference,
            reason=m.reason, status=ApprovalStatus(m.status) if m.status else ApprovalStatus.PENDING,
            lines=lines, created_by=m.created_by, created_at=m.created_at,
            approved_at=m.approved_at, approved_by=m.approved_by,
        )

    @staticmethod
    def _control_rule_to_domain(m: BudgetControlRuleModel) -> BudgetControlRule:
        return BudgetControlRule(
            id=m.id, structure_id=m.structure_id, gl_account_code=m.gl_account_code,
            dimension_type=BudgetDimensionType(m.dimension_type) if m.dimension_type else None,
            dimension_code=m.dimension_code,
            control_level=BudgetControlLevel(m.control_level) if m.control_level else BudgetControlLevel.HARD_BLOCK,
            warning_threshold_pct=m.warning_threshold_pct or Decimal("80"),
            soft_block_threshold_pct=m.soft_block_threshold_pct or Decimal("90"),
            hard_block_threshold_pct=m.hard_block_threshold_pct or Decimal("100"),
            is_active=m.is_active, created_at=m.created_at,
        )

    @staticmethod
    def _consolidation_to_domain(m: BudgetConsolidationModel) -> BudgetConsolidation:
        entities = [BudgetConsolidationEntity(
            id=e.id, consolidation_id=e.consolidation_id, entity_code=e.entity_code,
            entity_name=e.entity_name, version_id=e.version_id, fx_rate=e.fx_rate or Decimal("1"),
        ) for e in (m.entities or [])]
        return BudgetConsolidation(
            id=m.id, fiscal_year=m.fiscal_year, parent_entity_code=m.parent_entity_code,
            status=BudgetVersionStatus(m.status) if m.status else BudgetVersionStatus.DRAFT,
            entities=entities, created_at=m.created_at, completed_at=m.completed_at,
        )

    # ── Structures ────────────────────────────────────────────────────

    def create_structure(self, entity: BudgetStructure) -> Result:
        existing = self.session.execute(
            select(BudgetStructureModel).where(
                BudgetStructureModel.fiscal_year == entity.fiscal_year,
                BudgetStructureModel.is_active == True,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_STRUCTURE_EXISTS))
        m = BudgetStructureModel(
            fiscal_year=entity.fiscal_year, name=entity.name,
            budget_types=[t.value for t in entity.budget_types],
            dimensions=[d.value for d in entity.dimensions],
            period_type=entity.period_type.value, is_active=entity.is_active,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def get_structure(self, structure_id: int) -> Optional[BudgetStructure]:
        m = self.session.get(BudgetStructureModel, structure_id)
        return self._structure_to_domain(m) if m else None

    def get_structure_by_fiscal_year(self, fiscal_year: int) -> Optional[BudgetStructure]:
        m = self.session.execute(
            select(BudgetStructureModel).where(
                BudgetStructureModel.fiscal_year == fiscal_year,
                BudgetStructureModel.is_active == True,
            )
        ).scalar_one_or_none()
        return self._structure_to_domain(m) if m else None

    def list_structures(self) -> List[BudgetStructure]:
        rows = self.session.execute(select(BudgetStructureModel).order_by(desc(BudgetStructureModel.fiscal_year))).scalars().all()
        return [self._structure_to_domain(r) for r in rows]

    def update_structure(self, structure_id: int, **updates) -> Optional[BudgetStructure]:
        m = self.session.get(BudgetStructureModel, structure_id)
        if not m:
            return None
        for k, v in updates.items():
            if k == "budget_types" and v:
                v = [t.value if hasattr(t, "value") else t for t in v]
            elif k == "dimensions" and v:
                v = [d.value if hasattr(d, "value") else d for d in v]
            elif k == "period_type" and v:
                v = v.value if hasattr(v, "value") else v
            setattr(m, k, v)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return self._structure_to_domain(m)

    # ── Dimensions ────────────────────────────────────────────────────

    def create_dimension(self, entity: BudgetDimension) -> Result:
        existing = self.session.execute(
            select(BudgetDimensionModel).where(
                BudgetDimensionModel.structure_id == entity.structure_id,
                BudgetDimensionModel.dimension_type == entity.dimension_type.value,
                BudgetDimensionModel.code == entity.code,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_DIMENSION_DUPLICATE))
        m = BudgetDimensionModel(
            structure_id=entity.structure_id, dimension_type=entity.dimension_type.value,
            code=entity.code, name=entity.name, is_active=entity.is_active,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def list_dimensions(self, structure_id: int, dim_type: Optional[BudgetDimensionType] = None) -> List[BudgetDimension]:
        q = select(BudgetDimensionModel).where(BudgetDimensionModel.structure_id == structure_id)
        if dim_type:
            q = q.where(BudgetDimensionModel.dimension_type == dim_type.value)
        rows = self.session.execute(q.order_by(BudgetDimensionModel.dimension_type, BudgetDimensionModel.code)).scalars().all()
        return [self._dimension_to_domain(r) for r in rows]

    # ── Calendar & Periods ────────────────────────────────────────────

    def create_calendar(self, entity: BudgetCalendar) -> Result:
        existing = self.session.execute(
            select(BudgetCalendarModel).where(BudgetCalendarModel.fiscal_year == entity.fiscal_year)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_PERIOD_EXISTS))
        m = BudgetCalendarModel(fiscal_year=entity.fiscal_year, name=entity.name)
        self.session.add(m)
        self.session.flush()
        for ph in entity.phases:
            pm = BudgetCalendarPhaseModel(
                calendar_id=m.id, phase_name=ph.phase_name,
                start_date=ph.start_date, end_date=ph.end_date, phase_order=ph.phase_order,
            )
            self.session.add(pm)
        entity.id = m.id
        return Result.success(entity)

    def get_calendar(self, calendar_id: int) -> Optional[BudgetCalendar]:
        m = self.session.get(BudgetCalendarModel, calendar_id)
        return self._calendar_to_domain(m) if m else None

    def get_calendar_by_year(self, fiscal_year: int) -> Optional[BudgetCalendar]:
        m = self.session.execute(
            select(BudgetCalendarModel).where(BudgetCalendarModel.fiscal_year == fiscal_year)
        ).scalar_one_or_none()
        return self._calendar_to_domain(m) if m else None

    def create_period(self, entity: BudgetPeriod) -> Result:
        existing = self.session.execute(
            select(BudgetPeriodModel).where(
                BudgetPeriodModel.calendar_id == entity.calendar_id,
                BudgetPeriodModel.period_key == entity.period_key,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.BUDGET_PERIOD_EXISTS))
        m = BudgetPeriodModel(
            calendar_id=entity.calendar_id, period_key=entity.period_key,
            period_type=entity.period_type.value,
            start_date=entity.start_date, end_date=entity.end_date,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def list_periods(self, calendar_id: int) -> List[BudgetPeriod]:
        rows = self.session.execute(
            select(BudgetPeriodModel).where(BudgetPeriodModel.calendar_id == calendar_id)
            .order_by(BudgetPeriodModel.period_key)
        ).scalars().all()
        return [self._period_to_domain(r) for r in rows]

    def close_period(self, period_id: int) -> Optional[BudgetPeriod]:
        m = self.session.get(BudgetPeriodModel, period_id)
        if not m:
            return None
        m.is_open = False
        self.session.flush()
        return self._period_to_domain(m)

    # ── Templates ─────────────────────────────────────────────────────

    def create_template(self, entity: BudgetTemplate) -> Result:
        m = BudgetTemplateModel(
            name=entity.name, description=entity.description,
            budget_type=entity.budget_type.value, is_active=entity.is_active,
        )
        self.session.add(m)
        self.session.flush()
        for line in entity.lines:
            lm = BudgetTemplateLineModel(
                template_id=m.id, line_order=line.line_order,
                gl_account_code=line.gl_account_code, name=line.name,
                category_type=line.category_type.value,
                formula=line.formula, is_required=line.is_required,
                default_amount=line.default_amount, notes=line.notes,
            )
            self.session.add(lm)
        entity.id = m.id
        return Result.success(entity)

    def get_template(self, template_id: int) -> Optional[BudgetTemplate]:
        m = self.session.get(BudgetTemplateModel, template_id)
        if not m:
            return None
        lines = [BudgetTemplateLine(
            id=l.id, template_id=l.template_id, line_order=l.line_order,
            gl_account_code=l.gl_account_code, name=l.name,
            category_type=BudgetCategoryType(l.category_type) if l.category_type else BudgetCategoryType.VARIABLE,
            formula=l.formula, is_required=l.is_required,
            default_amount=l.default_amount or Decimal("0"), notes=l.notes,
        ) for l in (m.lines or [])]
        return BudgetTemplate(
            id=m.id, name=m.name, description=m.description,
            budget_type=BudgetType(m.budget_type), lines=lines,
            is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at,
        )

    def list_templates(self, budget_type: Optional[BudgetType] = None) -> List[BudgetTemplate]:
        q = select(BudgetTemplateModel).where(BudgetTemplateModel.is_active == True)
        if budget_type:
            q = q.where(BudgetTemplateModel.budget_type == budget_type.value)
        rows = self.session.execute(q.order_by(BudgetTemplateModel.name)).scalars().all()
        result = []
        for m in rows:
            lines = [BudgetTemplateLine(
                id=l.id, template_id=l.template_id, line_order=l.line_order,
                gl_account_code=l.gl_account_code, name=l.name,
                category_type=BudgetCategoryType(l.category_type) if l.category_type else BudgetCategoryType.VARIABLE,
                formula=l.formula, is_required=l.is_required,
                default_amount=l.default_amount or Decimal("0"), notes=l.notes,
            ) for l in (m.lines or [])]
            result.append(BudgetTemplate(
                id=m.id, name=m.name, description=m.description,
                budget_type=BudgetType(m.budget_type), lines=lines,
                is_active=m.is_active, created_at=m.created_at,
            ))
        return result

    # ── Versions ──────────────────────────────────────────────────────

    def create_version(self, entity: BudgetVersion) -> Result:
        m = BudgetVersionModel(
            fiscal_year=entity.fiscal_year, version_number=entity.version_number,
            label=entity.label, status=entity.status.value,
            parent_version_id=entity.parent_version_id, is_locked=entity.is_locked,
            notes=entity.notes, created_by=entity.created_by,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def get_version(self, version_id: int) -> Optional[BudgetVersion]:
        m = self.session.get(BudgetVersionModel, version_id)
        return self._version_to_domain(m) if m else None

    def get_active_version(self, fiscal_year: int) -> Optional[BudgetVersion]:
        m = self.session.execute(
            select(BudgetVersionModel).where(
                BudgetVersionModel.fiscal_year == fiscal_year,
                BudgetVersionModel.status.in_(["approved", "revised"]),
                BudgetVersionModel.is_locked == True,
            ).order_by(desc(BudgetVersionModel.created_at))
        ).scalars().first()
        return self._version_to_domain(m) if m else None

    def list_versions(self, fiscal_year: int) -> List[BudgetVersion]:
        rows = self.session.execute(
            select(BudgetVersionModel).where(BudgetVersionModel.fiscal_year == fiscal_year)
            .order_by(desc(BudgetVersionModel.created_at))
        ).scalars().all()
        return [self._version_to_domain(r) for r in rows]

    def update_version_status(self, version_id: int, status: BudgetVersionStatus) -> Optional[BudgetVersion]:
        m = self.session.get(BudgetVersionModel, version_id)
        if not m:
            return None
        m.status = status.value
        if status == BudgetVersionStatus.APPROVED:
            m.approved_at = datetime.now(timezone.utc)
            m.is_locked = True
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return self._version_to_domain(m)

    def lock_version(self, version_id: int, lock: bool = True) -> Optional[BudgetVersion]:
        m = self.session.get(BudgetVersionModel, version_id)
        if not m:
            return None
        m.is_locked = lock
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return self._version_to_domain(m)

    # ── Plans ─────────────────────────────────────────────────────────

    def create_plan(self, entity: BudgetPlan) -> Result:
        m = BudgetPlanModel(
            version_id=entity.version_id, structure_id=entity.structure_id,
            dimension_type=entity.dimension_type.value, dimension_code=entity.dimension_code,
            notes=entity.notes, created_by=entity.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in entity.lines:
            amounts_str = {k: str(v) for k, v in line.amounts.items()} if line.amounts else {}
            lm = BudgetPlanLineModel(
                plan_id=m.id, gl_account_code=line.gl_account_code, name=line.name,
                category_type=line.category_type.value, amounts=amounts_str, notes=line.notes,
            )
            self.session.add(lm)
            self.session.flush()
            line.id = lm.id
            if line.driver:
                dm = BudgetPlanDriverModel(
                    plan_line_id=lm.id, quantity=line.driver.quantity,
                    unit_rate=line.driver.unit_rate, driver_name=line.driver.driver_name,
                )
                self.session.add(dm)
        entity.id = m.id
        return Result.success(entity)

    def get_plan(self, plan_id: int) -> Optional[BudgetPlan]:
        m = self.session.get(BudgetPlanModel, plan_id)
        return self._plan_to_domain(m) if m else None

    def get_plan_by_dimension(self, version_id: int, dim_type: BudgetDimensionType, dim_code: str) -> Optional[BudgetPlan]:
        m = self.session.execute(
            select(BudgetPlanModel).where(
                BudgetPlanModel.version_id == version_id,
                BudgetPlanModel.dimension_type == dim_type.value,
                BudgetPlanModel.dimension_code == dim_code,
            )
        ).scalar_one_or_none()
        return self._plan_to_domain(m) if m else None

    def list_plans(self, version_id: int) -> List[BudgetPlan]:
        rows = self.session.execute(
            select(BudgetPlanModel).where(BudgetPlanModel.version_id == version_id)
            .order_by(BudgetPlanModel.dimension_type, BudgetPlanModel.dimension_code)
        ).scalars().all()
        return [self._plan_to_domain(r) for r in rows]

    def update_plan_lines(self, plan_id: int, lines: List[BudgetPlanLine]) -> Optional[BudgetPlan]:
        m = self.session.get(BudgetPlanModel, plan_id)
        if not m:
            return None
        self.session.execute(delete(BudgetPlanDriverModel).where(
            BudgetPlanDriverModel.plan_line_id.in_(
                select(BudgetPlanLineModel.id).where(BudgetPlanLineModel.plan_id == plan_id)
            )
        ))
        self.session.execute(delete(BudgetPlanLineModel).where(BudgetPlanLineModel.plan_id == plan_id))
        for line in lines:
            amounts_str = {k: str(v) for k, v in line.amounts.items()} if line.amounts else {}
            lm = BudgetPlanLineModel(
                plan_id=plan_id, gl_account_code=line.gl_account_code, name=line.name,
                category_type=line.category_type.value, amounts=amounts_str, notes=line.notes,
            )
            self.session.add(lm)
            self.session.flush()
            if line.driver:
                dm = BudgetPlanDriverModel(
                    plan_line_id=lm.id, quantity=line.driver.quantity,
                    unit_rate=line.driver.unit_rate, driver_name=line.driver.driver_name,
                )
                self.session.add(dm)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.expire(m, attribute_names=["lines"])
        return self._plan_to_domain(m)

    # ── Approval Workflow ─────────────────────────────────────────────

    def create_workflow(self, entity: BudgetApprovalWorkflow) -> Result:
        wm = BudgetApprovalWorkflowModel(plan_id=entity.plan_id, status=entity.status.value)
        self.session.add(wm)
        self.session.flush()
        for step in entity.steps:
            sm = BudgetApprovalStepModel(
                workflow_id=wm.id, step_order=step.step_order, approver_role=step.approver_role,
                approver_name=step.approver_name, min_approvers=step.min_approvers,
                status=step.status.value, comments=step.comments,
            )
            self.session.add(sm)
            self.session.flush()
            step.id = sm.id
        entity.id = wm.id
        return Result.success(entity)

    def get_workflow(self, workflow_id: int) -> Optional[BudgetApprovalWorkflow]:
        m = self.session.get(BudgetApprovalWorkflowModel, workflow_id)
        return self._workflow_to_domain(m) if m else None

    def get_workflow_by_plan(self, plan_id: int) -> Optional[BudgetApprovalWorkflow]:
        m = self.session.execute(
            select(BudgetApprovalWorkflowModel).where(BudgetApprovalWorkflowModel.plan_id == plan_id)
        ).scalar_one_or_none()
        return self._workflow_to_domain(m) if m else None

    def approve_step(self, step_id: int, actor: str, comments: Optional[str] = None) -> Optional[BudgetApprovalStep]:
        sm = self.session.get(BudgetApprovalStepModel, step_id)
        if not sm:
            return None
        sm.status = ApprovalStatus.APPROVED.value
        sm.acted_at = datetime.now(timezone.utc)
        log = BudgetApprovalLogModel(
            workflow_id=sm.workflow_id, step_id=step_id,
            action="approve", actor=actor, comments=comments,
        )
        self.session.add(log)
        self.session.flush()
        return BudgetApprovalStep(
            id=sm.id, workflow_id=sm.workflow_id, step_order=sm.step_order,
            approver_role=sm.approver_role, approver_name=sm.approver_name,
            min_approvers=sm.min_approvers or 1,
            status=ApprovalStatus.APPROVED, comments=sm.comments, acted_at=sm.acted_at,
        )

    def reject_step(self, step_id: int, actor: str, comments: str) -> Optional[BudgetApprovalStep]:
        sm = self.session.get(BudgetApprovalStepModel, step_id)
        if not sm:
            return None
        sm.status = ApprovalStatus.REJECTED.value
        sm.comments = comments
        sm.acted_at = datetime.now(timezone.utc)
        log = BudgetApprovalLogModel(
            workflow_id=sm.workflow_id, step_id=step_id,
            action="reject", actor=actor, comments=comments,
        )
        self.session.add(log)
        self.session.flush()
        return BudgetApprovalStep(
            id=sm.id, workflow_id=sm.workflow_id, step_order=sm.step_order,
            approver_role=sm.approver_role, approver_name=sm.approver_name,
            min_approvers=sm.min_approvers or 1,
            status=ApprovalStatus.REJECTED, comments=sm.comments, acted_at=sm.acted_at,
        )

    def log_approval_action(self, workflow_id: int, step_id: int, action: str, actor: str, comments: Optional[str] = None):
        log = BudgetApprovalLogModel(
            workflow_id=workflow_id, step_id=step_id,
            action=action, actor=actor, comments=comments,
        )
        self.session.add(log)
        self.session.flush()

    # ── Adjustments ───────────────────────────────────────────────────

    def create_adjustment(self, entity: BudgetAdjustment) -> Result:
        m = BudgetAdjustmentModel(
            version_id=entity.version_id, adjustment_type=entity.adjustment_type.value,
            reference=entity.reference, reason=entity.reason,
            status=entity.status.value, created_by=entity.created_by,
        )
        self.session.add(m)
        self.session.flush()
        for line in entity.lines:
            lm = BudgetAdjustmentLineModel(
                adjustment_id=m.id, source_plan_line_id=line.source_plan_line_id,
                target_plan_line_id=line.target_plan_line_id,
                amount=line.amount, period_key=line.period_key,
            )
            self.session.add(lm)
        entity.id = m.id
        return Result.success(entity)

    def get_adjustment(self, adjustment_id: int) -> Optional[BudgetAdjustment]:
        m = self.session.get(BudgetAdjustmentModel, adjustment_id)
        return self._adjustment_to_domain(m) if m else None

    def list_adjustments(self, version_id: int) -> List[BudgetAdjustment]:
        rows = self.session.execute(
            select(BudgetAdjustmentModel).where(BudgetAdjustmentModel.version_id == version_id)
            .order_by(desc(BudgetAdjustmentModel.created_at))
        ).scalars().all()
        return [self._adjustment_to_domain(r) for r in rows]

    # ── Commitments ───────────────────────────────────────────────────

    def create_commitment(self, entity: BudgetCommitment) -> Result:
        m = BudgetCommitmentModel(
            plan_line_id=entity.plan_line_id, source_type=entity.source_type,
            source_id=entity.source_id, amount=entity.amount, period_key=entity.period_key,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def get_commitments(self, plan_line_id: int, period_key: Optional[str] = None) -> List[BudgetCommitment]:
        q = select(BudgetCommitmentModel).where(BudgetCommitmentModel.plan_line_id == plan_line_id)
        if period_key:
            q = q.where(BudgetCommitmentModel.period_key == period_key)
        rows = self.session.execute(q).scalars().all()
        return [BudgetCommitment(
            id=r.id, plan_line_id=r.plan_line_id, source_type=r.source_type,
            source_id=r.source_id, amount=r.amount or Decimal("0"), period_key=r.period_key,
        ) for r in rows]

    def get_total_commitment(self, plan_line_id: int) -> Decimal:
        r = self.session.execute(
            select(func.coalesce(func.sum(BudgetCommitmentModel.amount), 0))
            .where(BudgetCommitmentModel.plan_line_id == plan_line_id)
        ).scalar()
        return Decimal(str(r)) if r else Decimal("0")

    # ── Control Rules ─────────────────────────────────────────────────

    def create_control_rule(self, entity: BudgetControlRule) -> Result:
        m = BudgetControlRuleModel(
            structure_id=entity.structure_id, gl_account_code=entity.gl_account_code,
            dimension_type=entity.dimension_type.value if entity.dimension_type else None,
            dimension_code=entity.dimension_code,
            control_level=entity.control_level.value,
            warning_threshold_pct=entity.warning_threshold_pct,
            soft_block_threshold_pct=entity.soft_block_threshold_pct,
            hard_block_threshold_pct=entity.hard_block_threshold_pct,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def get_control_rule(self, rule_id: int) -> Optional[BudgetControlRule]:
        m = self.session.get(BudgetControlRuleModel, rule_id)
        return self._control_rule_to_domain(m) if m else None

    def find_control_rule(self, structure_id: int, gl_account_code: str,
                          dimension_type: Optional[str] = None,
                          dimension_code: Optional[str] = None) -> Optional[BudgetControlRule]:
        q = select(BudgetControlRuleModel).where(
            BudgetControlRuleModel.structure_id == structure_id,
            BudgetControlRuleModel.gl_account_code == gl_account_code,
            BudgetControlRuleModel.is_active == True,
        )
        if dimension_type:
            q = q.where(BudgetControlRuleModel.dimension_type == dimension_type)
            if dimension_code:
                q = q.where(BudgetControlRuleModel.dimension_code == dimension_code)
        m = self.session.execute(q).scalar_one_or_none()
        return self._control_rule_to_domain(m) if m else None

    def list_control_rules(self, structure_id: int) -> List[BudgetControlRule]:
        rows = self.session.execute(
            select(BudgetControlRuleModel).where(BudgetControlRuleModel.structure_id == structure_id)
        ).scalars().all()
        return [self._control_rule_to_domain(r) for r in rows]

    def create_override(self, entity: BudgetOverride) -> Result:
        m = BudgetOverrideModel(
            control_rule_id=entity.control_rule_id, override_code=entity.override_code,
            requested_by=entity.requested_by, approved_by=entity.approved_by,
            reason=entity.reason, status=entity.status.value,
            expires_at=entity.expires_at,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    def log_block(self, entity: BudgetBlockLog) -> Result:
        m = BudgetBlockLogModel(
            control_rule_id=entity.control_rule_id, source_type=entity.source_type,
            source_id=entity.source_id, gl_account_code=entity.gl_account_code,
            dimension_code=entity.dimension_code,
            attempted_amount=entity.attempted_amount, utilization_pct=entity.utilization_pct,
            control_level=entity.control_level.value if hasattr(entity.control_level, "value") else entity.control_level,
            was_blocked=entity.was_blocked, override_id=entity.override_id,
        )
        self.session.add(m)
        self.session.flush()
        entity.id = m.id
        return Result.success(entity)

    # ── Consolidation ─────────────────────────────────────────────────

    def create_consolidation(self, entity: BudgetConsolidation) -> Result:
        m = BudgetConsolidationModel(
            fiscal_year=entity.fiscal_year, parent_entity_code=entity.parent_entity_code,
            status=entity.status.value,
        )
        self.session.add(m)
        self.session.flush()
        for e in entity.entities:
            em = BudgetConsolidationEntityModel(
                consolidation_id=m.id, entity_code=e.entity_code, entity_name=e.entity_name,
                version_id=e.version_id, fx_rate=e.fx_rate,
            )
            self.session.add(em)
        for ic in (entity.ic_transactions or []):
            icm = BudgetICTransactionModel(
                consolidation_id=m.id, from_entity_code=ic.from_entity_code,
                to_entity_code=ic.to_entity_code, gl_account_code=ic.gl_account_code, amount=ic.amount,
            )
            self.session.add(icm)
        entity.id = m.id
        return Result.success(entity)

    def get_consolidation(self, consolidation_id: int) -> Optional[BudgetConsolidation]:
        m = self.session.get(BudgetConsolidationModel, consolidation_id)
        return self._consolidation_to_domain(m) if m else None

    # ── Audit Log ─────────────────────────────────────────────────────

    def log_audit(self, entity_type: str, entity_id: int, action: str, actor: str, changes: Optional[Dict] = None):
        m = BudgetAuditLogModel(
            entity_type=entity_type, entity_id=entity_id, action=action,
            changes=changes, actor=actor,
        )
        self.session.add(m)
        self.session.flush()

    def get_audit_logs(self, entity_type: str, entity_id: int) -> List[BudgetAuditLog]:
        rows = self.session.execute(
            select(BudgetAuditLogModel).where(
                BudgetAuditLogModel.entity_type == entity_type,
                BudgetAuditLogModel.entity_id == entity_id,
            ).order_by(desc(BudgetAuditLogModel.created_at))
        ).scalars().all()
        return [BudgetAuditLog(
            id=r.id, entity_type=r.entity_type, entity_id=r.entity_id,
            action=r.action, changes=r.changes, actor=r.actor, created_at=r.created_at,
        ) for r in rows]
