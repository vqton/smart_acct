# Spec: Financial Statements Module — Phase 1 Production-Ready

## Objective
Take the existing 65-70% complete FS code to **production-quality** — all Phase 1 use cases (B01-DN through B09-DN) working end-to-end with real GL data, proper period validation, accurate subtotal computation, balance sheet verification, and export.

## Commands
```
Test: .venv/bin/python -m pytest tests/test_fs_domain.py tests/test_fs_integration.py -v --tb=short
All : .venv/bin/python -m pytest tests/ -v --tb=short
Lint: .venv/bin/python -m flake8
```

## Success Criteria
1. `POST /api/v1/fs/generate {"period": "2026-06", "statement_type": "B01_DN"}` returns a verifiably correct TT99-compliant balance sheet with all line items, subtotals, and A=L+E identity check
2. Same for B02-DN (income statement) and B03-DN (cash flow)
3. B09-DN auto-populates from B01/B02/B03 data (not just 4 placeholder sections)
4. Period-closed checks block re-generation on locked periods
5. All 3 export formats (HTML/PDF/XLSX) work end-to-end
6. Approval workflow (DRAFT→IN_REVIEW→REVIEWED→APPROVED→SIGNED) works with audit trail
7. Seed migration populates default account mappings

## Gaps to Close

| # | Gap | Fix | Effort |
|---|-----|-----|--------|
| 1 | `is_period_closed` always bypassed (`and False`) | Remove `and False` | 1 line |
| 2 | No period check in B01/B02/B03 path | Add check in `_generate_fs` | 3 lines |
| 3 | B09-DN stub (4 sections only) | Add sections V-XIX, cross-ref B01/B02 data | Medium |
| 4 | B03-DN hardcoded accounts | Keep hardcoded for Phase 1 (Cash module integration deferred) | 0 — WONTFIX |
| 5 | No seed mappings in DB | Add Alembic seed migration with _B01_ACCOUNT_MAP etc. | Small |
| 6 | Template VND formatting basic | Add Jinja2 `vnd_format` filter | Small |
| 7 | No end-to-end GL→FS test | Write integration test with real JE→post→generate→verify | Medium |
| 8 | get_prior_period_fs string compare | Keep for Phase 1 (works for YYYY-MM) | 0 — WONTFIX |

## Implementation Plan

### Slice 1: Fix period validation + add end-to-end B01-DN test
Files: `use_cases/fs/__init__.py`, `tests/test_fs_integration.py`
Deliverable: B01-DN generation with GL data, balance sheet 270==440 verified

### Slice 2: Add seed data migration for account mappings
Files: New migration script
Deliverable: Default B01/B02/B03 mappings in fs_account_mappings table

### Slice 3: Polish B09-DN (auto-populate sections V-XIX)
Files: `use_cases/fs/__init__.py`, templates
Deliverable: B09-DN with 10+ auto-populated sections

### Slice 4: Polish templates + VND formatting
Files: `templates/fs/*.html`
Deliverable: Locale-aware VND formatting, proper TT99 layout

## Coding Standards
- Follow existing i18n pattern (error codes, no hardcoded Vietnamese)
- Type hints everywhere
- All new methods tested
- Match existing code style exactly

## Boundaries
- **Always:** Run tests before/after changes, follow i18n pattern
- **Ask first:** New DB tables, new dependencies, changing existing route signatures
- **Never:** Break existing tests, hardcode strings, skip validation
