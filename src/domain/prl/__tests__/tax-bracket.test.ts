import { describe, it, expect } from "vitest";
import { TaxBracket } from "../tax-bracket.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("TaxBracket", () => {
  it("creates with valid params", () => {
    const tb = TaxBracket.create({
      name: "Bậc 1", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 1, fromAmount: 0n, toAmount: 5000000n, rate: 0.05, deductAmount: 0n,
    });
    expect(tb.bracketOrder).toBe(1);
    expect(tb.rate).toBe(0.05);
  });

  it("rejects invalid rate", () => {
    expect(() => TaxBracket.create({
      name: "Invalid", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 1, fromAmount: 0n, rate: 1.5, deductAmount: 0n,
    })).toThrow(DomainError);
  });

  it("contains income within bracket", () => {
    const tb = TaxBracket.create({
      name: "Bậc 1", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 1, fromAmount: 0n, toAmount: 5000000n, rate: 0.05, deductAmount: 0n,
    });
    expect(tb.contains(3000000n)).toBe(true);
    expect(tb.contains(6000000n)).toBe(false);
    expect(tb.contains(0n)).toBe(true);
  });

  it("contains income in open-ended bracket", () => {
    const tb = TaxBracket.create({
      name: "Bậc 7", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 7, fromAmount: 80000000n, rate: 0.35, deductAmount: 9850000n,
    });
    expect(tb.contains(80000000n)).toBe(true);
    expect(tb.contains(100000000n)).toBe(true);
    expect(tb.contains(70000000n)).toBe(false);
  });

  it("calculates tax within bracket", () => {
    const tb = TaxBracket.create({
      name: "Bậc 1", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 1, fromAmount: 0n, toAmount: 5000000n, rate: 0.05, deductAmount: 0n,
    });
    const tax = tb.calculateTax(3000000n);
    expect(tax).toBeGreaterThan(0n);
  });

  it("returns zero tax for income not in bracket", () => {
    const tb = TaxBracket.create({
      name: "Bậc 1", effectiveFrom: new Date("2024-01-01"),
      bracketOrder: 1, fromAmount: 0n, toAmount: 5000000n, rate: 0.05, deductAmount: 0n,
    });
    expect(tb.calculateTax(10000000n)).toBe(0n);
  });

  it("serializes to/from state", () => {
    const tb = TaxBracket.create({
      name: "Bậc 3", effectiveFrom: new Date("2024-07-01"),
      bracketOrder: 3, fromAmount: 10000000n, toAmount: 18000000n, rate: 0.15, deductAmount: 750000n,
    });
    const state = tb.toState();
    const restored = TaxBracket.load(state);
    expect(restored.bracketOrder).toBe(3);
    expect(restored.rate).toBe(0.15);
    expect(restored.deductAmount).toBe(750000n);
  });
});
