import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class CashBoxId extends Identifier {
  static new(): CashBoxId { return new CashBoxId(IdGenerator.uuid()); }
}
export class CashRegisterId extends Identifier {
  static new(): CashRegisterId { return new CashRegisterId(IdGenerator.uuid()); }
}
export class CashierId extends Identifier {
  static new(): CashierId { return new CashierId(IdGenerator.uuid()); }
}
export class CashSessionId extends Identifier {
  static new(): CashSessionId { return new CashSessionId(IdGenerator.uuid()); }
}
export class CashCountId extends Identifier {
  static new(): CashCountId { return new CashCountId(IdGenerator.uuid()); }
}
export class CashDifferenceId extends Identifier {
  static new(): CashDifferenceId { return new CashDifferenceId(IdGenerator.uuid()); }
}
export class CashLocationId extends Identifier {
  static new(): CashLocationId { return new CashLocationId(IdGenerator.uuid()); }
}
export class PettyCashId extends Identifier {
  static new(): PettyCashId { return new PettyCashId(IdGenerator.uuid()); }
}
export class PettyCashReplenishmentId extends Identifier {
  static new(): PettyCashReplenishmentId { return new PettyCashReplenishmentId(IdGenerator.uuid()); }
}
export class CashAdvanceId extends Identifier {
  static new(): CashAdvanceId { return new CashAdvanceId(IdGenerator.uuid()); }
}
export class AdvanceSettlementId extends Identifier {
  static new(): AdvanceSettlementId { return new AdvanceSettlementId(IdGenerator.uuid()); }
}
export class CashTransferId extends Identifier {
  static new(): CashTransferId { return new CashTransferId(IdGenerator.uuid()); }
}
export class CashReceiptId extends Identifier {
  static new(): CashReceiptId { return new CashReceiptId(IdGenerator.uuid()); }
}
export class CashPaymentId extends Identifier {
  static new(): CashPaymentId { return new CashPaymentId(IdGenerator.uuid()); }
}
export class CompanyId extends Identifier {
  static new(): CompanyId { return new CompanyId(IdGenerator.uuid()); }
}
export class BankId extends Identifier {
  static new(): BankId { return new BankId(IdGenerator.uuid()); }
}
export class BankBranchId extends Identifier {
  static new(): BankBranchId { return new BankBranchId(IdGenerator.uuid()); }
}
export class BankAccountId extends Identifier {
  static new(): BankAccountId { return new BankAccountId(IdGenerator.uuid()); }
}
export class ChequeBookId extends Identifier {
  static new(): ChequeBookId { return new ChequeBookId(IdGenerator.uuid()); }
}
export class ChequeId extends Identifier {
  static new(): ChequeId { return new ChequeId(IdGenerator.uuid()); }
}
export class BankTransferId extends Identifier {
  static new(): BankTransferId { return new BankTransferId(IdGenerator.uuid()); }
}
export class BankStatementId extends Identifier {
  static new(): BankStatementId { return new BankStatementId(IdGenerator.uuid()); }
}
export class BankStatementLineId extends Identifier {
  static new(): BankStatementLineId { return new BankStatementLineId(IdGenerator.uuid()); }
}
export class BankReconciliationId extends Identifier {
  static new(): BankReconciliationId { return new BankReconciliationId(IdGenerator.uuid()); }
}
export class CashForecastId extends Identifier {
  static new(): CashForecastId { return new CashForecastId(IdGenerator.uuid()); }
}
export class LiquidityForecastId extends Identifier {
  static new(): LiquidityForecastId { return new LiquidityForecastId(IdGenerator.uuid()); }
}
export class ApprovalRequestId extends Identifier {
  static new(): ApprovalRequestId { return new ApprovalRequestId(IdGenerator.uuid()); }
}
