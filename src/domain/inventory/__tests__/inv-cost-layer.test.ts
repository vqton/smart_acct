import { describe, it, expect } from "vitest";
import { CostLayer } from "../inv-cost-layer.js";

describe("CostLayer", () => {
  it("creates with initial quantity", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 100, unitCost: 10, transactionId: "tx1" });
    expect(cl.remainingQty).toBe(100);
    expect(cl.unitCost).toBe(10);
    expect(cl.isConsumed).toBe(false);
  });

  it("consume reduces remaining", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 100, unitCost: 10, transactionId: "tx1" });
    cl.consume(30, "tx2");
    expect(cl.remainingQty).toBe(70);
    expect(cl.isConsumed).toBe(false);
  });

  it("full consume marks consumed", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 100, unitCost: 10, transactionId: "tx1" });
    cl.consume(100, "tx2");
    expect(cl.remainingQty).toBe(0);
    expect(cl.isConsumed).toBe(true);
  });

  it("rejects over-consume", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 50, unitCost: 10, transactionId: "tx1" });
    expect(() => cl.consume(60, "tx2")).toThrow("Cannot consume more");
  });

  it("split creates new layer", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 100, unitCost: 10, transactionId: "tx1" });
    const split = cl.split(40);
    expect(cl.remainingQty).toBe(60);
    expect(split.remainingQty).toBe(40);
    expect(split.unitCost).toBe(10);
  });

  it("serializes and loads", () => {
    const cl = CostLayer.create({ itemId: "item1", warehouseId: "wh1", quantity: 100, unitCost: 10, transactionId: "tx1" });
    cl.consume(30, "tx2");
    const state = cl.toState();
    const loaded = CostLayer.load(state);
    expect(loaded.remainingQty).toBe(70);
    expect(loaded.unitCost).toBe(10);
  });
});
