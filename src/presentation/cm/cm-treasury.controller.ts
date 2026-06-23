import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaCashForecastRepository, PrismaLiquidityForecastRepository } from "../../infrastructure/cm/cm-prisma-repos.js";
import { CashForecast, LiquidityForecast } from "../../domain/cm/cm-cash-forecast.js";
import { CashForecastId, LiquidityForecastId } from "../../domain/cm/cm-ids.js";
import { DomainError } from "../../shared/domain-error.js";
import { CreateCashForecastDto, AddForecastLineDto } from "./dto/cm.dto.js";

@ApiTags("CM - Treasury")
@Controller("api/cm/treasury")
export class TreasuryController {
  constructor(
    private readonly forecastRepo: PrismaCashForecastRepository,
    private readonly liquidityRepo: PrismaLiquidityForecastRepository,
  ) {}

  // ─── Cash Forecast ──────────────────────────────────────────────────────────

  @Post("forecasts")
  @ApiOperation({ summary: "Create cash forecast" })
  async createForecast(@Body() dto: CreateCashForecastDto) {
    const forecast = CashForecast.create({
      companyId: dto.companyId,
      forecastNumber: dto.forecastNumber,
      forecastName: dto.forecastName,
      periodType: dto.periodType,
      periodStart: new Date(dto.periodStart),
      periodEnd: new Date(dto.periodEnd),
      currencyCode: dto.currencyCode,
      openingBalance: dto.openingBalance,
    });
    await this.forecastRepo.save(forecast);
    return forecast.toState();
  }

  @Get("forecasts")
  @ApiOperation({ summary: "List cash forecasts" })
  async listForecasts() {
    return (await this.forecastRepo.findAll()).map(f => f.toState());
  }

  @Get("forecasts/:id")
  @ApiOperation({ summary: "Get forecast by ID" })
  async getForecast(@Param("id") id: string) {
    const f = await this.forecastRepo.findById(new CashForecastId(id));
    if (!f) throw new NotFoundException("Forecast not found");
    return f.toState();
  }

  @Post("forecasts/:id/lines")
  @ApiOperation({ summary: "Add line to cash forecast" })
  async addForecastLine(@Param("id") id: string, @Body() dto: AddForecastLineDto) {
    const f = await this.forecastRepo.findById(new CashForecastId(id));
    if (!f) throw new NotFoundException("Forecast not found");
    f.addLine({
      lineDate: new Date(dto.lineDate),
      description: dto.description,
      inflowAmount: dto.inflowAmount ?? 0,
      outflowAmount: dto.outflowAmount ?? 0,
      category: dto.category ?? null,
    });
    await this.forecastRepo.save(f);
    return f.toState();
  }

  @Put("forecasts/:id/confirm")
  @ApiOperation({ summary: "Confirm forecast" })
  async confirmForecast(@Param("id") id: string) {
    const f = await this.forecastRepo.findById(new CashForecastId(id));
    if (!f) throw new NotFoundException("Forecast not found");
    try {
      f.confirm();
      await this.forecastRepo.save(f);
      return f.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }
}
