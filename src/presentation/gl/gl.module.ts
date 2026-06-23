import { Module } from "@nestjs/common";
import { AccountController } from "./account.controller.js";
import { JournalController } from "./journal.controller.js";
import { PeriodController } from "./period.controller.js";
import {
  PrismaAccountRepository,
  PrismaJournalBatchRepository,
  PrismaFiscalYearRepository,
  PrismaPeriodRepository,
  PrismaVoucherTypeRepository,
  PrismaVoucherSeriesRepository,
  PrismaExchangeRateRepository,
  PrismaCostCenterRepository,
  PrismaDepartmentRepository,
  PrismaBudgetRepository,
  PrismaUnitOfWork,
} from "../../infrastructure/gl/gl-prisma-repos.js";

@Module({
  controllers: [AccountController, JournalController, PeriodController],
  providers: [
    PrismaAccountRepository,
    PrismaJournalBatchRepository,
    PrismaFiscalYearRepository,
    PrismaPeriodRepository,
    PrismaVoucherTypeRepository,
    PrismaVoucherSeriesRepository,
    PrismaExchangeRateRepository,
    PrismaCostCenterRepository,
    PrismaDepartmentRepository,
    PrismaBudgetRepository,
    PrismaUnitOfWork,
  ],
  exports: [
    PrismaAccountRepository,
    PrismaJournalBatchRepository,
    PrismaFiscalYearRepository,
    PrismaPeriodRepository,
  ],
})
export class GlModule {}
