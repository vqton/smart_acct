import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankTransferId } from "./cm-ids.js";
import { BankTransferType, BankTransferStatus } from "./cm-enums.js";
import { BankTransferCompleted } from "./cm-domain-events.js";

export interface BankTransferState {
  id: string;
  transferNumber: string;
  transferType: string;
  fromAccountId: string;
  toAccountId: string;
  amount: number;
  currencyCode: string;
  exchangeRate: number;
  vndAmount: number;
  transferDate: Date;
  valueDate: Date | null;
  reference: string | null;
  swiftMessage: string | null;
  beneficiaryName: string | null;
  beneficiaryBank: string | null;
  beneficiaryAccount: string | null;
  intermediaryBank: string | null;
  fees: number;
  status: string;
  approvedById: string | null;
  approvedAt: Date | null;
  executedById: string | null;
  executedAt: Date | null;
  completedAt: Date | null;
  failureReason: string | null;
  notes: string | null;
  postedToGL: boolean;
  glBatchId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class BankTransfer extends AggregateRoot<BankTransferId> {
  private _id: BankTransferId;
  private _transferNumber: string;
  private _transferType: BankTransferType;
  private _fromAccountId: string;
  private _toAccountId: string;
  private _amount: number;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _vndAmount: number;
  private _transferDate: Date;
  private _valueDate: Date | null;
  private _reference: string | null;
  private _swiftMessage: string | null;
  private _beneficiaryName: string | null;
  private _beneficiaryBank: string | null;
  private _beneficiaryAccount: string | null;
  private _intermediaryBank: string | null;
  private _fees: number;
  private _status: BankTransferStatus;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _executedById: string | null;
  private _executedAt: Date | null;
  private _completedAt: Date | null;
  private _failureReason: string | null;
  private _notes: string | null;
  private _postedToGL: boolean = false;
  private _glBatchId: string | null = null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: BankTransferId,
    transferNumber: string,
    transferType: BankTransferType,
    fromAccountId: string,
    toAccountId: string,
    amount: number,
    currencyCode: string,
    transferDate: Date,
  ) {
    super();
    if (fromAccountId === toAccountId) {
      throw new DomainError("BusinessRule", "Source and destination accounts must be different");
    }
    if (amount <= 0) throw new DomainError("BusinessRule", "Transfer amount must be positive");
    this._id = id;
    this._transferNumber = transferNumber;
    this._transferType = transferType;
    this._fromAccountId = fromAccountId;
    this._toAccountId = toAccountId;
    this._amount = amount;
    this._currencyCode = currencyCode;
    this._exchangeRate = 1;
    this._vndAmount = amount;
    this._transferDate = transferDate;
    this._valueDate = null;
    this._reference = null;
    this._swiftMessage = null;
    this._beneficiaryName = null;
    this._beneficiaryBank = null;
    this._beneficiaryAccount = null;
    this._intermediaryBank = null;
    this._fees = 0;
    this._status = BankTransferStatus.Draft;
    this._approvedById = null;
    this._approvedAt = null;
    this._executedById = null;
    this._executedAt = null;
    this._completedAt = null;
    this._failureReason = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
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
  }): BankTransfer {
    const t = new BankTransfer(
      BankTransferId.new(),
      params.transferNumber,
      params.transferType,
      params.fromAccountId,
      params.toAccountId,
      params.amount,
      params.currencyCode ?? "VND",
      params.transferDate,
    );
    t._reference = params.reference ?? null;
    t._beneficiaryName = params.beneficiaryName ?? null;
    t._beneficiaryBank = params.beneficiaryBank ?? null;
    t._beneficiaryAccount = params.beneficiaryAccount ?? null;
    t._notes = params.notes ?? null;
    if (params.exchangeRate && params.exchangeRate !== 1) {
      if (!params.currencyCode || params.currencyCode === "VND") {
        throw new DomainError("BusinessRule", "Exchange rate only applicable for foreign currency");
      }
      t._exchangeRate = params.exchangeRate;
      t._vndAmount = Math.round(params.amount * params.exchangeRate);
    }
    return t;
  }

  static load(state: BankTransferState): BankTransfer {
    const t = new BankTransfer(
      new BankTransferId(state.id),
      state.transferNumber,
      state.transferType as BankTransferType,
      state.fromAccountId,
      state.toAccountId,
      state.amount,
      state.currencyCode,
      state.transferDate,
    );
    t._exchangeRate = state.exchangeRate;
    t._vndAmount = state.vndAmount;
    t._valueDate = state.valueDate;
    t._reference = state.reference;
    t._swiftMessage = state.swiftMessage;
    t._beneficiaryName = state.beneficiaryName;
    t._beneficiaryBank = state.beneficiaryBank;
    t._beneficiaryAccount = state.beneficiaryAccount;
    t._intermediaryBank = state.intermediaryBank;
    t._fees = state.fees;
    t._status = state.status as BankTransferStatus;
    t._approvedById = state.approvedById;
    t._approvedAt = state.approvedAt;
    t._executedById = state.executedById;
    t._executedAt = state.executedAt;
    t._completedAt = state.completedAt;
    t._failureReason = state.failureReason;
    t._notes = state.notes;
    t._postedToGL = state.postedToGL;
    t._glBatchId = state.glBatchId;
    t._version = state.version;
    t._createdAt = state.createdAt;
    t._updatedAt = state.updatedAt;
    t._deletedAt = state.deletedAt;
    return t;
  }

  get id(): BankTransferId { return this._id; }
  get transferNumber(): string { return this._transferNumber; }
  get transferType(): BankTransferType { return this._transferType; }
  get fromAccountId(): string { return this._fromAccountId; }
  get toAccountId(): string { return this._toAccountId; }
  get amount(): number { return this._amount; }
  get currencyCode(): string { return this._currencyCode; }
  get vndAmount(): number { return this._vndAmount; }
  get status(): BankTransferStatus { return this._status; }
  get fees(): number { return this._fees; }
  get failureReason(): string | null { return this._failureReason; }
  get version(): number { return this._version; }

  approve(userId: string): void {
    if (this._status !== BankTransferStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft transfers can be approved");
    }
    this._status = BankTransferStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  execute(userId: string): void {
    if (this._status !== BankTransferStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved transfers can be executed");
    }
    this._status = BankTransferStatus.Sent;
    this._executedById = userId;
    this._executedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  complete(): void {
    if (this._status !== BankTransferStatus.Sent) {
      throw new DomainError("BusinessRule", "Transfer must be sent before completing");
    }
    this._status = BankTransferStatus.Completed;
    this._completedAt = new Date();
    this._valueDate = this._completedAt;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new BankTransferCompleted(this._id.value, new Date(), {
      transferNumber: this._transferNumber,
      amount: this._amount,
      fromAccount: this._fromAccountId,
      toAccount: this._toAccountId,
    }));
  }

  fail(reason: string): void {
    if (this._status !== BankTransferStatus.Sent) {
      throw new DomainError("BusinessRule", "Transfer must be sent before marking failed");
    }
    this._status = BankTransferStatus.Failed;
    this._failureReason = reason;
    this._updatedAt = new Date();
    this._version++;
  }

  cancel(): void {
    if (this._status === BankTransferStatus.Completed || this._status === BankTransferStatus.Sent) {
      throw new DomainError("BusinessRule", "Cannot cancel completed or sent transfer");
    }
    this._status = BankTransferStatus.Cancelled;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): BankTransferState {
    return {
      id: this._id.value,
      transferNumber: this._transferNumber,
      transferType: this._transferType,
      fromAccountId: this._fromAccountId,
      toAccountId: this._toAccountId,
      amount: this._amount,
      currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      vndAmount: this._vndAmount,
      transferDate: this._transferDate,
      valueDate: this._valueDate,
      reference: this._reference,
      swiftMessage: this._swiftMessage,
      beneficiaryName: this._beneficiaryName,
      beneficiaryBank: this._beneficiaryBank,
      beneficiaryAccount: this._beneficiaryAccount,
      intermediaryBank: this._intermediaryBank,
      fees: this._fees,
      status: this._status,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      executedById: this._executedById,
      executedAt: this._executedAt,
      completedAt: this._completedAt,
      failureReason: this._failureReason,
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
