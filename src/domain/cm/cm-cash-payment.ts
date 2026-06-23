import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashPaymentId } from "./cm-ids.js";
import { PaymentStatus, PaymentMethod } from "./cm-enums.js";
import { CashPaymentCreated, CashPaymentPosted, CashPaymentReversed } from "./cm-domain-events.js";

export interface CashPaymentState {
  id: string;
  paymentNumber: string;
  paymentDate: Date;
  cashBoxId: string;
  sessionId: string | null;
  cashierId: string;
  payeeName: string;
  payeeId: string | null;
  amount: number;
  currencyCode: string;
  exchangeRate: number;
  vndAmount: number;
  paymentMethod: string;
  reference: string | null;
  description: string | null;
  status: string;
  approvedById: string | null;
  approvedAt: Date | null;
  paidById: string | null;
  paidAt: Date | null;
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

export class CashPayment extends AggregateRoot<CashPaymentId> {
  private _id: CashPaymentId;
  private _paymentNumber: string;
  private _paymentDate: Date;
  private _cashBoxId: string;
  private _sessionId: string | null;
  private _cashierId: string;
  private _payeeName: string;
  private _payeeId: string | null;
  private _amount: number;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _vndAmount: number;
  private _paymentMethod: PaymentMethod;
  private _reference: string | null;
  private _description: string | null;
  private _status: PaymentStatus;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _paidById: string | null;
  private _paidAt: Date | null;
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
    id: CashPaymentId,
    paymentNumber: string,
    paymentDate: Date,
    cashBoxId: string,
    cashierId: string,
    payeeName: string,
    amount: number,
    currencyCode: string,
    paymentMethod: PaymentMethod,
    sessionId: string | null = null,
  ) {
    super();
    if (amount <= 0) throw new DomainError("BusinessRule", "Payment amount must be positive");
    this._id = id;
    this._paymentNumber = paymentNumber;
    this._paymentDate = paymentDate;
    this._cashBoxId = cashBoxId;
    this._cashierId = cashierId;
    this._payeeName = payeeName;
    this._payeeId = null;
    this._amount = amount;
    this._currencyCode = currencyCode;
    this._exchangeRate = 1;
    this._vndAmount = amount;
    this._paymentMethod = paymentMethod;
    this._sessionId = sessionId;
    this._reference = null;
    this._description = null;
    this._status = PaymentStatus.Draft;
    this._approvedById = null;
    this._approvedAt = null;
    this._paidById = null;
    this._paidAt = null;
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
    paymentNumber: string;
    paymentDate: Date;
    cashBoxId: string;
    cashierId: string;
    payeeName: string;
    amount: number;
    currencyCode?: string;
    paymentMethod?: PaymentMethod;
    sessionId?: string | null;
    payeeId?: string | null;
    reference?: string | null;
    description?: string | null;
    exchangeRate?: number;
  }): CashPayment {
    const p = new CashPayment(
      CashPaymentId.new(),
      params.paymentNumber,
      params.paymentDate,
      params.cashBoxId,
      params.cashierId,
      params.payeeName,
      params.amount,
      params.currencyCode ?? "VND",
      params.paymentMethod ?? PaymentMethod.Cash,
      params.sessionId ?? null,
    );
    p._payeeId = params.payeeId ?? null;
    p._reference = params.reference ?? null;
    p._description = params.description ?? null;
    if (params.exchangeRate && params.exchangeRate !== 1) {
      if (!params.currencyCode || params.currencyCode === "VND") {
        throw new DomainError("BusinessRule", "Exchange rate only applicable for foreign currency");
      }
      p._exchangeRate = params.exchangeRate;
      p._vndAmount = Math.round(params.amount * params.exchangeRate);
    }
    p.addEvent(new CashPaymentCreated(p._id.value, new Date(), {
      paymentNumber: params.paymentNumber,
      amount: params.amount,
      payeeName: params.payeeName,
    }));
    return p;
  }

  static load(state: CashPaymentState): CashPayment {
    const p = new CashPayment(
      new CashPaymentId(state.id),
      state.paymentNumber,
      state.paymentDate,
      state.cashBoxId,
      state.cashierId,
      state.payeeName,
      state.amount,
      state.currencyCode,
      state.paymentMethod as PaymentMethod,
      state.sessionId,
    );
    p._exchangeRate = state.exchangeRate;
    p._vndAmount = state.vndAmount;
    p._payeeId = state.payeeId;
    p._reference = state.reference;
    p._description = state.description;
    p._status = state.status as PaymentStatus;
    p._approvedById = state.approvedById;
    p._approvedAt = state.approvedAt;
    p._paidById = state.paidById;
    p._paidAt = state.paidAt;
    p._postedById = state.postedById;
    p._postedAt = state.postedAt;
    p._reversedById = state.reversedById;
    p._reversedAt = state.reversedAt;
    p._reversalReason = state.reversalReason;
    p._glBatchId = state.glBatchId;
    p._version = state.version;
    p._createdAt = state.createdAt;
    p._updatedAt = state.updatedAt;
    p._deletedAt = state.deletedAt;
    return p;
  }

  get id(): CashPaymentId { return this._id; }
  get paymentNumber(): string { return this._paymentNumber; }
  get paymentDate(): Date { return this._paymentDate; }
  get cashBoxId(): string { return this._cashBoxId; }
  get sessionId(): string | null { return this._sessionId; }
  get cashierId(): string { return this._cashierId; }
  get payeeName(): string { return this._payeeName; }
  get payeeId(): string | null { return this._payeeId; }
  get amount(): number { return this._amount; }
  get currencyCode(): string { return this._currencyCode; }
  get exchangeRate(): number { return this._exchangeRate; }
  get vndAmount(): number { return this._vndAmount; }
  get paymentMethod(): PaymentMethod { return this._paymentMethod; }
  get reference(): string | null { return this._reference; }
  get description(): string | null { return this._description; }
  get status(): PaymentStatus { return this._status; }
  get approvedById(): string | null { return this._approvedById; }
  get postedById(): string | null { return this._postedById; }
  get glBatchId(): string | null { return this._glBatchId; }
  get version(): number { return this._version; }

  submit(): void {
    if (this._status !== PaymentStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft payments can be submitted");
    }
    this._status = PaymentStatus.Submitted;
    this._updatedAt = new Date();
    this._version++;
  }

  approve(userId: string): void {
    if (this._status !== PaymentStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only submitted payments can be approved");
    }
    this._status = PaymentStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  reject(reason: string): void {
    if (this._status !== PaymentStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only submitted payments can be rejected");
    }
    this._status = PaymentStatus.Rejected;
    this._description = reason;
    this._updatedAt = new Date();
    this._version++;
  }

  pay(userId: string): void {
    if (this._status !== PaymentStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved payments can be paid");
    }
    this._status = PaymentStatus.Paid;
    this._paidById = userId;
    this._paidAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  post(userId: string): void {
    if (this._status !== PaymentStatus.Paid) {
      throw new DomainError("BusinessRule", "Only paid payments can be posted");
    }
    this._status = PaymentStatus.Posted;
    this._postedById = userId;
    this._postedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashPaymentPosted(this._id.value, new Date(), {
      paymentNumber: this._paymentNumber,
      amount: this._amount,
      vndAmount: this._vndAmount,
      cashBoxId: this._cashBoxId,
    }));
  }

  reverse(userId: string, reason: string): void {
    if (this._status !== PaymentStatus.Posted) {
      throw new DomainError("BusinessRule", "Only posted payments can be reversed");
    }
    this._status = PaymentStatus.Reversed;
    this._reversedById = userId;
    this._reversedAt = new Date();
    this._reversalReason = reason;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashPaymentReversed(this._id.value, new Date(), {
      paymentNumber: this._paymentNumber,
      amount: this._amount,
      reason,
    }));
  }

  cancel(): void {
    if (this._status !== PaymentStatus.Draft && this._status !== PaymentStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only draft or submitted payments can be cancelled");
    }
    this._status = PaymentStatus.Cancelled;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CashPaymentState {
    return {
      id: this._id.value,
      paymentNumber: this._paymentNumber,
      paymentDate: this._paymentDate,
      cashBoxId: this._cashBoxId,
      sessionId: this._sessionId,
      cashierId: this._cashierId,
      payeeName: this._payeeName,
      payeeId: this._payeeId,
      amount: this._amount,
      currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      vndAmount: this._vndAmount,
      paymentMethod: this._paymentMethod,
      reference: this._reference,
      description: this._description,
      status: this._status,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      paidById: this._paidById,
      paidAt: this._paidAt,
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
