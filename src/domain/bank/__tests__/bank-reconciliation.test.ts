import { describe, it, expect } from "vitest";
import { BankStatement } from "../bank-statement.js";
import { BankReconciliation, BankReconciliationItem } from "../bank-reconciliation.js";
import { ReconciliationStatus, ReconciliationMatchType, StatementSource } from "../bank-enums.js";

describe("BankStatement", () => {
  it("creates statement", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT001",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 150000000,
    });
    expect(s.statementNumber).toBe("STMT001");
    expect(s.openingBalance).toBe(100000000);
    expect(s.isReconciled).toBe(false);
    expect(s.isLocked).toBe(false);
  });

  it("adds lines and calculates totals", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT002",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 150000000,
    });
    s.addLine({ lineDate: new Date("2024-01-05"), lineType: "credit", amount: 10000000, runningBalance: 110000000 });
    s.addLine({ lineDate: new Date("2024-01-10"), lineType: "debit", amount: 5000000, runningBalance: 105000000 });
    expect(s.lines).toHaveLength(2);
    expect(s.totalCredit).toBe(10000000);
    expect(s.totalDebit).toBe(5000000);
  });

  it("validates correct balance", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT003",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 120000000,
    });
    s.addLine({ lineDate: new Date("2024-01-05"), lineType: "credit", amount: 20000000, runningBalance: 120000000 });
    expect(s.validateBalance()).toBe(true);
  });

  it("rejects invalid balance", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT004",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 99999999,
    });
    s.addLine({ lineDate: new Date("2024-01-05"), lineType: "credit", amount: 20000000, runningBalance: 120000000 });
    expect(() => s.validateBalance()).toThrow("does not balance");
  });

  it("locks and unlocks", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT005",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 100000000,
    });
    s.lock();
    expect(s.isLocked).toBe(true);
    s.unlock();
    expect(s.isLocked).toBe(false);
  });

  it("rejects modify locked", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT006",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 100000000,
    });
    s.lock();
    expect(() => s.addLine({ lineDate: new Date(), lineType: "credit", amount: 1000, runningBalance: 1000 })).toThrow("locked");
  });

  it("rejects unlock reconciled", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT007",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 100000000,
    });
    s.lock();
    s.markReconciled();
    expect(() => s.unlock()).toThrow("Cannot unlock reconciled");
  });

  it("round-trips through toState/load", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT008",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 120000000,
    });
    s.addLine({ lineDate: new Date("2024-01-05"), lineType: "credit", amount: 20000000, runningBalance: 120000000 });
    const state = s.toState();
    const loaded = BankStatement.load(state);
    expect(loaded.statementNumber).toBe("STMT008");
    expect(loaded.totalCredit).toBe(20000000);
  });

  it("statement line match/unmatch", () => {
    const s = BankStatement.create({
      bankAccountId: "ba1", statementNumber: "STMT009",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-01-31"),
      openingBalance: 100000000, closingBalance: 100000000,
    });
    const line = s.addLine({ lineDate: new Date(), lineType: "credit", amount: 50000, runningBalance: 100050000 });
    expect(line.isMatched).toBe(false);
    line.match("payment", "pmt-1");
    expect(line.isMatched).toBe(true);
    line.unmatch();
    expect(line.isMatched).toBe(false);
  });
});

describe("BankReconciliation", () => {
  it("creates reconciliation", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC001", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    expect(r.status).toBe(ReconciliationStatus.Open);
    expect(r.difference).toBe(0);
  });

  it("creates with difference", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC002", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 145000000,
    });
    expect(r.difference).toBe(5000000);
  });

  it("adds matched items", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC003", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    const item = r.addItem({ sourceType: "payment", sourceId: "pmt-1", amount: 50000000, matchType: ReconciliationMatchType.Auto });
    expect(r.matchedCount).toBe(1);
    expect(r.items).toHaveLength(1);
    expect(item.matchType).toBe(ReconciliationMatchType.Auto);
  });

  it("resolves when balanced", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC004", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.resolve("user1");
    expect(r.status).toBe(ReconciliationStatus.Resolved);
  });

  it("rejects resolve with difference", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC005", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 140000000,
    });
    expect(() => r.resolve("user1")).toThrow("Cannot resolve");
  });

  it("approves resolved reconciliation", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC006", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.resolve("user1");
    r.approve("user2");
    expect(r.status).toBe(ReconciliationStatus.Approved);
  });

  it("closes approved reconciliation", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC007", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.resolve("u1"); r.approve("u2"); r.close();
    expect(r.status).toBe(ReconciliationStatus.Closed);
  });

  it("reverses reconciliation", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC008", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.reverse("user1", "wrong data");
    expect(r.status).toBe(ReconciliationStatus.Reversed);
  });

  it("rejects close non-approved", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC009", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    expect(() => r.close()).toThrow("Only approved");
  });

  it("rejects reverse closed", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC010", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.resolve("u1"); r.approve("u2"); r.close();
    expect(() => r.reverse("u1", "no")).toThrow("Cannot reverse closed");
  });

  it("marks in-progress", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC011", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    r.markInProgress();
    expect(r.status).toBe(ReconciliationStatus.InProgress);
  });

  it("round-trips through toState/load", () => {
    const r = BankReconciliation.create({
      bankAccountId: "ba1", bankStatementId: "stmt1",
      reconciliationNumber: "REC012", reconciliationDate: new Date(),
      statementBalance: 150000000, bookBalance: 150000000,
    });
    const state = r.toState();
    const loaded = BankReconciliation.load(state);
    expect(loaded.reconciliationNumber).toBe("REC012");
    expect(loaded.status).toBe(ReconciliationStatus.Open);
  });
});

describe("BankReconciliationItem", () => {
  it("loads from state", () => {
    const item = BankReconciliationItem.load({
      id: "item-1", reconciliationId: "rec-1", statementLineId: "sl-1",
      sourceType: "payment", sourceId: "pmt-1", sourceReference: "INV-001",
      amount: 1000000, matchType: ReconciliationMatchType.Auto,
      matchDate: new Date(), isClearItem: true, notes: null,
      createdAt: new Date(), updatedAt: new Date(),
    });
    expect(item.sourceType).toBe("payment");
    expect(item.amount).toBe(1000000);
    expect(item.matchType).toBe(ReconciliationMatchType.Auto);
  });
});
