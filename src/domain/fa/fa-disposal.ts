import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaDisposalId } from "./fa-ids.js";
import { FaDisposalType } from "./fa-enums.js";

export interface FaDisposalState {
  id: string; assetId: string; disposalNumber: string;
  disposalType: FaDisposalType; disposalDate: Date;
  originalCost: number; accumulatedDepreciation: number;
  netBookValue: number; disposalProceeds: number;
  disposalCosts: number; gainOnDisposal: number;
  lossOnDisposal: number; vatAmount: number;
  customerId: string | null; customerName: string | null;
  invoiceNumber: string | null; invoiceDate: Date | null;
  reason: string | null; reference: string | null;
  documentNumber: string | null; approvedById: string | null;
  approvedAt: Date | null; postedToGL: boolean;
  glBatchId: string | null; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaDisposal extends AggregateRoot<FaDisposalId> {
  private _id: FaDisposalId;
  private _assetId: string;
  private _disposalNumber: string;
  private _disposalType: FaDisposalType;
  private _disposalDate: Date;
  private _originalCost: number;
  private _accumulatedDepreciation: number;
  private _netBookValue: number;
  private _disposalProceeds: number;
  private _disposalCosts: number;
  private _gainOnDisposal: number;
  private _lossOnDisposal: number;
  private _vatAmount: number;
  private _customerId: string | null;
  private _customerName: string | null;
  private _invoiceNumber: string | null;
  private _invoiceDate: Date | null;
  private _reason: string | null;
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

  private constructor(assetId: string, disposalNumber: string, disposalType: FaDisposalType, disposalDate: Date) {
    super();
    this._id = FaDisposalId.new();
    this._assetId = assetId;
    this._disposalNumber = disposalNumber;
    this._disposalType = disposalType;
    this._disposalDate = disposalDate;
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._originalCost = 0;
    this._accumulatedDepreciation = 0;
    this._netBookValue = 0;
    this._disposalProceeds = 0;
    this._disposalCosts = 0;
    this._gainOnDisposal = 0;
    this._lossOnDisposal = 0;
    this._vatAmount = 0;
    this._customerId = null;
    this._customerName = null;
    this._invoiceNumber = null;
    this._invoiceDate = null;
    this._reason = null;
    this._reference = null;
    this._documentNumber = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._glBatchId = null;
    this._notes = null;
  }

  static create(p: {
    assetId: string; disposalNumber: string; disposalType: FaDisposalType;
    disposalDate: Date; originalCost: number; accumulatedDepreciation: number;
    netBookValue: number; disposalProceeds: number; disposalCosts?: number;
    vatAmount?: number; customerId?: string; customerName?: string;
    invoiceNumber?: string; reason?: string; documentNumber?: string; notes?: string;
  }): FaDisposal {
    const d = new FaDisposal(p.assetId, p.disposalNumber, p.disposalType, p.disposalDate);
    d._originalCost = p.originalCost;
    d._accumulatedDepreciation = p.accumulatedDepreciation;
    d._netBookValue = p.netBookValue;
    d._disposalProceeds = p.disposalProceeds;
    d._disposalCosts = p.disposalCosts ?? 0;
    d._vatAmount = p.vatAmount ?? 0;
    if (p.customerId) d._customerId = p.customerId;
    if (p.customerName) d._customerName = p.customerName;
    if (p.invoiceNumber) d._invoiceNumber = p.invoiceNumber;
    if (p.reason) d._reason = p.reason;
    if (p.documentNumber) d._documentNumber = p.documentNumber;
    if (p.notes) d._notes = p.notes;
    const gainLoss = p.disposalProceeds - (d._disposalCosts) - p.netBookValue;
    if (gainLoss >= 0) {
      d._gainOnDisposal = gainLoss;
    } else {
      d._lossOnDisposal = Math.abs(gainLoss);
    }
    return d;
  }

  static load(s: FaDisposalState): FaDisposal {
    const d = new FaDisposal(s.assetId, s.disposalNumber, s.disposalType, s.disposalDate);
    d._id = FaDisposalId.from(s.id);
    d._originalCost = s.originalCost;
    d._accumulatedDepreciation = s.accumulatedDepreciation;
    d._netBookValue = s.netBookValue;
    d._disposalProceeds = s.disposalProceeds;
    d._disposalCosts = s.disposalCosts;
    d._gainOnDisposal = s.gainOnDisposal;
    d._lossOnDisposal = s.lossOnDisposal;
    d._vatAmount = s.vatAmount;
    d._customerId = s.customerId;
    d._customerName = s.customerName;
    d._invoiceNumber = s.invoiceNumber;
    d._invoiceDate = s.invoiceDate;
    d._reason = s.reason;
    d._reference = s.reference;
    d._documentNumber = s.documentNumber;
    d._approvedById = s.approvedById;
    d._approvedAt = s.approvedAt;
    d._postedToGL = s.postedToGL;
    d._glBatchId = s.glBatchId;
    d._notes = s.notes;
    d._version = s.version;
    d._createdAt = s.createdAt;
    d._updatedAt = s.updatedAt;
    return d;
  }

  get id() { return this._id; }
  get assetId() { return this._assetId; }
  get disposalNumber() { return this._disposalNumber; }
  get disposalType() { return this._disposalType; }
  get disposalDate() { return this._disposalDate; }
  get originalCost() { return this._originalCost; }
  get accumulatedDepreciation() { return this._accumulatedDepreciation; }
  get netBookValue() { return this._netBookValue; }
  get disposalProceeds() { return this._disposalProceeds; }
  get gainOnDisposal() { return this._gainOnDisposal; }
  get lossOnDisposal() { return this._lossOnDisposal; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaDisposalState {
    return {
      id: this._id.value, assetId: this._assetId,
      disposalNumber: this._disposalNumber,
      disposalType: this._disposalType, disposalDate: this._disposalDate,
      originalCost: this._originalCost,
      accumulatedDepreciation: this._accumulatedDepreciation,
      netBookValue: this._netBookValue,
      disposalProceeds: this._disposalProceeds,
      disposalCosts: this._disposalCosts,
      gainOnDisposal: this._gainOnDisposal,
      lossOnDisposal: this._lossOnDisposal,
      vatAmount: this._vatAmount,
      customerId: this._customerId, customerName: this._customerName,
      invoiceNumber: this._invoiceNumber, invoiceDate: this._invoiceDate,
      reason: this._reason, reference: this._reference,
      documentNumber: this._documentNumber,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
