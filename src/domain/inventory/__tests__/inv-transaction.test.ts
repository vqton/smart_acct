import { describe, it, expect } from "vitest";
import { InventoryTransaction, TransactionLine } from "../inv-transaction.js";
import { InventoryTransactionType } from "../inv-enums.js";

describe("InventoryTransaction", () => {
  it("creates draft transaction", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR001", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    expect(tx.transactionNumber).toBe("GR001");
    expect(tx.status).toBe("draft");
  });

  it("adds lines", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR002", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    const line = TransactionLine.create({ transactionId: tx.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", quantity: 10, unitCost: 5, totalCost: 50 });
    tx.addLine(line);
    expect(tx.lines).toHaveLength(1);
    expect(tx.lines[0].quantity).toBe(10);
  });

  it("state machine: draft -> submitted -> approved -> posted", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR003", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    const line = TransactionLine.create({ transactionId: tx.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", quantity: 10, unitCost: 5, totalCost: 50 });
    tx.addLine(line);
    tx.submit("user1");
    expect(tx.status).toBe("submitted");
    tx.approve("user2");
    expect(tx.status).toBe("approved");
    tx.post("user3");
    expect(tx.status).toBe("posted");
  });

  it("rejects submit without lines", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR004", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    expect(() => tx.submit("user1")).toThrow("empty");
  });

  it("reverses posted transaction", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR005", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    const line = TransactionLine.create({ transactionId: tx.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", quantity: 10, unitCost: 5, totalCost: 50 });
    tx.addLine(line);
    tx.submit("user1");
    tx.approve("user2");
    tx.post("user3");
    const rev = tx.reverse("user4", "Error");
    expect(tx.status).toBe("reversed");
    expect(rev.transactionNumber).toBe("REV-GR005");
    expect(rev.lines[0].quantity).toBe(-10);
  });

  it("cancels draft", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR006", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    tx.cancel("user1", "No longer needed");
    expect(tx.status).toBe("cancelled");
  });

  it("rejects cancel of posted", () => {
    const tx = InventoryTransaction.create({
      transactionNumber: "GR007", transactionType: InventoryTransactionType.GoodsReceipt,
      companyId: "comp1", warehouseId: "wh1",
    });
    const line = TransactionLine.create({ transactionId: tx.id.value, lineNumber: 1, itemId: "item1", warehouseId: "wh1", quantity: 10, unitCost: 5, totalCost: 50 });
    tx.addLine(line);
    tx.submit("u1"); tx.approve("u2"); tx.post("u3");
    expect(() => tx.cancel("u4", "too late")).toThrow("Cannot cancel posted");
  });
});
