import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankStatementId, BankStatementLineId } from "./bank-ids.js";
import { StatementSource } from "./bank-enums.js";
import { StatementImported, StatementBalanceValidated } from "./bank-events.js";

export interface BankStatementLineState {
  id: string; statementId: string; lineDate: Date; valueDate: Date | null;
  description: string | null; reference: string | null; chequeNumber: string | null;
  lineType: string; amount: number; currencyCode: string; exchangeRate: number;
  runningBalance: number; isMatched: boolean; matchedToId: string | null;
  matchedToType: string | null; matchedAt: Date | null;
  notes: string | null; createdAt: Date; updatedAt: Date;
}

export class BankStatementLine {
  private _id: BankStatementLineId; private _statementId: string;
  private _lineDate: Date; private _valueDate: Date | null;
  private _description: string | null; private _reference: string | null;
  private _chequeNumber: string | null; private _lineType: string;
  private _amount: number; private _currencyCode: string;
  private _exchangeRate: number; private _runningBalance: number;
  private _isMatched: boolean; private _matchedToId: string | null;
  private _matchedToType: string | null; private _matchedAt: Date | null;
  private _notes: string | null; private _createdAt: Date; private _updatedAt: Date;

  constructor(id: BankStatementLineId, statementId: string, lineDate: Date,
    lineType: string, amount: number, runningBalance: number, currencyCode: string = "VND",
    description: string | null = null, reference: string | null = null, chequeNumber: string | null = null) {
    this._id = id; this._statementId = statementId; this._lineDate = lineDate;
    this._valueDate = null; this._description = description; this._reference = reference;
    this._chequeNumber = chequeNumber; this._lineType = lineType; this._amount = amount;
    this._currencyCode = currencyCode; this._exchangeRate = 1; this._runningBalance = runningBalance;
    this._isMatched = false; this._matchedToId = null; this._matchedToType = null;
    this._matchedAt = null; this._notes = null;
    this._createdAt = new Date(); this._updatedAt = new Date();
  }

  get id(): BankStatementLineId { return this._id; }
  get statementId(): string { return this._statementId; }
  get lineDate(): Date { return this._lineDate; }
  get lineType(): string { return this._lineType; }
  get amount(): number { return this._amount; }
  get reference(): string | null { return this._reference; }
  get runningBalance(): number { return this._runningBalance; }
  get isMatched(): boolean { return this._isMatched; }
  get matchedToId(): string | null { return this._matchedToId; }
  get matchedToType(): string | null { return this._matchedToType; }

  match(sourceType: string, sourceId: string): void {
    if (this._isMatched) throw new DomainError("BusinessRule", "Statement line already matched");
    this._isMatched = true; this._matchedToId = sourceId; this._matchedToType = sourceType;
    this._matchedAt = new Date(); this._updatedAt = new Date();
  }

  unmatch(): void {
    if (!this._isMatched) throw new DomainError("BusinessRule", "Statement line not matched");
    this._isMatched = false; this._matchedToId = null; this._matchedToType = null;
    this._matchedAt = null; this._updatedAt = new Date();
  }

  toState(): BankStatementLineState {
    return { id: this._id.value, statementId: this._statementId, lineDate: this._lineDate,
      valueDate: this._valueDate, description: this._description, reference: this._reference,
      chequeNumber: this._chequeNumber, lineType: this._lineType, amount: this._amount,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      runningBalance: this._runningBalance, isMatched: this._isMatched,
      matchedToId: this._matchedToId, matchedToType: this._matchedToType,
      matchedAt: this._matchedAt, notes: this._notes, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Bank Statement Aggregate ───────────────────────────────────────────────────

export interface BankStatementState {
  id: string; bankAccountId: string; statementNumber: string;
  periodStart: Date; periodEnd: Date; openingBalance: number;
  closingBalance: number; totalDebit: number; totalCredit: number;
  transactionCount: number; source: string;
  importedAt: Date | null; importedBy: string | null;
  hash: string | null; isReconciled: boolean; isLocked: boolean;
  notes: string | null; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankStatement extends AggregateRoot<BankStatementId> {
  private _id: BankStatementId; private _bankAccountId: string;
  private _statementNumber: string; private _periodStart: Date; private _periodEnd: Date;
  private _openingBalance: number; private _closingBalance: number;
  private _totalDebit: number; private _totalCredit: number;
  private _transactionCount: number; private _source: StatementSource;
  private _importedAt: Date | null; private _importedBy: string | null;
  private _hash: string | null; private _isReconciled: boolean; private _isLocked: boolean;
  private _notes: string | null;
  private _lines: BankStatementLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: BankStatementId, bankAccountId: string, statementNumber: string,
    periodStart: Date, periodEnd: Date, openingBalance: number, closingBalance: number) {
    super(); this._id = id; this._bankAccountId = bankAccountId;
    this._statementNumber = statementNumber; this._periodStart = periodStart; this._periodEnd = periodEnd;
    this._openingBalance = openingBalance; this._closingBalance = closingBalance;
    this._totalDebit = 0; this._totalCredit = 0; this._transactionCount = 0;
    this._source = StatementSource.Manual; this._importedAt = null; this._importedBy = null;
    this._hash = null; this._isReconciled = false; this._isLocked = false; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    bankAccountId: string; statementNumber: string; periodStart: Date; periodEnd: Date;
    openingBalance: number; closingBalance: number; source?: StatementSource;
    importedBy?: string; notes?: string;
  }): BankStatement {
    const s = new BankStatement(BankStatementId.new(), p.bankAccountId, p.statementNumber,
      p.periodStart, p.periodEnd, p.openingBalance, p.closingBalance);
    s._source = p.source ?? StatementSource.Manual; s._importedBy = p.importedBy ?? null;
    s._importedAt = new Date(); s._notes = p.notes ?? null;
    s.addEvent(new StatementImported(s._id.value, new Date(), {
      statementNumber: s._statementNumber, bankAccountId: s._bankAccountId, source: s._source,
    }));
    return s;
  }

  static load(s: BankStatementState): BankStatement {
    const stmt = new BankStatement(new BankStatementId(s.id), s.bankAccountId, s.statementNumber,
      s.periodStart, s.periodEnd, s.openingBalance, s.closingBalance);
    stmt._totalDebit = s.totalDebit; stmt._totalCredit = s.totalCredit;
    stmt._transactionCount = s.transactionCount; stmt._source = s.source as StatementSource;
    stmt._importedAt = s.importedAt; stmt._importedBy = s.importedBy;
    stmt._hash = s.hash; stmt._isReconciled = s.isReconciled; stmt._isLocked = s.isLocked;
    stmt._notes = s.notes; stmt._version = s.version;
    stmt._createdAt = s.createdAt; stmt._updatedAt = s.updatedAt; stmt._deletedAt = s.deletedAt;
    return stmt;
  }

  get id(): BankStatementId { return this._id; }
  get bankAccountId(): string { return this._bankAccountId; }
  get statementNumber(): string { return this._statementNumber; }
  get openingBalance(): number { return this._openingBalance; }
  get closingBalance(): number { return this._closingBalance; }
  get totalDebit(): number { return this._totalDebit; }
  get totalCredit(): number { return this._totalCredit; }
  get isReconciled(): boolean { return this._isReconciled; }
  get isLocked(): boolean { return this._isLocked; }
  get lines(): readonly BankStatementLine[] { return this._lines; }
  get source(): StatementSource { return this._source; }
  get version(): number { return this._version; }

  addLine(p: {
    lineDate: Date; lineType: string; amount: number; runningBalance: number;
    description?: string | null; reference?: string | null; chequeNumber?: string | null;
    currencyCode?: string;
  }): BankStatementLine {
    if (this._isReconciled) throw new DomainError("BusinessRule", "Cannot modify reconciled statement");
    if (this._isLocked) throw new DomainError("BusinessRule", "Cannot modify locked statement");
    const line = new BankStatementLine(BankStatementLineId.new(), this._id.value,
      p.lineDate, p.lineType, p.amount, p.runningBalance, p.currencyCode ?? "VND",
      p.description ?? null, p.reference ?? null, p.chequeNumber ?? null);
    this._lines.push(line);
    if (p.lineType === "debit" || p.lineType === "fee" || p.lineType === "chargeback") {
      this._totalDebit += p.amount;
    } else {
      this._totalCredit += p.amount;
    }
    this._transactionCount++; this._updatedAt = new Date(); this._version++;
    return line;
  }

  addLines(lines: Array<Omit<Parameters<typeof this.addLine>[0], never>>): void {
    for (const line of lines) this.addLine(line);
  }

  validateBalance(): boolean {
    const expected = this._openingBalance + this._totalCredit - this._totalDebit;
    if (Math.abs(expected - this._closingBalance) > 0.01) {
      throw new DomainError("BusinessRule",
        `Statement ${this._statementNumber} does not balance. Expected closing: ${expected}, Got: ${this._closingBalance}`);
    }
    this.addEvent(new StatementBalanceValidated(this._id.value, new Date(), {
      statementNumber: this._statementNumber, expected, actual: this._closingBalance,
    }));
    return true;
  }

  markReconciled(): void {
    if (this._isReconciled) throw new DomainError("BusinessRule", "Statement already reconciled");
    this._isReconciled = true; this._updatedAt = new Date(); this._version++;
  }

  lock(): void {
    if (this._isLocked) throw new DomainError("BusinessRule", "Statement already locked");
    this._isLocked = true; this._updatedAt = new Date(); this._version++;
  }

  unlock(): void {
    if (!this._isLocked) throw new DomainError("BusinessRule", "Statement not locked");
    if (this._isReconciled) throw new DomainError("BusinessRule", "Cannot unlock reconciled statement");
    this._isLocked = false; this._updatedAt = new Date(); this._version++;
  }

  toState(): BankStatementState {
    return { id: this._id.value, bankAccountId: this._bankAccountId,
      statementNumber: this._statementNumber, periodStart: this._periodStart,
      periodEnd: this._periodEnd, openingBalance: this._openingBalance,
      closingBalance: this._closingBalance, totalDebit: this._totalDebit,
      totalCredit: this._totalCredit, transactionCount: this._transactionCount,
      source: this._source, importedAt: this._importedAt, importedBy: this._importedBy,
      hash: this._hash, isReconciled: this._isReconciled, isLocked: this._isLocked,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
