import { describe, it, expect } from "vitest";
import { ProductionVariance } from "../cst-prod-variance.js";
import { CstVarianceType, CstCostElementType } from "../cst-enums.js";

describe("ProductionVariance", () => {
  it("creates variance with difference", () => {
    const pv = ProductionVariance.create({
      orderId: "po-1",
      varianceType: CstVarianceType.MaterialPrice,
      costElement: CstCostElementType.Material,
      standardAmount: 200000,
      actualAmount: 220000,
    });
    expect(pv.varianceAmount).toBe(20000);
  });

  it("serializes and loads", () => {
    const pv = ProductionVariance.create({
      orderId: "po-2",
      varianceType: CstVarianceType.LaborEfficiency,
      costElement: CstCostElementType.Labor,
      standardAmount: 100000,
      actualAmount: 90000,
    });
    const state = pv.toState();
    const loaded = ProductionVariance.load(state);
    expect(loaded.varianceAmount).toBe(-10000);
  });
});
