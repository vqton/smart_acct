import { Controller, Get, Post, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesPaymentService } from "../../application/sales/sales-payment-service.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateReceiptDto, ApproveReceiptDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Payments")
@Controller("api/sales/payments")
export class SalesPaymentController {
  constructor(private readonly svc: SalesPaymentService) {}

  @Post("receipts")
  @ApiOperation({ summary: "Create customer receipt" })
  async createReceipt(@Body() dto: CreateReceiptDto) {
    try {
      const r = await this.svc.createReceipt({
        ...dto,
        paymentDate: dto.paymentDate ? new Date(dto.paymentDate) : undefined,
      });
      return r.toState();
    } catch (e) { handleError(e); }
  }

  @Get("receipts")
  @ApiOperation({ summary: "List receipts" })
  async listReceipts(@Query("customerId") customerId?: string, @Query("invoiceId") invoiceId?: string, @Query("from") from?: string, @Query("to") to?: string) {
    if (customerId) return this.svc.findByCustomer(customerId);
    if (invoiceId) return this.svc.findByInvoice(invoiceId);
    if (from && to) return this.svc.findByDateRange(new Date(from), new Date(to));
    return this.svc.findByCustomer("");
  }

  @Get("receipts/:id")
  @ApiOperation({ summary: "Get receipt by ID" })
  async getReceipt(@Param("id") id: string) {
    try {
      const r = await this.svc.getReceipt(id);
      return r.toState();
    } catch (e) { handleError(e); }
  }

  @Post("receipts/:id/approve")
  @ApiOperation({ summary: "Approve and optionally allocate receipt" })
  async approveReceipt(@Param("id") id: string, @Body() dto: ApproveReceiptDto) {
    try {
      const r = await this.svc.approveAndAllocate(id, dto.approvedBy, dto.allocateToInvoiceId);
      return r.toState();
    } catch (e) { handleError(e); }
  }
}
