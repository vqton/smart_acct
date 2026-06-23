import { describe, it, expect } from "vitest";
import { FiscalYear, Period, FiscalYearId, PeriodId, PeriodStatus } from "../period.js";

describe("FiscalYear", () => {
  it("creates fiscal year with monthly periods", () => {
    const fy = new FiscalYear(
      FiscalYearId.new(),
      "FY2026",
      "Năm tài chính 2026",
      new Date("2026-01-01"),
      new Date("2026-12-31"),
    );
    fy.generatePeriods("monthly");
    expect(fy.periods).toHaveLength(12);
    expect(fy.periods[0].periodNumber).toBe(1);
    expect(fy.periods[0].name).toBe("Tháng 1");
    expect(fy.periods[11].periodNumber).toBe(12);
  });

  it("prevents closing with open periods", () => {
    const fy = new FiscalYear(
      FiscalYearId.new(),
      "FY2026",
      "FY 2026",
      new Date("2026-01-01"),
      new Date("2026-12-31"),
    );
    fy.generatePeriods("monthly");
    expect(() => fy.close("user-1")).toThrow("All periods must be closed");
  });
});

describe("Period", () => {
  it("rejects posting to closed period", () => {
    const p = new Period(
      PeriodId.new(), "fy-1", 1, "Period 1",
      new Date("2026-01-01"), new Date("2026-01-31"),
    );
    p.close("user-1");
    expect(() => p.canPost()).toThrow("closed");
  });

  it("rejects posting to locked period", () => {
    const p = new Period(
      PeriodId.new(), "fy-1", 2, "Period 2",
      new Date("2026-02-01"), new Date("2026-02-28"),
    );
    p.lock();
    expect(() => p.canPost()).toThrow("locked");
  });

  it("allows reopen of closed period", () => {
    const p = new Period(
      PeriodId.new(), "fy-1", 3, "Period 3",
      new Date("2026-03-01"), new Date("2026-03-31"),
    );
    p.close("user-1");
    expect(p.status).toBe(PeriodStatus.Closed);
    p.reopen();
    expect(p.status).toBe(PeriodStatus.Open);
  });
});
