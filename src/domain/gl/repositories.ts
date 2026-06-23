import { AccountId } from "./account-id.js";
import { Account, AccountState } from "./account.js";
import {
  JournalBatch, JournalBatchId, JournalBatchState,
  JournalEntryStatus, JournalType,
} from "./journal.js";
import { FiscalYear, FiscalYearId, FiscalYearState } from "./period.js";
import { Period, PeriodId, PeriodState } from "./period.js";
import { VoucherType, VoucherTypeId, VoucherTypeState } from "./voucher.js";
import { VoucherSeries, VoucherSeriesId, VoucherSeriesState } from "./voucher.js";
import { ExchangeRate, ExchangeRateId, ExchangeRateState } from "./exchange-rate.js";
import { CostCenter, CostCenterId, CostCenterState } from "./dimension.js";
import { Department, DepartmentId, DepartmentState } from "./dimension.js";
import { Budget, BudgetId, BudgetState } from "./budget.js";

export interface UnitOfWork {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  isActive(): boolean;
}

export interface AccountRepository {
  save(account: Account): Promise<void>;
  findById(id: AccountId): Promise<Account | null>;
  findByCode(code: string): Promise<Account | null>;
  findAll(): Promise<Account[]>;
  findActive(): Promise<Account[]>;
  findPostingAccounts(): Promise<Account[]>;
  findChildren(parentId: string): Promise<Account[]>;
  search(criteria: AccountSearchCriteria): Promise<Account[]>;
  delete(id: AccountId): Promise<void>;
}

export interface AccountSearchCriteria {
  keyword?: string;
  category?: string;
  isActive?: boolean;
  isControl?: boolean;
  parentId?: string | null;
}

export interface JournalBatchRepository {
  save(batch: JournalBatch): Promise<void>;
  findById(id: JournalBatchId): Promise<JournalBatch | null>;
  findByBatchNumber(batchNumber: string): Promise<JournalBatch | null>;
  findByPeriod(periodId: string): Promise<JournalBatch[]>;
  findByStatus(status: JournalEntryStatus): Promise<JournalBatch[]>;
  findByDateRange(from: Date, to: Date): Promise<JournalBatch[]>;
  findByAccountId(accountId: string, from?: Date, to?: Date): Promise<JournalBatch[]>;
  findAll(): Promise<JournalBatch[]>;
  delete(id: JournalBatchId): Promise<void>;
}

export interface FiscalYearRepository {
  save(fiscalYear: FiscalYear): Promise<void>;
  findById(id: FiscalYearId): Promise<FiscalYear | null>;
  findByCode(code: string): Promise<FiscalYear | null>;
  findActive(): Promise<FiscalYear | null>;
  findAll(): Promise<FiscalYear[]>;
  delete(id: FiscalYearId): Promise<void>;
}

export interface PeriodRepository {
  save(period: Period): Promise<void>;
  findById(id: PeriodId): Promise<Period | null>;
  findByFiscalYear(fiscalYearId: string): Promise<Period[]>;
  findOpenByDate(date: Date): Promise<Period | null>;
  findOpen(): Promise<Period[]>;
}

export interface VoucherTypeRepository {
  save(vt: VoucherType): Promise<void>;
  findById(id: VoucherTypeId): Promise<VoucherType | null>;
  findByCode(code: string): Promise<VoucherType | null>;
  findAll(): Promise<VoucherType[]>;
  findActive(): Promise<VoucherType[]>;
}

export interface VoucherSeriesRepository {
  save(vs: VoucherSeries): Promise<void>;
  findById(id: VoucherSeriesId): Promise<VoucherSeries | null>;
  findByCode(code: string): Promise<VoucherSeries | null>;
  findByVoucherType(voucherTypeId: string): Promise<VoucherSeries[]>;
  findActive(): Promise<VoucherSeries[]>;
  findNextSequence(voucherTypeId: string, fiscalYearId?: string): Promise<VoucherSeries | null>;
}

export interface ExchangeRateRepository {
  save(rate: ExchangeRate): Promise<void>;
  findById(id: ExchangeRateId): Promise<ExchangeRate | null>;
  findRate(fromCurrency: string, toCurrency: string, date: Date): Promise<ExchangeRate | null>;
  findRatesByDate(date: Date): Promise<ExchangeRate[]>;
  findAll(): Promise<ExchangeRate[]>;
}

export interface CostCenterRepository {
  save(cc: CostCenter): Promise<void>;
  findById(id: CostCenterId): Promise<CostCenter | null>;
  findByCode(code: string): Promise<CostCenter | null>;
  findAll(): Promise<CostCenter[]>;
  findActive(): Promise<CostCenter[]>;
}

export interface DepartmentRepository {
  save(dept: Department): Promise<void>;
  findById(id: DepartmentId): Promise<Department | null>;
  findByCode(code: string): Promise<Department | null>;
  findAll(): Promise<Department[]>;
  findActive(): Promise<Department[]>;
}

export interface BudgetRepository {
  save(budget: Budget): Promise<void>;
  findById(id: BudgetId): Promise<Budget | null>;
  findByFiscalYear(fiscalYearId: string): Promise<Budget[]>;
  findByCostCenter(costCenterId: string): Promise<Budget[]>;
  findByAccountAndPeriod(accountId: string, fiscalYearId: string): Promise<Budget | null>;
  findAll(): Promise<Budget[]>;
}
