import { describe, it, expect, beforeEach } from "vitest";
import { RuleEngine, PreValidationRules, AccountingValidationRules } from "../rules/rule-engine.js";
import { RuleEvaluationContext, RuleDefinition, RuleSeverity, RuleEffect, RuleCategory } from "../rules/posting-rule.js";

class FakeRuleRepo {
  rules: RuleDefinition[] = [...PreValidationRules, ...AccountingValidationRules];

  async findByJournalType() { return this.rules; }
  async findByCategoriesAndJournal() { return this.rules; }
  async findAll() { return this.rules; }
  async save(r: RuleDefinition) { this.rules.push(r); }
  async findByCategory() { return this.rules; }
}

function makeCtx(overrides?: Partial<RuleEvaluationContext>): RuleEvaluationContext {
  return {
    batchId: "b-1", batchNumber: "J-001", journalType: "standard",
    periodId: "p-1", fiscalYearId: "fy-1", postingDate: new Date(),
    voucherDate: new Date(), currencyCode: "VND", exchangeRate: 1,
    isForeignCurrency: false, totalDebit: 1000, totalCredit: 1000,
    lines: [{ accountId: "a-1", accountCode: "1111", debitAmount: 1000, creditAmount: 0, currencyCode: "VND", exchangeRate: 1, costCenterId: null, departmentId: null, projectId: null, description: "test" }],
    accountMap: new Map([["a-1", { code: "1111", category: "short_term_asset", nature: "debit", isActive: true, isPosting: true, isControl: false, allowManualEntry: true, balance: 0, version: 1 }]]),
    periodStatus: "open", fiscalYearClosed: false, userId: "u-1", userRoles: ["poster"], idempotencyKey: null,
    ...overrides,
  };
}

describe("RuleEngine", () => {
  let engine: RuleEngine;
  let repo: FakeRuleRepo;

  beforeEach(() => {
    repo = new FakeRuleRepo();
    engine = new RuleEngine(repo as any);
  });

  it("returns passed=true for valid context", async () => {
    engine.registerEvaluator("DEBIT_CREDIT_EQUAL", (ctx) => ({
      ruleId: "r1", ruleCode: "DEBIT_CREDIT_EQUAL", passed: true,
      severity: RuleSeverity.Error, effect: RuleEffect.Block,
      message: "", errorCode: "ACC_001",
    }));
    engine.registerEvaluator("ACCOUNT_ACTIVE", (ctx) => ({
      ruleId: "r2", ruleCode: "ACCOUNT_ACTIVE", passed: true,
      severity: RuleSeverity.Error, effect: RuleEffect.Block,
      message: "", errorCode: "ACC_003",
    }));
    engine.registerEvaluator("POSTING_ACCOUNT_ONLY", (ctx) => ({
      ruleId: "r3", ruleCode: "POSTING_ACCOUNT_ONLY", passed: true,
      severity: RuleSeverity.Error, effect: RuleEffect.Block,
      message: "", errorCode: "ACC_002",
    }));
    engine.registerEvaluator("NON_NEGATIVE_AMOUNTS", (ctx) => ({
      ruleId: "r4", ruleCode: "NON_NEGATIVE_AMOUNTS", passed: true,
      severity: RuleSeverity.Error, effect: RuleEffect.Block,
      message: "", errorCode: "ACC_004",
    }));

    const result = await engine.evaluate(makeCtx());
    expect(result.passed).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("returns failed on blocking rule violation", async () => {
    engine.registerEvaluator("DEBIT_CREDIT_EQUAL", () => ({
      ruleId: "r1", ruleCode: "DEBIT_CREDIT_EQUAL", passed: false,
      severity: RuleSeverity.Error, effect: RuleEffect.Block,
      message: "ACC_001: Debit != Credit", errorCode: "ACC_001",
    }));

    const result = await engine.evaluate(makeCtx());
    expect(result.passed).toBe(false);
    expect(result.errors).toContain("ACC_001: Debit != Credit");
  });

  it("returns warning for non-blocking violations", async () => {
    engine.registerEvaluator("NORMAL_BALANCE", () => ({
      ruleId: "r1", ruleCode: "NORMAL_BALANCE", passed: false,
      severity: RuleSeverity.Warning, effect: RuleEffect.Warn,
      message: "ACC_006: Normal balance warning", errorCode: "ACC_006",
    }));

    const result = await engine.evaluate(makeCtx());
    expect(result.passed).toBe(true);
    expect(result.warnings).toContain("ACC_006: Normal balance warning");
  });

  it("skips rules with no evaluator registered", async () => {
    const result = await engine.evaluate(makeCtx());
    expect(result.passed).toBe(true);
  });

  it("respects rule ordering", async () => {
    const order: number[] = [];
    engine.registerEvaluator("DEBIT_CREDIT_EQUAL", async (ctx, rule) => {
      order.push(rule.order);
      return { ruleId: "", ruleCode: "", passed: true, severity: RuleSeverity.Error, effect: RuleEffect.Block, message: "", errorCode: "" };
    });
    engine.registerEvaluator("ACCOUNT_ACTIVE", async (ctx, rule) => {
      order.push(rule.order);
      return { ruleId: "", ruleCode: "", passed: true, severity: RuleSeverity.Error, effect: RuleEffect.Block, message: "", errorCode: "" };
    });

    await engine.evaluate(makeCtx());
    expect(order).toEqual([200, 220]);
  });

  it("returns default rules for standard journal type", () => {
    const rules = engine.getDefaultRules();
    expect(rules.length).toBeGreaterThan(20);
    expect(rules.filter(r => r.applicableJournalTypes.includes("*")).length).toBe(29);
  });
});
