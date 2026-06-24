import { describe, it, expect } from "vitest";
import { InventoryReservation, ReservationLine } from "../inv-reservation.js";

describe("InventoryReservation", () => {
  it("creates active reservation", () => {
    const resv = InventoryReservation.create({
      reservationNumber: "RSV001", orderType: "sales_order",
      orderId: "SO001", companyId: "comp1",
    });
    expect(resv.reservationNumber).toBe("RSV001");
    expect(resv.status).toBe("active");
  });

  it("fulfills when all lines fulfilled", () => {
    const resv = InventoryReservation.create({
      reservationNumber: "RSV002", orderType: "sales_order",
      orderId: "SO002", companyId: "comp1",
    });
    const line = ReservationLine.create({ reservationId: resv.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", quantity: 10 });
    resv.addLine(line);
    line.fulfill(10);
    resv.fulfill();
    expect(resv.status).toBe("fulfilled");
  });

  it("cancels and releases", () => {
    const resv = InventoryReservation.create({
      reservationNumber: "RSV003", orderType: "sales_order",
      orderId: "SO003", companyId: "comp1",
    });
    resv.cancel("Customer cancelled");
    expect(resv.status).toBe("cancelled");
  });

  it("expires", () => {
    const resv = InventoryReservation.create({
      reservationNumber: "RSV004", orderType: "sales_order",
      orderId: "SO004", companyId: "comp1",
    });
    resv.expire();
    expect(resv.status).toBe("expired");
  });
});
