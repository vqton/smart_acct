import { Controller, Get, Post, Put, Param, Body, Query, HttpCode, HttpStatus, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery, ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { EinvService } from "../../application/einvoice/einv-service.js";
import { PrismaEinvInvoiceRepository, PrismaEinvTemplateRepository, PrismaEinvSeriesRepository, PrismaEinvInvoiceTypeRepository, PrismaEinvProviderRepository, PrismaEinvReasonCodeRepository, PrismaEinvCertificateRepository } from "../../infrastructure/einvoice/einv-prisma-repos.js";
import { EinvInvoiceStatus, EinvInvoiceCategory } from "../../domain/einvoice/einv-enums.js";

// ─── DTOs ──────────────────────────────────────────────────────────────────────

class CreateInvoiceDto {
  @ApiProperty() invoiceNumber!: string;
  @ApiProperty() invoiceTypeId!: string;
  @ApiProperty() templateId!: string;
  @ApiProperty() sellerName!: string;
  @ApiProperty() sellerTaxCode!: string;
  @ApiProperty() buyerName!: string;
  @ApiProperty() invoiceDate!: Date;
  @ApiPropertyOptional({ enum: EinvInvoiceCategory }) category?: EinvInvoiceCategory;
  @ApiPropertyOptional() salesInvoiceId?: string;
  @ApiPropertyOptional() invoiceCode?: string;
  @ApiPropertyOptional() invoiceSymbol?: string;
  @ApiPropertyOptional() seriesId?: string;
  @ApiPropertyOptional() providerId?: string;
  @ApiPropertyOptional() sellerAddress?: string;
  @ApiPropertyOptional() sellerPhone?: string;
  @ApiPropertyOptional() sellerEmail?: string;
  @ApiPropertyOptional() sellerBankName?: string;
  @ApiPropertyOptional() sellerBankAccount?: string;
  @ApiPropertyOptional() buyerTaxCode?: string;
  @ApiPropertyOptional() buyerAddress?: string;
  @ApiPropertyOptional() buyerPhone?: string;
  @ApiPropertyOptional() buyerEmail?: string;
  @ApiPropertyOptional() buyerBankName?: string;
  @ApiPropertyOptional() buyerBankAccount?: string;
  @ApiPropertyOptional() currencyCode?: string;
  @ApiPropertyOptional() exchangeRate?: number;
  @ApiPropertyOptional() createdBy?: string;
}

class AddLineDto {
  @ApiProperty() lineNumber!: number;
  @ApiProperty() itemCode!: string;
  @ApiProperty() itemName!: string;
  @ApiProperty() unit!: string;
  @ApiProperty() quantity!: number;
  @ApiProperty() unitPrice!: string;
  @ApiPropertyOptional() discountPercent?: number;
  @ApiPropertyOptional() discountAmount?: string;
  @ApiPropertyOptional() taxCode?: string;
  @ApiPropertyOptional() taxRate?: number;
  @ApiPropertyOptional() salesLineId?: string;
  @ApiPropertyOptional() itemId?: string;
  @ApiPropertyOptional() description?: string;
}

class CancelInvoiceDto { @ApiProperty() reason!: string; }
class RejectInvoiceDto { @ApiProperty() reason!: string; }
class AcceptInvoiceDto { @ApiProperty() taxAuthorityCode!: string; @ApiProperty() verifyCode!: string; }
class PostToGLDto { @ApiProperty() glBatchId!: string; }

// ─── Invoice Controller ───────────────────────────────────────────────────────

@ApiTags("E-Invoice")
@Controller("api/einv")
export class EinvController {
  constructor(
    private readonly einvService: EinvService,
    private readonly invoiceRepo: PrismaEinvInvoiceRepository,
    private readonly templateRepo: PrismaEinvTemplateRepository,
    private readonly seriesRepo: PrismaEinvSeriesRepository,
    private readonly invoiceTypeRepo: PrismaEinvInvoiceTypeRepository,
    private readonly providerRepo: PrismaEinvProviderRepository,
    private readonly reasonCodeRepo: PrismaEinvReasonCodeRepository,
    private readonly certRepo: PrismaEinvCertificateRepository,
  ) {}

  // ─── Invoice CRUD ────────────────────────────────────────────────────────────

  @Post("invoices")
  @ApiOperation({ summary: "Create e-invoice" })
  async create(@Body() dto: CreateInvoiceDto) {
    const existing = await this.invoiceRepo.findByInvoiceNumber(dto.invoiceNumber);
    if (existing) throw new ConflictException(`Invoice number ${dto.invoiceNumber} already exists`);
    const invoice = await this.einvService.createInvoice(dto);
    return invoice.toState();
  }

  @Get("invoices/:id")
  @ApiOperation({ summary: "Get e-invoice by ID" })
  async get(@Param("id") id: string) {
    const invoice = await this.einvService.getInvoice(id);
    return invoice.toState();
  }

  @Get("invoices")
  @ApiOperation({ summary: "List e-invoices" })
  @ApiQuery({ name: "status", required: false })
  @ApiQuery({ name: "buyerTaxCode", required: false })
  @ApiQuery({ name: "fromDate", required: false })
  @ApiQuery({ name: "toDate", required: false })
  @ApiQuery({ name: "limit", required: false })
  @ApiQuery({ name: "offset", required: false })
  async list(
    @Query("status") status?: string,
    @Query("buyerTaxCode") buyerTaxCode?: string,
    @Query("fromDate") fromDate?: string,
    @Query("toDate") toDate?: string,
    @Query("limit") limit?: string,
    @Query("offset") offset?: string,
  ) {
    const params: any = {};
    if (status) params.status = status;
    if (buyerTaxCode) params.buyerTaxCode = buyerTaxCode;
    if (fromDate) params.fromDate = new Date(fromDate);
    if (toDate) params.toDate = new Date(toDate);
    if (limit) params.limit = parseInt(limit, 10);
    if (offset) params.offset = parseInt(offset, 10);
    return this.einvService.listInvoices(params);
  }

  @Get("invoices/by-sales/:salesInvoiceId")
  @ApiOperation({ summary: "Find e-invoice by sales invoice ID" })
  async findBySalesInvoice(@Param("salesInvoiceId") salesInvoiceId: string) {
    const inv = await this.einvService.findBySalesInvoiceId(salesInvoiceId);
    if (!inv) throw new NotFoundException("E-invoice not found for this sales invoice");
    return inv.toState();
  }

  // ─── Line Management ─────────────────────────────────────────────────────────

  @Post("invoices/:id/lines")
  @ApiOperation({ summary: "Add line to e-invoice" })
  async addLine(@Param("id") id: string, @Body() dto: AddLineDto) {
    const invoice = await this.einvService.addLine(id, {
      ...dto,
      unitPrice: BigInt(dto.unitPrice),
      discountAmount: dto.discountAmount ? BigInt(dto.discountAmount) : undefined,
    });
    return invoice.toState();
  }

  // ─── Lifecycle ───────────────────────────────────────────────────────────────

  @Post("invoices/:id/submit")
  @ApiOperation({ summary: "Submit e-invoice for approval" })
  async submit(@Param("id") id: string) {
    const invoice = await this.einvService.submitInvoice(id);
    return invoice.toState();
  }

  @Post("invoices/:id/approve")
  @ApiOperation({ summary: "Approve e-invoice" })
  async approve(@Param("id") id: string) {
    const invoice = await this.einvService.approveInvoice(id);
    return invoice.toState();
  }

  @Post("invoices/:id/reject")
  @ApiOperation({ summary: "Reject e-invoice" })
  async reject(@Param("id") id: string, @Body() dto: RejectInvoiceDto) {
    const invoice = await this.einvService.rejectInvoice(id, dto.reason);
    return invoice.toState();
  }

  @Post("invoices/:id/sign")
  @ApiOperation({ summary: "Digitally sign e-invoice" })
  async sign(@Param("id") id: string) {
    const invoice = await this.einvService.signInvoice(id);
    return invoice.toState();
  }

  @Post("invoices/:id/issue")
  @ApiOperation({ summary: "Issue e-invoice (official)" })
  async issue(@Param("id") id: string) {
    const invoice = await this.einvService.issueInvoice(id);
    return invoice.toState();
  }

  @Post("invoices/:id/cancel")
  @ApiOperation({ summary: "Cancel e-invoice" })
  async cancel(@Param("id") id: string, @Body() dto: CancelInvoiceDto) {
    const invoice = await this.einvService.cancelInvoice(id, dto.reason);
    return invoice.toState();
  }

  @Post("invoices/:id/accept")
  @ApiOperation({ summary: "Mark e-invoice as accepted by tax authority" })
  async accept(@Param("id") id: string, @Body() dto: AcceptInvoiceDto) {
    const invoice = await this.einvService.markAccepted(id, dto.taxAuthorityCode, dto.verifyCode);
    return invoice.toState();
  }

  @Post("invoices/:id/post-to-gl")
  @ApiOperation({ summary: "Post e-invoice to General Ledger" })
  async postToGL(@Param("id") id: string, @Body() dto: PostToGLDto) {
    const invoice = await this.einvService.postToGL(id, dto.glBatchId);
    return invoice.toState();
  }

  // ─── Pending Transmission ────────────────────────────────────────────────────

  @Get("invoices/pending-transmission")
  @ApiOperation({ summary: "Get invoices pending tax authority transmission" })
  async pendingTransmission() {
    return this.einvService.findPendingTransmission();
  }

  // ─── Master Data ─────────────────────────────────────────────────────────────

  @Get("invoice-types")
  @ApiOperation({ summary: "List invoice types" })
  async getInvoiceTypes() { return this.einvService.getInvoiceTypes(); }

  @Get("templates")
  @ApiOperation({ summary: "List invoice templates" })
  async getTemplates() { return this.einvService.getTemplates(); }

  @Get("series")
  @ApiOperation({ summary: "List invoice series" })
  @ApiQuery({ name: "invoiceTypeId", required: false })
  async getSeries(@Query("invoiceTypeId") invoiceTypeId?: string) {
    return this.einvService.getSeries(invoiceTypeId);
  }

  @Get("providers")
  @ApiOperation({ summary: "List e-invoice providers" })
  async getProviders() { return this.einvService.getProviders(); }

  @Get("reason-codes")
  @ApiOperation({ summary: "List reason codes" })
  @ApiQuery({ name: "category", required: false })
  async getReasonCodes(@Query("category") category?: string) {
    return this.einvService.getReasonCodes(category);
  }

  @Get("certificates")
  @ApiOperation({ summary: "List digital certificates" })
  @ApiQuery({ name: "providerId", required: false })
  async getCertificates(@Query("providerId") providerId?: string) {
    return this.einvService.getCertificates(providerId);
  }

  // ─── Stats ────────────────────────────────────────────────────────────────────

  @Get("stats")
  @ApiOperation({ summary: "E-invoice statistics" })
  async getStats() {
    const all = await this.einvService.listInvoices();
    return {
      total: all.total,
    };
  }
}
