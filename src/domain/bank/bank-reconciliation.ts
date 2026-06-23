import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankReconciliationId, BankReconciliationItemId } from "./bank-ids.js";
import { ReconciliationStatus, ReconciliationMatchType } from "./bank-enums.js";
import { ReconciliationCreated, ReconciliationMatched, ReconciliationApproved } from "./bank-events.js";

export interface BankReconciliationItemState {
  id: string; reconciliationId: string; statementLineId: string | null;
  sourceType: string; sourceId: string; sourceReference: string | null;
  amount: number; matchType: string; matchDate: Date;
  isClearItem: boolean; notes: string | null; createdAt: Date; updatedAt: Date;
}

export class BankReconciliationItem {
  constructor(
    private _id: BankReconciliationItemId, private _reconciliationId: string,
    private _statementLineId: string | null, private _sourceType: string,
    private _sourceId: string, private _sourceReference: string | null,
    private _amount: number, private _matchType: ReconciliationMatchType,
    private _matchDate: Date, private _isClearItem: boolean = true,
    private _notes: string | null = null,
  ) {}

  get id(): BankReconciliationItemId { return this._id; }
  get statementLineId(): string | null { return this._statementLineId; }
  get sourceType(): string { return this._sourceType; }
  get sourceId(): string { return this._sourceId; }
  get amount(): number { return this._amount; }
  get matchType(): ReconciliationMatchType { return this._matchType; }
  get isClearItem(): boolean { return this._isClearItem; }

  static load(s: BankReconciliationItemState): BankReconciliationItem {
    return new BankReconciliationItem(
      new BankReconciliationItemId(s.id), s.reconciliationId,
      s.statementLineId, s.sourceType, s.sourceId, s.sourceReference,
      s.amount, s.matchType as ReconciliationMatchType, s.matchDate,
      s.isClearItem, s.notes
    );
  }

  toState(): BankReconciliationItemState {
    return { id: this._id.value, reconciliationId: this._reconciliationId,
      statementLineId: this._statementLineId, sourceType: this._sourceType,
      sourceId: this._sourceId, sourceReference: this._sourceReference,
      amount: this._amount, matchType: this._matchType, matchDate: this._matchDate,
      isClearItem: this._isClearItem, notes: this._notes,
      createdAt: new Date(), updatedAt: new Date() };
  }
}

export interface BankReconciliationState {
  id: string; bankAccountId: string; bankStatementId: string;
  reconciliationNumber: string; reconciliationDate: Date;
  statementBalance: number; bookBalance: number; clearedAmount: number;
  outstandingAmount: number; difference: number; status: string;
  matchedCount: number; unmatchedCount: number; autoMatchedCount: number;
  manualMatchedCount: number; preparedById: string | null;
  reviewedById: string | null; approvedById: string | null;
  approvedAt: Date | null; reversedById: string | null;
  reversedAt: Date | null; reversalReason: string | null;
  notes: string | null; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankReconciliation extends AggregateRoot<BankReconciliationId> {
  private _id: BankReconciliationId; private _bankAccountId: string;
  private _bankStatementId: string; private _reconciliationNumber: string;
  private _reconciliationDate: Date; private _statementBalance: number;
  private _bookBalance: number; private _clearedAmount: number;
  private _outstandingAmount: number; private _difference: number;
  private _status: ReconciliationStatus; private _matchedCount: number;
  private _unmatchedCount: number; private _autoMatchedCount: number;
  private _manualMatchedCount: number; private _preparedById: string | null;
  private _reviewedById: string | null; private _approvedById: string | null;
  private _approvedAt: Date | null; private _reversedById: string | null;
  private _reversedAt: Date | null; private _reversalReason: string | null;
  private _notes: string | null;
  private _items: BankReconciliationItem[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: BankReconciliationId, bankAccountId: string, bankStatementId: string,
    reconciliationNumber: string, reconciliationDate: Date, statementBalance: number, bookBalance: number) {
    super(); this._id = id; this._bankAccountId = bankAccountId;
    this._bankStatementId = bankStatementId; this._reconciliationNumber = reconciliationNumber;
    this._reconciliationDate = reconciliationDate; this._statementBalance = statementBalance;
    this._bookBalance = bookBalance; this._clearedAmount = 0; this._outstandingAmount = 0;
    this._difference = Math.abs(statementBalance - bookBalance);
    this._status = ReconciliationStatus.Open;
    this._matchedCount = 0; this._unmatchedCount = 0;
    this._autoMatchedCount = 0; this._manualMatchedCount = 0;
    this._preparedById = null; this._reviewedById = null;
    this._approvedById = null; this._approvedAt = null;
    this._reversedById = null; this._reversedAt = null; this._reversalReason = null;
    this._notes = null; this._version = 1;
    this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    bankAccountId: string; bankStatementId: string; reconciliationNumber: string;
    reconciliationDate: Date; statementBalance: number; bookBalance: number;
    preparedById?: string; notes?: string;
  }): BankReconciliation {
    const r = new BankReconciliation(BankReconciliationId.new(), p.bankAccountId,
      p.bankStatementId, p.reconciliationNumber, p.reconciliationDate,
      p.statementBalance, p.bookBalance);
    r._preparedById = p.preparedById ?? null; r._notes = p.notes ?? null;
    r.addEvent(new ReconciliationCreated(r._id.value, new Date(), {
      reconciliationNumber: r._reconciliationNumber,
      statementBalance: r._statementBalance, bookBalance: r._bookBalance,
    }));
    return r;
  }

  static load(s: BankReconciliationState): BankReconciliation {
    const r = new BankReconciliation(new BankReconciliationId(s.id), s.bankAccountId,
      s.bankStatementId, s.reconciliationNumber, s.reconciliationDate,
      s.statementBalance, s.bookBalance);
    r._difference = s.difference; r._clearedAmount = s.clearedAmount;
    r._outstandingAmount = s.outstandingAmount; r._status = s.status as ReconciliationStatus;
    r._matchedCount = s.matchedCount; r._unmatchedCount = s.unmatchedCount;
    r._autoMatchedCount = s.autoMatchedCount; r._manualMatchedCount = s.manualMatchedCount;
    r._preparedById = s.preparedById; r._reviewedById = s.reviewedById;
    r._approvedById = s.approvedById; r._approvedAt = s.approvedAt;
    r._reversedById = s.reversedById; r._reversedAt = s.reversedAt;
    r._reversalReason = s.reversalReason; r._notes = s.notes;
    r._version = s.version; r._createdAt = s.createdAt;
    r._updatedAt = s.updatedAt; r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): BankReconciliationId { return this._id; }
  get bankAccountId(): string { return this._bankAccountId; }
  get bankStatementId(): string { return this._bankStatementId; }
  get reconciliationNumber(): string { return this._reconciliationNumber; }
  get status(): ReconciliationStatus { return this._status; }
  get difference(): number { return this._difference; }
  get matchedCount(): number { return this._matchedCount; }
  get unmatchedCount(): number { return this._unmatchedCount; }
  get items(): readonly BankReconciliationItem[] { return this._items; }
  get version(): number { return this._version; }

  addItem(p: {
    statementLineId?: string | null; sourceType: string; sourceId: string;
    sourceReference?: string | null; amount: number; matchType: ReconciliationMatchType;
    isClearItem?: boolean; notes?: string | null;
  }): BankReconciliationItem {
    if (this._status !== ReconciliationStatus.Open && this._status !== ReconciliationStatus.InProgress) {
      throw new DomainError("BusinessRule", "Reconciliation must be open or in-progress to add items");
    }
    const item = new BankReconciliationItem(BankReconciliationItemId.new(), this._id.value,
      p.statementLineId ?? null, p.sourceType, p.sourceId, p.sourceReference ?? null,
      p.amount, p.matchType, new Date(), p.isClearItem ?? true, p.notes ?? null);
    this._items.push(item);
    if (p.isClearItem ?? true) {
      this._clearedAmount += p.amount;
    } else {
      this._outstandingAmount += p.amount;
    }
    this._matchedCount++;
    if (p.matchType === ReconciliationMatchType.Auto) this._autoMatchedCount++;
    else this._manualMatchedCount++;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new ReconciliationMatched(this._id.value, new Date(), {
      sourceType: p.sourceType, sourceId: p.sourceId, amount: p.amount,
    }));
    return item;
  }

  addUnmatchedItem(amount: number, notes?: string): void {
    this._unmatchedCount++; this._outstandingAmount += amount;
    this._updatedAt = new Date(); this._version++;
  }

  resolve(userId: string): void {
    if (this._status !== ReconciliationStatus.Open && this._status !== ReconciliationStatus.InProgress) {
      throw new DomainError("BusinessRule", "Reconciliation must be open/in-progress to resolve");
    }
    this._difference = Math.abs(this._statementBalance - this._bookBalance - this._clearedAmount + this._outstandingAmount);
    if (this._difference > 0.01) {
      this._status = ReconciliationStatus.DifferenceFound;
      throw new DomainError("BusinessRule",
        `Cannot resolve with difference ${this._difference}. Investigate outstanding items.`);
    }
    this._status = ReconciliationStatus.Resolved;
    this._reviewedById = userId;
    this._updatedAt = new Date(); this._version++;
  }

  approve(userId: string): void {
    if (this._status !== ReconciliationStatus.Resolved && this._status !== ReconciliationStatus.Approved) {
      throw new DomainError("BusinessRule", "Only resolved reconciliations can be approved");
    }
    this._status = ReconciliationStatus.Approved;
    this._approvedById = userId; this._approvedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new ReconciliationApproved(this._id.value, new Date(), {
      reconciliationNumber: this._reconciliationNumber,
      statementBalance: this._statementBalance, bookBalance: this._bookBalance,
    }));
  }

  close(): void {
    if (this._status !== ReconciliationStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved reconciliations can be closed");
    }
    this._status = ReconciliationStatus.Closed;
    this._updatedAt = new Date(); this._version++;
  }

  reverse(userId: string, reason: string): void {
    if (this._status === ReconciliationStatus.Closed || this._status === ReconciliationStatus.Reversed) {
      throw new DomainError("BusinessRule", "Cannot reverse closed or already reversed reconciliation");
    }
    this._status = ReconciliationStatus.Reversed;
    this._reversedById = userId; this._reversedAt = new Date();
    this._reversalReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  markInProgress(): void {
    if (this._status !== ReconciliationStatus.Open) {
      throw new DomainError("BusinessRule", "Only open reconciliations can be marked in-progress");
    }
    this._status = ReconciliationStatus.InProgress;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): BankReconciliationState {
    return {
      id: this._id.value, bankAccountId: this._bankAccountId,
      bankStatementId: this._bankStatementId, reconciliationNumber: this._reconciliationNumber,
      reconciliationDate: this._reconciliationDate, statementBalance: this._statementBalance,
      bookBalance: this._bookBalance, clearedAmount: this._clearedAmount,
      outstandingAmount: this._outstandingAmount, difference: this._difference,
      status: this._status, matchedCount: this._matchedCount,
      unmatchedCount: this._unmatchedCount, autoMatchedCount: this._autoMatchedCount,
      manualMatchedCount: this._manualMatchedCount, preparedById: this._preparedById,
      reviewedById: this._reviewedById, approvedById: this._approvedById,
      approvedAt: this._approvedAt, reversedById: this._reversedById,
      reversedAt: this._reversedAt, reversalReason: this._reversalReason,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
