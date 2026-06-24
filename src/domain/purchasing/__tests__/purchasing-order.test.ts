import { describe, it, expect } from "vitest";
import { PurchaseOrder, POLine } from "../purchasing-order.js";
import { POStatus, POType } from "../purchasing-enums.js";

describe("PurchaseOrder", () => {
  it("creates a purchase order", () => {
    const po = PurchaseOrder.create({
      poNumber: "PO-2024-001", companyId: "C001", vendorId: "V001", vendorName: "Test Supplier",
    });
    expect(po.poNumber).toBe("PO-2024-001");
    expect(po.status).toBe(POStatus.draft);
    expect(po.grandTotal).toBe(0);
  });

  it("adds lines and recalculates totals", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-002", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    const line = POLine.create({ poId: po.id.value, lineNumber: 1, itemCode: "ITEM001", itemName: "Widget", quantity: 10, uom: "pcs", unitPrice: 1000, taxRate: 10 });
    po.addLine(line);
    expect(po.lines.length).toBe(1);
    expect(po.totalAmount).toBe(10000);
    expect(po.grandTotal).toBe(11000);
  });

  it("rejects lines in non-draft PO", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-003", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    po.addLine(POLine.create({ poId: po.id.value, lineNumber: 1, itemCode: "A", itemName: "B", quantity: 1, uom: "pcs", unitPrice: 100 }));
    po.submitForApproval();
    expect(() => po.addLine(POLine.create({ poId: po.id.value, lineNumber: 2, itemCode: "C", itemName: "D", quantity: 1, uom: "pcs", unitPrice: 200 }))).toThrow("non-draft");
  });

  it("submits, approves, sends, confirms lifecycle", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-004", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    po.addLine(POLine.create({ poId: po.id.value, lineNumber: 1, itemCode: "A", itemName: "B", quantity: 1, uom: "pcs", unitPrice: 100 }));

    po.submitForApproval();
    expect(po.status).toBe(POStatus.pendingApproval);

    po.approve("approver1");
    expect(po.status).toBe(POStatus.approved);

    po.send();
    expect(po.status).toBe(POStatus.sent);

    po.confirm("vendor1");
    expect(po.status).toBe(POStatus.confirmed);
  });

  it("cancels PO", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-005", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    po.cancel("No longer needed");
    expect(po.status).toBe(POStatus.cancelled);
  });

  it("holds and releases PO", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-006", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    po.hold("Budget freeze");
    expect(po.status).toBe(POStatus.onHold);
    po.release();
    expect(po.status).toBe(POStatus.approved);
  });

  it("rejects submit with no lines", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-007", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    expect(() => po.submitForApproval()).toThrow("no lines");
  });

  it("records receipt on line", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-008", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    const line = POLine.create({ poId: po.id.value, lineNumber: 1, itemCode: "A", itemName: "B", quantity: 10, uom: "pcs", unitPrice: 100 });
    po.addLine(line);
    line.recordReceipt(5);
    expect(line.receivedQuantity).toBe(5);
    expect(line.receiptStatus).toBe("partly_received");
    line.recordReceipt(5);
    expect(line.receiptStatus).toBe("fully_received");
  });

  it("rejects receipt exceeding quantity", () => {
    const line = POLine.create({ poId: "po1", lineNumber: 1, itemCode: "A", itemName: "B", quantity: 10, uom: "pcs", unitPrice: 100 });
    expect(() => line.recordReceipt(11)).toThrow("exceeds ordered");
  });

  it("round-trips through toState/load", () => {
    const po = PurchaseOrder.create({ poNumber: "PO-2024-009", companyId: "C001", vendorId: "V001", vendorName: "Test" });
    po.addLine(POLine.create({ poId: po.id.value, lineNumber: 1, itemCode: "A", itemName: "B", quantity: 5, uom: "pcs", unitPrice: 200 }));
    const state = po.toState();
    const loaded = PurchaseOrder.load(state);
    expect(loaded.poNumber).toBe("PO-2024-009");
    expect(loaded.totalAmount).toBe(1000);
  });
});
