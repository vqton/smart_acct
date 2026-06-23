import { describe, it, expect } from "vitest";
import { TaxReturn, TaxReturnStatus, TaxReturnType } from "../tax-return.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("TaxReturn", () => {
  const base = () => ({
    returnNumber: "VAT/Q1/2025/001", taxTypeId: "vat-1", taxpayerId: "tp-1",
    taxAuthorityId: "auth-1", periodId: "period-1", fiscalYearId: "fy-2025",
    returnType: TaxReturnType.Original, filingDate: new Date("2025-04-01"),
    dueDate: new Date("2025-04-20"), createdById: "user-1",
  });

  it("creates in draft status", () => {
    const tr = TaxReturn.create(base());
    expect(tr.status).toBe(TaxReturnStatus.Draft);
  });

  it("adds lines and aggregates totals", () => {
    const tr = TaxReturn.create(base());
    tr.addLine({
      taxCodeId: "vat10", taxCode: "VAT10", description: "Standard supplies",
      taxableAmount: 1000000, taxRate: 10, taxAmount: 100000,
      exemptAmount: 0, deductibleAmount: 100000, recoverableAmount: 0,
      isExempt: false, isZeroRated: false,
    });
    expect(tr.lines.length).toBe(1);
    expect(tr.totalTaxAmount).toBe(100000);
    expect(tr.toState().netPayableAmount).toBe(0);
  });

  it("submits and transitions to submitted", () => {
    const tr = TaxReturn.create(base());
    tr.addLine({
      taxCodeId: "vat10", taxCode: "VAT10", description: "Goods",
      taxableAmount: 500000, taxRate: 10, taxAmount: 50000,
      exemptAmount: 0, deductibleAmount: 25000, recoverableAmount: 0,
      isExempt: false, isZeroRated: false,
    });
    tr.submit();
    expect(tr.status).toBe(TaxReturnStatus.Submitted);
  });

  it("throws on submit without lines", () => {
    const tr = TaxReturn.create(base());
    expect(() => tr.submit()).toThrow(DomainError);
  });

  it("accepts a submitted return", () => {
    const tr = TaxReturn.create(base());
    tr.addLine({
      taxCodeId: "vat10", taxCode: "VAT10", description: "Goods",
      taxableAmount: 100000, taxRate: 10, taxAmount: 10000,
      exemptAmount: 0, deductibleAmount: 10000, recoverableAmount: 0,
      isExempt: false, isZeroRated: false,
    });
    tr.submit();
    tr.accept();
    expect(tr.status).toBe(TaxReturnStatus.Accepted);
  });

  it("rejects a submitted return", () => {
    const tr = TaxReturn.create(base());
    tr.addLine({
      taxCodeId: "vat10", taxCode: "VAT10", description: "Goods",
      taxableAmount: 100000, taxRate: 10, taxAmount: 10000,
      exemptAmount: 0, deductibleAmount: 10000, recoverableAmount: 0,
      isExempt: false, isZeroRated: false,
    });
    tr.submit();
    tr.reject("Underpayment of 500,000 VND");
    expect(tr.status).toBe(TaxReturnStatus.Rejected);
  });

  it("loads from state", () => {
    const tr = TaxReturn.create(base());
    tr.addLine({
      taxCodeId: "vat10", taxCode: "VAT10", description: "Sales",
      taxableAmount: 2000000, taxRate: 10, taxAmount: 200000,
      exemptAmount: 0, deductibleAmount: 200000, recoverableAmount: 0,
      isExempt: false, isZeroRated: false,
    });
    tr.submit();
    const state = tr.toState();
    const loaded = TaxReturn.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});
