import { Controller, Get, Post, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesReturnService } from "../../application/sales/sales-return-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { ReturnLine } from "../../domain/sales/sales-return.js";
import {
  CreateSalesReturnDto, CreateReturnLineDto, CreateFromOrderReturnDto,
  InspectReturnDto, ApproveReturnDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Returns")
@Controller("api/sales/returns")
export class SalesReturnController {
  constructor(private readonly svc: SalesReturnService) {}

  @Post()
  @ApiOperation({ summary: "Create return" })
  async create(@Body() dto: CreateSalesReturnDto) {
    try {
      const ret = await this.svc.create(dto);
      return ret.toState();
    } catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List returns" })
  async list(@Query("status") status?: string, @Query("customerId") customerId?: string) {
    if (customerId) return this.svc.findByCustomer(customerId);
    if (status) return this.svc.findByStatus(status);
    return this.svc.findByStatus("draft");
  }

  @Get(":id")
  @ApiOperation({ summary: "Get return by ID" })
  async getById(@Param("id") id: string) {
    try {
      const ret = await this.svc.getReturn(id);
      return ret.toState();
    } catch (e) { handleError(e); }
  }

  @Get("number/:returnNumber")
  @ApiOperation({ summary: "Get return by number" })
  async getByNumber(@Param("returnNumber") returnNumber: string) {
    const ret = await this.svc.findByReturnNumber(returnNumber);
    if (!ret) throw new NotFoundException("Return not found");
    return ret.toState();
  }

  @Post("from-order/:orderId")
  @ApiOperation({ summary: "Create return from order" })
  async createFromOrder(@Param("orderId") orderId: string, @Body() dto: CreateFromOrderReturnDto) {
    try {
      const ret = await this.svc.createFromOrder(orderId, dto.returnNumber, dto.companyId, dto.returnReason, dto.reasonDetail);
      return ret.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/lines")
  @ApiOperation({ summary: "Add line to return" })
  async addLine(@Param("id") id: string, @Body() dto: CreateReturnLineDto) {
    try {
      const line = ReturnLine.create({ returnId: id, ...dto });
      const ret = await this.svc.addLine(id, line);
      return ret.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/submit")
  @ApiOperation({ summary: "Submit return for approval" })
  async submit(@Param("id") id: string) {
    try { return (await this.svc.submit(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/approve")
  @ApiOperation({ summary: "Approve return" })
  async approve(@Param("id") id: string, @Body() dto: ApproveReturnDto) {
    try { return (await this.svc.approve(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/receive")
  @ApiOperation({ summary: "Record return receipt" })
  async receive(@Param("id") id: string) {
    try { return (await this.svc.recordReceipt(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/inspect")
  @ApiOperation({ summary: "Record return inspection" })
  async inspect(@Param("id") id: string, @Body() dto: InspectReturnDto) {
    try { return (await this.svc.recordInspection(id, dto.result, dto.notes)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/complete")
  @ApiOperation({ summary: "Complete return" })
  async complete(@Param("id") id: string) {
    try { return (await this.svc.complete(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/cancel")
  @ApiOperation({ summary: "Cancel return" })
  async cancel(@Param("id") id: string) {
    try { return (await this.svc.cancel(id)).toState(); }
    catch (e) { handleError(e); }
  }
}
