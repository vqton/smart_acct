import { describe, it, expect } from "vitest";
import { Account } from "../account.js";
import { AccountCategory, AccountNature } from "../account-category.js";
import { Money } from "../../shared/money.js";

describe("Account", () => {
  it("creates account with valid params", () => {
    const a = Account.create({
      code: "1111",
      name: "Tiền mặt VND",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
    });
    expect(a.code).toBe("1111");
    expect(a.name).toBe("Tiền mặt VND");
    expect(a.isActive).toBe(true);
    expect(a.isPosting).toBe(true);
    expect(a.balance.toNumber()).toBe(0);
    expect(a.version).toBe(1);
  });

  it("rejects invalid code format", () => {
    expect(() => Account.create({
      code: "TOO_LONG",
      name: "test",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
    })).toThrow("Invalid account code");
  });

  it("marks control accounts as non-posting", () => {
    const a = Account.create({
      code: "111",
      name: "Tiền mặt",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
      isControl: true,
    });
    expect(a.isControl).toBe(true);
    expect(a.isPosting).toBe(false);
  });

  it("updates balance correctly for debit-nature account", () => {
    const a = Account.create({
      code: "1111",
      name: "Cash",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
    });
    a.updateBalance(Money.fromVnd(1000), Money.zero());
    expect(a.balance.toNumber()).toBe(1000);
    a.updateBalance(Money.zero(), Money.fromVnd(500));
    expect(a.balance.toNumber()).toBe(500);
  });

  it("updates balance correctly for credit-nature account", () => {
    const a = Account.create({
      code: "3311",
      name: "AP",
      category: AccountCategory.ShortTermLiability,
      nature: AccountNature.Credit,
    });
    a.updateBalance(Money.zero(), Money.fromVnd(1000));
    expect(a.balance.toNumber()).toBe(1000);
  });

  it("prevents posting to inactive account", () => {
    const a = Account.create({
      code: "1111",
      name: "Cash",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
    });
    a.deactivate();
    expect(() => a.canPost()).toThrow("inactive");
  });

  it("prevents posting to control account", () => {
    const a = Account.create({
      code: "111",
      name: "Cash control",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
      isControl: true,
    });
    expect(() => a.canPost()).toThrow("not a posting account");
  });

  it("generates domain events on creation", () => {
    const a = Account.create({
      code: "1111",
      name: "Cash",
      category: AccountCategory.ShortTermAsset,
      nature: AccountNature.Debit,
    });
    const events = a.clearEvents();
    expect(events).toHaveLength(1);
    expect(events[0].eventName).toBe("AccountCreated");
  });
});
