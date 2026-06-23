import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  BankGroupId, BankId, BankBranchId, CorrespondentBankId, BankAccountId,
  AuthorizedSignerId, AccountLimitId, BankTransactionId, BankStatementId,
  BankStatementLineId, BankReconciliationId, BankReconciliationItemId,
  PaymentRequestId, PaymentBatchId, RecurringPaymentId, CashPositionId,
  CashForecastId, FXRateId, FXRevaluationId, ApprovalMatrixId, ApprovalRequestId,
  AccountMappingId,
} from "../../domain/bank/bank-ids.js";
import { BankGroup, type BankGroupState } from "../../domain/bank/bank-master.js";
import { Bank, type BankState } from "../../domain/bank/bank-master.js";
import { BankBranch, type BankBranchState } from "../../domain/bank/bank-master.js";
import { CorrespondentBank, type CorrespondentBankState } from "../../domain/bank/bank-master.js";
import { BankAccount, type BankAccountState, AuthorizedSigner, type AuthorizedSignerState, AccountLimit, type AccountLimitState, AccountMapping, type AccountMappingState } from "../../domain/bank/bank-account.js";
import { BankTransaction, type BankTransactionState } from "../../domain/bank/bank-transaction.js";
import { BankStatement, type BankStatementState, BankStatementLine, type BankStatementLineState } from "../../domain/bank/bank-statement.js";
import { BankReconciliation, type BankReconciliationState, BankReconciliationItem, type BankReconciliationItemState } from "../../domain/bank/bank-reconciliation.js";
import { PaymentRequest, type PaymentRequestState, PaymentBatch, type PaymentBatchState, RecurringPayment, type RecurringPaymentState } from "../../domain/bank/bank-payment.js";
import { CashPosition, type CashPositionState, CashForecast, type CashForecastState, FXRate, type FXRateState, FXRevaluation, type FXRevaluationState } from "../../domain/bank/bank-treasury.js";
import { ApprovalMatrix, type ApprovalMatrixState, ApprovalRequest, type ApprovalRequestState } from "../../domain/bank/bank-workflow.js";
import type {
  BankGroupRepository, BankRepository, BankBranchRepository, CorrespondentBankRepository,
  BankAccountRepository, AuthorizedSignerRepository, AccountLimitRepository, AccountMappingRepository,
  BankTransactionRepository, BankStatementRepository, BankStatementLineRepository,
  BankReconciliationRepository, BankReconciliationItemRepository,
  PaymentRequestRepository, PaymentBatchRepository, RecurringPaymentRepository,
  CashPositionRepository, CashForecastRepository, FXRateRepository, FXRevaluationRepository,
  ApprovalMatrixRepository, ApprovalRequestRepository,
} from "../../domain/bank/bank-repositories.js";
import type { TransactionStatus, BankAccountStatus, ReconciliationStatus, PaymentBatchStatus } from "../../domain/bank/bank-enums.js";

function toNumber(val: bigint | number | string | null | undefined, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  return val;
}

function toBigInt(val: number): bigint {
  return BigInt(Math.round(val));
}

// ─── Bank Group Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBankGroupRepository implements BankGroupRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(group: BankGroup): Promise<void> {
    const s = group.toState();
    await this.prisma.bnkGroup.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: BankGroupId): Promise<BankGroup | null> {
    const row = await this.prisma.bnkGroup.findUnique({ where: { id: id.value } });
    return row ? BankGroup.load(row as any) : null;
  }

  async findByCode(code: string): Promise<BankGroup | null> {
    const row = await this.prisma.bnkGroup.findUnique({ where: { code } });
    return row ? BankGroup.load(row as any) : null;
  }

  async findAll(): Promise<BankGroup[]> {
    return (await this.prisma.bnkGroup.findMany()).map(r => BankGroup.load(r as any));
  }

  async findActive(): Promise<BankGroup[]> {
    return (await this.prisma.bnkGroup.findMany({ where: { isActive: true } })).map(r => BankGroup.load(r as any));
  }
}

// ─── Bank Repository ────────────────────────────────────────────────────────────

@Injectable()
export class PrismaBankRepository implements BankRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(bank: Bank): Promise<void> {
    const s = bank.toState();
    await this.prisma.bnkBank.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: BankId): Promise<Bank | null> {
    const row = await this.prisma.bnkBank.findUnique({ where: { id: id.value } });
    return row ? Bank.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Bank | null> {
    const row = await this.prisma.bnkBank.findUnique({ where: { code } });
    return row ? Bank.load(row as any) : null;
  }

  async findBySwift(swift: string): Promise<Bank | null> {
    const row = await this.prisma.bnkBank.findFirst({ where: { swiftCode: swift } });
    return row ? Bank.load(row as any) : null;
  }

  async findAll(): Promise<Bank[]> {
    return (await this.prisma.bnkBank.findMany({ orderBy: { code: "asc" } })).map(r => Bank.load(r as any));
  }

  async findActive(): Promise<Bank[]> {
    return (await this.prisma.bnkBank.findMany({ where: { isActive: true }, orderBy: { code: "asc" } })).map(r => Bank.load(r as any));
  }

  async findByCountry(countryCode: string): Promise<Bank[]> {
    return (await this.prisma.bnkBank.findMany({ where: { countryCode } })).map(r => Bank.load(r as any));
  }
}

// ─── Bank Branch Repository ─────────────────────────────────────────────────────

@Injectable()
export class PrismaBankBranchRepository implements BankBranchRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(branch: BankBranch): Promise<void> {
    const s = branch.toState();
    await this.prisma.bnkBranch.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: BankBranchId): Promise<BankBranch | null> {
    const row = await this.prisma.bnkBranch.findUnique({ where: { id: id.value } });
    return row ? BankBranch.load(row as any) : null;
  }

  async findByCode(code: string): Promise<BankBranch | null> {
    const row = await this.prisma.bnkBranch.findUnique({ where: { code } });
    return row ? BankBranch.load(row as any) : null;
  }

  async findByBank(bankId: string): Promise<BankBranch[]> {
    return (await this.prisma.bnkBranch.findMany({ where: { bankId } })).map(r => BankBranch.load(r as any));
  }

  async findAll(): Promise<BankBranch[]> {
    return (await this.prisma.bnkBranch.findMany({ orderBy: { code: "asc" } })).map(r => BankBranch.load(r as any));
  }
}

// ─── Correspondent Bank Repository ──────────────────────────────────────────────

@Injectable()
export class PrismaCorrespondentBankRepository implements CorrespondentBankRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(correspondent: CorrespondentBank): Promise<void> {
    const s = correspondent.toState();
    await this.prisma.bnkCorrespondent.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: CorrespondentBankId): Promise<CorrespondentBank | null> {
    const row = await this.prisma.bnkCorrespondent.findUnique({ where: { id: id.value } });
    return row ? CorrespondentBank.load(row as any) : null;
  }

  async findByBank(bankId: string): Promise<CorrespondentBank[]> {
    return (await this.prisma.bnkCorrespondent.findMany({ where: { bankId } })).map(r => CorrespondentBank.load(r as any));
  }

  async findByCurrency(currencyCode: string): Promise<CorrespondentBank[]> {
    return (await this.prisma.bnkCorrespondent.findMany({ where: { currencyCode } })).map(r => CorrespondentBank.load(r as any));
  }

  async findAll(): Promise<CorrespondentBank[]> {
    return (await this.prisma.bnkCorrespondent.findMany()).map(r => CorrespondentBank.load(r as any));
  }
}

// ─── Bank Account Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaBankAccountRepository implements BankAccountRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(account: BankAccount): Promise<void> {
    const s = account.toState();
    await this.prisma.bnkAccount.upsert({
      where: { id: s.id },
      create: { ...s, currentBalance: toBigInt(s.currentBalance), availableBalance: toBigInt(s.availableBalance), blockedBalance: toBigInt(s.blockedBalance), creditLimit: toBigInt(s.creditLimit), minimumBalance: toBigInt(s.minimumBalance), maximumBalance: toBigInt(s.maximumBalance), overdraftLimit: toBigInt(s.overdraftLimit) } as any,
      update: { ...s, currentBalance: toBigInt(s.currentBalance), availableBalance: toBigInt(s.availableBalance), blockedBalance: toBigInt(s.blockedBalance), creditLimit: toBigInt(s.creditLimit), minimumBalance: toBigInt(s.minimumBalance), maximumBalance: toBigInt(s.maximumBalance), overdraftLimit: toBigInt(s.overdraftLimit) } as any,
    });
  }

  async findById(id: BankAccountId): Promise<BankAccount | null> {
    const row = await this.prisma.bnkAccount.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByAccountNumber(accountNumber: string): Promise<BankAccount | null> {
    const row = await this.prisma.bnkAccount.findFirst({ where: { accountNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByBank(bankId: string): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { bankId } })).map(r => this.toDomain(r as any));
  }

  async findByCompany(companyId: string): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { companyId } })).map(r => this.toDomain(r as any));
  }

  async findByStatus(status: BankAccountStatus): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { status } })).map(r => this.toDomain(r as any));
  }

  async findByCurrency(currencyCode: string): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { currencyCode } })).map(r => this.toDomain(r as any));
  }

  async findActive(): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { status: "active" } })).map(r => this.toDomain(r as any));
  }

  async findByGLAccount(glAccountId: string): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ where: { glAccountId } })).map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<BankAccount[]> {
    return (await this.prisma.bnkAccount.findMany({ orderBy: { accountNumber: "asc" } })).map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): BankAccount {
    return BankAccount.load({
      id: row.id, companyId: row.companyId, bankId: row.bankId, branchId: row.branchId ?? null,
      accountNumber: row.accountNumber, accountName: row.accountName, accountNameEn: row.accountNameEn ?? null,
      accountCategory: row.accountCategory, currencyCode: row.currencyCode, countryCode: row.countryCode,
      iban: row.iban ?? null, swiftCode: row.swiftCode ?? null, routingNumber: row.routingNumber ?? null,
      status: row.status, currentBalance: toNumber(row.currentBalance),
      availableBalance: toNumber(row.availableBalance), blockedBalance: toNumber(row.blockedBalance),
      creditLimit: toNumber(row.creditLimit), minimumBalance: toNumber(row.minimumBalance),
      maximumBalance: toNumber(row.maximumBalance), overdraftLimit: toNumber(row.overdraftLimit),
      interestRate: toNumber(row.interestRate),
      glAccountId: row.glAccountId ?? null, glBankChargeAccountId: row.glBankChargeAccountId ?? null,
      glInterestAccountId: row.glInterestAccountId ?? null, glFXAccountId: row.glFXAccountId ?? null,
      isVirtual: row.isVirtual, parentAccountId: row.parentAccountId ?? null,
      classification: row.classification ?? null,
      openingDate: row.openingDate, closingDate: row.closingDate ?? null,
      lastActivityDate: row.lastActivityDate ?? null, lastReconciliationDate: row.lastReconciliationDate ?? null,
      notes: row.notes ?? null, version: row.version,
      createdAt: row.createdAt, updatedAt: row.updatedAt, deletedAt: row.deletedAt ?? null,
    });
  }
}

// ─── Authorized Signer Repository ──────────────────────────────────────────────

@Injectable()
export class PrismaAuthorizedSignerRepository implements AuthorizedSignerRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(signer: AuthorizedSigner): Promise<void> {
    const s = signer.toState();
    await this.prisma.bnkAuthorizedSigner.upsert({
      where: { id: s.id },
      create: { ...s, signingLimit: toBigInt(s.signingLimit) } as any,
      update: { ...s, signingLimit: toBigInt(s.signingLimit) } as any,
    });
  }

  async findById(id: AuthorizedSignerId): Promise<AuthorizedSigner | null> {
    const row = await this.prisma.bnkAuthorizedSigner.findUnique({ where: { id: id.value } });
    return row ? AuthorizedSigner.load(row as any) : null;
  }

  async findByAccount(bankAccountId: string): Promise<AuthorizedSigner[]> {
    return (await this.prisma.bnkAuthorizedSigner.findMany({ where: { bankAccountId } })).map(r => AuthorizedSigner.load(r as any));
  }

  async findByUser(userId: string): Promise<AuthorizedSigner[]> {
    return (await this.prisma.bnkAuthorizedSigner.findMany({ where: { userId } })).map(r => AuthorizedSigner.load(r as any));
  }
}

// ─── Account Limit Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaAccountLimitRepository implements AccountLimitRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(limit: AccountLimit): Promise<void> {
    const s = limit.toState();
    await this.prisma.bnkAccountLimit.upsert({
      where: { id: s.id },
      create: { ...s, maxAmount: toBigInt(s.maxAmount), minAmount: toBigInt(s.minAmount) } as any,
      update: { ...s, maxAmount: toBigInt(s.maxAmount), minAmount: toBigInt(s.minAmount) } as any,
    });
  }

  async findById(id: AccountLimitId): Promise<AccountLimit | null> {
    const row = await this.prisma.bnkAccountLimit.findUnique({ where: { id: id.value } });
    return row ? AccountLimit.load(row as any) : null;
  }

  async findByAccount(bankAccountId: string): Promise<AccountLimit[]> {
    return (await this.prisma.bnkAccountLimit.findMany({ where: { bankAccountId } })).map(r => AccountLimit.load(r as any));
  }
}

// ─── Account Mapping Repository ─────────────────────────────────────────────────

@Injectable()
export class PrismaAccountMappingRepository implements AccountMappingRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(mapping: AccountMapping): Promise<void> {
    const s = mapping.toState();
    await this.prisma.bnkAccountMapping.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findByAccount(bankAccountId: string): Promise<AccountMapping[]> {
    const rows = await this.prisma.bnkAccountMapping.findMany({ where: { bankAccountId } });
    return rows.map(r => ({ id: r.id, bankAccountId: r.bankAccountId, mappingType: r.mappingType, glAccountId: r.glAccountId ?? null, branchId: r.branchId ?? null, costCenterId: r.costCenterId ?? null, departmentId: r.departmentId ?? null, projectId: r.projectId ?? null, isDefault: r.isDefault })) as any;
  }

  async findByGLAccount(glAccountId: string): Promise<AccountMapping[]> {
    return this.findByAccount(glAccountId); // simplified
  }

  async findDefault(bankAccountId: string): Promise<AccountMapping | null> {
    const row = await this.prisma.bnkAccountMapping.findFirst({ where: { bankAccountId, isDefault: true } });
    return row ? ({ id: row.id, bankAccountId: row.bankAccountId, mappingType: row.mappingType, glAccountId: row.glAccountId ?? null, branchId: row.branchId ?? null, costCenterId: row.costCenterId ?? null, departmentId: row.departmentId ?? null, projectId: row.projectId ?? null, isDefault: row.isDefault } as any) : null;
  }
}

// ─── Transaction Repository ─────────────────────────────────────────────────────

@Injectable()
export class PrismaBankTransactionRepository implements BankTransactionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transaction: BankTransaction): Promise<void> {
    const s = transaction.toState();
    const data = {
      ...s, amount: toBigInt(s.amount), vndAmount: toBigInt(s.vndAmount), fees: toBigInt(s.fees),
    };
    await this.prisma.bnkTransaction.upsert({
      where: { id: s.id }, create: data as any, update: data as any,
    });
  }

  async findById(id: BankTransactionId): Promise<BankTransaction | null> {
    const row = await this.prisma.bnkTransaction.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByNumber(transactionNumber: string): Promise<BankTransaction | null> {
    const row = await this.prisma.bnkTransaction.findUnique({ where: { transactionNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByFromAccount(accountId: string): Promise<BankTransaction[]> {
    return (await this.prisma.bnkTransaction.findMany({ where: { fromAccountId: accountId }, orderBy: { transactionDate: "desc" } })).map(r => this.toDomain(r as any));
  }

  async findByToAccount(accountId: string): Promise<BankTransaction[]> {
    return (await this.prisma.bnkTransaction.findMany({ where: { toAccountId: accountId }, orderBy: { transactionDate: "desc" } })).map(r => this.toDomain(r as any));
  }

  async findByStatus(status: TransactionStatus): Promise<BankTransaction[]> {
    return (await this.prisma.bnkTransaction.findMany({ where: { status }, orderBy: { transactionDate: "desc" } })).map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<BankTransaction[]> {
    return (await this.prisma.bnkTransaction.findMany({ where: { transactionDate: { gte: from, lte: to } }, orderBy: { transactionDate: "desc" } })).map(r => this.toDomain(r as any));
  }

  async findByReference(reference: string): Promise<BankTransaction | null> {
    const row = await this.prisma.bnkTransaction.findFirst({ where: { reference } });
    return row ? this.toDomain(row as any) : null;
  }

  async findAll(): Promise<BankTransaction[]> {
    return (await this.prisma.bnkTransaction.findMany({ orderBy: { transactionDate: "desc" } })).map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): BankTransaction {
    return BankTransaction.load({
      id: row.id, companyId: row.companyId, transactionNumber: row.transactionNumber,
      nature: row.nature, method: row.method, status: row.status,
      fromAccountId: row.fromAccountId, fromAccountNumber: row.fromAccountNumber ?? null,
      toAccountId: row.toAccountId ?? null, toAccountNumber: row.toAccountNumber ?? null,
      toBankId: row.toBankId ?? null, toBankName: row.toBankName ?? null,
      toBankSwift: row.toBankSwift ?? null, toBankRouting: row.toBankRouting ?? null,
      beneficiaryName: row.beneficiaryName ?? null, beneficiaryAccount: row.beneficiaryAccount ?? null,
      beneficiaryAddress: row.beneficiaryAddress ?? null, beneficiaryBank: row.beneficiaryBank ?? null,
      intermediaryBankId: row.intermediaryBankId ?? null, intermediaryBankSwift: row.intermediaryBankSwift ?? null,
      amount: toNumber(row.amount), currencyCode: row.currencyCode, exchangeRate: toNumber(row.exchangeRate),
      vndAmount: toNumber(row.vndAmount), chargeBearer: row.chargeBearer,
      paymentPriority: row.paymentPriority, settlementMethod: row.settlementMethod ?? null,
      paymentChannel: row.paymentChannel ?? null, reference: row.reference ?? null,
      description: row.description ?? null, fees: toNumber(row.fees),
      feeCurrencyCode: row.feeCurrencyCode,
      valueDate: row.valueDate ?? null, transactionDate: row.transactionDate,
      swiftMessage: row.swiftMessage ?? null, endToEndId: row.endToEndId ?? null,
      transactionId: row.transactionId ?? null, clearingSystemRef: row.clearingSystemRef ?? null,
      approvalLevel: row.approvalLevel, requiredApprovals: row.requiredApprovals,
      approvedById: row.approvedById ?? null, approvedAt: row.approvedAt ?? null,
      executedById: row.executedById ?? null, executedAt: row.executedAt ?? null,
      completedAt: row.completedAt ?? null, failureReason: row.failureReason ?? null,
      reversalReason: row.reversalReason ?? null, reversedAt: row.reversedAt ?? null,
      postedToGL: row.postedToGL, glBatchId: row.glBatchId ?? null,
      version: row.version, createdAt: row.createdAt, updatedAt: row.updatedAt, deletedAt: row.deletedAt ?? null,
    });
  }
}

// ─── Statement Repository ────────────────────────────────────────────────────────

@Injectable()
export class PrismaBankStatementRepository implements BankStatementRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(statement: BankStatement): Promise<void> {
    const s = statement.toState();
    const data = { ...s, openingBalance: toBigInt(s.openingBalance), closingBalance: toBigInt(s.closingBalance), totalDebit: toBigInt(s.totalDebit), totalCredit: toBigInt(s.totalCredit) };
    await this.prisma.bnkStatement.upsert({
      where: { id: s.id }, create: data as any, update: data as any,
    });
  }

  async findById(id: BankStatementId): Promise<BankStatement | null> {
    const row = await this.prisma.bnkStatement.findUnique({ where: { id: id.value } });
    return row ? BankStatement.load(row as any) : null;
  }

  async findByNumber(statementNumber: string): Promise<BankStatement | null> {
    const row = await this.prisma.bnkStatement.findFirst({ where: { statementNumber } });
    return row ? BankStatement.load(row as any) : null;
  }

  async findByBankAccount(bankAccountId: string): Promise<BankStatement[]> {
    return (await this.prisma.bnkStatement.findMany({ where: { bankAccountId }, orderBy: { periodStart: "desc" } })).map(r => BankStatement.load(r as any));
  }

  async findUnreconciled(bankAccountId: string): Promise<BankStatement[]> {
    return (await this.prisma.bnkStatement.findMany({ where: { bankAccountId, isReconciled: false } })).map(r => BankStatement.load(r as any));
  }

  async findReconciled(bankAccountId: string): Promise<BankStatement[]> {
    return (await this.prisma.bnkStatement.findMany({ where: { bankAccountId, isReconciled: true } })).map(r => BankStatement.load(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<BankStatement[]> {
    return (await this.prisma.bnkStatement.findMany({ where: { periodStart: { gte: from }, periodEnd: { lte: to } } })).map(r => BankStatement.load(r as any));
  }

  async findAll(): Promise<BankStatement[]> {
    return (await this.prisma.bnkStatement.findMany({ orderBy: { periodStart: "desc" } })).map(r => BankStatement.load(r as any));
  }
}

// ─── Statement Line Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaBankStatementLineRepository implements BankStatementLineRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(line: BankStatementLine): Promise<void> {
    const s = line.toState();
    await this.prisma.bnkStatementLine.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount), runningBalance: toBigInt(s.runningBalance) } as any,
      update: { ...s, amount: toBigInt(s.amount), runningBalance: toBigInt(s.runningBalance) } as any,
    });
  }

  async findById(id: BankStatementLineId): Promise<BankStatementLine | null> {
    const row = await this.prisma.bnkStatementLine.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByStatement(statementId: string): Promise<BankStatementLine[]> {
    return (await this.prisma.bnkStatementLine.findMany({ where: { statementId }, orderBy: { lineDate: "asc" } })).map(r => this.toDomain(r as any));
  }

  async findUnmatched(statementId: string): Promise<BankStatementLine[]> {
    return (await this.prisma.bnkStatementLine.findMany({ where: { statementId, isMatched: false } })).map(r => this.toDomain(r as any));
  }

  async findByReference(reference: string): Promise<BankStatementLine[]> {
    return (await this.prisma.bnkStatementLine.findMany({ where: { reference } })).map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): BankStatementLine {
    const line = new (BankStatementLine as any)(new BankStatementLineId(row.id), row.statementId, row.lineDate, row.lineType, toNumber(row.amount), toNumber(row.runningBalance), row.currencyCode);
    line._description = row.description ?? null; line._reference = row.reference ?? null;
    line._chequeNumber = row.chequeNumber ?? null; line._valueDate = row.valueDate ?? null;
    line._exchangeRate = toNumber(row.exchangeRate);
    line._isMatched = row.isMatched; line._matchedToId = row.matchedToId ?? null;
    line._matchedToType = row.matchedToType ?? null; line._matchedAt = row.matchedAt ?? null;
    line._notes = row.notes ?? null; line._createdAt = row.createdAt; line._updatedAt = row.updatedAt;
    return line;
  }
}

// ─── Reconciliation Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaBankReconciliationRepository implements BankReconciliationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rec: BankReconciliation): Promise<void> {
    const s = rec.toState();
    const data = { ...s, statementBalance: toBigInt(s.statementBalance), bookBalance: toBigInt(s.bookBalance), clearedAmount: toBigInt(s.clearedAmount), outstandingAmount: toBigInt(s.outstandingAmount), difference: toBigInt(s.difference) };
    await this.prisma.bnkReconciliation.upsert({
      where: { id: s.id }, create: data as any, update: data as any,
    });
  }

  async findById(id: BankReconciliationId): Promise<BankReconciliation | null> {
    const row = await this.prisma.bnkReconciliation.findUnique({ where: { id: id.value } });
    return row ? BankReconciliation.load(row as any) : null;
  }

  async findByNumber(reconciliationNumber: string): Promise<BankReconciliation | null> {
    const row = await this.prisma.bnkReconciliation.findUnique({ where: { reconciliationNumber } });
    return row ? BankReconciliation.load(row as any) : null;
  }

  async findByBankAccount(bankAccountId: string): Promise<BankReconciliation[]> {
    return (await this.prisma.bnkReconciliation.findMany({ where: { bankAccountId }, orderBy: { reconciliationDate: "desc" } })).map(r => BankReconciliation.load(r as any));
  }

  async findByStatement(bankStatementId: string): Promise<BankReconciliation[]> {
    return (await this.prisma.bnkReconciliation.findMany({ where: { bankStatementId } })).map(r => BankReconciliation.load(r as any));
  }

  async findByStatus(status: ReconciliationStatus): Promise<BankReconciliation[]> {
    return (await this.prisma.bnkReconciliation.findMany({ where: { status } })).map(r => BankReconciliation.load(r as any));
  }

  async findAll(): Promise<BankReconciliation[]> {
    return (await this.prisma.bnkReconciliation.findMany({ orderBy: { reconciliationDate: "desc" } })).map(r => BankReconciliation.load(r as any));
  }
}

// ─── Bank Reconciliation Item Repository ────────────────────────────────────────────

@Injectable()
export class PrismaBankReconciliationItemRepository implements BankReconciliationItemRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(item: BankReconciliationItem): Promise<void> {
    const s = item.toState();
    await this.prisma.bnkReconciliationItem.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount) } as any,
      update: { ...s, amount: toBigInt(s.amount) } as any,
    });
  }

  async findById(id: BankReconciliationItemId): Promise<BankReconciliationItem | null> {
    const row = await this.prisma.bnkReconciliationItem.findUnique({ where: { id: id.value } });
    return row ? BankReconciliationItem.load(row as any) : null;
  }

  async findByReconciliation(reconciliationId: string): Promise<BankReconciliationItem[]> {
    return (await this.prisma.bnkReconciliationItem.findMany({ where: { reconciliationId } })).map(r => BankReconciliationItem.load(r as any));
  }

  async findBySource(sourceType: string, sourceId: string): Promise<BankReconciliationItem[]> {
    return (await this.prisma.bnkReconciliationItem.findMany({ where: { sourceType, sourceId } })).map(r => BankReconciliationItem.load(r as any));
  }
}

// ─── Payment Request Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaPaymentRequestRepository implements PaymentRequestRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(request: PaymentRequest): Promise<void> {
    const s = request.toState();
    await this.prisma.bnkPaymentRequest.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount) } as any,
      update: { ...s, amount: toBigInt(s.amount) } as any,
    });
  }

  async findById(id: PaymentRequestId): Promise<PaymentRequest | null> {
    const row = await this.prisma.bnkPaymentRequest.findUnique({ where: { id: id.value } });
    return row ? PaymentRequest.load(row as any) : null;
  }

  async findByNumber(requestNumber: string): Promise<PaymentRequest | null> {
    const row = await this.prisma.bnkPaymentRequest.findUnique({ where: { requestNumber } });
    return row ? PaymentRequest.load(row as any) : null;
  }

  async findByStatus(status: string): Promise<PaymentRequest[]> {
    return (await this.prisma.bnkPaymentRequest.findMany({ where: { approvalStatus: status as any } })).map(r => PaymentRequest.load(r as any));
  }

  async findByFromAccount(accountId: string): Promise<PaymentRequest[]> {
    return (await this.prisma.bnkPaymentRequest.findMany({ where: { fromAccountId: accountId } })).map(r => PaymentRequest.load(r as any));
  }

  async findByCompany(companyId: string): Promise<PaymentRequest[]> {
    return (await this.prisma.bnkPaymentRequest.findMany({ where: { companyId } })).map(r => PaymentRequest.load(r as any));
  }

  async findByBatch(batchId: string): Promise<PaymentRequest[]> {
    return (await this.prisma.bnkPaymentRequest.findMany({ where: { batchId } })).map(r => PaymentRequest.load(r as any));
  }

  async findAll(): Promise<PaymentRequest[]> {
    return (await this.prisma.bnkPaymentRequest.findMany({ orderBy: { createdAt: "desc" } })).map(r => PaymentRequest.load(r as any));
  }
}

// ─── Payment Batch Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaPaymentBatchRepository implements PaymentBatchRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(batch: PaymentBatch): Promise<void> {
    const s = batch.toState();
    await this.prisma.bnkPaymentBatch.upsert({
      where: { id: s.id },
      create: { ...s, totalAmount: toBigInt(s.totalAmount) } as any,
      update: { ...s, totalAmount: toBigInt(s.totalAmount) } as any,
    });
  }

  async findById(id: PaymentBatchId): Promise<PaymentBatch | null> {
    const row = await this.prisma.bnkPaymentBatch.findUnique({ where: { id: id.value } });
    return row ? PaymentBatch.load(row as any) : null;
  }

  async findByNumber(batchNumber: string): Promise<PaymentBatch | null> {
    const row = await this.prisma.bnkPaymentBatch.findUnique({ where: { batchNumber } });
    return row ? PaymentBatch.load(row as any) : null;
  }

  async findByStatus(status: PaymentBatchStatus): Promise<PaymentBatch[]> {
    return (await this.prisma.bnkPaymentBatch.findMany({ where: { status } })).map(r => PaymentBatch.load(r as any));
  }

  async findByCompany(companyId: string): Promise<PaymentBatch[]> {
    return (await this.prisma.bnkPaymentBatch.findMany({ where: { companyId } })).map(r => PaymentBatch.load(r as any));
  }

  async findAll(): Promise<PaymentBatch[]> {
    return (await this.prisma.bnkPaymentBatch.findMany({ orderBy: { createdAt: "desc" } })).map(r => PaymentBatch.load(r as any));
  }
}

// ─── Recurring Payment Repository ───────────────────────────────────────────────

@Injectable()
export class PrismaRecurringPaymentRepository implements RecurringPaymentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(recurring: RecurringPayment): Promise<void> {
    const s = recurring.toState();
    await this.prisma.bnkRecurringPayment.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: RecurringPaymentId): Promise<RecurringPayment | null> {
    const row = await this.prisma.bnkRecurringPayment.findUnique({ where: { id: id.value } });
    return row ? RecurringPayment.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<RecurringPayment[]> {
    return (await this.prisma.bnkRecurringPayment.findMany({ where: { companyId } })).map(r => RecurringPayment.load(r as any));
  }

  async findDueForExecution(date: Date): Promise<RecurringPayment[]> {
    return (await this.prisma.bnkRecurringPayment.findMany({
      where: { isActive: true, nextExecutionDate: { lte: date } },
    })).map(r => RecurringPayment.load(r as any));
  }

  async findAll(): Promise<RecurringPayment[]> {
    return (await this.prisma.bnkRecurringPayment.findMany()).map(r => RecurringPayment.load(r as any));
  }
}

// ─── Cash Position Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaCashPositionRepository implements CashPositionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(position: CashPosition): Promise<void> {
    const s = position.toState();
    const data = { ...s, openingBalance: toBigInt(s.openingBalance), totalInflows: toBigInt(s.totalInflows), totalOutflows: toBigInt(s.totalOutflows), netFlow: toBigInt(s.netFlow), closingBalance: toBigInt(s.closingBalance), availableBalance: toBigInt(s.availableBalance), blockedBalance: toBigInt(s.blockedBalance), pendingInflows: toBigInt(s.pendingInflows), pendingOutflows: toBigInt(s.pendingOutflows), projectedBalance: toBigInt(s.projectedBalance), minimumBalance: toBigInt(s.minimumBalance), maximumBalance: toBigInt(s.maximumBalance) };
    await this.prisma.bnkCashPosition.upsert({
      where: { id: s.id }, create: data as any, update: data as any,
    });
  }

  async findById(id: CashPositionId): Promise<CashPosition | null> {
    const row = await this.prisma.bnkCashPosition.findUnique({ where: { id: id.value } });
    return row ? CashPosition.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<CashPosition[]> {
    return (await this.prisma.bnkCashPosition.findMany({ where: { companyId }, orderBy: { positionDate: "desc" } })).map(r => CashPosition.load(r as any));
  }

  async findByDate(companyId: string, date: Date): Promise<CashPosition | null> {
    const row = await this.prisma.bnkCashPosition.findFirst({ where: { companyId, positionDate: date } });
    return row ? CashPosition.load(row as any) : null;
  }

  async findByDateRange(companyId: string, from: Date, to: Date): Promise<CashPosition[]> {
    return (await this.prisma.bnkCashPosition.findMany({
      where: { companyId, positionDate: { gte: from, lte: to } },
      orderBy: { positionDate: "asc" },
    })).map(r => CashPosition.load(r as any));
  }
}

// ─── Cash Forecast Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaCashForecastRepository implements CashForecastRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(forecast: CashForecast): Promise<void> {
    const s = forecast.toState();
    await this.prisma.bnkCashForecast.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: CashForecastId): Promise<CashForecast | null> {
    const row = await this.prisma.bnkCashForecast.findUnique({ where: { id: id.value } });
    return row ? CashForecast.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<CashForecast[]> {
    return (await this.prisma.bnkCashForecast.findMany({ where: { companyId } })).map(r => CashForecast.load(r as any));
  }

  async findByDateRange(companyId: string, from: Date, to: Date): Promise<CashForecast[]> {
    return (await this.prisma.bnkCashForecast.findMany({
      where: { companyId, periodStart: { gte: from }, periodEnd: { lte: to } },
    })).map(r => CashForecast.load(r as any));
  }
}

// ─── FX Rate Repository ──────────────────────────────────────────────────────────

@Injectable()
export class PrismaFXRateRepository implements FXRateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rate: FXRate): Promise<void> {
    const s = rate.toState();
    await this.prisma.bnkFXRate.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: FXRateId): Promise<FXRate | null> {
    const row = await this.prisma.bnkFXRate.findUnique({ where: { id: id.value } });
    return row ? new FXRate(new FXRateId(row.id), row.fromCurrency, row.toCurrency, toNumber(row.rate as unknown as string), row.rateType as any, row.validFrom, row.validTo, row.source, row.isActive) : null;
  }

  async findRate(fromCurrency: string, toCurrency: string, date: Date): Promise<FXRate | null> {
    const row = await this.prisma.bnkFXRate.findFirst({
      where: { fromCurrency, toCurrency, isActive: true, validFrom: { lte: date }, validTo: { gte: date } },
      orderBy: { updatedAt: "desc" },
    });
    return row ? new FXRate(new FXRateId(row.id), row.fromCurrency, row.toCurrency, toNumber(row.rate as unknown as string), row.rateType as any, row.validFrom, row.validTo, row.source, row.isActive) : null;
  }

  async findByCurrencyPair(fromCurrency: string, toCurrency: string): Promise<FXRate[]> {
    return (await this.prisma.bnkFXRate.findMany({ where: { fromCurrency, toCurrency } })).map(r => new FXRate(new FXRateId(r.id), r.fromCurrency, r.toCurrency, toNumber(r.rate as unknown as string), r.rateType as any, r.validFrom, r.validTo, r.source, r.isActive));
  }

  async findByType(rateType: string): Promise<FXRate[]> {
    return (await this.prisma.bnkFXRate.findMany({ where: { rateType: rateType as any } })).map(r => new FXRate(new FXRateId(r.id), r.fromCurrency, r.toCurrency, toNumber(r.rate as unknown as string), r.rateType as any, r.validFrom, r.validTo, r.source, r.isActive));
  }
}

// ─── FX Revaluation Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaFXRevaluationRepository implements FXRevaluationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(revaluation: FXRevaluation): Promise<void> {
    const s = revaluation.toState();
    await this.prisma.bnkFXRevaluation.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: FXRevaluationId): Promise<FXRevaluation | null> {
    const row = await this.prisma.bnkFXRevaluation.findUnique({ where: { id: id.value } });
    return row ? FXRevaluation.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<FXRevaluation[]> {
    return (await this.prisma.bnkFXRevaluation.findMany({ where: { companyId } })).map(r => FXRevaluation.load(r as any));
  }

  async findByAccount(accountId: string): Promise<FXRevaluation[]> {
    return (await this.prisma.bnkFXRevaluation.findMany({ where: { accountId } })).map(r => FXRevaluation.load(r as any));
  }

  async findByDateRange(companyId: string, from: Date, to: Date): Promise<FXRevaluation[]> {
    return (await this.prisma.bnkFXRevaluation.findMany({
      where: { companyId, revaluationDate: { gte: from, lte: to } },
    })).map(r => FXRevaluation.load(r as any));
  }
}

// ─── Approval Matrix Repository ─────────────────────────────────────────────────

@Injectable()
export class PrismaApprovalMatrixRepository implements ApprovalMatrixRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(matrix: ApprovalMatrix): Promise<void> {
    const s = matrix.toState();
    await this.prisma.bnkApprovalMatrix.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: ApprovalMatrixId): Promise<ApprovalMatrix | null> {
    const row = await this.prisma.bnkApprovalMatrix.findUnique({ where: { id: id.value } });
    return row ? ApprovalMatrix.load(row as any) : null;
  }

  async findByEntityType(entityType: string): Promise<ApprovalMatrix[]> {
    return (await this.prisma.bnkApprovalMatrix.findMany({ where: { entityType } })).map(r => ApprovalMatrix.load(r as any));
  }

  async findByEntityTypeAndAmount(entityType: string, amount: number): Promise<ApprovalMatrix | null> {
    const rows = await this.prisma.bnkApprovalMatrix.findMany({ where: { entityType, isActive: true } });
    return rows.find(r => {
      const min = toNumber(r.minAmount); const max = toNumber(r.maxAmount);
      return (min === 0 || amount >= min) && (max === 0 || amount <= max);
    }) ? ApprovalMatrix.load(rows[0] as any) : null;
  }

  async findActive(): Promise<ApprovalMatrix[]> {
    return (await this.prisma.bnkApprovalMatrix.findMany({ where: { isActive: true } })).map(r => ApprovalMatrix.load(r as any));
  }
}

// ─── Approval Request Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaApprovalRequestRepository implements ApprovalRequestRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(request: ApprovalRequest): Promise<void> {
    const s = request.toState();
    await this.prisma.bnkApprovalRequest.upsert({
      where: { id: s.id }, create: s as any, update: s as any,
    });
  }

  async findById(id: ApprovalRequestId): Promise<ApprovalRequest | null> {
    const row = await this.prisma.bnkApprovalRequest.findUnique({ where: { id: id.value } });
    return row ? ApprovalRequest.load(row as any) : null;
  }

  async findByEntity(entityType: string, entityId: string): Promise<ApprovalRequest[]> {
    return (await this.prisma.bnkApprovalRequest.findMany({ where: { entityType, entityId } })).map(r => ApprovalRequest.load(r as any));
  }

  async findByStatus(status: string): Promise<ApprovalRequest[]> {
    return (await this.prisma.bnkApprovalRequest.findMany({ where: { status: status as any } })).map(r => ApprovalRequest.load(r as any));
  }

  async findByRequester(userId: string): Promise<ApprovalRequest[]> {
    return (await this.prisma.bnkApprovalRequest.findMany({ where: { requestedById: userId } })).map(r => ApprovalRequest.load(r as any));
  }
}
