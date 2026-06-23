import { describe, it, expect } from "vitest";
import { AccountMapping } from "../account-mapping.js";
import { AccountMappingStandard, AccountMappingType } from "../coa-enums.js";

describe("AccountMapping", () => {
  it("creates with required fields", () => {
    const m = AccountMapping.create({
      accountId: "acc-1",
      mappingStandard: AccountMappingStandard.Ifrs,
      mappingType: AccountMappingType.Direct,
      targetCode: "1101",
      effectiveFrom: new Date("2025-01-01"),
    });
    expect(m.mappingStandard).toBe(AccountMappingStandard.Ifrs);
    expect(m.targetCode).toBe("1101");
    expect(m.isActive).toBe(true);
  });

  it("supports deactivation", () => {
    const m = AccountMapping.create({
      accountId: "acc-1",
      mappingStandard: AccountMappingStandard.Vas,
      mappingType: AccountMappingType.Direct,
      targetCode: "111",
      effectiveFrom: new Date("2025-01-01"),
    });
    expect(m.isActive).toBe(true);
    m.deactivate();
    expect(m.isActive).toBe(false);
  });

  it("round-trips through toState", () => {
    const m = AccountMapping.create({
      accountId: "acc-1",
      mappingStandard: AccountMappingStandard.CashFlow,
      mappingType: AccountMappingType.Percentage,
      targetCode: "CF01",
      targetName: "Cash receipts",
      percentage: 100,
      effectiveFrom: new Date("2025-01-01"),
    });
    const state = m.toState();
    expect(state.targetCode).toBe("CF01");
    expect(state.percentage).toBe(100);
    const loaded = AccountMapping.load(state);
    expect(loaded.percentage).toBe(100);
  });
});
