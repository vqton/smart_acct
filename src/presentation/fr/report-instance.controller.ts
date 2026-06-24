import { Controller, Get, Post, Param, Body, NotFoundException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaReportInstanceRepository } from "../../infrastructure/fr/fr-prisma-repos.js";
import { FrReportInstanceId } from "../../domain/fr/fr-ids.js";
import { ReportEngine } from "../../application/fr/report-engine.js";
import { GenerateReportDto } from "./dto/report.dto.js";

@ApiTags("FR Report Instances")
@Controller("api/fr/report-instances")
export class ReportInstanceController {
  constructor(
    private readonly instanceRepo: PrismaReportInstanceRepository,
    private readonly engine: ReportEngine,
  ) {}

  @Post("generate")
  @ApiOperation({ summary: "Generate a report instance" })
  async generate(@Body() dto: GenerateReportDto) {
    return this.engine.generate({
      reportDefId: dto.reportDefId,
      fiscalYearId: dto.fiscalYearId,
      periodId: dto.periodId,
      periodNumber: dto.periodNumber,
      periodName: dto.periodName,
      asOfDate: dto.asOfDate,
      legalEntityId: dto.legalEntityId,
      generatedById: dto.generatedById,
    });
  }

  @Get()
  @ApiOperation({ summary: "List report instances" })
  async findAll() {
    return this.instanceRepo.findAll();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get report instance by ID" })
  async findById(@Param("id") id: string) {
    const inst = await this.instanceRepo.findById(new FrReportInstanceId(id));
    if (!inst) throw new NotFoundException("Report instance not found");
    return inst.toState();
  }

  @Post(":id/approve")
  @ApiOperation({ summary: "Approve report instance" })
  async approve(@Param("id") id: string, @Body("userId") userId: string) {
    const inst = await this.instanceRepo.findById(new FrReportInstanceId(id));
    if (!inst) throw new NotFoundException("Report instance not found");
    inst.approve(userId);
    await this.instanceRepo.save(inst);
    return inst.toState();
  }

  @Get("by-report/:reportDefId")
  @ApiOperation({ summary: "Get instances by report definition" })
  async findByReport(@Param("reportDefId") reportDefId: string) {
    return this.instanceRepo.findByReportDef(reportDefId);
  }

  @Get("by-fiscal-year/:fiscalYearId")
  @ApiOperation({ summary: "Get instances by fiscal year" })
  async findByFiscalYear(@Param("fiscalYearId") fiscalYearId: string) {
    return this.instanceRepo.findByFiscalYear(fiscalYearId);
  }
}
