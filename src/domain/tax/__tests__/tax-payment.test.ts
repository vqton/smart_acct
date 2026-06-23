import { describe, it, expect } from "vitest";
import { TaxPayment, TaxPaymentStatus, TaxPaymentMethod } from "../tax-payment.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("TaxPayment", () => {
  const base = () => ({
    taxReturnId: "return-1",
    taxpayerId: "tp-1",
    taxTypeId: "vat-1",
    amount: 10000000,
    paymentMethod: TaxPaymentMethod.BankTransfer,
    paymentDate: new Date("2026-03-15"),
    referenceNumber: "BCT-20260315-001",
    paidById: "user-1",
  });

  it("creates in pending status", () => {
    const p = TaxPayment.create(base());
    expect(p.status).toBe(TaxPaymentStatus.Pending);
    expect(p.amount).toBe(10000000);
    expect(p.refundAmount).toBe(0);
  });

  it("rejects zero or negative amount", () => {
    expect(() => TaxPayment.create({ ...base(), amount: 0 })).toThrow(DomainError);
    expect(() => TaxPayment.create({ ...base(), amount: -100 })).toThrow(DomainError);
  });

  it("completes a pending payment", () => {
    const p = TaxPayment.create(base());
    p.complete("CONF-001");
    expect(p.status).toBe(TaxPaymentStatus.Completed);
  });

  it("fails a pending payment", () => {
    const p = TaxPayment.create(base());
    p.fail("Insufficient funds");
    expect(p.status).toBe(TaxPaymentStatus.Failed);
  });

  it("throws completing non-pending payment", () => {
    const p = TaxPayment.create(base());
    p.complete();
    expect(() => p.complete()).toThrow(DomainError);
    expect(() => p.fail("reason")).toThrow(DomainError);
  });

  it("throws failing non-pending payment", () => {
    const p = TaxPayment.create(base());
    p.fail("reason");
    expect(() => p.complete()).toThrow(DomainError);
  });

  it("refunds a completed payment partially", () => {
    const p = TaxPayment.create(base());
    p.complete();
    p.refund(2000000, "Overpayment correction");
    expect(p.status).toBe(TaxPaymentStatus.PartiallyRefunded);
    expect(p.refundAmount).toBe(2000000);
  });

  it("refunds a completed payment fully", () => {
    const p = TaxPayment.create(base());
    p.complete();
    p.refund(10000000, "Full refund");
    expect(p.status).toBe(TaxPaymentStatus.FullyRefunded);
    expect(p.refundAmount).toBe(10000000);
  });

  it("throws refund on pending payment", () => {
    const p = TaxPayment.create(base());
    expect(() => p.refund(1000, "reason")).toThrow(DomainError);
  });

  it("throws refund exceeding balance", () => {
    const p = TaxPayment.create(base());
    p.complete();
    expect(() => p.refund(20000000, "too much")).toThrow(DomainError);
  });

  it("throws refund with zero amount", () => {
    const p = TaxPayment.create(base());
    p.complete();
    expect(() => p.refund(0, "zero")).toThrow(DomainError);
  });

  it("loads from state", () => {
    const original = TaxPayment.create(base());
    original.complete("CONF-001");
    const state = original.toState();
    const loaded = TaxPayment.load(state);
    expect(loaded.id.value).toBe(original.id.value);
    expect(loaded.status).toBe(TaxPaymentStatus.Completed);
    expect(loaded.amount).toBe(10000000);
  });
});
