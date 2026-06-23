import { describe, it, expect } from "vitest";
import { CashTransfer } from "../cm-cash-transfer.js";
import { CashTransferStatus } from "../cm-enums.js";

describe("CashTransfer", () => {
  it("creates draft transfer", () => {
    const t = CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc2", amount: 1000000, transferDate: new Date() });
    expect(t.transferNumber).toBe("T001");
    expect(t.status).toBe(CashTransferStatus.Draft);
  });

  it("rejects same location", () => {
    expect(() => CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc1", amount: 1000000, transferDate: new Date() }))
      .toThrow("different");
  });

  it("approves and sends", () => {
    const t = CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc2", amount: 1000000, transferDate: new Date() });
    t.approve("mgr1");
    expect(t.status).toBe(CashTransferStatus.Approved);
    t.send("sender1");
    expect(t.status).toBe(CashTransferStatus.InTransit);
    expect(t.sentById).toBe("sender1");
  });

  it("receives transfer", () => {
    const t = CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc2", amount: 1000000, transferDate: new Date() });
    t.approve("mgr1");
    t.send("sender1");
    t.receive("receiver1");
    expect(t.status).toBe(CashTransferStatus.Completed);
    expect(t.receivedById).toBe("receiver1");
    expect(t.actualArrivalDate).not.toBeNull();
  });

  it("cancels draft transfer", () => {
    const t = CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc2", amount: 1000000, transferDate: new Date() });
    t.cancel("changed mind");
    expect(t.status).toBe(CashTransferStatus.Cancelled);
  });

  it("rejects cancel completed", () => {
    const t = CashTransfer.create({ transferNumber: "T001", fromLocationId: "loc1", toLocationId: "loc2", amount: 1000000, transferDate: new Date() });
    t.approve("mgr1");
    t.send("s1");
    t.receive("r1");
    expect(() => t.cancel("already done")).toThrow("Cannot cancel completed");
  });
});
