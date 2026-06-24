import { describe, it, expect } from "vitest";
import { BankTransaction } from "../bank-transaction.js";
import { TransactionNature, TransactionMethod, TransactionStatus } from "../bank-enums.js";

describe("BankTransaction", () => {
  it("creates transaction in draft status", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN001", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 50000000,
      transactionDate: new Date(),
    });
    expect(t.transactionNumber).toBe("TXN001");
    expect(t.status).toBe(TransactionStatus.Draft);
    expect(t.amount).toBe(50000000);
  });

  it("rejects zero amount", () => {
    expect(() => BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN002", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 0,
      transactionDate: new Date(),
    })).toThrow("must be positive");
  });

  it("approves, executes, completes", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN003", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.authorize("user1");
    expect(t.status).toBe(TransactionStatus.Authorized);
    t.approve("user2");
    expect(t.status).toBe(TransactionStatus.Approved);
    t.execute("user3");
    expect(t.status).toBe(TransactionStatus.Executed);
    t.complete();
    expect(t.status).toBe(TransactionStatus.Completed);
  });

  it("rejects approve before authorize", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN004", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    expect(() => t.approve("user1")).toThrow("Only authorized");
  });

  it("rejects execute before approve", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN005", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.authorize("user1");
    expect(() => t.execute("user2")).toThrow("Only approved");
  });

  it("fails transaction", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN006", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.fail("NSF");
    expect(t.status).toBe(TransactionStatus.Failed);
    expect(t.failureReason).toBe("NSF");
  });

  it("rejects fail on completed", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN007", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.authorize("u1"); t.approve("u2"); t.execute("u3"); t.complete();
    expect(() => t.fail("reason")).toThrow("Cannot fail");
  });

  it("cancels draft", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN008", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.cancel();
    expect(t.status).toBe(TransactionStatus.Cancelled);
  });

  it("rejects cancel completed", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN009", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.authorize("u1"); t.approve("u2"); t.execute("u3"); t.complete();
    expect(() => t.cancel()).toThrow("Cannot cancel");
  });

  it("reverses completed", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN010", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.authorize("u1"); t.approve("u2"); t.execute("u3"); t.complete();
    t.reverse("wrong account");
    expect(t.status).toBe(TransactionStatus.Reversed);
  });

  it("rejects reverse non-completed", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN011", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    expect(() => t.reverse("no")).toThrow("Only completed");
  });

  it("marks GL posted", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN012", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 1000000,
      transactionDate: new Date(),
    });
    t.markGLPosted("batch-1");
  });

  it("handles exchange rate for foreign currency", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN013", nature: TransactionNature.External,
      method: TransactionMethod.Swift, fromAccountId: "acct1", amount: 1000,
      currencyCode: "USD", exchangeRate: 25400, transactionDate: new Date(),
    });
    expect(t.vndAmount).toBe(25400000);
  });

  it("round-trips through toState/load", () => {
    const t = BankTransaction.create({
      companyId: "c1", transactionNumber: "TXN014", nature: TransactionNature.Outgoing,
      method: TransactionMethod.Wire, fromAccountId: "acct1", amount: 50000000,
      transactionDate: new Date(), reference: "INV-001",
    });
    t.authorize("u1"); t.approve("u2");
    const state = t.toState();
    const loaded = BankTransaction.load(state);
    expect(loaded.transactionNumber).toBe("TXN014");
    expect(loaded.status).toBe(TransactionStatus.Approved);
  });
});
