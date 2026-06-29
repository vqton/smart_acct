# SmartACCT | AGENTS.md

Vietnamese ERP (Flask + SQLAlchemy + PostgreSQL 16). Flattened structure — no `/app/` directory.

---

## 1. Project Overview

```
/home/projects/smart_acct/
├── config.py              # Pydantic config, env vars, connection pooling
├── run.py                 # Flask entry point
├── alembic.ini            # Alembic config (reads DATABASE_URL from .env)
├── CHANGELOG.md           # Release notes
├── domain/                # Pure domain models (Pydantic v2, no framework deps)
│   └── __init__.py        # All domain entities + enums (TT99/2025, TT133/2016)
├── infrastructure/
│   ├── database.py        # DB manager, JWT auth, formatters
│   ├── models/
│   │   ├── __init__.py
│   │   ├── coa_models.py         # SQLAlchemy models for COA
│   │   └── tax_models.py         # SQLAlchemy models for tax (8 tables)
│   └── repositories/
│       ├── __init__.py
│       ├── coa_repository.py     # COA CRUD repo (domain↔DB mapping)
│       └── tax_repository.py     # Tax CRUD repo (7 entity types)
├── use_cases/
│   ├── __init__.py
│   ├── coa_use_cases.py          # COA CRUD use cases
│   ├── coa_validate_use_case.py  # VAS compliance validation
│   └── tax_use_cases.py          # Tax CRUD + VAT calc + schedule gen
├── presentation/
│   ├── __init__.py
│   ├── coa_routes.py     # Flask blueprint (/api/v1/coa/*)
│   └── tax_routes.py     # Flask blueprint (/api/v1/tax/*, 40 endpoints)
├── services/
│   ├── gdt_client.py     # GDT eTax API client stub
│   └── signing_service.py# RSA-SHA256 e-invoice signing stub
├── migrations/
│   └── versions/          # Alembic migration scripts (COA + tax)
├── tests/
│   ├── __init__.py
│   ├── test_coa_domain.py        # COA domain unit tests
│   ├── test_tax_domain.py        # Tax domain unit tests
│   └── test_tax_integration.py   # Tax repository + use case integration
└── requirements.txt
```

**Tech Stack**: Flask 3.0, SQLAlchemy 2.0, PostgreSQL 16, PyJWT, Casbin, openpyxl, WeasyPrint, pytest.

---

## 2. Setup & Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000
```

### Quick Start
```bash
mv .venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python run.py          # http://0.0.0.0:5000
```

### Database Pooling
- Pool size: 20, max overflow: 30, recycle: 3600s
- PostgreSQL 16 required (Docker recommended)
- Never create separate `SQLAlchemy` instances — use `infrastructure/database.py` manager
- Dispose connections in teardown

### Production
- TLS/HTTPS required
- Regular PostgreSQL backups
- Connection pool monitoring (nest 80/tcp)

---

## 3. Architecture

### Layer Rules
| Layer | Depends On | Responsibility |
|-------|-----------|----------------|
| `domain/` | Nothing | Pure Pydantic entities, no framework/DB imports |
| `use_cases/` | domain | Application logic (journal posting, VAT, month-end close) |
| `infrastructure/` | domain | DB, auth, formatting, repositories |
| `presentation/` | use_cases | Flask blueprints, Jinja2 templates |
| `services/` | domain, infrastructure | Report generation |

### Vietnam (VAS) Conventions
- **Account codes**: Circular 133/2016 format (`1.1.1`, `2.1.1`, `4.1.1`). Valid: `1`, `1.1`, `1.1.1`, `12345`. Invalid: `0`, `A1`, `>4 levels`.
- **DCR Direction**: Debit normal = ASSET, CASH, INVENTORY, EXPENSE. Credit normal = LIABILITY, EQUITY, REVENUE.
- **Double-entry**: Must balance within 0.001 VND tolerance
- **Currency**: VND preferred. Locale: `1.500.000,50 đ`. Also USD, EUR, JPY, GBP.
- **Dates**: Vietnamese month names (`15 tháng 1 năm 2024`)
- **Account types**: 33+ from Circular 133/2016
- **Monthly balances**: Table for fast financial statements

### Code Conventions
- **Imports**: `from domain.models import JournalEntry`
- **Type hints**: Required everywhere
- **Errors**: Raise `VASValidationError` or `ValidationError`
- **No hardcoded currency symbols**

---

## 4. Development Workflow (TDD)

### Feature Flow
```
interview-me → spec-driven-development → planning-and-task-breakdown
→ incremental-implementation + test-driven-development
→ code-review-and-quality → code-simplification
→ shipping-and-launch
```

### Implementation Steps
1. Write failing test in `tests/` (Red)
2. Implement minimal code in `use_cases/` (Green)
3. Refactor while tests stay green
4. Add repository in `infrastructure/repositories/` (if needed)
5. Update domain in `domain/` (if needed)
6. Add route in `presentation/routes.py`

### Testing
```bash
./venv/bin/pytest tests/                    # All
./venv/bin/pytest tests/test_domain.py      # Domain
./venv/bin/pytest tests/test_integration.py  # Integration
./venv/bin/pytest tests/ -v                 # Verbose
```

**Test categories**: Unit (domain validation), Integration (use cases + DB), Edge cases (invalid codes, amounts, dates).

### Security
- JWT Bearer tokens for API auth
- bcrypt password hashing
- Flask-JWT session management
- Rate limiting on endpoints

---

## 5. Tooling & Navigation

### CodeGraph (Primary Navigation)
**Always use CodeGraph first** — pre-built knowledge graph, faster than grep/read.

| Intent | Tool |
|--------|------|
| "How does X work?" / Architecture / Bug / "Where is X?" | `codegraph_explore` **(PRIMARY)** |
| "What calls X?" / "What does X call?" / Blast radius | `codegraph_callers` / `codegraph_callees` / `codegraph_impact` |
| Symbol location only | `codegraph_search` |
| One symbol full source (overloaded names) | `codegraph_node` with `includeCode=true` |
| Directory tree | `codegraph_files` |
| Index health | `codegraph_status` |

**Anti-patterns**: Don't grep first. Don't chain search+node — one `explore` does it. Don't loop `node` over many symbols. Don't re-verify CodeGraph results.

**Staleness**: If banner says "edited since last sync", read those files. Others are fresh.

### Skills Reference
**Always check skills before non-trivial work.** Load with: `skill <name>`

| When | Skill |
|------|-------|
| Vague request ("build X") | `interview-me` |
| Rough idea, need options | `idea-refine` |
| New project, no spec | `spec-driven-development` |
| Have spec, need tasks | `planning-and-task-breakdown` |
| Implementing | `incremental-implementation` |
| API design | `api-and-interface-design` |
| UI work | `frontend-ui-engineering` |
| Writing tests | `test-driven-development` |
| Bug | `debugging-and-error-recovery` |
| Code quality | `karpathy-guidelines` |
| Code review | `code-review-and-quality` |
| Too complex | `code-simplification` |
| Security | `security-and-hardening` |
| Performance | `performance-optimization` |
| Deploy | `shipping-and-launch` |
| Docs/ADRs | `documentation-and-adrs` |
| Git | `git-workflow-and-versioning` |
| CI/CD | `ci-cd-and-automation` |

### Karpathy Principles (Load at session start: `skill karpathy-guidelines`)

1. **Think before coding** — State assumptions, name confusion, ask.
2. **Simplicity first** — "Is this the minimum that solves the problem?"
3. **Surgical changes** — Match existing style. Touch only what's requested. Every line traces to the request.
4. **Goal-driven execution** — Transform tasks into verifiable goals. Tests pass before AND after.

### Session Initialization
```bash
skill caveman              # 75% token reduction (auto-active, off with "normal mode")
codegraph status           # Verify index is fresh
skill <skill-name>         # Load task-appropriate skill
```

---

## 6. Validation & Verification

### Health Checks
```bash
curl http://localhost:5000/api/v1/health
./venv/bin/python -c "from infrastructure.database import SmartACCTDatabase; print('DB OK')"
./venv/bin/pytest tests/test_vietnamese_formatting.py -v
```

### Architecture Validation
```bash
# Domain layer isolation
./venv/bin/python -c "
from domain.entities import Account, JournalEntry
assert 'app' not in str(Account.__module__)
assert 'app' not in str(JournalEntry.__module__)
print('Domain layer clean')
"

# Infrastructure import check
./venv/bin/python -c "
from infrastructure.database import SmartACCTDatabase
print('Infrastructure imports domain correctly')
"
```

---

## 7. Gotchas & Anti-Patterns

### Gotchas
- **Currency formatting**: `1000000.50` → `1.000.000,50 đ` (VND), `1,000,000.50 ¥` (JPY)
- **DCR Direction**: Commit to memory — wrong direction = invalid entries
- **Connection pooling**: Single manager instance only. No raw `SQLAlchemy()` calls.
- **CodeGraph stale?**: Check the sync banner. Read listed files, trust others.

### What NOT to Do
❌ Create `app/` subdirectory
❌ Bypass domain validation in use_cases
❌ Mix presentation logic with domain logic
❌ Hardcode currency symbols
❌ Skip TDD red-green cycle
❌ Implement without checking applicable skill first
❌ Guess when confused — surface the confusion

---

## 8. Persistent Memory (obsidian-mind)

An [obsidian-mind](https://github.com/breferrari/obsidian-mind) vault is installed at `.obsidian-mind/` for cross-session agent memory. Open it in Obsidian to browse/ edit memories, or use the built-in MCP (`Obsidian Bridge`) for agent-driven reads/writes.

Key vault directories:
- `brain/` — decisions, incidents, patterns, glossary
- `bases/` — domain knowledge bases (VAS, tax law)
- `org/` — North Star goals, team docs, roadmaps
- `perf/` — performance tracking, benchmarks
- `work/` — active tasks, context captures
- `reference/` — external reference materials
- `thinking/` — structured thinking (MOC, debate, first principles)
- `templates/` — note templates

The vault is `.gitignore`d — keep it local to each developer's machine.

---

## 9. Clarifying Questions

When requirements are unclear, ask about:
- Team conventions (contribution process)
- Performance requirements (concurrent users, transaction volume)
- Compliance scope (GST, CIT, PIT, VAT modules)
- Deployment infrastructure (Docker, k8s, AWS/GCP)
- Reporting requirements (Excel vs PDF, SLA deadlines)
