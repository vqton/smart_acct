import { describe, it, expect } from "vitest";
import { Formula } from "../fr-formula.js";
import { FrFormulaType } from "../fr-enums.js";

describe("Formula", () => {
  it("creates with simple formula", () => {
    const f = Formula.create({
      code: "GROSS_PROFIT",
      name: "Gross Profit",
      expression: "SUM(ACCOUNT(511), ACCOUNT(512)) - ACCOUNT(632)",
      createdById: "user-1",
    });
    expect(f.code).toBe("GROSS_PROFIT");
    expect(f.formulaType).toBe(FrFormulaType.Simple);
    expect(f.expression).toBe("SUM(ACCOUNT(511), ACCOUNT(512)) - ACCOUNT(632)");
    expect(f.isActive).toBe(true);
  });

  it("updates expression", () => {
    const f = Formula.create({
      code: "NET_PROFIT",
      name: "Net Profit",
      expression: "GROSS_PROFIT - SUM(ACCOUNT(641), ACCOUNT(642))",
      createdById: "user-1",
    });
    f.updateExpression("GROSS_PROFIT - SUM(ACCOUNT(641), ACCOUNT(642), ACCOUNT(635))");
    expect(f.expression).toContain("ACCOUNT(635)");
  });

  it("deactivates formula", () => {
    const f = Formula.create({
      code: "CURRENT_RATIO",
      name: "Current Ratio",
      expression: "ACCOUNT(111) / ACCOUNT(311)",
      createdById: "user-1",
    });
    f.deactivate();
    expect(f.isActive).toBe(false);
  });

  it("round-trips through toState and load", () => {
    const f = Formula.create({
      code: "QUICK_RATIO",
      name: "Quick Ratio",
      formulaType: FrFormulaType.Percentage,
      expression: "(ACCOUNT(111) + ACCOUNT(112)) / ACCOUNT(311)",
      createdById: "user-1",
    });
    f.deactivate();

    const state = f.toState();
    const loaded = Formula.load(state);
    expect(loaded.code).toBe("QUICK_RATIO");
    expect(loaded.formulaType).toBe(FrFormulaType.Percentage);
    expect(loaded.isActive).toBe(false);
  });
});
