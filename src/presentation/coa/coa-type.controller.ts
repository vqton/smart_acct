import { Controller, Get, Post, Param, Body, Query, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { CoaService } from "../../application/coa/coa-service.js";
import { PrismaAccountTypeRepository } from "../../infrastructure/coa/coa-prisma-repos.js";
import { CreateAccountTypeDto } from "./dto/coa.dto.js";
import { AccountTypeId } from "../../domain/coa/coa-ids.js";

@ApiTags("COA Account Types")
@Controller("api/coa/types")
export class CoaAccountTypeController {
  constructor(
    private readonly coaService: CoaService,
    private readonly typeRepo: PrismaAccountTypeRepository,
  ) {}

  @Post()
  @ApiOperation({ summary: "Create account type" })
  async create(@Body() dto: CreateAccountTypeDto) {
    const existing = await this.typeRepo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Type code ${dto.code} already exists`);
    return this.coaService.createType(dto);
  }

  @Get()
  @ApiOperation({ summary: "List account types" })
  @ApiQuery({ name: "classId", required: false })
  async findAll(@Query("classId") classId?: string) {
    if (classId) return this.coaService.getTypesByClass(classId);
    return this.coaService.getAllTypes();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get type by ID" })
  async findById(@Param("id") id: string) {
    const entity = await this.typeRepo.findById(new AccountTypeId(id));
    if (!entity) throw new NotFoundException("Account type not found");
    return entity.toState();
  }
}
