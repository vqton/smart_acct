import { Module } from "@nestjs/common";
import {
  PrismaReportDefinitionRepository,
  PrismaReportInstanceRepository,
  PrismaFormulaRepository,
  PrismaConsolidationGroupRepository,
  PrismaConsolidationRunRepository,
} from "../../infrastructure/fr/fr-prisma-repos.js";
import { FormulaEngine } from "../../application/fr/formula-engine.js";
import { ReportEngine } from "../../application/fr/report-engine.js";
import { FinancialStatementService } from "../../application/fr/financial-statement-service.js";
import { ConsolidationEngine } from "../../application/fr/consolidation-engine.js";
import { AnalyticsService } from "../../application/fr/analytics-service.js";
import { GlBalanceProvider } from "../../application/fr/gl-balance-provider.js";
import { GlConsolidationBalanceProvider } from "../../application/fr/gl-consolidation-balance-provider.js";
import { ReportDefinitionController } from "./report-definition.controller.js";
import { ReportInstanceController } from "./report-instance.controller.js";
import { FormulaController } from "./formula.controller.js";
import { ConsolidationController } from "./consolidation.controller.js";
import { AnalyticsController } from "./analytics.controller.js";

@Module({
  controllers: [
    ReportDefinitionController,
    ReportInstanceController,
    FormulaController,
    ConsolidationController,
    AnalyticsController,
  ],
  providers: [
    // Repositories
    PrismaReportDefinitionRepository,
    PrismaReportInstanceRepository,
    PrismaFormulaRepository,
    PrismaConsolidationGroupRepository,
    PrismaConsolidationRunRepository,
    // Engines
    FormulaEngine,
    ReportEngine,
    FinancialStatementService,
    ConsolidationEngine,
    AnalyticsService,
    // Balance Providers
    GlBalanceProvider,
    GlConsolidationBalanceProvider,
  ],
  exports: [
    PrismaReportDefinitionRepository,
    PrismaReportInstanceRepository,
    PrismaFormulaRepository,
    PrismaConsolidationGroupRepository,
    PrismaConsolidationRunRepository,
    FormulaEngine,
    ReportEngine,
    FinancialStatementService,
    ConsolidationEngine,
    AnalyticsService,
  ],
})
export class FrModule {}
