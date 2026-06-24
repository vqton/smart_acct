import { describe, it, expect } from "vitest";
import { EinvInvoice, EinvInvoiceLine } from "../einv-invoice.js";
import { EinvInvoiceStatus, EinvInvoiceCategory } from "../einv-enums.js";
import {
  CanSubmitSpec, CanIssueSpec, CanCancelSpec,
  GlPostingSpec, InvoiceCategorySpec,
  validateInvoiceNumberFormat, validateTaxCode, validateSeriesFormat,
} from "../einv-specifications.js";

function makeDraftInvoice(): EinvInvoice {
  const i = EinvInvoice.create({
    invoiceNumber: "0000001", invoiceTypeId: "type-1", templateId: "tmpl-1",
    sellerName: "Co", sellerTaxCode: "0123456789", buyerName: "Kh",
    invoiceDate: new Date(),
  });
  const l = EinvInvoiceLine.create({
    invoiceId: i.id.value, lineNumber: 1, itemCode: "SP", itemName: "SP",
    unit: "cái", quantity: 1, unitPrice: 100000n,
  });
  i.addLine(l);
  return i;
}

describe("CanSubmitSpec", () => {
  const spec = new CanSubmitSpec();
  it("allows draft with lines", () => {
    expect(spec.isSatisfiedBy(makeDraftInvoice())).toBe(true);
  });
  it("rejects submitted invoice", () => {
    const i = makeDraftInvoice();
    i.submit();
    expect(spec.isSatisfiedBy(i)).toBe(false);
  });
});

describe("CanIssueSpec", () => {
  const spec = new CanIssueSpec();
  it("rejects draft", () => {
    const i = makeDraftInvoice();
    expect(spec.isSatisfiedBy(i)).toBe(false);
  });
  it("allows signed", () => {
    const i = makeDraftInvoice();
    i.submit(); i.approve(); i.sign();
    expect(spec.isSatisfiedBy(i)).toBe(true);
  });
});

describe("CanCancelSpec", () => {
  const spec = new CanCancelSpec();
  it("allows accepted", () => {
    const i = makeDraftInvoice();
    i.submit(); i.approve(); i.sign(); i.issue();
    i.submitToTaxAuthority("p1");
    i.markAccepted("TA", "V");
    expect(spec.isSatisfiedBy(i)).toBe(true);
  });
  it("rejects draft", () => {
    const i = makeDraftInvoice();
    expect(spec.isSatisfiedBy(i)).toBe(false);
  });
});

describe("GlPostingSpec", () => {
  const spec = new GlPostingSpec();
  it("rejects non-accepted", () => {
    const i = makeDraftInvoice();
    expect(spec.isSatisfiedBy(i)).toBe(false);
  });
  it("allows accepted", () => {
    const i = makeDraftInvoice();
    i.submit(); i.approve(); i.sign(); i.issue();
    i.submitToTaxAuthority("p1");
    i.markAccepted("TA", "V");
    expect(spec.isSatisfiedBy(i)).toBe(true);
  });
});

describe("InvoiceCategorySpec", () => {
  const spec = new InvoiceCategorySpec();
  it("allows sales without original", () => {
    expect(() => spec.check({ category: EinvInvoiceCategory.sales, hasOriginalInvoice: false })).not.toThrow();
  });
  it("rejects adjustment without original", () => {
    expect(() => spec.check({ category: EinvInvoiceCategory.adjustment, hasOriginalInvoice: false })).toThrow("requires original invoice");
  });
  it("allows replacement with original", () => {
    expect(() => spec.check({ category: EinvInvoiceCategory.replacement, hasOriginalInvoice: true })).not.toThrow();
  });
});

describe("validation helpers", () => {
  it("validates tax code", () => {
    expect(() => validateTaxCode("0123456789")).not.toThrow();
    expect(() => validateTaxCode("0123456789-001")).not.toThrow();
    expect(() => validateTaxCode("123")).toThrow("Invalid tax code");
  });
  it("validates series format", () => {
    expect(() => validateSeriesFormat("AA24E")).not.toThrow();
    expect(() => validateSeriesFormat("aa24e")).toThrow("uppercase");
  });
  it("validates invoice number", () => {
    expect(() => validateInvoiceNumberFormat("1234567")).not.toThrow();
    expect(() => validateInvoiceNumberFormat("12345678901")).toThrow("1-10 digits");
  });
});
