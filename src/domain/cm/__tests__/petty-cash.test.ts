import { describe, it, expect } from "vitest";
import { PettyCash } from "../cm-petty-cash.js";
import { PettyCashStatus } from "../cm-enums.js";

describe("PettyCash", () => {
  it("creates petty cash fund", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office Petty Cash", maximumBalance: 5000000, minimumBalance: 500000 });
    expect(f.fundCode).toBe("PC001");
    expect(f.status).toBe(PettyCashStatus.Active);
    expect(f.fundBalance).toBe(0);
  });

  it("replenishes fund", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office", maximumBalance: 5000000, minimumBalance: 500000 });
    const r = f.replenish(3000000, "REF001");
    expect(f.fundBalance).toBe(3000000);
    expect(r.amount).toBe(3000000);
  });

  it("disburses from fund", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office", maximumBalance: 5000000, minimumBalance: 500000 });
    f.replenish(3000000, "REF001");
    f.disburse(1000000);
    expect(f.fundBalance).toBe(2000000);
  });

  it("rejects over-disbursement", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office", maximumBalance: 5000000, minimumBalance: 500000 });
    expect(() => f.disburse(100000)).toThrow("Insufficient");
  });

  it("detects replenishment need", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office", maximumBalance: 5000000, minimumBalance: 500000 });
    f.replenish(2000000, "R1");
    expect(f.needsReplenishment()).toBe(false);
    f.disburse(1000000);
    expect(f.fundBalance).toBe(1000000);
    expect(f.needsReplenishment()).toBe(true);
  });

  it("enforces max balance on replenish", () => {
    const f = PettyCash.create({ locationId: "loc1", fundCode: "PC001", fundName: "Office", maximumBalance: 5000000, minimumBalance: 500000 });
    f.replenish(3000000, "R1");
    expect(() => f.replenish(3000000, "R2")).toThrow("exceed maximum balance");
  });
});
