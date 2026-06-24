import { describe, it, expect } from "vitest";
import { StockBalance } from "../inv-stock.js";

describe("StockBalance", () => {
  it("creates with zero qty", () => {
    const sb = StockBalance.create("item1", "wh1");
    expect(sb.quantity).toBe(0);
    expect(sb.availableQty).toBe(0);
  });

  it("receive increases quantity", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.receive(100, 10, true);
    expect(sb.quantity).toBe(100);
    expect(sb.unitCost).toBe(10);
  });

  it("issue decreases quantity", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.receive(100, 10, true);
    sb.issue(30, true);
    expect(sb.quantity).toBe(70);
  });

  it("blocks negative inventory when not allowed", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.receive(10, 10, false);
    expect(() => sb.issue(20, false)).toThrow("Insufficient stock");
  });

  it("reserve reduces available", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.receive(100, 10, true);
    sb.reserve(30);
    expect(sb.reservedQty).toBe(30);
    expect(sb.availableQty).toBe(70);
  });

  it("transfer updates in transit", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.receive(100, 10, true);
    sb.transferOut(40);
    expect(sb.quantity).toBe(60);
    expect(sb.inTransitQty).toBe(40);
  });

  it("transfer in reduces in transit", () => {
    const sb = StockBalance.create("item1", "wh2");
    sb.transferIn(40, 10);
    expect(sb.quantity).toBe(40);
    expect(sb.inTransitQty).toBe(-40);
  });

  it("block/release cycle", () => {
    const sb = StockBalance.create("item1", "wh1");
    sb.block();
    expect(sb.stockStatus).toBe("blocked");
    sb.release();
    expect(sb.stockStatus).toBe("available");
  });

  it("serializes and loads", () => {
    const sb = StockBalance.create("item1", "wh1", "loc1", "lot1");
    sb.receive(50, 20, true);
    const state = sb.toState();
    const loaded = StockBalance.load(state);
    expect(loaded.quantity).toBe(50);
    expect(loaded.unitCost).toBe(20);
    expect(loaded.locationId).toBe("loc1");
    expect(loaded.lotId).toBe("lot1");
  });
});
