import { Controller, Get, Post, Put, Param, Body, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaFiscalYearRepository, PrismaPeriodRepository, PrismaJournalBatchRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { FiscalYear, FiscalYearId, Period, PeriodId } from "../../domain/gl/period.js";
import { CreateFiscalYearDto, CreatePeriodDto } from "./dto/period.dto.js";

@ApiTags("GL Periods & Fiscal Years")
@Controller("api/gl")
export class PeriodController {
  constructor(
    private readonly fiscalYearRepo: PrismaFiscalYearRepository,
    private readonly periodRepo: PrismaPeriodRepository,
    private readonly batchRepo: PrismaJournalBatchRepository,
  ) {}

  // --- Fiscal Years ---

  @Post("fiscal-years")
  @ApiOperation({ summary: "Create a fiscal year" })
  async createFiscalYear(@Body() dto: CreateFiscalYearDto) {
    const existing = await this.fiscalYearRepo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Fiscal year ${dto.code} already exists`);

    const fy = new FiscalYear(
      FiscalYearId.new(),
      dto.code,
      dto.name,
      new Date(dto.startDate),
      new Date(dto.endDate),
    );

    await this.fiscalYearRepo.save(fy);
    return fy.toState();
  }

  @Get("fiscal-years")
  @ApiOperation({ summary: "List fiscal years" })
  async listFiscalYears() {
    return this.fiscalYearRepo.findAll();
  }

  @Get("fiscal-years/active")
  @ApiOperation({ summary: "Get active fiscal year" })
  async getActiveFiscalYear() {
    const fy = await this.fiscalYearRepo.findActive();
    if (!fy) throw new NotFoundException("No active fiscal year found");
    return fy.toState();
  }

  @Get("fiscal-years/:id")
  @ApiOperation({ summary: "Get fiscal year by ID" })
  async getFiscalYear(@Param("id") id: string) {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(id));
    if (!fy) throw new NotFoundException("Fiscal year not found");
    return fy.toState();
  }

  @Put("fiscal-years/:id/close")
  @ApiOperation({ summary: "Close a fiscal year" })
  async closeFiscalYear(@Param("id") id: string, @Body("userId") userId: string) {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(id));
    if (!fy) throw new NotFoundException("Fiscal year not found");

    const periods = await this.periodRepo.findByFiscalYear(fy.id.value);
    const openPeriods = periods.filter(p => !["closed", "locked"].includes(p.status as string));
    if (openPeriods.length > 0) {
      throw new ConflictException("All periods must be closed before closing fiscal year");
    }

    fy.close(userId);
    await this.fiscalYearRepo.save(fy);
    return fy.toState();
  }

  // --- Periods ---

  @Post("periods")
  @ApiOperation({ summary: "Create a period within a fiscal year" })
  async createPeriod(@Body() dto: CreatePeriodDto) {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(dto.fiscalYearId));
    if (!fy) throw new NotFoundException("Fiscal year not found");

    const period = new Period(
      PeriodId.new(),
      dto.fiscalYearId,
      dto.periodNumber,
      dto.name,
      new Date(dto.startDate),
      new Date(dto.endDate),
    );

    await this.periodRepo.save(period);
    return period.toState();
  }

  @Get("periods")
  @ApiOperation({ summary: "List periods" })
  async listPeriods(@Param("fiscalYearId") fiscalYearId?: string) {
    if (fiscalYearId) return this.periodRepo.findByFiscalYear(fiscalYearId);
    return this.periodRepo.findOpen();
  }

  @Get("periods/open")
  @ApiOperation({ summary: "Get open periods" })
  async getOpenPeriods() {
    return this.periodRepo.findOpen();
  }

  @Get("periods/:id")
  @ApiOperation({ summary: "Get period by ID" })
  async getPeriod(@Param("id") id: string) {
    const period = await this.periodRepo.findById(new PeriodId(id));
    if (!period) throw new NotFoundException("Period not found");
    return period.toState();
  }

  @Put("periods/:id/close")
  @ApiOperation({ summary: "Close a period" })
  async closePeriod(@Param("id") id: string, @Body("userId") userId: string) {
    const period = await this.periodRepo.findById(new PeriodId(id));
    if (!period) throw new NotFoundException("Period not found");

    const batches = await this.batchRepo.findByPeriod(period.id.value);
    const unposted = batches.filter(b => !["posted", "cancelled", "reversed"].includes(b.status as string));
    if (unposted.length > 0) {
      throw new ConflictException("All batches must be posted before closing period");
    }

    period.close(userId);
    await this.periodRepo.save(period);
    return period.toState();
  }
}
