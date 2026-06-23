import { describe, it, expect } from "vitest";
import { CashSession } from "../cm-session.js";
import { CashSessionStatus } from "../cm-enums.js";

describe("CashSession", () => {
  it("creates a pending session", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1" });
    expect(s.sessionNumber).toBe("CS001");
    expect(s.status).toBe(CashSessionStatus.Pending);
  });

  it("opens session", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 1000 });
    s.open();
    expect(s.status).toBe(CashSessionStatus.Open);
    expect(s.openedBalance).toBe(1000);
  });

  it("rejects double open", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1" });
    s.open();
    expect(() => s.open()).toThrow("already opened");
  });

  it("tracks receipts and payments", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    s.addReceipt(50000);
    expect(s.expectedBalance).toBe(150000);
    s.addPayment(30000);
    expect(s.expectedBalance).toBe(120000);
  });

  it("counts cash correctly", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    s.addReceipt(50000);
    s.countCash(145000);
    expect(s.status).toBe(CashSessionStatus.Counting);
    expect(s.difference).toBe(5000);
  });

  it("closes session after count", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    s.countCash(100000);
    s.close();
    expect(s.status).toBe(CashSessionStatus.Closed);
    expect(s.closedAt).not.toBeNull();
  });

  it("rejects close without count", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    expect(() => s.close()).toThrow("count cash");
  });

  it("reconciles zero-difference session", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    s.countCash(100000);
    s.close();
    s.reconcile();
    expect(s.status).toBe(CashSessionStatus.Reconciled);
  });

  it("rejects reconcile with difference", () => {
    const s = CashSession.create({ sessionNumber: "CS001", cashBoxId: "box1", cashierId: "cashier1", openedBalance: 100000 });
    s.open();
    s.countCash(95000);
    s.close();
    expect(() => s.reconcile()).toThrow("difference");
  });

  it("loads from state", () => {
    const s = CashSession.load({
      id: "sid", sessionNumber: "CS001", cashBoxId: "box1", cashRegisterId: null, cashierId: "c1",
      status: "closed", openedAt: new Date(), closedAt: new Date(),
      openedBalance: 100000, expectedBalance: 100000, countedBalance: 100000, difference: 0,
      currencyCode: "VND", notes: null, version: 3, createdAt: new Date(), updatedAt: new Date(), deletedAt: null,
    });
    expect(s.sessionNumber).toBe("CS001");
    expect(s.status).toBe(CashSessionStatus.Closed);
  });
});
