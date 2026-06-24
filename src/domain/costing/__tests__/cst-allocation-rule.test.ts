import { describe, it, expect } from "vitest";
import { AllocationRule } from "../cst-allocation-rule.js";
import { CstAllocationMethod, CstAllocationBasis } from "../cst-enums.js";

describe("AllocationRule", () => {
  it("creates percentage-based rule", () => {
    const rule = AllocationRule.create({
      code: "ALLOC-001", name: "Manufacturing OH to Prod Dept",
      poolId: "pool-1",
      allocationMethod: CstAllocationMethod.Percentage,
      allocationBasis: CstAllocationBasis.DirectLaborHours,
      percentage: 80,
    });
    expect(rule.code).toBe("ALLOC-001");
    const amt = rule.calculateAllocation(100000000);
    expect(amt).toBe(80000000);
  });

  it("creates fixed-amount rule", () => {
    const rule = AllocationRule.create({
      code: "ALLOC-002", name: "Fixed Admin Allocation",
      allocationMethod: CstAllocationMethod.Fixed,
      allocationBasis: CstAllocationBasis.Headcount,
      fixedAmount: 25000000,
    });
    const amt = rule.calculateAllocation(100000000);
    expect(amt).toBe(25000000);
  });

  it("creates direct method rule", () => {
    const rule = AllocationRule.create({
      code: "ALLOC-003", name: "Direct Allocation",
      allocationMethod: CstAllocationMethod.Direct,
      allocationBasis: CstAllocationBasis.MachineHours,
      basisValue: 1000,
    });
    const amt = rule.calculateAllocation(50000000);
    expect(amt).toBe(50000);
  });

  it("serializes and loads", () => {
    const rule = AllocationRule.create({
      code: "ALLOC-004", name: "Test Rule",
      allocationMethod: CstAllocationMethod.Percentage,
      allocationBasis: CstAllocationBasis.Revenue,
      percentage: 50,
    });
    const state = rule.toState();
    const loaded = AllocationRule.load(state);
    expect(loaded.code).toBe("ALLOC-004");
  });
});
