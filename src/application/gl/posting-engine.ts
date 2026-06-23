import { DomainError } from "../../shared/domain-error.js";
import { Account } from "../../domain/gl/account.js";
import { AccountId } from "../../domain/gl/account-id.js";
import {
  JournalBatch, JournalBatchId, JournalEntryStatus, JournalType,
} from "../../domain/gl/journal.js";
import { Period, PeriodId, FiscalYearId, FiscalYear } from "../../domain/gl/period.js";
import {
  AccountRepository, JournalBatchRepository, PeriodRepository,
  FiscalYearRepository, ExchangeRateRepository, UnitOfWork,
} from "../../domain/gl/repositories.js";
import { RuleEngine } from "../../domain/gl/rules/rule-engine.js";
import { RuleCategory } from "../../domain/gl/rules/posting-rule.js";
import { PostingPipeline } from "../../domain/gl/posting/posting-pipeline.js";
import { PostingContext, createPostingContext } from "../../domain/gl/posting/posting-context.js";
import {
  AuthenticationStep, AuthorizationStep, BatchValidationStep,
  DebitCreditEqualStep, AccountValidationStep, FiscalPeriodStep,
  ForeignCurrencyStep, SegregationOfDutiesStep, AccountLockStep,
  BalanceCalculationStep, LedgerPostingStep, AuditLogStep, EventOutboxStep,
} from "../../domain/gl/posting/steps/index.js";
import { BalanceEngine } from "./services/balance-engine.js";
import { IdempotencyEngine } from "./services/idempotency-engine.js";
import { AuditEngine, AuditAction } from "./services/audit-engine.js";
import { RollbackEngine, RollbackStrategy, RecoveryEngine } from "./services/rollback-engine.js";
import { createPostingError } from "../../domain/gl/errors/error-catalogue.js";

export interface PostingResult {
  batchId: string;
  batchNumber: string;
  postedAt: Date;
  totalDebit: number;
  totalCredit: number;
  lineCount: number;
  error?: string;
  idempotencyReplay?: boolean;
}

export interface PostingValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface PostingOptions {
  idempotencyKey?: string;
  bypassValidation?: boolean;
  asyncPost?: boolean;
  priority?: number;
}

export class PostingEngine {
  private pipeline: PostingPipeline;
  private rollbackEngine: RollbackEngine;
  private recoveryEngine: RecoveryEngine;

  constructor(
    private readonly accountRepo: AccountRepository,
    private readonly journalBatchRepo: JournalBatchRepository,
    private readonly periodRepo: PeriodRepository,
    private readonly fiscalYearRepo: FiscalYearRepository,
    private readonly exchangeRateRepo: ExchangeRateRepository,
    private readonly uow: UnitOfWork,
    private readonly ruleEngine?: RuleEngine,
    private readonly balanceEngine?: BalanceEngine,
    private readonly idempotencyEngine?: IdempotencyEngine,
    private readonly auditEngine?: AuditEngine,
  ) {
    this.rollbackEngine = new RollbackEngine(accountRepo, journalBatchRepo, uow);
    this.recoveryEngine = new RecoveryEngine();
    this.pipeline = new PostingPipeline(this.ruleEngine ?? new RuleEngine({
      findAll: async () => [],
      findByCategory: async () => [],
      findByJournalType: async () => [],
      findByCategoriesAndJournal: async () => [],
      save: async () => {},
    }));

    this.pipeline.addSteps([
      new AuthenticationStep(),
      new AuthorizationStep(),
      new BatchValidationStep(),
      new DebitCreditEqualStep(),
      new AccountValidationStep(),
      new FiscalPeriodStep(),
      new ForeignCurrencyStep(),
      new SegregationOfDutiesStep(),
      new AccountLockStep(),
      new BalanceCalculationStep(),
      new LedgerPostingStep(),
      new AuditLogStep(),
      new EventOutboxStep(),
    ]);
  }

  async validate(batchId: string): Promise<PostingValidation> {
    const errors: string[] = [];
    const warnings: string[] = [];

    const batch = await this.journalBatchRepo.findById(new JournalBatchId(batchId));
    if (!batch) return { isValid: false, errors: ["Batch not found"], warnings: [] };

    try {
      batch.validateDebitCreditEqual();
    } catch (e) {
      errors.push((e as Error).message);
    }

    for (const line of batch.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) {
        errors.push(`Account ${line.accountId} not found`);
        continue;
      }
      try {
        account.canPost();
      } catch (e) {
        errors.push(`Account ${account.code}: ${(e as Error).message}`);
      }
    }

    const period = await this.periodRepo.findById(new PeriodId(batch.periodId));
    if (!period) {
      errors.push("Period not found");
    } else {
      try { period.canPost(); } catch (e) { errors.push(`Period ${period.name}: ${(e as Error).message}`); }
    }

    return { isValid: errors.length === 0, errors, warnings };
  }

  async post(batchId: string, userId: string, options?: PostingOptions): Promise<PostingResult> {
    const idempotencyKey = options?.idempotencyKey;

    if (this.idempotencyEngine && idempotencyKey) {
      const { isDuplicate, existingResult } = await this.idempotencyEngine.checkAndLock(idempotencyKey);
      if (isDuplicate && existingResult) {
        return {
          ...existingResult as unknown as PostingResult,
          idempotencyReplay: true,
        };
      }
    }

    const batch = await this.journalBatchRepo.findById(new JournalBatchId(batchId));
    if (!batch) throw createPostingError("VAL_001");

    await this.auditEngine?.record({
      action: AuditAction.PostingStarted,
      entityType: "journal_batch",
      entityId: batchId,
      userId,
      metadata: { batchNumber: batch.batchNumber },
    });

    if (options?.asyncPost) {
      return this.enqueuePost(batch, userId, options);
    }

    return this.executePost(batch, userId, idempotencyKey);
  }

  private async enqueuePost(batch: JournalBatch, userId: string, options: PostingOptions): Promise<PostingResult> {
    return {
      batchId: batch.id.value,
      batchNumber: batch.batchNumber,
      postedAt: new Date(),
      totalDebit: 0,
      totalCredit: 0,
      lineCount: 0,
      error: "Queued for async processing",
    };
  }

  private async executePost(
    batch: JournalBatch, userId: string, idempotencyKey?: string | null,
  ): Promise<PostingResult> {
    const validation = await this.validate(batch.id.value);
    if (!validation.isValid) {
      throw new DomainError("Validation", `Posting validation failed: ${validation.errors.join("; ")}`);
    }

    await this.uow.begin();
    try {
      const period = await this.periodRepo.findById(new PeriodId(batch.periodId));
      const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(batch.fiscalYearId));

      if (!period) throw createPostingError("VAL_003");
      if (!fiscalYear) throw createPostingError("VAL_004");

      const accountSnapshots = new Map<string, {
        id: string; code: string; category: string; nature: string;
        isActive: boolean; isPosting: boolean; isControl: boolean;
        allowManualEntry: boolean; balance: number; foreignBalance: number; version: number;
      }>();

      for (const line of batch.lines) {
        const account = await this.accountRepo.findById(new AccountId(line.accountId));
        if (!account) throw createPostingError("VAL_002", { accountId: line.accountId });
        accountSnapshots.set(line.accountId, {
          id: account.id.value,
          code: account.code,
          category: account.category,
          nature: account.nature,
          isActive: account.isActive,
          isPosting: account.isPosting,
          isControl: account.isControl,
          allowManualEntry: account.allowManualEntry,
          balance: account.balance,
          foreignBalance: account.foreignBalance,
          version: account.version,
        });
      }

      let ctx = createPostingContext({
        batchId: batch.id.value,
        batchNumber: batch.batchNumber,
        journalType: batch.journalType,
        periodId: batch.periodId,
        periodName: period.name,
        fiscalYearId: batch.fiscalYearId,
        fiscalYearCode: fiscalYear.code,
        postingDate: batch.postingDate,
        voucherDate: batch.voucherDate,
        currencyCode: batch.currencyCode,
        exchangeRate: batch.exchangeRate,
        isForeignCurrency: batch.isForeignCurrency,
        totalDebit: batch.totalDebit,
        totalCredit: batch.totalCredit,
        foreignTotalDebit: batch.foreignTotalDebit,
        foreignTotalCredit: batch.foreignTotalCredit,
        description: batch.description,
        reference: batch.reference,
        userId,
        userRoles: ["poster"],
        createdById: batch.createdById,
        approvedById: batch.approvedById,
        idempotencyKey,
        lines: batch.lines.map(l => ({
          id: l.id,
          accountId: l.accountId,
          accountCode: accountSnapshots.get(l.accountId)?.code ?? "",
          debitAmount: l.debitAmount,
          creditAmount: l.creditAmount,
          foreignDebitAmount: l.foreignDebitAmount,
          foreignCreditAmount: l.foreignCreditAmount,
          currencyCode: l.currencyCode,
          exchangeRate: l.exchangeRate,
          description: l.description,
          costCenterId: l.costCenterId,
          departmentId: l.departmentId,
          projectId: l.projectId,
          lineOrder: l.lineOrder,
        })),
        accountSnapshots,
        periodStatus: period.status,
        fiscalYearClosed: fiscalYear.isClosed,
      });

      await this.recoveryEngine.saveCheckpoint(batch.id.value, "context_ready", ctx);

      try {
        ctx = await this.pipeline.execute(ctx);
      } catch (pipelineError) {
        await this.rollbackEngine.restoreAccountBalances(ctx);
        await this.recoveryEngine.saveCheckpoint(batch.id.value, "rolled_back", ctx);

        await this.auditEngine?.record({
          action: AuditAction.PostingFailed,
          entityType: "journal_batch",
          entityId: batch.id.value,
          userId,
          changes: { error: (pipelineError as Error).message },
        });

        await this.uow.rollback();

        if (this.idempotencyEngine && idempotencyKey) {
          await this.idempotencyEngine.fail(idempotencyKey, (pipelineError as Error).message);
        }

        throw pipelineError;
      }

      for (const [accountId, snapshot] of accountSnapshots) {
        const account = await this.accountRepo.findById(new AccountId(accountId));
        if (!account) continue;
        const change = ctx.balanceChanges.get(accountId);
        if (change) {
          account.updateBalance(change.debitTotal, change.creditTotal);
        }
        await this.accountRepo.save(account);

        if (this.balanceEngine) {
          const isDebitNature = snapshot.nature === "debit";
          await this.balanceEngine.updatePeriodBalance(
            accountId, batch.periodId, batch.fiscalYearId,
            change?.debitTotal ?? 0, change?.creditTotal ?? 0,
            0, 0, isDebitNature,
          );
        }
      }

      batch.post(userId);
      await this.journalBatchRepo.save(batch);
      await this.uow.commit();

      await this.auditEngine?.record({
        action: AuditAction.PostingCompleted,
        entityType: "journal_batch",
        entityId: batch.id.value,
        userId,
        changes: {
          totalDebit: batch.totalDebit,
          totalCredit: batch.totalCredit,
          lineCount: batch.lines.length,
        },
      });

      if (this.idempotencyEngine && idempotencyKey) {
        const result: PostingResult = {
          batchId: batch.id.value,
          batchNumber: batch.batchNumber,
          postedAt: new Date(),
          totalDebit: batch.totalDebit,
          totalCredit: batch.totalCredit,
          lineCount: batch.lines.length,
        };
        await this.idempotencyEngine.complete(idempotencyKey, result as unknown as Record<string, unknown>);
      }

      return {
        batchId: batch.id.value,
        batchNumber: batch.batchNumber,
        postedAt: new Date(),
        totalDebit: batch.totalDebit,
        totalCredit: batch.totalCredit,
        lineCount: batch.lines.length,
      };
    } catch (error) {
      await this.uow.rollback().catch(() => {});
      throw error;
    }
  }

  async batchPost(batchIds: string[], userId: string, options?: PostingOptions): Promise<PostingResult[]> {
    const results: PostingResult[] = [];
    for (const batchId of batchIds) {
      try {
        const result = await this.post(batchId, userId, options);
        results.push(result);
      } catch (error) {
        results.push({
          batchId,
          batchNumber: "",
          postedAt: new Date(),
          totalDebit: 0,
          totalCredit: 0,
          lineCount: 0,
          error: (error as Error).message,
        });
      }
    }
    return results;
  }

  async reverseBatch(
    batchId: string, userId: string, description: string,
    strategy: RollbackStrategy = RollbackStrategy.FullReversal,
  ): Promise<PostingResult> {
    await this.uow.begin();
    try {
      const originalBatch = await this.journalBatchRepo.findById(new JournalBatchId(batchId));
      if (!originalBatch) throw createPostingError("VAL_001");
      if (originalBatch.status !== JournalEntryStatus.Posted) {
        throw new DomainError("BusinessRule", "Only posted batches can be reversed");
      }

      const period = await this.periodRepo.findById(new PeriodId(originalBatch.periodId));
      if (!period) throw createPostingError("VAL_003");
      period.canPost();

      const reverseBatch = await this.rollbackEngine.createReversalBatch(
        originalBatch, userId, new Date(), strategy,
      );
      await this.journalBatchRepo.save(reverseBatch);

      for (const line of reverseBatch.lines) {
        const account = await this.accountRepo.findById(new AccountId(line.accountId));
        if (!account) continue;
        account.updateBalance(line.debitAmount, line.creditAmount);
        await this.accountRepo.save(account);
      }

      originalBatch.reverse(reverseBatch.batchNumber);
      await this.journalBatchRepo.save(originalBatch);

      await this.auditEngine?.record({
        action: AuditAction.BatchReversed,
        entityType: "journal_batch",
        entityId: batchId,
        userId,
        changes: { strategy, reversalBatchNumber: reverseBatch.batchNumber },
      });

      await this.uow.commit();

      return {
        batchId: reverseBatch.id.value,
        batchNumber: reverseBatch.batchNumber,
        postedAt: reverseBatch.postedAt!,
        totalDebit: reverseBatch.totalDebit,
        totalCredit: reverseBatch.totalCredit,
        lineCount: reverseBatch.lines.length,
      };
    } catch (error) {
      await this.uow.rollback();
      throw error;
    }
  }
}
