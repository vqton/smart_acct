export enum IdempotencyStatus {
  Pending = "pending",
  Processing = "processing",
  Completed = "completed",
  Failed = "failed",
}

export interface IdempotencyRecord {
  key: string;
  status: IdempotencyStatus;
  result: Record<string, unknown> | null;
  error: string | null;
  createdAt: Date;
  updatedAt: Date;
  expiresAt: Date;
}

export interface IdempotencyRepository {
  save(record: IdempotencyRecord): Promise<void>;
  findByKey(key: string): Promise<IdempotencyRecord | null>;
  updateStatus(key: string, status: IdempotencyStatus, result?: Record<string, unknown>, error?: string): Promise<void>;
  deleteExpired(): Promise<void>;
}

export class IdempotencyEngine {
  constructor(private repo: IdempotencyRepository) {}

  async checkAndLock(key: string, ttlMinutes = 1440): Promise<{ isDuplicate: boolean; existingResult?: Record<string, unknown> }> {
    if (!key) return { isDuplicate: false };

    const existing = await this.repo.findByKey(key);
    if (existing) {
      if (existing.status === IdempotencyStatus.Completed) {
        return { isDuplicate: true, existingResult: existing.result ?? undefined };
      }
      if (existing.status === IdempotencyStatus.Processing) {
        return { isDuplicate: true };
      }
    }

    const record: IdempotencyRecord = {
      key,
      status: IdempotencyStatus.Processing,
      result: null,
      error: null,
      createdAt: new Date(),
      updatedAt: new Date(),
      expiresAt: new Date(Date.now() + ttlMinutes * 60 * 1000),
    };
    await this.repo.save(record);
    return { isDuplicate: false };
  }

  async complete(key: string, result: Record<string, unknown>): Promise<void> {
    await this.repo.updateStatus(key, IdempotencyStatus.Completed, result);
  }

  async fail(key: string, error: string): Promise<void> {
    await this.repo.updateStatus(key, IdempotencyStatus.Failed, undefined, error);
  }

  async cleanup(): Promise<void> {
    await this.repo.deleteExpired();
  }
}
