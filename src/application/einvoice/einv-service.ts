import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { EinvInvoice, EinvInvoiceLine } from "../../domain/einvoice/einv-invoice.js";
import { EinvInvoiceId } from "../../domain/einvoice/einv-ids.js";
import {
  EinvInvoiceStatus, EinvInvoiceCategory, EinvAdjustmentType,
} from "../../domain/einvoice/einv-enums.js";
import {
  EinvInvoiceRepository, EinvTemplateRepository, EinvSeriesRepository,
  EinvInvoiceTypeRepository, EinvProviderRepository, EinvCertificateRepository,
  EinvAdjustmentRepository, EinvTransmissionRepository, EinvArchiveRepository,
  EinvReasonCodeRepository,
} from "../../domain/einvoice/einv-repositories.js";
import { GlPostingSpec, CanCancelSpec, InvoiceCategorySpec } from "../../domain/einvoice/einv-specifications.js";

@Injectable()
export class EinvService {
  constructor(
    private readonly invoiceRepo: EinvInvoiceRepository,
    private readonly templateRepo: EinvTemplateRepository,
    private readonly seriesRepo: EinvSeriesRepository,
    private readonly invoiceTypeRepo: EinvInvoiceTypeRepository,
    private readonly providerRepo: EinvProviderRepository,
    private readonly certRepo: EinvCertificateRepository,
    private readonly adjustmentRepo: EinvAdjustmentRepository,
    private readonly transmissionRepo: EinvTransmissionRepository,
    private readonly archiveRepo: EinvArchiveRepository,
    private readonly reasonCodeRepo: EinvReasonCodeRepository,
  ) {}

  // ─── Invoice Lifecycle ───────────────────────────────────────────────────────

  async createInvoice(dto: {
    invoiceNumber: string; invoiceTypeId: string; templateId: string;
    sellerName: string; sellerTaxCode: string; buyerName: string;
    invoiceDate: Date; category?: EinvInvoiceCategory;
    salesInvoiceId?: string; invoiceCode?: string; invoiceSymbol?: string;
    seriesId?: string; providerId?: string;
    sellerAddress?: string; sellerPhone?: string; sellerEmail?: string;
    sellerBankName?: string; sellerBankAccount?: string;
    buyerTaxCode?: string; buyerAddress?: string; buyerPhone?: string; buyerEmail?: string;
    buyerBankName?: string; buyerBankAccount?: string;
    currencyCode?: string; exchangeRate?: number;
    createdBy?: string;
  }): Promise<EinvInvoice> {
    const existing = await this.invoiceRepo.findByInvoiceNumber(dto.invoiceNumber);
    if (existing) throw new DomainError("Conflict", `Invoice number ${dto.invoiceNumber} already exists`);

    const catSpec = new InvoiceCategorySpec();
    catSpec.check({ category: dto.category ?? EinvInvoiceCategory.sales, hasOriginalInvoice: !!dto.salesInvoiceId });

    const invoice = EinvInvoice.create(dto as any);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async addLine(invoiceId: string, dto: {
    lineNumber: number; itemCode: string; itemName: string; unit: string;
    quantity: number; unitPrice: bigint;
    discountPercent?: number; discountAmount?: bigint;
    taxCode?: string; taxRate?: number;
    salesLineId?: string; itemId?: string; description?: string;
  }): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    const line = EinvInvoiceLine.create({ invoiceId, ...dto });
    invoice.addLine(line);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async submitInvoice(invoiceId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.submit();
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async approveInvoice(invoiceId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.approve();
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async rejectInvoice(invoiceId: string, reason: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.reject(reason);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async signInvoice(invoiceId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.sign();
    // Generate XML and PDF would happen here via provider adapter
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async issueInvoice(invoiceId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.issue();
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async cancelInvoice(invoiceId: string, reason: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    const spec = new CanCancelSpec();
    spec.check(invoice);
    invoice.cancel(reason);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async markAccepted(invoiceId: string, taxAuthorityCode: string, verifyCode: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    invoice.markAccepted(taxAuthorityCode, verifyCode);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  async postToGL(invoiceId: string, glBatchId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    const spec = new GlPostingSpec();
    spec.check(invoice);
    invoice.markPostedToGL(glBatchId);
    await this.invoiceRepo.save(invoice);
    return invoice;
  }

  // ─── Queries ─────────────────────────────────────────────────────────────────

  async getInvoice(invoiceId: string): Promise<EinvInvoice> {
    const invoice = await this.invoiceRepo.findById(new EinvInvoiceId(invoiceId));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    return invoice;
  }

  async findBySalesInvoiceId(salesInvoiceId: string): Promise<EinvInvoice | null> {
    return this.invoiceRepo.findBySalesInvoiceId(salesInvoiceId);
  }

  async listInvoices(params?: {
    status?: string; buyerTaxCode?: string;
    fromDate?: Date; toDate?: Date; limit?: number; offset?: number;
  }) {
    return this.invoiceRepo.findAll(params);
  }

  async findPendingTransmission(): Promise<EinvInvoice[]> {
    return this.invoiceRepo.findPendingTransmission();
  }

  // ─── Master Data ─────────────────────────────────────────────────────────────

  async getInvoiceTypes() { return this.invoiceTypeRepo.findAll(); }
  async getTemplates() { return this.templateRepo.findAll(); }
  async getSeries(invoiceTypeId?: string) {
    if (invoiceTypeId) return this.seriesRepo.findByInvoiceType(invoiceTypeId);
    return this.seriesRepo.findAll();
  }
  async getProviders() { return this.providerRepo.findAll(); }
  async getReasonCodes(category?: string) {
    if (category) return this.reasonCodeRepo.findByCategory(category);
    return this.reasonCodeRepo.findAll();
  }
  async getCertificates(providerId?: string) {
    if (providerId) return this.certRepo.findValidByProvider(providerId);
    return []; // would need a findAll on cert repo
  }
}
