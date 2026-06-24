import { describe, it, expect } from "vitest";
import { Bom, BomLine, BomRouting } from "../cst-bom.js";
import { CstCostElementType } from "../cst-enums.js";

describe("Bom", () => {
  it("creates BOM", () => {
    const bom = Bom.create({
      code: "BOM-001", name: "Widget Assembly",
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
    });
    expect(bom.code).toBe("BOM-001");
    expect(bom.totalCost()).toBe(0);
  });

  it("adds lines", () => {
    const bom = Bom.create({
      code: "BOM-002", name: "Widget Assembly",
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
    });
    const line = BomLine.create({
      bomId: bom.id.value, lineNumber: 10,
      componentItemId: "comp-1", componentCode: "SC-001", componentName: "Screw",
      quantity: 4, unitCost: 500,
    });
    bom.addLine(line);
    expect(bom.lines.length).toBe(1);
    expect(bom.totalMaterialCost()).toBe(2000);
  });

  it("adds routings", () => {
    const bom = Bom.create({
      code: "BOM-003", name: "Widget Assembly",
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
    });
    const routing = BomRouting.create({
      bomId: bom.id.value, operationSeq: 10,
      operationDescription: "Cutting", laborRate: 50000, runTime: 0.5,
    });
    bom.addRouting(routing);
    expect(bom.routings.length).toBe(1);
  });

  it("calculates total cost", () => {
    const bom = Bom.create({
      code: "BOM-004", name: "Widget Assembly",
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
    });
    bom.addLine(BomLine.create({
      bomId: bom.id.value, lineNumber: 10,
      componentItemId: "comp-1", componentCode: "SC-001", componentName: "Screw",
      quantity: 4, unitCost: 500,
    }));
    bom.addRouting(BomRouting.create({
      bomId: bom.id.value, operationSeq: 10,
      operationDescription: "Assembly", laborRate: 60000, runTime: 1,
    }));
    expect(bom.totalMaterialCost()).toBe(2000);
    expect(bom.totalRoutingCost()).toBe(60000);
    expect(bom.totalCost()).toBe(62000);
  });

  it("serializes and loads", () => {
    const bom = Bom.create({
      code: "BOM-005", name: "Widget Assembly",
      itemId: "item-1", itemCode: "WD-001", itemName: "Widget",
    });
    const state = bom.toState();
    const loaded = Bom.load(state);
    expect(loaded.code).toBe("BOM-005");
  });
});
