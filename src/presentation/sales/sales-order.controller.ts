import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesOrderService } from "../../application/sales/sales-order-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { OrderLine } from "../../domain/sales/sales-order.js";
import {
  CreateSalesOrderDto, CreateOrderLineDto, AddOrderLinesDto,
  ConvertQuotationDto, ApproveOrderDto, CancelOrderDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Orders")
@Controller("api/sales/orders")
export class SalesOrderController {
  constructor(private readonly svc: SalesOrderService) {}

  @Post()
  @ApiOperation({ summary: "Create sales order" })
  async create(@Body() dto: CreateSalesOrderDto) {
    try {
      const order = await this.svc.create(dto);
      return order.toState();
    } catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List orders" })
  async list(@Query("status") status?: string, @Query("customerId") customerId?: string) {
    if (customerId) return this.svc.findByCustomer(customerId);
    if (status) return this.svc.findByStatus(status);
    return this.svc.findOpen();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get order by ID" })
  async getById(@Param("id") id: string) {
    try {
      const order = await this.svc.getOrder(id);
      return order.toState();
    } catch (e) { handleError(e); }
  }

  @Get("number/:orderNumber")
  @ApiOperation({ summary: "Get order by number" })
  async getByNumber(@Param("orderNumber") orderNumber: string) {
    const order = await this.svc.getByOrderNumber(orderNumber);
    if (!order) throw new NotFoundException("Order not found");
    return order.toState();
  }

  @Post("from-quotation/:quotationId")
  @ApiOperation({ summary: "Create order from quotation" })
  async fromQuotation(@Param("quotationId") quotationId: string, @Body() dto: ConvertQuotationDto) {
    try {
      const order = await this.svc.fromQuotation(quotationId, dto.orderNumber, dto.companyId, dto.orderDate ? new Date(dto.orderDate) : undefined);
      return order.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/lines")
  @ApiOperation({ summary: "Add line to order" })
  async addLine(@Param("id") id: string, @Body() dto: CreateOrderLineDto) {
    try {
      const line = OrderLine.create({
        orderId: id, ...dto,
        expectedDate: dto.expectedDate ? new Date(dto.expectedDate) : undefined,
        promisedDate: dto.promisedDate ? new Date(dto.promisedDate) : undefined,
      });
      const order = await this.svc.addLine(id, line);
      return order.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/submit")
  @ApiOperation({ summary: "Submit order for approval" })
  async submit(@Param("id") id: string) {
    try { return (await this.svc.submit(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/approve")
  @ApiOperation({ summary: "Approve order" })
  async approve(@Param("id") id: string, @Body() dto: ApproveOrderDto) {
    try { return (await this.svc.approve(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/confirm")
  @ApiOperation({ summary: "Confirm order" })
  async confirm(@Param("id") id: string, @Body() dto: { confirmedBy: string }) {
    try { return (await this.svc.confirm(id, dto.confirmedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/cancel")
  @ApiOperation({ summary: "Cancel order" })
  async cancel(@Param("id") id: string, @Body() dto: CancelOrderDto) {
    try { return (await this.svc.cancel(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/hold")
  @ApiOperation({ summary: "Hold order" })
  async hold(@Param("id") id: string, @Body() dto: CancelOrderDto) {
    try { return (await this.svc.hold(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/release")
  @ApiOperation({ summary: "Release order from hold" })
  async release(@Param("id") id: string) {
    try { return (await this.svc.releaseHold(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/process")
  @ApiOperation({ summary: "Start processing order" })
  async process(@Param("id") id: string) {
    try { return (await this.svc.startProcessing(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/complete")
  @ApiOperation({ summary: "Complete order" })
  async complete(@Param("id") id: string) {
    try { return (await this.svc.complete(id)).toState(); }
    catch (e) { handleError(e); }
  }
}
