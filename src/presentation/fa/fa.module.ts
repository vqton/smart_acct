import { Module } from "@nestjs/common";
import { FaController } from "./fa.controller.js";
import { FaService } from "../../application/fa/fa-service.js";
import { FaGlService } from "../../application/fa/fa-gl-service.js";
import {
  PrismaFaAssetGroupRepository,
  PrismaFaAssetClassRepository,
  PrismaFaAssetCategoryRepository,
  PrismaFaAssetRepository,
  PrismaFaCipProjectRepository,
  PrismaFaRevaluationRepository,
  PrismaFaImpairmentRepository,
  PrismaFaDisposalRepository,
  PrismaFaTransferRepository,
  PrismaFaDepreciationRunRepository,
  PrismaFaLeaseRepository,
  PrismaFaMaintenanceRecordRepository,
  PrismaFaPhysicalVerificationRepository,
} from "../../infrastructure/fa/fa-prisma-repos.js";
import {
  PrismaJournalBatchRepository,
  PrismaAccountRepository,
  PrismaPeriodRepository,
  PrismaFiscalYearRepository,
} from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaModule } from "../../prisma/prisma.module.js";

@Module({
  imports: [PrismaModule],
  controllers: [FaController],
  providers: [
    FaService,
    FaGlService,
    PrismaFaAssetGroupRepository,
    PrismaFaAssetClassRepository,
    PrismaFaAssetCategoryRepository,
    PrismaFaAssetRepository,
    PrismaFaCipProjectRepository,
    PrismaFaRevaluationRepository,
    PrismaFaImpairmentRepository,
    PrismaFaDisposalRepository,
    PrismaFaTransferRepository,
    PrismaFaDepreciationRunRepository,
    PrismaFaLeaseRepository,
    PrismaFaMaintenanceRecordRepository,
    PrismaFaPhysicalVerificationRepository,
    PrismaJournalBatchRepository,
    PrismaAccountRepository,
    PrismaPeriodRepository,
    PrismaFiscalYearRepository,
  ],
  exports: [
    FaService,
    FaGlService,
    PrismaFaAssetRepository,
    PrismaFaCipProjectRepository,
  ],
})
export class FaModule {}
