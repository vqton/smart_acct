import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashSessionId } from "./cm-ids.js";
import { CashSessionStatus } from "./cm-enums.js";
import { CashSessionOpened, CashSessionClosed, CashSessionDiscrepancyFound } from "./cm-domain-events.js";
import { CashCountReport } from "./cm-value-objects.js";

export interface CashSessionState {
  id: string;
  sessionNumber: string;
  cashBoxId: string;
  cashRegisterId: string | null;
  cashierId: string;
  status: string;
  openedAt: Date;
  closedAt: Date | null;
  openedBalance: number;
  expectedBalance: number;
  countedBalance: number;
  difference: number;
  currencyCode: string;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashSession extends AggregateRoot<CashSessionId> {
  private _id: CashSessionId;
  private _sessionNumber: string;
  private _cashBoxId: string;
  private _cashRegisterId: string | null;
  private _cashierId: string;
  private _status: CashSessionStatus;
  private _openedAt: Date;
  private _closedAt: Date | null;
  private _openedBalance: number;
  private _expectedBalance: number;
  private _countedBalance: number;
  private _difference: number;
  private _currencyCode: string;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private _totalReceipts: number = 0;
  private _totalPayments: number = 0;

  constructor(
    id: CashSessionId,
    sessionNumber: string,
    cashBoxId: string,
    cashierId: string,
    openedBalance: number,
    currencyCode: string,
    cashRegisterId: string | null = null,
  ) {
    super();
    this._id = id;
    this._sessionNumber = sessionNumber;
    this._cashBoxId = cashBoxId;
    this._cashierId = cashierId;
    this._status = CashSessionStatus.Pending;
    this._openedAt = new Date();
    this._closedAt = null;
    this._openedBalance = openedBalance;
    this._expectedBalance = openedBalance;
    this._countedBalance = 0;
    this._difference = 0;
    this._currencyCode = currencyCode;
    this._cashRegisterId = cashRegisterId;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    sessionNumber: string;
    cashBoxId: string;
    cashierId: string;
    openedBalance?: number;
    currencyCode?: string;
    cashRegisterId?: string | null;
  }): CashSession {
    return new CashSession(
      CashSessionId.new(),
      params.sessionNumber,
      params.cashBoxId,
      params.cashierId,
      params.openedBalance ?? 0,
      params.currencyCode ?? "VND",
      params.cashRegisterId ?? null,
    );
  }

  static load(state: CashSessionState): CashSession {
    const s = new CashSession(
      new CashSessionId(state.id),
      state.sessionNumber,
      state.cashBoxId,
      state.cashierId,
      state.openedBalance,
      state.currencyCode,
      state.cashRegisterId,
    );
    s._status = state.status as CashSessionStatus;
    s._openedAt = state.openedAt;
    s._closedAt = state.closedAt;
    s._expectedBalance = state.expectedBalance;
    s._countedBalance = state.countedBalance;
    s._difference = state.difference;
    s._notes = state.notes;
    s._version = state.version;
    s._createdAt = state.createdAt;
    s._updatedAt = state.updatedAt;
    s._deletedAt = state.deletedAt;
    return s;
  }

  get id(): CashSessionId { return this._id; }
  get sessionNumber(): string { return this._sessionNumber; }
  get cashBoxId(): string { return this._cashBoxId; }
  get cashRegisterId(): string | null { return this._cashRegisterId; }
  get cashierId(): string { return this._cashierId; }
  get status(): CashSessionStatus { return this._status; }
  get openedAt(): Date { return this._openedAt; }
  get closedAt(): Date | null { return this._closedAt; }
  get openedBalance(): number { return this._openedBalance; }
  get expectedBalance(): number { return this._expectedBalance; }
  get countedBalance(): number { return this._countedBalance; }
  get difference(): number { return this._difference; }
  get currencyCode(): string { return this._currencyCode; }
  get notes(): string | null { return this._notes; }
  get totalReceipts(): number { return this._totalReceipts; }
  get totalPayments(): number { return this._totalPayments; }
  get version(): number { return this._version; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get deletedAt(): Date | null { return this._deletedAt; }

  open(): void {
    if (this._status !== CashSessionStatus.Pending) {
      throw new DomainError("BusinessRule", `Session ${this._sessionNumber} already opened`);
    }
    this._status = CashSessionStatus.Open;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashSessionOpened(this._id.value, new Date(), {
      sessionNumber: this._sessionNumber,
      cashierId: this._cashierId,
      openedBalance: this._openedBalance,
    }));
  }

  addReceipt(amount: number): void {
    if (this._status !== CashSessionStatus.Open) {
      throw new DomainError("BusinessRule", "Can only add receipts to open session");
    }
    this._totalReceipts += amount;
    this._expectedBalance += amount;
    this._updatedAt = new Date();
    this._version++;
  }

  addPayment(amount: number): void {
    if (this._status !== CashSessionStatus.Open) {
      throw new DomainError("BusinessRule", "Can only add payments to open session");
    }
    this._totalPayments += amount;
    this._expectedBalance -= amount;
    this._updatedAt = new Date();
    this._version++;
  }

  countCash(countedBalance: number): void {
    if (this._status !== CashSessionStatus.Open && this._status !== CashSessionStatus.Counting) {
      throw new DomainError("BusinessRule", "Session must be open to count cash");
    }
    this._status = CashSessionStatus.Counting;
    this._countedBalance = countedBalance;
    this._difference = this._expectedBalance - countedBalance;
    this._updatedAt = new Date();
    this._version++;
  }

  close(notes?: string): void {
    if (this._status !== CashSessionStatus.Counting) {
      throw new DomainError("BusinessRule", "Must count cash before closing session");
    }
    this._status = CashSessionStatus.Closed;
    this._closedAt = new Date();
    this._notes = notes ?? null;
    this._updatedAt = new Date();
    this._version++;

    if (Math.abs(this._difference) > 0) {
      this.addEvent(new CashSessionDiscrepancyFound(this._id.value, new Date(), {
        sessionNumber: this._sessionNumber,
        expectedBalance: this._expectedBalance,
        countedBalance: this._countedBalance,
        difference: this._difference,
      }));
    }

    this.addEvent(new CashSessionClosed(this._id.value, new Date(), {
      sessionNumber: this._sessionNumber,
      expectedBalance: this._expectedBalance,
      countedBalance: this._countedBalance,
      difference: this._difference,
    }));
  }

  reconcile(): void {
    if (this._status !== CashSessionStatus.Closed) {
      throw new DomainError("BusinessRule", "Can only reconcile closed session");
    }
    if (Math.abs(this._difference) > 0) {
      throw new DomainError("BusinessRule", `Cannot reconcile session ${this._sessionNumber} with open difference ${this._difference}`);
    }
    this._status = CashSessionStatus.Reconciled;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CashSessionState {
    return {
      id: this._id.value,
      sessionNumber: this._sessionNumber,
      cashBoxId: this._cashBoxId,
      cashRegisterId: this._cashRegisterId,
      cashierId: this._cashierId,
      status: this._status,
      openedAt: this._openedAt,
      closedAt: this._closedAt,
      openedBalance: this._openedBalance,
      expectedBalance: this._expectedBalance,
      countedBalance: this._countedBalance,
      difference: this._difference,
      currencyCode: this._currencyCode,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
