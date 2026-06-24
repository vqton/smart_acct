import { Controller, Get, Post, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesInvoiceService } from "../../application/sales/sales-invoice-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { InvoiceLine } from "../../domain/sales/sales-invoice.js";
import {
  CreateSalesInvoiceDto, CreateInvoiceLineDto, CreateFromOrderInvoiceDto,
  PostInvoiceDto, CreditNoteDto, EinvoiceUpdateDto, ApproveDto, CancelWithReasonDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Invoices")
@Controller("api/sales/invoices")
export class SalesInvoiceController {
  constructor(private readonly svc: SalesInvoiceService) {}

  @Post()
  @ApiOperation({ summary: "Create invoice" })
  async create(@Body() dto: CreateSalesInvoiceDto) {
    try {
      const inv = await this.svc.create({
        ...dto,
        invoiceDate: dto.invoiceDate ? new Date(dto.invoiceDate) : undefined,
      });
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List invoices" })
  async list(@Query("status") status?: string, @Query("customerId") customerId?: string, @Query("orderId") orderId?: string) {
    if (orderId) return this.svc.findByOrder(orderId);
    if (customerId) return this.svc.findByCustomer(customerId);
    if (status) return this.svc.findByStatus(status);
    return this.svc.findByStatus("draft");
  }

  @Get(":id")
  @ApiOperation({ summary: "Get invoice by ID" })
  async getById(@Param("id") id: string) {
    try {
      const inv = await this.svc.getInvoice(id);
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Get("number/:invoiceNumber")
  @ApiOperation({ summary: "Get invoice by number" })
  async getByNumber(@Param("invoiceNumber") invoiceNumber: string) {
    const inv = await this.svc.findByInvoiceNumber(invoiceNumber);
    if (!inv) throw new NotFoundException("Invoice not found");
    return inv.toState();
  }

  @Post("from-order/:orderId")
  @ApiOperation({ summary: "Create invoice from order" })
  async createFromOrder(@Param("orderId") orderId: string, @Body() dto: CreateFromOrderInvoiceDto) {
    try {
      const inv = await this.svc.createFromOrder(orderId, dto.invoiceNumber, dto.companyId);
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/lines")
  @ApiOperation({ summary: "Add line to invoice" })
  async addLine(@Param("id") id: string, @Body() dto: CreateInvoiceLineDto) {
    try {
      const line = InvoiceLine.create({ invoiceId: id, ...dto });
      const inv = await this.svc.addLine(id, line);
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/approve")
  @ApiOperation({ summary: "Approve invoice" })
  async approve(@Param("id") id: string, @Body() dto: ApproveDto) {
    try { return (await this.svc.approve(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/post")
  @ApiOperation({ summary: "Post invoice (creates receivable)" })
  async post(@Param("id") id: string, @Body() dto: PostInvoiceDto) {
    try { return (await this.svc.post(id, dto.postedById, dto.dueDays)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/cancel")
  @ApiOperation({ summary: "Cancel invoice" })
  async cancel(@Param("id") id: string, @Body() dto: CancelWithReasonDto) {
    try { return (await this.svc.cancel(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/credit-note")
  @ApiOperation({ summary: "Create credit note from invoice" })
  async creditNote(@Param("id") id: string, @Body() dto: CreditNoteDto) {
    try {
      const cn = await this.svc.createCreditNote(id, dto.creditNoteNumber, dto.reason);
      return cn.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/einvoice")
  @ApiOperation({ summary: "Update e-invoice info" })
  async updateEinvoice(@Param("id") id: string, @Body() dto: EinvoiceUpdateDto) {
    try {
      const inv = await this.svc.updateEinvoice(id, dto.einvoiceNumber, dto.einvoiceCode, dto.verifyCode, new Date(dto.issueDate));
      return inv.toState();
    } catch (e) { handleError(e); }
  }
}
