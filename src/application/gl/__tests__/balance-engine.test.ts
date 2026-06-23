import { describe, it, expect, beforeEach } from "vitest";
import { BalanceEngine, BalanceRepository, PeriodBalance, YearBalance, BalanceEntry } from "../services/balance-engine.js";

class FakeBalanceRepo implements BalanceRepository {
  periodBalances = new Map<string, PeriodBalance>();
  yearBalances = new Map<string, YearBalance>();
  entries: BalanceEntry[] = [];

  async savePeriodBalance(b: PeriodBalance) { this.periodBalances.set(`${b.accountId}:${b.periodId}`, b); }
  async getPeriodBalance(accountId: string, periodId: string) { return this.periodBalances.get(`${accountId}:${periodId}`) ?? null; }
  async saveYearBalance(b: YearBalance) { this.yearBalances.set(`${b.accountId}:${b.fiscalYearId}`, b); }
  async getYearBalance(accountId: string, fiscalYearId: string) { return this.yearBalances.get(`${accountId}:${fiscalYearId}`) ?? null; }
  async saveBalanceEntry(e: BalanceEntry) { this.entries.push(e); }
  async getBalanceEntries(accountId: string, periodId: string) { return this.entries.filter(e => e.accountId === accountId && e.periodId === periodId); }
}

describe("BalanceEngine", () => {
  let engine: BalanceEngine;
  let repo: FakeBalanceRepo;

  beforeEach(() => {
    repo = new FakeBalanceRepo();
    engine = new BalanceEngine(repo);
  });

  it("updates period balance for debit-nature account", async () => {
    const bal = await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 1000, 0, 0, 0, true);
    expect(bal.periodDebit).toBe(1000);
    expect(bal.periodCredit).toBe(0);
    expect(bal.closingBalance).toBe(1000);
  });

  it("updates period balance for credit-nature account", async () => {
    const bal = await engine.updatePeriodBalance("a-2", "p-1", "fy-1", 0, 1000, 0, 0, false);
    expect(bal.periodDebit).toBe(0);
    expect(bal.periodCredit).toBe(1000);
    expect(bal.closingBalance).toBe(1000);
  });

  it("accumulates multiple updates to period balance", async () => {
    await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 1000, 0, 0, 0, true);
    const bal = await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 500, 0, 0, 0, true);
    expect(bal.periodDebit).toBe(1500);
    expect(bal.closingBalance).toBe(1500);
  });

  it("handles credit updates for debit account (reduces balance)", async () => {
    await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 1000, 0, 0, 0, true);
    const bal = await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 0, 300, 0, 0, true);
    expect(bal.closingBalance).toBe(700);
  });

  it("updates year balance", async () => {
    const bal = await engine.updateYearBalance("a-1", "fy-1", 1000, 0, 0, 0, true);
    expect(bal.yearDebit).toBe(1000);
    expect(bal.closingBalance).toBe(1000);
  });

  it("records balance entry", async () => {
    await engine.recordBalanceEntry("a-1", "p-1", "fy-1", 1000, 0, 0, 0, 1000, 0, new Date());
    const entries = await repo.getBalanceEntries("a-1", "p-1");
    expect(entries).toHaveLength(1);
    expect(entries[0].runningBalance).toBe(1000);
  });

  it("persists period balance to repo", async () => {
    await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 1000, 0, 0, 0, true);
    const saved = await repo.getPeriodBalance("a-1", "p-1");
    expect(saved).not.toBeNull();
    expect(saved!.closingBalance).toBe(1000);
  });

  it("persists year balance to repo", async () => {
    await engine.updateYearBalance("a-1", "fy-1", 2000, 0, 0, 0, true);
    const saved = await repo.getYearBalance("a-1", "fy-1");
    expect(saved).not.toBeNull();
    expect(saved!.closingBalance).toBe(2000);
  });

  it("handles foreign currency balance tracking", async () => {
    const bal = await engine.updatePeriodBalance("a-1", "p-1", "fy-1", 0, 0, 500, 200, true);
    expect(bal.periodForeignDebit).toBe(500);
    expect(bal.periodForeignCredit).toBe(200);
    expect(bal.closingForeignBalance).toBe(300);
  });
});
