import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { BankTransaction } from "../../domain/bank/bank-transaction.js";
import { BankAccount } from "../../domain/bank/bank-account.js";
import { BankStatement } from "../../domain/bank/bank-statement.js";
import { BankReconciliation } from "../../domain/bank/bank-reconciliation.js";
import { PaymentRequest, PaymentBatch, RecurringPayment } from "../../domain/bank/bank-payment.js";
import { CashPosition, FXRevaluation } from "../../domain/bank/bank-treasury.js";
import { TransactionNature, TransactionMethod, StatementSource, ReconciliationMatchType, PaymentBatchStatus, TransactionStatus } from "../../domain/bank/bank-enums.js";
import { BankTransactionId, BankAccountId, BankStatementId, BankReconciliationId, PaymentRequestId, PaymentBatchId, RecurringPaymentId, CashPositionId, FXRevaluationId } from "../../domain/bank/bank-ids.js";
import { PositiveAmountSpec, DuplicateTransactionSpec, ValidTransactionTransitionSpec, ActiveAccountSpec } from "../../domain/bank/bank-specifications.js";
import {
  PrismaBankTransactionRepository, PrismaBankAccountRepository, PrismaBankStatementRepository,
  PrismaBankStatementLineRepository, PrismaBankReconciliationRepository, PrismaBankReconciliationItemRepository,
  PrismaPaymentRequestRepository, PrismaPaymentBatchRepository, PrismaRecurringPaymentRepository,
  PrismaCashPositionRepository, PrismaFXRevaluationRepository,
} from "../../infrastructure/bank/bank-prisma-repos.js";

@Injectable()
export class BankTransactionService {
  constructor(
    private readonly accountRepo: PrismaBankAccountRepository,
    private readonly txRepo: PrismaBankTransactionRepository,
    private readonly statementRepo: PrismaBankStatementRepository,
    private readonly statementLineRepo: PrismaBankStatementLineRepository,
    private readonly reconciliationRepo: PrismaBankReconciliationRepository,
    private readonly reconciliationItemRepo: PrismaBankReconciliationItemRepository,
    private readonly paymentRequestRepo: PrismaPaymentRequestRepository,
    private readonly paymentBatchRepo: PrismaPaymentBatchRepository,
    private readonly recurringPaymentRepo: PrismaRecurringPaymentRepository,
    private readonly positionRepo: PrismaCashPositionRepository,
    private readonly fxRevaluationRepo: PrismaFXRevaluationRepository,
  ) {}

  // ─── Bank Transactions ───────────────────────────────────────────────────────

  async createTransaction(p: {
    companyId: string; transactionNumber: string; nature: TransactionNature;
    method: TransactionMethod; fromAccountId: string; amount: number;
    currencyCode?: string; transactionDate: Date;
    toAccountId?: string; beneficiaryName?: string; reference?: string;
    description?: string; fees?: number;
  }): Promise<BankTransaction> {
    const existing = await this.txRepo.findByNumber(p.transactionNumber);
    DuplicateTransactionSpec.check(p.transactionNumber, existing);

    const fromAccount = await this.accountRepo.findById(BankAccountId.from(p.fromAccountId));
    if (!fromAccount) throw new DomainError("NotFound", "Source account not found");
    ActiveAccountSpec.check(fromAccount);

    PositiveAmountSpec.check(p.amount);
    const tx = BankTransaction.create(p);

    await this.txRepo.save(tx);
    return tx;
  }

  async getTransaction(id: string): Promise<BankTransaction | null> {
    return this.txRepo.findById(new BankTransactionId(id));
  }

  async listTransactions(accountId?: string): Promise<BankTransaction[]> {
    if (accountId) return this.txRepo.findByFromAccount(accountId);
    return this.txRepo.findAll();
  }

  async authorizeTransaction(id: string, userId: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.authorize(userId);
    await this.txRepo.save(tx);
    return tx;
  }

  async approveTransaction(id: string, userId: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.approve(userId);
    await this.txRepo.save(tx);
    return tx;
  }

  async executeTransaction(id: string, userId: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.execute(userId);

    const fromAccount = await this.accountRepo.findById(BankAccountId.from(tx.fromAccountId));
    if (fromAccount) {
      fromAccount.debit(tx.amount, tx.transactionNumber);
      await this.accountRepo.save(fromAccount);
    }

    await this.txRepo.save(tx);
    return tx;
  }

  async completeTransaction(id: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.complete();

    if (tx.toAccountId) {
      const toAccount = await this.accountRepo.findById(BankAccountId.from(tx.toAccountId));
      if (toAccount) {
        toAccount.credit(tx.amount, tx.transactionNumber);
        await this.accountRepo.save(toAccount);
      }
    }

    await this.txRepo.save(tx);
    return tx;
  }

  async failTransaction(id: string, reason: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.fail(reason);
    await this.txRepo.save(tx);
    return tx;
  }

  async reverseTransaction(id: string, reason: string): Promise<BankTransaction> {
    const tx = await this.txRepo.findById(new BankTransactionId(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.reverse(reason);
    await this.txRepo.save(tx);
    return tx;
  }

  // ─── Bank Statements ─────────────────────────────────────────────────────────

  async importStatement(p: {
    bankAccountId: string; statementNumber: string; periodStart: Date; periodEnd: Date;
    openingBalance: number; closingBalance: number; source?: StatementSource;
    importedBy?: string; lines: Array<{
      lineDate: Date; lineType: string; amount: number; runningBalance: number;
      description?: string; reference?: string;
    }>;
  }): Promise<BankStatement> {
    const statement = BankStatement.create({
      bankAccountId: p.bankAccountId, statementNumber: p.statementNumber,
      periodStart: p.periodStart, periodEnd: p.periodEnd,
      openingBalance: p.openingBalance, closingBalance: p.closingBalance,
      source: p.source, importedBy: p.importedBy,
    });
    for (const line of p.lines) {
      statement.addLine(line);
    }
    statement.validateBalance();
    await this.statementRepo.save(statement);
    return statement;
  }

  async getStatement(id: string): Promise<BankStatement | null> {
    return this.statementRepo.findById(new BankStatementId(id));
  }

  async listStatements(bankAccountId?: string): Promise<BankStatement[]> {
    if (bankAccountId) return this.statementRepo.findByBankAccount(bankAccountId);
    return this.statementRepo.findAll();
  }

  async lockStatement(id: string): Promise<BankStatement> {
    const s = await this.statementRepo.findById(new BankStatementId(id));
    if (!s) throw new DomainError("NotFound", "Statement not found");
    s.lock();
    await this.statementRepo.save(s);
    return s;
  }

  async unlockStatement(id: string): Promise<BankStatement> {
    const s = await this.statementRepo.findById(new BankStatementId(id));
    if (!s) throw new DomainError("NotFound", "Statement not found");
    s.unlock();
    await this.statementRepo.save(s);
    return s;
  }

  // ─── Reconciliation ──────────────────────────────────────────────────────────

  async createReconciliation(p: {
    bankAccountId: string; bankStatementId: string; reconciliationNumber: string;
    reconciliationDate: Date; statementBalance: number; bookBalance: number;
    preparedById?: string;
  }): Promise<BankReconciliation> {
    const rec = BankReconciliation.create(p);
    await this.reconciliationRepo.save(rec);
    return rec;
  }

  async getReconciliation(id: string): Promise<BankReconciliation | null> {
    return this.reconciliationRepo.findById(new BankReconciliationId(id));
  }

  async listReconciliations(bankAccountId?: string): Promise<BankReconciliation[]> {
    if (bankAccountId) return this.reconciliationRepo.findByBankAccount(bankAccountId);
    return this.reconciliationRepo.findAll();
  }

  async matchReconciliationItem(id: string, p: {
    statementLineId?: string; sourceType: string; sourceId: string;
    amount: number; matchType: ReconciliationMatchType;
  }): Promise<BankReconciliation> {
    const rec = await this.reconciliationRepo.findById(new BankReconciliationId(id));
    if (!rec) throw new DomainError("NotFound", "Reconciliation not found");
    rec.addItem(p);
    await this.reconciliationRepo.save(rec);
    return rec;
  }

  async resolveReconciliation(id: string, userId: string): Promise<BankReconciliation> {
    const rec = await this.reconciliationRepo.findById(new BankReconciliationId(id));
    if (!rec) throw new DomainError("NotFound", "Reconciliation not found");
    rec.resolve(userId);
    await this.reconciliationRepo.save(rec);
    return rec;
  }

  async approveReconciliation(id: string, userId: string): Promise<BankReconciliation> {
    const rec = await this.reconciliationRepo.findById(new BankReconciliationId(id));
    if (!rec) throw new DomainError("NotFound", "Reconciliation not found");
    rec.approve(userId);
    rec.close();

    const statement = await this.statementRepo.findById(new BankStatementId(rec.bankStatementId));
    if (statement) {
      statement.markReconciled();
      await this.statementRepo.save(statement);
    }

    await this.reconciliationRepo.save(rec);
    return rec;
  }

  // ─── Payments ────────────────────────────────────────────────────────────────

  async createPaymentRequest(p: {
    companyId: string; requestNumber: string; paymentDate: Date; amount: number;
    fromAccountId: string; beneficiaryName: string; method?: TransactionMethod;
    reference?: string; description?: string; requestedById: string;
  }): Promise<PaymentRequest> {
    const pr = PaymentRequest.create(p);
    await this.paymentRequestRepo.save(pr);
    return pr;
  }

  async approvePaymentRequest(id: string, userId: string): Promise<PaymentRequest> {
    const pr = await this.paymentRequestRepo.findById(new PaymentRequestId(id));
    if (!pr) throw new DomainError("NotFound", "Payment request not found");
    pr.approve(userId);
    await this.paymentRequestRepo.save(pr);
    return pr;
  }

  async rejectPaymentRequest(id: string, userId: string, reason: string): Promise<PaymentRequest> {
    const pr = await this.paymentRequestRepo.findById(new PaymentRequestId(id));
    if (!pr) throw new DomainError("NotFound", "Payment request not found");
    pr.reject(userId, reason);
    await this.paymentRequestRepo.save(pr);
    return pr;
  }

  async createPaymentBatch(p: {
    companyId: string; batchNumber: string; paymentDate: Date; currencyCode?: string;
  }): Promise<PaymentBatch> {
    const pb = PaymentBatch.create(p);
    await this.paymentBatchRepo.save(pb);
    return pb;
  }

  async releasePaymentBatch(id: string, userId: string): Promise<PaymentBatch> {
    const pb = await this.paymentBatchRepo.findById(new PaymentBatchId(id));
    if (!pb) throw new DomainError("NotFound", "Payment batch not found");
    pb.validate();
    pb.approve(userId);
    pb.release(userId);
    await this.paymentBatchRepo.save(pb);
    return pb;
  }

  // ─── Recurring Payments ──────────────────────────────────────────────────────

  async createRecurringPayment(p: {
    companyId: string; name: string; fromAccountId: string; beneficiaryName: string;
    amount: number; frequency: string; startDate: Date; method?: TransactionMethod;
  }): Promise<RecurringPayment> {
    const rp = RecurringPayment.create(p as any);
    await this.recurringPaymentRepo.save(rp);
    return rp;
  }

  async processDueRecurringPayments(): Promise<string[]> {
    const due = await this.recurringPaymentRepo.findDueForExecution(new Date());
    const processed: string[] = [];
    for (const rp of due) {
      rp.recordExecution();
      await this.recurringPaymentRepo.save(rp);
      processed.push(rp.id.value);
    }
    return processed;
  }

  // ─── Cash Positions ──────────────────────────────────────────────────────────

  async createCashPosition(p: {
    companyId: string; positionDate: Date; currencyCode?: string; openingBalance?: number;
  }): Promise<CashPosition> {
    const cp = CashPosition.create(p);
    await this.positionRepo.save(cp);
    return cp;
  }

  // ─── FX Revaluation ──────────────────────────────────────────────────────────

  async createFXRevaluation(p: {
    companyId: string; revaluationDate: Date; currencyCode: string;
    exchangeRate: number; previousRate: number; accountId: string;
    accountBalance: number; isRealized?: boolean;
  }): Promise<FXRevaluation> {
    const fx = FXRevaluation.create(p);
    await this.fxRevaluationRepo.save(fx);
    return fx;
  }

  async postFXRevaluationToGL(id: string, glBatchId: string): Promise<FXRevaluation> {
    const fx = await this.fxRevaluationRepo.findById(new FXRevaluationId(id));
    if (!fx) throw new DomainError("NotFound", "FX revaluation not found");
    fx.markGLPosted(glBatchId);
    await this.fxRevaluationRepo.save(fx);
    return fx;
  }
}
