import { describe, it, expect, beforeEach } from "vitest";
import { AuditEngine, AuditAction, AuditRecord, AuditRepository } from "../services/audit-engine.js";

class FakeAuditRepo implements AuditRepository {
  records: AuditRecord[] = [];

  async save(r: AuditRecord) { this.records.push(r); }
  async findByEntity(entityType: string, entityId: string) {
    return this.records.filter(r => r.entityType === entityType && r.entityId === entityId);
  }
  async findByAction(action: AuditAction) {
    return this.records.filter(r => r.action === action);
  }
  async findLatestByEntity(entityType: string, entityId: string) {
    const ents = await this.findByEntity(entityType, entityId);
    return ents.length > 0 ? ents[ents.length - 1] : null;
  }
  async verifyChain(entityType: string, entityId: string): Promise<boolean> {
    const ents = await this.findByEntity(entityType, entityId);
    if (ents.length === 0) return true;
    for (let i = 1; i < ents.length; i++) {
      if (ents[i].previousHash !== ents[i - 1].hash) return false;
    }
    return true;
  }
}

describe("AuditEngine", () => {
  let engine: AuditEngine;
  let repo: FakeAuditRepo;

  beforeEach(() => {
    repo = new FakeAuditRepo();
    engine = new AuditEngine(repo);
  });

  it("records an audit entry", async () => {
    const record = await engine.record({
      action: AuditAction.PostingStarted,
      entityType: "journal_batch",
      entityId: "b-1",
      userId: "u-1",
    });
    expect(record.action).toBe(AuditAction.PostingStarted);
    expect(record.entityId).toBe("b-1");
    expect(record.hash).toBeTruthy();
    expect(record.previousHash).toBe("0");
    expect(record.version).toBe(1);
  });

  it("chains hashes correctly", async () => {
    await engine.record({ action: AuditAction.PostingStarted, entityType: "batch", entityId: "b-1", userId: "u-1" });
    await engine.record({ action: AuditAction.PostingCompleted, entityType: "batch", entityId: "b-1", userId: "u-1" });
    const records = await repo.findByEntity("batch", "b-1");
    expect(records).toHaveLength(2);
    expect(records[1].previousHash).toBe(records[0].hash);
    expect(records[1].hash).not.toBe(records[0].hash);
  });

  it("verifies chain integrity", async () => {
    await engine.record({ action: AuditAction.PostingStarted, entityType: "batch", entityId: "b-2", userId: "u-1" });
    await engine.record({ action: AuditAction.PostingCompleted, entityType: "batch", entityId: "b-2", userId: "u-1" });
    const valid = await engine.verifyChain("batch", "b-2");
    expect(valid).toBe(true);
  });

    it("detects tampered chain", async () => {
      await engine.record({ action: AuditAction.PostingStarted, entityType: "batch", entityId: "b-3", userId: "u-1" });
      await engine.record({ action: AuditAction.PostingCompleted, entityType: "batch", entityId: "b-3", userId: "u-1" });
      repo.records[0].hash = "tampered";
      const valid = await engine.verifyChain("batch", "b-3");
      expect(valid).toBe(false);
    });

  it("stores changes and metadata", async () => {
    const record = await engine.record({
      action: AuditAction.AccountBalancesUpdated,
      entityType: "account",
      entityId: "a-1",
      userId: "u-1",
      changes: { balanceBefore: 0, balanceAfter: 1000 },
      metadata: { batchId: "b-1" },
    });
    expect(record.changes).toEqual({ balanceBefore: 0, balanceAfter: 1000 });
    expect(record.metadata).toEqual({ batchId: "b-1" });
  });

  it("sets version sequentially", async () => {
    await engine.record({ action: AuditAction.PostingStarted, entityType: "batch", entityId: "b-4", userId: "u-1" });
    const r2 = await engine.record({ action: AuditAction.PostingCompleted, entityType: "batch", entityId: "b-4", userId: "u-1" });
    expect(r2.version).toBe(2);
  });
});
