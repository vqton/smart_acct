import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import type { AccountBalanceProvider } from "./report-engine.js";

@Injectable()
export class GlBalanceProvider implements AccountBalanceProvider {
  constructor(private readonly prisma: PrismaService) {}

  async getAccountBalance(
    accountCode: string,
    fiscalYearId: string,
    periodNumber?: number,
  ): Promise<number> {
    const account = await this.prisma.account.findUnique({ where: { code: accountCode } });
    if (!account) return 0;
    return Number(account.balance);
  }

  async getBudgetAmount(
    accountCode: string,
    fiscalYearId: string,
    periodNumber?: number,
  ): Promise<number> {
    const account = await this.prisma.account.findUnique({ where: { code: accountCode } });
    if (!account) return 0;
    const budgetLine = await this.prisma.budgetLine.findFirst({
      where: {
        accountId: account.id,
        budget: { fiscalYearId },
      },
    });
    if (!budgetLine) return 0;
    const periodKey = `period${periodNumber ?? 1}` as keyof typeof budgetLine;
    return Number(budgetLine[periodKey] ?? 0);
  }

  async getPeriodBalances(
    fiscalYearId: string,
    periodNumber?: number,
  ): Promise<Record<string, number>> {
    const batches = await this.prisma.journalBatch.findMany({
      where: {
        fiscalYearId,
        status: "posted",
        ...(periodNumber ? {
          period: { periodNumber },
        } : {}),
      },
      include: { lines: { include: { account: true } } },
    });

    const balances: Record<string, number> = {};
    for (const batch of batches) {
      for (const line of batch.lines) {
        const code = line.account.code;
        balances[code] = (balances[code] ?? 0) + Number(line.debitAmount) - Number(line.creditAmount);
      }
    }
    return balances;
  }
}
