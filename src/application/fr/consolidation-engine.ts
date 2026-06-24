import { Injectable } from "@nestjs/common";
import type {
  ConsolidationGroupRepository,
  ConsolidationRunRepository,
} from "../../domain/fr/fr-repositories.js";
import { ConsolidationRun, ConsolidationGroup, type ConsolidationGroupState, type ConsolidationRunState } from "../../domain/fr/fr-consolidation.js";
import { ConsolidationEliminationEntry, type ConsolidationGroupMember } from "../../domain/fr/fr-value-objects.js";
import { FrConsolidationMethod, FrEliminationType, FrConsolidationStatus } from "../../domain/fr/fr-enums.js";
import { DomainError } from "../../shared/domain-error.js";
import { GlConsolidationBalanceProvider, type IntercompanyBalanceProvider, type ConsolidationBalanceProvider } from "./gl-consolidation-balance-provider.js";

@Injectable()
export class ConsolidationEngine {
  constructor(
    private readonly groupRepo: ConsolidationGroupRepository,
    private readonly runRepo: ConsolidationRunRepository,
    private readonly balanceProvider: GlConsolidationBalanceProvider,
  ) {}

  async createRun(params: {
    groupId: string;
    fiscalYearId: string;
    periodId?: string;
    periodNumber: number;
    periodName: string;
    asOfDate: Date;
    preparedById: string;
  }): Promise<ConsolidationRunState> {
    const group = await this.groupRepo.findById(params.groupId as any);
    if (!group) throw new DomainError("NotFound", "Consolidation group not found");
    if (!group.isActive) throw new DomainError("BusinessRule", "Inactive consolidation group");

    const existingRun = await this.runRepo.findByPeriod(
      params.groupId,
      params.fiscalYearId,
      params.periodNumber,
    );
    if (existingRun) throw new DomainError("Conflict", "Run already exists for this period");

    const run = ConsolidationRun.create({
      ...params,
      runNumber: `CONS-${params.groupId.slice(0, 8)}-${params.fiscalYearId.slice(0, 8)}-P${params.periodNumber}`,
    });

    await this.runRepo.save(run);
    return run.toState();
  }

  async generateEntries(runId: string): Promise<void> {
    const run = await this.runRepo.findById(runId as any);
    if (!run) throw new DomainError("NotFound", "Consolidation run not found");

    const group = await this.groupRepo.findById(run.groupId as any);
    if (!group) throw new DomainError("NotFound", "Consolidation group not found");

    for (const member of group.members) {
      if (!member.isActive) continue;
      await this.generateMemberEntries(run, group, member);
    }

    run.complete();
    await this.runRepo.save(run);
  }

  getIntercompanyBalances: GlConsolidationBalanceProvider["getIntercompanyBalances"] =
    (...args) => this.balanceProvider.getIntercompanyBalances(...args);

  getEntityBalances: GlConsolidationBalanceProvider["getEntityBalances"] =
    (...args) => this.balanceProvider.getEntityBalances(...args);

  private async generateMemberEntries(
    run: ConsolidationRun,
    group: ConsolidationGroup,
    member: ConsolidationGroupMember,
  ): Promise<void> {
    if (member.consolidationMethod === FrConsolidationMethod.Full) {
      if (member.ownershipPercentage < 1) {
        const minorityInterest = await this.calculateMinorityInterest(run, member);
        if (minorityInterest > 0) {
          run.addEntry(new ConsolidationEliminationEntry(
            FrEliminationType.MinorityInterest,
            member.legalEntityId,
            null,
            "MINORITY_INTEREST",
            0,
            minorityInterest,
            `MI for ${member.legalEntityCode} @ ${(member.ownershipPercentage * 100).toFixed(1)}%`,
            true,
            null,
          ));
        }
      }

      const icBalances = await this.balanceProvider.getIntercompanyBalances(
        group.id.value,
        group.parentCompanyId,
        member.legalEntityId,
        run.fiscalYearId,
        run.periodNumber,
      );

      for (const ic of icBalances) {
        if (ic.fromDebit !== ic.toCredit || ic.fromCredit !== ic.toDebit) {
          throw new DomainError("BusinessRule",
            `Unmatched intercompany balance for ${ic.accountCode}: ` +
            `${member.legalEntityCode}`,
          );
        }

        if (ic.fromDebit > 0) {
          run.addEntry(new ConsolidationEliminationEntry(
            FrEliminationType.IntercompanyReceivable,
            group.parentCompanyId,
            member.legalEntityId,
            ic.accountCode,
            ic.fromDebit,
            0,
            `IC elimination: ${member.legalEntityCode}`,
            true,
            null,
          ));
          run.addEntry(new ConsolidationEliminationEntry(
            FrEliminationType.IntercompanyPayable,
            member.legalEntityId,
            group.parentCompanyId,
            ic.accountCode,
            0,
            ic.fromDebit,
            `IC elimination: ${member.legalEntityCode}`,
            true,
            null,
          ));
        }

        if (ic.fromCredit > 0) {
          run.addEntry(new ConsolidationEliminationEntry(
            FrEliminationType.IntercompanyRevenue,
            group.parentCompanyId,
            member.legalEntityId,
            ic.accountCode,
            ic.fromCredit,
            0,
            `IC revenue elimination: ${member.legalEntityCode}`,
            true,
            null,
          ));
          run.addEntry(new ConsolidationEliminationEntry(
            FrEliminationType.IntercompanyExpense,
            member.legalEntityId,
            group.parentCompanyId,
            ic.accountCode,
            0,
            ic.fromCredit,
            `IC expense elimination: ${member.legalEntityCode}`,
            true,
            null,
          ));
        }
      }
    }
  }

  private async calculateMinorityInterest(
    run: ConsolidationRun,
    member: ConsolidationGroupMember,
  ): Promise<number> {
    const balances = await this.balanceProvider.getEntityBalances(
      member.legalEntityId,
      run.fiscalYearId,
      run.periodNumber,
    );

    const equityBalances = ["3", "4"];
    let totalEquity = 0;
    for (const [code, balance] of Object.entries(balances)) {
      if (equityBalances.some(p => code.startsWith(p))) {
        totalEquity += balance;
      }
    }

    const minorityShare = (1 - member.ownershipPercentage) * totalEquity;
    return Math.max(0, minorityShare);
  }

  async getConsolidatedBalances(
    groupId: string,
    fiscalYearId: string,
    periodNumber: number,
  ): Promise<Record<string, number>> {
    const group = await this.groupRepo.findById(groupId as any);
    if (!group) throw new DomainError("NotFound", "Consolidation group not found");

    const consolidated: Record<string, number> = {};

    for (const member of group.members) {
      if (!member.isActive) continue;
      const balances = await this.balanceProvider.getEntityBalances(
        member.legalEntityId,
        fiscalYearId,
        periodNumber,
      );

      const ownership = member.consolidationMethod === FrConsolidationMethod.Equity
        ? member.ownershipPercentage : 1;

      for (const [code, balance] of Object.entries(balances)) {
        consolidated[code] = (consolidated[code] ?? 0) + balance * ownership;
      }
    }

    const latestRun = await this.runRepo.findByPeriod(groupId, fiscalYearId, periodNumber);
    if (latestRun && latestRun.status === FrConsolidationStatus.Approved) {
      for (const entry of latestRun.entries) {
        const accountCode = entry.accountCode;
        consolidated[accountCode] = (consolidated[accountCode] ?? 0)
          + entry.debitAmount - entry.creditAmount;
      }
    }

    return consolidated;
  }
}
