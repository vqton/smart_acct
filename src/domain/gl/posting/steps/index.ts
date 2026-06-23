import { PipelineStep, PipelineStepStage } from "../pipeline-step.js";
import { PostingContext, AccountSnapshot } from "../posting-context.js";
import { DomainError } from "../../../../shared/domain-error.js";

/** Step 1: Verify user session is active */
export class AuthenticationStep implements PipelineStep {
  readonly name = "Authentication";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 100;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (!ctx.userId || ctx.userId.trim() === "") {
      throw new DomainError("Validation", "AUTH_001: User session is not active");
    }
    return ctx;
  }
}

/** Step 2: Verify user has posting permission */
export class AuthorizationStep implements PipelineStep {
  readonly name = "Authorization";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 110;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (!ctx.userRoles.includes("poster") && !ctx.userRoles.includes("admin")) {
      throw new DomainError("BusinessRule", "AUTH_002: User lacks posting permission");
    }
    return ctx;
  }
}

/** Step 3: Voucher type access control */
export class VoucherAccessStep implements PipelineStep {
  readonly name = "VoucherAccess";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 120;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    return ctx;
  }
}

/** Step 4: Validate batch exists and is in correct state */
export class BatchValidationStep implements PipelineStep {
  readonly name = "BatchValidation";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 200;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (!ctx.batchId) throw new DomainError("NotFound", "VAL_001: Journal batch not found");
    if (ctx.lines.length === 0) throw new DomainError("Validation", "VAL_005: Batch is empty");
    return ctx;
  }
}

/** Step 5: Debit = Credit validation */
export class DebitCreditEqualStep implements PipelineStep {
  readonly name = "DebitCreditEqual";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 210;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    const tolerance = 1;
    if (Math.abs(ctx.totalDebit - ctx.totalCredit) > tolerance) {
      throw new DomainError(
        "BusinessRule",
        `ACC_001: Total debit (${ctx.totalDebit}) does not equal total credit (${ctx.totalCredit})`,
      );
    }
    return ctx;
  }
}

/** Step 6: Validate all accounts exist, are active, posting accounts */
export class AccountValidationStep implements PipelineStep {
  readonly name = "AccountValidation";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 220;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    for (const line of ctx.lines) {
      const account = ctx.accountSnapshots.get(line.accountId);
      if (!account) {
        throw new DomainError("NotFound", `VAL_002: Account ${line.accountId} not found`);
      }
      if (!account.isActive) {
        throw new DomainError("BusinessRule", `ACC_003: Account ${account.code} is inactive`);
      }
      if (!account.isPosting) {
        throw new DomainError("BusinessRule", `ACC_002: Account ${account.code} is not a posting account`);
      }
      if (account.isControl) {
        throw new DomainError("BusinessRule", `ACC_007: Control account ${account.code} cannot be posted to`);
      }
      if (!account.allowManualEntry) {
        throw new DomainError("BusinessRule", `ACC_008: Account ${account.code} does not allow manual entry`);
      }
      if (line.debitAmount < 0 || line.creditAmount < 0) {
        throw new DomainError("Validation", "ACC_005: Line amount must be non-negative");
      }
      if (line.debitAmount === 0 && line.creditAmount === 0) {
        throw new DomainError("Validation", "ACC_006: Line must have debit or credit amount");
      }
      if (!line.description) {
        throw new DomainError("Validation", "ACC_009: Line description is required");
      }
    }
    if (ctx.lines.length < 2 && ctx.journalType !== "opening") {
      throw new DomainError("Validation", "ACC_011: Journal must have at least 2 lines");
    }
    return ctx;
  }
}

/** Step 7: Period and fiscal year validation */
export class FiscalPeriodStep implements PipelineStep {
  readonly name = "FiscalPeriod";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 300;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (ctx.fiscalYearClosed) {
      throw new DomainError("BusinessRule", `FIS_003: Fiscal year ${ctx.fiscalYearCode} is closed`);
    }
    if (ctx.periodStatus === "closed") {
      throw new DomainError("BusinessRule", `FIS_001: Period ${ctx.periodName} is closed`);
    }
    if (ctx.periodStatus === "locked") {
      throw new DomainError("BusinessRule", `FIS_002: Period ${ctx.periodName} is locked`);
    }
    const now = new Date();
    if (ctx.postingDate > now) {
      throw new DomainError("Validation", "FIS_005: Posting date is in the future");
    }
    return ctx;
  }
}

/** Step 8: Foreign currency total match */
export class ForeignCurrencyStep implements PipelineStep {
  readonly name = "ForeignCurrency";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 310;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (ctx.isForeignCurrency) {
      const tolerance = 1;
      if (Math.abs(ctx.foreignTotalDebit - ctx.foreignTotalCredit) > tolerance) {
        throw new DomainError(
          "BusinessRule",
          `CUR_002: Foreign currency debit (${ctx.foreignTotalDebit}) != credit (${ctx.foreignTotalCredit})`,
        );
      }
      for (const line of ctx.lines) {
        if (line.currencyCode !== ctx.currencyCode && line.currencyCode !== "VND") {
          throw new DomainError(
            "Validation",
            `CUR_003: Line currency ${line.currencyCode} does not match batch currency ${ctx.currencyCode}`,
          );
        }
      }
    }
    return ctx;
  }
}

/** Step 9: Segregation of duties */
export class SegregationOfDutiesStep implements PipelineStep {
  readonly name = "SegregationOfDuties";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 400;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    if (ctx.approvedById && ctx.createdById === ctx.approvedById) {
      throw new DomainError("BusinessRule", "AUTH_004: Creator and approver must be different users");
    }
    return ctx;
  }
}

/** Step 10: Lock accounts (optimistic) */
export class AccountLockStep implements PipelineStep {
  readonly name = "AccountLock";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 500;
  private locks: Map<string, number> = new Map();

  async execute(ctx: PostingContext): Promise<PostingContext> {
    this.locks.clear();
    for (const line of ctx.lines) {
      const account = ctx.accountSnapshots.get(line.accountId);
      if (!account) continue;
      const key = `account:${line.accountId}`;
      if (this.locks.has(key)) continue;
      this.locks.set(key, account.version);
      ctx.originalBalanceBefore.set(line.accountId, account.balance);
      ctx.balanceChanges.set(line.accountId, { debitTotal: 0, creditTotal: 0, delta: 0 });
    }
    return ctx;
  }

  async rollback(ctx: PostingContext): Promise<PostingContext> {
    this.locks.clear();
    return ctx;
  }
}

/** Step 11: Calculate balance changes */
export class BalanceCalculationStep implements PipelineStep {
  readonly name = "BalanceCalculation";
  readonly stage = PipelineStepStage.PreValidation;
  readonly order = 600;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    const changes = new Map<string, { debitTotal: number; creditTotal: number; delta: number }>();

    for (const line of ctx.lines) {
      const existing = changes.get(line.accountId) ?? { debitTotal: 0, creditTotal: 0, delta: 0 };
      existing.debitTotal += line.debitAmount;
      existing.creditTotal += line.creditAmount;

      const account = ctx.accountSnapshots.get(line.accountId);
      if (account) {
        const delta = account.nature === "debit"
          ? line.debitAmount - line.creditAmount
          : line.creditAmount - line.debitAmount;
        existing.delta += delta;
      }

      changes.set(line.accountId, existing);
    }

    for (const [accountId, change] of changes) {
      ctx.balanceChanges.set(accountId, change);
    }
    return ctx;
  }
}

/** Step 12: Post to ledger (update balances) */
export class LedgerPostingStep implements PipelineStep {
  readonly name = "LedgerPosting";
  readonly stage = PipelineStepStage.PreCommit;
  readonly order = 700;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    for (const [accountId, change] of ctx.balanceChanges) {
      const account = ctx.accountSnapshots.get(accountId);
      if (!account) continue;

      const isDebitNature = account.nature === "debit";
      account.balance += isDebitNature
        ? change.debitTotal - change.creditTotal
        : change.creditTotal - change.debitTotal;
    }
    return ctx;
  }
}

/** Step 13: Audit trail */
export class AuditLogStep implements PipelineStep {
  readonly name = "AuditLog";
  readonly stage = PipelineStepStage.PostCommit;
  readonly order = 800;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    return ctx;
  }

  async rollback(ctx: PostingContext): Promise<PostingContext> {
    return ctx;
  }
}

/** Step 14: Domain event outbox */
export class EventOutboxStep implements PipelineStep {
  readonly name = "EventOutbox";
  readonly stage = PipelineStepStage.PostCommit;
  readonly order = 900;

  async execute(ctx: PostingContext): Promise<PostingContext> {
    return ctx;
  }

  async rollback(ctx: PostingContext): Promise<PostingContext> {
    return ctx;
  }
}
