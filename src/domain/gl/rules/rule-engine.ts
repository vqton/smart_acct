import {
  RuleDefinition, RuleEvaluationContext, RuleEvaluationResult,
  RuleEffect, RuleCategory, RuleSeverity,
} from "./posting-rule.js";

export interface RuleRepository {
  findByCategory(category: RuleCategory): Promise<RuleDefinition[]>;
  findByJournalType(journalType: string): Promise<RuleDefinition[]>;
  findByCategoriesAndJournal(categories: RuleCategory[], journalType: string): Promise<RuleDefinition[]>;
  findAll(): Promise<RuleDefinition[]>;
  save(rule: RuleDefinition): Promise<void>;
}

export class RuleEngine {
  private evaluators = new Map<string, (ctx: RuleEvaluationContext, rule: RuleDefinition) => RuleEvaluationResult | Promise<RuleEvaluationResult>>();

  constructor(private ruleRepo: RuleRepository) {}

  registerEvaluator(ruleCode: string, fn: (ctx: RuleEvaluationContext, rule: RuleDefinition) => RuleEvaluationResult | Promise<RuleEvaluationResult>): void {
    this.evaluators.set(ruleCode, fn);
  }

  async evaluate(ctx: RuleEvaluationContext, categories?: RuleCategory[]): Promise<{
    results: RuleEvaluationResult[];
    passed: boolean;
    errors: string[];
    warnings: string[];
  }> {
    const rules = categories
      ? await this.ruleRepo.findByCategoriesAndJournal(categories, ctx.journalType)
      : await this.ruleRepo.findByJournalType(ctx.journalType);

    const active = rules.filter(r => r.enabled).sort((a, b) => a.order - b.order);
    const results: RuleEvaluationResult[] = [];
    const errors: string[] = [];
    const warnings: string[] = [];

    for (const rule of active) {
      const evaluator = this.evaluators.get(rule.code);
      if (!evaluator) {
        results.push({
          ruleId: rule.id, ruleCode: rule.code,
          passed: false, severity: rule.severity,
          effect: RuleEffect.Skip,
          message: `No evaluator registered for rule: ${rule.code}`,
          errorCode: rule.errorCode,
        });
        continue;
      }

      const result = await evaluator(ctx, rule);
      results.push(result);

      if (!result.passed) {
        if (result.effect === RuleEffect.Block || rule.severity === RuleSeverity.Error) {
          errors.push(result.message);
        } else if (result.effect === RuleEffect.Warn || rule.severity === RuleSeverity.Warning) {
          warnings.push(result.message);
        }
      }
    }

    return { results, passed: errors.length === 0, errors, warnings };
  }

  getDefaultRules(): RuleDefinition[] {
    return [
      ...PreValidationRules,
      ...AccountingValidationRules,
      ...FiscalValidationRules,
      ...CurrencyRules,
      ...DimensionRules,
      ...BudgetRules,
      ...SecurityRules,
    ];
  }
}

export const PreValidationRules: RuleDefinition[] = [
  { id: "rule-auth-001", code: "AUTH_ACTIVE_SESSION", name: "Active Session", description: "User must have active session", category: RuleCategory.PreValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 100, applicableJournalTypes: ["*"], errorCode: "AUTH_001", config: {} },
  { id: "rule-auth-002", code: "AUTH_POSTING_PERMISSION", name: "Posting Permission", description: "User must have posting permission", category: RuleCategory.PreValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 110, applicableJournalTypes: ["*"], errorCode: "AUTH_002", config: {} },
  { id: "rule-access-001", code: "ACCESS_VOUCHER_TYPE", name: "Voucher Type Access", description: "User must have access to voucher type", category: RuleCategory.PreValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 120, applicableJournalTypes: ["*"], errorCode: "ACCESS_001", config: {} },
];

export const AccountingValidationRules: RuleDefinition[] = [
  { id: "rule-acc-001", code: "DEBIT_CREDIT_EQUAL", name: "Debit = Credit", description: "Total debit must equal total credit within tolerance", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 200, applicableJournalTypes: ["*"], errorCode: "ACC_001", config: { tolerance: 1 } },
  { id: "rule-acc-002", code: "POSTING_ACCOUNT_ONLY", name: "Posting Account Only", description: "Only posting accounts (not control accounts) allowed", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 210, applicableJournalTypes: ["*"], errorCode: "ACC_002", config: {} },
  { id: "rule-acc-003", code: "ACCOUNT_ACTIVE", name: "Account Active", description: "Account must be active", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 220, applicableJournalTypes: ["*"], errorCode: "ACC_003", config: {} },
  { id: "rule-acc-004", code: "NON_NEGATIVE_AMOUNTS", name: "Non-Negative Amounts", description: "Debit and credit amounts must be non-negative", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 230, applicableJournalTypes: ["*"], errorCode: "ACC_004", config: {} },
  { id: "rule-acc-005", code: "MIN_LINES", name: "Minimum Lines", description: "Journal must have at least 2 lines", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 240, applicableJournalTypes: ["standard", "reversing", "adjustment"], errorCode: "ACC_005", config: { minLines: 2 } },
  { id: "rule-acc-006", code: "NORMAL_BALANCE", name: "Normal Balance Check", description: "Debit-nature accounts should normally have debit balance, credit-nature accounts should normally have credit balance", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Warning, effect: RuleEffect.Warn, enabled: true, order: 250, applicableJournalTypes: ["*"], errorCode: "ACC_006", config: {} },
  { id: "rule-acc-007", code: "CONTROL_ACCOUNT_RESTRICTION", name: "Control Account Restriction", description: "Cannot post directly to control accounts", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 260, applicableJournalTypes: ["*"], errorCode: "ACC_007", config: {} },
  { id: "rule-acc-008", code: "ALLOW_MANUAL_ENTRY", name: "Allow Manual Entry", description: "Account must allow manual entry", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 270, applicableJournalTypes: ["standard", "adjustment"], errorCode: "ACC_008", config: {} },
  { id: "rule-acc-009", code: "LINE_DESCRIPTION", name: "Line Description Required", description: "Each line must have a description", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 280, applicableJournalTypes: ["*"], errorCode: "ACC_009", config: {} },
  { id: "rule-acc-010", code: "SAME_CURRENCY_LINES", name: "Same Currency Per Batch", description: "All lines must use the same currency except for exchange difference lines", category: RuleCategory.AccountingValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 290, applicableJournalTypes: ["*"], errorCode: "ACC_010", config: {} },
];

export const FiscalValidationRules: RuleDefinition[] = [
  { id: "rule-fis-001", code: "PERIOD_OPEN", name: "Period Open", description: "Posting period must be open", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 300, applicableJournalTypes: ["*"], errorCode: "FIS_001", config: {} },
  { id: "rule-fis-002", code: "FISCAL_YEAR_OPEN", name: "Fiscal Year Open", description: "Fiscal year must not be closed", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 310, applicableJournalTypes: ["*"], errorCode: "FIS_002", config: {} },
  { id: "rule-fis-003", code: "POSTING_DATE_IN_PERIOD", name: "Posting Date in Period", description: "Posting date must fall within the period's date range", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 320, applicableJournalTypes: ["*"], errorCode: "FIS_003", config: {} },
  { id: "rule-fis-004", code: "NO_FUTURE_POSTING", name: "No Future Posting", description: "Posting date cannot be in the future", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 330, applicableJournalTypes: ["*"], errorCode: "FIS_004", config: { maxFutureDays: 0 } },
  { id: "rule-fis-005", code: "VOUCHER_DATE_RANGE", name: "Voucher Date Range", description: "Voucher date must be within valid range", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 340, applicableJournalTypes: ["*"], errorCode: "FIS_005", config: { maxPastDays: 90 } },
  { id: "rule-fis-006", code: "SEQUENTIAL_VOUCHER", name: "Sequential Voucher Number", description: "Voucher numbers within series must be sequential without gaps", category: RuleCategory.FiscalValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 350, applicableJournalTypes: ["*"], errorCode: "FIS_006", config: {} },
];

export const CurrencyRules: RuleDefinition[] = [
  { id: "rule-cur-001", code: "VALID_EXCHANGE_RATE", name: "Valid Exchange Rate", description: "Exchange rate must be valid and active on posting date", category: RuleCategory.CurrencyValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 400, applicableJournalTypes: ["*"], errorCode: "CUR_001", config: {} },
  { id: "rule-cur-002", code: "FC_TOTAL_MATCH", name: "Foreign Currency Total Match", description: "Foreign currency debit must equal foreign currency credit", category: RuleCategory.CurrencyValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 410, applicableJournalTypes: ["*"], errorCode: "CUR_002", config: { tolerance: 1 } },
  { id: "rule-cur-003", code: "CURRENCY_CONSISTENCY", name: "Currency Consistency", description: "Line currency must match batch currency or be VND", category: RuleCategory.CurrencyValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 420, applicableJournalTypes: ["*"], errorCode: "CUR_003", config: {} },
];

export const DimensionRules: RuleDefinition[] = [
  { id: "rule-dim-001", code: "COST_CENTER_ACTIVE", name: "Cost Center Active", description: "Referenced cost center must be active", category: RuleCategory.DimensionValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 500, applicableJournalTypes: ["*"], errorCode: "DIM_001", config: {} },
  { id: "rule-dim-002", code: "DEPARTMENT_ACTIVE", name: "Department Active", description: "Referenced department must be active", category: RuleCategory.DimensionValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 510, applicableJournalTypes: ["*"], errorCode: "DIM_002", config: {} },
  { id: "rule-dim-003", code: "MANDATORY_COST_CENTER", name: "Mandatory Cost Center", description: "Cost center is mandatory for expense accounts", category: RuleCategory.DimensionValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: false, order: 520, applicableJournalTypes: ["*"], errorCode: "DIM_003", config: { accountCategories: ["operating_expense", "cost_of_goods_sold", "other_expense", "manufacturing_cost"] } },
  { id: "rule-dim-004", code: "COST_CENTER_IN_PERIOD", name: "Cost Center Active in Period", description: "Cost center must be active during the posting period", category: RuleCategory.DimensionValidation, severity: RuleSeverity.Warning, effect: RuleEffect.Warn, enabled: true, order: 530, applicableJournalTypes: ["*"], errorCode: "DIM_004", config: {} },
];

export const BudgetRules: RuleDefinition[] = [
  { id: "rule-bud-001", code: "BUDGET_AVAILABLE", name: "Budget Available", description: "Budget must have sufficient remaining amount", category: RuleCategory.BudgetValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: false, order: 600, applicableJournalTypes: ["*"], errorCode: "BUD_001", config: {} },
  { id: "rule-bud-002", code: "BUDGET_APPROVED", name: "Budget Approved", description: "Budget must be in approved status", category: RuleCategory.BudgetValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: false, order: 610, applicableJournalTypes: ["*"], errorCode: "BUD_002", config: {} },
  { id: "rule-bud-003", code: "BUDGET_WARNING", name: "Budget Warning", description: "Budget remaining below threshold", category: RuleCategory.BudgetValidation, severity: RuleSeverity.Warning, effect: RuleEffect.Warn, enabled: true, order: 620, applicableJournalTypes: ["*"], errorCode: "BUD_003", config: { thresholdPercent: 10 } },
];

export const SecurityRules: RuleDefinition[] = [
  { id: "rule-sec-001", code: "DUPLICATE_DETECTION", name: "Duplicate Detection", description: "Prevent duplicate posting via idempotency key", category: RuleCategory.SecurityValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 700, applicableJournalTypes: ["*"], errorCode: "SEC_001", config: {} },
  { id: "rule-sec-002", code: "SEGREGATION_OF_DUTIES", name: "Segregation of Duties", description: "Creator and approver must be different users", category: RuleCategory.SecurityValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 710, applicableJournalTypes: ["*"], errorCode: "SEC_002", config: {} },
  { id: "rule-sec-003", code: "APPROVAL_REQUIRED", name: "Approval Required", description: "Journal type requires approval before posting", category: RuleCategory.SecurityValidation, severity: RuleSeverity.Error, effect: RuleEffect.Block, enabled: true, order: 720, applicableJournalTypes: ["standard", "adjustment", "allocation"], errorCode: "SEC_003", config: {} },
];
