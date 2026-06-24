import { describe, it, expect } from "vitest";
import { OverheadRate } from "../cst-overhead-rate.js";
import { CstCostPoolType, CstAllocationBasis } from "../cst-enums.js";

describe("OverheadRate", () => {
  it("creates overhead rate", () => {
    const rate = OverheadRate.create({
      code: "OHR-001", name: "Labor Overhead Rate",
      costPoolType: CstCostPoolType.LaborOverhead,
      allocationBasis: CstAllocationBasis.DirectLaborHours,
      rate: 1.5, rateType: "percentage",
    });
    expect(rate.code).toBe("OHR-001");
    expect(rate.rate).toBe(1.5);
    expect(rate.rateType).toBe("percentage");
  });

  it("serializes and loads", () => {
    const rate = OverheadRate.create({
      code: "OHR-002", name: "Machining Overhead",
      costPoolType: CstCostPoolType.MachineOverhead,
      allocationBasis: CstAllocationBasis.MachineHours,
      rate: 250000, rateType: "per_unit",
    });
    const state = rate.toState();
    const loaded = OverheadRate.load(state);
    expect(loaded.code).toBe("OHR-002");
    expect(loaded.rate).toBe(250000);
  });
});
