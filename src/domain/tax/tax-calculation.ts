import { DomainError } from "../../shared/domain-error.js";
import { TaxCode, TaxRateApplication, TaxRateType, RoundingMethod } from "./tax-code.js";
import { TaxExemption, IncentiveType } from "./tax-incentive.js";

export enum TaxTiming {
  AtInvoice = "at_invoice",
  AtPayment = "at_payment",
  AtDelivery = "at_delivery",
  AtCustoms = "at_customs",
}

export enum TransactionSide {
  Purchase = "purchase",
  Sales = "sales",
  Import = "import",
  Export = "export",
  Adjustment = "adjustment",
  CreditNote = "credit_note",
  DebitNote = "debit_note",
}

export interface TaxCalculationRequest {
  transactionId: string;
  transactionDate: Date;
  side: TransactionSide;
  lines: TaxCalculationLine[];
  currencyCode: string;
  exchangeRate: number;
  customerId?: string;
  supplierId?: string;
  productId?: string;
  regionId?: string;
  branchId?: string;
  isExport?: boolean;
  isImport?: boolean;
  freeTradeZone?: boolean;
}

export interface TaxCalculationLine {
  lineId: string;
  itemCode: string;
  description: string;
  quantity: number;
  unitPrice: number;
  netAmount: number;
  discountAmount: number;
  discountPercent: number;
  taxCodeId: string;
  taxCode: string;
  isExempt: boolean;
  isZeroRated: boolean;
  isService: boolean;
  productCategory: string;
  originCountry: string;
  hsCode: string;
  metadata: Record<string, unknown>;
}

export interface TaxCalculationResult {
  transactionId: string;
  lines: TaxCalculationLineResult[];
  totalTaxableAmount: number;
  totalTaxAmount: number;
  totalExemptAmount: number;
  totalDeductibleAmount: number;
  totalRecoverableAmount: number;
  netPayableAmount: number;
  calculatedAt: Date;
}

export interface TaxCalculationLineResult {
  lineId: string;
  taxCode: string;
  taxableAmount: number;
  taxRate: number;
  taxAmount: number;
  taxInclusiveAmount: number;
  exemptAmount: number;
  deductibleAmount: number;
  recoverableAmount: number;
  isExempt: boolean;
  isZeroRated: boolean;
  exemptionApplied: string | null;
  roundingAdjustment: number;
}

export interface TaxRuleMatch {
  taxCodeId: string;
  priority: number;
  rule: string;
}

export interface TaxDeterminationContext {
  transactionDate: Date;
  side: TransactionSide;
  productCategory: string;
  hsCode: string;
  originCountry: string;
  customerId?: string;
  supplierId?: string;
  regionId?: string;
  isExport: boolean;
  isImport: boolean;
  freeTradeZone: boolean;
  branchId?: string;
  metadata: Record<string, unknown>;
}

export interface TaxDeterminationRule {
  id: string;
  name: string;
  taxCodeId: string;
  priority: number;
  conditions: TaxCondition[];
  effectiveFrom: Date;
  effectiveTo: Date | null;
}

export interface TaxCondition {
  field: string;
  operator: "eq" | "neq" | "in" | "nin" | "gt" | "gte" | "lt" | "lte" | "between" | "contains" | "startsWith";
  value: unknown;
}

export class TaxCalculationEngine {
  constructor(
    private readonly getTaxCode: (id: string) => Promise<TaxCode | null>,
    private readonly getExemptions: (taxCodeId: string, taxpayerId: string, date: Date) => Promise<TaxExemption[]>,
  ) {}

  async calculate(req: TaxCalculationRequest): Promise<TaxCalculationResult> {
    const lineResults: TaxCalculationLineResult[] = [];
    let totalTaxable = 0, totalTax = 0, totalExempt = 0, totalDeductible = 0, totalRecoverable = 0;

    for (const line of req.lines) {
      const result = await this.calculateLine(line, req);
      lineResults.push(result);
      totalTaxable += result.taxableAmount;
      totalTax += result.taxAmount;
      totalExempt += result.exemptAmount;
      totalDeductible += result.deductibleAmount;
      totalRecoverable += result.recoverableAmount;
    }

    return {
      transactionId: req.transactionId,
      lines: lineResults,
      totalTaxableAmount: totalTaxable,
      totalTaxAmount: totalTax,
      totalExemptAmount: totalExempt,
      totalDeductibleAmount: totalDeductible,
      totalRecoverableAmount: totalRecoverable,
      netPayableAmount: totalTax - totalDeductible,
      calculatedAt: new Date(),
    };
  }

  private async calculateLine(line: TaxCalculationLine, req: TaxCalculationRequest): Promise<TaxCalculationLineResult> {
    const taxCode = await this.getTaxCode(line.taxCodeId);
    if (!taxCode) throw new DomainError("NotFound", `Tax code ${line.taxCode} not found`);

    const netAmount = line.netAmount - line.discountAmount;
    let taxableAmount = netAmount;
    let exemptAmount = 0;

    if (line.isExempt) {
      return {
        lineId: line.lineId, taxCode: taxCode.code, taxableAmount: 0, taxRate: 0,
        taxAmount: 0, taxInclusiveAmount: netAmount, exemptAmount: netAmount,
        deductibleAmount: 0, recoverableAmount: 0, isExempt: true, isZeroRated: false,
        exemptionApplied: null, roundingAdjustment: 0,
      };
    }

    if (line.isZeroRated) {
      return {
        lineId: line.lineId, taxCode: taxCode.code, taxableAmount: netAmount, taxRate: 0,
        taxAmount: 0, taxInclusiveAmount: netAmount, exemptAmount: 0,
        deductibleAmount: 0, recoverableAmount: 0, isExempt: false, isZeroRated: true,
        exemptionApplied: null, roundingAdjustment: 0,
      };
    }

    const calc = taxCode.calculate(netAmount, req.transactionDate, line.quantity);
    let taxAmount = calc.taxAmount;

    const rate = calc.rate;
    const roundingAdj = taxAmount - Math.round(taxAmount * 100) / 100;

    let deductibleAmount = taxCode.isRecoverable ? taxAmount : 0;
    let recoverableAmount = (taxCode as any).isRefundable ? taxAmount : 0;

    return {
      lineId: line.lineId,
      taxCode: taxCode.code,
      taxableAmount: netAmount,
      taxRate: rate.rate,
      taxAmount: Math.round(taxAmount * 100) / 100,
      taxInclusiveAmount: netAmount + (taxCode.application === TaxRateApplication.Inclusive ? 0 : taxAmount),
      exemptAmount: 0,
      deductibleAmount: Math.round(deductibleAmount * 100) / 100,
      recoverableAmount: Math.round(recoverableAmount * 100) / 100,
      isExempt: false,
      isZeroRated: false,
      exemptionApplied: null,
      roundingAdjustment: Math.round(roundingAdj * 100) / 100,
    };
  }
}

export class TaxDeterminationEngine {
  private rules: TaxDeterminationRule[] = [];

  addRule(rule: TaxDeterminationRule): void {
    this.rules.push(rule);
  }

  determine(ctx: TaxDeterminationContext): TaxRuleMatch[] {
    const sorted = [...this.rules].sort((a, b) => a.priority - b.priority);
    const matches: TaxRuleMatch[] = [];

    for (const rule of sorted) {
      if (this.evaluateConditions(rule.conditions, ctx)) {
        if (rule.effectiveFrom <= ctx.transactionDate && (!rule.effectiveTo || rule.effectiveTo >= ctx.transactionDate)) {
          matches.push({ taxCodeId: rule.taxCodeId, priority: rule.priority, rule: rule.name });
        }
      }
    }

    return matches;
  }

  private evaluateConditions(conditions: TaxCondition[], ctx: TaxDeterminationContext): boolean {
    return conditions.every(c => {
      const ctxValue = (ctx as unknown as Record<string, unknown>)[c.field];
      switch (c.operator) {
        case "eq": return ctxValue === c.value;
        case "neq": return ctxValue !== c.value;
        case "in": return Array.isArray(c.value) && c.value.includes(ctxValue);
        case "nin": return Array.isArray(c.value) && !c.value.includes(ctxValue);
        case "gt": return typeof ctxValue === "number" && typeof c.value === "number" && ctxValue > c.value;
        case "gte": return typeof ctxValue === "number" && typeof c.value === "number" && ctxValue >= c.value;
        case "lt": return typeof ctxValue === "number" && typeof c.value === "number" && ctxValue < c.value;
        case "lte": return typeof ctxValue === "number" && typeof c.value === "number" && ctxValue <= c.value;
        case "contains": return typeof ctxValue === "string" && ctxValue.includes(String(c.value));
        default: return false;
      }
    });
  }
}
