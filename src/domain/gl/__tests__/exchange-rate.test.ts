import { describe, it, expect } from "vitest";
import { ExchangeRate, ExchangeRateType, ExchangeRateId } from "../exchange-rate.js";

describe("ExchangeRate", () => {
  it("creates valid rate", () => {
    const er = new ExchangeRate(
      ExchangeRateId.new(), "USD", "VND", 25400,
      ExchangeRateType.Reference,
      new Date("2026-01-01"), new Date("2026-12-31"),
    );
    expect(er.rate).toBe(25400);
    expect(er.fromCurrency).toBe("USD");
    expect(er.toCurrency).toBe("VND");
  });

  it("rejects zero or negative rate", () => {
    expect(() => new ExchangeRate(
      ExchangeRateId.new(), "USD", "VND", -1,
      ExchangeRateType.Reference,
      new Date(), new Date(),
    )).toThrow("must be positive");
  });

  it("checks validity by date", () => {
    const er = new ExchangeRate(
      ExchangeRateId.new(), "USD", "EUR", 0.92,
      ExchangeRateType.Reference,
      new Date("2026-01-01"), new Date("2026-06-30"),
    );
    expect(er.isValidAt(new Date("2026-03-15"))).toBe(true);
    expect(er.isValidAt(new Date("2025-12-31"))).toBe(false);
    expect(er.isValidAt(new Date("2026-07-01"))).toBe(false);
  });

  it("converts amount correctly", () => {
    const er = new ExchangeRate(
      ExchangeRateId.new(), "USD", "VND", 25400,
      ExchangeRateType.Reference,
      new Date(), new Date("2026-12-31"),
    );
    expect(er.convert(100)).toBe(2540000);
  });
});
