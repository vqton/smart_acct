import { RuleEvaluationContext, RuleEvaluationResult } from "../rules/posting-rule.js";

export interface AccountSnapshot {
  id: string;
  code: string;
  category: string;
  nature: string;
  isActive: boolean;
  isPosting: boolean;
  isControl: boolean;
  allowManualEntry: boolean;
  balance: number;
  foreignBalance: number;
  version: number;
}

export interface PostingContext {
  batchId: string;
  batchNumber: string;
  journalType: string;
  periodId: string;
  periodName: string;
  fiscalYearId: string;
  fiscalYearCode: string;
  postingDate: Date;
  voucherDate: Date;
  currencyCode: string;
  exchangeRate: number;
  isForeignCurrency: boolean;
  totalDebit: number;
  totalCredit: number;
  foreignTotalDebit: number;
  foreignTotalCredit: number;
  description: string;
  reference: string | null;
  userId: string;
  userRoles: string[];
  createdById: string;
  approvedById: string | null;
  idempotencyKey: string | null;
  lines: Array<{
    id: string;
    accountId: string;
    accountCode: string;
    debitAmount: number;
    creditAmount: number;
    foreignDebitAmount: number;
    foreignCreditAmount: number;
    currencyCode: string;
    exchangeRate: number;
    description: string | null;
    costCenterId: string | null;
    departmentId: string | null;
    projectId: string | null;
    lineOrder: number;
  }>;
  accountSnapshots: Map<string, AccountSnapshot>;
  periodStatus: string;
  fiscalYearClosed: boolean;
  voucherNumber: string | null;
  voucherSeriesId: string | null;
  voucherTypeId: string | null;
  ruleResults: RuleEvaluationResult[];
  originalBalanceBefore: Map<string, number>;
  balanceChanges: Map<string, { debitTotal: number; creditTotal: number; delta: number }>;
  startedAt: Date;
  state: "initialized" | "validating" | "posting" | "committed" | "rolled_back" | "failed";
  error?: Error;
}

export function createPostingContext(params: {
  batchId: string;
  batchNumber: string;
  journalType: string;
  periodId: string;
  periodName: string;
  fiscalYearId: string;
  fiscalYearCode: string;
  postingDate: Date;
  voucherDate: Date;
  currencyCode: string;
  exchangeRate: number;
  isForeignCurrency: boolean;
  totalDebit: number;
  totalCredit: number;
  foreignTotalDebit: number;
  foreignTotalCredit: number;
  description: string;
  reference: string | null;
  userId: string;
  userRoles?: string[];
  createdById: string;
  approvedById: string | null;
  idempotencyKey?: string | null;
  lines: PostingContext["lines"];
  accountSnapshots?: Map<string, AccountSnapshot>;
  periodStatus?: string;
  fiscalYearClosed?: boolean;
  voucherNumber?: string | null;
  voucherSeriesId?: string | null;
  voucherTypeId?: string | null;
}): PostingContext {
  return {
    batchId: params.batchId,
    batchNumber: params.batchNumber,
    journalType: params.journalType,
    periodId: params.periodId,
    periodName: params.periodName,
    fiscalYearId: params.fiscalYearId,
    fiscalYearCode: params.fiscalYearCode,
    postingDate: params.postingDate,
    voucherDate: params.voucherDate,
    currencyCode: params.currencyCode,
    exchangeRate: params.exchangeRate,
    isForeignCurrency: params.isForeignCurrency,
    totalDebit: params.totalDebit,
    totalCredit: params.totalCredit,
    foreignTotalDebit: params.foreignTotalDebit,
    foreignTotalCredit: params.foreignTotalCredit,
    description: params.description,
    reference: params.reference,
    userId: params.userId,
    userRoles: params.userRoles ?? [],
    createdById: params.createdById,
    approvedById: params.approvedById,
    idempotencyKey: params.idempotencyKey ?? null,
    lines: params.lines,
    accountSnapshots: params.accountSnapshots ?? new Map(),
    periodStatus: params.periodStatus ?? "open",
    fiscalYearClosed: params.fiscalYearClosed ?? false,
    voucherNumber: params.voucherNumber ?? null,
    voucherSeriesId: params.voucherSeriesId ?? null,
    voucherTypeId: params.voucherTypeId ?? null,
    ruleResults: [],
    originalBalanceBefore: new Map(),
    balanceChanges: new Map(),
    startedAt: new Date(),
    state: "initialized",
  };
}

export function toRuleContext(ctx: PostingContext): RuleEvaluationContext {
  return {
    batchId: ctx.batchId,
    batchNumber: ctx.batchNumber,
    journalType: ctx.journalType,
    periodId: ctx.periodId,
    fiscalYearId: ctx.fiscalYearId,
    postingDate: ctx.postingDate,
    voucherDate: ctx.voucherDate,
    currencyCode: ctx.currencyCode,
    exchangeRate: ctx.exchangeRate,
    isForeignCurrency: ctx.isForeignCurrency,
    totalDebit: ctx.totalDebit,
    totalCredit: ctx.totalCredit,
    lines: ctx.lines.map(l => ({
      accountId: l.accountId,
      accountCode: l.accountCode,
      debitAmount: l.debitAmount,
      creditAmount: l.creditAmount,
      currencyCode: l.currencyCode,
      exchangeRate: l.exchangeRate,
      costCenterId: l.costCenterId,
      departmentId: l.departmentId,
      projectId: l.projectId,
      description: l.description,
    })),
    accountMap: new Map(Array.from(ctx.accountSnapshots.entries()).map(([k, v]) => [k, { ...v }])),
    periodStatus: ctx.periodStatus,
    fiscalYearClosed: ctx.fiscalYearClosed,
    userId: ctx.userId,
    userRoles: ctx.userRoles,
    idempotencyKey: ctx.idempotencyKey,
  };
}
