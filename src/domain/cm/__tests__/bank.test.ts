import { describe, it, expect } from "vitest";
import { Bank, BankAccount, BankBranch } from "../cm-bank.js";
import { BankAccountType, BankAccountStatus } from "../cm-enums.js";
import { BankId, BankBranchId, BankAccountId } from "../cm-ids.js";

describe("Bank", () => {
  it("creates a bank", () => {
    const b = Bank.create({ companyId: "c1", code: "VCB", name: "Vietcombank", swiftCode: "VCBVVNVX" });
    expect(b.code).toBe("VCB");
    expect(b.swiftCode).toBe("VCBVVNVX");
    expect(b.isActive).toBe(true);
  });

  it("deactivates bank", () => {
    const b = Bank.create({ companyId: "c1", code: "VCB", name: "Vietcombank" });
    b.deactivate();
    expect(b.isActive).toBe(false);
  });
});

describe("BankAccount", () => {
  it("creates bank account", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "0071101234567", accountName: "Main Ops", openingDate: new Date() });
    expect(a.accountNumber).toBe("0071101234567");
    expect(a.status).toBe(BankAccountStatus.Active);
  });

  it("credits and debits", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "0071101234567", accountName: "Ops", openingDate: new Date() });
    a.credit(1000000, "deposit");
    expect(a.currentBalance).toBe(1000000);
    expect(a.availableBalance).toBe(1000000);
    a.debit(400000, "withdrawal");
    expect(a.currentBalance).toBe(600000);
  });

  it("blocks and unblocks", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "007", accountName: "Ops", openingDate: new Date() });
    a.credit(1000000, "dep");
    a.block(200000);
    expect(a.blockedBalance).toBe(200000);
    expect(a.availableBalance).toBe(800000);
    a.unblock(100000);
    expect(a.blockedBalance).toBe(100000);
    expect(a.availableBalance).toBe(900000);
  });

  it("rejects over-debit", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "007", accountName: "Ops", openingDate: new Date() });
    expect(() => a.debit(100, "x")).toThrow("Insufficient");
  });

  it("closes with zero balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "007", accountName: "Ops", openingDate: new Date() });
    a.close();
    expect(a.status).toBe(BankAccountStatus.Closed);
  });

  it("rejects close with balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "007", accountName: "Ops", openingDate: new Date() });
    a.credit(500, "dep");
    expect(() => a.close()).toThrow("non-zero");
  });
});
