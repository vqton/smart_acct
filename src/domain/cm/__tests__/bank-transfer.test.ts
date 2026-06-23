import { describe, it, expect } from "vitest";
import { BankTransfer } from "../cm-bank-transfer.js";
import { BankTransferType, BankTransferStatus } from "../cm-enums.js";

describe("BankTransfer", () => {
  it("creates draft transfer", () => {
    const t = BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Internal, fromAccountId: "acct1", toAccountId: "acct2", amount: 50000000, transferDate: new Date() });
    expect(t.transferNumber).toBe("BT001");
    expect(t.status).toBe(BankTransferStatus.Draft);
  });

  it("rejects same account", () => {
    expect(() => BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Internal, fromAccountId: "acct1", toAccountId: "acct1", amount: 50000000, transferDate: new Date() }))
      .toThrow("different");
  });

  it("approves, executes, completes", () => {
    const t = BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Domestic, fromAccountId: "acct1", toAccountId: "acct2", amount: 50000000, transferDate: new Date() });
    t.approve("mgr1");
    expect(t.status).toBe(BankTransferStatus.Approved);
    t.execute("ops1");
    expect(t.status).toBe(BankTransferStatus.Sent);
    t.complete();
    expect(t.status).toBe(BankTransferStatus.Completed);
  });

  it("fails transfer", () => {
    const t = BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Wire, fromAccountId: "acct1", toAccountId: "acct2", amount: 50000000, transferDate: new Date() });
    t.approve("mgr1");
    t.execute("ops1");
    t.fail("insufficient balance in nostro");
    expect(t.status).toBe(BankTransferStatus.Failed);
    expect(t.failureReason).toBe("insufficient balance in nostro");
  });

  it("cancels draft", () => {
    const t = BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Domestic, fromAccountId: "acct1", toAccountId: "acct2", amount: 50000000, transferDate: new Date() });
    t.cancel();
    expect(t.status).toBe(BankTransferStatus.Cancelled);
  });

  it("rejects cancel completed", () => {
    const t = BankTransfer.create({ transferNumber: "BT001", transferType: BankTransferType.Domestic, fromAccountId: "acct1", toAccountId: "acct2", amount: 50000000, transferDate: new Date() });
    t.approve("m1");
    t.execute("o1");
    t.complete();
    expect(() => t.cancel()).toThrow("Cannot cancel");
  });
});
