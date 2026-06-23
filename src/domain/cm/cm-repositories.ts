import type {
  CashBoxId, CashRegisterId, CashierId, CashSessionId,
  CashReceiptId, CashPaymentId, CashAdvanceId, CashTransferId,
  PettyCashId, BankId, BankAccountId, BankStatementId,
  BankTransferId, ChequeBookId, BankReconciliationId,
  CashForecastId, LiquidityForecastId, CompanyId, CashLocationId, BankBranchId,
} from "./cm-ids.js";
import type { CashBox, CashBoxState } from "./cm-cash-box.js";
import type { CashSession, CashSessionState } from "./cm-session.js";
import type { CashReceipt, CashReceiptState } from "./cm-cash-receipt.js";
import type { CashPayment, CashPaymentState } from "./cm-cash-payment.js";
import type { CashAdvance, CashAdvanceState } from "./cm-cash-advance.js";
import type { CashTransfer, CashTransferState } from "./cm-cash-transfer.js";
import type { PettyCash, PettyCashState } from "./cm-petty-cash.js";
import type { Bank, BankState, BankAccount, BankAccountState } from "./cm-bank.js";
import type { ChequeBook, ChequeBookState } from "./cm-cheque.js";
import type { BankTransfer, BankTransferState } from "./cm-bank-transfer.js";
import type { BankStatement, BankStatementState, BankReconciliation, BankReconciliationState } from "./cm-bank-statement.js";
import type { CashForecast, CashForecastState, LiquidityForecast, LiquidityForecastState } from "./cm-cash-forecast.js";
import type { ReceiptStatus, PaymentStatus, CashTransferStatus, ChequeStatus, BankReconciliationStatus } from "./cm-enums.js";

export interface CompanyRepository {
  save(company: any): Promise<void>;
  findById(id: CompanyId): Promise<any | null>;
  findAll(): Promise<any[]>;
}

export interface CashBoxRepository {
  save(box: CashBox): Promise<void>;
  findById(id: CashBoxId): Promise<CashBox | null>;
  findByCode(code: string): Promise<CashBox | null>;
  findByLocation(locationId: string): Promise<CashBox[]>;
  findAll(): Promise<CashBox[]>;
  findActive(): Promise<CashBox[]>;
}

export interface CashSessionRepository {
  save(session: CashSession): Promise<void>;
  findById(id: CashSessionId): Promise<CashSession | null>;
  findByCashBox(cashBoxId: string): Promise<CashSession[]>;
  findByCashier(cashierId: string): Promise<CashSession[]>;
  findByDateRange(from: Date, to: Date): Promise<CashSession[]>;
  findOpenByCashBox(cashBoxId: string): Promise<CashSession | null>;
  findAll(): Promise<CashSession[]>;
}

export interface CashReceiptRepository {
  save(receipt: CashReceipt): Promise<void>;
  findById(id: CashReceiptId): Promise<CashReceipt | null>;
  findByNumber(receiptNumber: string): Promise<CashReceipt | null>;
  findByCashBox(cashBoxId: string): Promise<CashReceipt[]>;
  findBySession(sessionId: string): Promise<CashReceipt[]>;
  findByCashier(cashierId: string): Promise<CashReceipt[]>;
  findByDateRange(from: Date, to: Date): Promise<CashReceipt[]>;
  findByStatus(status: ReceiptStatus): Promise<CashReceipt[]>;
  findAll(): Promise<CashReceipt[]>;
}

export interface CashPaymentRepository {
  save(payment: CashPayment): Promise<void>;
  findById(id: CashPaymentId): Promise<CashPayment | null>;
  findByNumber(paymentNumber: string): Promise<CashPayment | null>;
  findByCashBox(cashBoxId: string): Promise<CashPayment[]>;
  findBySession(sessionId: string): Promise<CashPayment[]>;
  findByCashier(cashierId: string): Promise<CashPayment[]>;
  findByDateRange(from: Date, to: Date): Promise<CashPayment[]>;
  findByStatus(status: PaymentStatus): Promise<CashPayment[]>;
  findAll(): Promise<CashPayment[]>;
}

export interface CashAdvanceRepository {
  save(advance: CashAdvance): Promise<void>;
  findById(id: CashAdvanceId): Promise<CashAdvance | null>;
  findByNumber(advanceNumber: string): Promise<CashAdvance | null>;
  findByEmployee(employeeId: string): Promise<CashAdvance[]>;
  findByDateRange(from: Date, to: Date): Promise<CashAdvance[]>;
  findOutstanding(): Promise<CashAdvance[]>;
  findAll(): Promise<CashAdvance[]>;
}

export interface CashTransferRepository {
  save(transfer: CashTransfer): Promise<void>;
  findById(id: CashTransferId): Promise<CashTransfer | null>;
  findByNumber(transferNumber: string): Promise<CashTransfer | null>;
  findByFromLocation(locationId: string): Promise<CashTransfer[]>;
  findByToLocation(locationId: string): Promise<CashTransfer[]>;
  findByStatus(status: CashTransferStatus): Promise<CashTransfer[]>;
  findByDateRange(from: Date, to: Date): Promise<CashTransfer[]>;
  findAll(): Promise<CashTransfer[]>;
}

export interface PettyCashRepository {
  save(fund: PettyCash): Promise<void>;
  findById(id: PettyCashId): Promise<PettyCash | null>;
  findByCode(fundCode: string): Promise<PettyCash | null>;
  findByLocation(locationId: string): Promise<PettyCash[]>;
  findAll(): Promise<PettyCash[]>;
}

export interface BankRepository {
  save(bank: Bank): Promise<void>;
  findById(id: BankId): Promise<Bank | null>;
  findByCode(code: string): Promise<Bank | null>;
  findAll(): Promise<Bank[]>;
  findActive(): Promise<Bank[]>;
}

export interface BankAccountRepository {
  save(account: BankAccount): Promise<void>;
  findById(id: BankAccountId): Promise<BankAccount | null>;
  findByAccountNumber(accountNumber: string): Promise<BankAccount | null>;
  findByBank(bankId: string): Promise<BankAccount[]>;
  findByCompany(companyId: string): Promise<BankAccount[]>;
  findActive(): Promise<BankAccount[]>;
  findAll(): Promise<BankAccount[]>;
}

export interface ChequeBookRepository {
  save(book: ChequeBook): Promise<void>;
  findById(id: ChequeBookId): Promise<ChequeBook | null>;
  findByBankAccount(bankAccountId: string): Promise<ChequeBook[]>;
  findByNumber(chequeBookNumber: string): Promise<ChequeBook | null>;
  findAll(): Promise<ChequeBook[]>;
}

export interface BankTransferRepository {
  save(transfer: BankTransfer): Promise<void>;
  findById(id: BankTransferId): Promise<BankTransfer | null>;
  findByNumber(transferNumber: string): Promise<BankTransfer | null>;
  findByFromAccount(accountId: string): Promise<BankTransfer[]>;
  findByToAccount(accountId: string): Promise<BankTransfer[]>;
  findByDateRange(from: Date, to: Date): Promise<BankTransfer[]>;
  findAll(): Promise<BankTransfer[]>;
}

export interface BankStatementRepository {
  save(statement: BankStatement): Promise<void>;
  findById(id: BankStatementId): Promise<BankStatement | null>;
  findByBankAccount(bankAccountId: string): Promise<BankStatement[]>;
  findByNumber(statementNumber: string): Promise<BankStatement | null>;
  findUnreconciled(bankAccountId: string): Promise<BankStatement[]>;
  findAll(): Promise<BankStatement[]>;
}

export interface BankReconciliationRepository {
  save(rec: BankReconciliation): Promise<void>;
  findById(id: BankReconciliationId): Promise<BankReconciliation | null>;
  findByBankAccount(bankAccountId: string): Promise<BankReconciliation[]>;
  findByStatus(status: BankReconciliationStatus): Promise<BankReconciliation[]>;
  findAll(): Promise<BankReconciliation[]>;
}

export interface CashForecastRepository {
  save(forecast: CashForecast): Promise<void>;
  findById(id: CashForecastId): Promise<CashForecast | null>;
  findByCompany(companyId: string): Promise<CashForecast[]>;
  findByDateRange(from: Date, to: Date): Promise<CashForecast[]>;
  findAll(): Promise<CashForecast[]>;
}

export interface LiquidityForecastRepository {
  save(forecast: LiquidityForecast): Promise<void>;
  findById(id: LiquidityForecastId): Promise<LiquidityForecast | null>;
  findByCompany(companyId: string): Promise<LiquidityForecast[]>;
  findAll(): Promise<LiquidityForecast[]>;
}
