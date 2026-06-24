import { describe, it, expect } from "vitest";
import { CostVersion } from "../cst-cost-version.js";
import { CstCostMethod } from "../cst-enums.js";

describe("CostVersion", () => {
  it("creates cost version", () => {
    const cv = CostVersion.create({
      code: "STD-2026", name: "Standard Cost 2026",
      costMethod: CstCostMethod.Standard,
      fiscalYearId: "fy-2026",
      effectiveFrom: new Date("2026-01-01"),
    });
    expect(cv.code).toBe("STD-2026");
    expect(cv.costMethod).toBe(CstCostMethod.Standard);
    expect(cv.isLocked).toBe(false);
  });

  it("locks cost version", () => {
    const cv = CostVersion.create({
      code: "STD-2026-B", name: "Standard Cost 2026 B",
      costMethod: CstCostMethod.Standard,
      fiscalYearId: "fy-2026",
      effectiveFrom: new Date("2026-01-01"),
    });
    cv.lock();
    expect(cv.isLocked).toBe(true);
  });

  it("rejects double lock", () => {
    const cv = CostVersion.create({
      code: "STD-2026-C", name: "Standard Cost 2026 C",
      costMethod: CstCostMethod.Standard,
      fiscalYearId: "fy-2026",
      effectiveFrom: new Date("2026-01-01"),
    });
    cv.lock();
    expect(() => cv.lock()).toThrow("already locked");
  });

  it("serializes to state and loads back", () => {
    const cv = CostVersion.create({
      code: "STD-2026-D", name: "Standard Cost 2026 D",
      costMethod: CstCostMethod.Average,
      fiscalYearId: "fy-2026",
      effectiveFrom: new Date("2026-01-01"),
      effectiveTo: new Date("2026-12-31"),
      description: "Test version",
    });
    const state = cv.toState();
    const loaded = CostVersion.load(state);
    expect(loaded.code).toBe("STD-2026-D");
    expect(loaded.costMethod).toBe(CstCostMethod.Average);
  });
});
