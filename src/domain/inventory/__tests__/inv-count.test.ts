import { describe, it, expect } from "vitest";
import { StockCount, CountLine } from "../inv-count.js";

describe("StockCount", () => {
  it("creates count", () => {
    const sc = StockCount.create({ countNumber: "CNT001", companyId: "comp1", warehouseId: "wh1" });
    expect(sc.countNumber).toBe("CNT001");
    expect(sc.status).toBe("planned");
  });

  it("full lifecycle", () => {
    const sc = StockCount.create({ countNumber: "CNT002", companyId: "comp1", warehouseId: "wh1" });
    const line1 = CountLine.create({ countId: sc.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", expectedQty: 100, unitCost: 10 });
    const line2 = CountLine.create({ countId: sc.id.value, lineNumber: 2, itemId: "item2", warehouseId: "wh1", expectedQty: 50, unitCost: 20 });
    sc.addLine(line1);
    sc.addLine(line2);

    sc.freeze();
    expect(sc.status).toBe("frozen");

    sc.startCounting();
    expect(sc.status).toBe("in_progress");

    const l1 = sc.lines[0];
    l1.recordCount(95, "counter1");
    l1.approve();
    const l2 = sc.lines[1];
    l2.recordCount(55, "counter1");
    l2.approve();

    sc.complete();
    expect(sc.status).toBe("completed");
    expect(l1.varianceQty).toBe(-5);
    expect(l2.varianceQty).toBe(5);
  });
});
