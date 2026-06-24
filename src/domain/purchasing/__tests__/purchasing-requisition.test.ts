import { describe, it, expect } from "vitest";
import { PurchaseRequisition, RequisitionItem } from "../purchasing-requisition.js";
import { RequisitionStatus } from "../purchasing-enums.js";

describe("PurchaseRequisition", () => {
  it("creates a requisition", () => {
    const pr = PurchaseRequisition.create({ prNumber: "PR-001", companyId: "C001", requesterId: "R001" });
    expect(pr.prNumber).toBe("PR-001");
    expect(pr.status).toBe(RequisitionStatus.draft);
  });

  it("adds items and calculates total", () => {
    const pr = PurchaseRequisition.create({ prNumber: "PR-002", companyId: "C001", requesterId: "R001" });
    const item = RequisitionItem.create({ requisitionId: pr.id.value, lineNumber: 1, itemCode: "A", itemName: "Item A", quantity: 5, uom: "pcs", estimatedUnitPrice: 2000 });
    pr.addItem(item);
    expect(pr.items.length).toBe(1);
    expect(pr.totalEstimated).toBe(10000);
  });

  it("submits and approves", () => {
    const pr = PurchaseRequisition.create({ prNumber: "PR-003", companyId: "C001", requesterId: "R001" });
    pr.addItem(RequisitionItem.create({ requisitionId: pr.id.value, lineNumber: 1, itemCode: "A", itemName: "A", quantity: 1, uom: "pcs", estimatedUnitPrice: 100 }));
    pr.submit();
    expect(pr.status).toBe(RequisitionStatus.submitted);
    pr.approve("manager1");
    expect(pr.status).toBe(RequisitionStatus.approved);
  });

  it("rejects submit of empty requisition", () => {
    const pr = PurchaseRequisition.create({ prNumber: "PR-004", companyId: "C001", requesterId: "R001" });
    expect(() => pr.submit()).toThrow("empty");
  });

  it("cancels requisition", () => {
    const pr = PurchaseRequisition.create({ prNumber: "PR-005", companyId: "C001", requesterId: "R001" });
    pr.cancel("No budget");
    expect(pr.status).toBe(RequisitionStatus.cancelled);
  });
});
