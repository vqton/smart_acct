import { Controller, Get, Post, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesDeliveryService } from "../../application/sales/sales-delivery-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { DeliveryLine } from "../../domain/sales/sales-delivery.js";
import {
  CreateDeliveryDto, CreateFromOrderDeliveryDto, CreateDeliveryLineDto,
  MarkDeliveredDto, DeliveryExceptionDto, DeliveryCancelDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Deliveries")
@Controller("api/sales/deliveries")
export class SalesDeliveryController {
  constructor(private readonly svc: SalesDeliveryService) {}

  @Post()
  @ApiOperation({ summary: "Create delivery" })
  async create(@Body() dto: CreateDeliveryDto) {
    try {
      const d = await this.svc.create({
        ...dto,
        deliveryDate: dto.deliveryDate ? new Date(dto.deliveryDate) : undefined,
      });
      return d.toState();
    } catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List deliveries" })
  async list(@Query("status") status?: string, @Query("orderId") orderId?: string) {
    if (orderId) return this.svc.findByOrder(orderId);
    if (status) return this.svc.findByStatus(status);
    return this.svc.findByStatus("draft");
  }

  @Get(":id")
  @ApiOperation({ summary: "Get delivery by ID" })
  async getById(@Param("id") id: string) {
    try {
      const d = await this.svc.getDelivery(id);
      return d.toState();
    } catch (e) { handleError(e); }
  }

  @Get("number/:deliveryNumber")
  @ApiOperation({ summary: "Get delivery by number" })
  async getByNumber(@Param("deliveryNumber") deliveryNumber: string) {
    const d = await this.svc.findByDeliveryNumber(deliveryNumber);
    if (!d) throw new NotFoundException("Delivery not found");
    return d.toState();
  }

  @Post("from-order/:orderId")
  @ApiOperation({ summary: "Create delivery from order" })
  async createFromOrder(@Param("orderId") orderId: string, @Body() dto: CreateFromOrderDeliveryDto) {
    try {
      const d = await this.svc.createFromOrder(orderId, dto.deliveryNumber, dto.companyId);
      return d.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/lines")
  @ApiOperation({ summary: "Add line to delivery" })
  async addLine(@Param("id") id: string, @Body() dto: CreateDeliveryLineDto) {
    try {
      const line = DeliveryLine.create({
        deliveryId: id, ...dto,
        expiryDate: dto.expiryDate ? new Date(dto.expiryDate) : undefined,
      });
      const d = await this.svc.addLine(id, line);
      return d.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/ship")
  @ApiOperation({ summary: "Mark delivery as shipped" })
  async ship(@Param("id") id: string) {
    try { return (await this.svc.ship(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/deliver")
  @ApiOperation({ summary: "Mark delivery as delivered" })
  async deliver(@Param("id") id: string, @Body() dto: MarkDeliveredDto) {
    try { return (await this.svc.markDelivered(id, dto.podReceivedBy, dto.podNotes)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/confirm")
  @ApiOperation({ summary: "Confirm delivery" })
  async confirm(@Param("id") id: string) {
    try { return (await this.svc.confirm(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/exception")
  @ApiOperation({ summary: "Report delivery exception" })
  async exception(@Param("id") id: string, @Body() dto: DeliveryExceptionDto) {
    try { return (await this.svc.reportException(id, dto.exceptionType, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/cancel")
  @ApiOperation({ summary: "Cancel delivery" })
  async cancel(@Param("id") id: string, @Body() dto: DeliveryCancelDto) {
    try { return (await this.svc.cancel(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }
}
