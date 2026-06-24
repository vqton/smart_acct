import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PurchasingVendorService } from "../../application/purchasing/purchasing-vendor-service.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateVendorDto, UpdateVendorDto, VendorActionDto, VendorSearchDto, EvaluateVendorDto,
} from "./dto/purchasing.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Purchasing - Vendor Management")
@Controller("api/purchasing/vendors")
export class PurchasingVendorController {
  constructor(private readonly vendorService: PurchasingVendorService) {}

  @Post()
  @ApiOperation({ summary: "Create vendor" })
  async create(@Body() dto: CreateVendorDto) {
    try { return (await this.vendorService.create(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List vendors" })
  async list(@Query() query?: VendorSearchDto) {
    if (query && (query.code || query.name || query.taxCode || query.status || query.category)) {
      return (await this.vendorService.search(query)).map(v => v.toState());
    }
    return (await this.vendorService.list()).map(v => v.toState());
  }

  @Get(":id")
  @ApiOperation({ summary: "Get vendor by ID" })
  async getById(@Param("id") id: string) {
    const v = await this.vendorService.getById(id);
    if (!v) throw new NotFoundException("Vendor not found");
    return v.toState();
  }

  @Put(":id")
  @ApiOperation({ summary: "Update vendor" })
  async update(@Param("id") id: string, @Body() dto: UpdateVendorDto) {
    try { return (await this.vendorService.update(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put(":id/block")
  @ApiOperation({ summary: "Block vendor" })
  async block(@Param("id") id: string, @Body() dto: VendorActionDto) {
    try { return (await this.vendorService.block(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put(":id/unblock")
  @ApiOperation({ summary: "Unblock vendor" })
  async unblock(@Param("id") id: string) {
    try { return (await this.vendorService.unblock(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put(":id/deactivate")
  @ApiOperation({ summary: "Deactivate vendor" })
  async deactivate(@Param("id") id: string) {
    try { return (await this.vendorService.deactivate(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/qualify")
  @ApiOperation({ summary: "Qualify vendor" })
  async qualify(@Param("id") id: string, @Body() dto: { qualifiedBy: string; expiresAt?: string; notes?: string }) {
    try {
      const q = await this.vendorService.qualify(id, dto.qualifiedBy, dto.expiresAt ? new Date(dto.expiresAt) : undefined, dto.notes);
      return q.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/evaluate")
  @ApiOperation({ summary: "Evaluate vendor" })
  async evaluate(@Param("id") id: string, @Body() dto: EvaluateVendorDto) {
    try { return (await this.vendorService.evaluate(id, dto.evaluator, dto.score as any, dto.criteria, dto.comments)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get(":id/qualifications")
  @ApiOperation({ summary: "Get vendor qualifications" })
  async getQualifications(@Param("id") id: string) {
    return (await this.vendorService.getQualifications(id)).map(q => q.toState());
  }

  @Get(":id/evaluations")
  @ApiOperation({ summary: "Get vendor evaluations" })
  async getEvaluations(@Param("id") id: string) {
    return (await this.vendorService.getEvaluations(id)).map(e => e.toState());
  }
}
