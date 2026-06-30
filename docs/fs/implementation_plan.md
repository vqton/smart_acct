# FS Module — Implementation Plan

**Phase 1 MVP**: 8 weeks | **Phase 2**: 4 weeks | **Phase 3**: 4 weeks  
**Total**: ~16 weeks to full PROD

---

## Phase 1 — MVP (Weeks 1-8)

### Week 1: Domain + Data Model

| Task | Files | Tests |
|------|-------|-------|
| Create `domain/fs.py`: FS entities, enums, FSLineItem, FinancialStatement, FSAuditLog, FSAccountMapping | `domain/fs.py` | `tests/test_fs_domain.py` (25 tests) |
| Create FS models: `infrastructure/models/fs_models.py` (6 tables) | `infrastructure/models/fs_models.py` | Manual |
| Create Alembic migration | `migrations/versions/` | Verify |
| Define FS i18n error codes in `domain/i18n.py` | `domain/i18n.py` | None |

### Week 2: GL-to-FS Mapping

| Task | Files | Tests |
|------|-------|-------|
| FSAccountMapping CRUD repository | `infrastructure/repositories/fs_repository.py` | 10 tests |
| GL-to-FS account map use case | `use_cases/fs/__init__.py` | 8 tests |
| Default mapping per TT99 account types | Seed data | Manual |
| Mapping routes | `presentation/fs/routes.py` | 4 tests |

### Week 3-4: FS Generation Engine (B01-DN + B02-DN)

| Task | Files | Tests |
|------|-------|-------|
| Trial balance query by account type | `infrastructure/repositories/fs_repository.py` | 5 tests |
| B01-DN generation logic | `use_cases/fs/__init__.py` | 15 tests |
| B02-DN generation logic | `use_cases/fs/__init__.py` | 10 tests |
| Balance sheet verification | `use_cases/fs/__init__.py` | 5 tests |
| Comparative period population | `use_cases/fs/__init__.py` | 3 tests |

### Week 5: B03-DN + B09-DN Generation

| Task | Files | Tests |
|------|-------|-------|
| Cash flow direct method | `use_cases/fs/__init__.py` | 8 tests |
| Cash flow indirect method | `use_cases/fs/__init__.py` | 8 tests |
| Cross-statement verification | `use_cases/fs/__init__.py` | 5 tests |
| B09-DN auto-population | `use_cases/fs/__init__.py` | 8 tests |

### Week 6: FS CRUD + Routes

| Task | Files | Tests |
|------|-------|-------|
| FS CRUD repository | `infrastructure/repositories/fs_repository.py` | 8 tests |
| FS use cases (create, list, get, version) | `use_cases/fs/__init__.py` | 5 tests |
| FS routes (basic CRUD) | `presentation/fs/routes.py` | 8 tests |
| FS generation endpoint | `presentation/fs/routes.py` | 4 tests |

### Week 7: Approval Workflow + Export

| Task | Files | Tests |
|------|-------|-------|
| Approval state machine | `use_cases/fs/__init__.py` | 10 tests |
| FS audit log | `infrastructure/repositories/fs_repository.py` | 3 tests |
| WebTemplate-based HTML templates for B01/B02/B03/B09 | `templates/fs/*.html` | Manual |
| PDF generation (WeasyPrint) | `use_cases/fs/__init__.py` | 3 tests |
| Excel export (openpyxl) | `use_cases/fs/__init__.py` | 2 tests |

### Week 8: Testing + Integration + Bug Fixes

| Task | Tests |
|------|-------|
| Integration tests (all FS endpoints) | 30 tests |
| Edge case tests | 20 tests |
| Cross-module integration (GL→FS, Cash→FS) | 10 tests |
| Performance test (10K GL lines → FS) | Manual |

### Phase 1 Test Target: 83 unit + 50 integration + 30 edge = 163 tests

---

## Phase 2 — Enhancement (Weeks 9-12)

| Week | Task | Tests |
|------|------|-------|
| 9 | DNKLT templates + generation | 15 |
| 10 | Interim reports (full + condensed) | 15 |
| 11 | Multi-entity consolidation engine | 20 |
| 12 | Financial ratios + Excel polish | 10 |
| **Total** | | **60** |

---

## Phase 3 — Advanced (Weeks 13-16)

| Week | Task | Tests |
|------|------|-------|
| 13 | IFRS 18 convergence + MPM disclosure | 15 |
| 14 | e-Submission GDT integration | 10 |
| 15 | XBRL export | 8 |
| 16 | FS dashboard + final integration testing | 12 |
| **Total** | | **45** |

---

## File Creation Order

```
1. domain/fs.py                          # Domain entities
2. domain/i18n.py                        # Add FS error codes
3. infrastructure/models/fs_models.py   # DB models
4. migrations/versions/                  # Migration
5. infrastructure/repositories/fs_repository.py  # Repository
6. use_cases/fs/__init__.py              # Use cases
7. use_cases/fs_use_cases.py             # Shim
8. presentation/fs/__init__.py           # Blueprint
9. presentation/fs/routes.py             # Routes
10. templates/fs/                        # Report templates
11. tests/test_fs_domain.py              # Domain tests
12. tests/test_fs_integration.py         # Integration tests
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| TT99 interpretation ambiguity | Medium | High | Cross-reference with VACPA guidelines |
| GL data quality issues | Medium | High | Data validation before FS generation |
| Performance with large GL | Low | Medium | Indexed queries, caching |
| PDF layout compliance | Medium | Medium | Automated visual comparison tests |
| Consolidation complexity | High | High | Start with simple ownership structures |

---

## Key Design Decisions

1. **JSONB for FS data**: Store full FS line items as JSONB in `fs_statements.data` for flexible query + versioning
2. **Separate FS Repository**: Not mixing with GLRepository — FS has distinct query patterns
3. **Template-driven PDF**: Jinja2 + WeasyPrint for TT99-compliant output
4. **Mapping-driven generation**: Configurable COA→FS mapping enables flexible customization
5. **Version as integer + full data copy**: Each version stores complete FS data (not diff) for audit integrity
