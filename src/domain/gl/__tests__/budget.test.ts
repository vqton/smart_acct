import { describe, it, expect } from "vitest";
import { Budget, BudgetType, BudgetStatus } from "../budget.js";

describe("Budget", () => {
  it("creates draft budget", () => {
    const b = Budget.create({
      code: "BUD-2026-001",
      name: "Operating Budget 2026",
      type: BudgetType.Operational,
      fiscalYearId: "fy-2026",
      createdById: "user-1",
    });
    expect(b.status).toBe(BudgetStatus.Draft);
    expect(b.totalOriginalAmount).toBe(0);
    expect(b.lines).toHaveLength(0);
  });

  it("adds budget lines", () => {
    const b = Budget.create({
      code: "BUD-2026-002",
      name: "Budget 2026",
      type: BudgetType.Operational,
      fiscalYearId: "fy-2026",
      createdById: "user-1",
    });
    b.addLine("acc-6411", 120000000);
    expect(b.lines).toHaveLength(1);
    expect(b.totalOriginalAmount).toBe(120000000);
    expect(b.lines[0].period1).toBe(10000000);
  });

  it("consumes budget", () => {
    const b = Budget.create({
      code: "BUD-2026-003",
      name: "Budget 2026",
      type: BudgetType.Operational,
      fiscalYearId: "fy-2026",
      createdById: "user-1",
    });
    b.addLine("acc-6411", 1000000);
    b.submit();
    b.approve("approver-1");
    b.consumeBudget("acc-6411", 500000, 1);
    expect(b.totalUsedAmount).toBe(500000);
    expect(b.totalRemainingAmount).toBe(500000);
  });

  it("rejects budget overshoot", () => {
    const b = Budget.create({
      code: "BUD-2026-004",
      name: "Budget 2026",
      type: BudgetType.Operational,
      fiscalYearId: "fy-2026",
      createdById: "user-1",
    });
    b.addLine("acc-6411", 100000);
    b.submit();
    b.approve("approver-1");
    expect(() => b.consumeBudget("acc-6411", 200000, 1)).toThrow("Budget exceeded");
  });

  it("prevents modifying after approval", () => {
    const b = Budget.create({
      code: "BUD-2026-005",
      name: "Budget 2026",
      type: BudgetType.Operational,
      fiscalYearId: "fy-2026",
      createdById: "user-1",
    });
    b.addLine("acc-6421", 50000);
    b.submit();
    b.approve("approver-1");
    expect(() => b.addLine("acc-6422", 30000)).toThrow("Cannot modify approved budget");
  });
});
