import { Controller, Get, Post, Param, Body, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { CoaService } from "../../application/coa/coa-service.js";
import { PrismaAccountClassRepository } from "../../infrastructure/coa/coa-prisma-repos.js";
import { AccountClassId } from "../../domain/coa/coa-ids.js";
import { CreateAccountClassDto } from "./dto/coa.dto.js";

@ApiTags("COA Account Classes")
@Controller("api/coa/classes")
export class CoaAccountClassController {
  constructor(
    private readonly coaService: CoaService,
    private readonly classRepo: PrismaAccountClassRepository,
  ) {}

  @Post()
  @ApiOperation({ summary: "Create account class (1-9 classification)" })
  async create(@Body() dto: CreateAccountClassDto) {
    const existing = await this.classRepo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Class code ${dto.code} already exists`);
    return this.coaService.createClass(dto);
  }

  @Get()
  @ApiOperation({ summary: "List all account classes" })
  async findAll() {
    return this.coaService.getAllClasses();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get class by ID" })
  async findById(@Param("id") id: string) {
    const entity = await this.classRepo.findById(new AccountClassId(id));
    if (!entity) throw new NotFoundException("Account class not found");
    return entity.toState();
  }
}
