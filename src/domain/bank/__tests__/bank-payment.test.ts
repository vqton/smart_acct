import { describe, it, expect } from "vitest";
import { PaymentRequest, PaymentBatch, RecurringPayment } from "../bank-payment.js";
import { TransactionMethod, ApprovalStatus, PaymentBatchStatus, RecurringFrequency } from "../bank-enums.js";

describe("PaymentRequest", () => {
  it("creates payment request", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR001", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    expect(r.requestNumber).toBe("PR001");
    expect(r.amount).toBe(50000000);
    expect(r.approvalStatus).toBe(ApprovalStatus.Pending);
  });

  it("approves payment request", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR002", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.approve("user2");
    expect(r.approvalStatus).toBe(ApprovalStatus.Approved);
  });

  it("rejects approve already approved", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR003", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.approve("u1");
    expect(() => r.approve("u2")).toThrow("Only pending");
  });

  it("rejects payment request", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR004", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.reject("user2", "Insufficient funds");
    expect(r.approvalStatus).toBe(ApprovalStatus.Rejected);
  });

  it("rejects reject already approved", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR005", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.approve("u1");
    expect(() => r.reject("u2", "no")).toThrow("Only pending");
  });

  it("assigns batch", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR006", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.assignBatch("batch-1");
  });

  it("round-trips through toState/load", () => {
    const r = PaymentRequest.create({
      companyId: "c1", requestNumber: "PR007", paymentDate: new Date(),
      amount: 50000000, fromAccountId: "acct1", beneficiaryName: "Vendor A",
      requestedById: "user1",
    });
    r.approve("u1");
    const state = r.toState();
    const loaded = PaymentRequest.load(state);
    expect(loaded.requestNumber).toBe("PR007");
    expect(loaded.approvalStatus).toBe(ApprovalStatus.Approved);
  });
});

describe("PaymentBatch", () => {
  it("creates payment batch", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH001", paymentDate: new Date() });
    expect(b.batchNumber).toBe("BATCH001");
    expect(b.status).toBe(PaymentBatchStatus.Draft);
  });

  it("validates, approves, releases, completes", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH002", paymentDate: new Date() });
    b.addPayment("pmt-1", 50000000);
    b.addPayment("pmt-2", 30000000);
    expect(b.paymentCount).toBe(2);
    expect(b.totalAmount).toBe(80000000);
    b.validate();
    expect(b.status).toBe(PaymentBatchStatus.Validated);
    b.approve("user1");
    expect(b.status).toBe(PaymentBatchStatus.Approved);
    b.release("user2");
    expect(b.status).toBe(PaymentBatchStatus.Released);
    b.complete();
    expect(b.status).toBe(PaymentBatchStatus.Completed);
  });

  it("rejects validate empty batch", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH003", paymentDate: new Date() });
    expect(() => b.validate()).toThrow("empty");
  });

  it("rejects add payment released", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH004", paymentDate: new Date() });
    b.addPayment("pmt-1", 10000);
    b.validate(); b.approve("u1"); b.release("u1");
    expect(() => b.addPayment("pmt-2", 20000)).toThrow("Cannot add");
  });

  it("cancels draft batch", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH005", paymentDate: new Date() });
    b.cancel();
    expect(b.status).toBe(PaymentBatchStatus.Cancelled);
  });

  it("rejects cancel completed", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH006", paymentDate: new Date() });
    b.addPayment("pmt-1", 10000);
    b.validate(); b.approve("u1"); b.release("u1"); b.complete();
    expect(() => b.cancel()).toThrow("Cannot cancel");
  });

  it("marks failed", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH007", paymentDate: new Date() });
    b.markFailed();
  });

  it("round-trips through toState/load", () => {
    const b = PaymentBatch.create({ companyId: "c1", batchNumber: "BATCH008", paymentDate: new Date() });
    b.addPayment("pmt-1", 50000000);
    b.validate(); b.approve("u1");
    const state = b.toState();
    const loaded = PaymentBatch.load(state);
    expect(loaded.batchNumber).toBe("BATCH008");
    expect(loaded.status).toBe(PaymentBatchStatus.Approved);
  });
});

describe("RecurringPayment", () => {
  it("creates recurring payment", () => {
    const r = RecurringPayment.create({
      companyId: "c1", name: "Monthly Rent", fromAccountId: "acct1",
      beneficiaryName: "Landlord", amount: 10000000,
      frequency: RecurringFrequency.Monthly, startDate: new Date("2024-01-01"),
    });
    expect(r.isActive).toBe(true);
  });

  it("records execution and advances date", () => {
    const r = RecurringPayment.create({
      companyId: "c1", name: "Subscription", fromAccountId: "acct1",
      beneficiaryName: "SaaS Co", amount: 500000,
      frequency: RecurringFrequency.Monthly, startDate: new Date("2024-01-01"),
    });
    const before = r.nextExecutionDate;
    r.recordExecution();
    expect(r.nextExecutionDate.getMonth()).not.toBe(before.getMonth());
  });

  it("suspends and activates", () => {
    const r = RecurringPayment.create({
      companyId: "c1", name: "Insurance", fromAccountId: "acct1",
      beneficiaryName: "Ins Co", amount: 2000000,
      frequency: RecurringFrequency.Quarterly, startDate: new Date("2024-01-01"),
    });
    expect(r.isActive).toBe(true);
    r.suspend();
    expect(r.isActive).toBe(false);
    r.activate();
    expect(r.isActive).toBe(true);
  });
});
