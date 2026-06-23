import { describe, it, expect } from "vitest";
import { CashReceipt } from "../cm-cash-receipt.js";
import { ReceiptStatus, PaymentMethod } from "../cm-enums.js";

describe("CashReceipt", () => {
  it("creates draft receipt", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    expect(r.receiptNumber).toBe("R001");
    expect(r.status).toBe(ReceiptStatus.Draft);
    expect(r.amount).toBe(50000);
  });

  it("rejects zero amount", () => {
    expect(() => CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 0 }))
      .toThrow("positive");
  });

  it("approves receipt", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    r.approve("approver1");
    expect(r.status).toBe(ReceiptStatus.Approved);
    expect(r.approvedById).toBe("approver1");
  });

  it("posts approved receipt", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    r.approve("a1");
    r.post("p1");
    expect(r.status).toBe(ReceiptStatus.Posted);
  });

  it("rejects post without approve", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    expect(() => r.post("p1")).toThrow("approved");
  });

  it("reverses posted receipt", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    r.approve("a1");
    r.post("p1");
    r.reverse("u1", "wrong entry");
    expect(r.status).toBe(ReceiptStatus.Reversed);
  });

  it("cancels draft", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    r.cancel();
    expect(r.status).toBe(ReceiptStatus.Cancelled);
  });

  it("rejects cancel posted", () => {
    const r = CashReceipt.create({ receiptNumber: "R001", receiptDate: new Date(), cashBoxId: "box1", cashierId: "c1", amount: 50000 });
    r.approve("a1");
    r.post("p1");
    expect(() => r.cancel()).toThrow("draft");
  });
});
