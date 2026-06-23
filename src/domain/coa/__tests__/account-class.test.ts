import { describe, it, expect } from "vitest";
import { AccountClass } from "../account-class.js";
import { AccountClassType } from "../coa-enums.js";

describe("AccountClass", () => {
  it("creates with valid code", () => {
    const c = AccountClass.create({ code: "1", name: "Tài sản", classType: AccountClassType.Asset });
    expect(c.code).toBe("1");
    expect(c.name).toBe("Tài sản");
    expect(c.classType).toBe(AccountClassType.Asset);
    expect(c.isActive).toBe(true);
  });

  it("rejects non-digit code", () => {
    expect(() => AccountClass.create({ code: "AB", name: "Test", classType: AccountClassType.Asset }))
      .toThrow("Account class code must be single digit");
  });

  it("loads from state", () => {
    const c = AccountClass.load({
      id: "test-id",
      code: "2",
      name: "Nợ phải trả",
      nameEn: "Liabilities",
      classType: AccountClassType.Liability,
      description: null,
      displayOrder: 2,
      isActive: true,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
    });
    expect(c.code).toBe("2");
    expect(c.nameEn).toBe("Liabilities");
  });

  it("round-trips through toState", () => {
    const c = AccountClass.create({ code: "3", name: "VCSH", classType: AccountClassType.Equity, displayOrder: 3 });
    const state = c.toState();
    expect(state.code).toBe("3");
    expect(state.displayOrder).toBe(3);
    const loaded = AccountClass.load(state);
    expect(loaded.code).toBe(c.code);
    expect(loaded.id.value).toBe(c.id.value);
  });
});
