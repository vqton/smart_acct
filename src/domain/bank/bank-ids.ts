import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class BankGroupId extends Identifier { static new(): BankGroupId { return new BankGroupId(IdGenerator.uuid()); } }
export class BankId extends Identifier { static new(): BankId { return new BankId(IdGenerator.uuid()); } }
export class BankBranchId extends Identifier { static new(): BankBranchId { return new BankBranchId(IdGenerator.uuid()); } }
export class CorrespondentBankId extends Identifier { static new(): CorrespondentBankId { return new CorrespondentBankId(IdGenerator.uuid()); } }
export class BankAccountId extends Identifier { static new(): BankAccountId { return new BankAccountId(IdGenerator.uuid()); }
  static from(id: string): BankAccountId { return new BankAccountId(id); } }
export class AuthorizedSignerId extends Identifier { static new(): AuthorizedSignerId { return new AuthorizedSignerId(IdGenerator.uuid()); } }
export class SignatureMatrixId extends Identifier { static new(): SignatureMatrixId { return new SignatureMatrixId(IdGenerator.uuid()); } }
export class AccountLimitId extends Identifier { static new(): AccountLimitId { return new AccountLimitId(IdGenerator.uuid()); } }
export class BankTransactionId extends Identifier { static new(): BankTransactionId { return new BankTransactionId(IdGenerator.uuid()); } }
export class BankStatementId extends Identifier { static new(): BankStatementId { return new BankStatementId(IdGenerator.uuid()); } }
export class BankStatementLineId extends Identifier { static new(): BankStatementLineId { return new BankStatementLineId(IdGenerator.uuid()); } }
export class BankReconciliationId extends Identifier { static new(): BankReconciliationId { return new BankReconciliationId(IdGenerator.uuid()); } }
export class BankReconciliationItemId extends Identifier { static new(): BankReconciliationItemId { return new BankReconciliationItemId(IdGenerator.uuid()); } }
export class PaymentRequestId extends Identifier { static new(): PaymentRequestId { return new PaymentRequestId(IdGenerator.uuid()); } }
export class PaymentBatchId extends Identifier { static new(): PaymentBatchId { return new PaymentBatchId(IdGenerator.uuid()); } }
export class PaymentScheduleId extends Identifier { static new(): PaymentScheduleId { return new PaymentScheduleId(IdGenerator.uuid()); } }
export class RecurringPaymentId extends Identifier { static new(): RecurringPaymentId { return new RecurringPaymentId(IdGenerator.uuid()); } }
export class StandingInstructionId extends Identifier { static new(): StandingInstructionId { return new StandingInstructionId(IdGenerator.uuid()); } }
export class CashPositionId extends Identifier { static new(): CashPositionId { return new CashPositionId(IdGenerator.uuid()); } }
export class CashForecastId extends Identifier { static new(): CashForecastId { return new CashForecastId(IdGenerator.uuid()); } }
export class FXRateId extends Identifier { static new(): FXRateId { return new FXRateId(IdGenerator.uuid()); } }
export class FXRevaluationId extends Identifier { static new(): FXRevaluationId { return new FXRevaluationId(IdGenerator.uuid()); } }
export class ApprovalMatrixId extends Identifier { static new(): ApprovalMatrixId { return new ApprovalMatrixId(IdGenerator.uuid()); } }
export class ApprovalRequestId extends Identifier { static new(): ApprovalRequestId { return new ApprovalRequestId(IdGenerator.uuid()); } }
export class ApprovalStepId extends Identifier { static new(): ApprovalStepId { return new ApprovalStepId(IdGenerator.uuid()); } }
export class ChargeId extends Identifier { static new(): ChargeId { return new ChargeId(IdGenerator.uuid()); } }
export class InterestCalculationId extends Identifier { static new(): InterestCalculationId { return new InterestCalculationId(IdGenerator.uuid()); } }
export class AccountMappingId extends Identifier { static new(): AccountMappingId { return new AccountMappingId(IdGenerator.uuid()); } }
export class HolidayCalendarId extends Identifier { static new(): HolidayCalendarId { return new HolidayCalendarId(IdGenerator.uuid()); } }
export class BusinessCalendarId extends Identifier { static new(): BusinessCalendarId { return new BusinessCalendarId(IdGenerator.uuid()); } }
