import { describe, it, expect } from "vitest";
import { SalaryComponent } from "../salary-component.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("SalaryComponent", () => {
  it("creates with valid params", () => {
    const sc = SalaryComponent.create({ code: "BASIC", name: "Lương cơ bản", elementType: "base_salary", category: "earning" });
    expect(sc.code).toBe("BASIC");
    expect(sc.category).toBe("earning");
    expect(sc.isTaxable).toBe(true);
  });

  it("rejects empty code", () => {
    expect(() => SalaryComponent.create({ code: "", name: "Test", elementType: "base_salary", category: "earning" })).toThrow(DomainError);
  });

  it("sets insurable components", () => {
    const sc = SalaryComponent.create({ code: "SI", name: "BHXH", elementType: "social_insurance_ee", category: "insurance", isInsurable: true, isTaxable: false });
    expect(sc.isInsurable).toBe(true);
    expect(sc.isTaxable).toBe(false);
  });

  it("serializes to/from state", () => {
    const sc = SalaryComponent.create({ code: "ALLOW", name: "Phụ cấp", elementType: "allowance_fixed", category: "earning", priority: 5 });
    const state = sc.toState();
    const restored = SalaryComponent.load(state);
    expect(restored.code).toBe("ALLOW");
    expect(restored.priority).toBe(5);
  });
});
