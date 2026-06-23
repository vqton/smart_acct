# smart_acct

## Stack

- TypeScript, single package (non-monorepo).
- Runtime: Node.js 20+.
- Web framework: **NestJS 11** (Express platform). Old Express 5 code fully removed.
- ORM: **Prisma 7** with `@prisma/adapter-mariadb` (driver adapter).
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
npm run codegraph:sync   # incremental codegraph update
npm run codegraph:status # codegraph index stats
```

## App entrypoint

- `src/main.ts` — NestJS bootstrap (Swagger + ValidationPipe + CORS).
- `src/app.module.ts` — root module, imports `PrismaModule`, `GlModule`, `TaxModule`.
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

- No database or external services required at this stage.
- Dependencies are added by editing `package.json` and running `npm install`.

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

## Progress (as of Jun 23, 2026)

### Done
- **GL Domain + Application + Pipeline:** Full 14-step posting pipeline, BalanceEngine, IdempotencyEngine, AuditEngine (SHA-256), QueueEngine, RollbackEngine. 29 metadata rules. 40+ typed error codes. 20 domain events.
- **GL NestJS rewrite:** `PrismaAccountRepository`, `PrismaJournalBatchRepository`, `PrismaFiscalYearRepository`, `PrismaPeriodRepository` + controllers (account CRUD, journal create/submit/approve/post/reverse, period/FY management). Swagger docs at `/api/docs`. All 26 routes mapped.
- **Tax NestJS rewrite:** `PrismaTaxTypeRepository`, `PrismaTaxCodeRepository`, `PrismaTaxRateRepository`, `PrismaTaxAuthorityRepository`, `PrismaTaxRegionRepository`, `PrismaTaxRegistrationRepository`, `PrismaTaxReturnRepository`, `PrismaTaxExemptionRepository`, `PrismaTaxPaymentRepository`, `PrismaTaxDeterminationRuleRepository` + controller (26 routes for types/codes/authorities/regions/registrations/returns/exemptions/payments/calculation).
- **Prisma 7 migration:** Adapter-based client (`@prisma/adapter-mariadb`), `prisma.config.ts`, generator output to `src/generated/prisma/`.
- **Critical fixes applied:** Account code validation expanded to `/^\d{1,7}$/` (TT 99 compliance). `DEBIT_EPSILON` removed — strict Nợ=Có enforcement.
- **Money value object:** `src/domain/shared/money.ts` wraps `Decimal` for precise arithmetic.
- **Docker Compose:** `docker-compose.yml` + `Dockerfile` + `.env.example`.
- **Old Express code removed:** All Express 5 handlers, middleware, old application services, old infrastructure (mariadb/in-memory), old tests, and `main-express.ts` deleted.
- **20 test files, 152 tests** — all passing.

### Pending
- Full Money integration across domain entities (currently at repo boundary).
- Auth module (RBAC).
- Actual DB migration (prisma migrate dev).
- Production seed data script.
- CONTEXT.md handoff doc.

### Stats
- 20 test files, 152 tests, all passing. `tsc --noEmit` clean.
