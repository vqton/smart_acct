from decimal import Decimal
from datetime import date, datetime
import pytest
from domain.budget import (
    BudgetType, BudgetVersionStatus, BudgetPeriodType,
    BudgetControlLevel, BudgetDimensionType, BudgetCategoryType,
    AdjustmentType, ApprovalStatus, VarianceFlag, KPIThreshold, OverrideStatus,
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
    HeadcountBudget, ExpenseBudgetLine, BudgetAuditLog,
)
from domain.common import AccountError


class TestBudgetStructure:
    def test_valid_minimal(self):
        s = BudgetStructure(name="NS 2026", fiscal_year=2026)
        assert s.fiscal_year == 2026
        assert s.name == "NS 2026"
        assert BudgetType.REVENUE in s.budget_types
        assert BudgetType.EXPENSE in s.budget_types
        assert s.period_type == BudgetPeriodType.MONTHLY

    def test_valid_custom(self):
        s = BudgetStructure(name="CAPEX 2027", fiscal_year=2027,
                            budget_types=[BudgetType.CAPEX],
                            dimensions=[BudgetDimensionType.PROJECT])
        assert len(s.budget_types) == 1
        assert s.dimensions[0] == BudgetDimensionType.PROJECT

    def test_fiscal_year_too_early(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FISCAL_YEAR"):
            BudgetStructure(name="Bad", fiscal_year=1999)

    def test_fiscal_year_too_late(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FISCAL_YEAR"):
            BudgetStructure(name="Bad", fiscal_year=2101)

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            BudgetStructure(name="", fiscal_year=2026)

    def test_id_optional(self):
        s = BudgetStructure(name="Test", fiscal_year=2026, id=42)
        assert s.id == 42


class TestBudgetDimension:
    def test_valid_minimal(self):
        d = BudgetDimension(structure_id=1, dimension_type=BudgetDimensionType.COST_CENTER,
                            code="CC001", name="IT Department")
        assert d.code == "CC001"
        assert d.is_active is True

    def test_code_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_DIM_CODE_EMPTY"):
            BudgetDimension(structure_id=1, dimension_type=BudgetDimensionType.DEPARTMENT,
                            code="", name="Test")

    def test_code_whitespace_raises(self):
        with pytest.raises(AccountError):
            BudgetDimension(structure_id=1, dimension_type=BudgetDimensionType.DEPARTMENT,
                            code="   ", name="Test")

    def test_code_too_long(self):
        with pytest.raises(Exception):
            BudgetDimension(structure_id=1, dimension_type=BudgetDimensionType.DEPARTMENT,
                            code="X" * 51, name="Test")


class TestBudgetCategory:
    def test_valid_minimal(self):
        c = BudgetCategory(structure_id=1, budget_type=BudgetType.EXPENSE, name="Salary")
        assert c.category_type == BudgetCategoryType.VARIABLE
        assert c.gl_account_codes == []

    def test_name_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_CATEGORY_NAME_EMPTY"):
            BudgetCategory(structure_id=1, budget_type=BudgetType.EXPENSE, name="")

    def test_with_gl_accounts(self):
        c = BudgetCategory(structure_id=1, budget_type=BudgetType.REVENUE, name="Sales",
                           gl_account_codes=["511", "512"])
        assert "511" in c.gl_account_codes


class TestBudgetCalendarPhase:
    def test_valid(self):
        p = BudgetCalendarPhase(calendar_id=1, phase_name="Planning",
                                start_date=date(2026, 1, 1), end_date=date(2026, 2, 28),
                                phase_order=1)
        assert p.phase_name == "Planning"

    def test_end_before_start_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_DATE_RANGE"):
            BudgetCalendarPhase(calendar_id=1, phase_name="Bad",
                                start_date=date(2026, 3, 1), end_date=date(2026, 2, 28),
                                phase_order=1)


class TestBudgetCalendar:
    def test_valid_minimal(self):
        c = BudgetCalendar(fiscal_year=2026, name="NS 2026 Calendar")
        assert c.fiscal_year == 2026
        assert c.is_active is True

    def test_with_phases(self):
        phases = [BudgetCalendarPhase(calendar_id=0, phase_name="Plan",
                                      start_date=date(2026, 1, 1), end_date=date(2026, 3, 31),
                                      phase_order=1)]
        c = BudgetCalendar(fiscal_year=2026, name="Test", phases=phases)
        assert len(c.phases) == 1

    def test_fiscal_year_invalid(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FISCAL_YEAR"):
            BudgetCalendar(fiscal_year=1999, name="Bad")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            BudgetCalendar(fiscal_year=2026, name="")


class TestBudgetPeriod:
    def test_valid(self):
        p = BudgetPeriod(calendar_id=1, period_key="2026-01",
                         start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        assert p.period_key == "2026-01"
        assert p.is_open is True
        assert p.period_type == BudgetPeriodType.MONTHLY

    def test_key_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_PERIOD_KEY_EMPTY"):
            BudgetPeriod(calendar_id=1, period_key="", start_date=date(2026, 1, 1),
                         end_date=date(2026, 1, 31))

    def test_quarterly(self):
        p = BudgetPeriod(calendar_id=1, period_key="2026-Q1",
                         period_type=BudgetPeriodType.QUARTERLY,
                         start_date=date(2026, 1, 1), end_date=date(2026, 3, 31))
        assert p.period_type == BudgetPeriodType.QUARTERLY


class TestBudgetTemplateLine:
    def test_valid_minimal(self):
        l = BudgetTemplateLine(template_id=1, gl_account_code="511", name="Sales Revenue")
        assert l.line_order == 0
        assert l.category_type == BudgetCategoryType.VARIABLE
        assert l.is_required is False

    def test_with_custom_values(self):
        l = BudgetTemplateLine(template_id=1, gl_account_code="622", name="Salary",
                                line_order=1, category_type=BudgetCategoryType.FIXED,
                                formula="PRIOR_YEAR * 1.1", is_required=True,
                                default_amount=Decimal("1000000"))
        assert l.formula == "PRIOR_YEAR * 1.1"
        assert l.default_amount == Decimal("1000000.00")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_TEMPLATE_LINE_NAME_EMPTY"):
            BudgetTemplateLine(template_id=1, gl_account_code="511", name="")

    def test_negative_amount_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            BudgetTemplateLine(template_id=1, gl_account_code="511", name="Test",
                               default_amount=Decimal("-100"))


class TestBudgetTemplate:
    def test_valid_minimal(self):
        t = BudgetTemplate(name="Revenue Template", budget_type=BudgetType.REVENUE)
        assert t.budget_type == BudgetType.REVENUE
        assert t.lines == []

    def test_with_lines(self):
        lines = [BudgetTemplateLine(template_id=0, gl_account_code="511", name="Sales")]
        t = BudgetTemplate(name="Test", budget_type=BudgetType.REVENUE, lines=lines)
        assert len(t.lines) == 1

    def test_name_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_TEMPLATE_NAME_EMPTY"):
            BudgetTemplate(name="", budget_type=BudgetType.EXPENSE)

    def test_expense_template(self):
        t = BudgetTemplate(name="Opex", budget_type=BudgetType.EXPENSE)
        assert t.budget_type == BudgetType.EXPENSE


class TestBudgetVersion:
    def test_valid_minimal(self):
        v = BudgetVersion(fiscal_year=2026, version_number="v2026.1", label="Initial")
        assert v.status == BudgetVersionStatus.DRAFT
        assert v.is_locked is False

    def test_valid_all_fields(self):
        v = BudgetVersion(fiscal_year=2026, version_number="v2026.2", label="Revised",
                          status=BudgetVersionStatus.APPROVED, is_locked=True,
                          parent_version_id=1, notes="Approved version",
                          created_by="admin")
        assert v.is_locked is True
        assert v.parent_version_id == 1

    def test_version_number_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_VERSION_NUMBER_EMPTY"):
            BudgetVersion(fiscal_year=2026, version_number="", label="Test")

    def test_label_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_VERSION_LABEL_EMPTY"):
            BudgetVersion(fiscal_year=2026, version_number="v1", label="")

    def test_fiscal_year_invalid(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FISCAL_YEAR"):
            BudgetVersion(fiscal_year=1999, version_number="v1", label="Test")


class TestBudgetPlanDriver:
    def test_valid_minimal(self):
        d = BudgetPlanDriver(plan_line_id=1)
        assert d.quantity == Decimal("0")
        assert d.unit_rate == Decimal("0")

    def test_valid_with_values(self):
        d = BudgetPlanDriver(plan_line_id=1, quantity=Decimal("100"),
                             unit_rate=Decimal("50000"), driver_name="Headcount")
        assert d.quantity == Decimal("100.00")
        assert d.driver_name == "Headcount"

    def test_negative_quantity_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            BudgetPlanDriver(plan_line_id=1, quantity=Decimal("-10"))

    def test_negative_unit_rate_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            BudgetPlanDriver(plan_line_id=1, unit_rate=Decimal("-5000"))


class TestBudgetPlanLine:
    def test_valid_minimal(self):
        l = BudgetPlanLine(plan_id=1, gl_account_code="511", name="Sales")
        assert l.amounts == {}
        assert l.category_type == BudgetCategoryType.VARIABLE

    def test_with_amounts(self):
        l = BudgetPlanLine(plan_id=1, gl_account_code="511", name="Sales",
                           amounts={"2026-01": Decimal("100000"), "2026-02": Decimal("150000")})
        assert len(l.amounts) == 2

    def test_with_driver(self):
        d = BudgetPlanDriver(plan_line_id=0, quantity=Decimal("10"), unit_rate=Decimal("50000"))
        l = BudgetPlanLine(plan_id=1, gl_account_code="511", name="Sales", driver=d)
        assert l.driver is not None

    def test_account_code_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_ACCOUNT_CODE_EMPTY"):
            BudgetPlanLine(plan_id=1, gl_account_code="", name="Test")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_LINE_NAME_EMPTY"):
            BudgetPlanLine(plan_id=1, gl_account_code="511", name="")


class TestBudgetPlan:
    def test_valid_minimal(self):
        p = BudgetPlan(version_id=1, structure_id=1,
                       dimension_type=BudgetDimensionType.COST_CENTER,
                       dimension_code="CC001")
        assert p.lines == []
        assert p.total_amount() == Decimal("0")

    def test_with_lines(self):
        lines = [BudgetPlanLine(plan_id=0, gl_account_code="511", name="Sales",
                                amounts={"2026-01": Decimal("100000")})]
        p = BudgetPlan(version_id=1, structure_id=1,
                       dimension_type=BudgetDimensionType.DEPARTMENT,
                       dimension_code="IT", lines=lines)
        assert p.total_amount() == Decimal("100000")

    def test_multiple_lines_total(self):
        lines = [
            BudgetPlanLine(plan_id=0, gl_account_code="511", name="Sales",
                           amounts={"2026-01": Decimal("100000")}),
            BudgetPlanLine(plan_id=0, gl_account_code="512", name="Services",
                           amounts={"2026-01": Decimal("200000"), "2026-02": Decimal("300000")}),
        ]
        p = BudgetPlan(version_id=1, structure_id=1,
                       dimension_type=BudgetDimensionType.COST_CENTER,
                       dimension_code="CC001", lines=lines)
        assert p.total_amount() == Decimal("600000")

    def test_dim_code_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_DIM_CODE_EMPTY"):
            BudgetPlan(version_id=1, structure_id=1,
                       dimension_type=BudgetDimensionType.DEPARTMENT,
                       dimension_code="")


class TestBudgetApprovalStep:
    def test_valid_minimal(self):
        s = BudgetApprovalStep(workflow_id=1, step_order=1, approver_role="CFO")
        assert s.status == ApprovalStatus.PENDING
        assert s.min_approvers == 1

    def test_valid_all_fields(self):
        s = BudgetApprovalStep(workflow_id=1, step_order=2, approver_role="Board",
                               approver_name="Nguyen Van A", min_approvers=2,
                               status=ApprovalStatus.APPROVED, comments="Approved",
                               acted_at=datetime(2026, 6, 1))
        assert s.status == ApprovalStatus.APPROVED
        assert s.approver_name == "Nguyen Van A"

    def test_step_order_zero_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_STEP_ORDER"):
            BudgetApprovalStep(workflow_id=1, step_order=0, approver_role="CFO")


class TestBudgetApprovalWorkflow:
    def test_valid_minimal(self):
        w = BudgetApprovalWorkflow(plan_id=1)
        assert w.status == BudgetVersionStatus.DRAFT

    def test_with_steps(self):
        steps = [BudgetApprovalStep(workflow_id=0, step_order=1, approver_role="CFO")]
        w = BudgetApprovalWorkflow(plan_id=1, steps=steps)
        assert len(w.steps) == 1

    def test_with_completed(self):
        w = BudgetApprovalWorkflow(plan_id=1, status=BudgetVersionStatus.APPROVED,
                                   completed_at=datetime(2026, 6, 1))
        assert w.status == BudgetVersionStatus.APPROVED


class TestBudgetApprovalLog:
    def test_valid(self):
        l = BudgetApprovalLog(workflow_id=1, step_id=1, action="approve",
                              actor="admin", comments="Looks good")
        assert l.action == "approve"
        assert l.actor == "admin"


class TestBudgetAdjustmentLine:
    def test_valid_source_to_target(self):
        l = BudgetAdjustmentLine(adjustment_id=1, source_plan_line_id=10,
                                 target_plan_line_id=20, amount=Decimal("500000"))
        assert l.amount == Decimal("500000.00")

    def test_zero_amount(self):
        l = BudgetAdjustmentLine(adjustment_id=1, amount=Decimal("0"))
        assert l.amount == Decimal("0.00")

    def test_with_period_key(self):
        l = BudgetAdjustmentLine(adjustment_id=1, amount=Decimal("100000"),
                                 period_key="2026-06")
        assert l.period_key == "2026-06"


class TestBudgetAdjustment:
    def test_valid_minimal(self):
        a = BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.VIREMENT,
                             reference="ADJ-001", reason="Rebalance budget lines",
                             created_by="admin")
        assert a.status == ApprovalStatus.PENDING
        assert a.net_change() == Decimal("0")

    def test_with_lines(self):
        lines = [BudgetAdjustmentLine(adjustment_id=0, amount=Decimal("500000"))]
        a = BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.SUPPLEMENTARY,
                             reference="ADJ-002", reason="Additional funding",
                             lines=lines, created_by="admin")
        assert a.net_change() == Decimal("500000.00")

    def test_multiple_lines_net_change(self):
        lines = [
            BudgetAdjustmentLine(adjustment_id=0, amount=Decimal("300000")),
            BudgetAdjustmentLine(adjustment_id=0, amount=Decimal("-100000")),
        ]
        a = BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.VIREMENT,
                             reference="ADJ-003", reason="Transfer",
                             lines=lines, created_by="admin")
        assert a.net_change() == Decimal("200000.00")

    def test_reference_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_ADJ_REF_EMPTY"):
            BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.VIREMENT,
                             reference="", reason="Test", created_by="admin")

    def test_reason_empty_raises(self):
        with pytest.raises(AccountError, match="BUDGET_ADJ_REASON_EMPTY"):
            BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.VIREMENT,
                             reference="ADJ-001", reason="", created_by="admin")

    def test_emergency_type(self):
        a = BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.EMERGENCY,
                             reference="ADJ-004", reason="Emergency fund",
                             created_by="admin")
        assert a.adjustment_type == AdjustmentType.EMERGENCY

    def test_reduction_type(self):
        a = BudgetAdjustment(version_id=1, adjustment_type=AdjustmentType.REDUCTION,
                             reference="ADJ-005", reason="Cut costs",
                             created_by="admin")
        assert a.adjustment_type == AdjustmentType.REDUCTION


class TestBudgetCommitment:
    def test_valid(self):
        c = BudgetCommitment(plan_line_id=1, source_type="AP_INVOICE",
                             source_id=100, amount=Decimal("500000"),
                             period_key="2026-06")
        assert c.amount == Decimal("500000.00")

    def test_negative_amount_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            BudgetCommitment(plan_line_id=1, source_type="PO", source_id=1,
                             amount=Decimal("-1000"), period_key="2026-06")


class TestBudgetExecutionItem:
    def test_defaults(self):
        item = BudgetExecutionItem(plan_line_id=1)
        assert item.budget_amount == Decimal("0")
        assert item.free_balance == Decimal("0")

    def test_calculate_free_balance(self):
        item = BudgetExecutionItem(plan_line_id=1, budget_amount=Decimal("1000000"),
                                    actual_amount=Decimal("300000"),
                                    commitment_amount=Decimal("200000"))
        item.calculate()
        assert item.free_balance == Decimal("500000")
        assert item.utilization_pct == Decimal("50.00")

    def test_zero_budget_does_not_divide(self):
        item = BudgetExecutionItem(plan_line_id=1)
        item.calculate()
        assert item.utilization_pct == Decimal("0")

    def test_full_utilization(self):
        item = BudgetExecutionItem(plan_line_id=1, budget_amount=Decimal("1000000"),
                                    actual_amount=Decimal("1000000"))
        item.calculate()
        assert item.free_balance == Decimal("0")
        assert item.utilization_pct == Decimal("100.00")

    def test_over_utilization(self):
        item = BudgetExecutionItem(plan_line_id=1, budget_amount=Decimal("1000000"),
                                    actual_amount=Decimal("1200000"))
        item.calculate()
        assert item.free_balance == Decimal("-200000")


class TestBudgetControlRule:
    def test_valid_minimal(self):
        r = BudgetControlRule(structure_id=1, gl_account_code="622")
        assert r.control_level == BudgetControlLevel.HARD_BLOCK
        assert r.warning_threshold_pct == Decimal("80.00")

    def test_valid_all_fields(self):
        r = BudgetControlRule(structure_id=1, gl_account_code="622",
                              dimension_type=BudgetDimensionType.DEPARTMENT,
                              dimension_code="IT",
                              control_level=BudgetControlLevel.WARNING_ONLY,
                              warning_threshold_pct=Decimal("75"),
                              soft_block_threshold_pct=Decimal("85"),
                              hard_block_threshold_pct=Decimal("95"))
        assert r.control_level == BudgetControlLevel.WARNING_ONLY

    def test_threshold_too_high_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_THRESHOLD"):
            BudgetControlRule(structure_id=1, gl_account_code="622",
                             warning_threshold_pct=Decimal("2000"))

    def test_threshold_negative_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_THRESHOLD"):
            BudgetControlRule(structure_id=1, gl_account_code="622",
                             warning_threshold_pct=Decimal("-10"))

    def test_max_threshold_allowed(self):
        r = BudgetControlRule(structure_id=1, gl_account_code="622",
                              hard_block_threshold_pct=Decimal("1000"))
        assert r.hard_block_threshold_pct == Decimal("1000.00")

    def test_control_level_soft_block(self):
        r = BudgetControlRule(structure_id=1, gl_account_code="622",
                              control_level=BudgetControlLevel.SOFT_BLOCK)
        assert r.control_level == BudgetControlLevel.SOFT_BLOCK

    def test_control_level_none(self):
        r = BudgetControlRule(structure_id=1, gl_account_code="622",
                              control_level=BudgetControlLevel.NONE)
        assert r.control_level == BudgetControlLevel.NONE


class TestBudgetOverride:
    def test_valid(self):
        o = BudgetOverride(control_rule_id=1, override_code="123456",
                           requested_by="manager", reason="Emergency")
        assert o.status == OverrideStatus.ACTIVE
        assert o.expires_at is None

    def test_with_expiry(self):
        o = BudgetOverride(control_rule_id=1, override_code="654321",
                           requested_by="manager", reason="Urgent",
                           expires_at=datetime(2026, 7, 1))
        assert o.expires_at is not None

    def test_used_status(self):
        o = BudgetOverride(control_rule_id=1, override_code="111111",
                           requested_by="manager", reason="Test",
                           status=OverrideStatus.USED, used_at=datetime(2026, 6, 1))
        assert o.status == OverrideStatus.USED


class TestBudgetBlockLog:
    def test_valid(self):
        b = BudgetBlockLog(control_rule_id=1, source_type="AP_INVOICE",
                           source_id=100, gl_account_code="622",
                           attempted_amount=Decimal("2000000"),
                           utilization_pct=Decimal("110"),
                           control_level=BudgetControlLevel.HARD_BLOCK)
        assert b.was_blocked is True

    def test_with_override(self):
        b = BudgetBlockLog(control_rule_id=1, source_type="PO", source_id=50,
                           gl_account_code="622", attempted_amount=Decimal("500000"),
                           utilization_pct=Decimal("95"),
                           control_level=BudgetControlLevel.SOFT_BLOCK,
                           was_blocked=False, override_id=1)
        assert b.override_id == 1
        assert b.was_blocked is False


class TestBudgetICTransaction:
    def test_valid(self):
        ic = BudgetICTransaction(consolidation_id=1, from_entity_code="HCMC",
                                 to_entity_code="HANOI", gl_account_code="511",
                                 amount=Decimal("100000"))
        assert ic.amount == Decimal("100000.00")


class TestBudgetConsolidationEntity:
    def test_valid(self):
        e = BudgetConsolidationEntity(consolidation_id=1, entity_code="HCMC",
                                      entity_name="Ho Chi Minh Branch",
                                      version_id=1)
        assert e.fx_rate == Decimal("1.00")

    def test_invalid_fx_rate_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FX_RATE"):
            BudgetConsolidationEntity(consolidation_id=1, entity_code="HCMC",
                                      entity_name="Test", version_id=1,
                                      fx_rate=Decimal("0"))

    def test_negative_fx_rate_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_FX_RATE"):
            BudgetConsolidationEntity(consolidation_id=1, entity_code="HCMC",
                                      entity_name="Test", version_id=1,
                                      fx_rate=Decimal("-1"))


class TestBudgetConsolidation:
    def test_valid_minimal(self):
        c = BudgetConsolidation(fiscal_year=2026, parent_entity_code="HQ")
        assert c.status == BudgetVersionStatus.DRAFT
        assert c.entities == []

    def test_with_entities(self):
        entities = [BudgetConsolidationEntity(consolidation_id=0, entity_code="HCMC",
                                              entity_name="Branch", version_id=1)]
        c = BudgetConsolidation(fiscal_year=2026, parent_entity_code="HQ",
                                entities=entities)
        assert len(c.entities) == 1


class TestBudgetVarianceAnnotation:
    def test_valid(self):
        a = BudgetVarianceAnnotation(variance_line_id=1, annotation="Due to market",
                                     created_by="analyst")
        assert a.annotation == "Due to market"


class TestBudgetVarianceLine:
    def test_valid(self):
        l = BudgetVarianceLine(report_id=1, gl_account_code="511", name="Sales",
                               budget_amount=Decimal("1000000"),
                               actual_amount=Decimal("800000"),
                               variance_amount=Decimal("-200000"),
                               variance_pct=Decimal("-20"),
                               flag=VarianceFlag.UNFAVORABLE)
        assert l.flag == VarianceFlag.UNFAVORABLE

    def test_favorable_variance(self):
        l = BudgetVarianceLine(report_id=1, gl_account_code="622", name="Cost",
                               budget_amount=Decimal("500000"),
                               actual_amount=Decimal("450000"),
                               variance_amount=Decimal("50000"),
                               variance_pct=Decimal("10"),
                               flag=VarianceFlag.FAVORABLE)
        assert l.flag == VarianceFlag.FAVORABLE

    def test_with_annotations(self):
        anns = [BudgetVarianceAnnotation(variance_line_id=0, annotation="Savings",
                                         created_by="analyst")]
        l = BudgetVarianceLine(report_id=1, gl_account_code="511", name="Sales",
                               budget_amount=Decimal("1000000"),
                               actual_amount=Decimal("900000"),
                               variance_amount=Decimal("100000"),
                               variance_pct=Decimal("10"),
                               flag=VarianceFlag.FAVORABLE,
                               annotations=anns)
        assert len(l.annotations) == 1


class TestBudgetVarianceReport:
    def test_valid(self):
        r = BudgetVarianceReport(fiscal_year=2026, version_id=1, period_key="2026-Q1")
        assert r.lines == []

    def test_with_lines(self):
        lines = [BudgetVarianceLine(report_id=0, gl_account_code="511", name="Sales",
                                    budget_amount=Decimal("1000000"),
                                    actual_amount=Decimal("800000"),
                                    variance_amount=Decimal("-200000"),
                                    variance_pct=Decimal("-20"),
                                    flag=VarianceFlag.UNFAVORABLE)]
        r = BudgetVarianceReport(fiscal_year=2026, version_id=1, period_key="2026-Q1",
                                 lines=lines)
        assert len(r.lines) == 1


class TestBudgetKPIValue:
    def test_valid(self):
        v = BudgetKPIValue(kpi_id=1, period_key="2026-06",
                           actual_value=Decimal("95"), target_value=Decimal("100"))
        assert v.threshold == KPIThreshold.GREEN

    def test_yellow_threshold(self):
        v = BudgetKPIValue(kpi_id=1, period_key="2026-06",
                           actual_value=Decimal("80"), target_value=Decimal("100"),
                           threshold=KPIThreshold.YELLOW)
        assert v.threshold == KPIThreshold.YELLOW


class TestBudgetKPI:
    def test_valid(self):
        k = BudgetKPI(structure_id=1, kpi_code="REV_GROWTH",
                      kpi_name="Revenue Growth", expression="(Current - Prior) / Prior * 100")
        assert k.is_active is True
        assert k.green_min == Decimal("90.00")

    def test_custom_thresholds(self):
        k = BudgetKPI(structure_id=1, kpi_code="OPEX_RATIO",
                      kpi_name="OPEX Ratio", expression="OPEX / Revenue * 100",
                      green_min=Decimal("95"), yellow_min=Decimal("80"))
        assert k.yellow_min == Decimal("80.00")


class TestBudgetDashboard:
    def test_valid(self):
        d = BudgetDashboard(fiscal_year=2026)
        assert d.burn_rate == Decimal("0")
        assert d.ytd_variance == Decimal("0")
        assert d.days_of_budget_left is None

    def test_with_kpis(self):
        kpis = [BudgetKPIValue(kpi_id=1, period_key="2026-06",
                               actual_value=Decimal("95"), target_value=Decimal("100"))]
        d = BudgetDashboard(fiscal_year=2026, kpis=kpis,
                            revenue_achievement=Decimal("85"),
                            opex_utilization=Decimal("72"),
                            capex_utilization=Decimal("30"))
        assert d.revenue_achievement == Decimal("85")
        assert len(d.kpis) == 1


class TestRevenueSeasonality:
    def test_valid(self):
        s = RevenueSeasonality(revenue_line_id=1, month=6, weight_pct=Decimal("10"))
        assert s.weight_pct == Decimal("10.00")

    def test_month_out_of_range_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_MONTH"):
            RevenueSeasonality(revenue_line_id=1, month=13, weight_pct=Decimal("10"))

    def test_month_zero_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_MONTH"):
            RevenueSeasonality(revenue_line_id=1, month=0, weight_pct=Decimal("10"))

    def test_weight_negative_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_WEIGHT"):
            RevenueSeasonality(revenue_line_id=1, month=6, weight_pct=Decimal("-5"))

    def test_weight_over_100_raises(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_WEIGHT"):
            RevenueSeasonality(revenue_line_id=1, month=6, weight_pct=Decimal("101"))


class TestRevenueBudgetDriver:
    def test_valid(self):
        d = RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("1000"),
                                unit_price=Decimal("50000"))
        assert d.calculated_revenue() == Decimal("50000000.00")

    def test_with_growth_rate(self):
        d = RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("1000"),
                                unit_price=Decimal("50000"),
                                growth_rate_pct=Decimal("10"),
                                fx_rate=Decimal("1"))
        assert d.growth_rate_pct == Decimal("10")

    def test_negative_volume_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_VOLUME"):
            RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("-100"),
                                unit_price=Decimal("50000"))

    def test_negative_price_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_PRICE"):
            RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("100"),
                                unit_price=Decimal("-50000"))

    def test_currency_default(self):
        d = RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("100"),
                                unit_price=Decimal("50000"))
        assert d.currency_code == "VND"

    def test_calculated_revenue_with_fx(self):
        d = RevenueBudgetDriver(revenue_line_id=1, sales_volume=Decimal("100"),
                                unit_price=Decimal("50"), fx_rate=Decimal("23000"))
        assert d.calculated_revenue() == Decimal("115000000.00")


class TestRevenueBudgetLine:
    def test_valid_minimal(self):
        r = RevenueBudgetLine(plan_line_id=1)
        assert r.product_code is None

    def test_with_fields(self):
        d = RevenueBudgetDriver(revenue_line_id=0, sales_volume=Decimal("1000"),
                                unit_price=Decimal("50000"))
        r = RevenueBudgetLine(plan_line_id=1, product_code="PROD-001",
                              region_code="HCMC", channel_code="Retail", driver=d)
        assert r.product_code == "PROD-001"
        assert r.driver is not None


class TestHeadcountBudget:
    def test_valid(self):
        h = HeadcountBudget(expense_line_id=1, fte_count=Decimal("10"),
                            avg_cost_per_fte=Decimal("15000000"))
        assert h.fte_count == Decimal("10.00")
        assert h.si_employer_pct == Decimal("23.50")

    def test_total_labor_cost(self):
        h = HeadcountBudget(expense_line_id=1, fte_count=Decimal("10"),
                            avg_cost_per_fte=Decimal("15000000"))
        total = h.total_labor_cost()
        annual_salary = Decimal("15000000") * Decimal("10") * Decimal("12")
        employer_si = annual_salary * Decimal("23.5") / Decimal("100")
        assert total == (annual_salary + employer_si).quantize(Decimal("0.01"))

    def test_negative_fte_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_FTE"):
            HeadcountBudget(expense_line_id=1, fte_count=Decimal("-1"),
                           avg_cost_per_fte=Decimal("15000000"))

    def test_negative_cost_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_COST"):
            HeadcountBudget(expense_line_id=1, fte_count=Decimal("10"),
                           avg_cost_per_fte=Decimal("-50000"))


class TestExpenseBudgetLine:
    def test_valid(self):
        e = ExpenseBudgetLine(plan_line_id=1, expense_category="Salary")
        assert e.is_zero_based is False

    def test_with_headcount(self):
        h = HeadcountBudget(expense_line_id=0, fte_count=Decimal("5"),
                           avg_cost_per_fte=Decimal("10000000"))
        e = ExpenseBudgetLine(plan_line_id=1, expense_category="Salary",
                             is_zero_based=True, headcount=h)
        assert e.is_zero_based is True

    def test_with_justification(self):
        e = ExpenseBudgetLine(plan_line_id=1, expense_category="Marketing",
                             justification="Annual marketing campaign")
        assert e.justification == "Annual marketing campaign"


class TestCAPEXRequest:
    def test_valid(self):
        c = CAPEXRequest(plan_line_id=1, asset_type="Machinery",
                         description="CNC Machine", estimated_cost=Decimal("500000000"),
                         useful_life_years=10, expected_roi_pct=Decimal("15"),
                         funding_source="Retained Earnings")
        assert c.status == ApprovalStatus.PENDING

    def test_negative_cost_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_COST"):
            CAPEXRequest(plan_line_id=1, asset_type="Test", description="Test",
                        estimated_cost=Decimal("-1000"), useful_life_years=5,
                        expected_roi_pct=Decimal("10"), funding_source="Loan")

    def test_useful_life_too_short(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_USEFUL_LIFE"):
            CAPEXRequest(plan_line_id=1, asset_type="Test", description="Test",
                        estimated_cost=Decimal("1000000"), useful_life_years=0,
                        expected_roi_pct=Decimal("10"), funding_source="Loan")

    def test_useful_life_too_long(self):
        with pytest.raises(AccountError, match="BUDGET_INVALID_USEFUL_LIFE"):
            CAPEXRequest(plan_line_id=1, asset_type="Test", description="Test",
                        estimated_cost=Decimal("1000000"), useful_life_years=51,
                        expected_roi_pct=Decimal("10"), funding_source="Loan")

    def test_approved(self):
        c = CAPEXRequest(plan_line_id=1, asset_type="Vehicle",
                         description="Delivery truck", estimated_cost=Decimal("800000000"),
                         useful_life_years=7, expected_roi_pct=Decimal("12"),
                         funding_source="Bank Loan",
                         status=ApprovalStatus.APPROVED,
                         approved_by="CFO", approved_at=datetime(2026, 6, 1))
        assert c.status == ApprovalStatus.APPROVED

    def test_capex_defaults(self):
        c = CAPEXRequest(plan_line_id=1, asset_type="Equipment",
                         description="Office equipment", estimated_cost=Decimal("50000000"),
                         expected_roi_pct=Decimal("8"), funding_source="Budget")
        assert c.useful_life_years == 5


class TestCashFlowBudgetLine:
    def test_valid(self):
        c = CashFlowBudgetLine(plan_line_id=1, cash_flow_type="OPERATING",
                               period_key="2026-06",
                               inflow_amount=Decimal("1000000"),
                               outflow_amount=Decimal("600000"))
        assert c.net_amount == Decimal("0")  # default

    def test_negative_inflow_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            CashFlowBudgetLine(plan_line_id=1, cash_flow_type="OPERATING",
                              period_key="2026-06", inflow_amount=Decimal("-100"))

    def test_negative_outflow_raises(self):
        with pytest.raises(AccountError, match="BUDGET_NEGATIVE_AMOUNT"):
            CashFlowBudgetLine(plan_line_id=1, cash_flow_type="INVESTING",
                              period_key="2026-06", outflow_amount=Decimal("-100"))


class TestCashFlowFinancing:
    def test_valid(self):
        f = CashFlowFinancing(cash_flow_line_id=1, financing_type="Loan",
                              amount=Decimal("500000000"))
        assert f.is_additional is True

    def test_repayment(self):
        f = CashFlowFinancing(cash_flow_line_id=1, financing_type="Loan Repayment",
                              amount=Decimal("100000000"), is_additional=False)
        assert f.is_additional is False


class TestBudgetAuditLog:
    def test_valid(self):
        l = BudgetAuditLog(entity_type="budget_structure", entity_id=1,
                           action="create", changes={"name": "NS 2026"},
                           actor="admin")
        assert l.action == "create"

    def test_without_changes(self):
        l = BudgetAuditLog(entity_type="budget_version", entity_id=1,
                           action="lock", actor="admin")
        assert l.changes is None


class TestEnums:
    def test_budget_type_values(self):
        assert BudgetType.REVENUE.value == "revenue"
        assert BudgetType.EXPENSE.value == "expense"
        assert BudgetType.CAPEX.value == "capex"
        assert BudgetType.CASH_FLOW.value == "cash_flow"
        assert BudgetType.BALANCE_SHEET.value == "balance_sheet"

    def test_budget_version_status_values(self):
        assert BudgetVersionStatus.DRAFT.value == "draft"
        assert BudgetVersionStatus.APPROVED.value == "approved"
        assert BudgetVersionStatus.REVISED.value == "revised"

    def test_budget_control_level_values(self):
        assert BudgetControlLevel.NONE.value == "none"
        assert BudgetControlLevel.WARNING_ONLY.value == "warning_only"
        assert BudgetControlLevel.SOFT_BLOCK.value == "soft_block"
        assert BudgetControlLevel.HARD_BLOCK.value == "hard_block"

    def test_adjustment_type_values(self):
        assert AdjustmentType.VIREMENT.value == "virement"
        assert AdjustmentType.SUPPLEMENTARY.value == "supplementary"
        assert AdjustmentType.EMERGENCY.value == "emergency"
        assert AdjustmentType.REDUCTION.value == "reduction"
