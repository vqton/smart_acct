import { describe, it, expect } from "vitest";
import { PostingAccountSpec, ManualEntryAllowedSpec, ActiveStatusSpec, EffectiveDateSpec, validateAccountCode, validateHierarchyCycle } from "../coa-specifications.js";
import { AccountEffectiveStatus } from "../coa-enums.js";
import { AccountCategory, AccountNature } from "../../gl/account-category.js";

describe("PostingAccountSpec", () => {
  const spec = new PostingAccountSpec();

  it("allows active posting account", () => {
    expect(spec.isSatisfiedBy({
      id: "1", code: "1111", name: "Cash", category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit, parentId: null, isActive: true, isControl: false,
      isPosting: true, allowManualEntry: true, balance: 0, foreignBalance: 0,
      currencyCode: null, description: null, nameEn: null, createdAt: new Date(),
      updatedAt: new Date(), version: 1, deletedAt: null,
    })).toBe(true);
  });

  it("rejects inactive account", () => {
    expect(spec.isSatisfiedBy({
      id: "1", code: "1111", name: "Cash", category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit, parentId: null, isActive: false, isControl: false,
      isPosting: true, allowManualEntry: true, balance: 0, foreignBalance: 0,
      currencyCode: null, description: null, nameEn: null, createdAt: new Date(),
      updatedAt: new Date(), version: 1, deletedAt: null,
    })).toBe(false);
  });
});

describe("validateAccountCode", () => {
  it("accepts valid codes", () => {
    expect(() => validateAccountCode("1")).not.toThrow();
    expect(() => validateAccountCode("1111")).not.toThrow();
    expect(() => validateAccountCode("9999999")).not.toThrow();
  });

  it("rejects invalid codes", () => {
    expect(() => validateAccountCode("")).toThrow();
    expect(() => validateAccountCode("12345678")).toThrow();
    expect(() => validateAccountCode("ABC")).toThrow();
  });
});

describe("validateHierarchyCycle", () => {
  const makeAccount = (id: string, parentId: string | null) => ({
    id, code: id, name: `Account ${id}`, nameEn: null,
    category: AccountCategory.ShortTermAsset, nature: AccountNature.Debit,
    parentId, isActive: true, isControl: false, isPosting: true,
    allowManualEntry: true, balance: 0, foreignBalance: 0,
    currencyCode: null, description: null, createdAt: new Date(),
    updatedAt: new Date(), version: 1, deletedAt: null,
  });

  it("rejects self-parent", () => {
    expect(() => validateHierarchyCycle("a", "a", [])).toThrow("own parent");
  });

  it("rejects cycle", () => {
    const accounts = [makeAccount("a", null), makeAccount("b", "a"), makeAccount("c", "b")];
    expect(() => validateHierarchyCycle("a", "c", accounts)).toThrow("Circular hierarchy");
  });

  it("accepts valid parent", () => {
    const accounts = [makeAccount("a", null), makeAccount("b", "a")];
    expect(() => validateHierarchyCycle("b", "a", accounts)).not.toThrow();
  });
});
