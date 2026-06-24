import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PrismaBgtForecastRepository, PrismaBgtScenarioRepository } from "../../infrastructure/budget/budget-prisma-repos.js";
import { BgtForecastHeader, BgtForecastLine, BgtForecastDriver } from "../../domain/budget/bgt-forecast.js";
import { BgtBudgetScenario, type BgtBudgetScenarioState } from "../../domain/budget/bgt-budget-scenario.js";
import { BgtForecastStatus, BgtForecastMethod } from "../../domain/budget/bgt-enums.js";

export interface CreateForecastInput {
  budgetPlanId: string; forecastNumber: string; forecastMethod?: string;
  scenarioId?: string; description?: string; forecastPeriods?: number;
  periodType?: string; startDate?: Date; endDate?: Date;
  totalForecastAmount?: number; confidencePct?: number;
  notes?: string; createdById?: string;
}

export interface CreateScenarioInput {
  budgetPlanId: string; code: string; name: string; scenarioType?: string;
  description?: string; assumptions?: string; isBase?: boolean;
  confidencePct?: number; weightPct?: number; createdById?: string;
}

@Injectable()
export class ForecastEngineService {
  constructor(
    private readonly forecastRepo: PrismaBgtForecastRepository,
    private readonly scenarioRepo: PrismaBgtScenarioRepository,
  ) {}

  // ─── Scenarios ─────────────────────────────────────────────────────────────

  async createScenario(p: CreateScenarioInput): Promise<BgtBudgetScenario> {
    const scenario = BgtBudgetScenario.create(p);
    await this.scenarioRepo.save(scenario);
    return scenario;
  }

  async getScenario(id: string): Promise<BgtBudgetScenario | null> {
    return this.scenarioRepo.findById(id);
  }

  async getScenarios(budgetPlanId: string): Promise<BgtBudgetScenario[]> {
    return this.scenarioRepo.findByBudgetPlan(budgetPlanId);
  }

  async setBaseScenario(budgetPlanId: string, scenarioId: string): Promise<void> {
    const scenarios = await this.scenarioRepo.findByBudgetPlan(budgetPlanId);
    for (const s of scenarios) {
      const isBase = s.id.value === scenarioId;
      if (isBase) {
        await this.scenarioRepo.save(s);
      }
    }
  }

  // ─── Forecasts ─────────────────────────────────────────────────────────────

  async createForecast(p: CreateForecastInput): Promise<BgtForecastHeader> {
    const existing = await this.forecastRepo.findByNumber(p.forecastNumber);
    if (existing) throw new DomainError("Conflict", `Forecast ${p.forecastNumber} already exists`);
    const forecast = BgtForecastHeader.create(p);
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  async getForecast(id: string): Promise<BgtForecastHeader | null> {
    return this.forecastRepo.findById(id);
  }

  async listForecasts(budgetPlanId?: string, status?: string): Promise<BgtForecastHeader[]> {
    if (status) return this.forecastRepo.findByStatus(status);
    if (budgetPlanId) return this.forecastRepo.findByBudgetPlan(budgetPlanId);
    return this.forecastRepo.findByStatus(BgtForecastStatus.Draft);
  }

  async submitForecast(id: string): Promise<BgtForecastHeader> {
    const forecast = await this.forecastRepo.findById(id);
    if (!forecast) throw new DomainError("NotFound", "Forecast not found");
    forecast.submit();
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  async approveForecast(id: string, userId: string): Promise<BgtForecastHeader> {
    const forecast = await this.forecastRepo.findById(id);
    if (!forecast) throw new DomainError("NotFound", "Forecast not found");
    forecast.approve(userId);
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  async publishForecast(id: string): Promise<BgtForecastHeader> {
    const forecast = await this.forecastRepo.findById(id);
    if (!forecast) throw new DomainError("NotFound", "Forecast not found");
    forecast.publish();
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  async addForecastLine(forecastId: string, p: {
    lineNumber: number; glAccountId?: string; costCenterId?: string;
    departmentId?: string; projectId?: string; productId?: string;
    description?: string; forecastAmount?: number;
  }): Promise<BgtForecastHeader> {
    const forecast = await this.forecastRepo.findById(forecastId);
    if (!forecast) throw new DomainError("NotFound", "Forecast not found");
    const line = BgtForecastLine.create({ forecastHeaderId: forecastId, ...p });
    forecast.addLine(line);
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  async addForecastDriver(forecastId: string, p: {
    driverName: string; driverType: string; baseValue?: number;
    growthRate?: number; seasonalFactor?: number; periodValues?: number[];
  }): Promise<BgtForecastHeader> {
    const forecast = await this.forecastRepo.findById(forecastId);
    if (!forecast) throw new DomainError("NotFound", "Forecast not found");
    const driver = BgtForecastDriver.create({ forecastHeaderId: forecastId, ...p });
    forecast.addDriver(driver);
    await this.forecastRepo.save(forecast);
    return forecast;
  }

  // ─── Rolling Forecast ──────────────────────────────────────────────────────

  async generateRollingForecast(sourceForecastId: string, newForecastNumber: string, additionalPeriods: number, createdById?: string): Promise<BgtForecastHeader> {
    const source = await this.forecastRepo.findById(sourceForecastId);
    if (!source) throw new DomainError("NotFound", "Source forecast not found");
    const forecast = BgtForecastHeader.create({
      budgetPlanId: source.budgetPlanId, forecastNumber: newForecastNumber,
      forecastMethod: BgtForecastMethod.Rolling, forecastPeriods: source.forecastPeriods + additionalPeriods,
      periodType: source.periodType, createdById,
      description: `Rolling forecast from ${source.forecastNumber}`,
    });
    await this.forecastRepo.save(forecast);
    return forecast;
  }
}
