import { describe, it, expect } from "vitest";
import {
  TaxCode, TaxRate, TaxRateId, TaxRateApplication, TaxRateType, RoundingMethod,
} from "../tax-code.js";

describe("TaxCode", () => {
  it("creates VAT 10% standard rate", () => {
    const tc = new TaxCode("VAT10", "VAT 10%", "vat-1", TaxRateType.Percentage, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    const s = tc.toState();
    expect(s.code).toBe("VAT10");
    expect(s.isActive).toBe(true);
  });

  it("adds and retrieves effective rates", () => {
    const tc = new TaxCode("VAT8", "VAT 8%", "vat-1", TaxRateType.Percentage, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    const rate = TaxRate.create(tc.id.value, 8, TaxRateType.Percentage, new Date("2024-01-01"));
    tc.addRate(rate);
    const found = tc.getEffectiveRate(new Date("2024-06-01"));
    expect(found).not.toBeUndefined();
    expect(found!.rate).toBe(8);

    const older = tc.getEffectiveRate(new Date("2023-01-01"));
    expect(older).toBeUndefined();
  });

  it("calculates exclusive tax", () => {
    const tc = new TaxCode("VAT10", "VAT 10%", "vat-1", TaxRateType.Percentage, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    tc.addRate(TaxRate.create(tc.id.value, 10, TaxRateType.Percentage, new Date("2024-01-01")));
    const result = tc.calculate(1000, new Date("2024-06-01"));
    expect(result.taxAmount).toBe(100);
    expect(result.rate.rate).toBe(10);
  });

  it("calculates inclusive tax", () => {
    const tc = new TaxCode("VAT10INC", "VAT 10% Inclusive", "vat-1", TaxRateType.Percentage, TaxRateApplication.Inclusive, new Date("2024-01-01"));
    tc.addRate(TaxRate.create(tc.id.value, 10, TaxRateType.Percentage, new Date("2024-01-01")));
    const result = tc.calculate(1100, new Date("2024-06-01"));
    expect(result.taxAmount).toBe(100);
  });

  it("calculates flat amount tax per unit", () => {
    const tc = new TaxCode("STAMP", "Stamp Duty", "stamp-1", TaxRateType.PerUnit, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    tc.addRate(TaxRate.create(tc.id.value, 5000, TaxRateType.PerUnit, new Date("2024-01-01")));
    const result = tc.calculate(0, new Date("2024-06-01"), 10);
    expect(result.taxAmount).toBe(50000);
  });

  it("applies rounding to nearest integer", () => {
    const tc = new TaxCode("VAT8", "VAT 8%", "vat-1", TaxRateType.Percentage, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    tc.addRate(TaxRate.create(tc.id.value, 8, TaxRateType.Percentage, new Date("2024-01-01")));
    const result = tc.calculate(999, new Date("2024-06-01"));
    expect(result.taxAmount).toBe(80);
  });

  it("loads from state", () => {
    const tc = new TaxCode("VAT5", "VAT 5%", "vat-1", TaxRateType.Percentage, TaxRateApplication.Exclusive, new Date("2024-01-01"));
    tc.addRate(TaxRate.create(tc.id.value, 5, TaxRateType.Percentage, new Date("2024-01-01")));
    const state = tc.toState();
    const loaded = TaxCode.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});

describe("TaxRate", () => {
  it("creates a rate", () => {
    const r = TaxRate.create("tc-1", 10, TaxRateType.Percentage, new Date("2024-01-01"));
    const s = r.toState();
    expect(s.rateType).toBe(TaxRateType.Percentage);
    expect(s.rate).toBe(10);
  });
});
