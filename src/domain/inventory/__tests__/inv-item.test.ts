import { describe, it, expect } from "vitest";
import { Item } from "../inv-item.js";
import { ItemType, ItemCategory, ItemStatus, ItemValuationMethod, LotControl } from "../inv-enums.js";

describe("Item", () => {
  it("creates inventory item", () => {
    const item = Item.create({ code: "SP001", sku: "SKU001", name: "Test Item", uomId: "uom1" });
    expect(item.code).toBe("SP001");
    expect(item.sku).toBe("SKU001");
    expect(item.itemType).toBe(ItemType.Inventory);
    expect(item.status).toBe(ItemStatus.Active);
  });

  it("rejects duplicate delete", () => {
    const item = Item.create({ code: "SP002", sku: "SKU002", name: "Test", uomId: "uom1" });
    item.delete();
    expect(() => item.delete()).toThrow("already deleted");
  });

  it("changes status", () => {
    const item = Item.create({ code: "SP003", sku: "SKU003", name: "Test", uomId: "uom1" });
    item.changeStatus(ItemStatus.Discontinued);
    expect(item.status).toBe(ItemStatus.Discontinued);
  });

  it("updates fields", () => {
    const item = Item.create({ code: "SP004", sku: "SKU004", name: "Old Name", uomId: "uom1" });
    item.update({ name: "New Name", standardCost: 100 });
    expect(item.name).toBe("New Name");
    expect(item.standardCost).toBe(100);
  });

  it("serializes to state and loads back", () => {
    const item = Item.create({ code: "SP005", sku: "SKU005", name: "Test", uomId: "uom1", lotControl: LotControl.Serial });
    const state = item.toState();
    const loaded = Item.load(state);
    expect(loaded.code).toBe("SP005");
    expect(loaded.isSerialized).toBe(true);
  });
});
