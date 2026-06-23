import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class JournalEntryId extends Identifier {
  static new(): JournalEntryId {
    return new JournalEntryId(IdGenerator.uuid());
  }
}

export class JournalBatchId extends Identifier {
  static new(): JournalBatchId {
    return new JournalBatchId(IdGenerator.uuid());
  }
}

export enum JournalEntryStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Posted = "posted",
  Reversed = "reversed",
  Cancelled = "cancelled",
}

export enum JournalType {
  Standard = "standard",
  Recurring = "recurring",
  Reversing = "reversing",
  Accrual = "accrual",
  Allocation = "allocation",
  Adjustment = "adjustment",
  Closing = "closing",
  Opening = "opening",
}

export interface JournalEntryLine {
  id: string;
  accountId: string;
  debitAmount: number;
  creditAmount: number;
  foreignDebitAmount: number;
  foreignCreditAmount: number;
  currencyCode: string;
  exchangeRate: number;
  description: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  lineOrder: number;
}

export interface JournalBatchState {
  id: string;
  batchNumber: string;
  journalType: JournalType;
  status: JournalEntryStatus;
  periodId: string;
  fiscalYearId: string;
  voucherTypeId: string | null;
  voucherSeriesId: string | null;
  voucherNumber: string | null;
  voucherDate: Date;
  postingDate: Date;
  description: string;
  reference: string | null;
  source: string | null;
  totalDebit: number;
  totalCredit: number;
  foreignTotalDebit: number;
  foreignTotalCredit: number;
  currencyCode: string;
  exchangeRate: number;
  isForeignCurrency: boolean;
  approvedById: string | null;
  approvedAt: Date | null;
  postedById: string | null;
  postedAt: Date | null;
  reversedBatchId: string | null;
  recurringTemplateId: string | null;
  attachmentCount: number;
  commentCount: number;
  lines: JournalEntryLine[];
  createdById: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export class JournalBatchPosted implements DomainEvent {
  readonly eventName = "JournalBatchPosted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class JournalBatchApproved implements DomainEvent {
  readonly eventName = "JournalBatchApproved";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class JournalBatch extends AggregateRoot<JournalBatchId> {
  private _id!: JournalBatchId;
  private _batchNumber!: string;
  private _journalType!: JournalType;
  private _status: JournalEntryStatus = JournalEntryStatus.Draft;
  private _periodId!: string;
  private _fiscalYearId!: string;
  private _voucherTypeId: string | null = null;
  private _voucherSeriesId: string | null = null;
  private _voucherNumber: string | null = null;
  private _voucherDate!: Date;
  private _postingDate!: Date;
  private _description!: string;
  private _reference: string | null = null;
  private _source: string | null = null;
  private _totalDebit = 0;
  private _totalCredit = 0;
  private _foreignTotalDebit = 0;
  private _foreignTotalCredit = 0;
  private _currencyCode = "VND";
  private _exchangeRate = 1;
  private _isForeignCurrency = false;
  private _approvedById: string | null = null;
  private _approvedAt: Date | null = null;
  private _postedById: string | null = null;
  private _postedAt: Date | null = null;
  private _reversedBatchId: string | null = null;
  private _recurringTemplateId: string | null = null;
  private _attachmentCount = 0;
  private _commentCount = 0;
  private _lines: JournalEntryLine[] = [];
  private _createdById!: string;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _version = 1;
  private _deletedAt: Date | null = null;

  private constructor(id: JournalBatchId) {
    super();
    this._id = id;
  }

  static create(params: {
    batchNumber: string;
    journalType: JournalType;
    periodId: string;
    fiscalYearId: string;
    voucherDate: Date;
    postingDate: Date;
    description: string;
    currencyCode?: string;
    exchangeRate?: number;
    createdById: string;
    voucherTypeId?: string;
    voucherSeriesId?: string;
    reference?: string;
    source?: string;
  }): JournalBatch {
    const batch = new JournalBatch(JournalBatchId.new());
    batch._batchNumber = params.batchNumber;
    batch._journalType = params.journalType;
    batch._periodId = params.periodId;
    batch._fiscalYearId = params.fiscalYearId;
    batch._voucherDate = params.voucherDate;
    batch._postingDate = params.postingDate;
    batch._description = params.description;
    batch._currencyCode = params.currencyCode ?? "VND";
    batch._exchangeRate = params.exchangeRate ?? 1;
    batch._createdById = params.createdById;
    batch._voucherTypeId = params.voucherTypeId ?? null;
    batch._voucherSeriesId = params.voucherSeriesId ?? null;
    batch._reference = params.reference ?? null;
    batch._source = params.source ?? null;

    if (batch._currencyCode !== "VND") {
      batch._isForeignCurrency = true;
    }

    return batch;
  }

  static load(state: JournalBatchState): JournalBatch {
    const batch = new JournalBatch(new JournalBatchId(state.id));
    batch._batchNumber = state.batchNumber;
    batch._journalType = state.journalType;
    batch._status = state.status;
    batch._periodId = state.periodId;
    batch._fiscalYearId = state.fiscalYearId;
    batch._voucherTypeId = state.voucherTypeId;
    batch._voucherSeriesId = state.voucherSeriesId;
    batch._voucherNumber = state.voucherNumber;
    batch._voucherDate = state.voucherDate;
    batch._postingDate = state.postingDate;
    batch._description = state.description;
    batch._reference = state.reference;
    batch._source = state.source;
    batch._totalDebit = state.totalDebit;
    batch._totalCredit = state.totalCredit;
    batch._foreignTotalDebit = state.foreignTotalDebit;
    batch._foreignTotalCredit = state.foreignTotalCredit;
    batch._currencyCode = state.currencyCode;
    batch._exchangeRate = state.exchangeRate;
    batch._isForeignCurrency = state.isForeignCurrency;
    batch._approvedById = state.approvedById;
    batch._approvedAt = state.approvedAt;
    batch._postedById = state.postedById;
    batch._postedAt = state.postedAt;
    batch._reversedBatchId = state.reversedBatchId;
    batch._recurringTemplateId = state.recurringTemplateId;
    batch._attachmentCount = state.attachmentCount;
    batch._commentCount = state.commentCount;
    batch._lines = state.lines;
    batch._createdById = state.createdById;
    batch._createdAt = state.createdAt;
    batch._updatedAt = state.updatedAt;
    batch._version = state.version;
    batch._deletedAt = state.deletedAt;
    return batch;
  }

  get id(): JournalBatchId { return this._id; }
  get batchNumber(): string { return this._batchNumber; }
  get journalType(): JournalType { return this._journalType; }
  get status(): JournalEntryStatus { return this._status; }
  get periodId(): string { return this._periodId; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get voucherTypeId(): string | null { return this._voucherTypeId; }
  get voucherSeriesId(): string | null { return this._voucherSeriesId; }
  get voucherNumber(): string | null { return this._voucherNumber; }
  get voucherDate(): Date { return this._voucherDate; }
  get postingDate(): Date { return this._postingDate; }
  get description(): string { return this._description; }
  get reference(): string | null { return this._reference; }
  get source(): string | null { return this._source; }
  get totalDebit(): number { return this._totalDebit; }
  get totalCredit(): number { return this._totalCredit; }
  get foreignTotalDebit(): number { return this._foreignTotalDebit; }
  get foreignTotalCredit(): number { return this._foreignTotalCredit; }
  get currencyCode(): string { return this._currencyCode; }
  get exchangeRate(): number { return this._exchangeRate; }
  get isForeignCurrency(): boolean { return this._isForeignCurrency; }
  get approvedById(): string | null { return this._approvedById; }
  get approvedAt(): Date | null { return this._approvedAt; }
  get postedById(): string | null { return this._postedById; }
  get postedAt(): Date | null { return this._postedAt; }
  get reversedBatchId(): string | null { return this._reversedBatchId; }
  get recurringTemplateId(): string | null { return this._recurringTemplateId; }
  get attachmentCount(): number { return this._attachmentCount; }
  get commentCount(): number { return this._commentCount; }
  get lines(): readonly JournalEntryLine[] { return this._lines; }
  get createdById(): string { return this._createdById; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  addLine(line: Omit<JournalEntryLine, "id" | "lineOrder">): void {
    if (this._status !== JournalEntryStatus.Draft) {
      throw new DomainError("BusinessRule", "Cannot modify posted batch");
    }
    if (line.debitAmount < 0 || line.creditAmount < 0) {
      throw new DomainError("Validation", "Amounts must be non-negative");
    }
    if (line.debitAmount === 0 && line.creditAmount === 0) {
      throw new DomainError("Validation", "Line must have debit or credit amount");
    }

    const entry: JournalEntryLine = {
      id: IdGenerator.uuid(),
      ...line,
      lineOrder: this._lines.length + 1,
    };

    this._lines.push(entry);
    this._totalDebit += entry.debitAmount;
    this._totalCredit += entry.creditAmount;
    this._foreignTotalDebit += entry.foreignDebitAmount;
    this._foreignTotalCredit += entry.foreignCreditAmount;
    this._updatedAt = new Date();
    this._version++;
  }

  validateDebitCreditEqual(): void {
    if (this._totalDebit !== this._totalCredit) {
      throw new DomainError(
        "BusinessRule",
        `Total debit (${this._totalDebit}) must equal total credit (${this._totalCredit})`,
      );
    }
  }

  submit(): void {
    if (this._status !== JournalEntryStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft batches can be submitted");
    }
    if (this._lines.length === 0) {
      throw new DomainError("BusinessRule", "Cannot submit empty batch");
    }
    this.validateDebitCreditEqual();
    this._status = JournalEntryStatus.Submitted;
    this._updatedAt = new Date();
    this._version++;
  }

  approve(userId: string): void {
    if (this._status !== JournalEntryStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only submitted batches can be approved");
    }
    this._status = JournalEntryStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new JournalBatchApproved(this._id.value, new Date(), {
      userId,
      batchNumber: this._batchNumber,
    }));
  }

  post(userId: string): void {
    if (this._status !== JournalEntryStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved batches can be posted");
    }
    this.validateDebitCreditEqual();
    this._status = JournalEntryStatus.Posted;
    this._postedById = userId;
    this._postedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new JournalBatchPosted(this._id.value, new Date(), {
      userId,
      batchNumber: this._batchNumber,
      totalDebit: this._totalDebit,
      totalCredit: this._totalCredit,
    }));
  }

  reverse(reverseBatchNumber: string): void {
    if (this._status !== JournalEntryStatus.Posted) {
      throw new DomainError("BusinessRule", "Only posted batches can be reversed");
    }
    this._status = JournalEntryStatus.Reversed;
    this._updatedAt = new Date();
    this._version++;
  }

  cancel(): void {
    if (this._status === JournalEntryStatus.Posted) {
      throw new DomainError("BusinessRule", "Posted batches must be reversed, not cancelled");
    }
    this._status = JournalEntryStatus.Cancelled;
    this._updatedAt = new Date();
    this._version++;
  }

  markDeleted(): void {
    if (this._status === JournalEntryStatus.Posted) {
      throw new DomainError("BusinessRule", "Cannot delete posted batch");
    }
    this._deletedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): JournalBatchState {
    return {
      id: this._id.value,
      batchNumber: this._batchNumber,
      journalType: this._journalType,
      status: this._status,
      periodId: this._periodId,
      fiscalYearId: this._fiscalYearId,
      voucherTypeId: this._voucherTypeId,
      voucherSeriesId: this._voucherSeriesId,
      voucherNumber: this._voucherNumber,
      voucherDate: this._voucherDate,
      postingDate: this._postingDate,
      description: this._description,
      reference: this._reference,
      source: this._source,
      totalDebit: this._totalDebit,
      totalCredit: this._totalCredit,
      foreignTotalDebit: this._foreignTotalDebit,
      foreignTotalCredit: this._foreignTotalCredit,
      currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      isForeignCurrency: this._isForeignCurrency,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      postedById: this._postedById,
      postedAt: this._postedAt,
      reversedBatchId: this._reversedBatchId,
      recurringTemplateId: this._recurringTemplateId,
      attachmentCount: this._attachmentCount,
      commentCount: this._commentCount,
      lines: [...this._lines],
      createdById: this._createdById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}
