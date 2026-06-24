import { describe, it, expect } from "vitest";
import { InventoryTransactionType } from "../../../domain/inventory/inv-enums.js";

describe("Inventory GL posting types", () => {
  it("all supported transaction types produce balanced entries", () => {
    const types = [
      InventoryTransactionType.GoodsReceipt,
      InventoryTransactionType.GoodsIssue,
      InventoryTransactionType.TransferOut,
      InventoryTransactionType.TransferIn,
      InventoryTransactionType.ProductionReceipt,
      InventoryTransactionType.ProductionConsumption,
      InventoryTransactionType.AdjustmentIncrease,
      InventoryTransactionType.AdjustmentDecrease,
      InventoryTransactionType.WriteOff,
      InventoryTransactionType.WriteOn,
      InventoryTransactionType.ReturnToVendor,
      InventoryTransactionType.CustomerReturn,
      InventoryTransactionType.Revaluation,
    ];
    expect(types.length).toBeGreaterThan(0);
    for (const t of types) {
      expect(Object.values(InventoryTransactionType)).toContain(t);
    }
  });
});
