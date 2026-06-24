import { Injectable } from "@nestjs/common";
import { GlBalanceProvider } from "./gl-balance-provider.js";

export interface TrialBalanceRow {
  accountCode: string;
  accountName: string;
  openingDebit: number;
  openingCredit: number;
  periodDebit: number;
  periodCredit: number;
  closingDebit: number;
  closingCredit: number;
}

export interface BalanceSheetSection {
  section: string;
  items: Array<{ accountCode: string; accountName: string; balance: number }>;
  total: number;
}

export interface IncomeStatementSection {
  section: string;
  items: Array<{ accountCode: string; accountName: string; amount: number }>;
  total: number;
}

export interface CashFlowItem {
  itemCode: string;
  itemName: string;
  amount: number;
  children?: CashFlowItem[];
}

const ACCOUNT_CLASS_1_PREFIX = ["1"];
const ACCOUNT_CLASS_2_PREFIX = ["2"];
const ACCOUNT_CLASS_3_PREFIX = ["3"];
const ACCOUNT_CLASS_4_PREFIX = ["4"];
const ACCOUNT_CLASS_5_PREFIX = ["5"];
const ACCOUNT_CLASS_6_PREFIX = ["6"];
const ACCOUNT_CLASS_7_PREFIX = ["7"];

@Injectable()
export class FinancialStatementService {
  constructor(private readonly balanceProvider: GlBalanceProvider) {}

  async getTrialBalance(
    fiscalYearId: string,
    periodNumber?: number,
    allAccounts?: Array<{ code: string; name: string; nature: string; category: string }>,
  ): Promise<TrialBalanceRow[]> {
    const balances = await this.balanceProvider.getPeriodBalances(fiscalYearId, periodNumber);
    const accounts = allAccounts ?? [];

    return accounts.map(a => {
      const balance = balances[a.code] ?? 0;
      const isDebit = a.nature === "debit";

      return {
        accountCode: a.code,
        accountName: a.name,
        openingDebit: isDebit ? balance : 0,
        openingCredit: !isDebit ? balance : 0,
        periodDebit: isDebit ? balance : 0,
        periodCredit: !isDebit ? balance : 0,
        closingDebit: isDebit ? balance : 0,
        closingCredit: !isDebit ? balance : 0,
      };
    });
  }

  async getBalanceSheet(
    fiscalYearId: string,
    periodNumber?: number,
    allAccounts?: Array<{ code: string; name: string; nature: string; category: string }>,
  ): Promise<{ sections: BalanceSheetSection[]; totalAssets: number; totalLiabilities: number; totalEquity: number }> {
    const balances = await this.balanceProvider.getPeriodBalances(fiscalYearId, periodNumber);
    const accounts = allAccounts ?? [];

    const shortTermAssets = this.filterAccounts(accounts, ["short_term_asset"], balances);
    const longTermAssets = this.filterAccounts(accounts, ["long_term_asset"], balances);
    const shortTermLiabilities = this.filterAccounts(accounts, ["short_term_liability"], balances);
    const longTermLiabilities = this.filterAccounts(accounts, ["long_term_liability"], balances);
    const equityItems = this.filterAccounts(accounts, ["equity"], balances);

    const totalAssets = shortTermAssets.total + longTermAssets.total;
    const totalLiabilities = shortTermLiabilities.total + longTermLiabilities.total;
    const totalEquity = equityItems.total;

    return {
      sections: [
        { section: "SHORT_TERM_ASSETS", items: shortTermAssets.items, total: shortTermAssets.total },
        { section: "LONG_TERM_ASSETS", items: longTermAssets.items, total: longTermAssets.total },
        { section: "SHORT_TERM_LIABILITIES", items: shortTermLiabilities.items, total: shortTermLiabilities.total },
        { section: "LONG_TERM_LIABILITIES", items: longTermLiabilities.items, total: longTermLiabilities.total },
        { section: "EQUITY", items: equityItems.items, total: equityItems.total },
      ],
      totalAssets,
      totalLiabilities,
      totalEquity,
    };
  }

  async getIncomeStatement(
    fiscalYearId: string,
    periodNumber?: number,
    allAccounts?: Array<{ code: string; name: string; nature: string; category: string }>,
  ): Promise<{ sections: IncomeStatementSection[]; totalRevenue: number; totalExpense: number; netProfit: number }> {
    const balances = await this.balanceProvider.getPeriodBalances(fiscalYearId, periodNumber);
    const accounts = allAccounts ?? [];

    const revenue = this.filterAccounts(accounts, ["revenue", "other_income"], balances);
    const cogs = this.filterAccounts(accounts, ["cost_of_goods_sold"], balances);
    const expenses = this.filterAccounts(accounts, ["operating_expense", "other_expense"], balances);

    const totalRevenue = revenue.total;
    const totalExpense = cogs.total + expenses.total;
    const netProfit = totalRevenue - totalExpense;

    const mapItems = (items: Array<{ accountCode: string; accountName: string; balance: number }>) =>
      items.map(i => ({ accountCode: i.accountCode, accountName: i.accountName, amount: i.balance }));

    return {
      sections: [
        { section: "REVENUE", items: mapItems(revenue.items), total: revenue.total },
        { section: "COST_OF_GOODS_SOLD", items: mapItems(cogs.items), total: cogs.total },
        { section: "OPERATING_EXPENSES", items: mapItems(expenses.items), total: expenses.total },
      ],
      totalRevenue,
      totalExpense,
      netProfit,
    };
  }

  async getCashFlow(
    fiscalYearId: string,
    periodNumber?: number,
    allAccounts?: Array<{ code: string; name: string; nature: string; category: string }>,
  ): Promise<{ operating: CashFlowItem[]; investing: CashFlowItem[]; financing: CashFlowItem[] }> {
    const balances = await this.balanceProvider.getPeriodBalances(fiscalYearId, periodNumber);
    const accounts = allAccounts ?? [];

    const operatingCodes = this.getAccountsByPrefix(accounts, ACCOUNT_CLASS_4_PREFIX.concat(ACCOUNT_CLASS_5_PREFIX, ACCOUNT_CLASS_6_PREFIX));
    const investingCodes = this.getAccountsByPrefix(accounts, ACCOUNT_CLASS_2_PREFIX);
    const financingCodes = this.getAccountsByPrefix(accounts, ACCOUNT_CLASS_3_PREFIX);

    return {
      operating: this.buildCashFlowItems(operatingCodes, balances),
      investing: this.buildCashFlowItems(investingCodes, balances),
      financing: this.buildCashFlowItems(financingCodes, balances),
    };
  }

  private filterAccounts(
    accounts: Array<{ code: string; name: string; nature: string; category: string }>,
    categories: string[],
    balances: Record<string, number>,
  ): { items: Array<{ accountCode: string; accountName: string; balance: number }>; total: number } {
    const filtered = accounts.filter(a => categories.includes(a.category));
    const items = filtered.map(a => ({
      accountCode: a.code,
      accountName: a.name,
      balance: balances[a.code] ?? 0,
    }));
    const total = items.reduce((s, i) => s + i.balance, 0);
    return { items, total };
  }

  private getAccountsByPrefix(
    accounts: Array<{ code: string; name: string; nature: string; category: string }>,
    prefixes: string[],
  ): Array<{ code: string; name: string }> {
    return accounts.filter(a => prefixes.some(p => a.code.startsWith(p)));
  }

  private buildCashFlowItems(
    accounts: Array<{ code: string; name: string }>,
    balances: Record<string, number>,
  ): CashFlowItem[] {
    return accounts.map(a => ({
      itemCode: a.code,
      itemName: a.name,
      amount: balances[a.code] ?? 0,
    }));
  }
}
