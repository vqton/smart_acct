import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { EinvInvoiceId, EinvInvoiceLineId, EinvTemplateId, EinvSeriesId, EinvProviderId, EinvCertificateId, EinvProviderTemplateId, EinvInvoiceTypeId, EinvReasonCodeId, EinvAdjustmentId, EinvTransmissionId, EinvArchiveId } from "../../domain/einvoice/einv-ids.js";
import { EinvInvoice, EinvInvoiceState, EinvInvoiceLine, EinvInvoiceLineState } from "../../domain/einvoice/einv-invoice.js";
import { EinvTemplate, EinvTemplateState } from "../../domain/einvoice/einv-master.js";
import { EinvSeries, EinvSeriesState } from "../../domain/einvoice/einv-master.js";
import { EinvProvider, EinvProviderState } from "../../domain/einvoice/einv-master.js";
import { EinvDigitalCertificate, EinvCertificateState } from "../../domain/einvoice/einv-master.js";
import { EinvProviderTemplate, EinvProviderTemplateState } from "../../domain/einvoice/einv-master.js";
import { EinvInvoiceType, EinvInvoiceTypeState } from "../../domain/einvoice/einv-master.js";
import { EinvReasonCode, EinvReasonCodeState } from "../../domain/einvoice/einv-master.js";
import { EinvAdjustment, EinvAdjustmentState } from "../../domain/einvoice/einv-adjustment.js";
import { EinvTransmission, EinvTransmissionState } from "../../domain/einvoice/einv-transmission.js";
import { EinvArchive, EinvArchiveState } from "../../domain/einvoice/einv-archive.js";
import { EinvInvoiceRepository, EinvTemplateRepository, EinvSeriesRepository, EinvProviderRepository, EinvCertificateRepository, EinvProviderTemplateRepository, EinvInvoiceTypeRepository, EinvReasonCodeRepository, EinvAdjustmentRepository, EinvTransmissionRepository, EinvArchiveRepository } from "../../domain/einvoice/einv-repositories.js";

// ─── Helper: DB row → Domain entity conversions ────────────────────────────────

function fromPrismaInvoice(row: any, lines?: any[]): EinvInvoice {
  const i = EinvInvoice.load({
    id: row.id, salesInvoiceId: row.salesInvoiceId,
    invoiceNumber: row.invoiceNumber, invoiceCode: row.invoiceCode,
    invoiceSymbol: row.invoiceSymbol, invoiceName: row.invoiceName,
    invoiceTypeId: row.invoiceTypeId, templateId: row.templateId,
    seriesId: row.seriesId, providerId: row.providerId,
    sellerName: row.sellerName, sellerTaxCode: row.sellerTaxCode,
    sellerAddress: row.sellerAddress, sellerPhone: row.sellerPhone,
    sellerEmail: row.sellerEmail, sellerBankName: row.sellerBankName,
    sellerBankAccount: row.sellerBankAccount,
    buyerName: row.buyerName, buyerTaxCode: row.buyerTaxCode,
    buyerAddress: row.buyerAddress, buyerPhone: row.buyerPhone,
    buyerEmail: row.buyerEmail, buyerBankName: row.buyerBankName,
    buyerBankAccount: row.buyerBankAccount,
    currencyCode: row.currencyCode, exchangeRate: Number(row.exchangeRate),
    subtotal: BigInt(row.subtotal), discountAmount: BigInt(row.discountAmount),
    taxAmount: BigInt(row.taxAmount), grandTotal: BigInt(row.grandTotal),
    amountInWords: row.amountInWords,
    status: row.status, category: row.category,
    invoiceDate: row.invoiceDate, issueDate: row.issueDate, signingDate: row.signingDate,
    taxAuthorityCode: row.taxAuthorityCode,
    taxAuthorityResponse: row.taxAuthorityResponse, verifyCode: row.verifyCode,
    glBatchId: row.glBatchId, postedToGL: row.postedToGL,
    xmlData: row.xmlData, pdfData: row.pdfData,
    version: row.version, createdBy: row.createdBy,
    createdAt: row.createdAt, updatedAt: row.updatedAt, deletedAt: row.deletedAt,
  });
  if (lines) {
    lines.forEach((l: any) => i.addLine(fromPrismaLine(l)));
  }
  return i;
}

function fromPrismaLine(row: any): EinvInvoiceLine {
  return EinvInvoiceLine.load({
    id: row.id, invoiceId: row.invoiceId, lineNumber: row.lineNumber,
    itemCode: row.itemCode, itemName: row.itemName, unit: row.unit,
    quantity: Number(row.quantity), unitPrice: BigInt(row.unitPrice),
    totalPrice: BigInt(row.totalPrice), discountPercent: Number(row.discountPercent),
    discountAmount: BigInt(row.discountAmount),
    taxCode: row.taxCode, taxRate: Number(row.taxRate), taxAmount: BigInt(row.taxAmount),
    netAmount: BigInt(row.netAmount),
    salesLineId: row.salesLineId, itemId: row.itemId, description: row.description,
  });
}

function fromPrismaTemplate(row: any): EinvTemplate {
  return EinvTemplate.load({
    id: row.id, code: row.code, name: row.name, description: row.description,
    templateFile: row.templateFile, isDefault: row.isDefault, isActive: row.isActive,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaSeries(row: any): EinvSeries {
  return EinvSeries.load({
    id: row.id, code: row.code, name: row.name, invoiceTypeId: row.invoiceTypeId,
    prefix: row.prefix, suffix: row.suffix,
    currentNumber: row.currentNumber, nextNumber: row.nextNumber,
    minDigits: row.minDigits, maxDigits: row.maxDigits,
    fiscalYear: row.fiscalYear, isActive: row.isActive,
    validFrom: row.validFrom, validTo: row.validTo,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaProvider(row: any): EinvProvider {
  return EinvProvider.load({
    id: row.id, code: row.code, name: row.name, providerType: row.providerType,
    apiEndpoint: row.apiEndpoint, apiVersion: row.apiVersion,
    apiUsername: row.apiUsername, apiPassword: row.apiPassword,
    apiKey: row.apiKey, apiSecret: row.apiSecret,
    timeout: row.timeout, maxRetries: row.maxRetries, isActive: row.isActive,
    config: row.config, version: row.version,
    createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaCertificate(row: any): EinvDigitalCertificate {
  return EinvDigitalCertificate.load({
    id: row.id, providerId: row.providerId, serialNumber: row.serialNumber,
    subjectDN: row.subjectDN, issuerDN: row.issuerDN,
    issuedTo: row.issuedTo, issuedBy: row.issuedBy,
    validFrom: row.validFrom, validTo: row.validTo,
    thumbprint: row.thumbprint, certificateData: row.certificateData,
    privateKeyRef: row.privateKeyRef, algorithm: row.algorithm,
    digestAlgorithm: row.digestAlgorithm, status: row.status,
    isDefault: row.isDefault, companyId: row.companyId, branchId: row.branchId,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaInvoiceType(row: any): EinvInvoiceType {
  return EinvInvoiceType.load({
    id: row.id, code: row.code, name: row.name, description: row.description,
    category: row.category, isActive: row.isActive,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaReasonCode(row: any): EinvReasonCode {
  return EinvReasonCode.load({
    id: row.id, code: row.code, name: row.name, description: row.description,
    category: row.category, isActive: row.isActive,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaAdjustment(row: any): EinvAdjustment {
  return EinvAdjustment.load({
    id: row.id, invoiceId: row.invoiceId, adjustmentType: row.adjustmentType,
    originalInvoiceId: row.originalInvoiceId, reasonCode: row.reasonCode,
    reasonDescription: row.reasonDescription, adjustmentNumber: row.adjustmentNumber,
    adjustmentDate: row.adjustmentDate, additionalData: row.additionalData,
    version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaTransmission(row: any): EinvTransmission {
  return EinvTransmission.load({
    id: row.id, invoiceId: row.invoiceId, providerId: row.providerId,
    transmissionId: row.transmissionId, status: row.status,
    requestData: row.requestData, responseData: row.responseData,
    statusCode: row.statusCode, statusMessage: row.statusMessage,
    retryCount: row.retryCount, maxRetries: row.maxRetries,
    nextRetryAt: row.nextRetryAt, acknowledgedAt: row.acknowledgedAt,
    completedAt: row.completedAt, failedAt: row.failedAt,
    errorDetail: row.errorDetail, version: row.version,
    createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

function fromPrismaArchive(row: any): EinvArchive {
  return EinvArchive.load({
    id: row.id, invoiceId: row.invoiceId, archiveDate: row.archiveDate,
    archiveType: row.archiveType, storagePath: row.storagePath,
    xmlData: row.xmlData, pdfData: row.pdfData,
    checksum: row.checksum, fileSize: row.fileSize ? BigInt(row.fileSize) : null,
    status: row.status, retentionUntil: row.retentionUntil,
    destroyedAt: row.destroyedAt, version: row.version,
    createdAt: row.createdAt, updatedAt: row.updatedAt,
  });
}

// ─── Invoice Repository ────────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvInvoiceRepository implements EinvInvoiceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(invoice: EinvInvoice): Promise<void> {
    const s = invoice.toState();
    await (this.prisma as any).einvInvoice.upsert({
      where: { id: s.id }, create: s, update: s,
    });
    const lines = invoice.lines.map(l => l.toState());
    for (const line of lines) {
      await (this.prisma as any).einvInvoiceLine.upsert({
        where: { id: line.id }, create: line, update: line,
      });
    }
  }

  async findById(id: EinvInvoiceId): Promise<EinvInvoice | null> {
    const row = await (this.prisma as any).einvInvoice.findUnique({
      where: { id: id.value }, include: { lines: true },
    });
    return row ? fromPrismaInvoice(row, row.lines) : null;
  }

  async findByInvoiceNumber(number: string): Promise<EinvInvoice | null> {
    const row = await (this.prisma as any).einvInvoice.findUnique({
      where: { invoiceNumber: number }, include: { lines: true },
    });
    return row ? fromPrismaInvoice(row, row.lines) : null;
  }

  async findBySalesInvoiceId(salesInvoiceId: string): Promise<EinvInvoice | null> {
    const row = await (this.prisma as any).einvInvoice.findUnique({
      where: { salesInvoiceId }, include: { lines: true },
    });
    return row ? fromPrismaInvoice(row, row.lines) : null;
  }

  async findByStatus(status: string): Promise<EinvInvoice[]> {
    const rows = await (this.prisma as any).einvInvoice.findMany({
      where: { status }, include: { lines: true },
    });
    return rows.map((r: any) => fromPrismaInvoice(r, r.lines));
  }

  async findPendingTransmission(): Promise<EinvInvoice[]> {
    const rows = await (this.prisma as any).einvInvoice.findMany({
      where: { status: "issued" },
      include: { lines: true },
    });
    return rows.map((r: any) => fromPrismaInvoice(r, r.lines));
  }

  async findAll(params?: { status?: string; buyerTaxCode?: string; fromDate?: Date; toDate?: Date; limit?: number; offset?: number }): Promise<{ invoices: EinvInvoiceState[]; total: number }> {
    const where: any = {};
    if (params?.status) where.status = params.status;
    if (params?.buyerTaxCode) where.buyerTaxCode = params.buyerTaxCode;
    if (params?.fromDate || params?.toDate) {
      where.invoiceDate = {};
      if (params?.fromDate) where.invoiceDate.gte = params.fromDate;
      if (params?.toDate) where.invoiceDate.lte = params.toDate;
    }
    const [rows, total] = await Promise.all([
      (this.prisma as any).einvInvoice.findMany({
        where, skip: params?.offset ?? 0, take: params?.limit ?? 50, orderBy: { createdAt: "desc" },
      }),
      (this.prisma as any).einvInvoice.count({ where }),
    ]);
    return { invoices: rows, total };
  }
}

// ─── Template Repository ───────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvTemplateRepository implements EinvTemplateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(template: EinvTemplate): Promise<void> {
    const s = template.toState();
    await (this.prisma as any).einvTemplate.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvTemplate | null> {
    const row = await (this.prisma as any).einvTemplate.findUnique({ where: { id } });
    return row ? fromPrismaTemplate(row) : null;
  }

  async findByCode(code: string): Promise<EinvTemplate | null> {
    const row = await (this.prisma as any).einvTemplate.findUnique({ where: { code } });
    return row ? fromPrismaTemplate(row) : null;
  }

  async findAll(): Promise<EinvTemplateState[]> {
    return (this.prisma as any).einvTemplate.findMany({ orderBy: { code: "asc" } });
  }
}

// ─── Series Repository ─────────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvSeriesRepository implements EinvSeriesRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(series: EinvSeries): Promise<void> {
    const s = series.toState();
    await (this.prisma as any).einvSeries.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvSeries | null> {
    const row = await (this.prisma as any).einvSeries.findUnique({ where: { id } });
    return row ? fromPrismaSeries(row) : null;
  }

  async findByCodeAndType(code: string, invoiceTypeId: string): Promise<EinvSeries | null> {
    const row = await (this.prisma as any).einvSeries.findFirst({
      where: { code, invoiceTypeId },
    });
    return row ? fromPrismaSeries(row) : null;
  }

  async findByInvoiceType(invoiceTypeId: string): Promise<EinvSeriesState[]> {
    return (this.prisma as any).einvSeries.findMany({ where: { invoiceTypeId }, orderBy: { code: "asc" } });
  }

  async findAll(): Promise<EinvSeriesState[]> {
    return (this.prisma as any).einvSeries.findMany({ orderBy: { code: "asc" } });
  }

  async getNextNumber(id: string): Promise<number> {
    const series = await this.findById(id);
    return series ? series.nextNumber : 1;
  }
}

// ─── Invoice Type Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaEinvInvoiceTypeRepository implements EinvInvoiceTypeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(type: EinvInvoiceType): Promise<void> {
    const s = type.toState();
    await (this.prisma as any).einvInvoiceType.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvInvoiceType | null> {
    const row = await (this.prisma as any).einvInvoiceType.findUnique({ where: { id } });
    return row ? fromPrismaInvoiceType(row) : null;
  }

  async findByCode(code: string): Promise<EinvInvoiceType | null> {
    const row = await (this.prisma as any).einvInvoiceType.findUnique({ where: { code } });
    return row ? fromPrismaInvoiceType(row) : null;
  }

  async findAll(): Promise<EinvInvoiceTypeState[]> {
    return (this.prisma as any).einvInvoiceType.findMany({ orderBy: { code: "asc" } });
  }
}

// ─── Provider Repository ───────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvProviderRepository implements EinvProviderRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(provider: EinvProvider): Promise<void> {
    const s = provider.toState();
    await (this.prisma as any).einvProvider.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvProvider | null> {
    const row = await (this.prisma as any).einvProvider.findUnique({ where: { id } });
    return row ? fromPrismaProvider(row) : null;
  }

  async findByCode(code: string): Promise<EinvProvider | null> {
    const row = await (this.prisma as any).einvProvider.findUnique({ where: { code } });
    return row ? fromPrismaProvider(row) : null;
  }

  async findAll(): Promise<EinvProviderState[]> {
    return (this.prisma as any).einvProvider.findMany({ orderBy: { code: "asc" } });
  }
}

// ─── Provider Template Repository ──────────────────────────────────────────────

@Injectable()
export class PrismaEinvProviderTemplateRepository implements EinvProviderTemplateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(pt: EinvProviderTemplate): Promise<void> {
    const s = pt.toState();
    await (this.prisma as any).einvProviderTemplate.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findByProviderAndTemplate(providerId: string, templateId: string): Promise<EinvProviderTemplate | null> {
    const row = await (this.prisma as any).einvProviderTemplate.findFirst({
      where: { providerId, templateId },
    });
    return row ? EinvProviderTemplate.load(row) : null;
  }

  async findByProvider(providerId: string): Promise<EinvProviderTemplateState[]> {
    return (this.prisma as any).einvProviderTemplate.findMany({ where: { providerId } });
  }
}

// ─── Certificate Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvCertificateRepository implements EinvCertificateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(cert: EinvDigitalCertificate): Promise<void> {
    const s = cert.toState();
    await (this.prisma as any).einvDigitalCertificate.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvDigitalCertificate | null> {
    const row = await (this.prisma as any).einvDigitalCertificate.findUnique({ where: { id } });
    return row ? fromPrismaCertificate(row) : null;
  }

  async findBySerialNumber(serialNumber: string): Promise<EinvDigitalCertificate | null> {
    const row = await (this.prisma as any).einvDigitalCertificate.findUnique({ where: { serialNumber } });
    return row ? fromPrismaCertificate(row) : null;
  }

  async findValidByProvider(providerId: string): Promise<EinvCertificateState[]> {
    return (this.prisma as any).einvDigitalCertificate.findMany({
      where: { providerId, status: "active", validTo: { gte: new Date() } },
      orderBy: { validTo: "desc" },
    });
  }

  async findExpiring(days: number): Promise<EinvCertificateState[]> {
    const future = new Date();
    future.setDate(future.getDate() + days);
    return (this.prisma as any).einvDigitalCertificate.findMany({
      where: { status: "active", validTo: { lte: future } },
      orderBy: { validTo: "asc" },
    });
  }
}

// ─── Adjustment Repository ─────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvAdjustmentRepository implements EinvAdjustmentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(adjustment: EinvAdjustment): Promise<void> {
    const s = adjustment.toState();
    await (this.prisma as any).einvAdjustment.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findByInvoiceId(invoiceId: string): Promise<EinvAdjustment | null> {
    const row = await (this.prisma as any).einvAdjustment.findFirst({ where: { invoiceId } });
    return row ? fromPrismaAdjustment(row) : null;
  }

  async findByOriginalInvoiceId(originalInvoiceId: string): Promise<EinvAdjustment[]> {
    const rows = await (this.prisma as any).einvAdjustment.findMany({ where: { originalInvoiceId } });
    return rows.map(fromPrismaAdjustment);
  }
}

// ─── Transmission Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaEinvTransmissionRepository implements EinvTransmissionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transmission: EinvTransmission): Promise<void> {
    const s = transmission.toState();
    await (this.prisma as any).einvTransmission.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findById(id: string): Promise<EinvTransmission | null> {
    const row = await (this.prisma as any).einvTransmission.findUnique({ where: { id } });
    return row ? fromPrismaTransmission(row) : null;
  }

  async findByInvoiceId(invoiceId: string): Promise<EinvTransmission[]> {
    const rows = await (this.prisma as any).einvTransmission.findMany({ where: { invoiceId } });
    return rows.map(fromPrismaTransmission);
  }

  async findPendingRetry(): Promise<EinvTransmissionState[]> {
    return (this.prisma as any).einvTransmission.findMany({
      where: { status: "retrying", nextRetryAt: { lte: new Date() } },
      orderBy: { nextRetryAt: "asc" },
    });
  }
}

// ─── Archive Repository ────────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvArchiveRepository implements EinvArchiveRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(archive: EinvArchive): Promise<void> {
    const s = archive.toState();
    await (this.prisma as any).einvArchive.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findByInvoiceId(invoiceId: string): Promise<EinvArchive | null> {
    const row = await (this.prisma as any).einvArchive.findFirst({ where: { invoiceId } });
    return row ? fromPrismaArchive(row) : null;
  }

  async findExpired(): Promise<EinvArchiveState[]> {
    return (this.prisma as any).einvArchive.findMany({
      where: { retentionUntil: { lte: new Date() }, status: "active" },
    });
  }
}

// ─── Reason Code Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaEinvReasonCodeRepository implements EinvReasonCodeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(reasonCode: EinvReasonCode): Promise<void> {
    const s = reasonCode.toState();
    await (this.prisma as any).einvReasonCode.upsert({ where: { id: s.id }, create: s, update: s });
  }

  async findByCode(code: string): Promise<EinvReasonCode | null> {
    const row = await (this.prisma as any).einvReasonCode.findUnique({ where: { code } });
    return row ? fromPrismaReasonCode(row) : null;
  }

  async findByCategory(category: string): Promise<EinvReasonCodeState[]> {
    return (this.prisma as any).einvReasonCode.findMany({ where: { category } });
  }

  async findAll(): Promise<EinvReasonCodeState[]> {
    return (this.prisma as any).einvReasonCode.findMany({ orderBy: { code: "asc" } });
  }
}
