import { describe, it, expect } from "vitest";
import { AccountType } from "../account-type.js";
import { AccountTypeCategory } from "../coa-enums.js";
import { AccountNature } from "../../gl/account-category.js";

describe("AccountType", () => {
  it("creates with required fields", () => {
    const t = AccountType.create({
      classId: "class-1",
      code: "111",
      name: "Tiền mặt",
      category: AccountTypeCategory.CurrentAsset,
      nature: AccountNature.Debit,
    });
    expect(t.code).toBe("111");
    expect(t.name).toBe("Tiền mặt");
    expect(t.category).toBe(AccountTypeCategory.CurrentAsset);
  });

  it("loads from state", () => {
    const t = AccountType.load({
      id: "type-1",
      classId: "class-1",
      code: "112",
      name: "Tiền gửi NH",
      nameEn: "Bank deposits",
      category: AccountTypeCategory.CurrentAsset,
      subType: null,
      nature: AccountNature.Debit,
      description: null,
      parentTypeId: null,
      isActive: true,
      displayOrder: 0,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
    });
    expect(t.code).toBe("112");
  });

  it("round-trips through toState", () => {
    const t = AccountType.create({
      classId: "class-2",
      code: "331",
      name: "Phải trả người bán",
      category: AccountTypeCategory.CurrentLiability,
      nature: AccountNature.Credit,
    });
    const state = t.toState();
    expect(state.code).toBe("331");
    const loaded = AccountType.load(state);
    expect(loaded.code).toBe(t.code);
    expect(loaded.id.value).toBe(t.id.value);
  });
});
