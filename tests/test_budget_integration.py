from decimal import Decimal
from datetime import date, datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    BudgetType, BudgetVersionStatus, BudgetPeriodType,
    BudgetControlLevel, BudgetDimensionType, BudgetCategoryType,
    ApprovalStatus,
)
from domain.budget import AdjustmentType as BudgetAdjustmentType
from domain import (
    BudgetStructure, BudgetDimension, BudgetCategory,
    BudgetCalendar, BudgetCalendarPhase, BudgetPeriod,
    BudgetTemplate, BudgetTemplateLine,
    BudgetVersion, BudgetPlan, BudgetPlanLine, BudgetPlanDriver,
    BudgetApprovalWorkflow, BudgetApprovalStep,
    BudgetAdjustment, BudgetAdjustmentLine,
    BudgetCommitment, BudgetExecutionItem,
    BudgetControlRule, BudgetOverride, BudgetBlockLog,
    BudgetConsolidation, BudgetConsolidationEntity,
    RevenueBudgetDriver, HeadcountBudget, CAPEXRequest,
    Result,
)
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base
from infrastructure.repositories.budget_repository import BudgetRepository
from use_cases.budget import BudgetUseCases


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn)
    yield session
    session.close()
    trans.rollback()
    conn.close()


@pytest.fixture
def repo(session):
    return BudgetRepository(session)


@pytest.fixture
def uc(session):
    return BudgetUseCases(session)


# ═══════════════════════════════════════════════════════════════════
# Fixture factories
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def structure(repo, session):
    s = BudgetStructure(fiscal_year=2026, name="NS 2026")
    result = repo.create_structure(s)
    session.flush()
    return result.get_data()


@pytest.fixture
def dimension(repo, structure, session):
    d = BudgetDimension(structure_id=structure.id,
                        dimension_type=BudgetDimensionType.DEPARTMENT,
                        code="IT", name="IT Dept")
    result = repo.create_dimension(d)
    session.flush()
    return result.get_data()


@pytest.fixture
def calendar(repo, session):
    phases = [BudgetCalendarPhase(calendar_id=0, phase_name="Plan",
                                  start_date=date(2026, 1, 1),
                                  end_date=date(2026, 3, 31), phase_order=1)]
    c = BudgetCalendar(fiscal_year=2026, name="NS2026", phases=phases)
    result = repo.create_calendar(c)
    session.flush()
    return result.get_data()


@pytest.fixture
def period(repo, calendar, session):
    p = BudgetPeriod(calendar_id=calendar.id, period_key="2026-01",
                     start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
    result = repo.create_period(p)
    session.flush()
    return result.get_data()


@pytest.fixture
def template(repo, session):
    lines = [BudgetTemplateLine(template_id=0, gl_account_code="511",
                                name="Sales", line_order=1)]
    t = BudgetTemplate(name="Revenue Template", budget_type=BudgetType.REVENUE,
                       lines=lines)
    result = repo.create_template(t)
    session.flush()
    return result.get_data()


@pytest.fixture
def version(repo, session):
    v = BudgetVersion(fiscal_year=2026, version_number="v2026.1", label="Initial")
    result = repo.create_version(v)
    session.flush()
    return result.get_data()


@pytest.fixture
def plan_with_line(repo, structure, version, session):
    driver = BudgetPlanDriver(plan_line_id=0, quantity=Decimal("10"),
                              unit_rate=Decimal("50000"))
    lines = [BudgetPlanLine(plan_id=0, gl_account_code="511", name="Sales",
                            amounts={"2026-01": Decimal("500000")}, driver=driver)]
    p = BudgetPlan(version_id=version.id, structure_id=structure.id,
                   dimension_type=BudgetDimensionType.DEPARTMENT,
                   dimension_code="IT", lines=lines)
    result = repo.create_plan(p)
    session.flush()
    return result.get_data()


# ═══════════════════════════════════════════════════════════════════
# Structure CRUD
# ═══════════════════════════════════════════════════════════════════

class TestStructureCRUD:
    def test_create_structure(self, repo, session):
        s = BudgetStructure(fiscal_year=2026, name="NS 2026")
        result = repo.create_structure(s)
        assert result.is_success()
        assert result.get_data().id is not None
        session.flush()

    def test_create_duplicate_fiscal_year(self, repo, structure, session):
        s = BudgetStructure(fiscal_year=structure.fiscal_year, name="Duplicate")
        result = repo.create_structure(s)
        assert result.is_failure()

    def test_get_structure(self, repo, structure):
        s = repo.get_structure(structure.id)
        assert s is not None
        assert s.name == "NS 2026"

    def test_get_structure_by_fiscal_year(self, repo, structure):
        s = repo.get_structure_by_fiscal_year(structure.fiscal_year)
        assert s is not None
        assert s.fiscal_year == structure.fiscal_year

    def test_list_structures(self, repo, structure):
        lst = repo.list_structures()
        assert len(lst) >= 1

    def test_update_structure(self, repo, structure, session):
        s = repo.update_structure(structure.id, name="NS 2026 Updated")
        assert s is not None
        assert s.name == "NS 2026 Updated"
        session.flush()

    def test_get_nonexistent_structure(self, repo):
        assert repo.get_structure(99999) is None


# ═══════════════════════════════════════════════════════════════════
# Dimension CRUD
# ═══════════════════════════════════════════════════════════════════

class TestDimensionCRUD:
    def test_create_dimension(self, repo, structure, session):
        d = BudgetDimension(structure_id=structure.id,
                            dimension_type=BudgetDimensionType.COST_CENTER,
                            code="CC001", name="IT")
        result = repo.create_dimension(d)
        assert result.is_success()
        session.flush()

    def test_create_duplicate_dimension(self, repo, dimension, session):
        d = BudgetDimension(structure_id=dimension.structure_id,
                            dimension_type=dimension.dimension_type,
                            code=dimension.code, name="Duplicate")
        result = repo.create_dimension(d)
        assert result.is_failure()

    def test_list_dimensions(self, repo, structure, dimension):
        lst = repo.list_dimensions(structure.id)
        assert len(lst) >= 1

    def test_list_dimensions_filtered(self, repo, structure, dimension):
        lst = repo.list_dimensions(structure.id, BudgetDimensionType.COST_CENTER)
        for d in lst:
            assert d.dimension_type == BudgetDimensionType.COST_CENTER


# ═══════════════════════════════════════════════════════════════════
# Calendar & Period CRUD
# ═══════════════════════════════════════════════════════════════════

class TestCalendarCRUD:
    def test_create_calendar(self, repo, session):
        c = BudgetCalendar(fiscal_year=2027, name="NS2027")
        result = repo.create_calendar(c)
        assert result.is_success()
        session.flush()

    def test_create_duplicate_calendar_year(self, repo, calendar, session):
        c = BudgetCalendar(fiscal_year=calendar.fiscal_year, name="Dup")
        result = repo.create_calendar(c)
        assert result.is_failure()

    def test_get_calendar(self, repo, calendar):
        c = repo.get_calendar(calendar.id)
        assert c is not None

    def test_get_calendar_by_year(self, repo, calendar):
        c = repo.get_calendar_by_year(calendar.fiscal_year)
        assert c is not None
        assert len(c.phases) == 1

    def test_create_calendar_with_phases(self, repo, session):
        phases = [
            BudgetCalendarPhase(calendar_id=0, phase_name="Plan",
                                start_date=date(2026, 1, 1), end_date=date(2026, 3, 31),
                                phase_order=1),
            BudgetCalendarPhase(calendar_id=0, phase_name="Budget",
                                start_date=date(2026, 4, 1), end_date=date(2026, 6, 30),
                                phase_order=2),
        ]
        c = BudgetCalendar(fiscal_year=2028, name="NS2028", phases=phases)
        result = repo.create_calendar(c)
        assert result.is_success()
        assert len(result.get_data().phases) == 2
        session.flush()

    def test_create_period(self, repo, calendar, session):
        p = BudgetPeriod(calendar_id=calendar.id, period_key="2026-02",
                         start_date=date(2026, 2, 1), end_date=date(2026, 2, 28))
        result = repo.create_period(p)
        assert result.is_success()
        session.flush()

    def test_create_duplicate_period(self, repo, period, session):
        p = BudgetPeriod(calendar_id=period.calendar_id, period_key=period.period_key,
                         start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        result = repo.create_period(p)
        assert result.is_failure()

    def test_list_periods(self, repo, calendar, period):
        lst = repo.list_periods(calendar.id)
        assert len(lst) >= 1

    def test_close_period(self, repo, period, session):
        p = repo.close_period(period.id)
        assert p is not None
        assert p.is_open is False
        session.flush()

    def test_close_nonexistent_period(self, repo):
        assert repo.close_period(99999) is None


# ═══════════════════════════════════════════════════════════════════
# Template CRUD
# ═══════════════════════════════════════════════════════════════════

class TestTemplateCRUD:
    def test_create_template(self, repo, session):
        lines = [BudgetTemplateLine(template_id=0, gl_account_code="511",
                                    name="Sales", line_order=1)]
        t = BudgetTemplate(name="Rev Template", budget_type=BudgetType.REVENUE,
                           lines=lines)
        result = repo.create_template(t)
        assert result.is_success()
        session.flush()

    def test_get_template(self, repo, template):
        t = repo.get_template(template.id)
        assert t is not None
        assert len(t.lines) > 0

    def test_list_templates(self, repo, template):
        lst = repo.list_templates()
        assert len(lst) >= 1

    def test_list_templates_by_type(self, repo, template):
        lst = repo.list_templates(BudgetType.REVENUE)
        assert all(t.budget_type == BudgetType.REVENUE for t in lst)

    def test_get_nonexistent_template(self, repo):
        assert repo.get_template(99999) is None


# ═══════════════════════════════════════════════════════════════════
# Version CRUD
# ═══════════════════════════════════════════════════════════════════

class TestVersionCRUD:
    def test_create_version(self, repo, session):
        v = BudgetVersion(fiscal_year=2026, version_number="v2026.1", label="V1")
        result = repo.create_version(v)
        assert result.is_success()
        session.flush()

    def test_get_version(self, repo, version):
        v = repo.get_version(version.id)
        assert v is not None
        assert v.version_number == "v2026.1"

    def test_list_versions(self, repo, version):
        lst = repo.list_versions(version.fiscal_year)
        assert len(lst) >= 1

    def test_update_version_status_to_approved(self, repo, version, session):
        v = repo.update_version_status(version.id, BudgetVersionStatus.APPROVED)
        assert v is not None
        assert v.status == BudgetVersionStatus.APPROVED
        assert v.is_locked is True
        assert v.approved_at is not None
        session.flush()

    def test_get_active_version(self, repo, version, session):
        repo.update_version_status(version.id, BudgetVersionStatus.APPROVED)
        session.flush()
        v = repo.get_active_version(version.fiscal_year)
        assert v is not None
        assert v.is_locked is True

    def test_lock_version(self, repo, version, session):
        v = repo.lock_version(version.id, True)
        assert v is not None
        assert v.is_locked is True
        session.flush()

    def test_unlock_version(self, repo, version, session):
        repo.lock_version(version.id, True)
        v = repo.lock_version(version.id, False)
        assert v is not None
        assert v.is_locked is False
        session.flush()


# ═══════════════════════════════════════════════════════════════════
# Plan CRUD
# ═══════════════════════════════════════════════════════════════════

class TestPlanCRUD:
    def test_create_plan(self, repo, structure, version, session):
        lines = [BudgetPlanLine(plan_id=0, gl_account_code="511", name="Sales",
                                amounts={"2026-01": Decimal("500000")})]
        p = BudgetPlan(version_id=version.id, structure_id=structure.id,
                       dimension_type=BudgetDimensionType.DEPARTMENT,
                       dimension_code="IT", lines=lines)
        result = repo.create_plan(p)
        assert result.is_success()
        session.flush()

    def test_create_plan_with_driver(self, repo, structure, version, session):
        driver = BudgetPlanDriver(plan_line_id=0, quantity=Decimal("10"),
                                  unit_rate=Decimal("50000"))
        lines = [BudgetPlanLine(plan_id=0, gl_account_code="511", name="Sales",
                                amounts={"2026-01": Decimal("500000")}, driver=driver)]
        p = BudgetPlan(version_id=version.id, structure_id=structure.id,
                       dimension_type=BudgetDimensionType.DEPARTMENT,
                       dimension_code="HR", lines=lines)
        result = repo.create_plan(p)
        assert result.is_success()
        assert result.get_data().lines[0].driver is not None
        session.flush()

    def test_get_plan(self, repo, plan_with_line):
        p = repo.get_plan(plan_with_line.id)
        assert p is not None
        assert len(p.lines) >= 1

    def test_get_plan_by_dimension(self, repo, plan_with_line):
        p = repo.get_plan_by_dimension(plan_with_line.version_id,
                                       plan_with_line.dimension_type,
                                       plan_with_line.dimension_code)
        assert p is not None
        assert p.dimension_code == "IT"

    def test_list_plans(self, repo, version, plan_with_line):
        lst = repo.list_plans(version.id)
        assert len(lst) >= 1

    def test_get_nonexistent_plan(self, repo):
        assert repo.get_plan(99999) is None

    def test_update_plan_lines(self, repo, plan_with_line, session):
        new_lines = [BudgetPlanLine(plan_id=0, gl_account_code="622", name="Salary",
                                    amounts={"2026-01": Decimal("300000")})]
        p = repo.update_plan_lines(plan_with_line.id, new_lines)
        assert p is not None
        assert len(p.lines) == 1
        assert p.lines[0].gl_account_code == "622"
        session.flush()


# ═══════════════════════════════════════════════════════════════════
# Approval Workflow
# ═══════════════════════════════════════════════════════════════════

class TestApprovalWorkflow:
    def test_create_workflow(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1,
                                    approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        result = repo.create_workflow(w)
        assert result.is_success()
        session.flush()

    def test_get_workflow(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        result = repo.create_workflow(w)
        session.flush()
        assert result.is_success()
        wf = repo.get_workflow(result.get_data().id)
        assert wf is not None

    def test_get_workflow_by_plan(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        repo.create_workflow(w)
        session.flush()
        wf = repo.get_workflow_by_plan(plan_with_line.id)
        assert wf is not None

    def test_approve_step(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        result = repo.create_workflow(w)
        session.flush()
        step = repo.approve_step(result.get_data().steps[0].id, "admin", "OK")
        assert step is not None
        assert step.status == ApprovalStatus.APPROVED
        session.flush()

    def test_reject_step(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        result = repo.create_workflow(w)
        session.flush()
        step = repo.reject_step(result.get_data().steps[0].id, "admin", "No")
        assert step is not None
        assert step.status == ApprovalStatus.REJECTED
        session.flush()

    def test_approve_nonexistent_step(self, repo):
        assert repo.approve_step(99999, "admin") is None

    def test_log_approval_action(self, repo, plan_with_line, session):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=plan_with_line.id, steps=steps)
        result = repo.create_workflow(w)
        session.flush()
        wf = result.get_data()
        repo.log_approval_action(wf.id, wf.steps[0].id, "notify", "admin")
        session.flush()


# ═══════════════════════════════════════════════════════════════════
# Adjustments
# ═══════════════════════════════════════════════════════════════════

class TestAdjustments:
    def test_create_adjustment(self, repo, version, plan_with_line, session):
        lines = [BudgetAdjustmentLine(adjustment_id=0,
                                      source_plan_line_id=plan_with_line.lines[0].id,
                                      target_plan_line_id=plan_with_line.lines[0].id,
                                      amount=Decimal("100000"))]
        a = BudgetAdjustment(version_id=version.id,
                            adjustment_type=BudgetAdjustmentType.VIREMENT,
                            reference="ADJ-001", reason="Rebalance",
                            lines=lines, created_by="admin")
        result = repo.create_adjustment(a)
        assert result.is_success()
        session.flush()

    def test_get_adjustment(self, repo, version, plan_with_line, session):
        lines = [BudgetAdjustmentLine(adjustment_id=0,
                                      source_plan_line_id=plan_with_line.lines[0].id,
                                      amount=Decimal("50000"))]
        a = BudgetAdjustment(version_id=version.id,
                            adjustment_type=BudgetAdjustmentType.SUPPLEMENTARY,
                            reference="ADJ-002", reason="Extra",
                            lines=lines, created_by="admin")
        result = repo.create_adjustment(a)
        session.flush()
        adj = repo.get_adjustment(result.get_data().id)
        assert adj is not None
        assert adj.adjustment_type == BudgetAdjustmentType.SUPPLEMENTARY

    def test_list_adjustments(self, repo, version, plan_with_line, session):
        a = BudgetAdjustment(version_id=version.id,
                            adjustment_type=BudgetAdjustmentType.VIREMENT,
                            reference="ADJ-003", reason="Transfer",
                            created_by="admin")
        repo.create_adjustment(a)
        session.flush()
        lst = repo.list_adjustments(version.id)
        assert len(lst) >= 1


# ═══════════════════════════════════════════════════════════════════
# Commitments
# ═══════════════════════════════════════════════════════════════════

class TestCommitments:
    def test_create_commitment(self, repo, plan_with_line, session):
        c = BudgetCommitment(plan_line_id=plan_with_line.lines[0].id,
                            source_type="AP_INVOICE", source_id=100,
                            amount=Decimal("200000"), period_key="2026-01")
        result = repo.create_commitment(c)
        assert result.is_success()
        session.flush()

    def test_get_commitments(self, repo, plan_with_line, session):
        c = BudgetCommitment(plan_line_id=plan_with_line.lines[0].id,
                            source_type="PO", source_id=200,
                            amount=Decimal("100000"), period_key="2026-01")
        repo.create_commitment(c)
        session.flush()
        lst = repo.get_commitments(plan_with_line.lines[0].id)
        assert len(lst) >= 1

    def test_total_commitment(self, repo, plan_with_line, session):
        for i in range(3):
            c = BudgetCommitment(plan_line_id=plan_with_line.lines[0].id,
                                source_type="PO", source_id=i + 1,
                                amount=Decimal("100000"), period_key="2026-01")
            repo.create_commitment(c)
        session.flush()
        total = repo.get_total_commitment(plan_with_line.lines[0].id)
        assert total == Decimal("300000")


# ═══════════════════════════════════════════════════════════════════
# Control Rules
# ═══════════════════════════════════════════════════════════════════

class TestControlRules:
    def test_create_rule(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        result = repo.create_control_rule(r)
        assert result.is_success()
        session.flush()

    def test_get_rule(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        result = repo.create_control_rule(r)
        session.flush()
        r2 = repo.get_control_rule(result.get_data().id)
        assert r2 is not None
        assert r2.control_level == BudgetControlLevel.HARD_BLOCK

    def test_find_control_rule(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        repo.create_control_rule(r)
        session.flush()
        r2 = repo.find_control_rule(structure.id, "622")
        assert r2 is not None

    def test_find_control_rule_with_dimension(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622",
                              dimension_type=BudgetDimensionType.DEPARTMENT,
                              dimension_code="IT")
        repo.create_control_rule(r)
        session.flush()
        r2 = repo.find_control_rule(structure.id, "622", "department", "IT")
        assert r2 is not None

    def test_list_control_rules(self, repo, structure, session):
        r1 = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        r2 = BudgetControlRule(structure_id=structure.id, gl_account_code="511")
        repo.create_control_rule(r1)
        repo.create_control_rule(r2)
        session.flush()
        lst = repo.list_control_rules(structure.id)
        assert len(lst) >= 2

    def test_create_override(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        result = repo.create_control_rule(r)
        session.flush()
        o = BudgetOverride(control_rule_id=result.get_data().id,
                          override_code="123456",
                          requested_by="manager", reason="Emergency")
        result2 = repo.create_override(o)
        assert result2.is_success()
        session.flush()

    def test_log_block(self, repo, structure, session):
        r = BudgetControlRule(structure_id=structure.id, gl_account_code="622")
        result = repo.create_control_rule(r)
        session.flush()
        b = BudgetBlockLog(control_rule_id=result.get_data().id,
                          source_type="AP_INVOICE", source_id=1,
                          gl_account_code="622",
                          attempted_amount=Decimal("2000000"),
                          utilization_pct=Decimal("110"),
                          control_level=BudgetControlLevel.HARD_BLOCK)
        result2 = repo.log_block(b)
        assert result2.is_success()
        session.flush()


# ═══════════════════════════════════════════════════════════════════
# Consolidation
# ═══════════════════════════════════════════════════════════════════

class TestConsolidation:
    def test_create_consolidation(self, repo, version, session):
        entities = [BudgetConsolidationEntity(consolidation_id=0,
                                              entity_code="HCMC",
                                              entity_name="HCMC Branch",
                                              version_id=version.id)]
        c = BudgetConsolidation(fiscal_year=2026, parent_entity_code="HQ",
                               entities=entities)
        result = repo.create_consolidation(c)
        assert result.is_success()
        session.flush()

    def test_get_consolidation(self, repo, version, session):
        entities = [BudgetConsolidationEntity(consolidation_id=0,
                                              entity_code="HN",
                                              entity_name="HN Branch",
                                              version_id=version.id)]
        c = BudgetConsolidation(fiscal_year=2026, parent_entity_code="HQ",
                               entities=entities)
        result = repo.create_consolidation(c)
        session.flush()
        c2 = repo.get_consolidation(result.get_data().id)
        assert c2 is not None
        assert len(c2.entities) == 1

    def test_get_nonexistent_consolidation(self, repo):
        assert repo.get_consolidation(99999) is None


# ═══════════════════════════════════════════════════════════════════
# Audit Log
# ═══════════════════════════════════════════════════════════════════

class TestAuditLog:
    def test_log_audit(self, repo, session):
        repo.log_audit("budget_structure", 1, "create", "admin",
                      {"name": "NS 2026"})
        session.flush()

    def test_get_audit_logs(self, repo, session):
        repo.log_audit("budget_structure", 1, "update", "admin")
        session.flush()
        logs = repo.get_audit_logs("budget_structure", 1)
        assert len(logs) >= 1


# ═══════════════════════════════════════════════════════════════════
# Use Case Integration
# ═══════════════════════════════════════════════════════════════════

class TestUseCaseIntegration:
    def test_create_structure_uc(self, uc):
        result = uc.create_budget_structure(2026, "NS 2026")
        assert result.is_success()
        assert result.get_data().id is not None

    def test_create_structure_same_year_fails(self, uc):
        uc.create_budget_structure(2026, "NS 2026")
        result = uc.create_budget_structure(2026, "NS 2026 Dup")
        assert result.is_failure()

    def test_create_dimension_uc(self, uc):
        s = uc.create_budget_structure(2027, "NS 2027").get_data()
        result = uc.create_budget_dimension(s.id, BudgetDimensionType.DEPARTMENT,
                                            "IT", "IT Dept")
        assert result.is_success()

    def test_list_dimensions_uc(self, uc):
        s = uc.create_budget_structure(2028, "NS 2028").get_data()
        uc.create_budget_dimension(s.id, BudgetDimensionType.DEPARTMENT, "IT", "IT")
        lst = uc.list_budget_dimensions(s.id)
        assert len(lst) >= 1

    def test_create_calendar_uc(self, uc):
        phases = [{"name": "Plan", "start_date": date(2026, 1, 1),
                   "end_date": date(2026, 3, 31), "order": 1}]
        result = uc.create_budget_calendar(2026, "NS 2026", phases)
        assert result.is_success()

    def test_create_version_uc(self, uc):
        result = uc.create_budget_version(2026, "Initial", created_by="admin")
        assert result.is_success()

    def test_create_plan_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        result = uc.create_budget_plan(v.id, s.id,
                                       BudgetDimensionType.DEPARTMENT,
                                       "IT", lines, "admin")
        assert result.is_success()

    def test_get_plan_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        p2 = uc.get_budget_plan(p.id)
        assert p2 is not None
        assert p2.dimension_code == "IT"

    def test_get_plan_by_dimension_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                              "IT", lines, "admin")
        p = uc.get_budget_plan_by_dimension(v.id, BudgetDimensionType.DEPARTMENT, "IT")
        assert p is not None

    def test_submit_and_approve_budget_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        steps = [{"role": "CFO", "name": "CFO User", "min_approvers": 1}]
        wf_result = uc.submit_budget_for_approval(p.id, steps, "admin")
        assert wf_result.is_success()
        wf = wf_result.get_data()
        step = uc.approve_budget(wf.steps[0].id, "CFO User", "Approved")
        assert step.is_success()
        result = uc.finalize_approval(wf.id, p.id, "CFO User")
        assert result.is_success()

    def test_reject_approval_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V2", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        steps = [{"role": "CFO", "min_approvers": 1}]
        wf_result = uc.submit_budget_for_approval(p.id, steps, "admin")
        wf = wf_result.get_data()
        step = uc.reject_budget(wf.steps[0].id, "CFO User", "Not approved")
        assert step.is_success()

    def test_lock_unlock_version_uc(self, uc):
        v = uc.create_budget_version(2026, "V1").get_data()
        locked = uc.lock_budget_version(v.id)
        assert locked.is_locked is True
        unlocked = uc.unlock_budget_version(v.id, "Need changes")
        assert unlocked.is_locked is False

    def test_create_revised_version_uc(self, uc):
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        rv = uc.create_revised_version(v.id, "Revised V2", "admin")
        assert rv.is_success()
        assert rv.get_data().parent_version_id == v.id
        assert rv.get_data().version_number == "v2026.2"

    def test_adjustment_virement_zero_net_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}},
                 {"gl_account_code": "512", "name": "Services",
                  "amounts": {"2026-01": "200000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        adj_lines = [
            {"source_plan_line_id": p.lines[0].id, "target_plan_line_id": p.lines[1].id,
             "amount": "50000"},
            {"source_plan_line_id": p.lines[1].id, "target_plan_line_id": p.lines[0].id,
             "amount": "-50000"},
        ]
        result = uc.request_budget_adjustment(v.id, BudgetAdjustmentType.VIREMENT,
                                              "ADJ-001", "Rebalance", adj_lines, "admin")
        assert result.is_success()

    def test_execution_monitoring_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "1000000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        results = uc.get_budget_execution(v.id)
        assert len(results) >= 1
        assert results[0].budget_amount == Decimal("1000000")

    def test_variance_analysis_uc(self, uc):
        v = uc.create_budget_version(2026, "V1").get_data()
        report = uc.run_variance_analysis(v.id, "2026-01")
        assert report is not None

    def test_dashboard_uc(self, uc):
        uc.create_budget_structure(2026, "NS 2026")
        v = uc.create_budget_version(2026, "V1").get_data()
        uc.lock_budget_version(v.id)
        uc.update_budget_structure(v.fiscal_year, name="NS 2026")
        dash = uc.get_budget_dashboard(2026)
        assert dash is not None
        assert dash.fiscal_year == 2026

    def test_create_revenue_budget_line_uc(self, uc):
        result = uc.create_revenue_budget_line(
            plan_line_id=1, product_code="PROD-001",
            sales_volume=Decimal("1000"), unit_price=Decimal("50000")
        )
        assert result.is_success()
        rbl = result.get_data()
        assert rbl.driver.calculated_revenue() == Decimal("50000000.00")

    def test_create_headcount_budget_uc(self, uc):
        result = uc.create_headcount_budget(
            expense_line_id=1, fte_count=Decimal("10"),
            avg_cost_per_fte=Decimal("15000000")
        )
        assert result.is_success()
        h = result.get_data()
        assert h.total_labor_cost() > Decimal("0")

    def test_create_capex_request_uc(self, uc):
        result = uc.create_capex_request(
            plan_line_id=1, asset_type="Machinery",
            description="CNC Machine", estimated_cost=Decimal("500000000"),
            useful_life_years=10, expected_roi_pct=Decimal("15"),
            funding_source="Retained Earnings"
        )
        assert result.is_success()
        c = result.get_data()
        assert c.status == ApprovalStatus.PENDING

    def test_configure_budget_control_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        result = uc.configure_budget_control(
            s.id, "622", BudgetControlLevel.HARD_BLOCK)
        assert result.is_success()

    def test_list_control_rules_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        uc.configure_budget_control(s.id, "622", BudgetControlLevel.HARD_BLOCK)
        lst = uc.list_control_rules(s.id)
        assert len(lst) >= 1

    def test_consolidate_budget_uc(self, uc):
        v = uc.create_budget_version(2026, "V1").get_data()
        entities = [{"code": "HCMC", "name": "HCMC Branch",
                     "version_id": v.id, "fx_rate": "1"}]
        result = uc.consolidate_budget(2026, "HQ", entities)
        assert result.is_success()

    def test_generate_override_code_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        r = uc.configure_budget_control(s.id, "622",
                                        BudgetControlLevel.HARD_BLOCK).get_data()
        override = uc.generate_override_code(r.id, "manager", "Emergency", 24)
        assert override.is_success()
        assert override.get_data().override_code is not None

    def test_create_budget_template_uc(self, uc):
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "category_type": "variable", "order": 1}]
        result = uc.create_budget_template("Revenue Template",
                                           BudgetType.REVENUE, lines)
        assert result.is_success()

    def test_list_budget_templates_uc(self, uc):
        uc.create_budget_template("Rev", BudgetType.REVENUE)
        lst = uc.list_budget_templates(BudgetType.REVENUE)
        assert len(lst) >= 1

    def test_get_template_uc(self, uc):
        t = uc.create_budget_template("Rev", BudgetType.REVENUE).get_data()
        t2 = uc.get_budget_template(t.id)
        assert t2 is not None

    def test_update_plan_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        new_lines = [{"gl_account_code": "622", "name": "Salary",
                      "amounts": {"2026-01": "300000"}}]
        p2 = uc.update_budget_plan(p.id, new_lines)
        assert p2 is not None
        assert p2.lines[0].gl_account_code == "622"

    def test_version_list_uc(self, uc):
        uc.create_budget_version(2026, "V1")
        lst = uc.list_budget_versions(2026)
        assert len(lst) >= 1

    def test_close_budget_period_uc(self, uc, repo, calendar, session):
        p = BudgetPeriod(calendar_id=calendar.id, period_key="2026-12",
                         start_date=date(2026, 12, 1), end_date=date(2026, 12, 31))
        repo.create_period(p)
        session.flush()
        closed = uc.close_budget_period(p.id)
        assert closed is not None
        assert closed.is_open is False

    def test_list_budget_structures_uc(self, uc):
        uc.create_budget_structure(2026, "NS 2026")
        lst = uc.list_budget_structures()
        assert len(lst) >= 1


class TestBudgetE2E:
    """End-to-end tests for budget execution, control, variance, dashboard, and category CRUD."""

    def test_check_budget_available_no_rule(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        result = uc.check_budget_available(s.id, "511", Decimal("100000"))
        assert result["status"] == "allow"
        assert "No control rule" in result["message"]

    def test_check_budget_available_none_level(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        from domain import BudgetControlLevel
        uc.configure_budget_control(s.id, "511", BudgetControlLevel.NONE)
        result = uc.check_budget_available(s.id, "511", Decimal("100000"))
        assert result["status"] == "allow"

    def test_check_budget_available_warning(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        from domain import BudgetControlLevel
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        wf = uc.submit_budget_for_approval(p.id,
            [{"role": "CFO", "name": "CFO", "min_approvers": 1}], "admin").get_data()
        uc.approve_budget(wf.steps[0].id, "CFO", "Approved")
        uc.finalize_approval(wf.id, p.id, "CFO")
        rule = uc.configure_budget_control(s.id, "511",
            BudgetControlLevel.HARD_BLOCK).get_data()
        result = uc.check_budget_available(s.id, "511", Decimal("5000"),
                                           "DEPARTMENT", "IT", "2026-01")
        assert result["status"] in ("allow", "warning")

    def test_execution_monitoring_uc_edge(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "1000000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        results = uc.get_budget_execution(v.id, BudgetDimensionType.DEPARTMENT, "IT")
        assert len(results) >= 1
        assert results[0].budget_amount == Decimal("1000000")
        results_all = uc.get_budget_execution(v.id)
        assert len(results_all) >= 1

    def test_variance_analysis_uc_edge(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "500000", "2026-02": "600000"}}]
        uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                              "IT", lines, "admin").get_data()
        report = uc.run_variance_analysis(v.id, "2026-01")
        assert report is not None
        assert len(report.lines) >= 1
        assert report.lines[0].budget_amount >= Decimal("1000000")

    def test_dashboard_uc_edge(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        uc.create_budget_plan(v.id, s.id, BudgetDimensionType.PRODUCT_LINE,
                              "PROD-A", lines, "admin").get_data()
        lines2 = [{"gl_account_code": "622", "name": "Salary",
                   "amounts": {"2026-01": "50000"}}]
        uc.create_budget_plan(v.id, s.id, BudgetDimensionType.COST_CENTER,
                              "CC-IT", lines2, "admin").get_data()
        uc.lock_budget_version(v.id)
        dash = uc.get_budget_dashboard(2026)
        assert dash is not None
        assert dash.fiscal_year == 2026

    def test_create_and_list_category_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        result = uc.create_budget_category(
            s.id, BudgetType.EXPENSE, "Raw Materials",
            BudgetCategoryType.VARIABLE, ["621", "622"]
        )
        assert result.is_success()
        cat = result.get_data()
        assert cat.name == "Raw Materials"
        assert cat.gl_account_codes == ["621", "622"]
        lst = uc.list_budget_categories(s.id)
        assert len(lst) >= 1
        assert any(c.name == "Raw Materials" for c in lst)

    def test_duplicate_category_uc(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        uc.create_budget_category(s.id, BudgetType.EXPENSE, "Duplicate")
        result = uc.create_budget_category(s.id, BudgetType.EXPENSE, "Duplicate")
        assert result.is_failure()

    def test_adjustment_supplementary_with_target(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}},
                 {"gl_account_code": "512", "name": "Services",
                  "amounts": {"2026-01": "200000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        adj_lines = [
            {"source_plan_line_id": p.lines[0].id, "target_plan_line_id": p.lines[1].id,
             "amount": "30000", "period_key": "2026-01"},
        ]
        adj = uc.request_budget_adjustment(v.id, BudgetAdjustmentType.SUPPLEMENTARY,
                                           "ADJ-SUP-001", "Increase Services", adj_lines, "admin")
        assert adj.is_success()
        wf = adj.get_data()
        approve = uc.approve_adjustment(wf.id, "CFO")
        assert approve.is_success()
        updated = uc.get_budget_plan(p.id)
        tgt_line = [l for l in updated.lines if l.gl_account_code == "512"][0]
        assert Decimal(tgt_line.amounts.get("2026-01", "0")) == Decimal("230000")

    def test_adjustment_supplementary_no_target(self, uc):
        s = uc.create_budget_structure(2026, "NS 2026").get_data()
        v = uc.create_budget_version(2026, "V1", created_by="admin").get_data()
        lines = [{"gl_account_code": "511", "name": "Sales",
                  "amounts": {"2026-01": "100000"}}]
        p = uc.create_budget_plan(v.id, s.id, BudgetDimensionType.DEPARTMENT,
                                  "IT", lines, "admin").get_data()
        src_line = p.lines[0]
        adj_lines = [
            {"source_plan_line_id": src_line.id,
             "amount": "20000", "period_key": "2026-01"},
        ]
        adj = uc.request_budget_adjustment(v.id, BudgetAdjustmentType.SUPPLEMENTARY,
                                           "ADJ-SUP-001", "Increase budget", adj_lines, "admin")
        assert adj.is_success()
        wf = adj.get_data()
        approve = uc.approve_adjustment(wf.id, "CFO")
        assert approve.is_success()
