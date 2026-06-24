import { Controller, Get, Post, Put, Delete, Param, Body, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaReportDefinitionRepository } from "../../infrastructure/fr/fr-prisma-repos.js";
import { FrReportDefinitionId } from "../../domain/fr/fr-ids.js";
import { ReportDefinition } from "../../domain/fr/fr-report-definition.js";
import { CreateReportDefinitionDto, UpdateReportDefinitionDto, AddReportRowDto } from "./dto/report-definition.dto.js";

@ApiTags("FR Report Definitions")
@Controller("api/fr/report-definitions")
export class ReportDefinitionController {
  constructor(private readonly repo: PrismaReportDefinitionRepository) {}

  @Post()
  @ApiOperation({ summary: "Create report definition" })
  async create(@Body() dto: CreateReportDefinitionDto) {
    const existing = await this.repo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Report code ${dto.code} already exists`);

    const def = ReportDefinition.create({
      code: dto.code,
      name: dto.name,
      nameEn: dto.nameEn,
      category: dto.category,
      description: dto.description,
      displayCurrency: dto.displayCurrency,
      isComparative: dto.isComparative,
      createdById: dto.createdById,
    });

    await this.repo.save(def);
    return def.toState();
  }

  @Get()
  @ApiOperation({ summary: "List all report definitions" })
  async findAll() {
    return this.repo.findAll();
  }

  @Get("active")
  @ApiOperation({ summary: "List active report definitions" })
  async findActive() {
    return this.repo.findActive();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get report definition by ID" })
  async findById(@Param("id") id: string) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");
    return def.toState();
  }

  @Put(":id")
  @ApiOperation({ summary: "Update report definition" })
  async update(@Param("id") id: string, @Body() dto: UpdateReportDefinitionDto) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");

    def.modify({ name: dto.name, description: dto.description });
    await this.repo.save(def);
    return def.toState();
  }

  @Post(":id/activate")
  @ApiOperation({ summary: "Activate report definition" })
  async activate(@Param("id") id: string) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");
    def.activate();
    await this.repo.save(def);
    return def.toState();
  }

  @Post(":id/deactivate")
  @ApiOperation({ summary: "Deactivate report definition" })
  async deactivate(@Param("id") id: string) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");
    def.deactivate();
    await this.repo.save(def);
    return def.toState();
  }

  @Post(":id/rows")
  @ApiOperation({ summary: "Add row to report definition" })
  async addRow(@Param("id") id: string, @Body() dto: AddReportRowDto) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");

    def.addRow({
      rowCode: dto.rowCode,
      label: dto.label,
      labelEn: dto.labelEn ?? null,
      rowType: dto.rowType,
      indentLevel: dto.indentLevel ?? 0,
      displayOrder: def.rows.length + 1,
      isBold: dto.isBold ?? false,
      isVisible: true,
      showSubtotal: false,
      pageBreakBefore: false,
      parentRowCode: dto.parentRowCode ?? null,
      cells: [],
    });

    await this.repo.save(def);
    return def.toState();
  }

  @Delete(":id/rows/:rowCode")
  @ApiOperation({ summary: "Remove row from report definition" })
  async removeRow(@Param("id") id: string, @Param("rowCode") rowCode: string) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");
    def.removeRow(rowCode);
    await this.repo.save(def);
    return { success: true };
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete report definition (soft)" })
  async delete(@Param("id") id: string) {
    const def = await this.repo.findById(new FrReportDefinitionId(id));
    if (!def) throw new NotFoundException("Report definition not found");
    def.markDeleted();
    await this.repo.save(def);
    return { success: true };
  }
}
