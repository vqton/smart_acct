import { describe, it, expect } from "vitest";
import { EinvInvoice, EinvInvoiceLine } from "../einv-invoice.js";
import { EinvInvoiceStatus, EinvInvoiceCategory } from "../einv-enums.js";

describe("EinvInvoiceLine", () => {
  it("creates with basic fields", () => {
    const l = EinvInvoiceLine.create({
      invoiceId: "inv-1", lineNumber: 1, itemCode: "SP001", itemName: "Sản phẩm A",
      unit: "cái", quantity: 10, unitPrice: 100000n,
    });
    expect(l.itemCode).toBe("SP001");
    expect(l.quantity).toBe(10);
    expect(l.unitPrice).toBe(100000n);
    expect(l.totalPrice).toBe(1000000n);
    expect(l.taxAmount).toBe(0n);
    expect(l.netAmount).toBe(1000000n);
  });

  it("calculates tax and discount", () => {
    const l = EinvInvoiceLine.create({
      invoiceId: "inv-1", lineNumber: 1, itemCode: "SP001", itemName: "SP",
      unit: "cái", quantity: 2, unitPrice: 50000n,
      taxCode: "VAT10", taxRate: 10,
    });
    expect(l.totalPrice).toBe(100000n);
    expect(l.taxAmount).toBe(10000n);
    expect(l.netAmount).toBe(110000n);
  });

  it("loads from state", () => {
    const l = EinvInvoiceLine.load({
      id: "line-1", invoiceId: "inv-1", lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 5, unitPrice: 20000n, totalPrice: 100000n,
      discountPercent: 0, discountAmount: 0n, taxCode: null, taxRate: 0, taxAmount: 0n,
      netAmount: 100000n, salesLineId: null, itemId: null, description: null,
    });
    expect(l.quantity).toBe(5);
    expect(l.netAmount).toBe(100000n);
  });
});

describe("EinvInvoice", () => {
  const validParams = {
    invoiceNumber: "0000001", invoiceTypeId: "type-1", templateId: "tmpl-1",
    sellerName: "Công ty ABC", sellerTaxCode: "0123456789", buyerName: "Khách hàng XYZ",
    invoiceDate: new Date("2024-01-15"),
  };

  it("creates as draft", () => {
    const i = EinvInvoice.create(validParams);
    expect(i.status).toBe(EinvInvoiceStatus.draft);
    expect(i.category).toBe(EinvInvoiceCategory.sales);
    expect(i.invoiceNumber).toBe("0000001");
    expect(i.grandTotal).toBe(0n);
  });

  it("rejects submit with no lines", () => {
    const i = EinvInvoice.create(validParams);
    expect(() => i.submit()).toThrow("Cannot submit invoice with no lines");
  });

  it("transitions through lifecycle", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);

    i.submit();
    expect(i.status).toBe(EinvInvoiceStatus.pendingApproval);

    i.approve();
    expect(i.status).toBe(EinvInvoiceStatus.approved);

    i.sign();
    expect(i.status).toBe(EinvInvoiceStatus.signed);
    expect(i.signingDate).toBeTruthy();

    i.issue();
    expect(i.status).toBe(EinvInvoiceStatus.issued);
    expect(i.issueDate).toBeTruthy();
  });

  it("rejects invalid status transitions", () => {
    const i = EinvInvoice.create(validParams);
    expect(() => i.approve()).toThrow("Invoice not pending approval");
    expect(() => i.sign()).toThrow("Only approved invoice can be signed");
  });

  it("handles tax authority acceptance", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);
    i.submit();
    i.approve();
    i.sign();
    i.issue();
    i.submitToTaxAuthority("provider-1");
    expect(i.status).toBe(EinvInvoiceStatus.submitted);

    i.markAccepted("TA001", "ABC123");
    expect(i.status).toBe(EinvInvoiceStatus.accepted);
    expect(i.taxAuthorityCode).toBe("TA001");
    expect(i.verifyCode).toBe("ABC123");
  });

  it("cancels accepted invoice", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);
    i.submit(); i.approve(); i.sign(); i.issue();
    i.submitToTaxAuthority("provider-1");
    i.markAccepted("TA001", "ABC");
    i.cancel("Customer request");
    expect(i.status).toBe(EinvInvoiceStatus.cancelled);
  });

  it("posts to GL", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);
    i.submit(); i.approve(); i.sign(); i.issue();
    i.submitToTaxAuthority("provider-1");
    i.markAccepted("TA001", "ABC");
    i.markPostedToGL("gl-batch-1");
    expect(i.postedToGL).toBe(true);
    expect(i.glBatchId).toBe("gl-batch-1");
  });

  it("rejects double GL posting", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);
    i.submit(); i.approve(); i.sign(); i.issue();
    i.submitToTaxAuthority("provider-1");
    i.markAccepted("TA001", "ABC");
    i.markPostedToGL("gl-batch-1");
    expect(() => i.markPostedToGL("gl-batch-2")).toThrow("already posted to GL");
  });

  it("round-trips through toState/load", () => {
    const i = EinvInvoice.create(validParams);
    const line = EinvInvoiceLine.create({
      invoiceId: i.id.value, lineNumber: 1, itemCode: "SP001",
      itemName: "SP", unit: "cái", quantity: 1, unitPrice: 100000n,
    });
    i.addLine(line);
    i.submit(); i.approve(); i.sign(); i.issue();

    const state = i.toState();
    const loaded = EinvInvoice.load(state);
    expect(loaded.invoiceNumber).toBe("0000001");
    expect(loaded.status).toBe(EinvInvoiceStatus.issued);
    expect(loaded.sellerName).toBe("Công ty ABC");
    expect(loaded.sellerTaxCode).toBe("0123456789");
    expect(loaded.buyerName).toBe("Khách hàng XYZ");
    expect(loaded.subtotal).toBe(100000n);
  });
});
