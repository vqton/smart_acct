import { DomainError } from "../../../shared/domain-error.js";

export enum RuleCategory {
  PreValidation = "pre_validation",
  AccountingValidation = "accounting_validation",
  FiscalValidation = "fiscal_validation",
  CurrencyValidation = "currency_validation",
  DimensionValidation = "dimension_validation",
  BudgetValidation = "budget_validation",
  SecurityValidation = "security_validation",
  BusinessLogic = "business_logic",
  PostProcessing = "post_processing",
}

export enum RuleSeverity {
  Error = "error",
  Warning = "warning",
  Info = "info",
}

export enum RuleEffect {
  Block = "block",
  Warn = "warn",
  Skip = "skip",
  Audit = "audit",
}

export interface RuleDefinition {
  id: string;
  code: string;
  name: string;
  description: string;
  category: RuleCategory;
  severity: RuleSeverity;
  effect: RuleEffect;
  enabled: boolean;
  order: number;
  applicableJournalTypes: string[];
  errorCode: string;
  config?: Record<string, unknown>;
}

export interface RuleEvaluationContext {
  batchId: string;
  batchNumber: string;
  journalType: string;
  periodId: string;
  fiscalYearId: string;
  postingDate: Date;
  voucherDate: Date;
  currencyCode: string;
  exchangeRate: number;
  isForeignCurrency: boolean;
  totalDebit: number;
  totalCredit: number;
  lines: Array<{
    accountId: string;
    accountCode: string;
    debitAmount: number;
    creditAmount: number;
    currencyCode: string;
    exchangeRate: number;
    costCenterId: string | null;
    departmentId: string | null;
    projectId: string | null;
    description: string | null;
  }>;
  accountMap: Map<string, { code: string; category: string; nature: string; isActive: boolean; isPosting: boolean; isControl: boolean; allowManualEntry: boolean; balance: number; version: number; }>;
  periodStatus: string;
  fiscalYearClosed: boolean;
  userId: string;
  userRoles: string[];
  idempotencyKey: string | null;
}

export interface RuleEvaluationResult {
  ruleId: string;
  ruleCode: string;
  passed: boolean;
  severity: RuleSeverity;
  effect: RuleEffect;
  message: string;
  errorCode: string;
}

export type RuleEvaluator = (ctx: RuleEvaluationContext, rule: RuleDefinition) => RuleEvaluationResult | Promise<RuleEvaluationResult>;

export class RuleExecutionError extends DomainError {
  constructor(ruleCode: string, message: string) {
    super("BusinessRule", `[${ruleCode}] ${message}`);
    this.name = "RuleExecutionError";
  }
}
