from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.costing_center import (
    CostCenterType, DriverType, AllocationMethod, AllocationRunStatus,
    CostObjectType, RuleApprovalStatus,
    CostCenterCreate, CostCenterUpdate,
    CostDriverCreate,
    CostAllocationRuleTarget, CostAllocationRuleCreate,
    CostObjectCreate,
    CostAllocationLine,
)
from domain import Result, VASValidationError
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base, COAModel
from infrastructure.models.costing_center_models import (
    CostCenterModel, CostDriverModel, CostAllocationRuleModel,
    CostAllocationRuleTargetModel, CostAllocationRunModel, CostAllocationLineModel,
    CostObjectModel, CostAccumulationModel,
    CostCenterBudgetModel, CostCenterActualModel, CostCenterVarianceModel,
    CostingAuditLogModel,
)
from infrastructure.models.gl_models import AccountingPeriodModel, JournalEntryModel, JournalLineModel
from infrastructure.repositories.costing_center_repository import CostingCenterRepository
from use_cases.costing_center import CostingCenterUseCases


# ── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def repo(session):
    return CostingCenterRepository(session)


@pytest.fixture
def uc(session):
    return CostingCenterUseCases(session)


@pytest.fixture
def coa_accounts(session):
    codes = ["621", "622", "623", "627", "641", "642", "6421", "6422", "2141", "911"]
    for code in codes:
        m = COAModel(
            code=code, name=f"Account {code}",
            account_type="expense" if code.startswith(("6", "8")) else "asset",
            drcr_direction="debit" if code.startswith(("1", "2", "6")) else "credit",
            level=1,
        )
        session.add(m)
    session.flush()


@pytest.fixture
def accounting_period(session):
    p = AccountingPeriodModel(
        period="2026-06",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 30),
        is_closed=False,
        is_current=True,
    )
    session.add(p)
    session.flush()
    return p


def _make_cost_center_data(code="CC-PROD", name="Production", cc_type="production", **kw) -> dict:
    data = {
        "code": code, "name": name,
        "cost_center_type": cc_type,
        "is_cost_collector": True,
    }
    data.update(kw)
    return data


def _make_driver_data(code="HEADCOUNT", name="Headcount", driver_type="quantity", **kw) -> dict:
    data = {"code": code, "name": name, "driver_type": driver_type}
    data.update(kw)
    return data


# ── UC-CC-01: Cost Center Hierarchy ────────────────────────────────

class TestCostCenterCRUD:
    def test_create_cost_center(self, uc, session, coa_accounts):
        result = uc.create_cost_center(_make_cost_center_data())
        assert result.is_success()
        cc = result.get_data()
        assert cc.code == "CC-PROD"
        assert cc.name == "Production"
        assert cc.level == 1
        assert cc.path == "CC-PROD"

    def test_create_with_parent(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data(code="CTY", name="Company"))
        assert r1.is_success()
        parent = r1.get_data()
        r2 = uc.create_cost_center(_make_cost_center_data(code="PROD", name="Production", parent_id=parent.id))
        assert r2.is_success()
        child = r2.get_data()
        assert child.level == 2
        assert child.path == "CTY/PROD"

    def test_create_duplicate_code_fails(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="DUP", name="First"))
        result = uc.create_cost_center(_make_cost_center_data(code="DUP", name="Second"))
        assert result.is_failure()

    def test_get_cost_center(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data())
        cc_id = r1.get_data().id
        r2 = uc.get_cost_center(cc_id)
        assert r2.is_success()
        assert r2.get_data().code == "CC-PROD"

    def test_get_nonexistent_fails(self, uc):
        result = uc.get_cost_center(9999)
        assert result.is_failure()

    def test_update_cost_center(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data())
        cc_id = r1.get_data().id
        r2 = uc.update_cost_center(cc_id, {"name": "Updated Production"})
        assert r2.is_success()
        assert r2.get_data().name == "Updated Production"

    def test_deactivate_cost_center(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data())
        cc_id = r1.get_data().id
        r2 = uc.deactivate_cost_center(cc_id)
        assert r2.is_success()
        cc = uc.get_cost_center(cc_id).get_data()
        assert cc.is_active is False

    def test_move_cost_center(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data(code="CTY", name="Company"))
        r2 = uc.create_cost_center(_make_cost_center_data(code="DEPT1", name="Dept 1"))
        parent = r1.get_data()
        child = r2.get_data()
        r3 = uc.move_cost_center(child.id, parent.id)
        assert r3.is_success()
        moved = r3.get_data()
        assert moved.parent_id == parent.id
        assert moved.level == 2

    def test_move_circular_ref_fails(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data(code="A", name="A"))
        a = r1.get_data()
        r2 = uc.create_cost_center(_make_cost_center_data(code="B", name="B", parent_id=a.id))
        b = r2.get_data()
        result = uc.move_cost_center(a.id, b.id)
        assert result.is_failure()

    def test_list_cost_centers(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="CC1", name="CC 1"))
        uc.create_cost_center(_make_cost_center_data(code="CC2", name="CC 2"))
        result = uc.list_cost_centers()
        assert result.is_success()
        ccs = result.get_data()
        assert len(ccs) == 2

    def test_tree(self, uc, session, coa_accounts):
        r1 = uc.create_cost_center(_make_cost_center_data(code="ROOT", name="Root"))
        root = r1.get_data()
        uc.create_cost_center(_make_cost_center_data(code="CHILD", name="Child", parent_id=root.id))
        result = uc.get_cost_center_tree()
        assert result.is_success()
        tree = result.get_data()
        assert len(tree) == 1
        assert tree[0]["code"] == "ROOT"

    def test_bulk_import(self, uc, session, coa_accounts):
        rows = [
            {"code": "IMP1", "name": "Import 1", "type": "cost"},
            {"code": "IMP2", "name": "Import 2", "type": "cost"},
        ]
        result = uc.bulk_import_cost_centers(rows)
        assert result.is_success()
        br = result.get_data()
        assert br.success_count == 2

    def test_export_cost_centers(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="EXP1", name="Export 1"))
        result = uc.export_cost_centers()
        assert result.is_success()
        rows = result.get_data()
        assert len(rows) == 1
        assert rows[0]["code"] == "EXP1"

    def test_cost_center_max_depth(self, uc, session, coa_accounts):
        r = None
        for i in range(11):
            data = _make_cost_center_data(code=f"L{i}", name=f"Level {i}")
            if r:
                data["parent_id"] = r.get_data().id
            r = uc.create_cost_center(data)
            if i >= 10:
                assert r.is_failure()
            else:
                assert r.is_success()


# ── UC-CC-02: Cost Driver Management ───────────────────────────────

class TestDriverCRUD:
    def test_create_driver(self, uc, session, coa_accounts):
        result = uc.create_driver(_make_driver_data())
        assert result.is_success()
        d = result.get_data()
        assert d.code == "HEADCOUNT"
        assert d.driver_type == DriverType.quantity

    def test_create_duplicate_fails(self, uc, session, coa_accounts):
        uc.create_driver(_make_driver_data(code="DUP"))
        result = uc.create_driver(_make_driver_data(code="DUP"))
        assert result.is_failure()

    def test_get_driver(self, uc, session, coa_accounts):
        r1 = uc.create_driver(_make_driver_data())
        d_id = r1.get_data().id
        r2 = uc.get_driver(d_id)
        assert r2.is_success()
        assert r2.get_data().code == "HEADCOUNT"

    def test_get_nonexistent_fails(self, uc):
        result = uc.get_driver(9999)
        assert result.is_failure()

    def test_update_driver(self, uc, session, coa_accounts):
        r1 = uc.create_driver(_make_driver_data())
        d_id = r1.get_data().id
        r2 = uc.update_driver(d_id, {"name": "Updated Driver", "driver_type": "percentage"})
        assert r2.is_success()
        assert r2.get_data().driver_type == DriverType.percentage

    def test_delete_driver(self, uc, session, coa_accounts):
        r1 = uc.create_driver(_make_driver_data())
        d_id = r1.get_data().id
        r2 = uc.delete_driver(d_id)
        assert r2.is_success()
        r3 = uc.get_driver(d_id)
        assert r3.is_failure()

    def test_list_drivers(self, uc, session, coa_accounts):
        uc.create_driver(_make_driver_data(code="D1", name="Driver 1"))
        uc.create_driver(_make_driver_data(code="D2", name="Driver 2"))
        result = uc.list_drivers()
        assert len(result.get_data()) == 2


# ── UC-CC-03: Allocation Rules ─────────────────────────────────────

class TestAllocationRules:
    def _setup(self, uc):
        p = uc.create_cost_center(_make_cost_center_data(code="SRC", name="Source"))
        src = p.get_data()
        t = uc.create_cost_center(_make_cost_center_data(code="TGT", name="Target"))
        tgt = t.get_data()
        d = uc.create_driver(_make_driver_data())
        drv = d.get_data()
        return src, tgt, drv

    def test_create_rule(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        result = uc.create_rule({
            "rule_code": "R1", "rule_name": "Rule 1",
            "source_cost_center_id": src.id,
            "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627",
            "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(),
            "created_by": "admin",
        })
        assert result.is_success()
        rule = result.get_data()
        assert rule.rule_code == "R1"
        assert rule.approval_status == RuleApprovalStatus.draft

    def test_create_rule_percentage_total_not_100_fails(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        result = uc.create_rule({
            "rule_code": "R2", "rule_name": "Rule 2",
            "source_cost_center_id": src.id,
            "driver_id": drv.id,
            "allocation_method": "percentage",
            "targets": [{"target_cost_center_id": tgt.id, "percentage": "50"}],
            "gl_debit_account_code": "627",
            "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(),
            "created_by": "admin",
        })
        assert result.is_failure()

    def test_get_rule(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        data = {
            "rule_code": "GET-R", "rule_name": "Get Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }
        r1 = uc.create_rule(data)
        r_id = r1.get_data().id
        r2 = uc.get_rule(r_id)
        assert r2.is_success()

    def test_approve_rule(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        data = {
            "rule_code": "APP-R", "rule_name": "Approve Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }
        r1 = uc.create_rule(data)
        r_id = r1.get_data().id
        r2 = uc.approve_rule(r_id, approved_by="manager")
        assert r2.is_success()
        assert r2.get_data().approval_status == RuleApprovalStatus.approved

    def test_archive_rule(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        data = {
            "rule_code": "ARC-R", "rule_name": "Archive Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }
        r1 = uc.create_rule(data)
        r_id = r1.get_data().id
        result = uc.archive_rule(r_id)
        assert result.is_success()

    def test_list_rules(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        data = {
            "rule_code": "LST-R", "rule_name": "List Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }
        uc.create_rule(data)
        result = uc.list_rules()
        assert result.is_success()
        assert len(result.get_data()) == 1

    def test_get_allocation_preview(self, uc, session, coa_accounts):
        src, tgt, drv = self._setup(uc)
        data = {
            "rule_code": "PREV-R", "rule_name": "Preview Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }
        r1 = uc.create_rule(data)
        r_id = r1.get_data().id
        uc.approve_rule(r_id, "admin")
        result = uc.get_allocation_preview(r_id, "202606")
        assert result.is_success()


# ── UC-CC-04: Allocation Execution ─────────────────────────────────

class TestAllocationExecution:
    def test_execute_allocation_dry_run(self, uc, session, coa_accounts, accounting_period):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC", name="Source")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT", name="Target")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r1 = uc.create_rule({
            "rule_code": "EXEC-R", "rule_name": "Exec Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        uc.approve_rule(r1.id, "admin")
        result = uc.execute_allocation("202606", "admin", dry_run=True)
        assert result.is_success()

    def test_execute_allocation_no_rules(self, uc, session, accounting_period):
        result = uc.execute_allocation("202606", "admin")
        assert result.is_failure()

    def test_execute_allocation_closed_period(self, uc, session, coa_accounts):
        p = AccountingPeriodModel(period="2026-05", is_closed=True)
        session.add(p)
        session.flush()
        result = uc.execute_allocation("202605", "admin")
        assert result.is_failure()

    def test_post_allocation_run(self, uc, session, coa_accounts, accounting_period):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC", name="Source", gl_account_code="642")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT", name="Target")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r1 = uc.create_rule({
            "rule_code": "POST-R", "rule_name": "Post Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        uc.approve_rule(r1.id, "admin")
        run = uc.execute_allocation("202606", "admin").get_data()
        result = uc.post_allocation_run(run.id, "admin")
        assert result.is_success()

    def test_get_allocation_run(self, uc, session, coa_accounts, accounting_period):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC", name="Source")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT", name="Target")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r1 = uc.create_rule({
            "rule_code": "GET-R", "rule_name": "Get Run",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        uc.approve_rule(r1.id, "admin")
        run = uc.execute_allocation("202606", "admin").get_data()
        r2 = uc.get_allocation_run(run.id)
        assert r2.is_success()

    def test_list_allocation_runs(self, uc, session, coa_accounts, accounting_period):
        result = uc.list_allocation_runs()
        assert result.is_success()

    def test_reverse_allocation_run(self, uc, session, coa_accounts, accounting_period):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC", name="Source", gl_account_code="642")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT", name="Target")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r1 = uc.create_rule({
            "rule_code": "REV-R", "rule_name": "Rev Rule",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        uc.approve_rule(r1.id, "admin")
        run = uc.execute_allocation("202606", "admin").get_data()
        uc.post_allocation_run(run.id, "admin")
        result = uc.reverse_allocation_run(run.id, "admin")
        assert result.is_success()
        reversed_run = result.get_data()
        assert reversed_run.status == AllocationRunStatus.reversed


# ── UC-CC-05: Cost Object Management ───────────────────────────────

class TestCostObjectCRUD:
    def test_create_cost_object(self, uc, session, coa_accounts):
        result = uc.create_cost_object({
            "code": "OBJ-001", "name": "Object 1",
            "object_type": "product",
        })
        assert result.is_success()
        o = result.get_data()
        assert o.code == "OBJ-001"
        assert o.object_type == CostObjectType.product

    def test_create_duplicate_fails(self, uc, session, coa_accounts):
        uc.create_cost_object({"code": "DUP", "name": "First", "object_type": "project"})
        result = uc.create_cost_object({"code": "DUP", "name": "Second", "object_type": "project"})
        assert result.is_failure()

    def test_get_cost_object(self, uc, session, coa_accounts):
        r1 = uc.create_cost_object({"code": "GET", "name": "Get Obj", "object_type": "department"})
        o_id = r1.get_data().id
        r2 = uc.get_cost_object(o_id)
        assert r2.is_success()

    def test_update_cost_object(self, uc, session, coa_accounts):
        r1 = uc.create_cost_object({"code": "UPD", "name": "Update Obj", "object_type": "customer"})
        o_id = r1.get_data().id
        r2 = uc.update_cost_object(o_id, {"name": "Updated", "object_type": "customer"})
        assert r2.is_success()
        assert r2.get_data().name == "Updated"

    def test_delete_cost_object(self, uc, session, coa_accounts):
        r1 = uc.create_cost_object({"code": "DEL", "name": "Delete Obj", "object_type": "campaign"})
        o_id = r1.get_data().id
        result = uc.delete_cost_object(o_id)
        assert result.is_success()

    def test_list_cost_objects(self, uc, session, coa_accounts):
        uc.create_cost_object({"code": "O1", "name": "O1", "object_type": "product"})
        uc.create_cost_object({"code": "O2", "name": "O2", "object_type": "project"})
        result = uc.list_cost_objects()
        assert len(result.get_data()) == 2

    def test_export_cost_objects(self, uc, session, coa_accounts):
        uc.create_cost_object({"code": "EXP", "name": "Export", "object_type": "product"})
        result = uc.export_cost_objects()
        assert result.is_success()
        assert len(result.get_data()) == 1


# ── UC-CC-06: Cost Accumulation ────────────────────────────────────

class TestCostAccumulation:
    def test_accumulate_costs_empty(self, uc, session, coa_accounts, accounting_period):
        result = uc.accumulate_costs("202606")
        assert result.is_success()
        acc = result.get_data()
        assert acc.total_lines == 0

    def test_get_accumulated_costs_empty(self, uc, session, coa_accounts):
        result = uc.get_accumulated_costs(1, "202606")
        assert result.is_success()
        assert result.get_data() == []

    def test_accumulate_with_cost_center_data(self, uc, session, coa_accounts, accounting_period):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        obj = uc.create_cost_object({"code": "ACC-OBJ", "name": "Acc Obj", "object_type": "product"}).get_data()
        je = JournalEntryModel(
            journal_number="TEST-001",
            transaction_date=date(2026, 6, 15),
            description="Test entry",
            period="2026-06",
            is_posted=True,
            posted_date=datetime.now(timezone.utc),
            created_by="test",
        )
        session.add(je)
        session.flush()
        jl = JournalLineModel(
            journal_entry_id=je.id, account_id="621",
            debit=Decimal("5000"), credit=Decimal("0"),
            period="2026-06",
        )
        jl.cost_center_id = cc.id
        jl.cost_object_id = obj.id
        session.add(jl)
        session.flush()

        result = uc.accumulate_costs("202606")
        assert result.is_success()


# ── UC-CC-07: Budget Integration ───────────────────────────────────

class TestBudgetIntegration:
    def test_sync_budget(self, uc, session, coa_accounts):
        result = uc.sync_budget("202606")
        assert result.is_success()
        assert result.get_data()["lines_synced"] == 0

    def test_get_budget_empty(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        result = uc.get_budget(cc.id, "202606")
        assert result.is_success()
        assert result.get_data() == []


# ── UC-CC-08: Variance Analysis ────────────────────────────────────

class TestVarianceAnalysis:
    def test_compute_variance_empty(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        result = uc.compute_variance(cc.id, "202606")
        assert result.is_success()
        assert result.get_data() == []

    def test_get_cc_pl_empty(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        result = uc.get_cc_pl(cc.id, "202606")
        assert result.is_success()

    def test_get_cc_pl_nonexistent_cc(self, uc):
        result = uc.get_cc_pl(9999, "202606")
        assert result.is_failure()


# ── UC-CC-09: GL Integration ───────────────────────────────────────

class TestGLIntegration:
    def test_validate_cost_center_active(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        result = uc.validate_cost_center_for_je(cc.id, "627")
        assert result.is_success()

    def test_validate_cost_center_inactive(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        uc.deactivate_cost_center(cc.id)
        result = uc.validate_cost_center_for_je(cc.id, "627")
        assert result.is_failure()

    def test_validate_cost_center_nonexistent(self, uc):
        result = uc.validate_cost_center_for_je(9999, "627")
        assert result.is_failure()


# ── UC-CC-10: Cost Center P&L Report ───────────────────────────────

class TestCCPLReport:
    def test_report_cc_pl(self, uc, session, coa_accounts):
        cc = uc.create_cost_center(_make_cost_center_data()).get_data()
        result = uc.report_cc_pl(cc.id, "202606")
        assert result.is_success()

    def test_report_cc_pl_with_children(self, uc, session, coa_accounts):
        parent = uc.create_cost_center(_make_cost_center_data(code="PARENT", name="Parent")).get_data()
        child = uc.create_cost_center(_make_cost_center_data(code="CHILD", name="Child", parent_id=parent.id)).get_data()
        result = uc.report_cc_pl(parent.id, "202606", include_children=True)
        assert result.is_success()


# ── UC-CC-11: Allocation Summary Report ────────────────────────────

class TestAllocationReport:
    def test_allocation_summary(self, uc, session, coa_accounts, accounting_period):
        result = uc.report_allocation_summary("202606")
        assert result.is_success()
        report = result.get_data()
        assert report["period_key"] == "202606"

    def test_allocation_matrix(self, uc, session, coa_accounts, accounting_period):
        result = uc.get_allocation_matrix("202606")
        assert result.is_success()


# ── UC-CC-12: Import/Export ────────────────────────────────────────

class TestImportExport:
    def test_export_cost_centers_empty(self, uc):
        result = uc.export_cost_centers()
        assert result.is_success()
        assert result.get_data() == []

    def test_export_cost_objects_empty(self, uc):
        result = uc.export_cost_objects()
        assert result.is_success()
        assert result.get_data() == []


# ── UC-CC-13: Audit Trail ──────────────────────────────────────────

class TestAuditTrail:
    def test_get_audit_logs(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="AUDIT", name="Audit CC"))
        result = uc.get_audit_logs()
        assert result.is_success()
        logs = result.get_data()
        audit_events = [l for l in logs if l["entity_type"] == "CostCenter"]
        assert len(audit_events) >= 1

    def test_get_audit_logs_filtered(self, uc, session, coa_accounts):
        result = uc.get_audit_logs(entity_type="CostCenter")
        assert result.is_success()


# ── UC-CC-14: Dashboard & KPIs ─────────────────────────────────────

class TestDashboard:
    def test_dashboard_summary_empty(self, uc):
        result = uc.dashboard_summary()
        assert result.is_success()
        data = result.get_data()
        assert data["total_cost_centers"] == 0

    def test_dashboard_summary_with_data(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="D1", name="D1"))
        uc.create_cost_center(_make_cost_center_data(code="D2", name="D2"))
        result = uc.dashboard_summary()
        assert result.is_success()
        data = result.get_data()
        assert data["total_cost_centers"] == 2
        assert data["rule_coverage_pct"] == 0


# ── UC-CC-15: Self-Service ─────────────────────────────────────────

class TestSelfService:
    def test_get_manager_cost_centers(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="MGR1", name="Mgr 1", manager_employee_id=101))
        uc.create_cost_center(_make_cost_center_data(code="MGR2", name="Mgr 2", manager_employee_id=102))
        result = uc.get_manager_cost_centers(101)
        assert result.is_success()
        assert len(result.get_data()) == 1

    def test_get_manager_dashboard(self, uc, session, coa_accounts):
        uc.create_cost_center(_make_cost_center_data(code="DASH", name="Dashboard", manager_employee_id=201,
                                                      gl_account_code="642"))
        result = uc.get_manager_dashboard(201, "202606")
        assert result.is_success()
        data = result.get_data()
        assert data["managed_cost_centers"] == 1


# ── Edge Cases ─────────────────────────────────────────────────────

class TestEdgeCases:
    def test_get_nonexistent_rule(self, uc):
        result = uc.get_rule(9999)
        assert result.is_failure()

    def test_get_nonexistent_run(self, uc):
        result = uc.get_allocation_run(9999)
        assert result.is_failure()

    def test_empty_list_cost_centers(self, uc):
        result = uc.list_cost_centers()
        assert result.is_success()
        assert result.get_data() == []

    def test_empty_list_drivers(self, uc):
        result = uc.list_drivers()
        assert result.is_success()
        assert result.get_data() == []

    def test_empty_list_rules(self, uc):
        result = uc.list_rules()
        assert result.is_success()
        assert result.get_data() == []

    def test_approve_nonexistent_rule(self, uc):
        result = uc.approve_rule(9999, "admin")
        assert result.is_failure()

    def test_archive_nonexistent_rule(self, uc):
        result = uc.archive_rule(9999)
        assert result.is_failure()

    def test_delete_nonexistent_driver(self, uc):
        result = uc.delete_driver(9999)
        assert result.is_failure()

    def test_update_nonexistent_cost_center(self, uc):
        result = uc.update_cost_center(9999, {"name": "Test"})
        assert result.is_failure()

    def test_update_nonexistent_driver(self, uc):
        result = uc.update_driver(9999, {"code": "T", "name": "Test", "driver_type": "quantity"})
        assert result.is_failure()

    def test_deactivate_nonexistent_cc(self, uc):
        result = uc.deactivate_cost_center(9999)
        assert result.is_failure()

    def test_move_nonexistent_cc(self, uc):
        result = uc.move_cost_center(9999, 1)
        assert result.is_failure()

    def test_compute_variance_nonexistent(self, uc):
        result = uc.compute_variance(9999, "202606")
        assert result.is_failure()

    def test_get_budget_nonexistent(self, uc):
        result = uc.get_budget(9999, "202606")
        assert result.is_failure()

    def test_preview_nonexistent_rule(self, uc):
        result = uc.get_allocation_preview(9999, "202606")
        assert result.is_failure()

    def test_preview_unapproved_rule(self, uc, session, coa_accounts):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC", name="S")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT", name="T")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r = uc.create_rule({
            "rule_code": "UNAPP", "rule_name": "Unapproved",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        result = uc.get_allocation_preview(r.id, "202606")
        assert result.is_failure()

    def test_post_closed_period(self, uc, session, coa_accounts):
        p = AccountingPeriodModel(period="2026-05", is_closed=True)
        session.add(p)
        session.flush()
        src = uc.create_cost_center(_make_cost_center_data(code="SRC2", name="S2")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT2", name="T2")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        r = uc.create_rule({
            "rule_code": "CLOSED", "rule_name": "Closed Period",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        }).get_data()
        uc.approve_rule(r.id, "admin")
        result = uc.execute_allocation("202605", "admin")
        assert result.is_failure()

    def test_reverse_nonexistent_run(self, uc):
        result = uc.reverse_allocation_run(9999, "admin")
        assert result.is_failure()

    def test_create_cost_object_missing_type(self, uc):
        result = uc.create_cost_object({"code": "NO-TYPE", "name": "No Type"})
        assert result.is_failure()

    def test_driver_in_use_delete_fails(self, uc, session, coa_accounts):
        src = uc.create_cost_center(_make_cost_center_data(code="SRC3", name="S3")).get_data()
        tgt = uc.create_cost_center(_make_cost_center_data(code="TGT3", name="T3")).get_data()
        drv = uc.create_driver(_make_driver_data()).get_data()
        uc.create_rule({
            "rule_code": "DRV-USE", "rule_name": "Driver Use",
            "source_cost_center_id": src.id, "driver_id": drv.id,
            "allocation_method": "direct",
            "targets": [{"target_cost_center_id": tgt.id}],
            "gl_debit_account_code": "627", "gl_credit_account_code": "642",
            "effective_from": date(2026, 1, 1).isoformat(), "created_by": "admin",
        })
        result = uc.delete_driver(drv.id)
        assert result.is_failure()
