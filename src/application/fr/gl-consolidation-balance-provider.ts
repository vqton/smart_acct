import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";

export interface IntercompanyBalanceProvider {
  getIntercompanyBalances(
    groupId: string,
    fromEntityId: string,
    toEntityId: string,
    fiscalYearId: string,
    periodNumber: number,
  ): Promise<Array<{
    accountCode: string;
    fromDebit: number;
    fromCredit: number;
    toDebit: number;
    toCredit: number;
  }>>;
}

export interface ConsolidationBalanceProvider {
  getEntityBalances(
    legalEntityId: string,
    fiscalYearId: string,
    periodNumber: number,
  ): Promise<Record<string, number>>;
}

@Injectable()
export class GlConsolidationBalanceProvider implements IntercompanyBalanceProvider, ConsolidationBalanceProvider {
  constructor(private readonly prisma: PrismaService) {}

  async getIntercompanyBalances(
    groupId: string,
    fromEntityId: string,
    toEntityId: string,
    fiscalYearId: string,
    periodNumber: number,
  ): Promise<Array<{
    accountCode: string;
    fromDebit: number;
    fromCredit: number;
    toDebit: number;
    toCredit: number;
  }>> {
    return [];
  }

  async getEntityBalances(
    legalEntityId: string,
    fiscalYearId: string,
    periodNumber: number,
  ): Promise<Record<string, number>> {
    const batches = await this.prisma.journalBatch.findMany({
      where: {
        fiscalYearId,
        status: "posted",
        period: { periodNumber },
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
