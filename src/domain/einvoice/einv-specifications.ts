import { DomainError } from "../../shared/domain-error.js";
import { EinvInvoiceStatus, EinvInvoiceCategory } from "./einv-enums.js";
import { EinvInvoice, EinvInvoiceState } from "./einv-invoice.js";

// ─── Specification Interface ───────────────────────────────────────────────────

export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  check(candidate: T): void;
}

// ─── Invoice Status Guard ──────────────────────────────────────────────────────

export class InvoiceStatusSpec implements Specification<EinvInvoice> {
  constructor(private readonly allowedStatuses: EinvInvoiceStatus[]) {}
  isSatisfiedBy(invoice: EinvInvoice): boolean {
    return this.allowedStatuses.includes(invoice.status);
  }
  check(invoice: EinvInvoice): void {
    if (!this.isSatisfiedBy(invoice)) {
      throw new DomainError("BusinessRule", `Invoice status ${invoice.status} not allowed. Expected: ${this.allowedStatuses.join(", ")}`);
    }
  }
}

// ─── Can Submit Spec ───────────────────────────────────────────────────────────

export class CanSubmitSpec implements Specification<EinvInvoice> {
  isSatisfiedBy(invoice: EinvInvoice): boolean {
    return invoice.status === EinvInvoiceStatus.draft && invoice.lines.length > 0;
  }
  check(invoice: EinvInvoice): void {
    if (invoice.status !== EinvInvoiceStatus.draft) throw new DomainError("BusinessRule", "Only draft invoice can be submitted");
    if (invoice.lines.length === 0) throw new DomainError("Validation", "Cannot submit invoice with no lines");
  }
}

// ─── Can Issue Spec ────────────────────────────────────────────────────────────

export class CanIssueSpec implements Specification<EinvInvoice> {
  isSatisfiedBy(invoice: EinvInvoice): boolean {
    return invoice.status === EinvInvoiceStatus.signed || invoice.status === EinvInvoiceStatus.approved;
  }
  check(invoice: EinvInvoice): void {
    if (!this.isSatisfiedBy(invoice)) throw new DomainError("BusinessRule", "Invoice must be signed or approved before issuance");
  }
}

// ─── Can Cancel Spec ───────────────────────────────────────────────────────────

export class CanCancelSpec implements Specification<EinvInvoice> {
  isSatisfiedBy(invoice: EinvInvoice): boolean {
    return invoice.status === EinvInvoiceStatus.accepted || invoice.status === EinvInvoiceStatus.issued;
  }
  check(invoice: EinvInvoice): void {
    if (!this.isSatisfiedBy(invoice)) throw new DomainError("BusinessRule", "Only accepted/issued invoice can be cancelled");
  }
}

// ─── Invoice Numbering Spec ────────────────────────────────────────────────────

export class SequentialNumberSpec implements Specification<{ seriesCode: string; invoiceNumber: string; expectedNext: number }> {
  isSatisfiedBy(candidate: { seriesCode: string; invoiceNumber: string; expectedNext: number }): boolean {
    const actualNum = parseInt(candidate.invoiceNumber.replace(candidate.seriesCode, ""), 10);
    return actualNum === candidate.expectedNext;
  }
  check(candidate: { seriesCode: string; invoiceNumber: string; expectedNext: number }): void {
    if (!this.isSatisfiedBy(candidate)) {
      throw new DomainError("BusinessRule", `Invoice number ${candidate.invoiceNumber} does not match expected next number ${candidate.expectedNext} in series ${candidate.seriesCode}`);
    }
  }
}

// ─── Category Validation Spec ──────────────────────────────────────────────────

export class InvoiceCategorySpec implements Specification<{ category: EinvInvoiceCategory; hasOriginalInvoice: boolean }> {
  isSatisfiedBy(candidate: { category: EinvInvoiceCategory; hasOriginalInvoice: boolean }): boolean {
    if (candidate.category === EinvInvoiceCategory.adjustment || candidate.category === EinvInvoiceCategory.replacement) {
      return candidate.hasOriginalInvoice;
    }
    return true;
  }
  check(candidate: { category: EinvInvoiceCategory; hasOriginalInvoice: boolean }): void {
    if (!this.isSatisfiedBy(candidate)) {
      throw new DomainError("BusinessRule", `Invoice category ${candidate.category} requires original invoice reference`);
    }
  }
}

// ─── GL Posting Spec ───────────────────────────────────────────────────────────

export class GlPostingSpec implements Specification<EinvInvoice> {
  isSatisfiedBy(invoice: EinvInvoice): boolean {
    return invoice.status === EinvInvoiceStatus.accepted && !invoice.postedToGL;
  }
  check(invoice: EinvInvoice): void {
    if (invoice.postedToGL) throw new DomainError("BusinessRule", "Invoice already posted to GL");
    if (invoice.status !== EinvInvoiceStatus.accepted) throw new DomainError("BusinessRule", "Only accepted invoice can be posted to GL");
  }
}

// ─── Validator functions ───────────────────────────────────────────────────────

export function validateInvoiceNumberFormat(number: string): void {
  if (!/^\d{1,10}$/.test(number)) {
    throw new DomainError("Validation", "Invoice number must be 1-10 digits");
  }
}

export function validateTaxCode(taxCode: string): void {
  if (!/^\d{10}(-\d{3})?$/.test(taxCode)) {
    throw new DomainError("Validation", "Invalid tax code format (expecting 10 or 13 digits)");
  }
}

export function validateAmountInWords(text: string): void {
  if (!text || text.trim().length === 0) {
    throw new DomainError("Validation", "Amount in words cannot be empty");
  }
}

export function validateSeriesFormat(code: string): void {
  if (!/^[A-Z0-9]{1,10}$/.test(code)) {
    throw new DomainError("Validation", "Series code must be 1-10 uppercase alphanumeric characters");
  }
}
