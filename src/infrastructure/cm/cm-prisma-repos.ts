import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  CashBoxId, CashSessionId, CashReceiptId, CashPaymentId,
  CashAdvanceId, CashTransferId, PettyCashId, BankId, BankAccountId,
  BankStatementId, BankTransferId, ChequeBookId, BankReconciliationId,
  CashForecastId, LiquidityForecastId, CompanyId, CashierId, CashRegisterId,
} from "../../domain/cm/cm-ids.js";
import { CashBox } from "../../domain/cm/cm-cash-box.js";
import { CashSession } from "../../domain/cm/cm-session.js";
import { CashReceipt } from "../../domain/cm/cm-cash-receipt.js";
import { CashPayment } from "../../domain/cm/cm-cash-payment.js";
import { CashAdvance } from "../../domain/cm/cm-cash-advance.js";
import { CashTransfer } from "../../domain/cm/cm-cash-transfer.js";
import { PettyCash } from "../../domain/cm/cm-petty-cash.js";
import { Bank } from "../../domain/cm/cm-bank.js";
import { BankAccount } from "../../domain/cm/cm-bank.js";
import { ChequeBook } from "../../domain/cm/cm-cheque.js";
import { BankTransfer } from "../../domain/cm/cm-bank-transfer.js";
import { BankStatement } from "../../domain/cm/cm-bank-statement.js";
import { BankReconciliation } from "../../domain/cm/cm-bank-statement.js";
import { CashForecast } from "../../domain/cm/cm-cash-forecast.js";
import { LiquidityForecast } from "../../domain/cm/cm-cash-forecast.js";
import type {
  CashBoxRepository, CashSessionRepository, CashReceiptRepository,
  CashPaymentRepository, CashAdvanceRepository, CashTransferRepository,
  PettyCashRepository, BankRepository, BankAccountRepository,
  ChequeBookRepository, BankTransferRepository as IBankTransferRepository,
  BankStatementRepository, BankReconciliationRepository,
  CashForecastRepository, LiquidityForecastRepository,
} from "../../domain/cm/cm-repositories.js";
import type { ReceiptStatus, PaymentStatus, CashTransferStatus, BankReconciliationStatus } from "../../domain/cm/cm-enums.js";

function toNumber(val: bigint | number | string | null | undefined, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  return val;
}

function toBigInt(val: number): bigint {
  return BigInt(Math.round(val));
}

@Injectable()
export class PrismaCashBoxRepository implements CashBoxRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(box: CashBox): Promise<void> {
    const s = box.toState();
    await this.prisma.cashBox.upsert({
      where: { id: s.id },
      create: { ...s, currentBalance: toBigInt(s.currentBalance), minBalance: toBigInt(s.minBalance), maxBalance: s.maxBalance !== null ? toBigInt(s.maxBalance) : null } as any,
      update: { ...s, currentBalance: toBigInt(s.currentBalance), minBalance: toBigInt(s.minBalance), maxBalance: s.maxBalance !== null ? toBigInt(s.maxBalance) : null } as any,
    });
  }

  async findById(id: CashBoxId): Promise<CashBox | null> {
    const row = await this.prisma.cashBox.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByCode(code: string): Promise<CashBox | null> {
    const row = await this.prisma.cashBox.findUnique({ where: { code } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByLocation(locationId: string): Promise<CashBox[]> {
    const rows = await this.prisma.cashBox.findMany({ where: { locationId } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<CashBox[]> {
    const rows = await this.prisma.cashBox.findMany();
    return rows.map(r => this.toDomain(r as any));
  }

  async findActive(): Promise<CashBox[]> {
    const rows = await this.prisma.cashBox.findMany({ where: { status: "active", deletedAt: null } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashBox {
    return CashBox.load({
      id: row.id,
      locationId: row.locationId,
      code: row.code,
      name: row.name,
      boxType: row.boxType,
      currencyCode: row.currencyCode,
      minBalance: toNumber(row.minBalance),
      maxBalance: row.maxBalance !== null ? toNumber(row.maxBalance) : null,
      currentBalance: toNumber(row.currentBalance),
      allowNegative: row.allowNegative,
      status: row.status,
      description: row.description,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaCashSessionRepository implements CashSessionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(session: CashSession): Promise<void> {
    const s = session.toState();
    await this.prisma.cashSession.upsert({
      where: { id: s.id },
      create: {
        ...s,
        openedBalance: toBigInt(s.openedBalance),
        expectedBalance: toBigInt(s.expectedBalance),
        countedBalance: toBigInt(s.countedBalance),
        difference: toBigInt(s.difference),
      } as any,
      update: {
        ...s,
        openedBalance: toBigInt(s.openedBalance),
        expectedBalance: toBigInt(s.expectedBalance),
        countedBalance: toBigInt(s.countedBalance),
        difference: toBigInt(s.difference),
      } as any,
    });
  }

  async findById(id: CashSessionId): Promise<CashSession | null> {
    const row = await this.prisma.cashSession.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByCashBox(cashBoxId: string): Promise<CashSession[]> {
    const rows = await this.prisma.cashSession.findMany({ where: { cashBoxId }, orderBy: { openedAt: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByCashier(cashierId: string): Promise<CashSession[]> {
    const rows = await this.prisma.cashSession.findMany({ where: { cashierId }, orderBy: { openedAt: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashSession[]> {
    const rows = await this.prisma.cashSession.findMany({
      where: { openedAt: { gte: from, lte: to } },
      orderBy: { openedAt: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findOpenByCashBox(cashBoxId: string): Promise<CashSession | null> {
    const row = await this.prisma.cashSession.findFirst({
      where: { cashBoxId, status: "open" },
    });
    return row ? this.toDomain(row as any) : null;
  }

  async findAll(): Promise<CashSession[]> {
    const rows = await this.prisma.cashSession.findMany({ orderBy: { openedAt: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashSession {
    return CashSession.load({
      id: row.id,
      sessionNumber: row.sessionNumber,
      cashBoxId: row.cashBoxId,
      cashRegisterId: row.cashRegisterId ?? null,
      cashierId: row.cashierId,
      status: row.status,
      openedAt: row.openedAt,
      closedAt: row.closedAt ?? null,
      openedBalance: toNumber(row.openedBalance),
      expectedBalance: toNumber(row.expectedBalance),
      countedBalance: toNumber(row.countedBalance),
      difference: toNumber(row.difference),
      currencyCode: row.currencyCode,
      notes: row.notes ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaCashReceiptRepository implements CashReceiptRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(receipt: CashReceipt): Promise<void> {
    const s = receipt.toState();
    await this.prisma.cashReceipt.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount), vndAmount: toBigInt(s.vndAmount) } as any,
      update: { ...s, amount: toBigInt(s.amount), vndAmount: toBigInt(s.vndAmount) } as any,
    });
  }

  async findById(id: CashReceiptId): Promise<CashReceipt | null> {
    const row = await this.prisma.cashReceipt.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByNumber(receiptNumber: string): Promise<CashReceipt | null> {
    const row = await this.prisma.cashReceipt.findUnique({ where: { receiptNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByCashBox(cashBoxId: string): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({ where: { cashBoxId }, orderBy: { receiptDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findBySession(sessionId: string): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({ where: { sessionId }, orderBy: { receiptDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByCashier(cashierId: string): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({ where: { cashierId }, orderBy: { receiptDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({
      where: { receiptDate: { gte: from, lte: to } },
      orderBy: { receiptDate: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByStatus(status: ReceiptStatus): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({ where: { status }, orderBy: { receiptDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<CashReceipt[]> {
    const rows = await this.prisma.cashReceipt.findMany({ orderBy: { receiptDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashReceipt {
    return CashReceipt.load({
      id: row.id,
      receiptNumber: row.receiptNumber,
      receiptDate: row.receiptDate,
      cashBoxId: row.cashBoxId,
      sessionId: row.sessionId ?? null,
      cashierId: row.cashierId,
      amount: toNumber(row.amount),
      currencyCode: row.currencyCode,
      exchangeRate: Number(row.exchangeRate),
      vndAmount: toNumber(row.vndAmount),
      paidBy: row.paidBy ?? null,
      paidById: row.paidById ?? null,
      paymentMethod: row.paymentMethod,
      reference: row.reference ?? null,
      description: row.description ?? null,
      status: row.status,
      approvedById: row.approvedById ?? null,
      approvedAt: row.approvedAt ?? null,
      postedById: row.postedById ?? null,
      postedAt: row.postedAt ?? null,
      reversedById: row.reversedById ?? null,
      reversedAt: row.reversedAt ?? null,
      reversalReason: row.reversalReason ?? null,
      glBatchId: row.glBatchId ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaCashPaymentRepository implements CashPaymentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(payment: CashPayment): Promise<void> {
    const s = payment.toState();
    await this.prisma.cashPayment.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount), vndAmount: toBigInt(s.vndAmount) } as any,
      update: { ...s, amount: toBigInt(s.amount), vndAmount: toBigInt(s.vndAmount) } as any,
    });
  }

  async findById(id: CashPaymentId): Promise<CashPayment | null> {
    const row = await this.prisma.cashPayment.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByNumber(paymentNumber: string): Promise<CashPayment | null> {
    const row = await this.prisma.cashPayment.findUnique({ where: { paymentNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByCashBox(cashBoxId: string): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({ where: { cashBoxId }, orderBy: { paymentDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findBySession(sessionId: string): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({ where: { sessionId }, orderBy: { paymentDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByCashier(cashierId: string): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({ where: { cashierId }, orderBy: { paymentDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({
      where: { paymentDate: { gte: from, lte: to } },
      orderBy: { paymentDate: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByStatus(status: PaymentStatus): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({ where: { status }, orderBy: { paymentDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<CashPayment[]> {
    const rows = await this.prisma.cashPayment.findMany({ orderBy: { paymentDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashPayment {
    return CashPayment.load({
      id: row.id,
      paymentNumber: row.paymentNumber,
      paymentDate: row.paymentDate,
      cashBoxId: row.cashBoxId,
      sessionId: row.sessionId ?? null,
      cashierId: row.cashierId,
      payeeName: row.payeeName,
      payeeId: row.payeeId ?? null,
      amount: toNumber(row.amount),
      currencyCode: row.currencyCode,
      exchangeRate: Number(row.exchangeRate),
      vndAmount: toNumber(row.vndAmount),
      paymentMethod: row.paymentMethod,
      reference: row.reference ?? null,
      description: row.description ?? null,
      status: row.status,
      approvedById: row.approvedById ?? null,
      approvedAt: row.approvedAt ?? null,
      paidById: row.paidById ?? null,
      paidAt: row.paidAt ?? null,
      postedById: row.postedById ?? null,
      postedAt: row.postedAt ?? null,
      reversedById: row.reversedById ?? null,
      reversedAt: row.reversedAt ?? null,
      reversalReason: row.reversalReason ?? null,
      glBatchId: row.glBatchId ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaCashAdvanceRepository implements CashAdvanceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(advance: CashAdvance): Promise<void> {
    const s = advance.toState();
    await this.prisma.cashAdvance.upsert({
      where: { id: s.id },
      create: {
        ...s,
        amount: toBigInt(s.amount),
        settledAmount: toBigInt(s.settledAmount),
        outstandingAmount: toBigInt(s.outstandingAmount),
      } as any,
      update: {
        ...s,
        amount: toBigInt(s.amount),
        settledAmount: toBigInt(s.settledAmount),
        outstandingAmount: toBigInt(s.outstandingAmount),
      } as any,
    });
  }

  async findById(id: CashAdvanceId): Promise<CashAdvance | null> {
    const row = await this.prisma.cashAdvance.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByNumber(advanceNumber: string): Promise<CashAdvance | null> {
    const row = await this.prisma.cashAdvance.findUnique({ where: { advanceNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByEmployee(employeeId: string): Promise<CashAdvance[]> {
    const rows = await this.prisma.cashAdvance.findMany({ where: { employeeId }, orderBy: { advanceDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashAdvance[]> {
    const rows = await this.prisma.cashAdvance.findMany({
      where: { advanceDate: { gte: from, lte: to } },
      orderBy: { advanceDate: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findOutstanding(): Promise<CashAdvance[]> {
    const rows = await this.prisma.cashAdvance.findMany({
      where: { status: { in: ["draft", "approved", "disbursed", "partially_settled"] } },
      orderBy: { advanceDate: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<CashAdvance[]> {
    const rows = await this.prisma.cashAdvance.findMany({ orderBy: { advanceDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashAdvance {
    return CashAdvance.load({
      id: row.id,
      advanceNumber: row.advanceNumber,
      companyId: row.companyId,
      employeeId: row.employeeId,
      employeeName: row.employeeName,
      amount: toNumber(row.amount),
      settledAmount: toNumber(row.settledAmount),
      outstandingAmount: toNumber(row.outstandingAmount),
      currencyCode: row.currencyCode,
      advanceDate: row.advanceDate,
      expectedSettleDate: row.expectedSettleDate ?? null,
      purpose: row.purpose,
      status: row.status,
      approvedById: row.approvedById ?? null,
      approvedAt: row.approvedAt ?? null,
      disbursedById: row.disbursedById ?? null,
      disbursedAt: row.disbursedAt ?? null,
      notes: row.notes ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaCashTransferRepository implements CashTransferRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transfer: CashTransfer): Promise<void> {
    const s = transfer.toState();
    await this.prisma.cashTransfer.upsert({
      where: { id: s.id },
      create: { ...s, amount: toBigInt(s.amount) } as any,
      update: { ...s, amount: toBigInt(s.amount) } as any,
    });
  }

  async findById(id: CashTransferId): Promise<CashTransfer | null> {
    const row = await this.prisma.cashTransfer.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByNumber(transferNumber: string): Promise<CashTransfer | null> {
    const row = await this.prisma.cashTransfer.findUnique({ where: { transferNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByFromLocation(locationId: string): Promise<CashTransfer[]> {
    const rows = await this.prisma.cashTransfer.findMany({ where: { fromLocationId: locationId }, orderBy: { transferDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByToLocation(locationId: string): Promise<CashTransfer[]> {
    const rows = await this.prisma.cashTransfer.findMany({ where: { toLocationId: locationId }, orderBy: { transferDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByStatus(status: CashTransferStatus): Promise<CashTransfer[]> {
    const rows = await this.prisma.cashTransfer.findMany({ where: { status }, orderBy: { transferDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashTransfer[]> {
    const rows = await this.prisma.cashTransfer.findMany({
      where: { transferDate: { gte: from, lte: to } },
      orderBy: { transferDate: "desc" },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<CashTransfer[]> {
    const rows = await this.prisma.cashTransfer.findMany({ orderBy: { transferDate: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): CashTransfer {
    return CashTransfer.load({
      id: row.id,
      transferNumber: row.transferNumber,
      fromLocationId: row.fromLocationId,
      toLocationId: row.toLocationId,
      fromCashBoxId: row.fromCashBoxId ?? null,
      toCashBoxId: row.toCashBoxId ?? null,
      amount: toNumber(row.amount),
      currencyCode: row.currencyCode,
      transferDate: row.transferDate,
      expectedArrivalDate: row.expectedArrivalDate ?? null,
      actualArrivalDate: row.actualArrivalDate ?? null,
      status: row.status,
      sentById: row.sentById ?? null,
      receivedById: row.receivedById ?? null,
      reference: row.reference ?? null,
      notes: row.notes ?? null,
      postedToGL: row.postedToGL ?? false,
      glBatchId: row.glBatchId ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaPettyCashRepository implements PettyCashRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(fund: PettyCash): Promise<void> {
    const s = fund.toState();
    await this.prisma.pettyCash.upsert({
      where: { id: s.id },
      create: {
        ...s,
        fundBalance: toBigInt(s.fundBalance),
        maximumBalance: toBigInt(s.maximumBalance),
        minimumBalance: toBigInt(s.minimumBalance),
        replenishThreshold: toBigInt(s.replenishThreshold),
      } as any,
      update: {
        ...s,
        fundBalance: toBigInt(s.fundBalance),
        maximumBalance: toBigInt(s.maximumBalance),
        minimumBalance: toBigInt(s.minimumBalance),
        replenishThreshold: toBigInt(s.replenishThreshold),
      } as any,
    });
  }

  async findById(id: PettyCashId): Promise<PettyCash | null> {
    const row = await this.prisma.pettyCash.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByCode(fundCode: string): Promise<PettyCash | null> {
    const row = await this.prisma.pettyCash.findUnique({ where: { fundCode } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByLocation(locationId: string): Promise<PettyCash[]> {
    const rows = await this.prisma.pettyCash.findMany({ where: { locationId } });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<PettyCash[]> {
    const rows = await this.prisma.pettyCash.findMany();
    return rows.map(r => this.toDomain(r as any));
  }

  private toDomain(row: any): PettyCash {
    return PettyCash.load({
      id: row.id,
      locationId: row.locationId,
      fundCode: row.fundCode,
      fundName: row.fundName,
      fundBalance: toNumber(row.fundBalance),
      maximumBalance: toNumber(row.maximumBalance),
      minimumBalance: toNumber(row.minimumBalance),
      replenishThreshold: toNumber(row.replenishThreshold),
      currencyCode: row.currencyCode,
      holderId: row.holderId ?? null,
      status: row.status,
      description: row.description ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt ?? null,
    });
  }
}

@Injectable()
export class PrismaBankRepository implements BankRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(bank: Bank): Promise<void> {
    const s = bank.toState();
    await this.prisma.bank.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: BankId): Promise<Bank | null> {
    const row = await this.prisma.bank.findUnique({ where: { id: id.value } });
    return row ? Bank.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Bank | null> {
    const row = await this.prisma.bank.findUnique({ where: { code } });
    return row ? Bank.load(row as any) : null;
  }

  async findAll(): Promise<Bank[]> {
    const rows = await this.prisma.bank.findMany({ orderBy: { code: "asc" } });
    return rows.map(r => Bank.load(r as any));
  }

  async findActive(): Promise<Bank[]> {
    const rows = await this.prisma.bank.findMany({ where: { isActive: true }, orderBy: { code: "asc" } });
    return rows.map(r => Bank.load(r as any));
  }
}

@Injectable()
export class PrismaBankAccountRepository implements BankAccountRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(account: BankAccount): Promise<void> {
    const s = account.toState();
    await this.prisma.bankAccount.upsert({
      where: { id: s.id },
      create: {
        ...s,
        currentBalance: toBigInt(s.currentBalance),
        availableBalance: toBigInt(s.availableBalance),
        blockedBalance: toBigInt(s.blockedBalance),
      } as any,
      update: {
        ...s,
        currentBalance: toBigInt(s.currentBalance),
        availableBalance: toBigInt(s.availableBalance),
        blockedBalance: toBigInt(s.blockedBalance),
      } as any,
    });
  }

  async findById(id: BankAccountId): Promise<BankAccount | null> {
    const row = await this.prisma.bankAccount.findUnique({ where: { id: id.value } });
    return row ? BankAccount.load(row as any) : null;
  }

  async findByAccountNumber(accountNumber: string): Promise<BankAccount | null> {
    const row = await this.prisma.bankAccount.findFirst({ where: { accountNumber } });
    return row ? BankAccount.load(row as any) : null;
  }

  async findByBank(bankId: string): Promise<BankAccount[]> {
    const rows = await this.prisma.bankAccount.findMany({ where: { bankId } });
    return rows.map(r => BankAccount.load(r as any));
  }

  async findByCompany(companyId: string): Promise<BankAccount[]> {
    const rows = await this.prisma.bankAccount.findMany({ where: { companyId } });
    return rows.map(r => BankAccount.load(r as any));
  }

  async findActive(): Promise<BankAccount[]> {
    const rows = await this.prisma.bankAccount.findMany({ where: { status: "active" } });
    return rows.map(r => BankAccount.load(r as any));
  }

  async findAll(): Promise<BankAccount[]> {
    const rows = await this.prisma.bankAccount.findMany({ orderBy: { accountNumber: "asc" } });
    return rows.map(r => BankAccount.load(r as any));
  }
}

@Injectable()
export class PrismaChequeBookRepository implements ChequeBookRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(book: ChequeBook): Promise<void> {
    const s = book.toState();
    await this.prisma.chequeBook.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: ChequeBookId): Promise<ChequeBook | null> {
    const row = await this.prisma.chequeBook.findUnique({ where: { id: id.value } });
    return row ? ChequeBook.load(row as any) : null;
  }

  async findByBankAccount(bankAccountId: string): Promise<ChequeBook[]> {
    const rows = await this.prisma.chequeBook.findMany({ where: { bankAccountId } });
    return rows.map(r => ChequeBook.load(r as any));
  }

  async findByNumber(chequeBookNumber: string): Promise<ChequeBook | null> {
    const row = await this.prisma.chequeBook.findUnique({ where: { chequeBookNumber } });
    return row ? ChequeBook.load(row as any) : null;
  }

  async findAll(): Promise<ChequeBook[]> {
    const rows = await this.prisma.chequeBook.findMany({ orderBy: { chequeBookNumber: "asc" } });
    return rows.map(r => ChequeBook.load(r as any));
  }
}

@Injectable()
export class PrismaBankTransferRepository implements IBankTransferRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transfer: BankTransfer): Promise<void> {
    const s = transfer.toState();
    await this.prisma.bankTransfer.upsert({
      where: { id: s.id },
      create: {
        ...s,
        amount: toBigInt(s.amount),
        vndAmount: toBigInt(s.vndAmount),
        fees: toBigInt(s.fees),
      } as any,
      update: {
        ...s,
        amount: toBigInt(s.amount),
        vndAmount: toBigInt(s.vndAmount),
        fees: toBigInt(s.fees),
      } as any,
    });
  }

  async findById(id: BankTransferId): Promise<BankTransfer | null> {
    const row = await this.prisma.bankTransfer.findUnique({ where: { id: id.value } });
    return row ? BankTransfer.load(row as any) : null;
  }

  async findByNumber(transferNumber: string): Promise<BankTransfer | null> {
    const row = await this.prisma.bankTransfer.findUnique({ where: { transferNumber } });
    return row ? BankTransfer.load(row as any) : null;
  }

  async findByFromAccount(accountId: string): Promise<BankTransfer[]> {
    const rows = await this.prisma.bankTransfer.findMany({ where: { fromAccountId: accountId }, orderBy: { transferDate: "desc" } });
    return rows.map(r => BankTransfer.load(r as any));
  }

  async findByToAccount(accountId: string): Promise<BankTransfer[]> {
    const rows = await this.prisma.bankTransfer.findMany({ where: { toAccountId: accountId }, orderBy: { transferDate: "desc" } });
    return rows.map(r => BankTransfer.load(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<BankTransfer[]> {
    const rows = await this.prisma.bankTransfer.findMany({
      where: { transferDate: { gte: from, lte: to } },
      orderBy: { transferDate: "desc" },
    });
    return rows.map(r => BankTransfer.load(r as any));
  }

  async findAll(): Promise<BankTransfer[]> {
    const rows = await this.prisma.bankTransfer.findMany({ orderBy: { transferDate: "desc" } });
    return rows.map(r => BankTransfer.load(r as any));
  }
}

@Injectable()
export class PrismaBankStatementRepository implements BankStatementRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(statement: BankStatement): Promise<void> {
    const s = statement.toState();
    await this.prisma.bankStatement.upsert({
      where: { id: s.id },
      create: {
        ...s,
        openingBalance: toBigInt(s.openingBalance),
        closingBalance: toBigInt(s.closingBalance),
        totalDebit: toBigInt(s.totalDebit),
        totalCredit: toBigInt(s.totalCredit),
      } as any,
      update: {
        ...s,
        openingBalance: toBigInt(s.openingBalance),
        closingBalance: toBigInt(s.closingBalance),
        totalDebit: toBigInt(s.totalDebit),
        totalCredit: toBigInt(s.totalCredit),
      } as any,
    });
  }

  async findById(id: BankStatementId): Promise<BankStatement | null> {
    const row = await this.prisma.bankStatement.findUnique({ where: { id: id.value } });
    return row ? BankStatement.load(row as any) : null;
  }

  async findByBankAccount(bankAccountId: string): Promise<BankStatement[]> {
    const rows = await this.prisma.bankStatement.findMany({ where: { bankAccountId }, orderBy: { periodStart: "desc" } });
    return rows.map(r => BankStatement.load(r as any));
  }

  async findByNumber(statementNumber: string): Promise<BankStatement | null> {
    const row = await this.prisma.bankStatement.findFirst({ where: { statementNumber } });
    return row ? BankStatement.load(row as any) : null;
  }

  async findUnreconciled(bankAccountId: string): Promise<BankStatement[]> {
    const rows = await this.prisma.bankStatement.findMany({ where: { bankAccountId, isReconciled: false } });
    return rows.map(r => BankStatement.load(r as any));
  }

  async findAll(): Promise<BankStatement[]> {
    const rows = await this.prisma.bankStatement.findMany({ orderBy: { periodStart: "desc" } });
    return rows.map(r => BankStatement.load(r as any));
  }
}

@Injectable()
export class PrismaBankReconciliationRepository implements BankReconciliationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rec: BankReconciliation): Promise<void> {
    const s = rec.toState();
    await this.prisma.bankReconciliation.upsert({
      where: { id: s.id },
      create: {
        ...s,
        statementBalance: toBigInt(s.statementBalance),
        bookBalance: toBigInt(s.bookBalance),
        difference: toBigInt(s.difference),
      } as any,
      update: {
        ...s,
        statementBalance: toBigInt(s.statementBalance),
        bookBalance: toBigInt(s.bookBalance),
        difference: toBigInt(s.difference),
      } as any,
    });
  }

  async findById(id: BankReconciliationId): Promise<BankReconciliation | null> {
    const row = await this.prisma.bankReconciliation.findUnique({ where: { id: id.value } });
    return row ? BankReconciliation.load(row as any) : null;
  }

  async findByBankAccount(bankAccountId: string): Promise<BankReconciliation[]> {
    const rows = await this.prisma.bankReconciliation.findMany({ where: { bankAccountId }, orderBy: { reconciliationDate: "desc" } });
    return rows.map(r => BankReconciliation.load(r as any));
  }

  async findByStatus(status: BankReconciliationStatus): Promise<BankReconciliation[]> {
    const rows = await this.prisma.bankReconciliation.findMany({ where: { status } });
    return rows.map(r => BankReconciliation.load(r as any));
  }

  async findAll(): Promise<BankReconciliation[]> {
    const rows = await this.prisma.bankReconciliation.findMany({ orderBy: { reconciliationDate: "desc" } });
    return rows.map(r => BankReconciliation.load(r as any));
  }
}

@Injectable()
export class PrismaCashForecastRepository implements CashForecastRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(forecast: CashForecast): Promise<void> {
    const s = forecast.toState();
    await this.prisma.cashForecast.upsert({
      where: { id: s.id },
      create: {
        ...s,
        totalInflow: toBigInt(s.totalInflow),
        totalOutflow: toBigInt(s.totalOutflow),
        netFlow: toBigInt(s.netFlow),
        openingBalance: toBigInt(s.openingBalance),
        closingBalance: toBigInt(s.closingBalance),
      } as any,
      update: {
        ...s,
        totalInflow: toBigInt(s.totalInflow),
        totalOutflow: toBigInt(s.totalOutflow),
        netFlow: toBigInt(s.netFlow),
        openingBalance: toBigInt(s.openingBalance),
        closingBalance: toBigInt(s.closingBalance),
      } as any,
    });
  }

  async findById(id: CashForecastId): Promise<CashForecast | null> {
    const row = await this.prisma.cashForecast.findUnique({ where: { id: id.value } });
    return row ? CashForecast.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<CashForecast[]> {
    const rows = await this.prisma.cashForecast.findMany({ where: { companyId }, orderBy: { periodStart: "desc" } });
    return rows.map(r => CashForecast.load(r as any));
  }

  async findByDateRange(from: Date, to: Date): Promise<CashForecast[]> {
    const rows = await this.prisma.cashForecast.findMany({
      where: { periodStart: { gte: from }, periodEnd: { lte: to } },
      orderBy: { periodStart: "asc" },
    });
    return rows.map(r => CashForecast.load(r as any));
  }

  async findAll(): Promise<CashForecast[]> {
    const rows = await this.prisma.cashForecast.findMany({ orderBy: { periodStart: "desc" } });
    return rows.map(r => CashForecast.load(r as any));
  }
}

@Injectable()
export class PrismaLiquidityForecastRepository implements LiquidityForecastRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(forecast: LiquidityForecast): Promise<void> {
    const s = forecast.toState();
    await this.prisma.liquidityForecast.upsert({
      where: { id: s.id },
      create: {
        ...s,
        totalInflow: toBigInt(s.totalInflow),
        totalOutflow: toBigInt(s.totalOutflow),
        netLiquidity: toBigInt(s.netLiquidity),
        currentCash: toBigInt(s.currentCash),
        projectedCash: toBigInt(s.projectedCash),
        minimumRequired: toBigInt(s.minimumRequired),
        surplusDeficit: toBigInt(s.surplusDeficit),
      } as any,
      update: {
        ...s,
        totalInflow: toBigInt(s.totalInflow),
        totalOutflow: toBigInt(s.totalOutflow),
        netLiquidity: toBigInt(s.netLiquidity),
        currentCash: toBigInt(s.currentCash),
        projectedCash: toBigInt(s.projectedCash),
        minimumRequired: toBigInt(s.minimumRequired),
        surplusDeficit: toBigInt(s.surplusDeficit),
      } as any,
    });
  }

  async findById(id: LiquidityForecastId): Promise<LiquidityForecast | null> {
    const row = await this.prisma.liquidityForecast.findUnique({ where: { id: id.value } });
    return row ? LiquidityForecast.load(row as any) : null;
  }

  async findByCompany(companyId: string): Promise<LiquidityForecast[]> {
    const rows = await this.prisma.liquidityForecast.findMany({ where: { companyId }, orderBy: { forecastDate: "desc" } });
    return rows.map(r => LiquidityForecast.load(r as any));
  }

  async findAll(): Promise<LiquidityForecast[]> {
    const rows = await this.prisma.liquidityForecast.findMany({ orderBy: { forecastDate: "desc" } });
    return rows.map(r => LiquidityForecast.load(r as any));
  }
}
