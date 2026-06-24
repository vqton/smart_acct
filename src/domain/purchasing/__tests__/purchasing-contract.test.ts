import { describe, it, expect } from "vitest";
import { PurchaseContract } from "../purchasing-contract.js";
import { ContractStatus, ContractType } from "../purchasing-enums.js";

describe("PurchaseContract", () => {
  it("creates a contract", () => {
    const c = PurchaseContract.create({
      contractNumber: "CT-001", companyId: "C001", vendorId: "V001", vendorName: "Supplier",
      title: "Annual Supply Agreement", startDate: new Date(), endDate: new Date("2025-12-31"),
      totalValue: 500000000,
    });
    expect(c.contractNumber).toBe("CT-001");
    expect(c.status).toBe(ContractStatus.draft);
    expect(c.totalValue).toBe(500000000);
  });

  it("activates contract", () => {
    const c = PurchaseContract.create({
      contractNumber: "CT-002", companyId: "C001", vendorId: "V001", vendorName: "Supplier",
      title: "Test", startDate: new Date(), endDate: new Date("2025-12-31"),
    });
    c.activate();
    expect(c.status).toBe(ContractStatus.active);
  });

  it("records spend", () => {
    const c = PurchaseContract.create({
      contractNumber: "CT-003", companyId: "C001", vendorId: "V001", vendorName: "Supplier",
      title: "Test", startDate: new Date(), endDate: new Date("2025-12-31"),
      totalValue: 100000000,
    });
    c.recordSpend(30000000);
    expect(c.amountSpent).toBe(30000000);
    expect(c.amountRemaining).toBe(70000000);
  });

  it("amends contract", () => {
    const c = PurchaseContract.create({
      contractNumber: "CT-004", companyId: "C001", vendorId: "V001", vendorName: "Supplier",
      title: "Test", startDate: new Date(), endDate: new Date("2025-12-31"),
    });
    c.activate();
    c.amend({ totalValue: 200000000 });
    expect(c.status).toBe(ContractStatus.amended);
    expect(c.totalValue).toBe(200000000);
  });

  it("terminates contract", () => {
    const c = PurchaseContract.create({
      contractNumber: "CT-005", companyId: "C001", vendorId: "V001", vendorName: "Supplier",
      title: "Test", startDate: new Date(), endDate: new Date("2025-12-31"),
    });
    c.terminate();
    expect(c.status).toBe(ContractStatus.terminated);
  });
});
