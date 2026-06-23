import {
  AccountRepository,
  JournalBatchRepository,
  PeriodRepository,
  FiscalYearRepository,
  CostCenterRepository,
  DepartmentRepository,
  BudgetRepository,
} from "../../domain/gl/repositories.js";
import { AccountNature } from "../../domain/gl/account-category.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { FiscalYearId } from "../../domain/gl/period.js";
import { CostCenterId, DepartmentId } from "../../domain/gl/dimension.js";
import { JournalEntryStatus } from "../../domain/gl/journal.js";

export interface TrialBalanceRow {
  accountId: string;
  accountCode: string;
  accountName: string;
  category: string;
  nature: string;
  openingDebit: number;
  openingCredit: number;
  periodDebit: number;
  periodCredit: number;
  closingDebit: number;
  closingCredit: number;
}

export interface BalanceSheetItem {
  category: string;
  accountCode: string;
  accountName: string;
  balance: number;
}

export interface IncomeStatementItem {
  accountCode: string;
  accountName: string;
  revenue: number;
  expense: number;
}

export interface GeneralLedgerEntry {
  postDate: string;
  voucherNumber: string;
  description: string;
  debitAmount: number;
  creditAmount: number;
  balance: number;
}

export interface DimensionAnalysis {
  dimensionId: string;
  dimensionCode: string;
  dimensionName: string;
  totalDebit: number;
  totalCredit: number;
  balance: number;
}

export class ReportingService {
  constructor(
    private readonly accountRepo: AccountRepository,
    private readonly batchRepo: JournalBatchRepository,
    private readonly periodRepo: PeriodRepository,
    private readonly fiscalYearRepo: FiscalYearRepository,
    private readonly costCenterRepo: CostCenterRepository,
    private readonly deptRepo: DepartmentRepository,
    private readonly budgetRepo: BudgetRepository,
  ) {}

  async getTrialBalance(
    fiscalYearId: string,
    periodNumber?: number,
    asOfDate?: string,
  ): Promise<TrialBalanceRow[]> {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(fiscalYearId));
    if (!fy) throw new Error("Fiscal year not found");

    const periods = await this.periodRepo.findByFiscalYear(fiscalYearId);
    let targetPeriods = periods;
    if (periodNumber) {
      targetPeriods = periods.filter(p => p.periodNumber <= periodNumber);
    }

    const periodIds = targetPeriods.map(p => p.id.value);
    const allBatches: any[] = [];

    for (const pid of periodIds) {
      const batches = await this.batchRepo.findByPeriod(pid);
      allBatches.push(...batches.filter(b => b.status === JournalEntryStatus.Posted));
    }

    const accounts = await this.accountRepo.findAll();
    const periodDebit = new Map<string, number>();
    const periodCredit = new Map<string, number>();

    for (const batch of allBatches) {
      for (const line of batch.lines) {
        periodDebit.set(line.accountId, (periodDebit.get(line.accountId) ?? 0) + line.debitAmount);
        periodCredit.set(line.accountId, (periodCredit.get(line.accountId) ?? 0) + line.creditAmount);
      }
    }

    const rows: TrialBalanceRow[] = [];
    for (const account of accounts) {
      const pDebit = periodDebit.get(account.id.value) ?? 0;
      const pCredit = periodCredit.get(account.id.value) ?? 0;

      let openingDebit = 0;
      let openingCredit = 0;

      if (account.nature === AccountNature.Debit) {
        openingDebit = account.balance - (pDebit - pCredit);
      } else {
        openingCredit = account.balance - (pCredit - pDebit);
      }

      if (openingDebit < 0) { openingCredit += Math.abs(openingDebit); openingDebit = 0; }
      if (openingCredit < 0) { openingDebit += Math.abs(openingCredit); openingCredit = 0; }

      const closingBalance = account.balance;
      let closingDebit = 0;
      let closingCredit = 0;
      if (account.nature === AccountNature.Debit) {
        closingDebit = closingBalance;
      } else {
        closingCredit = closingBalance;
      }

      rows.push({
        accountId: account.id.value,
        accountCode: account.code,
        accountName: account.name,
        category: account.category,
        nature: account.nature,
        openingDebit, openingCredit,
        periodDebit: pDebit, periodCredit: pCredit,
        closingDebit, closingCredit,
      });
    }

    return rows;
  }

  async getGeneralLedger(
    accountId: string,
    fromDate: string,
    toDate: string,
  ): Promise<GeneralLedgerEntry[]> {
    const batches = await this.batchRepo.findByAccountId(
      accountId,
      new Date(fromDate),
      new Date(toDate),
    );

    const account = await this.accountRepo.findById(new AccountId(accountId));
    if (!account) throw new Error("Account not found");

    let runningBalance = 0;
    const entries: GeneralLedgerEntry[] = [];

    for (const batch of batches.sort((a, b) => a.postingDate.getTime() - b.postingDate.getTime())) {
      for (const line of batch.lines) {
        if (line.accountId !== accountId) continue;

        if (account.nature === AccountNature.Debit) {
          runningBalance += line.debitAmount - line.creditAmount;
        } else {
          runningBalance += line.creditAmount - line.debitAmount;
        }

        entries.push({
          postDate: batch.postingDate.toISOString().split("T")[0],
          voucherNumber: batch.batchNumber,
          description: line.description ?? batch.description,
          debitAmount: line.debitAmount,
          creditAmount: line.creditAmount,
          balance: runningBalance,
        });
      }
    }

    return entries;
  }

  async getBalanceSheet(fiscalYearId: string, asOfDate?: string): Promise<BalanceSheetItem[]> {
    const trialBalance = await this.getTrialBalance(fiscalYearId, undefined, asOfDate);
    const items: BalanceSheetItem[] = [];

    const assetCategories = ["short_term_asset", "long_term_asset"];
    const liabilityCategories = ["short_term_liability", "long_term_liability"];
    const equityCategories = ["equity"];

    const addCategory = (categories: string[], section: string) => {
      for (const row of trialBalance) {
        if (categories.includes(row.category)) {
          items.push({
            category: section,
            accountCode: row.accountCode,
            accountName: row.accountName,
            balance: row.closingDebit - row.closingCredit,
          });
        }
      }
    };

    addCategory(assetCategories, "ASSETS");
    addCategory(liabilityCategories, "LIABILITIES");
    addCategory(equityCategories, "EQUITY");

    return items;
  }

  async getIncomeStatement(fiscalYearId: string): Promise<IncomeStatementItem[]> {
    const trialBalance = await this.getTrialBalance(fiscalYearId);
    const items: IncomeStatementItem[] = [];

    for (const row of trialBalance) {
      if (row.category === "revenue" || row.category === "other_income") {
        items.push({
          accountCode: row.accountCode,
          accountName: row.accountName,
          revenue: row.closingCredit - row.closingDebit,
          expense: 0,
        });
      }
      if (row.category === "operating_expense" || row.category === "cost_of_goods_sold" || row.category === "other_expense") {
        items.push({
          accountCode: row.accountCode,
          accountName: row.accountName,
          revenue: 0,
          expense: row.closingDebit - row.closingCredit,
        });
      }
    }

    return items;
  }

  async getDimensionAnalysis(
    dimensionType: "cost_center" | "department",
    fromDate: string,
    toDate: string,
  ): Promise<DimensionAnalysis[]> {
    const batches = await this.batchRepo.findByDateRange(new Date(fromDate), new Date(toDate));
    const posted = batches.filter(b => b.status === JournalEntryStatus.Posted);

    const analysis = new Map<string, { code: string; name: string; debit: number; credit: number }>();

    for (const batch of posted) {
      for (const line of batch.lines) {
        const dimId = dimensionType === "cost_center" ? line.costCenterId : line.departmentId;
        if (!dimId) continue;

        const existing = analysis.get(dimId) ?? { code: "", name: dimId, debit: 0, credit: 0 };
        existing.debit += line.debitAmount;
        existing.credit += line.creditAmount;
        analysis.set(dimId, existing);
      }
    }

    const results: DimensionAnalysis[] = [];
    for (const [dimId, data] of analysis) {
      let dimCode = "";
      let dimName = "";

      if (dimensionType === "cost_center") {
        const cc = await this.costCenterRepo.findById(new CostCenterId(dimId));
        if (cc) { dimCode = cc.code; dimName = cc.name; }
      } else {
        const dept = await this.deptRepo.findById(new DepartmentId(dimId));
        if (dept) { dimCode = dept.code; dimName = dept.name; }
      }

      results.push({
        dimensionId: dimId,
        dimensionCode: dimCode,
        dimensionName: dimName,
        totalDebit: data.debit,
        totalCredit: data.credit,
        balance: data.debit - data.credit,
      });
    }

    return results;
  }
}
