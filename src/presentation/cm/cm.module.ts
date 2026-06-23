import { Module } from "@nestjs/common";
import { CashOfficeController } from "./cm-cash-office.controller.js";
import { BankController } from "./cm-bank.controller.js";
import { TreasuryController } from "./cm-treasury.controller.js";
import {
  PrismaCashBoxRepository,
  PrismaCashSessionRepository,
  PrismaCashReceiptRepository,
  PrismaCashPaymentRepository,
  PrismaCashAdvanceRepository,
  PrismaCashTransferRepository,
  PrismaPettyCashRepository,
  PrismaBankRepository,
  PrismaBankAccountRepository,
  PrismaBankTransferRepository,
  PrismaBankStatementRepository,
  PrismaBankReconciliationRepository,
  PrismaChequeBookRepository,
  PrismaCashForecastRepository,
  PrismaLiquidityForecastRepository,
} from "../../infrastructure/cm/cm-prisma-repos.js";
import { CashBoxService } from "../../application/cm/cm-cashbox-service.js";
import { BankService } from "../../application/cm/cm-bank-service.js";

@Module({
  controllers: [CashOfficeController, BankController, TreasuryController],
  providers: [
    PrismaCashBoxRepository,
    PrismaCashSessionRepository,
    PrismaCashReceiptRepository,
    PrismaCashPaymentRepository,
    PrismaCashAdvanceRepository,
    PrismaCashTransferRepository,
    PrismaPettyCashRepository,
    PrismaBankRepository,
    PrismaBankAccountRepository,
    PrismaBankTransferRepository,
    PrismaBankStatementRepository,
    PrismaBankReconciliationRepository,
    PrismaChequeBookRepository,
    PrismaCashForecastRepository,
    PrismaLiquidityForecastRepository,
    CashBoxService,
    BankService,
  ],
  exports: [
    PrismaCashBoxRepository,
    PrismaBankAccountRepository,
  ],
})
export class CmModule {}
