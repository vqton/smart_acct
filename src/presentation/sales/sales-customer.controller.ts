import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesCustomerService } from "../../application/sales/sales-customer-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { CustomerId } from "../../domain/sales/sales-ids.js";
import {
  CreateCustomerDto, UpdateCustomerDto, CustomerSearchDto,
  CustomerActionDto, SetCreditLimitDto,
} from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Customers")
@Controller("api/sales/customers")
export class SalesCustomerController {
  constructor(private readonly svc: SalesCustomerService) {}

  @Post()
  @ApiOperation({ summary: "Create customer" })
  async create(@Body() dto: CreateCustomerDto) {
    try {
      const c = await this.svc.create(dto);
      return c.toState();
    } catch (e) { handleError(e); }
  }

  @Get()
  @ApiOperation({ summary: "List customers" })
  async list(@Query() q?: CustomerSearchDto) {
    if (q && (q.code || q.name || q.taxCode || q.status || q.phone || q.email)) {
      return this.svc.search(q as any);
    }
    return this.svc.list();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get customer by ID" })
  async getById(@Param("id") id: string) {
    const c = await this.svc.getById(id);
    if (!c) throw new NotFoundException("Customer not found");
    return c.toState();
  }

  @Get("code/:code")
  @ApiOperation({ summary: "Get customer by code" })
  async getByCode(@Param("code") code: string) {
    const c = await this.svc.getByCode(code);
    if (!c) throw new NotFoundException("Customer not found");
    return c.toState();
  }

  @Put(":id")
  @ApiOperation({ summary: "Update customer" })
  async update(@Param("id") id: string, @Body() dto: UpdateCustomerDto) {
    try {
      const c = await this.svc.update(id, dto);
      return c.toState();
    } catch (e) { handleError(e); }
  }

  @Post(":id/block")
  @ApiOperation({ summary: "Block customer" })
  async block(@Param("id") id: string, @Body() dto: CustomerActionDto) {
    try { return (await this.svc.block(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/unblock")
  @ApiOperation({ summary: "Unblock customer" })
  async unblock(@Param("id") id: string) {
    try { return (await this.svc.unblock(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/blacklist")
  @ApiOperation({ summary: "Blacklist customer" })
  async blacklist(@Param("id") id: string, @Body() dto: CustomerActionDto) {
    try { return (await this.svc.blacklist(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/remove-blacklist")
  @ApiOperation({ summary: "Remove customer blacklist" })
  async removeBlacklist(@Param("id") id: string) {
    try { return (await this.svc.removeBlacklist(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post(":id/credit-limit")
  @ApiOperation({ summary: "Set customer credit limit" })
  async setCreditLimit(@Param("id") id: string, @Body() dto: SetCreditLimitDto) {
    try { return (await this.svc.setCreditLimit(id, dto.creditLimit, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }
}
