import { describe, it, expect } from "vitest";
import { ProductionOrder, ProductionOrderComponent, ProductionOrderOperation } from "../cst-production-order.js";
import { CstProductionOrderStatus, CstCostElementType } from "../cst-enums.js";

describe("ProductionOrder", () => {
  it("creates planned order", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-001", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    expect(po.orderNumber).toBe("PO-001");
    expect(po.status).toBe(CstProductionOrderStatus.Planned);
    expect(po.quantity).toBe(100);
  });

  it("adds components", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-002", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    const comp = ProductionOrderComponent.create({
      orderId: po.id.value, lineNumber: 10,
      componentItemId: "comp-1", componentCode: "SC-001",
      componentName: "Screw", requiredQty: 400, unitCost: 500,
    });
    po.addComponent(comp);
    expect(po.components.length).toBe(1);
  });

  it("adds operations", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-003", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    const op = ProductionOrderOperation.create({
      orderId: po.id.value, operationSeq: 10, operationName: "Assembly",
      laborRate: 50000, runTime: 2, overheadRate: 10000,
    });
    po.addOperation(op);
    expect(po.operations.length).toBe(1);
  });

  it("releases order", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-004", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    po.release("user-1");
    expect(po.status).toBe(CstProductionOrderStatus.Released);
  });

  it("rejects release from wrong state", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-005", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    po.release("user-1");
    expect(() => po.release("user-1")).toThrow("Only planned orders can be released");
  });

  it("issues component", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-006", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    const comp = ProductionOrderComponent.create({
      orderId: po.id.value, lineNumber: 10,
      componentItemId: "comp-1", componentCode: "SC-001",
      componentName: "Screw", requiredQty: 400, unitCost: 500,
    });
    po.addComponent(comp);
    po.release("user-1");
    po.issueComponent(comp.id.value, 400, 550);
    expect(po.actualMaterialCost).toBe(220000);
  });

  it("completes operation", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-007", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
      estimatedLaborCost: 100000, estimatedMachineCost: 50000,
    });
    const op = ProductionOrderOperation.create({
      orderId: po.id.value, operationSeq: 10, operationName: "Assembly",
      laborRate: 50000, runTime: 2, machineRate: 25000,
    });
    po.addOperation(op);
    po.release("user-1");
    po.completeOperation(op.id.value, 1.5, 2.5);
    expect(op.isCompleted).toBe(true);
  });

  it("completes order and records variances", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-008", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
      estimatedMaterialCost: 200000, estimatedLaborCost: 100000,
    });
    const comp = ProductionOrderComponent.create({
      orderId: po.id.value, lineNumber: 10,
      componentItemId: "comp-1", componentCode: "SC-001",
      componentName: "Screw", requiredQty: 400, unitCost: 500,
    });
    po.addComponent(comp);
    const op = ProductionOrderOperation.create({
      orderId: po.id.value, operationSeq: 10, operationName: "Assembly",
      laborRate: 50000, runTime: 2,
    });
    po.addOperation(op);

    po.release("user-1");
    po.issueComponent(comp.id.value, 400, 550);
    po.completeOperation(op.id.value, 0, 2);
    po.complete("user-1");

    expect(po.status).toBe(CstProductionOrderStatus.Completed);
    expect(po.totalVariance).not.toBe(0);
  });

  it("closes completed order", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-009", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    const op = ProductionOrderOperation.create({
      orderId: po.id.value, operationSeq: 10, operationName: "Assembly",
      laborRate: 50000, runTime: 2,
    });
    po.addOperation(op);
    po.release("user-1");
    po.completeOperation(op.id.value, 1.5, 2.5);
    po.complete("user-1");
    po.close("user-1");
    expect(po.status).toBe(CstProductionOrderStatus.Closed);
  });

  it("rejects close from non-completed state", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-010", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    expect(() => po.close("user-1")).toThrow("Only completed orders can be closed");
  });

  it("serializes and loads", () => {
    const po = ProductionOrder.create({
      orderNumber: "PO-011", itemId: "item-1", itemCode: "WD-001",
      itemName: "Widget", quantity: 100,
      plannedStartDate: new Date("2026-06-01"), companyId: "comp-1",
    });
    const state = po.toState();
    const loaded = ProductionOrder.load(state);
    expect(loaded.orderNumber).toBe("PO-011");
    expect(loaded.quantity).toBe(100);
  });
});
