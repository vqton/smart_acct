import { describe, it, expect } from "vitest";
import { SupplierInvoice, InvoiceLine } from "../purchasing-invoice.js";
import { InvoiceStatus } from "../purchasing-enums.js";

describe("SupplierInvoice", () => {
  it("creates an invoice", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-001", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    expect(inv.invoiceNumber).toBe("INV-001");
    expect(inv.status).toBe(InvoiceStatus.draft);
  });

  it("adds lines and calculates totals", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-002", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    const line = InvoiceLine.create({ invoiceId: inv.id.value, lineNumber: 1, itemCode: "A", itemName: "Widget", quantity: 10, uom: "pcs", unitPrice: 5000, taxRate: 10 });
    inv.addLine(line);
    expect(inv.totalAmount).toBe(50000);
    expect(inv.totalTax).toBe(5000);
    expect(inv.grandTotal).toBe(55000);
  });

  it("follows register-verify-approve lifecycle", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-003", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    inv.addLine(InvoiceLine.create({ invoiceId: inv.id.value, lineNumber: 1, itemCode: "A", itemName: "A", quantity: 1, uom: "pcs", unitPrice: 100 }));
    inv.register();
    expect(inv.status).toBe(InvoiceStatus.registered);
    inv.verify();
    expect(inv.status).toBe(InvoiceStatus.verified);
    inv.approve("approver1");
    expect(inv.status).toBe(InvoiceStatus.approved);
  });

  it("rejects register with no lines", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-004", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    expect(() => inv.register()).toThrow("no lines");
  });

  it("records payment", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-005", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    inv.addLine(InvoiceLine.create({ invoiceId: inv.id.value, lineNumber: 1, itemCode: "A", itemName: "A", quantity: 1, uom: "pcs", unitPrice: 1000 }));
    inv.register();
    inv.verify();
    inv.approve("boss");
    inv.recordPayment(1000);
    expect(inv.amountDue).toBe(0);
  });

  it("holds and releases invoice", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-006", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    inv.hold("Discrepancy");
    expect(inv.status).toBe(InvoiceStatus.onHold);
    inv.release();
    expect(inv.status).toBe(InvoiceStatus.verified);
  });

  it("cancels invoice", () => {
    const inv = SupplierInvoice.create({ invoiceNumber: "INV-007", invoiceDate: new Date(), companyId: "C001", vendorId: "V001", vendorName: "Supplier" });
    inv.cancel("Duplicate");
    expect(inv.status).toBe(InvoiceStatus.cancelled);
  });
});
