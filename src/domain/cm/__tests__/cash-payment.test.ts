import { describe, it, expect } from "vitest";
import { CashPayment } from "../cm-cash-payment.js";
import { PaymentStatus, PaymentMethod } from "../cm-enums.js";

describe("CashPayment", () => {
  it("creates draft payment", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "Vendor A", amount: 100000 });
    expect(p.paymentNumber).toBe("P001");
    expect(p.status).toBe(PaymentStatus.Draft);
  });

  it("rejects zero amount", () => {
    expect(() => CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 0 }))
      .toThrow("positive");
  });

  it("submits for approval", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    p.submit();
    expect(p.status).toBe(PaymentStatus.Submitted);
  });

  it("approves submitted payment", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    p.submit();
    p.approve("a1");
    expect(p.status).toBe(PaymentStatus.Approved);
  });

  it("rejects approve without submit", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    expect(() => p.approve("a1")).toThrow("submitted");
  });

  it("pays and posts approved payment", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    p.submit();
    p.approve("a1");
    p.pay("c1");
    expect(p.status).toBe(PaymentStatus.Paid);
    p.post("p1");
    expect(p.status).toBe(PaymentStatus.Posted);
  });

  it("rejects rejected payment", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    p.submit();
    p.reject("insufficient funds");
    expect(p.status).toBe(PaymentStatus.Rejected);
  });

  it("reverses posted payment", () => {
    const p = CashPayment.create({ paymentNumber: "P001", paymentDate: new Date(), cashBoxId: "box1", cashierId: "c1", payeeName: "V", amount: 100000 });
    p.submit(); p.approve("a1"); p.pay("c1"); p.post("p1");
    p.reverse("u1", "duplicate payment");
    expect(p.status).toBe(PaymentStatus.Reversed);
  });
});
