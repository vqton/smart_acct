import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxPaymentId extends Identifier {
  static new(): TaxPaymentId { return new TaxPaymentId(IdGenerator.uuid()); }
}

export enum TaxPaymentStatus {
  Pending = "pending",
  Completed = "completed",
  Failed = "failed",
  PartiallyRefunded = "partially_refunded",
  FullyRefunded = "fully_refunded",
}

export enum TaxPaymentMethod {
  BankTransfer = "bank_transfer",
  Cash = "cash",
  Cheque = "cheque",
  Electronic = "electronic",
  Offset = "offset",
  Other = "other",
}

export class PaymentCompleted implements DomainEvent {
  readonly eventName = "PaymentCompleted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PaymentFailed implements DomainEvent {
  readonly eventName = "PaymentFailed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PaymentRefunded implements DomainEvent {
  readonly eventName = "PaymentRefunded";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export interface TaxPaymentState {
  id: string;
  taxReturnId: string;
  taxpayerId: string;
  taxTypeId: string;
  amount: number;
  status: TaxPaymentStatus;
  paymentMethod: TaxPaymentMethod;
  paymentDate: Date;
  referenceNumber: string;
  paidById: string;
  description: string | null;
  refundAmount: number;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxPayment extends AggregateRoot<TaxPaymentId> {
  private _id: TaxPaymentId;
  private _taxReturnId!: string;
  private _taxpayerId!: string;
  private _taxTypeId!: string;
  private _amount!: number;
  private _status: TaxPaymentStatus;
  private _paymentMethod!: TaxPaymentMethod;
  private _paymentDate!: Date;
  private _referenceNumber!: string;
  private _paidById!: string;
  private _description: string | null;
  private _refundAmount: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  private constructor(id: TaxPaymentId) {
    super();
    this._id = id;
    this._status = TaxPaymentStatus.Pending;
    this._description = null;
    this._refundAmount = 0;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static create(params: {
    taxReturnId: string;
    taxpayerId: string;
    taxTypeId: string;
    amount: number;
    paymentMethod: TaxPaymentMethod;
    paymentDate: Date;
    referenceNumber: string;
    paidById: string;
    description?: string;
  }): TaxPayment {
    if (params.amount <= 0) throw new DomainError("Validation", "Payment amount must be positive");
    const p = new TaxPayment(TaxPaymentId.new());
    p._taxReturnId = params.taxReturnId;
    p._taxpayerId = params.taxpayerId;
    p._taxTypeId = params.taxTypeId;
    p._amount = params.amount;
    p._paymentMethod = params.paymentMethod;
    p._paymentDate = params.paymentDate;
    p._referenceNumber = params.referenceNumber;
    p._paidById = params.paidById;
    p._description = params.description ?? null;
    return p;
  }

  static load(s: TaxPaymentState): TaxPayment {
    const p = new TaxPayment(new TaxPaymentId(s.id));
    p._taxReturnId = s.taxReturnId;
    p._taxpayerId = s.taxpayerId;
    p._taxTypeId = s.taxTypeId;
    p._amount = s.amount;
    p._status = s.status;
    p._paymentMethod = s.paymentMethod;
    p._paymentDate = s.paymentDate;
    p._referenceNumber = s.referenceNumber;
    p._paidById = s.paidById;
    p._description = s.description;
    p._refundAmount = s.refundAmount;
    p._createdAt = s.createdAt;
    p._updatedAt = s.updatedAt;
    p._version = s.version;
    return p;
  }

  get id() { return this._id; }
  get taxReturnId() { return this._taxReturnId; }
  get taxpayerId() { return this._taxpayerId; }
  get taxTypeId() { return this._taxTypeId; }
  get amount() { return this._amount; }
  get status() { return this._status; }
  get paymentMethod() { return this._paymentMethod; }
  get paymentDate() { return this._paymentDate; }
  get referenceNumber() { return this._referenceNumber; }
  get paidById() { return this._paidById; }
  get refundAmount() { return this._refundAmount; }
  get version() { return this._version; }

  complete(confirmationCode?: string): void {
    if (this._status !== TaxPaymentStatus.Pending) {
      throw new DomainError("BusinessRule", "Only pending payments can be completed");
    }
    this._status = TaxPaymentStatus.Completed;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new PaymentCompleted(this._id.value, new Date(), {
      taxReturnId: this._taxReturnId,
      amount: this._amount,
      confirmationCode: confirmationCode ?? null,
    }));
  }

  fail(reason: string): void {
    if (this._status !== TaxPaymentStatus.Pending) {
      throw new DomainError("BusinessRule", "Only pending payments can be marked as failed");
    }
    this._status = TaxPaymentStatus.Failed;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new PaymentFailed(this._id.value, new Date(), {
      taxReturnId: this._taxReturnId,
      amount: this._amount,
      reason,
    }));
  }

  refund(amount: number, reason: string): void {
    if (this._status !== TaxPaymentStatus.Completed) {
      throw new DomainError("BusinessRule", "Only completed payments can be refunded");
    }
    if (amount <= 0) throw new DomainError("Validation", "Refund amount must be positive");
    if (amount > this._amount - this._refundAmount) {
      throw new DomainError("Validation", "Refund amount exceeds remaining payment balance");
    }
    this._refundAmount += amount;
    this._status = this._refundAmount >= this._amount
      ? TaxPaymentStatus.FullyRefunded
      : TaxPaymentStatus.PartiallyRefunded;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new PaymentRefunded(this._id.value, new Date(), {
      taxReturnId: this._taxReturnId,
      refundAmount: amount,
      totalRefunded: this._refundAmount,
      reason,
    }));
  }

  toState(): TaxPaymentState {
    return {
      id: this._id.value,
      taxReturnId: this._taxReturnId,
      taxpayerId: this._taxpayerId,
      taxTypeId: this._taxTypeId,
      amount: this._amount,
      status: this._status,
      paymentMethod: this._paymentMethod,
      paymentDate: this._paymentDate,
      referenceNumber: this._referenceNumber,
      paidById: this._paidById,
      description: this._description,
      refundAmount: this._refundAmount,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
