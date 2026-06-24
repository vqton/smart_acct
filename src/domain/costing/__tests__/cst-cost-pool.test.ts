import { describe, it, expect } from "vitest";
import { CostPool } from "../cst-cost-pool.js";
import { CstCostPoolType } from "../cst-enums.js";

describe("CostPool", () => {
  it("creates cost pool", () => {
    const pool = CostPool.create({
      code: "OH-MFG", name: "Manufacturing Overhead",
      poolType: CstCostPoolType.Production,
      totalAmount: 100000000,
    });
    expect(pool.code).toBe("OH-MFG");
    expect(pool.totalAmount).toBe(100000000);
    expect(pool.unallocatedAmount).toBe(100000000);
  });

  it("allocates amount", () => {
    const pool = CostPool.create({
      code: "OH-ADMIN", name: "Admin Overhead",
      poolType: CstCostPoolType.Administration,
      totalAmount: 50000000,
    });
    pool.allocate(20000000);
    expect(pool.allocatedAmount).toBe(20000000);
    expect(pool.unallocatedAmount).toBe(30000000);
  });

  it("serializes and loads", () => {
    const pool = CostPool.create({
      code: "OH-SALES", name: "Selling Overhead",
      poolType: CstCostPoolType.Selling,
      totalAmount: 30000000,
    });
    const state = pool.toState();
    const loaded = CostPool.load(state);
    expect(loaded.code).toBe("OH-SALES");
    expect(loaded.totalAmount).toBe(30000000);
  });
});
