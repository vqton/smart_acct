import { Controller, Get, Post, Put, Param, Body, NotFoundException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { CoaService } from "../../application/coa/coa-service.js";
import { PrismaAccountExtensionRepository } from "../../infrastructure/coa/coa-prisma-repos.js";
import { UpdateAccountExtensionDto } from "./dto/coa.dto.js";

@ApiTags("COA Account Extensions")
@Controller("api/coa/extensions")
export class CoaAccountExtensionController {
  constructor(
    private readonly coaService: CoaService,
    private readonly extRepo: PrismaAccountExtensionRepository,
  ) {}

  @Post(":accountId")
  @ApiOperation({ summary: "Get or create extension for account" })
  async getOrCreate(@Param("accountId") accountId: string) {
    const ext = await this.coaService.getOrCreateExtension(accountId);
    return ext.toState();
  }

  @Get(":accountId")
  @ApiOperation({ summary: "Get extension by account ID" })
  async findByAccountId(@Param("accountId") accountId: string) {
    const ext = await this.coaService.getExtension(accountId);
    if (!ext) throw new NotFoundException("Extension not found for account");
    return ext;
  }

  @Put(":accountId")
  @ApiOperation({ summary: "Update account extension" })
  async update(@Param("accountId") accountId: string, @Body() dto: UpdateAccountExtensionDto) {
    const processed: any = { ...dto };
    if (dto.effectiveFrom) processed.effectiveFrom = new Date(dto.effectiveFrom);
    if (dto.effectiveTo) processed.effectiveTo = new Date(dto.effectiveTo);
    return this.coaService.updateExtension(accountId, processed);
  }

  @Get("type/:typeId")
  @ApiOperation({ summary: "Find extensions by type" })
  async findByType(@Param("typeId") typeId: string) {
    const entities = await this.extRepo.findByType(typeId);
    return entities.map(e => e.toState());
  }

  @Get("sub-ledger/cash")
  @ApiOperation({ summary: "Get all cash accounts" })
  async findCashAccounts() {
    const entities = await this.extRepo.findCashAccounts();
    return entities.map(e => e.toState());
  }

  @Get("sub-ledger/bank")
  @ApiOperation({ summary: "Get all bank accounts" })
  async findBankAccounts() {
    const entities = await this.extRepo.findBankAccounts();
    return entities.map(e => e.toState());
  }

  @Get("sub-ledger/tax")
  @ApiOperation({ summary: "Get all tax accounts" })
  async findTaxAccounts() {
    const entities = await this.extRepo.findTaxAccounts();
    return entities.map(e => e.toState());
  }
}
