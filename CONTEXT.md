# smart_acct — System Context

## Stack

- **Runtime:** Node.js 20+ (ESM, TypeScript 5)
- **Framework:** NestJS 11 (Express platform)
- **ORM:** Prisma 7 + `@prisma/adapter-mariadb` (driver adapter)
- **DB:** MariaDB 11.4 (InnoDB)
- **Money:** `decimal.js` via `Money` value object (`src/domain/shared/money.ts`)
- **Validation:** `class-validator` + `class-transformer`
- **API docs:** Swagger/OpenAPI at `/api/docs`
- **Test:** Vitest (~600 tests, 78 files)

## Module Architecture

```
All modules follow Clean Architecture:
  domain/ → application/ → infrastructure/ → presentation/
```

### Module Inventory (14 modules)

| Module | Domain | Models | Routes | State |
|--------|--------|--------|--------|-------|
| Auth | User, Role | 3 | 3 | ✅ New — JWT + RBAC |
| GL | Account, JournalBatch, Period, FiscalYear, Voucher, ExchangeRate | 5 | 26 | ✅ Stable |
| Tax | 10 types (codes, rates, authorities, returns, etc.) | 10 | 26 | ✅ Stable |
| COA | AccountClass, AccountType, Mapping, Extension | 7 | 29 | ✅ Stable |
| CM | CashReceipt, Payment, Box, Bank, Cheque, Advance, Session | 12 | — | 🟡 Domain only |
| Bank | 9 aggregates (account, transaction, statement, reconciliation, etc.) | 25 | 50+ | ✅ Stable |
| Sales | Order, Invoice, Return, Quotation, Customer, Receivable | 10+ | — | 🟡 Domain only |
| Purchasing | Order, Invoice, Contract, GoodsReceipt, Vendor | 8 | — | 🟡 Domain only |
| Inventory | Item, Stock, Transaction, CostLayer, Count, UOM | 11 | 50+ | ✅ Stable |
| PRL | PayrollRun, SalaryComponent, TaxBracket, InsuranceRate | 12 | — | 🟡 Domain only |
| e-Invoice | Invoice, Template, Provider, Signature, Transmission | 10 | — | 🟡 Domain only |
| FR | ReportDefinition, Instance, Consolidation, Ratio | 8 | — | 🟡 Domain only |
| Costing | CostVersion, WorkCenter, BOM, CostPool, Allocation | 15 | 25 | ✅ Controllers |
| Budget | Plan, Version, Detail, Scenario, Forecast, Control, Transfer | 26 | 60+ | ✅ Controllers |

### Module Dependencies

```
Auth → (global guard, no deps)
GL → Prisma (core accounting)
COA → GL (accounts)
Tax → GL (posting)
CM → GL (posting)
Bank → GL (posting)
Sales → GL, Inventory (posting, stock)
Purchasing → GL, Inventory (posting, stock)
Inventory → GL (cost posting)
PRL → GL (payroll posting)
e-Invoice → Sales, Tax
Costing → GL, Inventory
Budget → GL, Costing
FR → All (reporting)
```

## Key Architecture Decisions

### GL Posting Pipeline (14 steps)

```
Authentication → Authorization → Batch Validation → Debit=Credit →
Account Validation → Fiscal Period → Foreign Currency → Segregation of Duties →
Rule Engine → Account Lock → Balance Calculation → Ledger Posting →
Audit Trail → Event Outbox
```

### Money Usage

`Money` value object wraps `decimal.js` with 2-decimal precision. Currently used in:
- ✅ Shared Money class (`src/domain/shared/money.ts`)
- ✅ GL Account entity (balance, foreignBalance)
- ⏳ All other domain entities still use `number` (repo boundary conversion)

**Storage format:** Prisma `BigInt` (exact integer VND, no decimals).
**Repo conversion:** `bigint` → `Money.fromVnd(string)` on read, `Money.toNumber()` → `BigInt` on write.

### Auth System

- JWT-based authentication (Passport strategy)
- Global `JwtAuthGuard` — all routes protected by default
- `@Public()` decorator to bypass auth (login, register)
- `@Roles(...)` decorator for RBAC at endpoint level
- User/Role/UserRole models (3 Prisma tables)
- `@CurrentUser()` param decorator for request user access

## Domain Language (Vietnamese Accounting)

| Term | Meaning |
|------|---------|
| Chứng từ | Voucher / source document |
| Định khoản | Journal entry |
| Bút toán | Posting entry |
| Nợ | Debit |
| Có | Credit |
| Tài khoản | Account (chart of accounts) |
| Kỳ kế toán | Accounting period |
| Năm tài chính | Fiscal year |
| Số dư | Balance |
| Đối ứng | Double-entry matching |

## Integration Points

### GL Posting from Other Modules

Modules post to GL via `JournalBatch` creation through repositories:
- **Sales:** `SalesGlService` creates journal batches for invoices, receipts, credit notes
- **Payroll:** `PrlPayrollJournal` creates journal batches for payroll runs
- **CM/Cash/Bank:** Create journal batches for cash/bank transactions

Pattern:
```
ModuleAggregate → create JournalBatch → persist → post → update Account balances
```

### Key Files to Know

| File | Purpose |
|------|---------|
| `src/main.ts` | Bootstrap, Swagger, CORS, global pipes |
| `src/app.module.ts` | Root module, imports all 14 modules |
| `src/domain/shared/money.ts` | Money value object (decimal.js) |
| `prisma/schemas/` | 14 per-module Prisma schema files |
| `prisma.config.ts` | Prisma configuration (schema dir, adapter) |
| `src/generated/prisma/` | Generated Prisma client (gitignored) |
| `src/prisma/prisma.service.ts` | Prisma client wrapper |

## Known Gaps

- 🐛 7 pre-existing tsc errors in `src/domain/costing/__tests__/` (enum value mismatches)
- ⏳ `Money` integration only in GL Account; 60+ domain entities still use `number`
- ⏳ No per-module `@Roles()` decorators applied (auth guard exists but RBAC not configured per endpoint)
- ⏳ Costing domain tests not written
- ⏳ COA Excel/CSV import/export not implemented
- ⏳ Inventory GL posting (GR/IR, COGS) not integrated
