import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FaLeaseId } from "./fa-ids.js";
import { FaLeaseType, FaLeasePaymentFrequency } from "./fa-enums.js";
import { FaLeaseCreated, FaLeasePaymentMade } from "./fa-events.js";

export interface FaLeaseState {
  id: string; leaseNumber: string; leaseType: FaLeaseType;
  assetId: string | null; lessorId: string | null;
  lessorName: string | null; startDate: Date; endDate: Date;
  leaseTermMonths: number; paymentAmount: number;
  paymentFrequency: FaLeasePaymentFrequency;
  totalLeaseLiability: number; interestRate: number | null;
  incrementalRate: number | null; rightOfUseAsset: number;
  accumulatedAmortization: number; currencyCode: string;
  renewalOption: boolean; purchaseOption: boolean;
  terminationOption: boolean; status: string | null;
  reference: string | null; contractFile: string | null;
  notes: string | null; postedToGL: boolean;
  glBatchId: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaLease extends AggregateRoot<FaLeaseId> {
  private _id: FaLeaseId;
  private _leaseNumber: string;
  private _leaseType: FaLeaseType;
  private _assetId: string | null;
  private _lessorId: string | null;
  private _lessorName: string | null;
  private _startDate: Date;
  private _endDate: Date;
  private _leaseTermMonths: number;
  private _paymentAmount: number;
  private _paymentFrequency: FaLeasePaymentFrequency;
  private _totalLeaseLiability: number;
  private _interestRate: number | null;
  private _incrementalRate: number | null;
  private _rightOfUseAsset: number;
  private _accumulatedAmortization: number;
  private _currencyCode: string;
  private _renewalOption: boolean;
  private _purchaseOption: boolean;
  private _terminationOption: boolean;
  private _status: string | null;
  private _reference: string | null;
  private _contractFile: string | null;
  private _notes: string | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(leaseNumber: string, leaseType: FaLeaseType, startDate: Date, endDate: Date) {
    super();
    this._id = FaLeaseId.new();
    this._leaseNumber = leaseNumber;
    this._leaseType = leaseType;
    this._startDate = startDate;
    this._endDate = endDate;
    this._paymentFrequency = FaLeasePaymentFrequency.Monthly;
    this._currencyCode = "VND";
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._assetId = null;
    this._lessorId = null;
    this._lessorName = null;
    this._leaseTermMonths = 0;
    this._paymentAmount = 0;
    this._totalLeaseLiability = 0;
    this._interestRate = null;
    this._incrementalRate = null;
    this._rightOfUseAsset = 0;
    this._accumulatedAmortization = 0;
    this._renewalOption = false;
    this._purchaseOption = false;
    this._terminationOption = false;
    this._status = "active";
    this._reference = null;
    this._contractFile = null;
    this._notes = null;
    this._glBatchId = null;
  }

  static create(p: {
    leaseNumber: string; leaseType: FaLeaseType; startDate: Date; endDate: Date;
    paymentAmount: number; totalLeaseLiability: number;
    leaseTermMonths?: number; paymentFrequency?: FaLeasePaymentFrequency;
    interestRate?: number; incrementalRate?: number;
    rightOfUseAsset?: number; currencyCode?: string;
    lessorId?: string; lessorName?: string; assetId?: string;
    renewalOption?: boolean; purchaseOption?: boolean;
    terminationOption?: boolean; reference?: string; notes?: string;
  }): FaLease {
    if (p.endDate <= p.startDate) throw new DomainError("BusinessRule", "Lease end must be after start");
    const l = new FaLease(p.leaseNumber, p.leaseType, p.startDate, p.endDate);
    l._paymentAmount = p.paymentAmount;
    l._totalLeaseLiability = p.totalLeaseLiability;
    l._rightOfUseAsset = p.rightOfUseAsset ?? p.totalLeaseLiability;
    if (p.leaseTermMonths) l._leaseTermMonths = p.leaseTermMonths;
    if (p.paymentFrequency) l._paymentFrequency = p.paymentFrequency;
    if (p.interestRate) l._interestRate = p.interestRate;
    if (p.incrementalRate) l._incrementalRate = p.incrementalRate;
    if (p.currencyCode) l._currencyCode = p.currencyCode;
    if (p.lessorId) l._lessorId = p.lessorId;
    if (p.lessorName) l._lessorName = p.lessorName;
    if (p.assetId) l._assetId = p.assetId;
    if (p.renewalOption) l._renewalOption = true;
    if (p.purchaseOption) l._purchaseOption = true;
    if (p.terminationOption) l._terminationOption = true;
    if (p.reference) l._reference = p.reference;
    if (p.notes) l._notes = p.notes;
    l.addEvent(FaLeaseCreated.create(l._id.value, { leaseNumber: p.leaseNumber }));
    return l;
  }

  static load(s: FaLeaseState): FaLease {
    const l = new FaLease(s.leaseNumber, s.leaseType, s.startDate, s.endDate);
    l._id = FaLeaseId.from(s.id);
    l._assetId = s.assetId;
    l._lessorId = s.lessorId;
    l._lessorName = s.lessorName;
    l._leaseTermMonths = s.leaseTermMonths;
    l._paymentAmount = s.paymentAmount;
    l._paymentFrequency = s.paymentFrequency;
    l._totalLeaseLiability = s.totalLeaseLiability;
    l._interestRate = s.interestRate;
    l._incrementalRate = s.incrementalRate;
    l._rightOfUseAsset = s.rightOfUseAsset;
    l._accumulatedAmortization = s.accumulatedAmortization;
    l._currencyCode = s.currencyCode;
    l._renewalOption = s.renewalOption;
    l._purchaseOption = s.purchaseOption;
    l._terminationOption = s.terminationOption;
    l._status = s.status;
    l._reference = s.reference;
    l._contractFile = s.contractFile;
    l._notes = s.notes;
    l._postedToGL = s.postedToGL;
    l._glBatchId = s.glBatchId;
    l._version = s.version;
    l._createdAt = s.createdAt;
    l._updatedAt = s.updatedAt;
    return l;
  }

  get id() { return this._id; }
  get leaseNumber() { return this._leaseNumber; }
  get leaseType() { return this._leaseType; }
  get assetId() { return this._assetId; }
  get startDate() { return this._startDate; }
  get endDate() { return this._endDate; }
  get paymentAmount() { return this._paymentAmount; }
  get totalLeaseLiability() { return this._totalLeaseLiability; }
  get rightOfUseAsset() { return this._rightOfUseAsset; }
  get accumulatedAmortization() { return this._accumulatedAmortization; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  recordPayment(amount: number, interestAmount: number): void {
    const principal = amount - interestAmount;
    this._totalLeaseLiability -= principal;
    this._accumulatedAmortization += principal;
    this._updatedAt = new Date();
    this.addEvent(FaLeasePaymentMade.create(this._id.value, { amount, interestAmount, principal }));
  }

  terminate(): void {
    this._status = "terminated";
    this._updatedAt = new Date();
  }

  modify(p: { paymentAmount?: number; interestRate?: number; endDate?: Date }): void {
    if (p.paymentAmount !== undefined) this._paymentAmount = p.paymentAmount;
    if (p.interestRate !== undefined) this._interestRate = p.interestRate;
    if (p.endDate !== undefined) this._endDate = p.endDate;
    this._updatedAt = new Date();
  }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaLeaseState {
    return {
      id: this._id.value, leaseNumber: this._leaseNumber,
      leaseType: this._leaseType, assetId: this._assetId,
      lessorId: this._lessorId, lessorName: this._lessorName,
      startDate: this._startDate, endDate: this._endDate,
      leaseTermMonths: this._leaseTermMonths,
      paymentAmount: this._paymentAmount,
      paymentFrequency: this._paymentFrequency,
      totalLeaseLiability: this._totalLeaseLiability,
      interestRate: this._interestRate, incrementalRate: this._incrementalRate,
      rightOfUseAsset: this._rightOfUseAsset,
      accumulatedAmortization: this._accumulatedAmortization,
      currencyCode: this._currencyCode,
      renewalOption: this._renewalOption, purchaseOption: this._purchaseOption,
      terminationOption: this._terminationOption,
      status: this._status, reference: this._reference,
      contractFile: this._contractFile, notes: this._notes,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
