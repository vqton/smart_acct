import { describe, it, expect } from "vitest";
import { PayrollGroup } from "../payroll-group.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("PayrollGroup", () => {
  it("creates with valid params", () => {
    const g = PayrollGroup.create({ code: "PG01", name: "Monthly Payroll", companyId: "c1" });
    expect(g.code).toBe("PG01");
    expect(g.name).toBe("Monthly Payroll");
    expect(g.isActive).toBe(true);
    expect(g.payFrequency).toBe("monthly");
  });

  it("rejects empty code", () => {
    expect(() => PayrollGroup.create({ code: "", name: "Test", companyId: "c1" })).toThrow(DomainError);
  });

  it("rejects empty name", () => {
    expect(() => PayrollGroup.create({ code: "PG01", name: "", companyId: "c1" })).toThrow(DomainError);
  });

  it("updates fields", () => {
    const g = PayrollGroup.create({ code: "PG01", name: "Old Name", companyId: "c1" });
    g.update({ name: "New Name", currencyCode: "USD" });
    expect(g.name).toBe("New Name");
  });

  it("deactivates and activates", () => {
    const g = PayrollGroup.create({ code: "PG01", name: "Test", companyId: "c1" });
    g.deactivate();
    expect(g.isActive).toBe(false);
    expect(() => g.deactivate()).toThrow(DomainError);
    g.activate();
    expect(g.isActive).toBe(true);
  });

  it("serializes to/from state", () => {
    const g = PayrollGroup.create({ code: "PG01", name: "Test", companyId: "c1", branchId: "b1", payFrequency: "weekly" });
    const state = g.toState();
    const restored = PayrollGroup.load(state);
    expect(restored.code).toBe("PG01");
    expect(restored.name).toBe("Test");
    expect(restored.branchId).toBe("b1");
    expect(restored.payFrequency).toBe("weekly");
  });
});
