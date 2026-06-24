import { EinvInvoice, EinvInvoiceState } from "./einv-invoice.js";
import { EinvInvoiceId } from "./einv-ids.js";
import { EinvTemplate, EinvTemplateState } from "./einv-master.js";
import { EinvSeries, EinvSeriesState } from "./einv-master.js";
import { EinvProvider, EinvProviderState } from "./einv-master.js";
import { EinvDigitalCertificate, EinvCertificateState } from "./einv-master.js";
import { EinvProviderTemplate, EinvProviderTemplateState } from "./einv-master.js";
import { EinvInvoiceType, EinvInvoiceTypeState } from "./einv-master.js";
import { EinvReasonCode, EinvReasonCodeState } from "./einv-master.js";
import { EinvAdjustment, EinvAdjustmentState } from "./einv-adjustment.js";
import { EinvTransmission, EinvTransmissionState } from "./einv-transmission.js";
import { EinvArchive, EinvArchiveState } from "./einv-archive.js";

// ─── Invoice Repository ────────────────────────────────────────────────────────

export interface EinvInvoiceRepository {
  save(invoice: EinvInvoice): Promise<void>;
  findById(id: EinvInvoiceId): Promise<EinvInvoice | null>;
  findByInvoiceNumber(number: string): Promise<EinvInvoice | null>;
  findBySalesInvoiceId(salesInvoiceId: string): Promise<EinvInvoice | null>;
  findByStatus(status: string): Promise<EinvInvoice[]>;
  findPendingTransmission(): Promise<EinvInvoice[]>;
  findAll(params?: { status?: string; buyerTaxCode?: string; fromDate?: Date; toDate?: Date; limit?: number; offset?: number }): Promise<{ invoices: EinvInvoiceState[]; total: number }>;
}

// ─── Template Repository ───────────────────────────────────────────────────────

export interface EinvTemplateRepository {
  save(template: EinvTemplate): Promise<void>;
  findById(id: string): Promise<EinvTemplate | null>;
  findByCode(code: string): Promise<EinvTemplate | null>;
  findAll(): Promise<EinvTemplateState[]>;
}

// ─── Series Repository ─────────────────────────────────────────────────────────

export interface EinvSeriesRepository {
  save(series: EinvSeries): Promise<void>;
  findById(id: string): Promise<EinvSeries | null>;
  findByCodeAndType(code: string, invoiceTypeId: string): Promise<EinvSeries | null>;
  findByInvoiceType(invoiceTypeId: string): Promise<EinvSeriesState[]>;
  findAll(): Promise<EinvSeriesState[]>;
  getNextNumber(id: string): Promise<number>;
}

// ─── Invoice Type Repository ───────────────────────────────────────────────────

export interface EinvInvoiceTypeRepository {
  save(type: EinvInvoiceType): Promise<void>;
  findById(id: string): Promise<EinvInvoiceType | null>;
  findByCode(code: string): Promise<EinvInvoiceType | null>;
  findAll(): Promise<EinvInvoiceTypeState[]>;
}

// ─── Provider Repository ───────────────────────────────────────────────────────

export interface EinvProviderRepository {
  save(provider: EinvProvider): Promise<void>;
  findById(id: string): Promise<EinvProvider | null>;
  findByCode(code: string): Promise<EinvProvider | null>;
  findAll(): Promise<EinvProviderState[]>;
}

// ─── Provider Template Repository ──────────────────────────────────────────────

export interface EinvProviderTemplateRepository {
  save(pt: EinvProviderTemplate): Promise<void>;
  findByProviderAndTemplate(providerId: string, templateId: string): Promise<EinvProviderTemplate | null>;
  findByProvider(providerId: string): Promise<EinvProviderTemplateState[]>;
}

// ─── Certificate Repository ────────────────────────────────────────────────────

export interface EinvCertificateRepository {
  save(cert: EinvDigitalCertificate): Promise<void>;
  findById(id: string): Promise<EinvDigitalCertificate | null>;
  findBySerialNumber(serialNumber: string): Promise<EinvDigitalCertificate | null>;
  findValidByProvider(providerId: string): Promise<EinvCertificateState[]>;
  findExpiring(days: number): Promise<EinvCertificateState[]>;
}

// ─── Adjustment Repository ─────────────────────────────────────────────────────

export interface EinvAdjustmentRepository {
  save(adjustment: EinvAdjustment): Promise<void>;
  findByInvoiceId(invoiceId: string): Promise<EinvAdjustment | null>;
  findByOriginalInvoiceId(originalInvoiceId: string): Promise<EinvAdjustment[]>;
}

// ─── Transmission Repository ───────────────────────────────────────────────────

export interface EinvTransmissionRepository {
  save(transmission: EinvTransmission): Promise<void>;
  findById(id: string): Promise<EinvTransmission | null>;
  findByInvoiceId(invoiceId: string): Promise<EinvTransmission[]>;
  findPendingRetry(): Promise<EinvTransmissionState[]>;
}

// ─── Archive Repository ────────────────────────────────────────────────────────

export interface EinvArchiveRepository {
  save(archive: EinvArchive): Promise<void>;
  findByInvoiceId(invoiceId: string): Promise<EinvArchive | null>;
  findExpired(): Promise<EinvArchiveState[]>;
}

// ─── Reason Code Repository ────────────────────────────────────────────────────

export interface EinvReasonCodeRepository {
  save(reasonCode: EinvReasonCode): Promise<void>;
  findByCode(code: string): Promise<EinvReasonCode | null>;
  findByCategory(category: string): Promise<EinvReasonCodeState[]>;
  findAll(): Promise<EinvReasonCodeState[]>;
}
