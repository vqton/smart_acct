import { describe, it, expect } from "vitest";
import { InsuranceRate } from "../insurance-rate.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("InsuranceRate", () => {
  it("creates with valid params", () => {
    const ir = InsuranceRate.create({
      insuranceType: "social_insurance", name: "BHXH",
      effectiveFrom: new Date("2024-01-01"), eeRate: 0.08, erRate: 0.175,
    });
    expect(ir.insuranceType).toBe("social_insurance");
    expect(ir.eeRate).toBe(0.08);
  });

  it("rejects negative rates", () => {
    expect(() => InsuranceRate.create({
      insuranceType: "social_insurance", name: "BHXH",
      effectiveFrom: new Date("2024-01-01"), eeRate: -0.01, erRate: 0.175,
    })).toThrow(DomainError);
  });

  it("calculates employee contribution with ceiling", () => {
    const ir = InsuranceRate.create({
      insuranceType: "social_insurance", name: "BHXH",
      effectiveFrom: new Date("2024-01-01"), eeRate: 0.08, erRate: 0.175,
      ceilingAmount: 46800000n,
    });
    const contrib = ir.calculateEmployeeContribution(50000000n);
    expect(contrib).toBeLessThanOrEqual(46800000n * 8n / 100n + 1n);
  });

  it("calculates employer contribution", () => {
    const ir = InsuranceRate.create({
      insuranceType: "social_insurance", name: "BHXH",
      effectiveFrom: new Date("2024-01-01"), eeRate: 0.08, erRate: 0.175,
    });
    const contrib = ir.calculateEmployerContribution(20000000n);
    expect(contrib).toBeGreaterThan(0n);
  });

  it("serializes to/from state", () => {
    const ir = InsuranceRate.create({
      insuranceType: "health_insurance", name: "BHYT",
      effectiveFrom: new Date("2024-01-01"), eeRate: 0.015, erRate: 0.03,
      regulationRef: "Luật BHYT sửa đổi 2024",
    });
    const state = ir.toState();
    const restored = InsuranceRate.load(state);
    expect(restored.insuranceType).toBe("health_insurance");
    expect(restored.regulationRef).toBe("Luật BHYT sửa đổi 2024");
  });
});
