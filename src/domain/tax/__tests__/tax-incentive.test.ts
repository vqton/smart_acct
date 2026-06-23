import { describe, it, expect } from "vitest";
import { TaxExemption, IncentiveType, IncentiveApplicationLevel } from "../tax-incentive.js";

describe("TaxExemption", () => {
  it("creates a tax exemption", () => {
    const e = new TaxExemption("EXEMPT-EDU", "Education exemption", IncentiveType.Exemption, "vat-1", IncentiveApplicationLevel.TaxType, new Date("2024-01-01"));
    const s = e.toState();
    expect(s.code).toBe("EXEMPT-EDU");
    expect(s.incentiveType).toBe(IncentiveType.Exemption);
  });

  it("applies full exemption", () => {
    const e = new TaxExemption("EXEMPT-MED", "Medical exemption", IncentiveType.Exemption, "vat-1", IncentiveApplicationLevel.Product, new Date("2024-01-01"));
    expect(e.apply(100000, new Date("2025-01-01"))).toBe(0);
  });

  it("applies reduction percentage", () => {
    const e = new TaxExemption("REDUCE-SME", "SME reduction", IncentiveType.Reduction, "cit-1", IncentiveApplicationLevel.Taxpayer, new Date("2024-01-01"));
    const state = e.toState();
    const reducer = TaxExemption.load({ ...state, reductionPercent: 30 });
    const result = reducer.apply(1000000, new Date("2025-01-01"));
    expect(result).toBe(700000);
  });

  it("applies fixed amount reduction", () => {
    const e = new TaxExemption("FIXED", "Fixed reduction", IncentiveType.Reduction, "cit-1", IncentiveApplicationLevel.Taxpayer, new Date("2024-01-01"));
    const state = e.toState();
    const reducer = TaxExemption.load({ ...state, reductionAmount: 200000 });
    expect(reducer.apply(500000, new Date("2025-01-01"))).toBe(300000);
  });

  it("does not reduce below zero", () => {
    const e = new TaxExemption("FIXED-HIGH", "High fixed reduction", IncentiveType.Reduction, "cit-1", IncentiveApplicationLevel.Taxpayer, new Date("2024-01-01"));
    const state = e.toState();
    const reducer = TaxExemption.load({ ...state, reductionAmount: 999999 });
    expect(reducer.apply(100000, new Date("2025-01-01"))).toBe(0);
  });

  it("returns full tax when inactive", () => {
    const e = new TaxExemption("INACTIVE", "Inactive exemption", IncentiveType.Exemption, "vat-1", IncentiveApplicationLevel.TaxType, new Date("2024-01-01"));
    const state = e.toState();
    const inactive = TaxExemption.load({ ...state, isActive: false });
    expect(inactive.apply(50000, new Date("2025-01-01"))).toBe(50000);
  });

  it("returns full tax when out of effective period", () => {
    const e = new TaxExemption("EXPIRED", "Expired", IncentiveType.Exemption, "vat-1", IncentiveApplicationLevel.TaxType, new Date("2023-01-01"));
    const state = e.toState();
    const expired = TaxExemption.load({ ...state, effectiveTo: new Date("2023-12-31") });
    expect(expired.apply(50000, new Date("2025-01-01"))).toBe(50000);
  });

  it("loads from state", () => {
    const e = new TaxExemption("LOAD", "Load test", IncentiveType.Credit, "cit-1", IncentiveApplicationLevel.Taxpayer, new Date("2024-06-01"));
    const state = e.toState();
    const loaded = TaxExemption.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});
