import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PrismaCashBoxRepository, PrismaCashSessionRepository, PrismaCashReceiptRepository, PrismaCashPaymentRepository } from "../../infrastructure/cm/cm-prisma-repos.js";
import { CashBox } from "../../domain/cm/cm-cash-box.js";
import { CashSession } from "../../domain/cm/cm-session.js";
import { CashReceipt } from "../../domain/cm/cm-cash-receipt.js";
import { CashPayment } from "../../domain/cm/cm-cash-payment.js";
import { CashBoxId, CashSessionId, CashReceiptId, CashPaymentId } from "../../domain/cm/cm-ids.js";
import { CashBoxType, PaymentMethod, ReceiptStatus, PaymentStatus } from "../../domain/cm/cm-enums.js";

export interface OpenSessionCommand {
  cashBoxId: string;
  cashierId: string;
  openedBalance?: number;
  currencyCode?: string;
  cashRegisterId?: string | null;
}

export interface CreateReceiptCommand {
  receiptNumber: string;
  receiptDate: Date;
  cashBoxId: string;
  cashierId: string;
  amount: number;
  currencyCode?: string;
  paymentMethod?: PaymentMethod;
  sessionId?: string | null;
  paidBy?: string | null;
  reference?: string | null;
  description?: string | null;
}

export interface CreatePaymentCommand {
  paymentNumber: string;
  paymentDate: Date;
  cashBoxId: string;
  cashierId: string;
  payeeName: string;
  amount: number;
  currencyCode?: string;
  paymentMethod?: PaymentMethod;
  sessionId?: string | null;
  reference?: string | null;
  description?: string | null;
}

export interface CloseSessionCommand {
  sessionId: string;
  countedBalance: number;
  notes?: string;
}

@Injectable()
export class CashBoxService {
  constructor(
    private readonly boxRepo: PrismaCashBoxRepository,
    private readonly sessionRepo: PrismaCashSessionRepository,
    private readonly receiptRepo: PrismaCashReceiptRepository,
    private readonly paymentRepo: PrismaCashPaymentRepository,
  ) {}

  async createBox(params: {
    locationId: string;
    code: string;
    name: string;
    boxType: CashBoxType;
    currencyCode?: string;
    minBalance?: number;
    maxBalance?: number | null;
    allowNegative?: boolean;
    description?: string | null;
  }): Promise<CashBox> {
    const box = CashBox.create(params);
    await this.boxRepo.save(box);
    return box;
  }

  async openSession(cmd: OpenSessionCommand): Promise<CashSession> {
    const existing = await this.sessionRepo.findOpenByCashBox(cmd.cashBoxId);
    if (existing) throw new DomainError("BusinessRule", "An open session already exists for this cash box");

    const sessionNumber = `CS${Date.now()}`;
    const session = CashSession.create({
      sessionNumber,
      cashBoxId: cmd.cashBoxId,
      cashierId: cmd.cashierId,
      openedBalance: cmd.openedBalance ?? 0,
      currencyCode: cmd.currencyCode ?? "VND",
      cashRegisterId: cmd.cashRegisterId ?? null,
    });
    session.open();
    await this.sessionRepo.save(session);
    return session;
  }

  async closeSession(cmd: CloseSessionCommand): Promise<CashSession> {
    const session = await this.sessionRepo.findById(new CashSessionId(cmd.sessionId));
    if (!session) throw new DomainError("NotFound", "Session not found");
    session.countCash(cmd.countedBalance);
    session.close(cmd.notes);
    await this.sessionRepo.save(session);
    return session;
  }

  async recordReceipt(cmd: CreateReceiptCommand): Promise<CashReceipt> {
    const box = await this.boxRepo.findById(new CashBoxId(cmd.cashBoxId));
    if (!box) throw new DomainError("NotFound", "Cash box not found");
    box.canAcceptTransaction();

    let session: CashSession | null = null;
    if (cmd.sessionId) {
      session = await this.sessionRepo.findById(new CashSessionId(cmd.sessionId));
      if (!session) throw new DomainError("NotFound", "Session not found");
    }

    const receipt = CashReceipt.create({
      ...cmd,
      currencyCode: cmd.currencyCode ?? "VND",
      paymentMethod: cmd.paymentMethod ?? PaymentMethod.Cash,
    });
    receipt.approve(cmd.cashierId);
    receipt.post(cmd.cashierId);

    box.deposit(cmd.amount, receipt.receiptNumber);
    if (session) session.addReceipt(cmd.amount);

    await this.boxRepo.save(box);
    if (session) await this.sessionRepo.save(session);
    await this.receiptRepo.save(receipt);
    return receipt;
  }

  async recordPayment(cmd: CreatePaymentCommand): Promise<CashPayment> {
    const box = await this.boxRepo.findById(new CashBoxId(cmd.cashBoxId));
    if (!box) throw new DomainError("NotFound", "Cash box not found");
    box.canAcceptTransaction();

    let session: CashSession | null = null;
    if (cmd.sessionId) {
      session = await this.sessionRepo.findById(new CashSessionId(cmd.sessionId));
      if (!session) throw new DomainError("NotFound", "Session not found");
    }

    const payment = CashPayment.create({
      ...cmd,
      currencyCode: cmd.currencyCode ?? "VND",
      paymentMethod: cmd.paymentMethod ?? PaymentMethod.Cash,
    });
    payment.submit();
    payment.approve(cmd.cashierId);
    payment.pay(cmd.cashierId);
    payment.post(cmd.cashierId);

    box.withdraw(cmd.amount, payment.paymentNumber);
    if (session) session.addPayment(cmd.amount);

    await this.boxRepo.save(box);
    if (session) await this.sessionRepo.save(session);
    await this.paymentRepo.save(payment);
    return payment;
  }

  async getCashPosition(locationId: string) {
    const boxes = await this.boxRepo.findByLocation(locationId);
    return boxes
      .filter(b => b.status === "active")
      .map(b => ({
        cashBoxId: b.id.value,
        cashBoxCode: b.code,
        cashBoxName: b.name,
        balance: b.currentBalance,
        currency: b.currencyCode,
      }));
  }
}
