import { Controller, Get, Post, Put, Delete, Param, Body, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaFormulaRepository } from "../../infrastructure/fr/fr-prisma-repos.js";
import { FrFormulaId } from "../../domain/fr/fr-ids.js";
import { Formula } from "../../domain/fr/fr-formula.js";
import { CreateFormulaDto, UpdateFormulaDto } from "./dto/formula.dto.js";

@ApiTags("FR Formulas")
@Controller("api/fr/formulas")
export class FormulaController {
  constructor(private readonly repo: PrismaFormulaRepository) {}

  @Post()
  @ApiOperation({ summary: "Create formula" })
  async create(@Body() dto: CreateFormulaDto) {
    const existing = await this.repo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Formula code ${dto.code} already exists`);

    const formula = Formula.create({
      code: dto.code,
      name: dto.name,
      formulaType: dto.formulaType,
      expression: dto.expression,
      description: dto.description,
      createdById: dto.createdById,
    });

    await this.repo.save(formula);
    return formula.toState();
  }

  @Get()
  @ApiOperation({ summary: "List all formulas" })
  async findAll() {
    return this.repo.findAll();
  }

  @Get("active")
  @ApiOperation({ summary: "List active formulas" })
  async findActive() {
    return this.repo.findActive();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get formula by ID" })
  async findById(@Param("id") id: string) {
    const formula = await this.repo.findById(new FrFormulaId(id));
    if (!formula) throw new NotFoundException("Formula not found");
    return formula.toState();
  }

  @Put(":id")
  @ApiOperation({ summary: "Update formula" })
  async update(@Param("id") id: string, @Body() dto: UpdateFormulaDto) {
    const formula = await this.repo.findById(new FrFormulaId(id));
    if (!formula) throw new NotFoundException("Formula not found");

    if (dto.expression) formula.updateExpression(dto.expression);
    await this.repo.save(formula);
    return formula.toState();
  }

  @Post(":id/deactivate")
  @ApiOperation({ summary: "Deactivate formula" })
  async deactivate(@Param("id") id: string) {
    const formula = await this.repo.findById(new FrFormulaId(id));
    if (!formula) throw new NotFoundException("Formula not found");
    formula.deactivate();
    await this.repo.save(formula);
    return formula.toState();
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete formula (soft)" })
  async delete(@Param("id") id: string) {
    const formula = await this.repo.findById(new FrFormulaId(id));
    if (!formula) throw new NotFoundException("Formula not found");
    formula.markDeleted();
    await this.repo.save(formula);
    return { success: true };
  }
}
