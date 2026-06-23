import * as crypto from "crypto";

export enum AuditAction {
  PostingStarted = "posting_started",
  BatchValidated = "batch_validated",
  AccountBalancesUpdated = "account_balances_updated",
  PostingCompleted = "posting_completed",
  PostingFailed = "posting_failed",
  BatchReversed = "batch_reversed",
  BatchCancelled = "batch_cancelled",
  PeriodClosed = "period_closed",
  PeriodReopened = "period_reopened",
  FiscalYearClosed = "fiscal_year_closed",
  JournalCreated = "journal_created",
  JournalModified = "journal_modified",
  JournalApproved = "journal_approved",
  JournalSubmitted = "journal_submitted",
  AccountCreated = "account_created",
  AccountModified = "account_modified",
  AccountDeactivated = "account_deactivated",
  BudgetConsumed = "budget_consumed",
  BudgetModified = "budget_modified",
  ExchangeRateApplied = "exchange_rate_applied",
  IdempotencyChecked = "idempotency_checked",
}

export interface AuditRecord {
  id: string;
  action: AuditAction;
  entityType: string;
  entityId: string;
  userId: string;
  timestamp: Date;
  changes: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  previousHash: string;
  hash: string;
  version: number;
}

export interface AuditRepository {
  save(record: AuditRecord): Promise<void>;
  findByEntity(entityType: string, entityId: string): Promise<AuditRecord[]>;
  findByAction(action: AuditAction, from?: Date, to?: Date): Promise<AuditRecord[]>;
  findLatestByEntity(entityType: string, entityId: string): Promise<AuditRecord | null>;
  verifyChain(entityType: string, entityId: string): Promise<boolean>;
}

export class AuditEngine {
  constructor(private auditRepo: AuditRepository) {}

  async record(params: {
    action: AuditAction;
    entityType: string;
    entityId: string;
    userId: string;
    changes?: Record<string, unknown> | null;
    metadata?: Record<string, unknown> | null;
  }): Promise<AuditRecord> {
    const latest = await this.auditRepo.findLatestByEntity(params.entityType, params.entityId);
    const previousHash = latest?.hash ?? "0";
    const version = (latest?.version ?? 0) + 1;

    const record: AuditRecord = {
      id: crypto.randomUUID(),
      action: params.action,
      entityType: params.entityType,
      entityId: params.entityId,
      userId: params.userId,
      timestamp: new Date(),
      changes: params.changes ?? null,
      metadata: params.metadata ?? null,
      previousHash,
      hash: "",
      version,
    };

    record.hash = this.computeHash(record);
    await this.auditRepo.save(record);
    return record;
  }

  async verifyChain(entityType: string, entityId: string): Promise<boolean> {
    return this.auditRepo.verifyChain(entityType, entityId);
  }

  private computeHash(record: Omit<AuditRecord, "hash">): string {
    const data = `${record.id}|${record.action}|${record.entityType}|${record.entityId}|${record.userId}|${record.timestamp.toISOString()}|${JSON.stringify(record.changes)}|${JSON.stringify(record.metadata)}|${record.previousHash}|${record.version}`;
    return crypto.createHash("sha256").update(data).digest("hex");
  }
}
