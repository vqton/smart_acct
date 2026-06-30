from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import or_, and_, func, asc, desc
from sqlalchemy.orm import Session, joinedload

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
from domain.common import VASValidationError, Result
from infrastructure.models.costing_center_models import (
    CostCenterModel, CostDriverModel,
    CostAllocationRuleModel, CostAllocationRuleTargetModel,
    CostAllocationRunModel, CostAllocationLineModel,
    CostObjectModel, CostAccumulationModel,
    CostCenterBudgetModel, CostCenterActualModel, CostCenterVarianceModel,
    CostingAuditLogModel,
    CostCenterTypeDB, DriverTypeDB, AllocationMethodDB, AllocationRunStatusDB,
    CostObjectTypeDB, VarianceTypeDB, RuleApprovalStatusDB,
)


def _cost_center_to_domain(m: CostCenterModel) -> CostCenter:
    return CostCenter(
        id=m.id, code=m.code, name=m.name, name_en=m.name_en,
        cost_center_type=CostCenterType(m.cost_center_type.value if hasattr(m.cost_center_type, 'value') else m.cost_center_type),
        parent_id=m.parent_id, level=m.level, path=m.path,
        manager_employee_id=m.manager_employee_id,
        gl_account_code=m.gl_account_code, department_code=m.department_code,
        is_cost_collector=m.is_cost_collector, is_active=m.is_active,
        valid_from=m.valid_from, valid_to=m.valid_to,
        created_at=m.created_at, updated_at=m.updated_at,
    )


def _driver_to_domain(m: CostDriverModel) -> CostDriver:
    return CostDriver(
        id=m.id, code=m.code, name=m.name,
        driver_type=DriverType(m.driver_type.value if hasattr(m.driver_type, 'value') else m.driver_type),
        source_module=m.source_module, source_account_code=m.source_account_code,
        unit_of_measure=m.unit_of_measure, formula=m.formula,
        is_active=m.is_active, created_at=m.created_at,
    )


def _rule_to_domain(m: CostAllocationRuleModel) -> CostAllocationRule:
    targets = []
    for t in m.targets:
        targets.append(CostAllocationRuleTarget(
            id=t.id, rule_id=t.rule_id,
            target_cost_center_id=t.target_cost_center_id,
            percentage=t.percentage, created_at=t.created_at,
        ))
    return CostAllocationRule(
        id=m.id, rule_code=m.rule_code, rule_name=m.rule_name,
        source_cost_center_id=m.source_cost_center_id,
        driver_id=m.driver_id,
        allocation_method=AllocationMethod(m.allocation_method.value if hasattr(m.allocation_method, 'value') else m.allocation_method),
        targets=targets,
        gl_debit_account_code=m.gl_debit_account_code,
        gl_credit_account_code=m.gl_credit_account_code,
        priority_order=m.priority_order,
        effective_from=m.effective_from, effective_to=m.effective_to,
        approval_status=RuleApprovalStatus(m.approval_status.value if hasattr(m.approval_status, 'value') else m.approval_status),
        approved_by=m.approved_by, approved_at=m.approved_at,
        notes=m.notes, created_by=m.created_by,
        created_at=m.created_at, updated_at=m.updated_at,
    )


def _run_to_domain(m: CostAllocationRunModel) -> CostAllocationRun:
    lines = []
    for l in m.lines:
        lines.append(CostAllocationLine(
            id=l.id, run_id=l.run_id,
            source_cost_center_id=l.source_cost_center_id,
            target_cost_center_id=l.target_cost_center_id,
            rule_id=l.rule_id, driver_id=l.driver_id,
            gl_account_code=l.gl_account_code,
            original_amount=l.original_amount, allocated_amount=l.allocated_amount,
            driver_quantity=l.driver_quantity, driver_rate=l.driver_rate,
            allocation_basis_description=l.allocation_basis_description,
        ))
    return CostAllocationRun(
        id=m.id, run_code=m.run_code,
        period_key=m.period_key, fiscal_year=m.fiscal_year,
        period_month=m.period_month, run_date=m.run_date, run_by=m.run_by,
        status=AllocationRunStatus(m.status.value if hasattr(m.status, 'value') else m.status),
        total_allocated_amount=m.total_allocated_amount,
        lines=lines, notes=m.notes, created_at=m.created_at,
    )


def _cost_object_to_domain(m: CostObjectModel) -> CostObject:
    return CostObject(
        id=m.id, code=m.code, name=m.name,
        object_type=CostObjectType(m.object_type.value if hasattr(m.object_type, 'value') else m.object_type),
        parent_object_id=m.parent_object_id,
        gl_account_code=m.gl_account_code,
        external_ref_id=m.external_ref_id, external_ref_type=m.external_ref_type,
        is_active=m.is_active,
        custom_attributes=m.custom_attributes, created_at=m.created_at,
    )


class CostingCenterRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Cost Center CRUD ───────────────────────────────────────────────

    def get_cost_center(self, id: int) -> Optional[CostCenter]:
        m = self.session.query(CostCenterModel).get(id)
        return _cost_center_to_domain(m) if m else None

    def get_cost_center_by_code(self, code: str) -> Optional[CostCenter]:
        m = self.session.query(CostCenterModel).filter(CostCenterModel.code == code).first()
        return _cost_center_to_domain(m) if m else None

    def list_cost_centers(self, parent_id: Optional[int] = None, active_only: bool = True) -> List[CostCenter]:
        q = self.session.query(CostCenterModel)
        if parent_id is not None:
            q = q.filter(CostCenterModel.parent_id == parent_id)
        if active_only:
            q = q.filter(CostCenterModel.is_active == True)
        return [_cost_center_to_domain(m) for m in q.order_by(CostCenterModel.code).all()]

    def get_cost_center_tree(self, root_id: Optional[int] = None) -> List[Dict]:
        q = self.session.query(CostCenterModel)
        if root_id:
            root = self.session.query(CostCenterModel).get(root_id)
            if not root:
                return []
            q = q.filter(CostCenterModel.path.like(f"{root.path}%"))
        nodes = q.order_by(CostCenterModel.path, CostCenterModel.code).all()

        tree = []
        node_map: Dict[int, Dict] = {}
        for n in nodes:
            d = {
                "id": n.id, "code": n.code, "name": n.name,
                "type": n.cost_center_type.value if hasattr(n.cost_center_type, 'value') else n.cost_center_type,
                "parent_id": n.parent_id, "level": n.level, "path": n.path,
                "is_active": n.is_active, "children": [],
            }
            node_map[n.id] = d
            if n.parent_id is None:
                tree.append(d)
            elif n.parent_id in node_map:
                node_map[n.parent_id]["children"].append(d)
        return tree

    def create_cost_center(self, data: CostCenterCreate) -> CostCenter:
        parent_id = data.parent_id
        level = 1
        path = data.code
        if parent_id:
            parent = self.session.query(CostCenterModel).get(parent_id)
            if not parent:
                raise VASValidationError("COST_CENTER_NOT_FOUND")
            level = parent.level + 1
            if level > 10:
                raise VASValidationError("COST_CENTER_MAX_DEPTH")
            path = f"{parent.path}/{data.code}"
        existing = self.session.query(CostCenterModel).filter(
            CostCenterModel.code == data.code,
            CostCenterModel.parent_id == parent_id,
        ).first()
        if existing:
            raise VASValidationError("COST_CENTER_CODE_DUPLICATE")

        m = CostCenterModel(
            code=data.code, name=data.name, name_en=data.name_en,
            cost_center_type=CostCenterTypeDB[data.cost_center_type.value.upper()],
            parent_id=parent_id, level=level, path=path,
            manager_employee_id=data.manager_employee_id,
            gl_account_code=data.gl_account_code,
            department_code=data.department_code,
            is_cost_collector=data.is_cost_collector,
            is_active=data.is_active,
            valid_from=data.valid_from, valid_to=data.valid_to,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(m)
        self.session.flush()
        return _cost_center_to_domain(m)

    def update_cost_center(self, id: int, data: CostCenterUpdate) -> CostCenter:
        m = self.session.query(CostCenterModel).get(id)
        if not m:
            raise VASValidationError("COST_CENTER_NOT_FOUND")
        if data.name is not None:
            m.name = data.name
        if data.name_en is not None:
            m.name_en = data.name_en
        if data.cost_center_type is not None:
            m.cost_center_type = CostCenterTypeDB[data.cost_center_type.value.upper()]
        if data.manager_employee_id is not None:
            m.manager_employee_id = data.manager_employee_id
        if data.gl_account_code is not None:
            m.gl_account_code = data.gl_account_code
        if data.department_code is not None:
            m.department_code = data.department_code
        if data.is_cost_collector is not None:
            m.is_cost_collector = data.is_cost_collector
        if data.is_active is not None:
            m.is_active = data.is_active
        if data.valid_to is not None:
            m.valid_to = data.valid_to
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return _cost_center_to_domain(m)

    def deactivate_cost_center(self, id: int) -> bool:
        m = self.session.query(CostCenterModel).get(id)
        if not m:
            raise VASValidationError("COST_CENTER_NOT_FOUND")
        if self.has_active_transactions(id):
            raise VASValidationError("COST_CENTER_HAS_TRANSACTIONS")
        m.is_active = False
        m.updated_at = datetime.now(timezone.utc)
        return True

    def move_cost_center(self, id: int, new_parent_id: int) -> CostCenter:
        node = self.session.query(CostCenterModel).get(id)
        if not node:
            raise VASValidationError("COST_CENTER_NOT_FOUND")
        if self._is_descendant(new_parent_id, id):
            raise VASValidationError("COST_CENTER_CIRCULAR_REF")
        new_parent = self.session.query(CostCenterModel).get(new_parent_id)
        if not new_parent:
            raise VASValidationError("COST_CENTER_NOT_FOUND")
        new_level = new_parent.level + 1
        if new_level > 10:
            raise VASValidationError("COST_CENTER_MAX_DEPTH")
        old_path = node.path
        node.parent_id = new_parent_id
        node.level = new_level
        node.path = f"{new_parent.path}/{node.code}"
        node.updated_at = datetime.now(timezone.utc)
        self._repath_children(node.id, old_path, node.path)
        self.session.flush()
        return _cost_center_to_domain(node)

    def _is_descendant(self, node_id: int, ancestor_id: int) -> bool:
        node = self.session.query(CostCenterModel).get(node_id)
        while node and node.parent_id:
            if node.parent_id == ancestor_id:
                return True
            node = self.session.query(CostCenterModel).get(node.parent_id)
        return False

    def _repath_children(self, parent_id: int, old_path: str, new_path: str):
        children = self.session.query(CostCenterModel).filter(CostCenterModel.parent_id == parent_id).all()
        for c in children:
            c.path = c.path.replace(old_path, new_path, 1)
            c.level = c.path.count("/") + 1
            c.updated_at = datetime.now(timezone.utc)
            self._repath_children(c.id, old_path, new_path)

    def has_active_transactions(self, cc_id: int) -> bool:
        run_count = self.session.query(CostAllocationRunModel).join(
            CostAllocationLineModel,
            CostAllocationRunModel.id == CostAllocationLineModel.run_id,
        ).filter(
            CostAllocationLineModel.source_cost_center_id == cc_id,
            CostAllocationRunModel.status != AllocationRunStatusDB.REVERSED,
        ).count()
        budget_count = self.session.query(CostCenterBudgetModel).filter(
            CostCenterBudgetModel.cost_center_id == cc_id,
        ).count()
        return (run_count + budget_count) > 0

    def bulk_import_cost_centers(self, rows: List[Dict]) -> BulkImportResult:
        errors: List[Dict] = []
        success = 0
        for i, row in enumerate(rows):
            try:
                parent_code = row.get("parent_code")
                parent_id = None
                if parent_code:
                    parent = self.session.query(CostCenterModel).filter(
                        CostCenterModel.code == parent_code
                    ).first()
                    if not parent:
                        errors.append({"row": i + 1, "error": "PARENT_NOT_FOUND"})
                        continue
                    parent_id = parent.id
                existing = self.session.query(CostCenterModel).filter(
                    CostCenterModel.code == row["code"],
                    CostCenterModel.parent_id == parent_id,
                ).first()
                if existing:
                    errors.append({"row": i + 1, "error": "CODE_DUPLICATE"})
                    continue
                data = CostCenterCreate(
                    code=row["code"], name=row["name"],
                    cost_center_type=CostCenterType(row.get("type", "cost")),
                    parent_id=parent_id,
                )
                self.create_cost_center(data)
                success += 1
            except Exception as e:
                errors.append({"row": i + 1, "error": str(e)})
        return BulkImportResult(total_rows=len(rows), success_count=success, error_count=len(errors), errors=errors)

    # ── Driver CRUD ────────────────────────────────────────────────────

    def get_driver(self, id: int) -> Optional[CostDriver]:
        m = self.session.query(CostDriverModel).get(id)
        return _driver_to_domain(m) if m else None

    def list_drivers(self, active_only: bool = True) -> List[CostDriver]:
        q = self.session.query(CostDriverModel)
        if active_only:
            q = q.filter(CostDriverModel.is_active == True)
        return [_driver_to_domain(m) for m in q.order_by(CostDriverModel.code).all()]

    def create_driver(self, data: CostDriverCreate) -> CostDriver:
        existing = self.session.query(CostDriverModel).filter(CostDriverModel.code == data.code).first()
        if existing:
            raise VASValidationError("COST_DRIVER_CODE_DUPLICATE")
        m = CostDriverModel(
            code=data.code, name=data.name,
            driver_type=DriverTypeDB[data.driver_type.value.upper()],
            source_module=data.source_module,
            source_account_code=data.source_account_code,
            unit_of_measure=data.unit_of_measure,
            formula=data.formula, is_active=data.is_active,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(m)
        self.session.flush()
        return _driver_to_domain(m)

    def update_driver(self, id: int, data: CostDriverCreate) -> CostDriver:
        m = self.session.query(CostDriverModel).get(id)
        if not m:
            raise VASValidationError("COST_DRIVER_CODE_DUPLICATE")
        m.code = data.code
        m.name = data.name
        m.driver_type = DriverTypeDB[data.driver_type.value.upper()]
        m.source_module = data.source_module
        m.source_account_code = data.source_account_code
        m.unit_of_measure = data.unit_of_measure
        m.formula = data.formula
        m.is_active = data.is_active
        self.session.flush()
        return _driver_to_domain(m)

    def delete_driver(self, id: int) -> bool:
        m = self.session.query(CostDriverModel).get(id)
        if not m:
            raise VASValidationError("COST_DRIVER_CODE_DUPLICATE")
        if self._is_driver_in_use(id):
            raise VASValidationError("COST_DRIVER_IN_USE")
        self.session.delete(m)
        return True

    def _is_driver_in_use(self, driver_id: int) -> bool:
        count = self.session.query(CostAllocationRuleModel).filter(
            CostAllocationRuleModel.driver_id == driver_id
        ).count()
        return count > 0

    def get_driver_value(self, driver_id: int, cost_center_id: int, period_key: str) -> Decimal:
        driver = self.session.query(CostDriverModel).get(driver_id)
        if not driver:
            return Decimal("0")
        if driver.source_account_code:
            from infrastructure.models.gl_models import JournalLineModel, JournalEntryModel
            gl_period = f"{period_key[:4]}-{period_key[4:]}" if len(period_key) == 6 else period_key
            result = self.session.query(
                func.sum(JournalLineModel.debit - JournalLineModel.credit)
            ).join(
                JournalEntryModel, JournalEntryModel.id == JournalLineModel.journal_entry_id
            ).filter(
                JournalLineModel.account_id == driver.source_account_code,
                JournalEntryModel.period == gl_period,
                JournalEntryModel.is_posted == True,
            ).scalar()
            return Decimal(str(result)) if result else Decimal("0")
        return Decimal("1")

    # ── Allocation Rules ───────────────────────────────────────────────

    def get_rule(self, id: int) -> Optional[CostAllocationRule]:
        m = self.session.query(CostAllocationRuleModel).options(
            joinedload(CostAllocationRuleModel.targets)
        ).get(id)
        return _rule_to_domain(m) if m else None

    def list_rules(
        self, source_cc_id: Optional[int] = None, status: Optional[str] = None,
        period_key: Optional[str] = None,
    ) -> List[CostAllocationRule]:
        q = self.session.query(CostAllocationRuleModel).options(
            joinedload(CostAllocationRuleModel.targets)
        )
        if source_cc_id is not None:
            q = q.filter(CostAllocationRuleModel.source_cost_center_id == source_cc_id)
        if status:
            q = q.filter(CostAllocationRuleModel.approval_status == RuleApprovalStatusDB[status.upper()])
        return [_rule_to_domain(m) for m in q.order_by(CostAllocationRuleModel.priority_order).all()]

    def create_rule(self, data: CostAllocationRuleCreate) -> CostAllocationRule:
        existing = self.session.query(CostAllocationRuleModel).filter(
            CostAllocationRuleModel.rule_code == data.rule_code
        ).first()
        if existing:
            raise VASValidationError("COST_RULE_NOT_FOUND")
        self._validate_rule_targets(data)
        m = CostAllocationRuleModel(
            rule_code=data.rule_code, rule_name=data.rule_name,
            source_cost_center_id=data.source_cost_center_id,
            driver_id=data.driver_id,
            allocation_method=AllocationMethodDB[data.allocation_method.value.upper()],
            gl_debit_account_code=data.gl_debit_account_code,
            gl_credit_account_code=data.gl_credit_account_code,
            priority_order=data.priority_order,
            effective_from=data.effective_from, effective_to=data.effective_to,
            approval_status=RuleApprovalStatusDB.DRAFT,
            notes=data.notes, created_by=data.created_by,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(m)
        self.session.flush()
        for t in data.targets:
            self.session.add(CostAllocationRuleTargetModel(
                rule_id=m.id, target_cost_center_id=t.target_cost_center_id,
                percentage=t.percentage, created_at=datetime.now(timezone.utc),
            ))
        self.session.flush()
        return self.get_rule(m.id)

    def update_rule(self, id: int, data: CostAllocationRuleUpdate) -> CostAllocationRule:
        m = self.session.query(CostAllocationRuleModel).options(
            joinedload(CostAllocationRuleModel.targets)
        ).get(id)
        if not m:
            raise VASValidationError("COST_RULE_NOT_FOUND")
        if data.rule_name is not None:
            m.rule_name = data.rule_name
        if data.driver_id is not None:
            m.driver_id = data.driver_id
        if data.allocation_method is not None:
            m.allocation_method = AllocationMethodDB[data.allocation_method.value.upper()]
        if data.gl_debit_account_code is not None:
            m.gl_debit_account_code = data.gl_debit_account_code
        if data.gl_credit_account_code is not None:
            m.gl_credit_account_code = data.gl_credit_account_code
        if data.priority_order is not None:
            m.priority_order = data.priority_order
        if data.effective_from is not None:
            m.effective_from = data.effective_from
        if data.effective_to is not None:
            m.effective_to = data.effective_to
        if data.notes is not None:
            m.notes = data.notes
        if data.targets is not None:
            self.session.query(CostAllocationRuleTargetModel).filter(
                CostAllocationRuleTargetModel.rule_id == id
            ).delete()
            for t in data.targets:
                self.session.add(CostAllocationRuleTargetModel(
                    rule_id=id, target_cost_center_id=t.target_cost_center_id,
                    percentage=t.percentage, created_at=datetime.now(timezone.utc),
                ))
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return self.get_rule(id)

    def approve_rule(self, id: int, approved_by: str) -> CostAllocationRule:
        m = self.session.query(CostAllocationRuleModel).get(id)
        if not m:
            raise VASValidationError("COST_RULE_NOT_FOUND")
        m.approval_status = RuleApprovalStatusDB.APPROVED
        m.approved_by = approved_by
        m.approved_at = datetime.now(timezone.utc)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return self.get_rule(id)

    def archive_rule(self, id: int) -> bool:
        m = self.session.query(CostAllocationRuleModel).get(id)
        if not m:
            raise VASValidationError("COST_RULE_NOT_FOUND")
        m.approval_status = RuleApprovalStatusDB.ARCHIVED
        m.updated_at = datetime.now(timezone.utc)
        return True

    def _validate_rule_targets(self, data: CostAllocationRuleCreate):
        if not data.targets:
            raise VASValidationError("COST_RULE_NOT_FOUND")
        if data.allocation_method == AllocationMethod.percentage:
            total = sum(t.percentage or Decimal("0") for t in data.targets)
            if total != Decimal("100"):
                raise VASValidationError("COST_ALLOCATION_TOTAL_NOT_100")
        for t in data.targets:
            if t.target_cost_center_id == data.source_cost_center_id:
                raise VASValidationError("COST_ALLOCATION_SAME_CC")

    def detect_circular_allocation(self, source_cc_id: int, target_cc_ids: List[int]) -> bool:
        for tid in target_cc_ids:
            if self._is_descendant(tid, source_cc_id):
                return True
            rules = self.session.query(CostAllocationRuleModel).filter(
                CostAllocationRuleModel.source_cost_center_id == tid,
                CostAllocationRuleModel.approval_status == RuleApprovalStatusDB.APPROVED,
            ).all()
            for r in rules:
                targets = self.session.query(CostAllocationRuleTargetModel).filter(
                    CostAllocationRuleTargetModel.rule_id == r.id
                ).all()
                for t in targets:
                    if t.target_cost_center_id == source_cc_id:
                        return True
        return False

    def get_active_rules_for_period(self, period_key: str) -> List[CostAllocationRule]:
        today = date.today()
        q = self.session.query(CostAllocationRuleModel).options(
            joinedload(CostAllocationRuleModel.targets)
        ).filter(
            CostAllocationRuleModel.approval_status == RuleApprovalStatusDB.APPROVED,
            or_(
                CostAllocationRuleModel.effective_to.is_(None),
                CostAllocationRuleModel.effective_to >= today,
            ),
            CostAllocationRuleModel.effective_from <= today,
        ).order_by(CostAllocationRuleModel.priority_order)
        return [_rule_to_domain(m) for m in q.all()]

    # ── Allocation Run ─────────────────────────────────────────────────

    def create_allocation_run(self, period_key: str, run_by: str) -> CostAllocationRun:
        year = int(period_key[:4])
        month = int(period_key[4:])
        run_code = f"ALLOC-{period_key}-{int(datetime.now().timestamp())}"
        m = CostAllocationRunModel(
            run_code=run_code, period_key=period_key,
            fiscal_year=year, period_month=month,
            run_date=datetime.now(timezone.utc), run_by=run_by,
            status=AllocationRunStatusDB.DRAFT,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(m)
        self.session.flush()
        return self.get_allocation_run(m.id)

    def get_allocation_run(self, id: int) -> Optional[CostAllocationRun]:
        m = self.session.query(CostAllocationRunModel).options(
            joinedload(CostAllocationRunModel.lines)
        ).get(id)
        return _run_to_domain(m) if m else None

    def get_allocation_run_by_period(self, period_key: str) -> Optional[CostAllocationRun]:
        m = self.session.query(CostAllocationRunModel).filter(
            CostAllocationRunModel.period_key == period_key,
            CostAllocationRunModel.status != AllocationRunStatusDB.REVERSED,
        ).options(joinedload(CostAllocationRunModel.lines)).first()
        return _run_to_domain(m) if m else None

    def list_allocation_runs(self, period_key: Optional[str] = None) -> List[CostAllocationRun]:
        q = self.session.query(CostAllocationRunModel).options(
            joinedload(CostAllocationRunModel.lines)
        )
        if period_key:
            q = q.filter(CostAllocationRunModel.period_key == period_key)
        return [_run_to_domain(m) for m in q.order_by(desc(CostAllocationRunModel.created_at)).all()]

    def _set_run_status(self, run_id: int, status: AllocationRunStatusDB) -> CostAllocationRun:
        m = self.session.query(CostAllocationRunModel).get(run_id)
        if m:
            m.status = status
        self.session.flush()
        return self.get_allocation_run(run_id)

    def save_allocation_lines(self, run_id: int, lines: List[CostAllocationLine]):
        for l in lines:
            self.session.add(CostAllocationLineModel(
                run_id=run_id,
                source_cost_center_id=l.source_cost_center_id,
                target_cost_center_id=l.target_cost_center_id,
                rule_id=l.rule_id, driver_id=l.driver_id,
                gl_account_code=l.gl_account_code,
                original_amount=l.original_amount,
                allocated_amount=l.allocated_amount,
                driver_quantity=l.driver_quantity, driver_rate=l.driver_rate,
                allocation_basis_description=l.allocation_basis_description,
            ))

    def get_allocation_lines(self, run_id: int) -> List[CostAllocationLine]:
        lines = self.session.query(CostAllocationLineModel).filter(
            CostAllocationLineModel.run_id == run_id
        ).all()
        return [
            CostAllocationLine(
                id=l.id, run_id=l.run_id,
                source_cost_center_id=l.source_cost_center_id,
                target_cost_center_id=l.target_cost_center_id,
                rule_id=l.rule_id, driver_id=l.driver_id,
                gl_account_code=l.gl_account_code,
                original_amount=l.original_amount,
                allocated_amount=l.allocated_amount,
                driver_quantity=l.driver_quantity, driver_rate=l.driver_rate,
                allocation_basis_description=l.allocation_basis_description,
            ) for l in lines
        ]

    def get_allocation_matrix(self, period_key: str) -> List[Dict]:
        lines = self.session.query(CostAllocationLineModel).join(
            CostAllocationRunModel,
            CostAllocationRunModel.id == CostAllocationLineModel.run_id,
        ).filter(
            CostAllocationRunModel.period_key == period_key,
            CostAllocationRunModel.status == AllocationRunStatusDB.POSTED,
        ).all()
        matrix: Dict[str, Dict] = {}
        for l in lines:
            sk = f"source_{l.source_cost_center_id}"
            tk = f"target_{l.target_cost_center_id}"
            if sk not in matrix:
                matrix[sk] = {"cost_center_id": l.source_cost_center_id, "targets": {}}
            if tk not in matrix[sk]["targets"]:
                matrix[sk]["targets"][tk] = {"cost_center_id": l.target_cost_center_id, "amount": Decimal("0")}
            matrix[sk]["targets"][tk]["amount"] += l.allocated_amount
        return list(matrix.values())

    # ── Cost Object ────────────────────────────────────────────────────

    def get_cost_object(self, id: int) -> Optional[CostObject]:
        m = self.session.query(CostObjectModel).get(id)
        return _cost_object_to_domain(m) if m else None

    def list_cost_objects(self, object_type: Optional[str] = None) -> List[CostObject]:
        q = self.session.query(CostObjectModel)
        if object_type:
            q = q.filter(CostObjectModel.object_type == CostObjectTypeDB[object_type.upper()])
        return [_cost_object_to_domain(m) for m in q.all()]

    def create_cost_object(self, data: CostObjectCreate) -> CostObject:
        existing = self.session.query(CostObjectModel).filter(CostObjectModel.code == data.code).first()
        if existing:
            raise VASValidationError("COST_OBJECT_CODE_DUPLICATE")
        m = CostObjectModel(
            code=data.code, name=data.name,
            object_type=CostObjectTypeDB[data.object_type.value.upper()],
            parent_object_id=data.parent_object_id,
            gl_account_code=data.gl_account_code,
            external_ref_id=data.external_ref_id,
            external_ref_type=data.external_ref_type,
            is_active=data.is_active,
            custom_attributes=data.custom_attributes,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(m)
        self.session.flush()
        return _cost_object_to_domain(m)

    def update_cost_object(self, id: int, data: CostObjectCreate) -> CostObject:
        m = self.session.query(CostObjectModel).get(id)
        if not m:
            raise VASValidationError("COST_OBJECT_NOT_FOUND")
        m.code = data.code
        m.name = data.name
        m.object_type = CostObjectTypeDB[data.object_type.value.upper()]
        m.parent_object_id = data.parent_object_id
        m.gl_account_code = data.gl_account_code
        m.external_ref_id = data.external_ref_id
        m.external_ref_type = data.external_ref_type
        m.is_active = data.is_active
        m.custom_attributes = data.custom_attributes
        self.session.flush()
        return _cost_object_to_domain(m)

    def delete_cost_object(self, id: int) -> bool:
        m = self.session.query(CostObjectModel).get(id)
        if not m:
            raise VASValidationError("COST_OBJECT_NOT_FOUND")
        self.session.delete(m)
        return True

    # ── Accumulation ───────────────────────────────────────────────────

    def accumulate_costs(self, period_key: str) -> AccumulationResult:
        from infrastructure.models.gl_models import JournalLineModel, JournalEntryModel
        gl_period = f"{period_key[:4]}-{period_key[4:]}" if len(period_key) == 6 else period_key
        rows = self.session.query(
            JournalLineModel.account_id,
            func.sum(JournalLineModel.debit - JournalLineModel.credit),
        ).join(
            JournalEntryModel, JournalEntryModel.id == JournalLineModel.journal_entry_id
        ).filter(
            JournalEntryModel.period == gl_period,
            JournalEntryModel.is_posted == True,
        ).group_by(
            JournalLineModel.account_id,
        ).all()

        total_direct = Decimal("0")
        total_allocated = Decimal("0")
        line_count = 0
        for acct, amount in rows:
            if not amount:
                continue
            amt = Decimal(str(amount))
            total_direct += amt
            line_count += 1
        return AccumulationResult(
            period_key=period_key, total_lines=line_count,
            total_direct=total_direct, total_allocated=total_allocated,
        )

    def get_accumulated_costs(self, cost_object_id: int, period_key: str) -> List[CostAccumulation]:
        rows = self.session.query(CostAccumulationModel).filter(
            CostAccumulationModel.cost_object_id == cost_object_id,
            CostAccumulationModel.period_key == period_key,
        ).all()
        return [
            CostAccumulation(
                id=r.id, cost_object_id=r.cost_object_id,
                cost_center_id=r.cost_center_id,
                gl_account_code=r.gl_account_code, period_key=r.period_key,
                direct_cost_amount=r.direct_cost_amount,
                allocated_cost_amount=r.allocated_cost_amount,
                source_type=r.source_type, source_reference=r.source_reference,
                created_at=r.created_at,
            ) for r in rows
        ]

    # ── Budget / Actual / Variance ─────────────────────────────────────

    def sync_budget_data(self, period_key: str) -> int:
        count = 0
        try:
            from infrastructure.models.budget_models import BudgetPlanLine
            budget_lines = self.session.query(BudgetPlanLine).all()
            for bl in budget_lines:
                pass
        except ImportError:
            pass
        return count

    def get_budget(self, cost_center_id: int, period_key: str) -> List[CostCenterBudget]:
        rows = self.session.query(CostCenterBudgetModel).filter(
            CostCenterBudgetModel.cost_center_id == cost_center_id,
            CostCenterBudgetModel.period_key == period_key,
        ).all()
        return [
            CostCenterBudget(
                id=r.id, cost_center_id=r.cost_center_id,
                fiscal_year=r.fiscal_year, period_key=r.period_key,
                gl_account_code=r.gl_account_code,
                budget_amount=r.budget_amount, revised_amount=r.revised_amount,
                budget_version_id=r.budget_version_id, notes=r.notes,
            ) for r in rows
        ]

    def get_actuals(self, cost_center_id: int, period_key: str) -> List[CostCenterActual]:
        rows = self.session.query(CostCenterActualModel).filter(
            CostCenterActualModel.cost_center_id == cost_center_id,
            CostCenterActualModel.period_key == period_key,
        ).all()
        return [
            CostCenterActual(
                id=r.id, cost_center_id=r.cost_center_id,
                period_key=r.period_key, gl_account_code=r.gl_account_code,
                actual_amount=r.actual_amount, commitment_amount=r.commitment_amount,
                allocated_amount=r.allocated_amount, source_reference=r.source_reference,
            ) for r in rows
        ]

    def compute_variance(self, cost_center_id: int, period_key: str) -> List[CostCenterVariance]:
        budgets = self.get_budget(cost_center_id, period_key)
        actuals = self.get_actuals(cost_center_id, period_key)
        actual_map: Dict[str, Decimal] = {}
        for a in actuals:
            actual_map[f"{a.gl_account_code}"] = a.actual_amount
        variances: List[CostCenterVariance] = []
        for b in budgets:
            actual = actual_map.get(b.gl_account_code, Decimal("0"))
            variance = b.budget_amount - actual
            vtype = VarianceType.favorable
            if variance < Decimal("0"):
                vtype = VarianceType.unfavorable
            elif variance == Decimal("0"):
                vtype = VarianceType.neutral
            vpct = Decimal("0")
            if b.budget_amount > 0:
                vpct = (variance / b.budget_amount * Decimal("100")).quantize(Decimal("0.01"))
            variances.append(CostCenterVariance(
                cost_center_id=cost_center_id, period_key=period_key,
                gl_account_code=b.gl_account_code,
                budget_amount=b.budget_amount, actual_amount=actual,
                variance_pct=vpct, variance_type=vtype,
            ))
        return variances

    def get_cc_pl(self, cost_center_id: int, period_key: str) -> Dict:
        budgets = self.get_budget(cost_center_id, period_key)
        actuals = self.get_actuals(cost_center_id, period_key)
        act_map: Dict[str, Decimal] = {a.gl_account_code: a.actual_amount for a in actuals}
        lines: List[Dict] = []
        for b in budgets:
            act = act_map.get(b.gl_account_code, Decimal("0"))
            var = b.budget_amount - act
            lines.append({
                "gl_account_code": b.gl_account_code,
                "budget_amount": str(b.budget_amount),
                "actual_amount": str(act),
                "variance": str(var),
            })
        return {"cost_center_id": cost_center_id, "period_key": period_key, "lines": lines}

    # ── Audit ──────────────────────────────────────────────────────────

    def log_audit(self, entity_type: str, entity_id: int, action: str,
                   changes: Optional[Dict] = None, actor: str = "system",
                   ip_address: Optional[str] = None):
        self.session.add(CostingAuditLogModel(
            entity_type=entity_type, entity_id=entity_id,
            action=action, changes=changes,
            actor=actor, ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        ))
        self.session.flush()

    def get_audit_logs(self, entity_type: Optional[str] = None,
                        entity_id: Optional[int] = None,
                        limit: int = 100, offset: int = 0) -> List[Dict]:
        q = self.session.query(CostingAuditLogModel)
        if entity_type:
            q = q.filter(CostingAuditLogModel.entity_type == entity_type)
        if entity_id is not None:
            q = q.filter(CostingAuditLogModel.entity_id == entity_id)
        rows = q.order_by(desc(CostingAuditLogModel.created_at)).offset(offset).limit(limit).all()
        return [
            {
                "id": r.id, "entity_type": r.entity_type, "entity_id": r.entity_id,
                "action": r.action, "changes": r.changes,
                "actor": r.actor, "ip_address": r.ip_address,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            } for r in rows
        ]
