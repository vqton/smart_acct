import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashReceiptId } from "./cm-ids.js";
import { ReceiptStatus, PaymentMethod } from "./cm-enums.js";
import { CashReceiptCreated, CashReceiptPosted, CashReceiptReversed } from "./cm-domain-events.js";

export interface CashReceiptState {
  id: string;
  receiptNumber: string;
  receiptDate: Date;
  cashBoxId: string;
  sessionId: string | null;
  cashierId: string;
  amount: number;
  currencyCode: string;
  exchangeRate: number;
  vndAmount: number;
  paidBy: string | null;
  paidById: string | null;
  paymentMethod: string;
  reference: string | null;
  description: string | null;
  status: string;
  approvedById: string | null;
  approvedAt: Date | null;
  postedById: string | null;
  postedAt: Date | null;
  reversedById: string | null;
  reversedAt: Date | null;
  reversalReason: string | null;
  glBatchId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashReceipt extends AggregateRoot<CashReceiptId> {
  private _id: CashReceiptId;
  private _receiptNumber: string;
  private _receiptDate: Date;
  private _cashBoxId: string;
  private _sessionId: string | null;
  private _cashierId: string;
  private _amount: number;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _vndAmount: number;
  private _paidBy: string | null;
  private _paidById: string | null;
  private _paymentMethod: PaymentMethod;
  private _reference: string | null;
  private _description: string | null;
  private _status: ReceiptStatus;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _postedById: string | null;
  private _postedAt: Date | null;
  private _reversedById: string | null;
  private _reversedAt: Date | null;
  private _reversalReason: string | null;
  private _glBatchId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: CashReceiptId,
    receiptNumber: string,
    receiptDate: Date,
    cashBoxId: string,
    cashierId: string,
    amount: number,
    currencyCode: string,
    paymentMethod: PaymentMethod,
    sessionId: string | null = null,
  ) {
    super();
    if (amount <= 0) throw new DomainError("BusinessRule", "Receipt amount must be positive");
    this._id = id;
    this._receiptNumber = receiptNumber;
    this._receiptDate = receiptDate;
    this._cashBoxId = cashBoxId;
    this._cashierId = cashierId;
    this._amount = amount;
    this._currencyCode = currencyCode;
    this._exchangeRate = 1;
    this._vndAmount = amount;
    this._paidBy = null;
    this._paidById = null;
    this._paymentMethod = paymentMethod;
    this._sessionId = sessionId;
    this._reference = null;
    this._description = null;
    this._status = ReceiptStatus.Draft;
    this._approvedById = null;
    this._approvedAt = null;
    this._postedById = null;
    this._postedAt = null;
    this._reversedById = null;
    this._reversedAt = null;
    this._reversalReason = null;
    this._glBatchId = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    receiptNumber: string;
    receiptDate: Date;
    cashBoxId: string;
    cashierId: string;
    amount: number;
    currencyCode?: string;
    paymentMethod?: PaymentMethod;
    sessionId?: string | null;
    paidBy?: string | null;
    paidById?: string | null;
    reference?: string | null;
    description?: string | null;
    exchangeRate?: number;
  }): CashReceipt {
    const r = new CashReceipt(
      CashReceiptId.new(),
      params.receiptNumber,
      params.receiptDate,
      params.cashBoxId,
      params.cashierId,
      params.amount,
      params.currencyCode ?? "VND",
      params.paymentMethod ?? PaymentMethod.Cash,
      params.sessionId ?? null,
    );
    r._paidBy = params.paidBy ?? null;
    r._paidById = params.paidById ?? null;
    r._reference = params.reference ?? null;
    r._description = params.description ?? null;
    if (params.exchangeRate && params.exchangeRate !== 1) {
      if (!params.currencyCode || params.currencyCode === "VND") {
        throw new DomainError("BusinessRule", "Exchange rate only applicable for foreign currency");
      }
      r._exchangeRate = params.exchangeRate;
      r._vndAmount = Math.round(params.amount * params.exchangeRate);
    }
    r.addEvent(new CashReceiptCreated(r._id.value, new Date(), {
      receiptNumber: params.receiptNumber,
      amount: params.amount,
      cashierId: params.cashierId,
    }));
    return r;
  }

  static load(state: CashReceiptState): CashReceipt {
    const r = new CashReceipt(
      new CashReceiptId(state.id),
      state.receiptNumber,
      state.receiptDate,
      state.cashBoxId,
      state.cashierId,
      state.amount,
      state.currencyCode,
      state.paymentMethod as PaymentMethod,
      state.sessionId,
    );
    r._exchangeRate = state.exchangeRate;
    r._vndAmount = state.vndAmount;
    r._paidBy = state.paidBy;
    r._paidById = state.paidById;
    r._reference = state.reference;
    r._description = state.description;
    r._status = state.status as ReceiptStatus;
    r._approvedById = state.approvedById;
    r._approvedAt = state.approvedAt;
    r._postedById = state.postedById;
    r._postedAt = state.postedAt;
    r._reversedById = state.reversedById;
    r._reversedAt = state.reversedAt;
    r._reversalReason = state.reversalReason;
    r._glBatchId = state.glBatchId;
    r._version = state.version;
    r._createdAt = state.createdAt;
    r._updatedAt = state.updatedAt;
    r._deletedAt = state.deletedAt;
    return r;
  }

  get id(): CashReceiptId { return this._id; }
  get receiptNumber(): string { return this._receiptNumber; }
  get receiptDate(): Date { return this._receiptDate; }
  get cashBoxId(): string { return this._cashBoxId; }
  get sessionId(): string | null { return this._sessionId; }
  get cashierId(): string { return this._cashierId; }
  get amount(): number { return this._amount; }
  get currencyCode(): string { return this._currencyCode; }
  get exchangeRate(): number { return this._exchangeRate; }
  get vndAmount(): number { return this._vndAmount; }
  get paidBy(): string | null { return this._paidBy; }
  get paidById(): string | null { return this._paidById; }
  get paymentMethod(): PaymentMethod { return this._paymentMethod; }
  get reference(): string | null { return this._reference; }
  get description(): string | null { return this._description; }
  get status(): ReceiptStatus { return this._status; }
  get approvedById(): string | null { return this._approvedById; }
  get postedById(): string | null { return this._postedById; }
  get glBatchId(): string | null { return this._glBatchId; }
  get version(): number { return this._version; }

  approve(userId: string): void {
    if (this._status !== ReceiptStatus.Draft && this._status !== ReceiptStatus.Issued) {
      throw new DomainError("BusinessRule", "Only draft receipts can be approved");
    }
    this._status = ReceiptStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  post(userId: string): void {
    if (this._status !== ReceiptStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved receipts can be posted");
    }
    this._status = ReceiptStatus.Posted;
    this._postedById = userId;
    this._postedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashReceiptPosted(this._id.value, new Date(), {
      receiptNumber: this._receiptNumber,
      amount: this._amount,
      vndAmount: this._vndAmount,
      cashBoxId: this._cashBoxId,
    }));
  }

  reverse(userId: string, reason: string): void {
    if (this._status !== ReceiptStatus.Posted) {
      throw new DomainError("BusinessRule", "Only posted receipts can be reversed");
    }
    this._status = ReceiptStatus.Reversed;
    this._reversedById = userId;
    this._reversedAt = new Date();
    this._reversalReason = reason;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashReceiptReversed(this._id.value, new Date(), {
      receiptNumber: this._receiptNumber,
      amount: this._amount,
      reason,
    }));
  }

  cancel(): void {
    if (this._status !== ReceiptStatus.Draft && this._status !== ReceiptStatus.Issued) {
      throw new DomainError("BusinessRule", "Only draft receipts can be cancelled");
    }
    this._status = ReceiptStatus.Cancelled;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CashReceiptState {
    return {
      id: this._id.value,
      receiptNumber: this._receiptNumber,
      receiptDate: this._receiptDate,
      cashBoxId: this._cashBoxId,
      sessionId: this._sessionId,
      cashierId: this._cashierId,
      amount: this._amount,
      currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      vndAmount: this._vndAmount,
      paidBy: this._paidBy,
      paidById: this._paidById,
      paymentMethod: this._paymentMethod,
      reference: this._reference,
      description: this._description,
      status: this._status,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      postedById: this._postedById,
      postedAt: this._postedAt,
      reversedById: this._reversedById,
      reversedAt: this._reversedAt,
      reversalReason: this._reversalReason,
      glBatchId: this._glBatchId,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
