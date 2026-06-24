import { describe, it, expect } from "vitest";
import { CostSnapshot, CostSnapshotLine } from "../cst-cost-snapshot.js";
import { CstCostSnapshotType, CstCostMethod } from "../cst-enums.js";

describe("CostSnapshot", () => {
  it("creates snapshot", () => {
    const snap = CostSnapshot.create({
      snapshotNumber: "SNAP-2026-06",
      snapshotType: CstCostSnapshotType.PeriodClose,
      periodId: "period-06",
      fiscalYearId: "fy-2026",
    });
    expect(snap.snapshotNumber).toBe("SNAP-2026-06");
    expect(snap.isFrozen).toBe(false);
  });

  it("adds lines", () => {
    const snap = CostSnapshot.create({
      snapshotNumber: "SNAP-2026-07",
      snapshotType: CstCostSnapshotType.CostFreeze,
      periodId: "period-07",
    });
    const line = CostSnapshotLine.create({
      snapshotId: snap.id.value,
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
      quantity: 100, unitCost: 50000,
    });
    snap.addLine(line);
    expect(snap.lines.length).toBe(1);
    expect(snap.totalCost).toBe(5000000);
    expect(snap.totalQuantity).toBe(100);
  });

  it("freezes snapshot", () => {
    const snap = CostSnapshot.create({
      snapshotNumber: "SNAP-2026-08",
      snapshotType: CstCostSnapshotType.PeriodClose,
    });
    snap.freeze("user-1");
    expect(snap.isFrozen).toBe(true);
  });

  it("rejects double freeze", () => {
    const snap = CostSnapshot.create({
      snapshotNumber: "SNAP-2026-09",
      snapshotType: CstCostSnapshotType.PeriodClose,
    });
    snap.freeze("user-1");
    expect(() => snap.freeze("user-2")).toThrow("already frozen");
  });

  it("serializes and loads", () => {
    const snap = CostSnapshot.create({
      snapshotNumber: "SNAP-2026-10",
      snapshotType: CstCostSnapshotType.CostFreeze,
    });
    const state = snap.toState();
    const loaded = CostSnapshot.load(state);
    expect(loaded.snapshotNumber).toBe("SNAP-2026-10");
  });
});
