import { Module } from "@nestjs/common";
import { BankMasterController } from "./bank-master.controller.js";
import { BankMasterService } from "../../application/bank/bank-master-service.js";
import { BankAccountService } from "../../application/bank/bank-account-service.js";
import { BankTransactionService } from "../../application/bank/bank-transaction-service.js";
import {
  PrismaBankGroupRepository, PrismaBankRepository, PrismaBankBranchRepository,
  PrismaCorrespondentBankRepository, PrismaBankAccountRepository,
  PrismaAuthorizedSignerRepository, PrismaAccountLimitRepository,
  PrismaAccountMappingRepository, PrismaBankTransactionRepository,
  PrismaBankStatementRepository, PrismaBankStatementLineRepository,
  PrismaBankReconciliationRepository, PrismaBankReconciliationItemRepository,
  PrismaPaymentRequestRepository, PrismaPaymentBatchRepository,
  PrismaRecurringPaymentRepository, PrismaCashPositionRepository,
  PrismaCashForecastRepository, PrismaFXRateRepository,
  PrismaFXRevaluationRepository, PrismaApprovalMatrixRepository,
  PrismaApprovalRequestRepository,
} from "../../infrastructure/bank/bank-prisma-repos.js";

@Module({
  controllers: [BankMasterController],
  providers: [
    BankMasterService, BankAccountService, BankTransactionService,
    PrismaBankGroupRepository, PrismaBankRepository, PrismaBankBranchRepository,
    PrismaCorrespondentBankRepository, PrismaBankAccountRepository,
    PrismaAuthorizedSignerRepository, PrismaAccountLimitRepository,
    PrismaAccountMappingRepository, PrismaBankTransactionRepository,
    PrismaBankStatementRepository, PrismaBankStatementLineRepository,
    PrismaBankReconciliationRepository, PrismaBankReconciliationItemRepository,
    PrismaPaymentRequestRepository, PrismaPaymentBatchRepository,
    PrismaRecurringPaymentRepository, PrismaCashPositionRepository,
    PrismaCashForecastRepository, PrismaFXRateRepository,
    PrismaFXRevaluationRepository, PrismaApprovalMatrixRepository,
    PrismaApprovalRequestRepository,
  ],
})
export class BankModule {}
