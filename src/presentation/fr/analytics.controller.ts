import { Controller, Get, Query } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { AnalyticsService } from "../../application/fr/analytics-service.js";
import { FinancialStatementService } from "../../application/fr/financial-statement-service.js";

@ApiTags("FR Analytics")
@Controller("api/fr/analytics")
export class AnalyticsController {
  constructor(
    private readonly analytics: AnalyticsService,
    private readonly financialStatements: FinancialStatementService,
  ) {}

  @Get("ratios")
  @ApiOperation({ summary: "Calculate financial ratios" })
  @ApiQuery({ name: "fiscalYearId", required: true })
  @ApiQuery({ name: "periodNumber", required: false })
  async getRatios(
    @Query("fiscalYearId") fiscalYearId: string,
    @Query("periodNumber") periodNumber?: string,
  ) {
    return this.analytics.calculateRatios(
      fiscalYearId,
      periodNumber ? parseInt(periodNumber, 10) : undefined,
    );
  }

  @Get("trial-balance")
  @ApiOperation({ summary: "Get trial balance" })
  @ApiQuery({ name: "fiscalYearId", required: true })
  @ApiQuery({ name: "periodNumber", required: false })
  async getTrialBalance(
    @Query("fiscalYearId") fiscalYearId: string,
    @Query("periodNumber") periodNumber?: string,
  ) {
    return this.financialStatements.getTrialBalance(
      fiscalYearId,
      periodNumber ? parseInt(periodNumber, 10) : undefined,
    );
  }

  @Get("balance-sheet")
  @ApiOperation({ summary: "Get balance sheet" })
  @ApiQuery({ name: "fiscalYearId", required: true })
  @ApiQuery({ name: "periodNumber", required: false })
  async getBalanceSheet(
    @Query("fiscalYearId") fiscalYearId: string,
    @Query("periodNumber") periodNumber?: string,
  ) {
    return this.financialStatements.getBalanceSheet(
      fiscalYearId,
      periodNumber ? parseInt(periodNumber, 10) : undefined,
    );
  }

  @Get("income-statement")
  @ApiOperation({ summary: "Get income statement" })
  @ApiQuery({ name: "fiscalYearId", required: true })
  @ApiQuery({ name: "periodNumber", required: false })
  async getIncomeStatement(
    @Query("fiscalYearId") fiscalYearId: string,
    @Query("periodNumber") periodNumber?: string,
  ) {
    return this.financialStatements.getIncomeStatement(
      fiscalYearId,
      periodNumber ? parseInt(periodNumber, 10) : undefined,
    );
  }
}
