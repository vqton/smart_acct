import { describe, it, expect } from "vitest";
import { CashPosition, CashForecast, FXRate, FXRevaluation } from "../bank-treasury.js";
import { CashPositionStatus, FXRateType } from "../bank-enums.js";
import { FXRateId } from "../bank-ids.js";

describe("CashPosition", () => {
  it("creates cash position", () => {
    const c = CashPosition.create({ companyId: "c1", positionDate: new Date() });
    expect(c.status).toBe(CashPositionStatus.Draft);
    expect(c.closingBalance).toBe(0);
  });

  it("adds inflows and outflows", () => {
    const c = CashPosition.create({ companyId: "c1", positionDate: new Date(), openingBalance: 100000000 });
    c.addInflow(50000000);
    c.addOutflow(20000000);
    expect(c.closingBalance).toBe(130000000);
  });

  it("rejects negative inflow", () => {
    const c = CashPosition.create({ companyId: "c1", positionDate: new Date() });
    expect(() => c.addInflow(-1000)).toThrow("must be positive");
  });

  it("advances through statuses", () => {
    const c = CashPosition.create({ companyId: "c1", positionDate: new Date() });
    expect(c.status).toBe(CashPositionStatus.Draft);
    c.confirm();
    expect(c.status).toBe(CashPositionStatus.Confirmed);
    c.approve();
    expect(c.status).toBe(CashPositionStatus.Approved);
    c.lock();
    expect(c.status).toBe(CashPositionStatus.Locked);
  });

  it("round-trips through toState/load", () => {
    const c = CashPosition.create({ companyId: "c1", positionDate: new Date(), openingBalance: 50000000 });
    c.addInflow(10000000);
    const state = c.toState();
    const loaded = CashPosition.load(state);
    expect(loaded.closingBalance).toBe(60000000);
  });
});

describe("CashForecast", () => {
  it("creates forecast", () => {
    const f = CashForecast.create({
      companyId: "c1", forecastNumber: "FC001", name: "Q1 Forecast",
      periodStart: new Date("2024-01-01"), periodEnd: new Date("2024-03-31"),
      currencyCode: "VND",
    });
    expect(f.id).toBeDefined();
    expect(f.status).toBe(CashPositionStatus.Draft);
  });

  it("round-trips through toState/load", () => {
    const f = CashForecast.create({
      companyId: "c1", forecastNumber: "FC002", name: "Feb Forecast",
      periodStart: new Date("2024-02-01"), periodEnd: new Date("2024-02-29"),
      currencyCode: "VND",
    });
    f.confirm();
    const state = f.toState();
    const loaded = CashForecast.load(state);
    expect(loaded.status).toBe(CashPositionStatus.Confirmed);
  });
});

describe("FXRate", () => {
  it("creates FX rate", () => {
    const r = new FXRate(
      new FXRateId("fx-1"), "USD", "VND", 25400, FXRateType.Transfer,
      new Date("2024-01-01"), new Date("2024-12-31"), "SBV", true,
    );
    expect(r.rate).toBe(25400);
    expect(r.rateType).toBe(FXRateType.Transfer);
    expect(r.isActive).toBe(true);
  });

  it("checks effective date", () => {
    const r = new FXRate(
      new FXRateId("fx-2"), "USD", "VND", 25400, FXRateType.Transfer,
      new Date("2024-01-01"), new Date("2024-12-31"), "SBV", true,
    );
    expect(r.isEffective(new Date("2024-06-15"))).toBe(true);
    expect(r.isEffective(new Date("2023-01-01"))).toBe(false);
  });
});

describe("FXRevaluation", () => {
  it("creates FX revaluation", () => {
    const r = FXRevaluation.create({
      companyId: "c1", revaluationDate: new Date(),
      currencyCode: "USD", exchangeRate: 25400, previousRate: 25000,
      accountId: "acct1", accountBalance: 10000,
    });
    expect(r.fxGainLoss).toBeGreaterThan(0);
    expect(r.gainLossType).toBe("gain");
  });

  it("creates FX revaluation with loss", () => {
    const r = FXRevaluation.create({
      companyId: "c1", revaluationDate: new Date(),
      currencyCode: "USD", exchangeRate: 25000, previousRate: 25400,
      accountId: "acct1", accountBalance: 10000,
    });
    expect(r.fxGainLoss).toBeLessThan(0);
    expect(r.gainLossType).toBe("loss");
  });

  it("marks GL posted", () => {
    const r = FXRevaluation.create({
      companyId: "c1", revaluationDate: new Date(),
      currencyCode: "USD", exchangeRate: 25400, previousRate: 25000,
      accountId: "acct1", accountBalance: 10000,
    });
    r.markGLPosted("batch-gl-1");
  });

  it("round-trips through toState/load", () => {
    const r = FXRevaluation.create({
      companyId: "c1", revaluationDate: new Date(),
      currencyCode: "USD", exchangeRate: 25400, previousRate: 25000,
      accountId: "acct1", accountBalance: 10000,
    });
    const state = r.toState();
    const loaded = FXRevaluation.load(state);
    expect(loaded.fxGainLoss).toBe(r.fxGainLoss);
    expect(loaded.gainLossType).toBe(r.gainLossType);
  });
});
