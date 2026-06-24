import { Injectable } from "@nestjs/common";
import { GlBalanceProvider } from "./gl-balance-provider.js";

export interface FinancialRatioResult {
  code: string;
  name: string;
  value: number;
  category: string;
  benchmark: number | null;
  status: "good" | "warning" | "critical" | "unknown";
  unit: string;
}

@Injectable()
export class AnalyticsService {
  constructor(private readonly balanceProvider: GlBalanceProvider) {}

  async calculateRatios(
    fiscalYearId: string,
    periodNumber?: number,
    accounts?: Array<{ code: string; name: string; nature: string; category: string }>,
  ): Promise<FinancialRatioResult[]> {
    const balances = await this.balanceProvider.getPeriodBalances(fiscalYearId, periodNumber);
    const act = accounts ?? [];

    const currentAssets = this.sumByCategory(act, balances, ["short_term_asset"]);
    const currentLiabilities = this.sumByCategory(act, balances, ["short_term_liability"]);
    const totalAssets = this.sumByCategory(act, balances, ["short_term_asset", "long_term_asset"]);
    const totalLiabilities = this.sumByCategory(act, balances, ["short_term_liability", "long_term_liability"]);
    const totalEquity = this.sumByCategory(act, balances, ["equity"]);
    const revenue = this.sumByCategory(act, balances, ["revenue", "other_income"]);
    const expenses = this.sumByCategory(act, balances, ["operating_expense", "other_expense", "cost_of_goods_sold"]);
    const netProfit = revenue - expenses;
    const cashAndBank = this.sumByPrefix(act, balances, ["11"]);

    return [
      this.makeRatio("CR", "Current Ratio", currentAssets / (currentLiabilities || 1), "liquidity", 2.0, "times"),
      this.makeRatio("QR", "Quick Ratio", (currentAssets) / (currentLiabilities || 1), "liquidity", 1.0, "times"),
      this.makeRatio("NPM", "Net Profit Margin", (revenue > 0 ? netProfit / revenue : 0) * 100, "profitability", 10, "%"),
      this.makeRatio("ROA", "Return on Assets", (totalAssets > 0 ? netProfit / totalAssets : 0) * 100, "profitability", 5, "%"),
      this.makeRatio("ROE", "Return on Equity", (totalEquity > 0 ? netProfit / totalEquity : 0) * 100, "profitability", 15, "%"),
      this.makeRatio("DER", "Debt to Equity", totalEquity > 0 ? totalLiabilities / totalEquity : 0, "leverage", 2.0, "times"),
      this.makeRatio("AR", "Asset Turnover", totalAssets > 0 ? revenue / totalAssets : 0, "efficiency", 1.5, "times"),
      this.makeRatio("CFR", "Cash Ratio", cashAndBank / (currentLiabilities || 1), "liquidity", 0.5, "times"),
    ];
  }

  async trendAnalysis(
    fiscalYearId: string,
    periods: number[],
    accountCodes: string[],
  ): Promise<Record<string, number[]>> {
    const result: Record<string, number[]> = {};
    for (const code of accountCodes) {
      result[code] = [];
      for (const period of periods) {
        const balance = await this.balanceProvider.getAccountBalance(code, fiscalYearId, period);
        result[code].push(balance);
      }
    }
    return result;
  }

  async budgetVariance(
    fiscalYearId: string,
    periodNumber: number,
    actualBalances: Record<string, number>,
    budgetBalances: Record<string, number>,
  ): Promise<Array<{
    accountCode: string;
    actual: number;
    budget: number;
    variance: number;
    variancePercent: number;
  }>> {
    const results: Array<{
      accountCode: string;
      actual: number;
      budget: number;
      variance: number;
      variancePercent: number;
    }> = [];

    for (const [code, actual] of Object.entries(actualBalances)) {
      const budget = budgetBalances[code] ?? 0;
      results.push({
        accountCode: code,
        actual,
        budget,
        variance: actual - budget,
        variancePercent: budget > 0 ? ((actual - budget) / budget) * 100 : 0,
      });
    }

    return results;
  }

  private sumByCategory(
    accounts: Array<{ code: string; category: string }>,
    balances: Record<string, number>,
    categories: string[],
  ): number {
    return accounts
      .filter(a => categories.includes(a.category))
      .reduce((sum, a) => sum + (balances[a.code] ?? 0), 0);
  }

  private sumByPrefix(
    accounts: Array<{ code: string }>,
    balances: Record<string, number>,
    prefixes: string[],
  ): number {
    return accounts
      .filter(a => prefixes.some(p => a.code.startsWith(p)))
      .reduce((sum, a) => sum + (balances[a.code] ?? 0), 0);
  }

  private makeRatio(
    code: string,
    name: string,
    value: number,
    category: string,
    benchmark: number | null,
    unit: string,
  ): FinancialRatioResult {
    let status: FinancialRatioResult["status"] = "unknown";
    if (benchmark !== null) {
      const ratio = value / benchmark;
      status = ratio >= 0.8 ? "good" : ratio >= 0.5 ? "warning" : "critical";
    }
    return { code, name, value: Math.round(value * 100) / 100, category, benchmark, status, unit };
  }
}
