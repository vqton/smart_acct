import { describe, it, expect } from "vitest";
import { VoucherSeries, VoucherSeriesId, SequenceMethod } from "../voucher.js";

describe("VoucherSeries", () => {
  it("reserves sequential numbers", () => {
    const vs = new VoucherSeries(
      VoucherSeriesId.new(),
      "vt-payment",
      "PC",
      "Phiếu chi",
      "PC",
      SequenceMethod.Annual,
      5,
    );
    const n1 = vs.reserve();
    expect(n1).toMatch(/^PC20\d{2}\d{5}$/);
    const n2 = vs.reserve();
    const num2 = parseInt(n2.replace(/^PC20\d{2}/, ""));
    const num1 = parseInt(n1.replace(/^PC20\d{2}/, ""));
    expect(num2).toBe(num1 + 1);
    expect(vs.currentNumber).toBeGreaterThan(0);
  });

  it("rejects reserve on inactive series", () => {
    const vs = new VoucherSeries(
      VoucherSeriesId.new(),
      "vt-pt",
      "PT",
      "Phiếu thu",
      "PT",
    );
    vs["_isActive"] = false as any;
    expect(() => vs.reserve()).toThrow("inactive");
  });
});
