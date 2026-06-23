import { describe, it, expect } from "vitest";
import { BankStatement, BankReconciliation } from "../cm-bank-statement.js";
import { StatementLineType, BankReconciliationStatus } from "../cm-enums.js";

describe("BankStatement", () => {
  it("creates statement", () => {
    const s = BankStatement.create({ bankAccountId: "ba1", statementNumber: "STMT001", periodStart: new Date("2026-01-01"), periodEnd: new Date("2026-01-31"), openingBalance: 100000000, closingBalance: 150000000 });
    expect(s.statementNumber).toBe("STMT001");
    expect(s.openingBalance).toBe(100000000);
    expect(s.closingBalance).toBe(150000000);
  });

  it("adds lines and validates balance", () => {
    const s = BankStatement.create({ bankAccountId: "ba1", statementNumber: "STMT001", periodStart: new Date("2026-01-01"), periodEnd: new Date("2026-01-31"), openingBalance: 100000000, closingBalance: 150000000 });
    s.addLine({ lineDate: new Date("2026-01-02"), description: "Deposit", reference: null, chequeNumber: null, lineType: StatementLineType.Credit, amount: 50000000, runningBalance: 150000000 });
    s.validateBalance();
    expect(s.totalCredit).toBe(50000000);
  });

  it("validates balance with multiple lines", () => {
    const s = BankStatement.create({ bankAccountId: "ba1", statementNumber: "STMT001", periodStart: new Date("2026-01-01"), periodEnd: new Date("2026-01-31"), openingBalance: 100000000, closingBalance: 80000000 });
    s.addLine({ lineDate: new Date("2026-01-05"), description: "Withdrawal", reference: null, chequeNumber: null, lineType: StatementLineType.Debit, amount: 20000000, runningBalance: 80000000 });
    expect(() => s.validateBalance()).not.toThrow();
  });

  it("rejects invalid balance", () => {
    const s = BankStatement.create({ bankAccountId: "ba1", statementNumber: "STMT001", periodStart: new Date(), periodEnd: new Date(), openingBalance: 100, closingBalance: 200 });
    expect(() => s.validateBalance()).toThrow("does not balance");
  });
});

describe("BankReconciliation", () => {
  it("creates reconciliation", () => {
    const r = BankReconciliation.create({ bankAccountId: "ba1", bankStatementId: "st1", reconciliationNumber: "REC001", reconciliationDate: new Date(), statementBalance: 150000000, bookBalance: 148000000 });
    expect(r.reconciliationNumber).toBe("REC001");
    expect(r.difference).toBe(2000000);
    expect(r.status).toBe(BankReconciliationStatus.Open);
  });

  it("resolves zero-difference reconciliation", () => {
    const r = BankReconciliation.create({ bankAccountId: "ba1", bankStatementId: "st1", reconciliationNumber: "REC001", reconciliationDate: new Date(), statementBalance: 150000000, bookBalance: 150000000 });
    r.resolve("acct1");
    expect(r.status).toBe(BankReconciliationStatus.Resolved);
  });

  it("rejects resolve with difference", () => {
    const r = BankReconciliation.create({ bankAccountId: "ba1", bankStatementId: "st1", reconciliationNumber: "REC001", reconciliationDate: new Date(), statementBalance: 150000000, bookBalance: 148000000 });
    expect(() => r.resolve("acct1")).toThrow("outstanding");
  });

  it("approves resolved reconciliation", () => {
    const r = BankReconciliation.create({ bankAccountId: "ba1", bankStatementId: "st1", reconciliationNumber: "REC001", reconciliationDate: new Date(), statementBalance: 50000000, bookBalance: 50000000 });
    r.resolve("acct1");
    r.approve("mgr1");
    expect(r.status).toBe(BankReconciliationStatus.Closed);
  });
});
