import { Controller, Get, Post, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { ReceivableService } from "../../application/sales/sales-receivable-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { WriteOffDto, DunningDto } from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Receivables")
@Controller("api/sales/receivables")
export class SalesReceivableController {
  constructor(private readonly svc: ReceivableService) {}

  @Get()
  @ApiOperation({ summary: "List receivables" })
  async list(@Query("customerId") customerId?: string, @Query("overdue") overdue?: string, @Query("agingBucket") agingBucket?: string) {
    if (customerId) return this.svc.findByCustomer(customerId);
    if (overdue === "true") return this.svc.findOverdue();
    if (agingBucket) return this.svc.findByAgingBucket(agingBucket);
    return this.svc.findOverdue();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get receivable by ID" })
  async getById(@Param("id") id: string) {
    const accounts = await this.svc["recvRepo"].findByInvoiceId(id);
    if (accounts.length === 0) throw new NotFoundException("Receivable not found");
    return accounts[0];
  }

  @Post(":id/write-off")
  @ApiOperation({ summary: "Write off receivable" })
  async writeOff(@Param("id") id: string, @Body() dto: WriteOffDto) {
    try { return (await this.svc.writeOff(id, dto.amount, dto.reason, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/dispute")
  @ApiOperation({ summary: "Mark receivable as disputed" })
  async dispute(@Param("id") id: string) {
    try { return (await this.svc.markDisputed(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/dunning")
  @ApiOperation({ summary: "Record dunning level" })
  async dunning(@Param("id") id: string, @Body() dto: DunningDto) {
    try { return (await this.svc.recordDunning(id, dto.level)).toState(); }
    catch (e) { handleError(e); }
  }
}
