import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashAdvanceId, AdvanceSettlementId } from "./cm-ids.js";
import { CashAdvanceStatus } from "./cm-enums.js";
import { CashAdvanceDisbursed, AdvanceSettled } from "./cm-domain-events.js";

export interface CashAdvanceState {
  id: string;
  advanceNumber: string;
  companyId: string;
  employeeId: string;
  employeeName: string;
  amount: number;
  settledAmount: number;
  outstandingAmount: number;
  currencyCode: string;
  advanceDate: Date;
  expectedSettleDate: Date | null;
  purpose: string;
  status: string;
  approvedById: string | null;
  approvedAt: Date | null;
  disbursedById: string | null;
  disbursedAt: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashAdvance extends AggregateRoot<CashAdvanceId> {
  private _id: CashAdvanceId;
  private _advanceNumber: string;
  private _companyId: string;
  private _employeeId: string;
  private _employeeName: string;
  private _amount: number;
  private _settledAmount: number;
  private _outstandingAmount: number;
  private _currencyCode: string;
  private _advanceDate: Date;
  private _expectedSettleDate: Date | null;
  private _purpose: string;
  private _status: CashAdvanceStatus;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _disbursedById: string | null;
  private _disbursedAt: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: CashAdvanceId,
    advanceNumber: string,
    companyId: string,
    employeeId: string,
    employeeName: string,
    amount: number,
    advanceDate: Date,
    purpose: string,
    currencyCode: string,
    expectedSettleDate: Date | null = null,
  ) {
    super();
    this._id = id;
    this._advanceNumber = advanceNumber;
    this._companyId = companyId;
    this._employeeId = employeeId;
    this._employeeName = employeeName;
    this._amount = amount;
    this._settledAmount = 0;
    this._outstandingAmount = amount;
    this._currencyCode = currencyCode;
    this._advanceDate = advanceDate;
    this._expectedSettleDate = expectedSettleDate;
    this._purpose = purpose;
    this._status = CashAdvanceStatus.Draft;
    this._approvedById = null;
    this._approvedAt = null;
    this._disbursedById = null;
    this._disbursedAt = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    advanceNumber: string;
    companyId: string;
    employeeId: string;
    employeeName: string;
    amount: number;
    advanceDate: Date;
    purpose: string;
    currencyCode?: string;
    expectedSettleDate?: Date | null;
    notes?: string | null;
  }): CashAdvance {
    const a = new CashAdvance(
      CashAdvanceId.new(),
      params.advanceNumber,
      params.companyId,
      params.employeeId,
      params.employeeName,
      params.amount,
      params.advanceDate,
      params.purpose,
      params.currencyCode ?? "VND",
      params.expectedSettleDate ?? null,
    );
    a._notes = params.notes ?? null;
    return a;
  }

  static load(state: CashAdvanceState): CashAdvance {
    const a = new CashAdvance(
      new CashAdvanceId(state.id),
      state.advanceNumber,
      state.companyId,
      state.employeeId,
      state.employeeName,
      state.amount,
      state.advanceDate,
      state.purpose,
      state.currencyCode,
      state.expectedSettleDate,
    );
    a._settledAmount = state.settledAmount;
    a._outstandingAmount = state.outstandingAmount;
    a._status = state.status as CashAdvanceStatus;
    a._approvedById = state.approvedById;
    a._approvedAt = state.approvedAt;
    a._disbursedById = state.disbursedById;
    a._disbursedAt = state.disbursedAt;
    a._notes = state.notes;
    a._version = state.version;
    a._createdAt = state.createdAt;
    a._updatedAt = state.updatedAt;
    a._deletedAt = state.deletedAt;
    return a;
  }

  get id(): CashAdvanceId { return this._id; }
  get advanceNumber(): string { return this._advanceNumber; }
  get companyId(): string { return this._companyId; }
  get employeeId(): string { return this._employeeId; }
  get employeeName(): string { return this._employeeName; }
  get amount(): number { return this._amount; }
  get settledAmount(): number { return this._settledAmount; }
  get outstandingAmount(): number { return this._outstandingAmount; }
  get currencyCode(): string { return this._currencyCode; }
  get advanceDate(): Date { return this._advanceDate; }
  get expectedSettleDate(): Date | null { return this._expectedSettleDate; }
  get purpose(): string { return this._purpose; }
  get status(): CashAdvanceStatus { return this._status; }
  get approvedById(): string | null { return this._approvedById; }
  get disbursedById(): string | null { return this._disbursedById; }
  get notes(): string | null { return this._notes; }
  get version(): number { return this._version; }

  approve(userId: string): void {
    if (this._status !== CashAdvanceStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft advances can be approved");
    }
    this._status = CashAdvanceStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  disburse(userId: string): void {
    if (this._status !== CashAdvanceStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved advances can be disbursed");
    }
    this._status = CashAdvanceStatus.Disbursed;
    this._disbursedById = userId;
    this._disbursedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashAdvanceDisbursed(this._id.value, new Date(), {
      advanceNumber: this._advanceNumber,
      employeeId: this._employeeId,
      amount: this._amount,
    }));
  }

  settle(settlement: AdvanceSettlement): void {
    if (this._status !== CashAdvanceStatus.Disbursed && this._status !== CashAdvanceStatus.PartiallySettled) {
      throw new DomainError("BusinessRule", "Advance must be disbursed before settlement");
    }
    this._settledAmount += settlement.totalAmount;
    this._outstandingAmount = this._amount - this._settledAmount;
    this._updatedAt = new Date();
    this._version++;

    if (this._outstandingAmount <= 0) {
      this._status = CashAdvanceStatus.Settled;
    } else {
      this._status = CashAdvanceStatus.PartiallySettled;
    }

    this.addEvent(new AdvanceSettled(this._id.value, new Date(), {
      advanceNumber: this._advanceNumber,
      settledAmount: settlement.totalAmount,
      outstanding: this._outstandingAmount,
    }));
  }

  cancel(): void {
    if (this._status === CashAdvanceStatus.Settled) {
      throw new DomainError("BusinessRule", "Cannot cancel settled advance");
    }
    if (this._status === CashAdvanceStatus.Disbursed) {
      throw new DomainError("BusinessRule", "Cannot cancel disbursed advance, must settle first");
    }
    this._status = CashAdvanceStatus.Cancelled;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CashAdvanceState {
    return {
      id: this._id.value,
      advanceNumber: this._advanceNumber,
      companyId: this._companyId,
      employeeId: this._employeeId,
      employeeName: this._employeeName,
      amount: this._amount,
      settledAmount: this._settledAmount,
      outstandingAmount: this._outstandingAmount,
      currencyCode: this._currencyCode,
      advanceDate: this._advanceDate,
      expectedSettleDate: this._expectedSettleDate,
      purpose: this._purpose,
      status: this._status,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      disbursedById: this._disbursedById,
      disbursedAt: this._disbursedAt,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export interface AdvanceSettlementState {
  id: string;
  advanceId: string;
  settlementNumber: string;
  settlementDate: Date;
  totalAmount: number;
  returnAmount: number;
  expenseAmount: number;
  additionalAdvance: number;
  currencyCode: string;
  receiptCount: number;
  approvedById: string | null;
  approvedAt: Date | null;
  notes: string | null;
  postedToGL: boolean;
  glBatchId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class AdvanceSettlement {
  private _id: AdvanceSettlementId;
  private _advanceId: string;
  private _settlementNumber: string;
  private _settlementDate: Date;
  private _totalAmount: number;
  private _returnAmount: number;
  private _expenseAmount: number;
  private _additionalAdvance: number;
  private _currencyCode: string;
  private _notes: string | null;

  constructor(
    id: AdvanceSettlementId,
    advanceId: string,
    settlementNumber: string,
    settlementDate: Date,
    totalAmount: number,
    returnAmount: number,
    expenseAmount: number,
    currencyCode: string,
    additionalAdvance: number = 0,
    notes: string | null = null,
  ) {
    if (totalAmount !== returnAmount + expenseAmount) {
      throw new DomainError("BusinessRule", "Total must equal return + expense");
    }
    this._id = id;
    this._advanceId = advanceId;
    this._settlementNumber = settlementNumber;
    this._settlementDate = settlementDate;
    this._totalAmount = totalAmount;
    this._returnAmount = returnAmount;
    this._expenseAmount = expenseAmount;
    this._additionalAdvance = additionalAdvance;
    this._currencyCode = currencyCode;
    this._notes = notes;
  }

  get id(): AdvanceSettlementId { return this._id; }
  get advanceId(): string { return this._advanceId; }
  get settlementNumber(): string { return this._settlementNumber; }
  get settlementDate(): Date { return this._settlementDate; }
  get totalAmount(): number { return this._totalAmount; }
  get returnAmount(): number { return this._returnAmount; }
  get expenseAmount(): number { return this._expenseAmount; }
  get additionalAdvance(): number { return this._additionalAdvance; }
  get currencyCode(): string { return this._currencyCode; }
  get notes(): string | null { return this._notes; }
}
