# COA Module — Implementation Plan

## Overview
Implement Chart of Accounts module per BRD. Vertical slices, TDD, each leaves system working.

## Architecture Decisions
- **Regime strategy**: TT99 primary, TT133 backwards-compat via `AccountingRegime` enum. No IFRS yet.
- **DB**: SQLAlchemy declarative models in `infrastructure/models/`, one file per module.
- **Domain**: Pydantic models stay pure. DB models are separate. Repository maps between them.
- **No auth middleware yet** — skip JWT for Phase 1, focus on core logic.
- **No approval workflow yet** — skip DRAFT→APPROVED state machine. ACTIVE/SUSPENDED/CLOSED only.

## Task List

### Phase 0: Domain Model Update
- [ ] 0.1: Add `AccountingRegime` enum (TT99_2025, TT133_2016)
- [ ] 0.2: Add `AccountStatus` enum (ACTIVE, SUSPENDED, CLOSED)
- [ ] 0.3: Update `ChartOfAccounts` to include `regime` field
- [ ] 0.4: Add TT99-compatible validation rules
- **Verify**: `pytest tests/ -x` passes (empty suite = green)

### Phase 1: DB Models + Migration
- [ ] 1.1: Create `infrastructure/models/__init__.py`
- [ ] 1.2: Create `infrastructure/models/coa_models.py` — COAModel, AccountModel
- [ ] 1.3: Create Alembic migration for COA tables
- [ ] 1.4: Update `infrastructure/database.py` to load models
- **Verify**: `python -c "from infrastructure.models.coa_models import COAModel; print('OK')"`

### Phase 2: Repository Layer
- [ ] 2.1: Create `infrastructure/repositories/__init__.py`
- [ ] 2.2: Create `infrastructure/repositories/coa_repository.py`
- [ ] 2.3: Create `infrastructure/repositories/account_repository.py`
- **Verify**: Repo tests pass

### Phase 3: Use Cases
- [ ] 3.1: Create `use_cases/__init__.py`
- [ ] 3.2: Create `use_cases/coa_use_cases.py` — CreateCOA, GetCOA, ListCOA, UpdateCOA, DeleteCOA
- [ ] 3.3: Create `use_cases/account_use_cases.py` — CRUD for accounts
- [ ] 3.4: Create `use_cases/coa_import_use_case.py` — Excel import
- [ ] 3.5: Create `use_cases/coa_validate_use_case.py` — Compliance validation
- **Verify**: Use case unit tests pass

### Phase 4: Presentation (API)
- [ ] 4.1: Create `presentation/__init__.py`
- [ ] 4.2: Create `presentation/coa_routes.py` — COA CRUD endpoints
- [ ] 4.3: Create `presentation/account_routes.py` — Account CRUD endpoints
- **Verify**: `curl` smoke tests pass

### Phase 5: Tests
- [ ] 5.1: Domain model tests
- [ ] 5.2: Repository tests (with test DB)
- [ ] 5.3: Use case tests
- [ ] 5.4: API integration tests
- **Verify**: `pytest tests/ -v --cov` passes

### Phase 6: Docs & Git
- [ ] 6.1: Update AGENTS.md with new module structure
- [ ] 6.2: Commit all changes
- **Verify**: `git status` clean, `git log` shows history
