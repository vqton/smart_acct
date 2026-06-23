import * as crypto from "crypto";
import { AccountId } from "../../../domain/gl/account-id.js";
import { Account } from "../../../domain/gl/account.js";
import { JournalBatch, JournalType, JournalEntryStatus } from "../../../domain/gl/journal.js";
import { AccountRepository, JournalBatchRepository, UnitOfWork } from "../../../domain/gl/repositories.js";
import { createPostingError } from "../../../domain/gl/errors/error-catalogue.js";
import { PostingContext } from "../../../domain/gl/posting/posting-context.js";

export enum RollbackStrategy {
  FullReversal = "full_reversal",
  SelectiveCorrection = "selective_correction",
  StornoReversal = "storno_reversal",
  RedEntry = "red_entry",
}

export class RollbackEngine {
  constructor(
    private accountRepo: AccountRepository,
    private journalBatchRepo: JournalBatchRepository,
    private uow: UnitOfWork,
  ) {}

  async restoreAccountBalances(ctx: PostingContext): Promise<void> {
    await this.uow.begin();
    try {
      for (const [accountId, change] of ctx.balanceChanges) {
        const account = await this.accountRepo.findById(new AccountId(accountId));
        if (!account) continue;

        account.updateBalance(-change.debitTotal, -change.creditTotal);
        await this.accountRepo.save(account);
      }
      await this.uow.commit();
    } catch (error) {
      await this.uow.rollback();
      throw createPostingError("INF_002", { details: `Rollback failed: ${(error as Error).message}` });
    }
  }

  async createReversalBatch(
    originalBatch: JournalBatch,
    userId: string,
    reversalDate: Date,
    strategy: RollbackStrategy = RollbackStrategy.FullReversal,
  ): Promise<JournalBatch> {
    if (originalBatch.status !== JournalEntryStatus.Posted) {
      throw createPostingError("VAL_006");
    }

    const reverseBatch = JournalBatch.create({
      batchNumber: `REV-${originalBatch.batchNumber}-${Date.now()}`,
      journalType: JournalType.Reversing,
      periodId: originalBatch.periodId,
      fiscalYearId: originalBatch.fiscalYearId,
      voucherDate: reversalDate,
      postingDate: reversalDate,
      description: `${strategy === RollbackStrategy.StornoReversal ? "Storno" : "Reverse"} of ${originalBatch.batchNumber}`,
      createdById: userId,
      reference: originalBatch.batchNumber,
    });

    for (const line of originalBatch.lines) {
      if (strategy === RollbackStrategy.StornoReversal) {
        reverseBatch.addLine({
          accountId: line.accountId,
          debitAmount: line.creditAmount,
          creditAmount: line.debitAmount,
          foreignDebitAmount: line.foreignCreditAmount,
          foreignCreditAmount: line.foreignDebitAmount,
          currencyCode: line.currencyCode,
          exchangeRate: line.exchangeRate,
          description: `Storno: ${line.description}`,
          costCenterId: line.costCenterId,
          departmentId: line.departmentId,
          projectId: line.projectId,
        });
      } else {
        reverseBatch.addLine({
          accountId: line.accountId,
          debitAmount: line.creditAmount,
          creditAmount: line.debitAmount,
          foreignDebitAmount: line.foreignCreditAmount,
          foreignCreditAmount: line.foreignDebitAmount,
          currencyCode: line.currencyCode,
          exchangeRate: line.exchangeRate,
          description: `Reverse: ${line.description}`,
          costCenterId: line.costCenterId,
          departmentId: line.departmentId,
          projectId: line.projectId,
        });
      }
    }

    reverseBatch.submit();
    reverseBatch.approve(userId);
    reverseBatch.post(userId);
    return reverseBatch;
  }
}

export interface RecoveryCheckpoint {
  id: string;
  batchId: string;
  stepName: string;
  contextSnapshot: string;
  createdAt: Date;
}

export class RecoveryEngine {
  private checkpoints: RecoveryCheckpoint[] = [];

  async saveCheckpoint(batchId: string, stepName: string, ctx: PostingContext): Promise<RecoveryCheckpoint> {
    const cp: RecoveryCheckpoint = {
      id: crypto.randomUUID(),
      batchId,
      stepName,
      contextSnapshot: JSON.stringify({
        batchId: ctx.batchId,
        state: ctx.state,
        balanceChanges: Array.from(ctx.balanceChanges.entries()),
        originalBalances: Array.from(ctx.originalBalanceBefore.entries()),
      }),
      createdAt: new Date(),
    };
    this.checkpoints.push(cp);
    return cp;
  }

  getCheckpoints(batchId: string): RecoveryCheckpoint[] {
    return this.checkpoints.filter(c => c.batchId === batchId);
  }

  getLastCheckpoint(batchId: string): RecoveryCheckpoint | undefined {
    const cps = this.getCheckpoints(batchId);
    return cps.length > 0 ? cps[cps.length - 1] : undefined;
  }

  clearCheckpoints(batchId: string): void {
    this.checkpoints = this.checkpoints.filter(c => c.batchId !== batchId);
  }
}
