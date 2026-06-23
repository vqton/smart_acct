import { describe, it, expect, vi } from "vitest";
import {
  TaxCalculationEngine, TaxCalculationRequest, TaxDeterminationEngine,
  TransactionSide, TaxDeterminationRule,
} from "../tax-calculation.js";
import {
  TaxCode, TaxRate, TaxRateApplication, RoundingMethod, TaxRateType,
} from "../tax-code.js";

function makeTaxCode(code: string, rate: number, app: TaxRateApplication = TaxRateApplication.Exclusive): TaxCode {
  const tc = new TaxCode(code, `Tax ${code}`, "vat-1", TaxRateType.Percentage, app, new Date("2024-01-01"));
  tc.addRate(TaxRate.create(tc.id.value, rate, TaxRateType.Percentage, new Date("2024-01-01")));
  return tc;
}

describe("TaxCalculationEngine", () => {
  const code10 = makeTaxCode("VAT10", 10);
  const code5 = makeTaxCode("VAT5", 5);
  const code8 = makeTaxCode("VAT8", 8);

  const mockGetTaxCode = vi.fn(async (id: string) => {
    const map: Record<string, TaxCode> = { "vat10": code10, "vat5": code5, "vat8": code8 };
    return map[id] ?? null;
  });
  const mockGetExemptions = vi.fn(async () => []);

  const engine = new TaxCalculationEngine(mockGetTaxCode, mockGetExemptions);

  const baseReq: TaxCalculationRequest = {
    transactionId: "tx-1",
    transactionDate: new Date("2025-06-01"),
    side: TransactionSide.Sales,
    lines: [
      {
        lineId: "line-1", itemCode: "ITEM001", description: "Product A",
        quantity: 10, unitPrice: 100000, netAmount: 1000000,
        discountAmount: 0, discountPercent: 0,
        taxCodeId: "vat10", taxCode: "VAT10",
        isExempt: false, isZeroRated: false, isService: false,
        productCategory: "electronics", originCountry: "VN", hsCode: "8471",
        metadata: {},
      },
    ],
    currencyCode: "VND", exchangeRate: 1,
  };

  it("calculates single line exclusive tax", async () => {
    const result = await engine.calculate(baseReq);
    expect(result.totalTaxableAmount).toBe(1000000);
    expect(result.totalTaxAmount).toBe(100000);
    expect(result.lines[0].taxRate).toBe(10);
  });

  it("handles exempt line", async () => {
    const req: TaxCalculationRequest = {
      ...baseReq,
      lines: [{ ...baseReq.lines[0], isExempt: true, taxCodeId: "vat10" }],
    };
    const result = await engine.calculate(req);
    expect(result.lines[0].isExempt).toBe(true);
    expect(result.lines[0].taxAmount).toBe(0);
    expect(result.totalTaxAmount).toBe(0);
  });

  it("handles zero-rated line", async () => {
    const req: TaxCalculationRequest = {
      ...baseReq,
      lines: [{ ...baseReq.lines[0], isZeroRated: true, taxCodeId: "vat10" }],
    };
    const result = await engine.calculate(req);
    expect(result.lines[0].isZeroRated).toBe(true);
    expect(result.lines[0].taxAmount).toBe(0);
  });

  it("throws on unknown tax code", async () => {
    const req: TaxCalculationRequest = {
      ...baseReq,
      lines: [{ ...baseReq.lines[0], taxCodeId: "nonexistent" }],
    };
    await expect(engine.calculate(req)).rejects.toThrow();
  });

  it("calculates multiple lines", async () => {
    const req: TaxCalculationRequest = {
      ...baseReq,
      lines: [
        { ...baseReq.lines[0], lineId: "l1", netAmount: 200000, taxCodeId: "vat10" },
        { ...baseReq.lines[0], lineId: "l2", netAmount: 300000, taxCodeId: "vat5" },
      ],
    };
    const result = await engine.calculate(req);
    expect(result.totalTaxableAmount).toBe(500000);
    expect(result.totalTaxAmount).toBe(20000 + 15000);
    expect(result.lines.length).toBe(2);
  });
});

describe("TaxDeterminationEngine", () => {
  it("matches rules by conditions", () => {
    const engine = new TaxDeterminationEngine();
    const rule: TaxDeterminationRule = {
      id: "rule-1", name: "Electronics VAT 10%", taxCodeId: "vat10", priority: 10,
      conditions: [
        { field: "productCategory", operator: "eq", value: "electronics" },
        { field: "isImport", operator: "eq", value: false },
      ],
      effectiveFrom: new Date("2024-01-01"), effectiveTo: null,
    };
    engine.addRule(rule);

    const matches = engine.determine({
      transactionDate: new Date("2025-01-01"), side: TransactionSide.Sales,
      productCategory: "electronics", hsCode: "8471", originCountry: "VN",
      isExport: false, isImport: false, freeTradeZone: false, metadata: {},
    });
    expect(matches.length).toBe(1);
    expect(matches[0].taxCodeId).toBe("vat10");
  });

  it("returns empty on no match", () => {
    const engine = new TaxDeterminationEngine();
    const matches = engine.determine({
      transactionDate: new Date("2025-01-01"), side: TransactionSide.Sales,
      productCategory: "food", hsCode: "2106", originCountry: "VN",
      isExport: false, isImport: false, freeTradeZone: false, metadata: {},
    });
    expect(matches.length).toBe(0);
  });

  it("respects effective dates", () => {
    const engine = new TaxDeterminationEngine();
    engine.addRule({
      id: "r1", name: "Old rule", taxCodeId: "vat10", priority: 10,
      conditions: [{ field: "productCategory", operator: "eq", value: "old" }],
      effectiveFrom: new Date("2023-01-01"), effectiveTo: new Date("2023-12-31"),
    });

    const matches = engine.determine({
      transactionDate: new Date("2024-01-01"), side: TransactionSide.Purchase,
      productCategory: "old", hsCode: "0000", originCountry: "VN",
      isExport: false, isImport: false, freeTradeZone: false, metadata: {},
    });
    expect(matches.length).toBe(0);
  });
});
