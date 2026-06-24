import { Module } from "@nestjs/common";
import { CostingController } from "./costing.controller.js";
import { CostingEngineService } from "../../application/costing/costing-engine-service.js";
import { AllocationEngineService } from "../../application/costing/allocation-engine-service.js";
import { PeriodCloseService } from "../../application/costing/period-close-service.js";
import {
  PrismaCostVersionRepository,
  PrismaWorkCenterRepository,
  PrismaBomRepository,
  PrismaProductionOrderRepository,
  PrismaCostPoolRepository,
  PrismaAllocationRuleRepository,
  PrismaOverheadRateRepository,
  PrismaCostSnapshotRepository,
  PrismaProductionVarianceRepository,
  PrismaAllocationEntryRepository,
} from "../../infrastructure/costing/costing-prisma-repos.js";
import { PrismaItemRepository } from "../../infrastructure/inventory/inventory-prisma-repos.js";
import { PrismaModule } from "../../prisma/prisma.module.js";

@Module({
  imports: [PrismaModule],
  controllers: [CostingController],
  providers: [
    CostingEngineService,
    AllocationEngineService,
    PeriodCloseService,
    PrismaCostVersionRepository,
    PrismaWorkCenterRepository,
    PrismaBomRepository,
    PrismaProductionOrderRepository,
    PrismaCostPoolRepository,
    PrismaAllocationRuleRepository,
    PrismaOverheadRateRepository,
    PrismaCostSnapshotRepository,
    PrismaProductionVarianceRepository,
    PrismaAllocationEntryRepository,
    PrismaItemRepository,
  ],
  exports: [
    CostingEngineService,
    AllocationEngineService,
    PrismaCostVersionRepository,
    PrismaBomRepository,
    PrismaProductionOrderRepository,
  ],
})
export class CstModule {}
