import { describe, it, expect } from "vitest";
import { CashBox } from "../cm-cash-box.js";
import { CashBoxType, CashBoxStatus } from "../cm-enums.js";

describe("CashBox", () => {
  it("creates with default values", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main Cash", boxType: CashBoxType.CashRegister });
    expect(b.code).toBe("CB001");
    expect(b.currentBalance).toBe(0);
    expect(b.status).toBe(CashBoxStatus.Active);
    expect(b.currencyCode).toBe("VND");
  });

  it("deposits amount", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    b.deposit(100000, "receipt-1");
    expect(b.currentBalance).toBe(100000);
  });

  it("rejects negative deposit", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    expect(() => b.deposit(-100, "x")).toThrow("positive");
  });

  it("withdraws within balance", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    b.deposit(50000, "rcpt");
    b.withdraw(20000, "pmt");
    expect(b.currentBalance).toBe(30000);
  });

  it("rejects over-withdrawal", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    expect(() => b.withdraw(100, "x")).toThrow("Insufficient");
  });

  it("enforces max balance", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister, maxBalance: 1000 });
    expect(() => b.deposit(2000, "x")).toThrow("max balance");
  });

  it("allows negative when configured", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB002", name: "Petty", boxType: CashBoxType.PettyCash, allowNegative: true });
    b.deposit(100, "in");
    b.withdraw(200, "out");
    expect(b.currentBalance).toBe(-100);
  });

  it("closes only when balance zero", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    b.deposit(100, "x");
    expect(() => b.close()).toThrow("non-zero balance");
    b.withdraw(100, "y");
    b.close();
    expect(b.status).toBe(CashBoxStatus.Closed);
  });

  it("rejects transaction when inactive", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    b.deposit(100, "x");
    b.withdraw(100, "y");
    b.close();
    expect(() => b.deposit(50, "z")).toThrow("not active");
  });

  it("loads from state", () => {
    const b = CashBox.load({
      id: "test-id",
      locationId: "loc1",
      code: "CB001",
      name: "Loaded",
      boxType: "cash_register",
      currencyCode: "USD",
      minBalance: 0,
      maxBalance: null,
      currentBalance: 500,
      allowNegative: false,
      status: "active",
      description: null,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
      deletedAt: null,
    });
    expect(b.code).toBe("CB001");
    expect(b.currentBalance).toBe(500);
    expect(b.currencyCode).toBe("USD");
  });

  it("toState returns correct shape", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    const s = b.toState();
    expect(s.code).toBe("CB001");
    expect(s.currentBalance).toBe(0);
    expect(s.boxType).toBe("cash_register");
  });

  it("generates domain events on balance change", () => {
    const b = CashBox.create({ locationId: "loc1", code: "CB001", name: "Main", boxType: CashBoxType.CashRegister });
    b.deposit(1000, "test-ref");
    const events = b.clearEvents();
    expect(events.length).toBe(1);
    expect(events[0].eventName).toBe("CashBoxBalanceChanged");
  });
});
