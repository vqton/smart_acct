import { describe, it, expect } from "vitest";
import {
  TaxType, TaxCategory, TaxNature, TaxBasis, TaxCalculationMethod, TaxPaymentMethod, TaxFilingFrequency,
} from "../tax-type.js";

describe("TaxType", () => {
  it("creates VAT tax type", () => {
    const vat = new TaxType({
      code: "VAT", name: "Value Added Tax", category: TaxCategory.Consumption,
      nature: TaxNature.Indirect, basis: TaxBasis.ValueAdded,
      calculationMethod: TaxCalculationMethod.CreditMethod,
      paymentMethod: TaxPaymentMethod.Direct, filingFrequency: TaxFilingFrequency.Monthly,
    });
    const s = vat.toState();
    expect(s.code).toBe("VAT");
    expect(s.category).toBe(TaxCategory.Consumption);
    expect(s.isActive).toBe(true);
  });

  it("creates CIT tax type", () => {
    const cit = new TaxType({
      code: "CIT", name: "Corporate Income Tax", category: TaxCategory.Income,
      nature: TaxNature.Direct, basis: TaxBasis.TaxableIncome,
      calculationMethod: TaxCalculationMethod.Flat,
      paymentMethod: TaxPaymentMethod.Direct, filingFrequency: TaxFilingFrequency.Quarterly,
    });
    const s = cit.toState();
    expect(s.code).toBe("CIT");
    expect(s.calculationMethod).toBe(TaxCalculationMethod.Flat);
  });

  it("activates and deactivates", () => {
    const t = new TaxType({
      code: "TEST", name: "Test", category: TaxCategory.Other, nature: TaxNature.Direct,
      basis: TaxBasis.Other, calculationMethod: TaxCalculationMethod.Flat,
      paymentMethod: TaxPaymentMethod.Direct, filingFrequency: TaxFilingFrequency.Annual,
    });
    expect(t.toState().isActive).toBe(true);
    t.deactivate();
    expect(t.toState().isActive).toBe(false);
  });

  it("loads from state", () => {
    const t = new TaxType({
      code: "FBC", name: "Foreign Contractor Tax", category: TaxCategory.Other,
      nature: TaxNature.Direct, basis: TaxBasis.GrossRevenue,
      calculationMethod: TaxCalculationMethod.CreditMethod,
      paymentMethod: TaxPaymentMethod.Withholding, filingFrequency: TaxFilingFrequency.Monthly,
    });
    const state = t.toState();
    const loaded = TaxType.load(state);
    expect(loaded.toState()).toEqual(state);
    expect(loaded.id.value).toBe(t.id.value);
  });
});
