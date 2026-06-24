import { describe, it, expect } from "vitest";
import { WorkCenter } from "../cst-work-center.js";

describe("WorkCenter", () => {
  it("creates work center", () => {
    const wc = WorkCenter.create({
      code: "WC-001", name: "Assembly Line 1",
      hourlyRate: 50000, machineRate: 100000, overheadRate: 15000,
    });
    expect(wc.code).toBe("WC-001");
    expect(wc.hourlyRate).toBe(50000);
    expect(wc.machineRate).toBe(100000);
    expect(wc.overheadRate).toBe(15000);
  });

  it("serializes and loads", () => {
    const wc = WorkCenter.create({
      code: "WC-002", name: "Machining Center",
      workCenterType: "machining",
      hourlyRate: 60000, machineRate: 200000,
    });
    const state = wc.toState();
    const loaded = WorkCenter.load(state);
    expect(loaded.code).toBe("WC-002");
    expect(loaded.hourlyRate).toBe(60000);
  });
});
