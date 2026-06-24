# smart_acct

## Stack

- TypeScript, single package (non-monorepo).
- Runtime: Node.js 20+.
- Web framework: **NestJS 11** (Express platform). Old Express 5 code fully removed.
- ORM: **Prisma 7** with `@prisma/adapter-mariadb` (driver adapter).
- Schema: per-module files in `prisma/schemas/` (14 files, <1.6k lines each). Configured via `prisma.config.ts`.
- Money: `decimal.js` (via `Money` value object in `src/domain/shared/money.ts`).
- Validation: `class-validator` + `class-transformer`.
- API docs: Swagger/OpenAPI at `/api/docs`.
- Test: Vitest.
- DB: MariaDB 11.4 (InnoDB).

## Commands

```sh
npm run dev           # dev server with hot reload (tsx watch src/main.ts)
npm start             # run compiled dist/main.js
npm run build         # tsc compile
npm test              # vitest
npm run lint          # tsc --noEmit
npm run prisma:gen    # regenerate Prisma client
npm run seed          # seed VAS reference data (prisma/seed.ts)
npm run codegraph:sync   # incremental codegraph update
npm run codegraph:status # codegraph index stats
# headroom: see Headroom section below
```

## App entrypoint

- `src/main.ts` — NestJS bootstrap (Swagger + ValidationPipe + CORS).
- `src/app.module.ts` — root module, imports `PrismaModule`, `GlModule`, `TaxModule`, `CoaModule`.
- DDD structure: `domain/`, `application/`, `infrastructure/`, `presentation/`.

## Skill selection

See [docs/skill-decisions.md](docs/skill-decisions.md) for a 4W-H (What/Why/When/Where/How) decision tree mapping task types to the right skill.

Quick reference:
- Bug → `/diagnose`
- Feature → `/to-issues` → `/tdd` per slice
- Architecture → `/improve-codebase-architecture`
- Unclear → `/grill-with-docs` or `/grill-me`
- First time in area → `/zoom-out`
- Triage → `/triage`
- Edit prose → `/edit-article`

## Notes

- Dependencies are added by editing `package.json` and running `npm install`.
- MariaDB is required for the app to start. Run `docker compose up -d db` or start local MariaDB, then `npm run seed` for reference data.

## CodeGraph

[CodeGraph](https://github.com/colbymchenry/codegraph) pre-indexes the codebase for AI agents. It runs as an MCP server (configured in `opencode.json`) and auto-syncs on file changes.

- `codegraph status` — check index health
- `codegraph sync` — force incremental sync
- `codegraph explore <query>` — semantic code search
- `codegraph context <task>` — build AI context
- `codegraph callers <symbol>` — find callers
- `codegraph callees <symbol>` — find callees
- `codegraph impact <symbol>` — blast radius analysis

The graph lives in `.codegraph/` (gitignored db). Auto-rebuilt via `postinstall` script.

## Headroom

[Headroom](https://github.com/headroomlabs-ai/headroom) compresses tool outputs, logs, files, and RAG chunks before they reach the LLM (60-95% fewer tokens). Runs as a local proxy, MCP server, or inline library.

- `headroom wrap opencode` — one-command setup: starts proxy + injects provider + registers MCP
- `headroom unwrap opencode` — reverts wrap, restores config backup
- `headroom proxy --port 8787` — standalone proxy (zero code changes)
- `headroom perf` — benchmark compression on current session

**Setup options:**
1. **Docker** (recommended): `docker compose up -d headroom` — runs proxy on :8787
2. **Local install**: `pip install "headroom-ai[proxy]"` then `headroom proxy --port 8787`
3. **Wrap**: `headroom wrap opencode` — auto-configures everything

The proxy is configured as an MCP server in `opencode.json` (provides `headroom_compress`, `headroom_retrieve`, `headroom_stats` tools). The TypeScript SDK is available as `headroom-ai` (npm) for programmatic use.

## Progress (as of Jun 24, 2026)

### Done
- **GL Domain + Application + Pipeline:** Full 14-step posting pipeline, BalanceEngine, IdempotencyEngine, AuditEngine (SHA-256), QueueEngine, RollbackEngine. 29 metadata rules. 40+ typed error codes. 20 domain events.
- **GL NestJS rewrite:** `PrismaAccountRepository`, `PrismaJournalBatchRepository`, `PrismaFiscalYearRepository`, `PrismaPeriodRepository` + controllers (account CRUD, journal create/submit/approve/post/reverse, period/FY management). Swagger docs at `/api/docs`. All 26 routes mapped.
- **Tax NestJS rewrite:** `PrismaTaxTypeRepository`, `PrismaTaxCodeRepository`, `PrismaTaxRateRepository`, `PrismaTaxAuthorityRepository`, `PrismaTaxRegionRepository`, `PrismaTaxRegistrationRepository`, `PrismaTaxReturnRepository`, `PrismaTaxExemptionRepository`, `PrismaTaxPaymentRepository`, `PrismaTaxDeterminationRuleRepository` + controller (26 routes for types/codes/authorities/regions/registrations/returns/exemptions/payments/calculation).
- **Prisma 7 migration:** Adapter-based client (`@prisma/adapter-mariadb`), `prisma.config.ts`, generator output to `src/generated/prisma/`.
- **Critical fixes applied:** Account code validation expanded to `/^\d{1,7}$/` (TT 99 compliance). `DEBIT_EPSILON` removed — strict Nợ=Có enforcement.
- **Money value object:** `src/domain/shared/money.ts` wraps `Decimal` for precise arithmetic.
- **Docker Compose:** `docker-compose.yml` + `Dockerfile` + `.env.example`.
- **Old Express code removed:** All Express 5 handlers, middleware, old application services, old infrastructure (mariadb/in-memory), old tests, and `main-express.ts` deleted.
- **COA Module (Enterprise Chart of Accounts):** Full domain model (AccountClass, AccountType, AccountMapping, AccountExtension), 4 aggregate roots with domain events, specification pattern validators (PostingAccountSpec, ActiveStatusSpec, EffectiveDateSpec, hierarchy cycle detection), Prisma schema with 7 new tables + audit trail tables, 4 Prisma repositories, CoaService, 4 REST controllers (classes, types, mappings, extensions), 29 new tests.
- **Bank Module (Enterprise Bank Management):** Full domain model (35 enums, 30 identifiers, 20+ domain events, 12 VOs, 9 aggregates: BankGroup/Bank/Branch/Correspondent, BankAccount, BankTransaction, BankStatement, BankReconciliation, PaymentRequest/Batch/Recurring, CashPosition/Forecast/FX, ApprovalMatrix/Request), 15 business rule specifications, 20+ repository interfaces, 25 Prisma models (bnk_ prefix), 21 Prisma repository implementations, 3 application services (master, account, transaction), 1 REST controller (bank-master.controller.ts) with 50+ routes, DTOs with class-validator + Swagger, BankModule registered in AppModule. 106 bank tests pass.

- **Costing Module (Enterprise Costing Engine):** 40+ Prisma models (`cst_` prefix), full domain layer (9 aggregates: CostVersion/WorkCenter/Bom/ProductionOrder/CostPool/AllocationRule/OverheadRate/CostSnapshot/ProductionVariance), 15 IDs, 20+ domain events, DDD value objects, 9 repository interfaces, 9 Prisma repository implementations, 3 application services (CostingEngine, AllocationEngine, PeriodClose), 1 REST controller (25+ routes), CstModule registered in AppModule. Prisma client regenerated, `tsc --noEmit` clean, 566 tests pass.
- **Budget Module (Enterprise Budget Management):** 26 Prisma models (`bgt_` prefix), 17 enums, 9 aggregates (BudgetPlan/Version/Detail/Scenario/Forecast/Allocation/Control/Reservation/Transfer/Approval/Snapshot), 20+ domain events, 12 repository interfaces, 12 Prisma repository implementations, 5 application services (BudgetEngine/ForecastEngine/AllocationEngine/ControlEngine/ApprovalEngine), 1 REST controller (60+ routes), BudgetModule registered in AppModule. `tsc --noEmit` clean.
- **Prisma schema split:** Monolithic 10,248-line `schema.prisma` → 14 per-module files in `prisma/schemas/`. Each file <1.6k lines. Configured via `prisma.config.ts` (`schema: prisma/schemas/`).

### Pending
- Full Money integration across domain entities (currently at repo boundary).
- Auth module (RBAC).
- COA import/export (Excel/CSV/JSON) bulk APIs.
- Controller Swagger verification (manual endpoint review).
- Inventory accounting GL posting integration (GR/IR, COGS accrual, revaluation journals).
- Costing domain tests.
- CONTEXT.md handoff doc.

### Stats
- 69 test files, 566 tests, all passing. `tsc --noEmit` clean.
- Inventory: 17 Prisma models (inv_ prefix), 8 Prisma repos, 1 application service, 1 controller (50+ routes), 33 domain tests.
- Costing: 19 Prisma models (cst_ prefix), 9 Prisma repos, 3 application services, 1 controller (25+ routes).
