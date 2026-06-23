import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PrismaBankRepository, PrismaBankAccountRepository, PrismaBankTransferRepository, PrismaBankStatementRepository, PrismaBankReconciliationRepository, PrismaChequeBookRepository } from "../../infrastructure/cm/cm-prisma-repos.js";
import { Bank, BankAccount } from "../../domain/cm/cm-bank.js";
import { BankTransfer } from "../../domain/cm/cm-bank-transfer.js";
import { BankStatement, BankReconciliation } from "../../domain/cm/cm-bank-statement.js";
import { ChequeBook } from "../../domain/cm/cm-cheque.js";
import { BankAccountId, BankId, BankTransferId, BankStatementId, BankReconciliationId, ChequeBookId } from "../../domain/cm/cm-ids.js";
import { BankAccountType, BankTransferType, StatementLineType } from "../../domain/cm/cm-enums.js";

@Injectable()
export class BankService {
  constructor(
    private readonly bankRepo: PrismaBankRepository,
    private readonly accountRepo: PrismaBankAccountRepository,
    private readonly transferRepo: PrismaBankTransferRepository,
    private readonly statementRepo: PrismaBankStatementRepository,
    private readonly reconciliationRepo: PrismaBankReconciliationRepository,
    private readonly chequeBookRepo: PrismaChequeBookRepository,
  ) {}

  async createAccount(params: {
    companyId: string;
    bankId: string;
    accountNumber: string;
    accountName: string;
    accountType?: BankAccountType;
    currencyCode?: string;
    openingDate: Date;
    branchId?: string | null;
    glAccountId?: string | null;
    notes?: string | null;
  }): Promise<BankAccount> {
    const account = BankAccount.create(params);
    await this.accountRepo.save(account);
    return account;
  }

  async createTransfer(params: {
    transferNumber: string;
    transferType: BankTransferType;
    fromAccountId: string;
    toAccountId: string;
    amount: number;
    currencyCode?: string;
    transferDate: Date;
    exchangeRate?: number;
    reference?: string | null;
    beneficiaryName?: string | null;
    beneficiaryBank?: string | null;
    beneficiaryAccount?: string | null;
    notes?: string | null;
  }): Promise<BankTransfer> {
    const fromAccount = await this.accountRepo.findById(new BankAccountId(params.fromAccountId));
    if (!fromAccount) throw new DomainError("NotFound", "Source account not found");
    const toAccount = await this.accountRepo.findById(new BankAccountId(params.toAccountId));
    if (!toAccount) throw new DomainError("NotFound", "Destination account not found");

    const transfer = BankTransfer.create(params);

    await this.transferRepo.save(transfer);
    return transfer;
  }

  async completeTransfer(transferId: string, userId: string): Promise<BankTransfer> {
    const transfer = await this.transferRepo.findById(new BankTransferId(transferId));
    if (!transfer) throw new DomainError("NotFound", "Transfer not found");
    transfer.approve(userId);
    transfer.execute(userId);
    transfer.complete();

    const fromAccount = await this.accountRepo.findById(new BankAccountId(transfer.fromAccountId));
    const toAccount = await this.accountRepo.findById(new BankAccountId(transfer.toAccountId));
    if (fromAccount) fromAccount.debit(transfer.amount, transfer.transferNumber);
    if (toAccount) toAccount.credit(transfer.amount, transfer.transferNumber);

    await this.transferRepo.save(transfer);
    if (fromAccount) await this.accountRepo.save(fromAccount);
    if (toAccount) await this.accountRepo.save(toAccount);
    return transfer;
  }

  async importStatement(params: {
    bankAccountId: string;
    statementNumber: string;
    periodStart: Date;
    periodEnd: Date;
    openingBalance: number;
    closingBalance: number;
    lines: Array<{
      lineDate: Date;
      description: string | null;
      reference: string | null;
      chequeNumber: string | null;
      lineType: StatementLineType;
      amount: number;
      runningBalance: number;
    }>;
  }): Promise<BankStatement> {
    const statement = BankStatement.create({
      bankAccountId: params.bankAccountId,
      statementNumber: params.statementNumber,
      periodStart: params.periodStart,
      periodEnd: params.periodEnd,
      openingBalance: params.openingBalance,
      closingBalance: params.closingBalance,
    });
    for (const line of params.lines) {
      statement.addLine(line);
    }
    statement.validateBalance();
    await this.statementRepo.save(statement);
    return statement;
  }

  async createReconciliation(params: {
    bankAccountId: string;
    bankStatementId: string;
    reconciliationNumber: string;
    reconciliationDate: Date;
    statementBalance: number;
    bookBalance: number;
  }): Promise<BankReconciliation> {
    const rec = BankReconciliation.create(params);
    await this.reconciliationRepo.save(rec);
    return rec;
  }

  async approveReconciliation(id: string, userId: string): Promise<BankReconciliation> {
    const rec = await this.reconciliationRepo.findById(new BankReconciliationId(id));
    if (!rec) throw new DomainError("NotFound", "Reconciliation not found");
    rec.resolve(userId);
    rec.approve(userId);

    const statement = await this.statementRepo.findById(new BankStatementId(rec.reconciliationNumber.includes("R") ? "" : ""));
    if (statement) {
      statement.markReconciled();
      await this.statementRepo.save(statement);
    }
    await this.reconciliationRepo.save(rec);
    return rec;
  }
}
