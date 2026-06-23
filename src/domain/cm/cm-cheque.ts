import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ChequeBookId, ChequeId } from "./cm-ids.js";
import { ChequeType, ChequeStatus, ChequeBookStatus } from "./cm-enums.js";
import { ChequeIssued, ChequeCleared, ChequeReturned } from "./cm-domain-events.js";

export interface ChequeBookState {
  id: string;
  bankAccountId: string;
  chequeBookNumber: string;
  startNumber: number;
  endNumber: number;
  currentNumber: number;
  status: string;
  issuedDate: Date;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class ChequeBook extends AggregateRoot<ChequeBookId> {
  private _id: ChequeBookId;
  private _bankAccountId: string;
  private _chequeBookNumber: string;
  private _startNumber: number;
  private _endNumber: number;
  private _currentNumber: number;
  private _status: ChequeBookStatus;
  private _issuedDate: Date;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: ChequeBookId,
    bankAccountId: string,
    chequeBookNumber: string,
    startNumber: number,
    endNumber: number,
    issuedDate: Date,
  ) {
    super();
    if (endNumber < startNumber) throw new DomainError("BusinessRule", "End number must be >= start number");
    this._id = id;
    this._bankAccountId = bankAccountId;
    this._chequeBookNumber = chequeBookNumber;
    this._startNumber = startNumber;
    this._endNumber = endNumber;
    this._currentNumber = startNumber;
    this._status = ChequeBookStatus.Active;
    this._issuedDate = issuedDate;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    bankAccountId: string;
    chequeBookNumber: string;
    startNumber: number;
    endNumber: number;
    issuedDate: Date;
  }): ChequeBook {
    return new ChequeBook(
      ChequeBookId.new(),
      params.bankAccountId,
      params.chequeBookNumber,
      params.startNumber,
      params.endNumber,
      params.issuedDate,
    );
  }

  static load(state: ChequeBookState): ChequeBook {
    const cb = new ChequeBook(
      new ChequeBookId(state.id),
      state.bankAccountId,
      state.chequeBookNumber,
      state.startNumber,
      state.endNumber,
      state.issuedDate,
    );
    cb._currentNumber = state.currentNumber;
    cb._status = state.status as ChequeBookStatus;
    cb._version = state.version;
    cb._createdAt = state.createdAt;
    cb._updatedAt = state.updatedAt;
    cb._deletedAt = state.deletedAt;
    return cb;
  }

  get id(): ChequeBookId { return this._id; }
  get bankAccountId(): string { return this._bankAccountId; }
  get chequeBookNumber(): string { return this._chequeBookNumber; }
  get startNumber(): number { return this._startNumber; }
  get endNumber(): number { return this._endNumber; }
  get currentNumber(): number { return this._currentNumber; }
  get status(): ChequeBookStatus { return this._status; }
  get issuedDate(): Date { return this._issuedDate; }
  get version(): number { return this._version; }

  reserveNext(): Cheque {
    if (this._status !== ChequeBookStatus.Active) {
      throw new DomainError("BusinessRule", "Cheque book is not active");
    }
    if (this._currentNumber > this._endNumber) {
      this._status = ChequeBookStatus.FullUsed;
      throw new DomainError("BusinessRule", "All cheques in this book have been used");
    }
    const chequeNumber = this._currentNumber;
    this._currentNumber++;
    this._updatedAt = new Date();
    this._version++;

    const cheque = new Cheque(ChequeId.new(), this._id.value, chequeNumber);
    return cheque;
  }

  toState(): ChequeBookState {
    return {
      id: this._id.value,
      bankAccountId: this._bankAccountId,
      chequeBookNumber: this._chequeBookNumber,
      startNumber: this._startNumber,
      endNumber: this._endNumber,
      currentNumber: this._currentNumber,
      status: this._status,
      issuedDate: this._issuedDate,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export interface ChequeState {
  id: string;
  chequeBookId: string;
  chequeNumber: number;
  chequeType: string;
  payeeName: string | null;
  payeeId: string | null;
  amount: number;
  currencyCode: string;
  issueDate: Date | null;
  depositDate: Date | null;
  clearingDate: Date | null;
  returnedDate: Date | null;
  voidDate: Date | null;
  status: string;
  reference: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Cheque {
  private _id: ChequeId;
  private _chequeBookId: string;
  private _chequeNumber: number;
  private _chequeType: ChequeType;
  private _payeeName: string | null;
  private _payeeId: string | null;
  private _amount: number;
  private _currencyCode: string;
  private _issueDate: Date | null;
  private _depositDate: Date | null;
  private _clearingDate: Date | null;
  private _returnedDate: Date | null;
  private _voidDate: Date | null;
  private _status: ChequeStatus;
  private _reference: string | null;
  private _notes: string | null;
  private _version: number;

  constructor(id: ChequeId, chequeBookId: string, chequeNumber: number) {
    this._id = id;
    this._chequeBookId = chequeBookId;
    this._chequeNumber = chequeNumber;
    this._chequeType = ChequeType.Corporate;
    this._payeeName = null;
    this._payeeId = null;
    this._amount = 0;
    this._currencyCode = "VND";
    this._issueDate = null;
    this._depositDate = null;
    this._clearingDate = null;
    this._returnedDate = null;
    this._voidDate = null;
    this._status = ChequeStatus.Unissued;
    this._reference = null;
    this._notes = null;
    this._version = 1;
  }

  get id(): ChequeId { return this._id; }
  get chequeBookId(): string { return this._chequeBookId; }
  get chequeNumber(): number { return this._chequeNumber; }
  get payeeName(): string | null { return this._payeeName; }
  get amount(): number { return this._amount; }
  get status(): ChequeStatus { return this._status; }
  get clearingDate(): Date | null { return this._clearingDate; }
  get returnedDate(): Date | null { return this._returnedDate; }

  issue(amount: number, payeeName: string, issueDate: Date, currencyCode: string = "VND"): void {
    if (this._status !== ChequeStatus.Unissued) {
      throw new DomainError("BusinessRule", `Cheque ${this._chequeNumber} already issued`);
    }
    if (amount <= 0) throw new DomainError("BusinessRule", "Cheque amount must be positive");
    this._amount = amount;
    this._payeeName = payeeName;
    this._issueDate = issueDate;
    this._currencyCode = currencyCode;
    this._status = ChequeStatus.Issued;
    this._version++;
  }

  deposit(depositDate: Date): void {
    if (this._status !== ChequeStatus.Issued) {
      throw new DomainError("BusinessRule", "Only issued cheques can be deposited");
    }
    this._depositDate = depositDate;
    this._status = ChequeStatus.Deposited;
    this._version++;
  }

  clear(clearingDate: Date): void {
    if (this._status !== ChequeStatus.Deposited) {
      throw new DomainError("BusinessRule", "Only deposited cheques can be cleared");
    }
    this._clearingDate = clearingDate;
    this._status = ChequeStatus.Cleared;
    this._version++;
  }

  returnCheque(returnedDate: Date, reason: string): void {
    if (this._status !== ChequeStatus.Deposited && this._status !== ChequeStatus.Issued) {
      throw new DomainError("BusinessRule", "Cheque cannot be returned in current status");
    }
    this._returnedDate = returnedDate;
    this._notes = reason;
    this._status = ChequeStatus.Returned;
    this._version++;
  }

  stop(reason: string): void {
    if (this._status !== ChequeStatus.Issued && this._status !== ChequeStatus.Deposited) {
      throw new DomainError("BusinessRule", "Cheque cannot be stopped in current status");
    }
    this._notes = reason;
    this._status = ChequeStatus.Stopped;
    this._version++;
  }

  voidCheque(reason: string): void {
    if (this._status !== ChequeStatus.Unissued && this._status !== ChequeStatus.Issued) {
      throw new DomainError("BusinessRule", "Cheque cannot be voided in current status");
    }
    this._voidDate = new Date();
    this._notes = reason;
    this._status = ChequeStatus.Voided;
    this._version++;
  }

  toState(): ChequeState {
    return {
      id: this._id.value,
      chequeBookId: this._chequeBookId,
      chequeNumber: this._chequeNumber,
      chequeType: this._chequeType,
      payeeName: this._payeeName,
      payeeId: this._payeeId,
      amount: this._amount,
      currencyCode: this._currencyCode,
      issueDate: this._issueDate,
      depositDate: this._depositDate,
      clearingDate: this._clearingDate,
      returnedDate: this._returnedDate,
      voidDate: this._voidDate,
      status: this._status,
      reference: this._reference,
      notes: this._notes,
      version: this._version,
      createdAt: new Date(),
      updatedAt: new Date(),
      deletedAt: null,
    };
  }
}
