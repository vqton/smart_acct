import type {
  BankGroupId, BankId, BankBranchId, CorrespondentBankId, BankAccountId,
  AuthorizedSignerId, AccountLimitId, BankTransactionId, BankStatementId,
  BankStatementLineId, BankReconciliationId, BankReconciliationItemId,
  PaymentRequestId, PaymentBatchId, RecurringPaymentId, StandingInstructionId,
  CashPositionId, CashForecastId, FXRateId, FXRevaluationId,
  ApprovalMatrixId, ApprovalRequestId, AccountMappingId,
  HolidayCalendarId, BusinessCalendarId,
} from "./bank-ids.js";
import type { BankGroup, BankGroupState } from "./bank-master.js";
import type { Bank, BankState } from "./bank-master.js";
import type { BankBranch, BankBranchState } from "./bank-master.js";
import type { CorrespondentBank, CorrespondentBankState } from "./bank-master.js";
import type { BankAccount, BankAccountState, AuthorizedSigner, AuthorizedSignerState, AccountLimit, AccountLimitState, AccountMapping, AccountMappingState } from "./bank-account.js";
import type { BankTransaction, BankTransactionState } from "./bank-transaction.js";
import type { BankStatement, BankStatementState, BankStatementLine, BankStatementLineState } from "./bank-statement.js";
import type { BankReconciliation, BankReconciliationState, BankReconciliationItem, BankReconciliationItemState } from "./bank-reconciliation.js";
import type { PaymentRequest, PaymentRequestState, PaymentBatch, PaymentBatchState, RecurringPayment, RecurringPaymentState, StandingInstructionState } from "./bank-payment.js";
import type { CashPosition, CashPositionState, CashForecast, CashForecastState, FXRate, FXRateState, FXRevaluation, FXRevaluationState } from "./bank-treasury.js";
import type { ApprovalMatrix, ApprovalMatrixState, ApprovalRequest, ApprovalRequestState } from "./bank-workflow.js";
import type { TransactionStatus, BankAccountStatus, ReconciliationStatus, PaymentBatchStatus } from "./bank-enums.js";

export interface BankGroupRepository {
  save(group: BankGroup): Promise<void>;
  findById(id: BankGroupId): Promise<BankGroup | null>;
  findByCode(code: string): Promise<BankGroup | null>;
  findAll(): Promise<BankGroup[]>;
  findActive(): Promise<BankGroup[]>;
}

export interface BankRepository {
  save(bank: Bank): Promise<void>;
  findById(id: BankId): Promise<Bank | null>;
  findByCode(code: string): Promise<Bank | null>;
  findBySwift(swift: string): Promise<Bank | null>;
  findAll(): Promise<Bank[]>;
  findActive(): Promise<Bank[]>;
  findByCountry(countryCode: string): Promise<Bank[]>;
}

export interface BankBranchRepository {
  save(branch: BankBranch): Promise<void>;
  findById(id: BankBranchId): Promise<BankBranch | null>;
  findByCode(code: string): Promise<BankBranch | null>;
  findByBank(bankId: string): Promise<BankBranch[]>;
  findAll(): Promise<BankBranch[]>;
}

export interface CorrespondentBankRepository {
  save(correspondent: CorrespondentBank): Promise<void>;
  findById(id: CorrespondentBankId): Promise<CorrespondentBank | null>;
  findByBank(bankId: string): Promise<CorrespondentBank[]>;
  findByCurrency(currencyCode: string): Promise<CorrespondentBank[]>;
  findAll(): Promise<CorrespondentBank[]>;
}

export interface AuthorizedSignerRepository {
  save(signer: AuthorizedSigner): Promise<void>;
  findById(id: AuthorizedSignerId): Promise<AuthorizedSigner | null>;
  findByAccount(bankAccountId: string): Promise<AuthorizedSigner[]>;
  findByUser(userId: string): Promise<AuthorizedSigner[]>;
}

export interface AccountLimitRepository {
  save(limit: AccountLimit): Promise<void>;
  findById(id: AccountLimitId): Promise<AccountLimit | null>;
  findByAccount(bankAccountId: string): Promise<AccountLimit[]>;
}

export interface AccountMappingRepository {
  save(mapping: AccountMapping): Promise<void>;
  findByAccount(bankAccountId: string): Promise<AccountMapping[]>;
  findByGLAccount(glAccountId: string): Promise<AccountMapping[]>;
  findDefault(bankAccountId: string): Promise<AccountMapping | null>;
}

export interface BankAccountRepository {
  save(account: BankAccount): Promise<void>;
  findById(id: BankAccountId): Promise<BankAccount | null>;
  findByAccountNumber(accountNumber: string): Promise<BankAccount | null>;
  findByBank(bankId: string): Promise<BankAccount[]>;
  findByCompany(companyId: string): Promise<BankAccount[]>;
  findByStatus(status: BankAccountStatus): Promise<BankAccount[]>;
  findByCurrency(currencyCode: string): Promise<BankAccount[]>;
  findActive(): Promise<BankAccount[]>;
  findByGLAccount(glAccountId: string): Promise<BankAccount[]>;
  findAll(): Promise<BankAccount[]>;
}

export interface BankTransactionRepository {
  save(transaction: BankTransaction): Promise<void>;
  findById(id: BankTransactionId): Promise<BankTransaction | null>;
  findByNumber(transactionNumber: string): Promise<BankTransaction | null>;
  findByFromAccount(accountId: string): Promise<BankTransaction[]>;
  findByToAccount(accountId: string): Promise<BankTransaction[]>;
  findByStatus(status: TransactionStatus): Promise<BankTransaction[]>;
  findByDateRange(from: Date, to: Date): Promise<BankTransaction[]>;
  findByReference(reference: string): Promise<BankTransaction | null>;
  findAll(): Promise<BankTransaction[]>;
}

export interface BankStatementRepository {
  save(statement: BankStatement): Promise<void>;
  findById(id: BankStatementId): Promise<BankStatement | null>;
  findByNumber(statementNumber: string): Promise<BankStatement | null>;
  findByBankAccount(bankAccountId: string): Promise<BankStatement[]>;
  findUnreconciled(bankAccountId: string): Promise<BankStatement[]>;
  findReconciled(bankAccountId: string): Promise<BankStatement[]>;
  findByDateRange(from: Date, to: Date): Promise<BankStatement[]>;
  findAll(): Promise<BankStatement[]>;
}

export interface BankStatementLineRepository {
  save(line: BankStatementLine): Promise<void>;
  findById(id: BankStatementLineId): Promise<BankStatementLine | null>;
  findByStatement(statementId: string): Promise<BankStatementLine[]>;
  findUnmatched(statementId: string): Promise<BankStatementLine[]>;
  findByReference(reference: string): Promise<BankStatementLine[]>;
}

export interface BankReconciliationRepository {
  save(reconciliation: BankReconciliation): Promise<void>;
  findById(id: BankReconciliationId): Promise<BankReconciliation | null>;
  findByNumber(reconciliationNumber: string): Promise<BankReconciliation | null>;
  findByBankAccount(bankAccountId: string): Promise<BankReconciliation[]>;
  findByStatement(bankStatementId: string): Promise<BankReconciliation[]>;
  findByStatus(status: ReconciliationStatus): Promise<BankReconciliation[]>;
  findAll(): Promise<BankReconciliation[]>;
}

export interface BankReconciliationItemRepository {
  save(item: BankReconciliationItem): Promise<void>;
  findById(id: BankReconciliationItemId): Promise<BankReconciliationItem | null>;
  findByReconciliation(reconciliationId: string): Promise<BankReconciliationItem[]>;
  findBySource(sourceType: string, sourceId: string): Promise<BankReconciliationItem[]>;
}

export interface PaymentRequestRepository {
  save(request: PaymentRequest): Promise<void>;
  findById(id: PaymentRequestId): Promise<PaymentRequest | null>;
  findByNumber(requestNumber: string): Promise<PaymentRequest | null>;
  findByStatus(status: string): Promise<PaymentRequest[]>;
  findByFromAccount(accountId: string): Promise<PaymentRequest[]>;
  findByCompany(companyId: string): Promise<PaymentRequest[]>;
  findByBatch(batchId: string): Promise<PaymentRequest[]>;
  findAll(): Promise<PaymentRequest[]>;
}

export interface PaymentBatchRepository {
  save(batch: PaymentBatch): Promise<void>;
  findById(id: PaymentBatchId): Promise<PaymentBatch | null>;
  findByNumber(batchNumber: string): Promise<PaymentBatch | null>;
  findByStatus(status: PaymentBatchStatus): Promise<PaymentBatch[]>;
  findByCompany(companyId: string): Promise<PaymentBatch[]>;
  findAll(): Promise<PaymentBatch[]>;
}

export interface RecurringPaymentRepository {
  save(recurring: RecurringPayment): Promise<void>;
  findById(id: RecurringPaymentId): Promise<RecurringPayment | null>;
  findByCompany(companyId: string): Promise<RecurringPayment[]>;
  findDueForExecution(date: Date): Promise<RecurringPayment[]>;
  findAll(): Promise<RecurringPayment[]>;
}

export interface CashPositionRepository {
  save(position: CashPosition): Promise<void>;
  findById(id: CashPositionId): Promise<CashPosition | null>;
  findByCompany(companyId: string): Promise<CashPosition[]>;
  findByDate(companyId: string, date: Date): Promise<CashPosition | null>;
  findByDateRange(companyId: string, from: Date, to: Date): Promise<CashPosition[]>;
}

export interface CashForecastRepository {
  save(forecast: CashForecast): Promise<void>;
  findById(id: CashForecastId): Promise<CashForecast | null>;
  findByCompany(companyId: string): Promise<CashForecast[]>;
  findByDateRange(companyId: string, from: Date, to: Date): Promise<CashForecast[]>;
}

export interface FXRateRepository {
  save(rate: FXRate): Promise<void>;
  findById(id: FXRateId): Promise<FXRate | null>;
  findRate(fromCurrency: string, toCurrency: string, date: Date): Promise<FXRate | null>;
  findByCurrencyPair(fromCurrency: string, toCurrency: string): Promise<FXRate[]>;
  findByType(rateType: string): Promise<FXRate[]>;
}

export interface FXRevaluationRepository {
  save(revaluation: FXRevaluation): Promise<void>;
  findById(id: FXRevaluationId): Promise<FXRevaluation | null>;
  findByCompany(companyId: string): Promise<FXRevaluation[]>;
  findByAccount(accountId: string): Promise<FXRevaluation[]>;
  findByDateRange(companyId: string, from: Date, to: Date): Promise<FXRevaluation[]>;
}

export interface ApprovalMatrixRepository {
  save(matrix: ApprovalMatrix): Promise<void>;
  findById(id: ApprovalMatrixId): Promise<ApprovalMatrix | null>;
  findByEntityType(entityType: string): Promise<ApprovalMatrix[]>;
  findByEntityTypeAndAmount(entityType: string, amount: number): Promise<ApprovalMatrix | null>;
  findActive(): Promise<ApprovalMatrix[]>;
}

export interface ApprovalRequestRepository {
  save(request: ApprovalRequest): Promise<void>;
  findById(id: ApprovalRequestId): Promise<ApprovalRequest | null>;
  findByEntity(entityType: string, entityId: string): Promise<ApprovalRequest[]>;
  findByStatus(status: string): Promise<ApprovalRequest[]>;
  findByRequester(userId: string): Promise<ApprovalRequest[]>;
}

export interface HolidayCalendarRepository {
  findByCompany(companyId: string): Promise<any[]>;
  isHoliday(companyId: string, date: Date): Promise<boolean>;
}

export interface BankUnitOfWork {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  isActive(): boolean;
}
