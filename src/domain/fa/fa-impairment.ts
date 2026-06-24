import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaImpairmentId } from "./fa-ids.js";
import { FaImpairmentType } from "./fa-enums.js";

export interface FaImpairmentState {
  id: string; assetId: string; impairmentNumber: string;
  impairmentType: FaImpairmentType; impairmentDate: Date;
  carryingAmount: number; recoverableAmount: number;
  impairmentLoss: number; fairValueLessCost: number | null;
  valueInUse: number | null; impairmentReversal: number;
  isReversal: boolean; originalImpairmentId: string | null;
  reference: string | null; documentNumber: string | null;
  approvedById: string | null; approvedAt: Date | null;
  postedToGL: boolean; glBatchId: string | null;
  notes: string | null; version: number; createdAt: Date; updatedAt: Date;
}

export class FaImpairment extends AggregateRoot<FaImpairmentId> {
  private _id: FaImpairmentId;
  private _assetId: string;
  private _impairmentNumber: string;
  private _impairmentType: FaImpairmentType;
  private _impairmentDate: Date;
  private _carryingAmount: number;
  private _recoverableAmount: number;
  private _impairmentLoss: number;
  private _fairValueLessCost: number | null;
  private _valueInUse: number | null;
  private _impairmentReversal: number;
  private _isReversal: boolean;
  private _originalImpairmentId: string | null;
  private _reference: string | null;
  private _documentNumber: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(assetId: string, impairmentNumber: string) {
    super();
    this._id = FaImpairmentId.new();
    this._assetId = assetId;
    this._impairmentNumber = impairmentNumber;
    this._impairmentType = null as any;
    this._impairmentDate = new Date();
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._carryingAmount = 0;
    this._recoverableAmount = 0;
    this._impairmentLoss = 0;
    this._fairValueLessCost = null;
    this._valueInUse = null;
    this._impairmentReversal = 0;
    this._isReversal = false;
    this._originalImpairmentId = null;
    this._reference = null;
    this._documentNumber = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._glBatchId = null;
    this._notes = null;
  }

  static create(p: {
    assetId: string; impairmentNumber: string; impairmentType: FaImpairmentType;
    impairmentDate: Date; carryingAmount: number; recoverableAmount: number;
    impairmentLoss: number; fairValueLessCost?: number; valueInUse?: number;
    isReversal?: boolean; originalImpairmentId?: string;
    documentNumber?: string; notes?: string;
  }): FaImpairment {
    const i = new FaImpairment(p.assetId, p.impairmentNumber);
    i._impairmentType = p.impairmentType;
    i._impairmentDate = p.impairmentDate;
    i._carryingAmount = p.carryingAmount;
    i._recoverableAmount = p.recoverableAmount;
    i._impairmentLoss = p.impairmentLoss;
    if (p.fairValueLessCost !== undefined) i._fairValueLessCost = p.fairValueLessCost;
    if (p.valueInUse !== undefined) i._valueInUse = p.valueInUse;
    if (p.isReversal) { i._isReversal = true; i._impairmentReversal = p.impairmentLoss; }
    if (p.originalImpairmentId) i._originalImpairmentId = p.originalImpairmentId;
    if (p.documentNumber) i._documentNumber = p.documentNumber;
    if (p.notes) i._notes = p.notes;
    return i;
  }

  static load(s: FaImpairmentState): FaImpairment {
    const i = new FaImpairment(s.assetId, s.impairmentNumber);
    i._id = FaImpairmentId.from(s.id);
    i._impairmentType = s.impairmentType;
    i._impairmentDate = s.impairmentDate;
    i._carryingAmount = s.carryingAmount;
    i._recoverableAmount = s.recoverableAmount;
    i._impairmentLoss = s.impairmentLoss;
    i._fairValueLessCost = s.fairValueLessCost;
    i._valueInUse = s.valueInUse;
    i._impairmentReversal = s.impairmentReversal;
    i._isReversal = s.isReversal;
    i._originalImpairmentId = s.originalImpairmentId;
    i._reference = s.reference;
    i._documentNumber = s.documentNumber;
    i._approvedById = s.approvedById;
    i._approvedAt = s.approvedAt;
    i._postedToGL = s.postedToGL;
    i._glBatchId = s.glBatchId;
    i._notes = s.notes;
    i._version = s.version;
    i._createdAt = s.createdAt;
    i._updatedAt = s.updatedAt;
    return i;
  }

  get id() { return this._id; }
  get assetId() { return this._assetId; }
  get impairmentNumber() { return this._impairmentNumber; }
  get impairmentLoss() { return this._impairmentLoss; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaImpairmentState {
    return {
      id: this._id.value, assetId: this._assetId,
      impairmentNumber: this._impairmentNumber,
      impairmentType: this._impairmentType,
      impairmentDate: this._impairmentDate,
      carryingAmount: this._carryingAmount,
      recoverableAmount: this._recoverableAmount,
      impairmentLoss: this._impairmentLoss,
      fairValueLessCost: this._fairValueLessCost,
      valueInUse: this._valueInUse,
      impairmentReversal: this._impairmentReversal,
      isReversal: this._isReversal,
      originalImpairmentId: this._originalImpairmentId,
      reference: this._reference, documentNumber: this._documentNumber,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
