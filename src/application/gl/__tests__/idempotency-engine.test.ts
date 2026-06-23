import { describe, it, expect, beforeEach } from "vitest";
import { IdempotencyEngine, IdempotencyStatus, IdempotencyRepository, IdempotencyRecord } from "../services/idempotency-engine.js";

class FakeIdemRepo implements IdempotencyRepository {
  records = new Map<string, IdempotencyRecord>();

  async save(r: IdempotencyRecord) { this.records.set(r.key, r); }
  async findByKey(key: string) { return this.records.get(key) ?? null; }
  async updateStatus(key: string, status: IdempotencyStatus, result?: Record<string, unknown>, error?: string) {
    const r = this.records.get(key);
    if (r) { r.status = status; r.result = result ?? null; r.error = error ?? null; r.updatedAt = new Date(); }
  }
  async deleteExpired() {
    const now = new Date();
    for (const [k, v] of this.records) {
      if (v.expiresAt < now) this.records.delete(k);
    }
  }
}

describe("IdempotencyEngine", () => {
  let engine: IdempotencyEngine;
  let repo: FakeIdemRepo;

  beforeEach(() => {
    repo = new FakeIdemRepo();
    engine = new IdempotencyEngine(repo);
  });

  it("returns not duplicate for new key", async () => {
    const result = await engine.checkAndLock("key-1");
    expect(result.isDuplicate).toBe(false);
  });

  it("returns duplicate for existing completed key", async () => {
    await engine.checkAndLock("key-1");
    await engine.complete("key-1", { batchId: "b-1" });
    const result = await engine.checkAndLock("key-1");
    expect(result.isDuplicate).toBe(true);
    expect(result.existingResult).toEqual({ batchId: "b-1" });
  });

  it("returns duplicate for processing key", async () => {
    await engine.checkAndLock("key-2");
    const result = await engine.checkAndLock("key-2");
    expect(result.isDuplicate).toBe(true);
  });

  it("stores result on completion", async () => {
    await engine.checkAndLock("key-3");
    await engine.complete("key-3", { batchId: "b-3", totalDebit: 1000 });
    const record = await repo.findByKey("key-3");
    expect(record!.status).toBe(IdempotencyStatus.Completed);
    expect(record!.result).toEqual({ batchId: "b-3", totalDebit: 1000 });
  });

  it("stores error on failure", async () => {
    await engine.checkAndLock("key-4");
    await engine.fail("key-4", "Validation error");
    const record = await repo.findByKey("key-4");
    expect(record!.status).toBe(IdempotencyStatus.Failed);
    expect(record!.error).toBe("Validation error");
  });

  it("cleans up expired records", async () => {
    await engine.checkAndLock("expired-key", 0);
    await new Promise(r => setTimeout(r, 10));
    await engine.cleanup();
    const record = await repo.findByKey("expired-key");
    expect(record).toBeNull();
  });

  it("is a no-op for empty key", async () => {
    const result = await engine.checkAndLock("");
    expect(result.isDuplicate).toBe(false);
  });
});
