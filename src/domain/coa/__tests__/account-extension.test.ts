import { describe, it, expect } from "vitest";
import { AccountExtension } from "../account-extension.js";
import {
  AccountEffectiveStatus, AccountControlLevel, DimensionRequirement,
} from "../coa-enums.js";

describe("AccountExtension", () => {
  it("creates with default values", () => {
    const e = AccountExtension.create("acc-1");
    expect(e.accountId).toBe("acc-1");
    expect(e.effectiveStatus).toBe(AccountEffectiveStatus.Active);
    expect(e.allowAutoPosting).toBe(true);
    expect(e.isCashAccount).toBe(false);
  });

  it("updates status", () => {
    const e = AccountExtension.create("acc-1");
    e.updateEffectiveStatus(AccountEffectiveStatus.Suspended, "Under review");
    expect(e.effectiveStatus).toBe(AccountEffectiveStatus.Suspended);
    expect(e.statusReason).toBe("Under review");
  });

  it("prevents modifying closed account", () => {
    const e = AccountExtension.create("acc-1");
    e.updateEffectiveStatus(AccountEffectiveStatus.Closed, "Year-end close");
    expect(() => e.updateEffectiveStatus(AccountEffectiveStatus.Active)).toThrow("closed account");
  });

  it("prevents modifying archived account", () => {
    const e = AccountExtension.create("acc-1");
    e.updateEffectiveStatus(AccountEffectiveStatus.Closed, "Close");
    e.updateEffectiveStatus(AccountEffectiveStatus.Archived, "Archive");
    expect(() => e.updateEffectiveStatus(AccountEffectiveStatus.Active)).toThrow("archived account");
  });

  it("marks as cash account", () => {
    const e = AccountExtension.create("acc-1");
    e.markAsCashAccount("CF01");
    expect(e.isCashAccount).toBe(true);
    expect(e.cashFlowCode).toBe("CF01");
  });

  it("marks as bank account", () => {
    const e = AccountExtension.create("acc-1");
    e.markAsBankAccount();
    expect(e.isBankAccount).toBe(true);
  });

  it("marks as tax account", () => {
    const e = AccountExtension.create("acc-1");
    e.markAsTaxAccount("tax-code-1");
    expect(e.isTaxAccount).toBe(true);
    expect(e.defaultTaxCodeId).toBe("tax-code-1");
  });

  it("sets dimension requirements", () => {
    const e = AccountExtension.create("acc-1");
    e.setDimensionRequirement("costCenter", DimensionRequirement.Required);
    e.setDimensionRequirement("project", DimensionRequirement.Prohibited);
    expect(e.costCenterRequired).toBe(DimensionRequirement.Required);
    expect(e.projectRequired).toBe(DimensionRequirement.Prohibited);
  });

  it("sets budget control", () => {
    const e = AccountExtension.create("acc-1");
    e.setBudgetControl(AccountControlLevel.Strict, "Must not exceed approved budget");
    expect(e.budgetControlLevel).toBe(AccountControlLevel.Strict);
    expect(e.budgetCheckMessage).toBe("Must not exceed approved budget");
  });

  it("loads from state", () => {
    const e = AccountExtension.load({
      id: "ext-1",
      accountId: "acc-1",
      typeId: "type-1",
      effectiveStatus: AccountEffectiveStatus.Draft,
      effectiveFrom: null,
      effectiveTo: null,
      statusReason: null,
      allowAutoPosting: false,
      requireApproval: true,
      budgetControlLevel: AccountControlLevel.Warning,
      budgetCheckMessage: null,
      defaultCostCenterId: null,
      defaultDepartmentId: null,
      defaultProjectId: null,
      defaultBranchId: null,
      costCenterRequired: DimensionRequirement.Optional,
      departmentRequired: DimensionRequirement.Optional,
      projectRequired: DimensionRequirement.Optional,
      branchRequired: DimensionRequirement.Optional,
      profitCenterRequired: DimensionRequirement.Optional,
      isCashAccount: false,
      isBankAccount: true,
      isTaxAccount: false,
      isInventoryAccount: false,
      isReceivableAccount: false,
      isPayableAccount: false,
      isIntercompanyAccount: false,
      defaultTaxCodeId: null,
      defaultTaxRateId: null,
      cashFlowCode: null,
      financialStatementCode: null,
      financialStatementNote: null,
      createdById: null,
      updatedById: null,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
    });
    expect(e.effectiveStatus).toBe(AccountEffectiveStatus.Draft);
    expect(e.isBankAccount).toBe(true);
  });
});
