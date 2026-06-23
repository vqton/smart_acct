import { describe, it, expect } from "vitest";
import { CashAdvance, AdvanceSettlement } from "../cm-cash-advance.js";
import { CashAdvanceStatus } from "../cm-enums.js";
import { AdvanceSettlementId } from "../cm-ids.js";

describe("CashAdvance", () => {
  it("creates draft advance", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "Nguyen Van A", amount: 5000000, advanceDate: new Date(), purpose: "Business trip" });
    expect(a.advanceNumber).toBe("ADV001");
    expect(a.status).toBe(CashAdvanceStatus.Draft);
    expect(a.outstandingAmount).toBe(5000000);
  });

  it("approves advance", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "A", amount: 5000000, advanceDate: new Date(), purpose: "Trip" });
    a.approve("mgr1");
    expect(a.status).toBe(CashAdvanceStatus.Approved);
  });

  it("disburses approved advance", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "A", amount: 5000000, advanceDate: new Date(), purpose: "Trip" });
    a.approve("mgr1");
    a.disburse("cashier1");
    expect(a.status).toBe(CashAdvanceStatus.Disbursed);
  });

  it("settles advance partially then fully", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "A", amount: 5000000, advanceDate: new Date(), purpose: "Trip" });
    a.approve("mgr1");
    a.disburse("cashier1");

    const s1 = new AdvanceSettlement(AdvanceSettlementId.new(), a.id.value, "SET001", new Date(), 2000000, 500000, 1500000, "VND");
    a.settle(s1);
    expect(a.status).toBe(CashAdvanceStatus.PartiallySettled);
    expect(a.settledAmount).toBe(2000000);
    expect(a.outstandingAmount).toBe(3000000);

    const s2 = new AdvanceSettlement(AdvanceSettlementId.new(), a.id.value, "SET002", new Date(), 3000000, 0, 3000000, "VND");
    a.settle(s2);
    expect(a.status).toBe(CashAdvanceStatus.Settled);
    expect(a.outstandingAmount).toBe(0);
  });

  it("rejects settle amount mismatch", () => {
    expect(() => new AdvanceSettlement(AdvanceSettlementId.new(), "aid", "SET001", new Date(), 5000000, 3000000, 1000000, "VND"))
      .toThrow("Total must equal return + expense");
  });

  it("cancels draft advance", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "A", amount: 5000000, advanceDate: new Date(), purpose: "Trip" });
    a.cancel();
    expect(a.status).toBe(CashAdvanceStatus.Cancelled);
  });

  it("rejects cancel disbursed", () => {
    const a = CashAdvance.create({ advanceNumber: "ADV001", companyId: "c1", employeeId: "emp1", employeeName: "A", amount: 5000000, advanceDate: new Date(), purpose: "Trip" });
    a.approve("mgr1");
    a.disburse("cashier1");
    expect(() => a.cancel()).toThrow("must settle");
  });
});
