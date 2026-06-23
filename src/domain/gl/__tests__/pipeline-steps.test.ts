import { describe, it, expect, beforeEach } from "vitest";
import { PostingContext, createPostingContext, AccountSnapshot } from "../posting/posting-context.js";
import {
  AuthenticationStep, AuthorizationStep, BatchValidationStep,
  DebitCreditEqualStep, AccountValidationStep, FiscalPeriodStep,
  ForeignCurrencyStep, SegregationOfDutiesStep, AccountLockStep,
  BalanceCalculationStep, LedgerPostingStep,
} from "../posting/steps/index.js";

const BASE_CTX = {
  batchId: "b-1", batchNumber: "J-001", journalType: "standard",
  periodId: "p-1", periodName: "Tháng 1", fiscalYearId: "fy-1", fiscalYearCode: "FY2026",
  postingDate: new Date("2026-01-15"), voucherDate: new Date("2026-01-15"),
  currencyCode: "VND", exchangeRate: 1, isForeignCurrency: false,
  totalDebit: 1000, totalCredit: 1000, foreignTotalDebit: 0, foreignTotalCredit: 0,
  description: "Test", reference: null,
  userId: "u-1", userRoles: ["poster"], createdById: "u-2", approvedById: "approver-1",
};

function makeCtx(overrides?: Partial<PostingContext>): PostingContext {
  return createPostingContext({
    ...BASE_CTX,
    lines: [
      { id: "l-1", accountId: "a-1", accountCode: "1111", debitAmount: 1000, creditAmount: 0, foreignDebitAmount: 0, foreignCreditAmount: 0, currencyCode: "VND", exchangeRate: 1, description: "Debit", costCenterId: null, departmentId: null, projectId: null, lineOrder: 1 },
      { id: "l-2", accountId: "a-2", accountCode: "5111", debitAmount: 0, creditAmount: 1000, foreignDebitAmount: 0, foreignCreditAmount: 0, currencyCode: "VND", exchangeRate: 1, description: "Credit", costCenterId: null, departmentId: null, projectId: null, lineOrder: 2 },
    ],
    accountSnapshots: new Map([
      ["a-1", { id: "a-1", code: "1111", category: "short_term_asset", nature: "debit", isActive: true, isPosting: true, isControl: false, allowManualEntry: true, balance: 0, foreignBalance: 0, version: 1 }],
      ["a-2", { id: "a-2", code: "5111", category: "revenue", nature: "credit", isActive: true, isPosting: true, isControl: false, allowManualEntry: true, balance: 0, foreignBalance: 0, version: 1 }],
    ]),
    ...overrides,
  });
}

describe("Pipeline Steps", () => {
  describe("AuthenticationStep", () => {
    const step = new AuthenticationStep();

    it("passes with valid userId", async () => {
      const ctx = makeCtx();
      await expect(step.execute(ctx)).resolves.toBeDefined();
    });

    it("fails with empty userId", async () => {
      const ctx = makeCtx({ userId: "" });
      await expect(step.execute(ctx)).rejects.toThrow();
    });
  });

  describe("AuthorizationStep", () => {
    const step = new AuthorizationStep();

    it("passes with poster role", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails without poster role", async () => {
      const ctx = makeCtx({ userRoles: ["viewer"] });
      await expect(step.execute(ctx)).rejects.toThrow();
    });
  });

  describe("BatchValidationStep", () => {
    const step = new BatchValidationStep();

    it("passes with valid batch", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails with empty lines", async () => {
      const ctx = makeCtx({ lines: [] });
      await expect(step.execute(ctx)).rejects.toThrow();
    });
  });

  describe("DebitCreditEqualStep", () => {
    const step = new DebitCreditEqualStep();

    it("passes when totals match", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails when totals mismatch", async () => {
      const ctx = makeCtx({ totalDebit: 1000, totalCredit: 500 });
      await expect(step.execute(ctx)).rejects.toThrow();
    });
  });

  describe("AccountValidationStep", () => {
    const step = new AccountValidationStep();

    it("passes with valid accounts", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails with inactive account", async () => {
      const snapshots = new Map(makeCtx().accountSnapshots);
      snapshots.set("a-1", { ...snapshots.get("a-1")!, isActive: false });
      const ctx = makeCtx({ accountSnapshots: snapshots });
      await expect(step.execute(ctx)).rejects.toThrow(/inactive/);
    });

    it("fails with non-posting account", async () => {
      const snapshots = new Map(makeCtx().accountSnapshots);
      snapshots.set("a-1", { ...snapshots.get("a-1")!, isPosting: false });
      const ctx = makeCtx({ accountSnapshots: snapshots });
      await expect(step.execute(ctx)).rejects.toThrow(/posting account/);
    });

    it("fails with control account", async () => {
      const snapshots = new Map(makeCtx().accountSnapshots);
      snapshots.set("a-1", { ...snapshots.get("a-1")!, isControl: true });
      const ctx = makeCtx({ accountSnapshots: snapshots });
      await expect(step.execute(ctx)).rejects.toThrow(/ACC_007/);
    });

    it("fails with negative amounts", async () => {
      const ctx = makeCtx({
        lines: [{
          ...makeCtx().lines[0], debitAmount: -100,
        }, ...makeCtx().lines.slice(1)],
      });
      await expect(step.execute(ctx)).rejects.toThrow(/non-negative/);
    });

    it("fails with line missing description", async () => {
      const ctx = makeCtx({
        lines: [{
          ...makeCtx().lines[0], description: null,
        }, ...makeCtx().lines.slice(1)],
      });
      await expect(step.execute(ctx)).rejects.toThrow(/description is required/);
    });
  });

  describe("FiscalPeriodStep", () => {
    const step = new FiscalPeriodStep();

    it("passes with open period", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails with closed period", async () => {
      const ctx = makeCtx({ periodStatus: "closed" });
      await expect(step.execute(ctx)).rejects.toThrow(/closed/);
    });

    it("fails with locked period", async () => {
      const ctx = makeCtx({ periodStatus: "locked" });
      await expect(step.execute(ctx)).rejects.toThrow(/locked/);
    });

    it("fails with closed fiscal year", async () => {
      const ctx = makeCtx({ fiscalYearClosed: true });
      await expect(step.execute(ctx)).rejects.toThrow(/FIS_003/);
    });

    it("fails with future posting date", async () => {
      const future = new Date();
      future.setFullYear(future.getFullYear() + 1);
      const ctx = makeCtx({ postingDate: future });
      await expect(step.execute(ctx)).rejects.toThrow(/future/);
    });
  });

  describe("ForeignCurrencyStep", () => {
    const step = new ForeignCurrencyStep();

    it("passes for non-foreign currency", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails when FC totals mismatch", async () => {
      const ctx = makeCtx({
        isForeignCurrency: true,
        foreignTotalDebit: 1000,
        foreignTotalCredit: 500,
      });
      await expect(step.execute(ctx)).rejects.toThrow(/CUR_002/);
    });

    it("passes when FC totals match", async () => {
      const ctx = makeCtx({
        isForeignCurrency: true,
        foreignTotalDebit: 1000,
        foreignTotalCredit: 1000,
      });
      await expect(step.execute(ctx)).resolves.toBeDefined();
    });
  });

  describe("SegregationOfDutiesStep", () => {
    const step = new SegregationOfDutiesStep();

    it("passes when creator and approver differ", async () => {
      await expect(step.execute(makeCtx())).resolves.toBeDefined();
    });

    it("fails when creator equals approver", async () => {
      const ctx = makeCtx({ createdById: "approver-1", approvedById: "approver-1" });
      await expect(step.execute(ctx)).rejects.toThrow(/Creator and approver/);
    });
  });

  describe("AccountLockStep", () => {
    const step = new AccountLockStep();

    it("captures initial balances", async () => {
      const ctx = makeCtx();
      await step.execute(ctx);
      expect(ctx.originalBalanceBefore.size).toBe(2);
      expect(ctx.originalBalanceBefore.get("a-1")).toBe(0);
      expect(ctx.balanceChanges.has("a-1")).toBe(true);
    });

    it("supports rollback", async () => {
      const ctx = makeCtx();
      await step.execute(ctx);
      await step.rollback!(ctx);
      expect(ctx.accountSnapshots.size).toBe(2);
    });
  });

  describe("BalanceCalculationStep", () => {
    const step = new BalanceCalculationStep();

    it("calculates balance changes per account", async () => {
      const ctx = makeCtx();
      await new AccountLockStep().execute(ctx);
      await step.execute(ctx);
      const changeA1 = ctx.balanceChanges.get("a-1");
      expect(changeA1?.debitTotal).toBe(1000);
      expect(changeA1?.creditTotal).toBe(0);
      const changeA2 = ctx.balanceChanges.get("a-2");
      expect(changeA2?.debitTotal).toBe(0);
      expect(changeA2?.creditTotal).toBe(1000);
    });
  });

  describe("LedgerPostingStep", () => {
    const step = new LedgerPostingStep();

    it("updates account balances", async () => {
      const ctx = makeCtx();
      await new AccountLockStep().execute(ctx);
      await new BalanceCalculationStep().execute(ctx);
      await step.execute(ctx);
      expect(ctx.accountSnapshots.get("a-1")?.balance).toBe(1000);
      expect(ctx.accountSnapshots.get("a-2")?.balance).toBe(1000);
    });
  });
});
