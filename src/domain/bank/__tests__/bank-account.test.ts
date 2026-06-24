import { describe, it, expect } from "vitest";
import { BankAccount, AuthorizedSigner, AccountLimit, AccountMapping } from "../bank-account.js";
import { BankAccountCategory, BankAccountStatus, SignatureRule, AccountLimitType } from "../bank-enums.js";

describe("BankAccount", () => {
  it("creates bank account", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "0071101234567", accountName: "Main Ops" });
    expect(a.accountNumber.value).toBe("0071101234567");
    expect(a.status).toBe(BankAccountStatus.Active);
    expect(a.currencyCode).toBe("VND");
    expect(a.currentBalance).toBe(0);
  });

  it("credits and debits", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(1000000, "deposit");
    expect(a.currentBalance).toBe(1000000);
    expect(a.availableBalance).toBe(1000000);
    a.debit(400000, "withdrawal");
    expect(a.currentBalance).toBe(600000);
    expect(a.availableBalance).toBe(600000);
  });

  it("rejects debit over balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    expect(() => a.debit(100, "x")).toThrow("Insufficient");
  });

  it("allows debit within balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(2000, "dep");
    a.debit(1500, "payment");
    expect(a.currentBalance).toBe(500);
  });

  it("blocks and unblocks balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(1000000, "dep");
    a.blockBalance(200000, "hold");
    expect(a.blockedBalance).toBe(200000);
    expect(a.availableBalance).toBe(800000);
    a.unblockBalance(100000, "release");
    expect(a.blockedBalance).toBe(100000);
    expect(a.availableBalance).toBe(900000);
  });

  it("rejects block over available", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    expect(() => a.blockBalance(100, "x")).toThrow("Insufficient");
  });

  it("rejects debit on blocked account", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.block("court order");
    expect(a.status).toBe(BankAccountStatus.Blocked);
    expect(() => a.debit(100, "x")).toThrow("Cannot transact");
  });

  it("suspends and reactivates", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.suspend("fraud review");
    expect(a.status).toBe(BankAccountStatus.Suspended);
    a.activate();
    expect(a.status).toBe(BankAccountStatus.Active);
  });

  it("rejects suspend non-active", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.suspend("review");
    expect(() => a.suspend("again")).toThrow("Only active");
  });

  it("closes with zero balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.close();
    expect(a.status).toBe(BankAccountStatus.Closed);
  });

  it("rejects close with balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(500, "dep");
    expect(() => a.close()).toThrow("non-zero");
  });

  it("force-closes with balance", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(500, "dep");
    a.close(true);
    expect(a.status).toBe(BankAccountStatus.Closed);
  });

  it("canTransact returns false for suspended", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    expect(a.canTransact()).toBe(true);
    a.suspend("review");
    expect(a.canTransact()).toBe(false);
  });

  it("manages signers", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    const s = AuthorizedSigner.create({ bankAccountId: a.id.value, userId: "u1", name: "John Doe" });
    a.addSigner(s);
    expect(a.signers).toHaveLength(1);
    expect(a.signers[0].signingLimit).toBe(0);
  });

  it("manages limits", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    const l = AccountLimit.create({ bankAccountId: a.id.value, limitType: AccountLimitType.PerTransaction, maxAmount: 50000000 });
    a.addLimit(l);
    expect(a.limits).toHaveLength(1);
    expect(a.limits[0].maxAmount).toBe(50000000);
  });

  it("manages mappings", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    const m = AccountMapping.create({ bankAccountId: a.id.value, mappingType: "default", glAccountId: "gl1" });
    a.addMapping(m);
    expect(a.mappings).toHaveLength(1);
    expect(a.mappings[0].glAccountId).toBe("gl1");
  });

  it("round-trips through toState/load", () => {
    const a = BankAccount.create({ companyId: "c1", bankId: "bank1", accountNumber: "ACC-007", accountName: "Ops" });
    a.credit(1000000, "dep");
    const state = a.toState();
    const loaded = BankAccount.load(state);
    expect(loaded.accountNumber.value).toBe("ACC-007");
    expect(loaded.currentBalance).toBe(1000000);
    expect(loaded.status).toBe(BankAccountStatus.Active);
  });
});

describe("AuthorizedSigner", () => {
  it("creates signer", () => {
    const s = AuthorizedSigner.create({ bankAccountId: "ba1", userId: "u1", name: "Alice" });
    expect(s.isActive).toBe(true);
    expect(s.signatureRule).toBe(SignatureRule.Single);
  });

  it("deactivates signer", () => {
    const s = AuthorizedSigner.create({ bankAccountId: "ba1", userId: "u1", name: "Alice" });
    s.deactivate();
    expect(s.isActive).toBe(false);
  });

  it("canSign respects limit", () => {
    const s = AuthorizedSigner.create({ bankAccountId: "ba1", userId: "u1", name: "Bob", signingLimit: 10000000 });
    expect(s.canSign(5000000)).toBe(true);
    expect(s.canSign(20000000)).toBe(false);
  });
});

describe("AccountLimit", () => {
  it("exceedsLimit checks max/min", () => {
    const l = AccountLimit.create({ bankAccountId: "ba1", limitType: AccountLimitType.PerTransaction, maxAmount: 50000000, minAmount: 10000 });
    expect(l.exceedsLimit(30000000)).toBe(false);
    expect(l.exceedsLimit(100000000)).toBe(true);
    expect(l.exceedsLimit(5000)).toBe(true);
  });

  it("non-enforced limits never exceed", () => {
    const l = AccountLimit.create({ bankAccountId: "ba1", limitType: AccountLimitType.PerTransaction, maxAmount: 10000, isEnforced: false });
    expect(l.exceedsLimit(99999999)).toBe(false);
  });
});

describe("AccountMapping", () => {
  it("creates mapping", () => {
    const m = AccountMapping.create({ bankAccountId: "ba1", mappingType: "gl", glAccountId: "gl-1111" });
    expect(m.glAccountId).toBe("gl-1111");
    expect(m.isDefault).toBe(false);
  });

  it("creates default mapping", () => {
    const m = AccountMapping.create({ bankAccountId: "ba1", mappingType: "default", isDefault: true });
    expect(m.isDefault).toBe(true);
  });
});
