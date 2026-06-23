import { Controller, Get, Post, Delete, Param, Body, Query, NotFoundException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { CoaService } from "../../application/coa/coa-service.js";
import { PrismaAccountMappingRepository } from "../../infrastructure/coa/coa-prisma-repos.js";
import { AccountMappingId } from "../../domain/coa/coa-ids.js";
import { AccountMappingStandard } from "../../domain/coa/coa-enums.js";
import { CreateAccountMappingDto } from "./dto/coa.dto.js";

@ApiTags("COA Account Mappings")
@Controller("api/coa/mappings")
export class CoaAccountMappingController {
  constructor(
    private readonly coaService: CoaService,
    private readonly mappingRepo: PrismaAccountMappingRepository,
  ) {}

  @Post()
  @ApiOperation({ summary: "Create account mapping (IFRS/VAS/Cash Flow)" })
  async create(@Body() dto: CreateAccountMappingDto) {
    return this.coaService.createMapping({
      ...dto,
      effectiveFrom: new Date(dto.effectiveFrom),
      effectiveTo: dto.effectiveTo ? new Date(dto.effectiveTo) : undefined,
    });
  }

  @Get()
  @ApiOperation({ summary: "List account mappings" })
  @ApiQuery({ name: "accountId", required: false })
  @ApiQuery({ name: "standard", required: false, enum: AccountMappingStandard })
  async findAll(
    @Query("accountId") accountId?: string,
    @Query("standard") standard?: AccountMappingStandard,
  ) {
    if (accountId) return this.coaService.getMappingsByAccount(accountId);
    if (standard) return this.coaService.getMappingsByStandard(standard);
    return this.mappingRepo.findAll().then(entities => entities.map(e => e.toState()));
  }

  @Get(":id")
  @ApiOperation({ summary: "Get mapping by ID" })
  async findById(@Param("id") id: string) {
    const entity = await this.mappingRepo.findById(new AccountMappingId(id));
    if (!entity) throw new NotFoundException("Mapping not found");
    return entity.toState();
  }

  @Delete(":id")
  @ApiOperation({ summary: "Deactivate mapping" })
  async delete(@Param("id") id: string) {
    await this.coaService.deleteMapping(id);
    return { success: true };
  }
}
