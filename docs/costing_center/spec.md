# Costing Center Module — Technical Specification

**Version**: 1.0
**Date**: 2026-06-30

---

## 1. Architecture

### Layer Structure (following project conventions)

```
domain/
  costing_center.py          # Pydantic entities, enums, validators

infrastructure/
  models/
    costing_center_models.py # SQLAlchemy models (12 tables)
  repositories/
    costing_center_repository.py # CRUD + business queries

use_cases/
  costing_center/
    __init__.py              # CostingCenterUseCases class

presentation/
  costing_center/
    __init__.py              # Blueprint + serializers
    routes.py                # REST endpoints

tests/
  test_costing_center_domain.py       # Domain unit tests
  test_costing_center_integration.py  # Integration tests

migrations/
  versions/
    <new_migration>.py       # Alembic migration for CC tables
```

### Dependency Graph

```
domain/ (no deps)
    │
    ▼
use_cases/ (depends: domain, infrastructure.repository, infrastructure.database)
    │
    ▼
infrastructure/repositories (depends: domain, infrastructure.models, infrastructure.database)
    │
    ▼
presentation/routes (depends: use_cases)
```

---

## 2. Domain Entities — `domain/costing_center.py`

### Enums

```python
class CostCenterType(str, Enum):
    COST = "cost"                    # Trung tâm chi phí
    PROFIT = "profit"                # Trung tâm lợi nhuận
    INVESTMENT = "investment"        # Trung tâm đầu tư
    SERVICE = "service"              # Trung tâm dịch vụ
    ADMIN = "admin"                  # Trung tâm quản lý
    SELLING = "selling"              # Trung tâm bán hàng
    PRODUCTION = "production"        # Trung tâm sản xuất
    PROJECT = "project"              # Trung tâm dự án
    VIRTUAL = "virtual"              # Trung tâm ảo (pooling)

class DriverType(str, Enum):
    QUANTITY = "quantity"            # Số lượng (headcount, sqm, kWh)
    PERCENTAGE = "percentage"        # Tỷ lệ cố định (%)
    RATE = "rate"                    # Đơn giá (VND/unit)
    ACTUAL = "actual"                # Số liệu thực tế từ GL

class AllocationMethod(str, Enum):
    DIRECT = "direct"                # Phân bổ trực tiếp
    PERCENTAGE = "percentage"        # Phân bổ theo tỷ lệ %
    PROPORTIONAL = "proportional"    # Phân bổ theo yếu tố

class AllocationRunStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"

class CostObjectType(str, Enum):
    PRODUCT = "product"
    PROJECT = "project"
    SALES_ORDER = "sales_order"
    CAMPAIGN = "campaign"
    CUSTOMER = "customer"
    DEPARTMENT = "department"

class VarianceType(str, Enum):
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"

class RuleApprovalStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
```

### Entities (Pydantic v2)

#### CostCenter
```python
class CostCenter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str = Field(..., max_length=20, pattern=r'^[A-Z0-9_]+$')
    name: str = Field(..., max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    cost_center_type: CostCenterType = CostCenterType.COST
    parent_id: Optional[int] = None
    level: int = Field(default=1, ge=1, le=10)
    path: str = Field(default="", max_length=500)  # Materialized path
    manager_employee_id: Optional[int] = None
    gl_account_code: Optional[str] = Field(None, max_length=20)
    department_code: Optional[str] = Field(None, max_length=50)
    is_cost_collector: bool = True
    is_active: bool = True
    valid_from: date = Field(default_factory=lambda: date.today())
    valid_to: Optional[date] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
```

#### CostDriver
```python
class CostDriver(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    driver_type: DriverType
    source_module: Optional[str] = Field(None, max_length=50)
    source_account_code: Optional[str] = Field(None, max_length=20)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    formula: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

#### CostAllocationRule (full model with nested targets)
```python
class CostAllocationRuleTarget(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    rule_id: int
    target_cost_center_id: int
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostAllocationRule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    rule_code: str = Field(..., max_length=20)
    rule_name: str = Field(..., max_length=200)
    source_cost_center_id: int
    driver_id: int
    allocation_method: AllocationMethod
    targets: List[CostAllocationRuleTarget] = Field(default_factory=list)
    gl_debit_account_code: str = Field(..., max_length=20)
    gl_credit_account_code: str = Field(..., max_length=20)
    priority_order: int = Field(default=0, ge=0)
    effective_from: date
    effective_to: Optional[date] = None
    approval_status: RuleApprovalStatus = RuleApprovalStatus.DRAFT
    approved_by: Optional[str] = Field(None, max_length=100)
    approved_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_by: str = Field(..., max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
```

#### CostAllocationRun / Line (as shown in BRD)

#### CostObject / CostAccumulation (as shown in BRD)

---

## 3. DB Models — `infrastructure/models/costing_center_models.py`

### Table Layout

```python
# Migration chain: ... → 3fa4b5c6d7e8 → <new_cc_migration>

cost_centers:
  id (PK, serial)
  code VARCHAR(20) NOT NULL
  name VARCHAR(200) NOT NULL
  name_en VARCHAR(200)
  cost_center_type VARCHAR(20) NOT NULL DEFAULT 'cost'
  parent_id INTEGER REFERENCES cost_centers(id)
  level INTEGER NOT NULL DEFAULT 1
  path VARCHAR(500) NOT NULL DEFAULT ''
  manager_employee_id INTEGER
  gl_account_code VARCHAR(20)
  department_code VARCHAR(50)
  is_cost_collector BOOLEAN DEFAULT TRUE
  is_active BOOLEAN DEFAULT TRUE
  valid_from DATE NOT NULL
  valid_to DATE
  created_at TIMESTAMPTZ DEFAULT NOW()
  updated_at TIMESTAMPTZ
  UNIQUE(code, parent_id)

cost_drivers:
  id (PK, serial)
  code VARCHAR(20) NOT NULL UNIQUE
  name VARCHAR(200) NOT NULL
  driver_type VARCHAR(20) NOT NULL
  source_module VARCHAR(50)
  source_account_code VARCHAR(20)
  unit_of_measure VARCHAR(50)
  formula VARCHAR(500)
  is_active BOOLEAN DEFAULT TRUE
  created_at TIMESTAMPTZ DEFAULT NOW()

cost_allocation_rules:
  id (PK, serial)
  rule_code VARCHAR(20) NOT NULL UNIQUE
  rule_name VARCHAR(200) NOT NULL
  source_cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  driver_id INTEGER REFERENCES cost_drivers(id)
  allocation_method VARCHAR(20) NOT NULL
  gl_debit_account_code VARCHAR(20) NOT NULL
  gl_credit_account_code VARCHAR(20) NOT NULL
  priority_order INTEGER NOT NULL DEFAULT 0
  effective_from DATE NOT NULL
  effective_to DATE
  approval_status VARCHAR(20) NOT NULL DEFAULT 'draft'
  approved_by VARCHAR(100)
  approved_at TIMESTAMPTZ
  notes VARCHAR(500)
  created_by VARCHAR(100) NOT NULL
  created_at TIMESTAMPTZ DEFAULT NOW()
  updated_at TIMESTAMPTZ
  CHECK (allocation_method IN ('direct', 'percentage', 'proportional'))
  CHECK (approval_status IN ('draft','pending','approved','rejected','archived'))

cost_allocation_rule_targets:
  id (PK, serial)
  rule_id INTEGER NOT NULL REFERENCES cost_allocation_rules(id) ON DELETE CASCADE
  target_cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  percentage NUMERIC(5,2)
  UNIQUE(rule_id, target_cost_center_id)

cost_allocation_runs:
  id (PK, serial)
  run_code VARCHAR(30) NOT NULL UNIQUE
  period_key VARCHAR(6) NOT NULL  -- YYYYMM
  fiscal_year INTEGER NOT NULL
  period_month INTEGER NOT NULL CHECK (period_month BETWEEN 1 AND 12)
  run_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
  run_by VARCHAR(100) NOT NULL
  status VARCHAR(20) NOT NULL DEFAULT 'draft'
  total_allocated_amount NUMERIC(18,2) DEFAULT 0
  notes VARCHAR(500)
  created_at TIMESTAMPTZ DEFAULT NOW()
  CHECK (status IN ('draft','posted','reversed'))

cost_allocation_lines:
  id (PK, serial)
  run_id INTEGER NOT NULL REFERENCES cost_allocation_runs(id) ON DELETE CASCADE
  source_cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  target_cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  rule_id INTEGER REFERENCES cost_allocation_rules(id)
  driver_id INTEGER REFERENCES cost_drivers(id)
  gl_account_code VARCHAR(20) NOT NULL
  original_amount NUMERIC(18,2) NOT NULL
  allocated_amount NUMERIC(18,2) NOT NULL
  driver_quantity NUMERIC(18,2)
  driver_rate NUMERIC(18,2)
  allocation_basis_description VARCHAR(500)

cost_objects:
  id (PK, serial)
  code VARCHAR(20) NOT NULL UNIQUE
  name VARCHAR(200) NOT NULL
  object_type VARCHAR(20) NOT NULL
  parent_object_id INTEGER REFERENCES cost_objects(id)
  gl_account_code VARCHAR(20)
  external_ref_id INTEGER          -- FK to product/project/order
  external_ref_type VARCHAR(50)    -- 'product', 'project', 'order'
  is_active BOOLEAN DEFAULT TRUE
  custom_attributes JSONB
  created_at TIMESTAMPTZ DEFAULT NOW()

cost_accumulations:
  id (PK, serial)
  cost_object_id INTEGER NOT NULL REFERENCES cost_objects(id)
  cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  gl_account_code VARCHAR(20) NOT NULL
  period_key VARCHAR(6) NOT NULL
  direct_cost_amount NUMERIC(18,2) DEFAULT 0
  allocated_cost_amount NUMERIC(18,2) DEFAULT 0
  total_cost_amount NUMERIC(18,2) GENERATED ALWAYS AS (direct_cost_amount + allocated_cost_amount) STORED
  source_type VARCHAR(20)           -- 'gl', 'manual', 'allocation'
  source_reference VARCHAR(50)
  created_at TIMESTAMPTZ DEFAULT NOW()
  UNIQUE(cost_object_id, cost_center_id, gl_account_code, period_key)

cost_center_budgets:
  id (PK, serial)
  cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  fiscal_year INTEGER NOT NULL
  period_key VARCHAR(6) NOT NULL
  gl_account_code VARCHAR(20) NOT NULL
  budget_amount NUMERIC(18,2) DEFAULT 0
  revised_amount NUMERIC(18,2) DEFAULT 0
  budget_version_id INTEGER
  notes VARCHAR(500)
  UNIQUE(cost_center_id, period_key, gl_account_code)

cost_center_actuals:
  id (PK, serial)
  cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  period_key VARCHAR(6) NOT NULL
  gl_account_code VARCHAR(20) NOT NULL
  actual_amount NUMERIC(18,2) DEFAULT 0
  commitment_amount NUMERIC(18,2) DEFAULT 0
  allocated_amount NUMERIC(18,2) DEFAULT 0
  source_reference VARCHAR(100)
  updated_at TIMESTAMPTZ DEFAULT NOW()
  UNIQUE(cost_center_id, period_key, gl_account_code)

cost_center_variances:
  id (PK, serial)
  cost_center_id INTEGER NOT NULL REFERENCES cost_centers(id)
  period_key VARCHAR(6) NOT NULL
  gl_account_code VARCHAR(20) NOT NULL
  budget_amount NUMERIC(18,2) DEFAULT 0
  actual_amount NUMERIC(18,2) DEFAULT 0
  variance_amount NUMERIC(18,2) GENERATED ALWAYS AS (budget_amount - actual_amount) STORED
  variance_pct NUMERIC(5,2)
  variance_type VARCHAR(20)
  annotation TEXT
  UNIQUE(cost_center_id, period_key, gl_account_code)

costing_audit_logs:
  id (PK, serial)
  entity_type VARCHAR(30) NOT NULL
  entity_id INTEGER NOT NULL
  action VARCHAR(30) NOT NULL
  changes JSONB
  actor VARCHAR(100) NOT NULL
  ip_address VARCHAR(45)
  created_at TIMESTAMPTZ DEFAULT NOW()
  INDEX(entity_type, entity_id)
  INDEX(created_at)
```

### Index Strategy

```sql
CREATE INDEX idx_cc_path ON cost_centers(path);
CREATE INDEX idx_cc_parent ON cost_centers(parent_id);
CREATE INDEX idx_cc_active ON cost_centers(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_cc_code ON cost_centers(code);
CREATE INDEX idx_rules_source ON cost_allocation_rules(source_cost_center_id);
CREATE INDEX idx_rules_active ON cost_allocation_rules(effective_from, effective_to)
    WHERE approval_status = 'approved';
CREATE INDEX idx_runs_period ON cost_allocation_runs(period_key);
CREATE INDEX idx_lines_run ON cost_allocation_lines(run_id);
CREATE INDEX idx_acc_period ON cost_accumulations(period_key);
CREATE INDEX idx_acc_object ON cost_accumulations(cost_object_id);
CREATE INDEX idx_actuals_period ON cost_center_actuals(period_key);
CREATE INDEX idx_actuals_cc ON cost_center_actuals(cost_center_id);
CREATE INDEX idx_variances_cc ON cost_center_variances(cost_center_id, period_key);
```

---

## 4. Repository — `infrastructure/repositories/costing_center_repository.py`

### Methods

```python
class CostingCenterRepository:
    # Cost Center CRUD
    def get_cost_center(self, id: int) -> Optional[CostCenter]
    def get_cost_center_by_code(self, code: str) -> Optional[CostCenter]
    def list_cost_centers(self, parent_id: Optional[int], active_only: bool) -> List[CostCenter]
    def get_cost_center_tree(self, root_id: Optional[int]) -> List[Dict]  # recursive
    def create_cost_center(self, data: CostCenterCreate) -> CostCenter
    def update_cost_center(self, id: int, data: CostCenterUpdate) -> CostCenter
    def deactivate_cost_center(self, id: int) -> bool
    def move_cost_center(self, id: int, new_parent_id: int) -> CostCenter
    def validate_no_circular_ref(self, node_id: int, new_parent_id: int) -> bool
    def has_active_transactions(self, id: int) -> bool
    def bulk_import_cost_centers(self, rows: List[Dict]) -> BulkImportResult
    def export_cost_centers(self, active_only: bool) -> List[Dict]

    # Driver CRUD
    def get_driver(self, id: int) -> Optional[CostDriver]
    def list_drivers(self, active_only: bool) -> List[CostDriver]
    def create_driver(self, data: CostDriverCreate) -> CostDriver
    def update_driver(self, id: int, data: CostDriverUpdate) -> CostDriver
    def delete_driver(self, id: int) -> bool
    def is_driver_in_use(self, id: int) -> bool
    def get_driver_value(self, driver_id: int, cost_center_id: int, period_key: str) -> Decimal

    # Rule CRUD
    def get_rule(self, id: int) -> Optional[CostAllocationRule]
    def list_rules(self, filters: Dict) -> List[CostAllocationRule]
    def create_rule(self, data: CostAllocationRuleCreate) -> CostAllocationRule
    def update_rule(self, id: int, data: CostAllocationRuleUpdate) -> CostAllocationRule
    def approve_rule(self, id: int, approved_by: str) -> CostAllocationRule
    def archive_rule(self, id: int) -> bool
    def detect_circular_allocation(self, source_cc_id: int, target_cc_ids: List[int]) -> bool
    def get_active_rules_for_period(self, period_key: str) -> List[CostAllocationRule]

    # Allocation Run
    def create_allocation_run(self, period_key: str, run_by: str) -> CostAllocationRun
    def get_allocation_run(self, id: int) -> Optional[CostAllocationRun]
    def get_allocation_run_by_period(self, period_key: str) -> Optional[CostAllocationRun]
    def list_allocation_runs(self, period_key: Optional[str]) -> List[CostAllocationRun]
    def post_allocation_run(self, run_id: int, journal_entry_ref: str) -> CostAllocationRun
    def reverse_allocation_run(self, run_id: int, reversed_by: str) -> CostAllocationRun
    def save_allocation_lines(self, run_id: int, lines: List[CostAllocationLine])
    def get_allocation_lines(self, run_id: int) -> List[CostAllocationLine]
    def get_allocation_matrix(self, period_key: str) -> List[Dict]

    # Cost Object
    def get_cost_object(self, id: int) -> Optional[CostObject]
    def list_cost_objects(self, object_type: Optional[str]) -> List[CostObject]
    def create_cost_object(self, data: CostObjectCreate) -> CostObject
    def update_cost_object(self, id: int, data: CostObjectUpdate) -> CostObject
    def delete_cost_object(self, id: int) -> bool

    # Accumulation
    def accumulate_costs(self, period_key: str) -> AccumulationResult
    def get_accumulated_costs(self, cost_object_id: int, period_key: str) -> List[CostAccumulation]
    def get_cost_object_summary(self, cost_object_id: int) -> Dict

    # Budget / Actual / Variance
    def sync_budget_data(self, period_key: str) -> int
    def get_budget(self, cost_center_id: int, period_key: str) -> List[CostCenterBudget]
    def get_actuals(self, cost_center_id: int, period_key: str) -> List[CostCenterActual]
    def compute_variance(self, cost_center_id: int, period_key: str) -> List[CostCenterVariance]
    def get_cc_pl(self, cost_center_id: int, period_key: str) -> Dict

    # Reports
    def get_cc_pl_report(self, cost_center_ids: List[int], period_keys: List[str]) -> List[Dict]
    def get_allocation_summary_report(self, period_key: str) -> Dict
    def get_variance_report(self, cost_center_id: int, period_key: str) -> List[Dict]
    def get_hierarchy_report(self, root_id: Optional[int]) -> List[Dict]

    # Audit
    def log_audit(self, entity_type: str, entity_id: int, action: str,
                   changes: Optional[Dict], actor: str, ip_address: Optional[str])
    def get_audit_logs(self, entity_type: Optional[str], entity_id: Optional[int],
                        limit: int, offset: int) -> List[Dict]

    # Import/Export
    def export_to_excel(self, entity_type: str, filters: Dict) -> bytes
    def import_from_excel(self, entity_type: str, file_bytes: bytes) -> BulkImportResult
```

---

## 5. Use Cases — `use_cases/costing_center/__init__.py`

### Class: `CostingCenterUseCases`

```python
class CostingCenterUseCases:
    def __init__(self, repo: CostingCenterRepository, gl_repo: GLRepository, db: SmartACCTDatabase)

    # UC-CC-01
    def create_cost_center(self, data: CostCenterCreate, actor: str) -> Result
    def update_cost_center(self, id: int, data: CostCenterUpdate, actor: str) -> Result
    def deactivate_cost_center(self, id: int, actor: str) -> Result
    def move_cost_center(self, id: int, new_parent_id: int, actor: str) -> Result
    def get_cost_center_tree(self, root_id: Optional[int]) -> List[Dict]
    def bulk_import_cost_centers(self, rows: List[Dict], actor: str) -> BulkImportResult

    # UC-CC-02
    def create_driver(self, data: CostDriverCreate, actor: str) -> Result
    def update_driver(self, id: int, data: CostDriverUpdate, actor: str) -> Result
    def delete_driver(self, id: int, actor: str) -> Result
    def get_driver_value(self, driver_id: int, cc_id: int, period_key: str) -> Decimal

    # UC-CC-03
    def create_allocation_rule(self, data: CostAllocationRuleCreate, actor: str) -> Result
    def update_allocation_rule(self, id: int, data: CostAllocationRuleUpdate, actor: str) -> Result
    def approve_allocation_rule(self, id: int, approved_by: str) -> Result
    def archive_allocation_rule(self, id: int, actor: str) -> Result
    def preview_allocation(self, rule_id: int, period_key: str) -> List[Dict]

    # UC-CC-04
    def execute_allocation(self, period_key: str, rule_ids: Optional[List[int]], 
                           dry_run: bool, actor: str) -> Result
    def post_allocation(self, run_id: int, actor: str) -> Result
    def reverse_allocation(self, run_id: int, actor: str) -> Result

    # UC-CC-05
    def create_cost_object(self, data: CostObjectCreate, actor: str) -> Result
    def get_cost_object_costing(self, object_id: int, period_key: str) -> Dict

    # UC-CC-06
    def accumulate_costs(self, period_key: str, actor: str) -> AccumulationResult
    def get_cost_accumulation(self, object_id: int, period_key: str) -> List[Dict]

    # UC-CC-07/08
    def sync_budget(self, period_key: str, actor: str) -> int
    def get_variance_analysis(self, cc_id: int, period_key: str) -> List[Dict]

    # UC-CC-10/11 — Reports
    def get_cc_pl_report(self, cc_ids: List[int], period_keys: List[str]) -> bytes
    def get_allocation_summary(self, period_key: str) -> Dict
    def export_report_excel(self, report_type: str, params: Dict) -> bytes

    # UC-CC-13
    def get_audit_logs(self, entity_type: Optional[str], entity_id: Optional[int]) -> List[Dict]
```

### Allocation Engine Algorithm

```python
def execute_allocation(self, period_key: str, rule_ids: List[int], dry_run: bool, actor: str) -> Result:
    """Core allocation engine."""

    # 1. Validate period is open
    if not self._is_period_open(period_key):
        return Result.failure("PERIOD_CLOSED")

    # 2. Get rules in priority order
    rules = self.repo.get_active_rules_for_period(period_key)
    if rule_ids:
        rules = [r for r in rules if r.id in rule_ids]

    if not rules:
        return Result.failure("COST_NO_RULES_FOR_PERIOD")

    # 3. Cycle detection
    self._validate_no_cycles(rules)

    # 4. Execute each rule sequentially
    lines = []
    for rule in rules:
        source_amount = self._get_source_balance(rule.source_cost_center_id, 
                                                   rule.gl_debit_account_code, period_key)
        if source_amount == 0:
            continue

        driver_values = self._get_driver_values(rule.driver_id, rule.targets, period_key)
        total_driver = sum(dv.value for dv in driver_values)

        if total_driver == 0:
            continue

        for target in rule.targets:
            if rule.allocation_method == AllocationMethod.DIRECT:
                allocated = source_amount
            elif rule.allocation_method == AllocationMethod.PERCENTAGE:
                allocated = source_amount * target.percentage / 100
            elif rule.allocation_method == AllocationMethod.PROPORTIONAL:
                driver_val = next((dv.value for dv in driver_values 
                                   if dv.cc_id == target.target_cost_center_id), 0)
                allocated = source_amount * driver_val / total_driver

            lines.append(CostAllocationLine(
                source_cost_center_id=rule.source_cost_center_id,
                target_cost_center_id=target.target_cost_center_id,
                rule_id=rule.id,
                driver_id=rule.driver_id,
                gl_account_code=rule.gl_debit_account_code,
                original_amount=source_amount,
                allocated_amount=_quantize_vnd(allocated),
                driver_quantity=driver_val,
                driver_rate=source_amount / total_driver if total_driver > 0 else 0,
            ))

    # 5. Handle rounding remainder for percentage method
    lines = self._balance_rounding(lines)

    # 6. Save run (draft or posted)
    if dry_run:
        return Result.success(lines)
    else:
        run = self.repo.create_allocation_run(period_key, actor)
        self.repo.save_allocation_lines(run.id, lines)
        return Result.success({"run_id": run.id, "lines_count": len(lines), 
                               "total": sum(l.allocated_amount for l in lines)})
```

---

## 6. API Routes — `presentation/costing_center/routes.py`

### Blueprint: `/api/v1/costing-center`

| Method | Endpoint | UC | Description |
|--------|----------|----|-------------|
| POST | `/cost-centers` | CC-01 | Create cost center |
| GET | `/cost-centers/tree` | CC-01 | Get hierarchy tree |
| GET | `/cost-centers/{id}` | CC-01 | Get cost center |
| PUT | `/cost-centers/{id}` | CC-01 | Update cost center |
| PATCH | `/cost-centers/{id}/deactivate` | CC-01 | Deactivate cost center |
| POST | `/cost-centers/{id}/move` | CC-01 | Move in hierarchy |
| POST | `/cost-centers/import` | CC-12 | Bulk import |
| GET | `/cost-centers/export` | CC-12 | Export to Excel |
| POST | `/drivers` | CC-02 | Create driver |
| GET | `/drivers` | CC-02 | List drivers |
| PUT | `/drivers/{id}` | CC-02 | Update driver |
| DELETE | `/drivers/{id}` | CC-02 | Delete driver |
| POST | `/allocation-rules` | CC-03 | Create rule |
| GET | `/allocation-rules` | CC-03 | List rules |
| GET | `/allocation-rules/{id}` | CC-03 | Get rule |
| PUT | `/allocation-rules/{id}` | CC-03 | Update rule |
| POST | `/allocation-rules/{id}/approve` | CC-03 | Approve rule |
| POST | `/allocation-rules/{id}/archive` | CC-03 | Archive rule |
| POST | `/allocation-rules/{id}/preview` | CC-03 | Preview allocation |
| POST | `/allocation-runs` | CC-04 | Execute allocation |
| GET | `/allocation-runs` | CC-04 | List runs |
| GET | `/allocation-runs/{id}` | CC-04 | Get run details |
| POST | `/allocation-runs/{id}/post` | CC-04 | Post to GL |
| POST | `/allocation-runs/{id}/reverse` | CC-04 | Reverse |
| POST | `/cost-objects` | CC-05 | Create cost object |
| GET | `/cost-objects` | CC-05 | List cost objects |
| GET | `/cost-objects/{id}/costing` | CC-06 | Get cost accumulation |
| POST | `/accumulate` | CC-06 | Trigger accumulation |
| POST | `/sync-budget` | CC-07 | Sync budget data |
| GET | `/variance` | CC-08 | Get variance analysis |
| GET | `/reports/cc-pl` | CC-10 | Cost center P&L |
| GET | `/reports/allocation-summary` | CC-11 | Allocation summary |
| GET | `/reports/variance` | CC-08 | Variance report |
| GET | `/audit-logs` | CC-13 | Get audit logs |
| GET | `/dashboard` | CC-14 | Dashboard KPIs |
| GET | `/managers/my-cost-centers` | CC-15 | Manager self-service |

---

## 7. GL Posting Integration

### Journal Entry Format for Allocation

```python
def _build_allocation_journal_entries(lines: List[CostAllocationLine], period_key: str):
    """Build GL journal entries from allocation lines."""
    entries = []
    for line in lines:
        # Debit: target cost center
        entries.append({
            "account_code": line.gl_account_code,
            "debit_amount": line.allocated_amount,
            "credit_amount": 0,
            "cost_center_id": line.target_cost_center_id,
            "cost_object_id": None,
            "notes": f"Allocation from CC#{line.source_cost_center_id} via rule#{line.rule_id}",
        })
        # Credit: source cost center
        entries.append({
            "account_code": line.gl_account_code,
            "debit_amount": 0,
            "credit_amount": line.allocated_amount,
            "cost_center_id": line.source_cost_center_id,
            "cost_object_id": None,
            "notes": f"Allocated to CC#{line.target_cost_center_id} via rule#{line.rule_id}",
        })

    # Validate balance
    total_debit = sum(e["debit_amount"] for e in entries)
    total_credit = sum(e["credit_amount"] for e in entries)
    if abs(total_debit - total_credit) > Decimal("0.001"):
        raise VASValidationError("COST_GL_IMBALANCE")

    return JournalEntryCreate(
        journal_type="cost_allocation",
        period_key=period_key,
        description=f"Cost allocation for {period_key}",
        lines=entries,
    )
```

---

## 8. Data Flow Diagrams

### Allocation Execution Flow

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│ CostAccount  │───>│  Allocation  │───>│  GL Repository│
│  trigers     │    │  Engine      │    │               │
│  run         │    │              │    │  Validate     │
└─────────────┘    │  1. Read     │    │  accounts     │
                   │  rules       │    │  exist        │
                   │  2. Read     │    └───────┬───────┘
                   │  balances    │            │
                   │  3. Read     │            ▼
                   │  drivers     │    ┌───────────────┐
                   │  4. Compute  │    │  Create JE    │
                   │  amounts     │    │  in GL        │
                   │  5. Balance  │    │  (draft)      │
                   │  rounding    │    └───────┬───────┘
                   └──────┬───────┘            │
                          │                    │
                          ▼                    ▼
                   ┌──────────────┐    ┌───────────────┐
                   │  Save Run    │    │  Post JE      │
                   │  + Lines     │    │  (final)      │
                   │  (DB)        │    │               │
                   └──────┬───────┘    └───────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Audit Log   │
                   │  "Run posted"│
                   └──────────────┘
```

### Cost Accumulation Flow

```
GL Tables ──> CostCenterActuals ──> VarianceEngine ──> Report
     │                                      │
     │                                      ▼
     └──> CostObjectAccumulation ──> CostObjectCosting ──> PDF/Excel
```

---

## 9. Error Codes (`domain/i18n.py` additions)

```python
# Costing Center module (CC- prefix)
COST_CENTER_CODE_DUPLICATE = "COST_CENTER_CODE_DUPLICATE"
COST_CENTER_CIRCULAR_REF = "COST_CENTER_CIRCULAR_REF"
COST_CENTER_MAX_DEPTH = "COST_CENTER_MAX_DEPTH"
COST_CENTER_HAS_TRANSACTIONS = "COST_CENTER_HAS_TRANSACTIONS"
COST_CENTER_NOT_FOUND = "COST_CENTER_NOT_FOUND"
COST_CENTER_INACTIVE = "COST_CENTER_INACTIVE"
COST_CENTER_INVALID_TYPE = "COST_CENTER_INVALID_TYPE"
COST_CENTER_INVALID_DATE = "COST_CENTER_INVALID_DATE"
COST_CENTER_MANAGER_NOT_FOUND = "COST_CENTER_MANAGER_NOT_FOUND"
COST_CENTER_GL_ACCOUNT_INVALID = "COST_CENTER_GL_ACCOUNT_INVALID"
COST_CENTER_IMPORT_TEMPLATE_MISMATCH = "COST_CENTER_IMPORT_TEMPLATE_MISMATCH"

COST_DRIVER_CODE_DUPLICATE = "COST_DRIVER_CODE_DUPLICATE"
COST_DRIVER_INVALID_FORMULA = "COST_DRIVER_INVALID_FORMULA"
COST_DRIVER_IN_USE = "COST_DRIVER_IN_USE"
COST_DRIVER_DATA_MISSING = "COST_DRIVER_DATA_MISSING"
COST_DRIVER_DATA_STALE = "COST_DRIVER_DATA_STALE"

COST_ALLOCATION_CIRCULAR = "COST_ALLOCATION_CIRCULAR"
COST_ALLOCATION_TOTAL_NOT_100 = "COST_ALLOCATION_TOTAL_NOT_100"
COST_ALLOCATION_SAME_CC = "COST_ALLOCATION_SAME_CC"
COST_ALLOCATION_DUPLICATE_SOURCE = "COST_ALLOCATION_DUPLICATE_SOURCE"
COST_ALLOCATION_RULE_NOT_FOUND = "COST_ALLOCATION_RULE_NOT_FOUND"
COST_ALLOCATION_RULE_INACTIVE = "COST_ALLOCATION_RULE_INACTIVE"
COST_ALLOCATION_RULE_NOT_APPROVED = "COST_ALLOCATION_RULE_NOT_APPROVED"

COST_NO_RULES_FOR_PERIOD = "COST_NO_RULES_FOR_PERIOD"
COST_GL_POSTING_ERROR = "COST_GL_POSTING_ERROR"
COST_GL_DATA_UNAVAILABLE = "COST_GL_DATA_UNAVAILABLE"
COST_ACCUMULATION_MISMATCH = "COST_ACCUMULATION_MISMATCH"
COST_RUN_NOT_FOUND = "COST_RUN_NOT_FOUND"
COST_RUN_ALREADY_POSTED = "COST_RUN_ALREADY_POSTED"

COST_OBJECT_CODE_DUPLICATE = "COST_OBJECT_CODE_DUPLICATE"
COST_OBJECT_MISSING_BOM = "COST_OBJECT_MISSING_BOM"
COST_OBJECT_NOT_FOUND = "COST_OBJECT_NOT_FOUND"

COST_IMPORT_TEMPLATE_MISMATCH = "COST_IMPORT_TEMPLATE_MISMATCH"
COST_IMPORT_REF_ERROR = "COST_IMPORT_REF_ERROR"
```

---

## 10. Implementation Phases

### Phase 1 — Foundation (Weeks 1-4)
1. `domain/costing_center.py` — entities + enums + validators
2. `infrastructure/models/costing_center_models.py` — 12 tables
3. Alembic migration script
4. `infrastructure/repositories/costing_center_repository.py` — CRUD methods
5. `use_cases/costing_center/__init__.py` — UC-CC-01 through UC-CC-04
6. `presentation/costing_center/` — routes for UC-CC-01 to CC-04
7. Tests: domain (40+) + integration (30+)

### Phase 2 — Cost Tracking (Weeks 5-7)
1. UC-CC-05 (Cost Objects) + UC-CC-06 (Accumulation)
2. UC-CC-07 (Budget sync) + UC-CC-08 (Variance)
3. UC-CC-09 (GL integration — JE dimension)
4. Reports: CC P&L, Allocation Summary
5. Tests: 30+ integration

### Phase 3 — Advanced (Weeks 8-10)
1. UC-CC-10 through UC-CC-12 (Reports + Import/Export)
2. UC-CC-13 (Audit Trail)
3. UC-CC-14 (Dashboard)
4. UC-CC-15 (Manager Self-Service)
5. Edge case hardening
6. Performance optimization
7. Full test suite: 100+ tests

---

## 11. Test Plan

### Domain Tests (~60 tests)
- `test_cost_center_validation` (code format, dates, hierarchy)
- `test_cost_driver_validation` (type, formula parsing)
- `test_allocation_rule_validation` (circular detection, sum=100%)
- `test_allocation_engine` (direct, %, proportional, rounding)
- `test_cost_object_validation`
- `test_accumulation_calculation`
- `test_variance_computation`
- `test_error_codes`

### Integration Tests (~70 tests)
- `test_cost_center_crud` (CRUD + move + deactivate)
- `test_cost_center_hierarchy` (tree operations)
- `test_cost_center_import_export`
- `test_driver_crud`
- `test_allocation_rule_crud` + approval workflow
- `test_allocation_execution` (dry run, post, reverse)
- `test_gl_integration` (JE generation, balance check)
- `test_cost_accumulation`
- `test_budget_sync`
- `test_variance_analysis`
- `test_reports` (P&L, allocation summary)
- `test_audit_log`
- `test_dashboard_kpi`
- `test_error_scenarios` (circular ref, closed period, missing driver)
- `test_concurrency` (simultaneous runs)

---

## 12. Security

- Cost center data access: role-based (manager sees own, accountant sees all)
- Allocation rule approval: required 4-eyes principle (accountant creates, FD approves)
- Allocation run reversal: requires chief accountant approval + audit log
- API rate limiting on allocation execution (max 1 per 5 minutes per period)
- Input sanitization on all string fields
- SQL injection prevention via ORM parameterized queries
- Audit logs immutable (append-only)
- Sensitive data in allocation notes: encrypted at rest (column-level encryption)

---

## 13. Performance Targets

| Operation | Target | Max |
|-----------|--------|-----|
| Cost center tree load (1000 nodes) | 500ms | 2s |
| Single allocation run (200 CC, 50 rules) | 2min | 5min |
| Report generation (1000 CC) | 3s | 10s |
| Import 5000 rows | 30s | 60s |
| Cost accumulation (monthly) | 10s | 30s |
| API response (CRUD) | 200ms | 1s |
| Concurrent runs | 5 | 10 |
