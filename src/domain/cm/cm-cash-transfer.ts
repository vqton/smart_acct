import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashTransferId } from "./cm-ids.js";
import { CashTransferStatus } from "./cm-enums.js";
import { CashTransferCompleted } from "./cm-domain-events.js";

export interface CashTransferState {
  id: string;
  transferNumber: string;
  fromLocationId: string;
  toLocationId: string;
  fromCashBoxId: string | null;
  toCashBoxId: string | null;
  amount: number;
  currencyCode: string;
  transferDate: Date;
  expectedArrivalDate: Date | null;
  actualArrivalDate: Date | null;
  status: string;
  sentById: string | null;
  receivedById: string | null;
  reference: string | null;
  notes: string | null;
  postedToGL: boolean;
  glBatchId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashTransfer extends AggregateRoot<CashTransferId> {
  private _id: CashTransferId;
  private _transferNumber: string;
  private _fromLocationId: string;
  private _toLocationId: string;
  private _fromCashBoxId: string | null;
  private _toCashBoxId: string | null;
  private _amount: number;
  private _currencyCode: string;
  private _transferDate: Date;
  private _expectedArrivalDate: Date | null;
  private _actualArrivalDate: Date | null;
  private _status: CashTransferStatus;
  private _sentById: string | null;
  private _receivedById: string | null;
  private _reference: string | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: CashTransferId,
    transferNumber: string,
    fromLocationId: string,
    toLocationId: string,
    amount: number,
    transferDate: Date,
    currencyCode: string,
    fromCashBoxId: string | null = null,
    toCashBoxId: string | null = null,
  ) {
    super();
    if (fromLocationId === toLocationId) {
      throw new DomainError("BusinessRule", "Source and destination must be different");
    }
    if (amount <= 0) throw new DomainError("BusinessRule", "Transfer amount must be positive");
    this._id = id;
    this._transferNumber = transferNumber;
    this._fromLocationId = fromLocationId;
    this._toLocationId = toLocationId;
    this._fromCashBoxId = fromCashBoxId;
    this._toCashBoxId = toCashBoxId;
    this._amount = amount;
    this._currencyCode = currencyCode;
    this._transferDate = transferDate;
    this._expectedArrivalDate = null;
    this._actualArrivalDate = null;
    this._status = CashTransferStatus.Draft;
    this._sentById = null;
    this._receivedById = null;
    this._reference = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    transferNumber: string;
    fromLocationId: string;
    toLocationId: string;
    amount: number;
    transferDate: Date;
    currencyCode?: string;
    fromCashBoxId?: string | null;
    toCashBoxId?: string | null;
    reference?: string | null;
    notes?: string | null;
  }): CashTransfer {
    const t = new CashTransfer(
      CashTransferId.new(),
      params.transferNumber,
      params.fromLocationId,
      params.toLocationId,
      params.amount,
      params.transferDate,
      params.currencyCode ?? "VND",
      params.fromCashBoxId ?? null,
      params.toCashBoxId ?? null,
    );
    t._reference = params.reference ?? null;
    t._notes = params.notes ?? null;
    return t;
  }

  static load(state: CashTransferState): CashTransfer {
    const t = new CashTransfer(
      new CashTransferId(state.id),
      state.transferNumber,
      state.fromLocationId,
      state.toLocationId,
      state.amount,
      state.transferDate,
      state.currencyCode,
      state.fromCashBoxId,
      state.toCashBoxId,
    );
    t._expectedArrivalDate = state.expectedArrivalDate;
    t._actualArrivalDate = state.actualArrivalDate;
    t._status = state.status as CashTransferStatus;
    t._sentById = state.sentById;
    t._receivedById = state.receivedById;
    t._reference = state.reference;
    t._notes = state.notes;
    t._version = state.version;
    t._createdAt = state.createdAt;
    t._updatedAt = state.updatedAt;
    t._deletedAt = state.deletedAt;
    return t;
  }

  get id(): CashTransferId { return this._id; }
  get transferNumber(): string { return this._transferNumber; }
  get fromLocationId(): string { return this._fromLocationId; }
  get toLocationId(): string { return this._toLocationId; }
  get fromCashBoxId(): string | null { return this._fromCashBoxId; }
  get toCashBoxId(): string | null { return this._toCashBoxId; }
  get amount(): number { return this._amount; }
  get currencyCode(): string { return this._currencyCode; }
  get transferDate(): Date { return this._transferDate; }
  get status(): CashTransferStatus { return this._status; }
  get sentById(): string | null { return this._sentById; }
  get receivedById(): string | null { return this._receivedById; }
  get reference(): string | null { return this._reference; }
  get notes(): string | null { return this._notes; }
  get actualArrivalDate(): Date | null { return this._actualArrivalDate; }
  get version(): number { return this._version; }

  approve(userId: string): void {
    if (this._status !== CashTransferStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft transfers can be approved");
    }
    this._status = CashTransferStatus.Approved;
    this._version++;
    this._updatedAt = new Date();
  }

  send(userId: string): void {
    if (this._status !== CashTransferStatus.Approved) {
      throw new DomainError("BusinessRule", "Transfer must be approved before sending");
    }
    this._status = CashTransferStatus.InTransit;
    this._sentById = userId;
    this._version++;
    this._updatedAt = new Date();
  }

  receive(userId: string): void {
    if (this._status !== CashTransferStatus.InTransit) {
      throw new DomainError("BusinessRule", "Transfer must be in transit to receive");
    }
    this._status = CashTransferStatus.Completed;
    this._receivedById = userId;
    this._actualArrivalDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new CashTransferCompleted(this._id.value, new Date(), {
      transferNumber: this._transferNumber,
      amount: this._amount,
      fromLocation: this._fromLocationId,
      toLocation: this._toLocationId,
    }));
  }

  cancel(reason: string): void {
    if (this._status === CashTransferStatus.Completed) {
      throw new DomainError("BusinessRule", "Cannot cancel completed transfer");
    }
    this._status = CashTransferStatus.Cancelled;
    this._notes = reason;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): CashTransferState {
    return {
      id: this._id.value,
      transferNumber: this._transferNumber,
      fromLocationId: this._fromLocationId,
      toLocationId: this._toLocationId,
      fromCashBoxId: this._fromCashBoxId,
      toCashBoxId: this._toCashBoxId,
      amount: this._amount,
      currencyCode: this._currencyCode,
      transferDate: this._transferDate,
      expectedArrivalDate: this._expectedArrivalDate,
      actualArrivalDate: this._actualArrivalDate,
      status: this._status,
      sentById: this._sentById,
      receivedById: this._receivedById,
      reference: this._reference,
      notes: this._notes,
      postedToGL: false,
      glBatchId: null,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
