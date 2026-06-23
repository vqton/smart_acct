import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankStatementId, BankStatementLineId, BankReconciliationId } from "./cm-ids.js";
import { BankReconciliationStatus, StatementLineType } from "./cm-enums.js";
import { BankStatementReconciled } from "./cm-domain-events.js";

export interface BankStatementState {
  id: string;
  bankAccountId: string;
  statementNumber: string;
  periodStart: Date;
  periodEnd: Date;
  openingBalance: number;
  closingBalance: number;
  totalDebit: number;
  totalCredit: number;
  importedAt: Date | null;
  importedBy: string | null;
  source: string | null;
  isReconciled: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class BankStatement extends AggregateRoot<BankStatementId> {
  private _id: BankStatementId;
  private _bankAccountId: string;
  private _statementNumber: string;
  private _periodStart: Date;
  private _periodEnd: Date;
  private _openingBalance: number;
  private _closingBalance: number;
  private _totalDebit: number;
  private _totalCredit: number;
  private _importedAt: Date | null;
  private _importedBy: string | null;
  private _source: string | null;
  private _isReconciled: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private _lines: BankStatementLine[] = [];

  constructor(
    id: BankStatementId,
    bankAccountId: string,
    statementNumber: string,
    periodStart: Date,
    periodEnd: Date,
    openingBalance: number,
    closingBalance: number,
  ) {
    super();
    this._id = id;
    this._bankAccountId = bankAccountId;
    this._statementNumber = statementNumber;
    this._periodStart = periodStart;
    this._periodEnd = periodEnd;
    this._openingBalance = openingBalance;
    this._closingBalance = closingBalance;
    this._totalDebit = 0;
    this._totalCredit = 0;
    this._importedAt = null;
    this._importedBy = null;
    this._source = null;
    this._isReconciled = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    bankAccountId: string;
    statementNumber: string;
    periodStart: Date;
    periodEnd: Date;
    openingBalance: number;
    closingBalance: number;
  }): BankStatement {
    return new BankStatement(
      BankStatementId.new(),
      params.bankAccountId,
      params.statementNumber,
      params.periodStart,
      params.periodEnd,
      params.openingBalance,
      params.closingBalance,
    );
  }

  static load(state: BankStatementState): BankStatement {
    const s = new BankStatement(
      new BankStatementId(state.id),
      state.bankAccountId,
      state.statementNumber,
      state.periodStart,
      state.periodEnd,
      state.openingBalance,
      state.closingBalance,
    );
    s._totalDebit = state.totalDebit;
    s._totalCredit = state.totalCredit;
    s._importedAt = state.importedAt;
    s._importedBy = state.importedBy;
    s._source = state.source;
    s._isReconciled = state.isReconciled;
    s._version = state.version;
    s._createdAt = state.createdAt;
    s._updatedAt = state.updatedAt;
    s._deletedAt = state.deletedAt;
    return s;
  }

  get id(): BankStatementId { return this._id; }
  get bankAccountId(): string { return this._bankAccountId; }
  get statementNumber(): string { return this._statementNumber; }
  get periodStart(): Date { return this._periodStart; }
  get periodEnd(): Date { return this._periodEnd; }
  get openingBalance(): number { return this._openingBalance; }
  get closingBalance(): number { return this._closingBalance; }
  get totalDebit(): number { return this._totalDebit; }
  get totalCredit(): number { return this._totalCredit; }
  get isReconciled(): boolean { return this._isReconciled; }
  get lines(): readonly BankStatementLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(lineData: {
    lineDate: Date;
    description: string | null;
    reference: string | null;
    chequeNumber: string | null;
    lineType: StatementLineType;
    amount: number;
    currencyCode?: string;
    runningBalance: number;
  }): BankStatementLine {
    if (this._isReconciled) {
      throw new DomainError("BusinessRule", "Cannot modify a reconciled statement");
    }
    const line = new BankStatementLine(
      BankStatementLineId.new(),
      this._id.value,
      lineData.lineDate,
      lineData.description,
      lineData.reference,
      lineData.chequeNumber,
      lineData.lineType,
      lineData.amount,
      lineData.currencyCode ?? "VND",
      lineData.runningBalance,
    );
    this._lines.push(line);
    if (lineData.lineType === StatementLineType.Debit) {
      this._totalDebit += lineData.amount;
    } else {
      this._totalCredit += lineData.amount;
    }
    this._updatedAt = new Date();
    this._version++;
    return line;
  }

  markReconciled(): void {
    this._isReconciled = true;
    this._updatedAt = new Date();
    this._version++;
  }

  validateBalance(): void {
    const calculated = this._openingBalance + this._totalCredit - this._totalDebit;
    if (calculated !== this._closingBalance) {
      throw new DomainError("BusinessRule",
        `Statement ${this._statementNumber} does not balance. Expected: ${calculated}, Got: ${this._closingBalance}`);
    }
  }

  toState(): BankStatementState {
    return {
      id: this._id.value,
      bankAccountId: this._bankAccountId,
      statementNumber: this._statementNumber,
      periodStart: this._periodStart,
      periodEnd: this._periodEnd,
      openingBalance: this._openingBalance,
      closingBalance: this._closingBalance,
      totalDebit: this._totalDebit,
      totalCredit: this._totalCredit,
      importedAt: this._importedAt,
      importedBy: this._importedBy,
      source: this._source,
      isReconciled: this._isReconciled,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export class BankStatementLine {
  private _id: BankStatementLineId;
  private _statementId: string;
  private _lineDate: Date;
  private _description: string | null;
  private _reference: string | null;
  private _chequeNumber: string | null;
  private _lineType: StatementLineType;
  private _amount: number;
  private _currencyCode: string;
  private _runningBalance: number;
  private _isMatched: boolean;
  private _matchedToId: string | null;
  private _matchedToType: string | null;

  constructor(
    id: BankStatementLineId,
    statementId: string,
    lineDate: Date,
    description: string | null,
    reference: string | null,
    chequeNumber: string | null,
    lineType: StatementLineType,
    amount: number,
    currencyCode: string,
    runningBalance: number,
  ) {
    this._id = id;
    this._statementId = statementId;
    this._lineDate = lineDate;
    this._description = description;
    this._reference = reference;
    this._chequeNumber = chequeNumber;
    this._lineType = lineType;
    this._amount = amount;
    this._currencyCode = currencyCode;
    this._runningBalance = runningBalance;
    this._isMatched = false;
    this._matchedToId = null;
    this._matchedToType = null;
  }

  get id(): BankStatementLineId { return this._id; }
  get statementId(): string { return this._statementId; }
  get lineDate(): Date { return this._lineDate; }
  get description(): string | null { return this._description; }
  get reference(): string | null { return this._reference; }
  get lineType(): StatementLineType { return this._lineType; }
  get amount(): number { return this._amount; }
  get isMatched(): boolean { return this._isMatched; }

  match(sourceType: string, sourceId: string): void {
    if (this._isMatched) throw new DomainError("BusinessRule", "Line already matched");
    this._isMatched = true;
    this._matchedToId = sourceId;
    this._matchedToType = sourceType;
  }

  unmatch(): void {
    if (!this._isMatched) throw new DomainError("BusinessRule", "Line is not matched");
    this._isMatched = false;
    this._matchedToId = null;
    this._matchedToType = null;
  }
}

export interface BankReconciliationState {
  id: string;
  bankAccountId: string;
  bankStatementId: string;
  reconciliationNumber: string;
  reconciliationDate: Date;
  statementBalance: number;
  bookBalance: number;
  difference: number;
  status: string;
  matchedCount: number;
  unmatchedCount: number;
  preparedById: string | null;
  reviewedById: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class BankReconciliation extends AggregateRoot<BankReconciliationId> {
  private _id: BankReconciliationId;
  private _bankAccountId: string;
  private _bankStatementId: string;
  private _reconciliationNumber: string;
  private _reconciliationDate: Date;
  private _statementBalance: number;
  private _bookBalance: number;
  private _difference: number;
  private _status: BankReconciliationStatus;
  private _matchedCount: number;
  private _unmatchedCount: number;
  private _preparedById: string | null;
  private _reviewedById: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: BankReconciliationId,
    bankAccountId: string,
    bankStatementId: string,
    reconciliationNumber: string,
    reconciliationDate: Date,
    statementBalance: number,
    bookBalance: number,
  ) {
    super();
    this._id = id;
    this._bankAccountId = bankAccountId;
    this._bankStatementId = bankStatementId;
    this._reconciliationNumber = reconciliationNumber;
    this._reconciliationDate = reconciliationDate;
    this._statementBalance = statementBalance;
    this._bookBalance = bookBalance;
    this._difference = Math.abs(statementBalance - bookBalance);
    this._status = BankReconciliationStatus.Open;
    this._matchedCount = 0;
    this._unmatchedCount = 0;
    this._preparedById = null;
    this._reviewedById = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    bankAccountId: string;
    bankStatementId: string;
    reconciliationNumber: string;
    reconciliationDate: Date;
    statementBalance: number;
    bookBalance: number;
  }): BankReconciliation {
    return new BankReconciliation(
      BankReconciliationId.new(),
      params.bankAccountId,
      params.bankStatementId,
      params.reconciliationNumber,
      params.reconciliationDate,
      params.statementBalance,
      params.bookBalance,
    );
  }

  static load(state: BankReconciliationState): BankReconciliation {
    const r = new BankReconciliation(
      new BankReconciliationId(state.id),
      state.bankAccountId,
      state.bankStatementId,
      state.reconciliationNumber,
      state.reconciliationDate,
      state.statementBalance,
      state.bookBalance,
    );
    r._difference = state.difference;
    r._status = state.status as BankReconciliationStatus;
    r._matchedCount = state.matchedCount;
    r._unmatchedCount = state.unmatchedCount;
    r._preparedById = state.preparedById;
    r._reviewedById = state.reviewedById;
    r._approvedById = state.approvedById;
    r._approvedAt = state.approvedAt;
    r._notes = state.notes;
    r._version = state.version;
    r._createdAt = state.createdAt;
    r._updatedAt = state.updatedAt;
    r._deletedAt = state.deletedAt;
    return r;
  }

  get id(): BankReconciliationId { return this._id; }
  get reconciliationNumber(): string { return this._reconciliationNumber; }
  get status(): BankReconciliationStatus { return this._status; }
  get difference(): number { return this._difference; }
  get matchedCount(): number { return this._matchedCount; }
  get unmatchedCount(): number { return this._unmatchedCount; }

  addMatch(): void {
    this._matchedCount++;
    this._updatedAt = new Date();
    this._version++;
  }

  addUnmatched(): void {
    this._unmatchedCount++;
    this._updatedAt = new Date();
    this._version++;
  }

  resolve(userId: string): void {
    if (this._status !== BankReconciliationStatus.Open && this._status !== BankReconciliationStatus.InProgress) {
      throw new DomainError("BusinessRule", "Reconciliation must be in progress to resolve");
    }
    if (this._difference > 0) {
      this._status = BankReconciliationStatus.DifferenceFound;
      throw new DomainError("BusinessRule",
        `Cannot resolve with difference ${this._difference}. Investigate outstanding items first.`);
    }
    this._status = BankReconciliationStatus.Resolved;
    this._reviewedById = userId;
    this._updatedAt = new Date();
    this._version++;
  }

  approve(userId: string): void {
    if (this._status !== BankReconciliationStatus.Resolved) {
      throw new DomainError("BusinessRule", "Only resolved reconciliations can be approved");
    }
    this._status = BankReconciliationStatus.Closed;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new BankStatementReconciled(this._id.value, new Date(), {
      reconciliationNumber: this._reconciliationNumber,
      statementBalance: this._statementBalance,
      bookBalance: this._bookBalance,
    }));
  }

  toState(): BankReconciliationState {
    return {
      id: this._id.value,
      bankAccountId: this._bankAccountId,
      bankStatementId: this._bankStatementId,
      reconciliationNumber: this._reconciliationNumber,
      reconciliationDate: this._reconciliationDate,
      statementBalance: this._statementBalance,
      bookBalance: this._bookBalance,
      difference: this._difference,
      status: this._status,
      matchedCount: this._matchedCount,
      unmatchedCount: this._unmatchedCount,
      preparedById: this._preparedById,
      reviewedById: this._reviewedById,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
