import { Module } from "@nestjs/common";
import { BudgetController } from "./budget.controller.js";
import { BudgetEngineService } from "../../application/budget/budget-engine-service.js";
import { ForecastEngineService } from "../../application/budget/forecast-engine-service.js";
import { AllocationEngineService } from "../../application/budget/allocation-engine-service.js";
import { ControlEngineService } from "../../application/budget/control-engine-service.js";
import { ApprovalEngineService } from "../../application/budget/approval-engine-service.js";
import {
  PrismaBgtBudgetPlanRepository,
  PrismaBgtBudgetVersionRepository,
  PrismaBgtBudgetDetailRepository,
  PrismaBgtScenarioRepository,
  PrismaBgtForecastRepository,
  PrismaBgtAllocationRuleRepository,
  PrismaBgtAllocationResultRepository,
  PrismaBgtBudgetControlRepository,
  PrismaBgtReservationRepository,
  PrismaBgtTransferRepository,
  PrismaBgtApprovalRepository,
  PrismaBgtSnapshotRepository,
} from "../../infrastructure/budget/budget-prisma-repos.js";
import { PrismaModule } from "../../prisma/prisma.module.js";

@Module({
  imports: [PrismaModule],
  controllers: [BudgetController],
  providers: [
    BudgetEngineService,
    ForecastEngineService,
    AllocationEngineService,
    ControlEngineService,
    ApprovalEngineService,
    PrismaBgtBudgetPlanRepository,
    PrismaBgtBudgetVersionRepository,
    PrismaBgtBudgetDetailRepository,
    PrismaBgtScenarioRepository,
    PrismaBgtForecastRepository,
    PrismaBgtAllocationRuleRepository,
    PrismaBgtAllocationResultRepository,
    PrismaBgtBudgetControlRepository,
    PrismaBgtReservationRepository,
    PrismaBgtTransferRepository,
    PrismaBgtApprovalRepository,
    PrismaBgtSnapshotRepository,
  ],
  exports: [
    BudgetEngineService,
    ForecastEngineService,
    AllocationEngineService,
    ControlEngineService,
    ApprovalEngineService,
    PrismaBgtBudgetPlanRepository,
    PrismaBgtBudgetVersionRepository,
    PrismaBgtBudgetDetailRepository,
    PrismaBgtScenarioRepository,
    PrismaBgtForecastRepository,
    PrismaBgtAllocationRuleRepository,
    PrismaBgtAllocationResultRepository,
    PrismaBgtBudgetControlRepository,
    PrismaBgtReservationRepository,
    PrismaBgtTransferRepository,
    PrismaBgtApprovalRepository,
    PrismaBgtSnapshotRepository,
  ],
})
export class BudgetModule {}
