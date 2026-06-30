from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from pydantic import ValidationError as PydanticValidationError

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
from domain.common import VASValidationError, AccountError


# ── CostCenter Tests ───────────────────────────────────────────────

class TestCostCenter:
    def test_valid_cost_center_all_fields(self):
        cc = CostCenter(
            code="PROD_A", name="Phan xuong A", name_en="Workshop A",
            cost_center_type=CostCenterType.production,
            level=2, path="CTY/PROD_A",
            manager_employee_id=1001,
            gl_account_code="627", department_code="DEPT01",
            is_cost_collector=True, is_active=True,
        )
        assert cc.code == "PROD_A"
        assert cc.cost_center_type == CostCenterType.production
        assert cc.level == 2
        assert cc.is_cost_collector is True

    def test_valid_cost_center_minimal(self):
        cc = CostCenter(code="ADMIN", name="Admin")
        assert cc.cost_center_type == CostCenterType.cost
        assert cc.level == 1
        assert cc.is_active is True
        assert cc.parent_id is None

    def test_code_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            CostCenter(code="", name="Test")

    def test_code_uppercase_accepted(self):
        cc = CostCenter(code="TEST_CODE", name="Test")
        assert cc.code == "TEST_CODE"

    def test_code_reject_lowercase(self):
        with pytest.raises(PydanticValidationError):
            CostCenter(code="prod_a", name="Test")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            CostCenter(code="TEST", name="")

    def test_name_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            CostCenter(code="TEST", name="N" * 201)

    def test_level_valid_range(self):
        CostCenter(code="L1", name="Test", level=1)
        CostCenter(code="L10", name="Test", level=10)
        with pytest.raises(PydanticValidationError):
            CostCenter(code="L0", name="Test", level=0)
        with pytest.raises(PydanticValidationError):
            CostCenter(code="L11", name="Test", level=11)

    def test_valid_to_before_valid_from_raises(self):
        with pytest.raises(VASValidationError):
            CostCenter(
                code="TEST", name="Test",
                valid_from=date(2026, 6, 30),
                valid_to=date(2026, 1, 1),
            )

    def test_valid_to_after_valid_from_ok(self):
        cc = CostCenter(
            code="TEST", name="Test",
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
        )
        assert cc.valid_to == date(2026, 12, 31)

    def test_default_cost_collector(self):
        cc = CostCenter(code="DEF", name="Default")
        assert cc.is_cost_collector is True

    def test_gl_account_code_optional(self):
        cc = CostCenter(code="TEST", name="Test")
        assert cc.gl_account_code is None

    def test_path_default_empty(self):
        cc = CostCenter(code="TEST", name="Test")
        assert cc.path == ""

    def test_cost_center_type_default(self):
        cc = CostCenter(code="TEST", name="Test")
        assert cc.cost_center_type == CostCenterType.cost

    def test_created_at_none_by_default(self):
        cc = CostCenter(code="TEST", name="Test")
        assert cc.created_at is None


class TestCostCenterCreate:
    def test_valid_create(self):
        c = CostCenterCreate(code="PROD_B", name="Phan xuong B")
        assert c.code == "PROD_B"
        assert c.is_active is True

    def test_requires_code_name(self):
        with pytest.raises(PydanticValidationError):
            CostCenterCreate(code="", name="Test")
        with pytest.raises(AccountError):
            CostCenterCreate(code="TEST", name="")


class TestCostCenterUpdate:
    def test_valid_update(self):
        u = CostCenterUpdate(name="Updated Name", is_active=False)
        assert u.name == "Updated Name"
        assert u.is_active is False

    def test_empty_update(self):
        u = CostCenterUpdate()
        assert u.name is None


# ── CostDriver Tests ───────────────────────────────────────────────

class TestCostDriver:
    def test_valid_driver_all_fields(self):
        d = CostDriver(
            code="HEADCOUNT", name="So luong nhan vien",
            driver_type=DriverType.quantity,
            source_module="HR", source_account_code="6421",
            unit_of_measure="nguoi", formula="HR.HEADCOUNT",
        )
        assert d.code == "HEADCOUNT"
        assert d.driver_type == DriverType.quantity
        assert d.is_active is True

    def test_valid_driver_minimal(self):
        d = CostDriver(code="AREA", name="Dien tich", driver_type=DriverType.quantity)
        assert d.source_module is None
        assert d.formula is None

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            CostDriver(code="", name="Test", driver_type=DriverType.quantity)

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            CostDriver(code="TEST", name="", driver_type=DriverType.quantity)

    def test_driver_type_default_active(self):
        d = CostDriver(code="TEST", name="Test", driver_type=DriverType.percentage)
        assert d.is_active is True

    def test_created_at_none(self):
        d = CostDriver(code="TEST", name="Test", driver_type=DriverType.actual)
        assert d.created_at is None


class TestCostDriverCreate:
    def test_valid_create(self):
        c = CostDriverCreate(code="KWH", name="Dien nang tieu thu", driver_type=DriverType.rate)
        assert c.is_active is True


# ── Allocation Rule Tests ──────────────────────────────────────────

class TestCostAllocationRuleTarget:
    def test_valid_target(self):
        t = CostAllocationRuleTarget(target_cost_center_id=10, percentage=Decimal("50"))
        assert t.target_cost_center_id == 10
        assert t.percentage == Decimal("50")
        assert t.id is None

    def test_target_no_percentage(self):
        t = CostAllocationRuleTarget(target_cost_center_id=20)
        assert t.percentage is None


class TestCostAllocationRule:
    def test_valid_rule_all_fields(self):
        r = CostAllocationRule(
            rule_code="OH-RENT", rule_name="Phan bo tien thue",
            source_cost_center_id=1, driver_id=1,
            allocation_method=AllocationMethod.percentage,
            targets=[CostAllocationRuleTarget(target_cost_center_id=2, percentage=Decimal("60")),
                     CostAllocationRuleTarget(target_cost_center_id=3, percentage=Decimal("40"))],
            gl_debit_account_code="627", gl_credit_account_code="642",
            priority_order=1,
            effective_from=date(2026, 1, 1),
            approval_status=RuleApprovalStatus.draft,
            created_by="admin",
        )
        assert r.rule_code == "OH-RENT"
        assert r.approval_status == RuleApprovalStatus.draft
        assert len(r.targets) == 2

    def test_valid_rule_minimal(self):
        r = CostAllocationRule(
            rule_code="DIRECT", rule_name="Phan bo truc tiep",
            source_cost_center_id=1, driver_id=1,
            allocation_method=AllocationMethod.direct,
            targets=[CostAllocationRuleTarget(target_cost_center_id=2)],
            gl_debit_account_code="627", gl_credit_account_code="642",
            effective_from=date(2026, 1, 1),
            created_by="admin",
        )
        assert r.allocation_method == AllocationMethod.direct
        assert r.priority_order == 0

    def test_rules_code_empty_raises(self):
        with pytest.raises(AccountError):
            CostAllocationRule(
                rule_code="", rule_name="Test",
                source_cost_center_id=1, driver_id=1,
                allocation_method=AllocationMethod.direct,
                targets=[],
                gl_debit_account_code="627", gl_credit_account_code="642",
                effective_from=date(2026, 1, 1),
                created_by="admin",
            )

    def test_rule_name_empty_raises(self):
        with pytest.raises(AccountError):
            CostAllocationRule(
                rule_code="TEST", rule_name="",
                source_cost_center_id=1, driver_id=1,
                allocation_method=AllocationMethod.direct,
                targets=[],
                gl_debit_account_code="627", gl_credit_account_code="642",
                effective_from=date(2026, 1, 1),
                created_by="admin",
            )

    def test_default_status_draft(self):
        r = CostAllocationRule(
            rule_code="TEST", rule_name="Test",
            source_cost_center_id=1, driver_id=1,
            allocation_method=AllocationMethod.direct,
            targets=[],
            gl_debit_account_code="627", gl_credit_account_code="642",
            effective_from=date(2026, 1, 1),
            created_by="admin",
        )
        assert r.approval_status == RuleApprovalStatus.draft

    def test_targets_default_empty(self):
        r = CostAllocationRule(
            rule_code="TEST", rule_name="Test",
            source_cost_center_id=1, driver_id=1,
            allocation_method=AllocationMethod.direct,
            gl_debit_account_code="627", gl_credit_account_code="642",
            effective_from=date(2026, 1, 1),
            created_by="admin",
        )
        assert r.targets == []


class TestCostAllocationRuleCreate:
    def test_valid_create(self):
        c = CostAllocationRuleCreate(
            rule_code="NEW-RULE", rule_name="New Rule",
            source_cost_center_id=1, driver_id=1,
            allocation_method=AllocationMethod.proportional,
            targets=[CostAllocationRuleTarget(target_cost_center_id=2)],
            gl_debit_account_code="627", gl_credit_account_code="642",
            effective_from=date(2026, 1, 1),
            created_by="admin",
        )
        assert c.rule_code == "NEW-RULE"


class TestCostAllocationRuleUpdate:
    def test_valid_update(self):
        u = CostAllocationRuleUpdate(rule_name="Updated", notes="Changed")
        assert u.rule_name == "Updated"

    def test_empty_update(self):
        u = CostAllocationRuleUpdate()
        assert u.rule_name is None


# ── Allocation Run Tests ───────────────────────────────────────────

class TestCostAllocationLine:
    def test_valid_line(self):
        l = CostAllocationLine(
            source_cost_center_id=1,
            target_cost_center_id=2,
            gl_account_code="627",
            original_amount=Decimal("10000"),
            allocated_amount=Decimal("6000"),
        )
        assert l.allocated_amount == Decimal("6000")
        assert l.id is None


class TestCostAllocationRun:
    def test_valid_run(self):
        r = CostAllocationRun(
            run_code="ALLOC-202606-1234567890",
            period_key="202606",
            fiscal_year=2026, period_month=6,
            run_by="admin",
        )
        assert r.status == AllocationRunStatus.draft
        assert r.run_code == "ALLOC-202606-1234567890"

    def test_period_key_format(self):
        with pytest.raises(PydanticValidationError):
            CostAllocationRun(
                run_code="R1", period_key="2026-06",
                fiscal_year=2026, period_month=6,
                run_by="admin",
            )

    def test_period_key_valid(self):
        r = CostAllocationRun(
            run_code="R1", period_key="202612",
            fiscal_year=2026, period_month=12,
            run_by="admin",
        )
        assert r.period_key == "202612"

    def test_period_month_range(self):
        with pytest.raises(PydanticValidationError):
            CostAllocationRun(
                run_code="R1", period_key="202613",
                fiscal_year=2026, period_month=13,
                run_by="admin",
            )

    def test_default_status(self):
        r = CostAllocationRun(
            run_code="R1", period_key="202606",
            fiscal_year=2026, period_month=6,
            run_by="admin",
        )
        assert r.status == AllocationRunStatus.draft

    def test_lines_default_empty(self):
        r = CostAllocationRun(
            run_code="R1", period_key="202606",
            fiscal_year=2026, period_month=6,
            run_by="admin",
        )
        assert r.lines == []


# ── Cost Object Tests ──────────────────────────────────────────────

class TestCostObject:
    def test_valid_object_all_fields(self):
        o = CostObject(
            code="PROD-X100", name="San pham X100",
            object_type=CostObjectType.product,
            gl_account_code="155",
            external_ref_id=5001, external_ref_type="inventory",
            custom_attributes={"bom": "BOM-001"},
        )
        assert o.code == "PROD-X100"
        assert o.object_type == CostObjectType.product
        assert o.is_active is True

    def test_valid_object_minimal(self):
        o = CostObject(code="PROJ-ALPHA", name="Du an Alpha", object_type=CostObjectType.project)
        assert o.gl_account_code is None
        assert o.custom_attributes is None

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            CostObject(code="", name="Test", object_type=CostObjectType.department)

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            CostObject(code="TEST", name="", object_type=CostObjectType.customer)

    def test_code_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            CostObject(code="A" * 21, name="Test", object_type=CostObjectType.sales_order)

    def test_name_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            CostObject(code="TEST", name="N" * 201, object_type=CostObjectType.campaign)


class TestCostObjectCreate:
    def test_valid(self):
        c = CostObjectCreate(code="NEW-OBJ", name="New Object", object_type=CostObjectType.product)
        assert c.is_active is True


# ── Cost Accumulation Tests ────────────────────────────────────────

class TestCostAccumulation:
    def test_valid(self):
        a = CostAccumulation(
            cost_object_id=1, cost_center_id=2,
            gl_account_code="621", period_key="202606",
            direct_cost_amount=Decimal("5000"),
            allocated_cost_amount=Decimal("2000"),
        )
        assert a.total_cost_amount == Decimal("7000")

    def test_total_cost_property(self):
        a = CostAccumulation(
            cost_object_id=1, cost_center_id=2,
            gl_account_code="621", period_key="202606",
        )
        assert a.total_cost_amount == Decimal("0")

    def test_defaults(self):
        a = CostAccumulation(
            cost_object_id=1, cost_center_id=2,
            gl_account_code="621", period_key="202606",
        )
        assert a.direct_cost_amount == Decimal("0")
        assert a.allocated_cost_amount == Decimal("0")


# ── Budget / Actual Tests ──────────────────────────────────────────

class TestCostCenterBudget:
    def test_valid(self):
        b = CostCenterBudget(
            cost_center_id=1, fiscal_year=2026,
            period_key="202606", gl_account_code="627",
            budget_amount=Decimal("10000"),
        )
        assert b.budget_amount == Decimal("10000")
        assert b.revised_amount == Decimal("0")

    def test_defaults(self):
        b = CostCenterBudget(
            cost_center_id=1, fiscal_year=2026,
            period_key="202606", gl_account_code="627",
        )
        assert b.budget_amount == Decimal("0")


class TestCostCenterActual:
    def test_valid(self):
        a = CostCenterActual(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
            actual_amount=Decimal("8500"),
        )
        assert a.actual_amount == Decimal("8500")

    def test_defaults(self):
        a = CostCenterActual(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
        )
        assert a.commitment_amount == Decimal("0")


# ── Variance Tests ─────────────────────────────────────────────────

class TestCostCenterVariance:
    def test_valid(self):
        v = CostCenterVariance(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
            budget_amount=Decimal("10000"),
            actual_amount=Decimal("8500"),
            variance_type=VarianceType.favorable,
        )
        assert v.variance_amount == Decimal("1500")
        assert v.variance_type == VarianceType.favorable

    def test_variance_amount_property(self):
        v = CostCenterVariance(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
            budget_amount=Decimal("10000"),
            actual_amount=Decimal("12000"),
        )
        assert v.variance_amount == Decimal("-2000")

    def test_variance_amount_zero(self):
        v = CostCenterVariance(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
            budget_amount=Decimal("5000"),
            actual_amount=Decimal("5000"),
        )
        assert v.variance_amount == Decimal("0")

    def test_unfavorable(self):
        v = CostCenterVariance(
            cost_center_id=1, period_key="202606",
            gl_account_code="627",
            budget_amount=Decimal("5000"),
            actual_amount=Decimal("7000"),
            variance_type=VarianceType.unfavorable,
        )
        assert v.variance_type == VarianceType.unfavorable


# ── Audit Log Tests ────────────────────────────────────────────────

class TestCostingAuditLog:
    def test_valid(self):
        log = CostingAuditLog(
            entity_type="CostCenter",
            entity_id=123,
            action="CREATE",
            changes={"code": "PROD_A", "name": "Phan xuong A"},
            actor="admin",
            ip_address="192.168.1.1",
        )
        assert log.entity_type == "CostCenter"
        assert log.action == "CREATE"
        assert log.actor == "admin"

    def test_minimal(self):
        log = CostingAuditLog(
            entity_type="AllocationRun",
            entity_id=456,
            action="POST",
            actor="system",
        )
        assert log.ip_address is None
        assert log.changes is None


# ── Bulk Import Result Tests ───────────────────────────────────────

class TestBulkImportResult:
    def test_defaults(self):
        r = BulkImportResult()
        assert r.total_rows == 0
        assert r.success_count == 0
        assert r.error_count == 0
        assert r.errors == []

    def test_with_data(self):
        r = BulkImportResult(
            total_rows=10, success_count=8, error_count=2,
            errors=[{"row": 3, "error": "CODE_DUPLICATE"}],
        )
        assert r.success_count == 8
        assert len(r.errors) == 1


# ── Accumulation Result Tests ──────────────────────────────────────

class TestAccumulationResult:
    def test_defaults(self):
        r = AccumulationResult(period_key="202606")
        assert r.total_lines == 0
        assert r.total_direct == Decimal("0")
        assert r.total_allocated == Decimal("0")


# ── Allocation Preview Tests ───────────────────────────────────────

class TestAllocationPreview:
    def test_defaults(self):
        p = AllocationPreview(rule_id=1, rule_code="R1", source_cost_center_id=1)
        assert p.source_amount == Decimal("0")
        assert p.total_allocated == Decimal("0")
        assert p.lines == []
