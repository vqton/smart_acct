export enum QueuePriority {
  High = 10,
  Normal = 5,
  Low = 1,
}

export enum QueueStatus {
  Queued = "queued",
  Processing = "processing",
  Completed = "completed",
  Failed = "failed",
  Retrying = "retrying",
  DeadLetter = "dead_letter",
}

export interface QueueItem {
  id: string;
  batchId: string;
  userId: string;
  priority: QueuePriority;
  status: QueueStatus;
  retryCount: number;
  maxRetries: number;
  errorMessage: string | null;
  idempotencyKey: string | null;
  queuedAt: Date;
  startedAt: Date | null;
  completedAt: Date | null;
  nextRetryAt: Date | null;
}

export interface QueueRepository {
  enqueue(item: QueueItem): Promise<void>;
  dequeue(): Promise<QueueItem | null>;
  updateStatus(id: string, status: QueueStatus, error?: string): Promise<void>;
  findById(id: string): Promise<QueueItem | null>;
  findPending(): Promise<QueueItem[]>;
  findFailed(): Promise<QueueItem[]>;
  moveToDeadLetter(id: string, error: string): Promise<void>;
}

export class QueueEngine {
  private processing = false;
  private activeJobs = new Set<string>();

  constructor(
    private queueRepo: QueueRepository,
    private processor: (item: QueueItem) => Promise<void>,
    private concurrency = 3,
  ) {}

  async enqueue(batchId: string, userId: string, options?: {
    priority?: QueuePriority;
    idempotencyKey?: string;
    maxRetries?: number;
  }): Promise<string> {
    const item: QueueItem = {
      id: crypto.randomUUID(),
      batchId,
      userId,
      priority: options?.priority ?? QueuePriority.Normal,
      status: QueueStatus.Queued,
      retryCount: 0,
      maxRetries: options?.maxRetries ?? 3,
      errorMessage: null,
      idempotencyKey: options?.idempotencyKey ?? null,
      queuedAt: new Date(),
      startedAt: null,
      completedAt: null,
      nextRetryAt: null,
    };
    await this.queueRepo.enqueue(item);
    return item.id;
  }

  async start(): Promise<void> {
    this.processing = true;
    while (this.processing) {
      if (this.activeJobs.size >= this.concurrency) {
        await new Promise(r => setTimeout(r, 100));
        continue;
      }
      const item = await this.queueRepo.dequeue();
      if (!item) {
        await new Promise(r => setTimeout(r, 500));
        continue;
      }
      this.activeJobs.add(item.id);
      this.processItem(item).finally(() => this.activeJobs.delete(item.id));
    }
  }

  stop(): void {
    this.processing = false;
  }

  private async processItem(item: QueueItem): Promise<void> {
    try {
      await this.queueRepo.updateStatus(item.id, QueueStatus.Processing);
      await this.processor(item);
      await this.queueRepo.updateStatus(item.id, QueueStatus.Completed);
    } catch (error) {
      const errMsg = (error as Error).message;
      if (item.retryCount < item.maxRetries) {
        const backoffMs = Math.pow(2, item.retryCount) * 1000;
        await this.queueRepo.updateStatus(item.id, QueueStatus.Retrying, errMsg);
        item.retryCount++;
        item.nextRetryAt = new Date(Date.now() + backoffMs);
        setTimeout(() => {
          this.queueRepo.enqueue(item).catch(console.error);
        }, backoffMs);
      } else {
        await this.queueRepo.moveToDeadLetter(item.id, errMsg);
      }
    }
  }
}
