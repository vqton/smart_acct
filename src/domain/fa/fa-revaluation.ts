import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaRevaluationId } from "./fa-ids.js";
import { FaRevaluationType } from "./fa-enums.js";

export interface FaRevaluationState {
  id: string; assetId: string; revaluationNumber: string;
  revaluationType: FaRevaluationType; revaluationDate: Date;
  previousValue: number; revaluedAmount: number; newValue: number;
  accumulatedDepreciationBefore: number; accumulatedDepreciationAfter: number;
  revaluationReserve: number; reserveAccountId: string | null;
  reference: string | null; referenceId: string | null;
  documentNumber: string | null; approvedById: string | null;
  approvedAt: Date | null; postedToGL: boolean; glBatchId: string | null;
  notes: string | null; version: number; createdAt: Date; updatedAt: Date;
}

export class FaRevaluation extends AggregateRoot<FaRevaluationId> {
  private _id: FaRevaluationId;
  private _assetId: string;
  private _revaluationNumber: string;
  private _revaluationType: FaRevaluationType;
  private _revaluationDate: Date;
  private _previousValue: number;
  private _revaluedAmount: number;
  private _newValue: number;
  private _accumulatedDepreciationBefore: number;
  private _accumulatedDepreciationAfter: number;
  private _revaluationReserve: number;
  private _reserveAccountId: string | null;
  private _reference: string | null;
  private _referenceId: string | null;
  private _documentNumber: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(assetId: string, revaluationNumber: string) {
    super();
    this._id = FaRevaluationId.new();
    this._assetId = assetId;
    this._revaluationNumber = revaluationNumber;
    this._revaluationType = null as any;
    this._revaluationDate = new Date();
    this._previousValue = 0;
    this._revaluedAmount = 0;
    this._newValue = 0;
    this._accumulatedDepreciationBefore = 0;
    this._accumulatedDepreciationAfter = 0;
    this._revaluationReserve = 0;
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._reserveAccountId = null;
    this._reference = null;
    this._referenceId = null;
    this._documentNumber = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._glBatchId = null;
    this._notes = null;
  }

  static create(p: {
    assetId: string; revaluationNumber: string; revaluationType: FaRevaluationType;
    revaluationDate: Date; previousValue: number; revaluedAmount: number;
    newValue: number; accumulatedDepreciationBefore: number;
    accumulatedDepreciationAfter: number; revaluationReserve: number;
    reserveAccountId?: string; documentNumber?: string; notes?: string;
  }): FaRevaluation {
    const r = new FaRevaluation(p.assetId, p.revaluationNumber);
    r._revaluationType = p.revaluationType;
    r._revaluationDate = p.revaluationDate;
    r._previousValue = p.previousValue;
    r._revaluedAmount = p.revaluedAmount;
    r._newValue = p.newValue;
    r._accumulatedDepreciationBefore = p.accumulatedDepreciationBefore;
    r._accumulatedDepreciationAfter = p.accumulatedDepreciationAfter;
    r._revaluationReserve = p.revaluationReserve;
    if (p.reserveAccountId) r._reserveAccountId = p.reserveAccountId;
    if (p.documentNumber) r._documentNumber = p.documentNumber;
    if (p.notes) r._notes = p.notes;
    return r;
  }

  static load(s: FaRevaluationState): FaRevaluation {
    const r = new FaRevaluation(s.assetId, s.revaluationNumber);
    r._id = FaRevaluationId.from(s.id);
    r._revaluationType = s.revaluationType;
    r._revaluationDate = s.revaluationDate;
    r._previousValue = s.previousValue;
    r._revaluedAmount = s.revaluedAmount;
    r._newValue = s.newValue;
    r._accumulatedDepreciationBefore = s.accumulatedDepreciationBefore;
    r._accumulatedDepreciationAfter = s.accumulatedDepreciationAfter;
    r._revaluationReserve = s.revaluationReserve;
    r._reserveAccountId = s.reserveAccountId;
    r._reference = s.reference;
    r._referenceId = s.referenceId;
    r._documentNumber = s.documentNumber;
    r._approvedById = s.approvedById;
    r._approvedAt = s.approvedAt;
    r._postedToGL = s.postedToGL;
    r._glBatchId = s.glBatchId;
    r._notes = s.notes;
    r._version = s.version;
    r._createdAt = s.createdAt;
    r._updatedAt = s.updatedAt;
    return r;
  }

  get id() { return this._id; }
  get assetId() { return this._assetId; }
  get revaluationNumber() { return this._revaluationNumber; }
  get revaluationType() { return this._revaluationType; }
  get revaluationDate() { return this._revaluationDate; }
  get revaluedAmount() { return this._revaluedAmount; }
  get newValue() { return this._newValue; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaRevaluationState {
    return {
      id: this._id.value, assetId: this._assetId,
      revaluationNumber: this._revaluationNumber,
      revaluationType: this._revaluationType,
      revaluationDate: this._revaluationDate,
      previousValue: this._previousValue,
      revaluedAmount: this._revaluedAmount,
      newValue: this._newValue,
      accumulatedDepreciationBefore: this._accumulatedDepreciationBefore,
      accumulatedDepreciationAfter: this._accumulatedDepreciationAfter,
      revaluationReserve: this._revaluationReserve,
      reserveAccountId: this._reserveAccountId,
      reference: this._reference, referenceId: this._referenceId,
      documentNumber: this._documentNumber,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
