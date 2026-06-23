import { describe, it, expect } from "vitest";
import { CoaService } from "../coa-service.js";
import { AccountExtension } from "../../../domain/coa/account-extension.js";
import { AccountCategory, AccountNature } from "../../../domain/gl/account-category.js";

describe("CoaService", () => {
  it("validates account code via service helper", () => {
    const service = new CoaService(null as any, null as any, null as any, null as any);
    expect(() => service.validateAccountCode("1111")).not.toThrow();
    expect(() => service.validateAccountCode("12345678")).toThrow();
  });

  it("builds tree from flat accounts", () => {
    const service = new CoaService(null as any, null as any, null as any, null as any);

    const accounts = [
      { id: "a", code: "1", name: "Root", category: AccountCategory.ShortTermAsset,
        nature: AccountNature.Debit, parentId: null, isActive: true, isControl: true,
        isPosting: false, allowManualEntry: true, balance: 0, foreignBalance: 0,
        currencyCode: null, description: null, nameEn: null, createdAt: new Date(),
        updatedAt: new Date(), version: 1, deletedAt: null },
      { id: "b", code: "11", name: "Child", category: AccountCategory.ShortTermAsset,
        nature: AccountNature.Debit, parentId: "a", isActive: true, isControl: false,
        isPosting: true, allowManualEntry: true, balance: 0, foreignBalance: 0,
        currencyCode: null, description: null, nameEn: null, createdAt: new Date(),
        updatedAt: new Date(), version: 1, deletedAt: null },
    ];

    const exts = new Map<string, AccountExtension>();
    const types = new Map<string, { code: string; name: string }>();
    const tree = service.buildTree(accounts, exts, types);

    expect(tree.length).toBe(1);
    expect(tree[0].code).toBe("1");
    expect(tree[0].children.length).toBe(1);
    expect(tree[0].children[0].code).toBe("11");
  });
});
