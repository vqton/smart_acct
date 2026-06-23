import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxReturnId extends Identifier {
  static new(): TaxReturnId { return new TaxReturnId(IdGenerator.uuid()); }
}

export class TaxPaymentId extends Identifier {
  static new(): TaxPaymentId { return new TaxPaymentId(IdGenerator.uuid()); }
}

export enum TaxReturnStatus {
  Draft = "draft",
  Prepared = "prepared",
  Submitted = "submitted",
  Accepted = "accepted",
  Rejected = "rejected",
  Amended = "amended",
  UnderAudit = "under_audit",
  Closed = "closed",
}

export enum TaxReturnType {
  Original = "original",
  Amendment = "amendment",
  Supplementary = "supplementary",
  Finalization = "finalization",
  Provisional = "provisional",
}

export enum TaxPaymentStatus {
  Unpaid = "unpaid",
  Partial = "partial",
  Paid = "paid",
  Overpaid = "overpaid",
  Refunded = "refunded",
  Offset = "offset",
}

export class TaxReturnSubmitted implements DomainEvent {
  readonly eventName = "TaxReturnSubmitted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export interface TaxLineItem {
  id: string;
  taxCodeId: string;
  taxCode: string;
  description: string;
  taxableAmount: number;
  taxRate: number;
  taxAmount: number;
  exemptAmount: number;
  deductibleAmount: number;
  recoverableAmount: number;
  isExempt: boolean;
  isZeroRated: boolean;
  lineOrder: number;
}

export interface TaxReturnState {
  id: string;
  returnNumber: string;
  taxTypeId: string;
  taxpayerId: string;
  taxAuthorityId: string;
  periodId: string;
  fiscalYearId: string;
  returnType: TaxReturnType;
  status: TaxReturnStatus;
  filingDate: Date;
  dueDate: Date;
  submittedAt: Date | null;
  totalTaxableAmount: number;
  totalTaxAmount: number;
  totalExemptAmount: number;
  totalDeductibleAmount: number;
  totalRecoverableAmount: number;
  totalPaymentAmount: number;
  totalCreditAmount: number;
  totalPenaltyAmount: number;
  totalInterestAmount: number;
  netPayableAmount: number;
  currencyCode: string;
  exchangeRate: number;
  lines: TaxLineItem[];
  attachments: string[];
  notes: string | null;
  createdById: string;
  approvedById: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxReturn extends AggregateRoot<TaxReturnId> {
  private _id: TaxReturnId;
  private _returnNumber!: string;
  private _taxTypeId!: string;
  private _taxpayerId!: string;
  private _taxAuthorityId!: string;
  private _periodId!: string;
  private _fiscalYearId!: string;
  private _returnType!: TaxReturnType;
  private _status: TaxReturnStatus;
  private _filingDate!: Date;
  private _dueDate!: Date;
  private _submittedAt: Date | null;
  private _totalTaxableAmount = 0;
  private _totalTaxAmount = 0;
  private _totalExemptAmount = 0;
  private _totalDeductibleAmount = 0;
  private _totalRecoverableAmount = 0;
  private _totalPaymentAmount = 0;
  private _totalCreditAmount = 0;
  private _totalPenaltyAmount = 0;
  private _totalInterestAmount = 0;
  private _netPayableAmount = 0;
  private _currencyCode = "VND";
  private _exchangeRate = 1;
  private _lines: TaxLineItem[] = [];
  private _attachments: string[] = [];
  private _notes: string | null;
  private _createdById!: string;
  private _approvedById: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  private constructor(id: TaxReturnId) {
    super();
    this._id = id;
    this._status = TaxReturnStatus.Draft;
    this._submittedAt = null;
    this._notes = null;
    this._approvedById = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static create(params: {
    returnNumber: string; taxTypeId: string; taxpayerId: string; taxAuthorityId: string;
    periodId: string; fiscalYearId: string; returnType: TaxReturnType;
    filingDate: Date; dueDate: Date; createdById: string;
  }): TaxReturn {
    const tr = new TaxReturn(TaxReturnId.new());
    tr._returnNumber = params.returnNumber; tr._taxTypeId = params.taxTypeId;
    tr._taxpayerId = params.taxpayerId; tr._taxAuthorityId = params.taxAuthorityId;
    tr._periodId = params.periodId; tr._fiscalYearId = params.fiscalYearId;
    tr._returnType = params.returnType; tr._filingDate = params.filingDate;
    tr._dueDate = params.dueDate; tr._createdById = params.createdById;
    return tr;
  }

  static load(s: TaxReturnState): TaxReturn {
    const tr = new TaxReturn(new TaxReturnId(s.id));
    tr._returnNumber = s.returnNumber; tr._taxTypeId = s.taxTypeId;
    tr._taxpayerId = s.taxpayerId; tr._taxAuthorityId = s.taxAuthorityId;
    tr._periodId = s.periodId; tr._fiscalYearId = s.fiscalYearId;
    tr._returnType = s.returnType; tr._status = s.status;
    tr._filingDate = s.filingDate; tr._dueDate = s.dueDate; tr._submittedAt = s.submittedAt;
    tr._totalTaxableAmount = s.totalTaxableAmount; tr._totalTaxAmount = s.totalTaxAmount;
    tr._totalExemptAmount = s.totalExemptAmount; tr._totalDeductibleAmount = s.totalDeductibleAmount;
    tr._totalRecoverableAmount = s.totalRecoverableAmount; tr._totalPaymentAmount = s.totalPaymentAmount;
    tr._totalCreditAmount = s.totalCreditAmount; tr._totalPenaltyAmount = s.totalPenaltyAmount;
    tr._totalInterestAmount = s.totalInterestAmount; tr._netPayableAmount = s.netPayableAmount;
    tr._currencyCode = s.currencyCode; tr._exchangeRate = s.exchangeRate;
    tr._lines = s.lines; tr._attachments = s.attachments; tr._notes = s.notes;
    tr._createdById = s.createdById; tr._approvedById = s.approvedById;
    tr._createdAt = s.createdAt; tr._updatedAt = s.updatedAt; tr._version = s.version;
    return tr;
  }

  get id() { return this._id; }
  get returnNumber() { return this._returnNumber; }
  get taxTypeId() { return this._taxTypeId; }
  get status() { return this._status; }
  get totalTaxAmount() { return this._totalTaxAmount; }
  get totalDeductibleAmount() { return this._totalDeductibleAmount; }
  get netPayableAmount() { return this._netPayableAmount; }
  get lines() { return [...this._lines]; }
  get version() { return this._version; }

  addLine(line: Omit<TaxLineItem, "id" | "lineOrder">): void {
    if (this._status !== TaxReturnStatus.Draft) throw new DomainError("BusinessRule", "Cannot modify submitted return");
    const entry: TaxLineItem = { id: IdGenerator.uuid(), ...line, lineOrder: this._lines.length + 1 };
    this._lines.push(entry);
    this._totalTaxableAmount += line.taxableAmount;
    this._totalTaxAmount += line.taxAmount;
    this._totalExemptAmount += line.exemptAmount;
    this._totalDeductibleAmount += line.deductibleAmount;
    this._totalRecoverableAmount += line.recoverableAmount;
    this.recalculate();
    this._updatedAt = new Date(); this._version++;
  }

  submit(): void {
    if (this._status !== TaxReturnStatus.Draft && this._status !== TaxReturnStatus.Prepared) throw new DomainError("BusinessRule", "Only draft returns can be submitted");
    if (this._lines.length === 0) throw new DomainError("BusinessRule", "Cannot submit empty return");
    this._status = TaxReturnStatus.Submitted;
    this._submittedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new TaxReturnSubmitted(this._id.value, new Date(), { returnNumber: this._returnNumber }));
  }

  accept(): void {
    if (this._status !== TaxReturnStatus.Submitted) throw new DomainError("BusinessRule", "Only submitted returns can be accepted");
    this._status = TaxReturnStatus.Accepted;
    this._updatedAt = new Date(); this._version++;
  }

  reject(reason: string): void {
    if (this._status !== TaxReturnStatus.Submitted) throw new DomainError("BusinessRule", "Only submitted returns can be rejected");
    this._status = TaxReturnStatus.Rejected;
    this._notes = reason;
    this._updatedAt = new Date(); this._version++;
  }

  private recalculate(): void {
    this._netPayableAmount = this._totalTaxAmount - this._totalDeductibleAmount - this._totalCreditAmount + this._totalPenaltyAmount + this._totalInterestAmount - this._totalPaymentAmount;
  }

  toState(): TaxReturnState {
    return {
      id: this._id.value, returnNumber: this._returnNumber, taxTypeId: this._taxTypeId,
      taxpayerId: this._taxpayerId, taxAuthorityId: this._taxAuthorityId,
      periodId: this._periodId, fiscalYearId: this._fiscalYearId,
      returnType: this._returnType, status: this._status,
      filingDate: this._filingDate, dueDate: this._dueDate, submittedAt: this._submittedAt,
      totalTaxableAmount: this._totalTaxableAmount, totalTaxAmount: this._totalTaxAmount,
      totalExemptAmount: this._totalExemptAmount, totalDeductibleAmount: this._totalDeductibleAmount,
      totalRecoverableAmount: this._totalRecoverableAmount,
      totalPaymentAmount: this._totalPaymentAmount, totalCreditAmount: this._totalCreditAmount,
      totalPenaltyAmount: this._totalPenaltyAmount, totalInterestAmount: this._totalInterestAmount,
      netPayableAmount: this._netPayableAmount, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, lines: [...this._lines], attachments: [...this._attachments],
      notes: this._notes, createdById: this._createdById, approvedById: this._approvedById,
      createdAt: this._createdAt, updatedAt: this._updatedAt, version: this._version,
    };
  }
}
