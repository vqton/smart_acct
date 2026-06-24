import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaTransferId } from "./fa-ids.js";

export interface FaTransferState {
  id: string; assetId: string; transferNumber: string;
  transferDate: Date;
  fromBranchId: string | null; toBranchId: string | null;
  fromCompanyId: string | null; toCompanyId: string | null;
  fromCostCenterId: string | null; toCostCenterId: string | null;
  fromDepartmentId: string | null; toDepartmentId: string | null;
  fromLocationId: string | null; toLocationId: string | null;
  fromCustodianId: string | null; toCustodianId: string | null;
  fromCustodianName: string | null; toCustodianName: string | null;
  transferType: string | null; reason: string | null;
  reference: string | null; documentNumber: string | null;
  approvedById: string | null; approvedAt: Date | null;
  postedToGL: boolean; glBatchId: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaTransfer extends AggregateRoot<FaTransferId> {
  private _id: FaTransferId;
  private _assetId: string;
  private _transferNumber: string;
  private _transferDate: Date;
  private _fromBranchId: string | null;
  private _toBranchId: string | null;
  private _fromCompanyId: string | null;
  private _toCompanyId: string | null;
  private _fromCostCenterId: string | null;
  private _toCostCenterId: string | null;
  private _fromDepartmentId: string | null;
  private _toDepartmentId: string | null;
  private _fromLocationId: string | null;
  private _toLocationId: string | null;
  private _fromCustodianId: string | null;
  private _toCustodianId: string | null;
  private _fromCustodianName: string | null;
  private _toCustodianName: string | null;
  private _transferType: string | null;
  private _reason: string | null;
  private _reference: string | null;
  private _documentNumber: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(assetId: string, transferNumber: string, transferDate: Date) {
    super();
    this._id = FaTransferId.new();
    this._assetId = assetId;
    this._transferNumber = transferNumber;
    this._transferDate = transferDate;
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._fromBranchId = null;
    this._toBranchId = null;
    this._fromCompanyId = null;
    this._toCompanyId = null;
    this._fromCostCenterId = null;
    this._toCostCenterId = null;
    this._fromDepartmentId = null;
    this._toDepartmentId = null;
    this._fromLocationId = null;
    this._toLocationId = null;
    this._fromCustodianId = null;
    this._toCustodianId = null;
    this._fromCustodianName = null;
    this._toCustodianName = null;
    this._transferType = null;
    this._reason = null;
    this._reference = null;
    this._documentNumber = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._glBatchId = null;
  }

  static create(p: {
    assetId: string; transferNumber: string; transferDate: Date;
    fromBranchId?: string; toBranchId?: string;
    fromCostCenterId?: string; toCostCenterId?: string;
    fromDepartmentId?: string; toDepartmentId?: string;
    fromLocationId?: string; toLocationId?: string;
    fromCustodianId?: string; toCustodianId?: string;
    fromCustodianName?: string; toCustodianName?: string;
    transferType?: string; reason?: string; documentNumber?: string;
  }): FaTransfer {
    const t = new FaTransfer(p.assetId, p.transferNumber, p.transferDate);
    if (p.fromBranchId) t._fromBranchId = p.fromBranchId;
    if (p.toBranchId) t._toBranchId = p.toBranchId;
    if (p.fromCostCenterId) t._fromCostCenterId = p.fromCostCenterId;
    if (p.toCostCenterId) t._toCostCenterId = p.toCostCenterId;
    if (p.fromDepartmentId) t._fromDepartmentId = p.fromDepartmentId;
    if (p.toDepartmentId) t._toDepartmentId = p.toDepartmentId;
    if (p.fromLocationId) t._fromLocationId = p.fromLocationId;
    if (p.toLocationId) t._toLocationId = p.toLocationId;
    if (p.fromCustodianId) t._fromCustodianId = p.fromCustodianId;
    if (p.toCustodianId) t._toCustodianId = p.toCustodianId;
    if (p.fromCustodianName) t._fromCustodianName = p.fromCustodianName;
    if (p.toCustodianName) t._toCustodianName = p.toCustodianName;
    if (p.transferType) t._transferType = p.transferType;
    if (p.reason) t._reason = p.reason;
    if (p.documentNumber) t._documentNumber = p.documentNumber;
    return t;
  }

  static load(s: FaTransferState): FaTransfer {
    const t = new FaTransfer(s.assetId, s.transferNumber, s.transferDate);
    t._id = FaTransferId.from(s.id);
    t._fromBranchId = s.fromBranchId;
    t._toBranchId = s.toBranchId;
    t._fromCompanyId = s.fromCompanyId;
    t._toCompanyId = s.toCompanyId;
    t._fromCostCenterId = s.fromCostCenterId;
    t._toCostCenterId = s.toCostCenterId;
    t._fromDepartmentId = s.fromDepartmentId;
    t._toDepartmentId = s.toDepartmentId;
    t._fromLocationId = s.fromLocationId;
    t._toLocationId = s.toLocationId;
    t._fromCustodianId = s.fromCustodianId;
    t._toCustodianId = s.toCustodianId;
    t._fromCustodianName = s.fromCustodianName;
    t._toCustodianName = s.toCustodianName;
    t._transferType = s.transferType;
    t._reason = s.reason;
    t._reference = s.reference;
    t._documentNumber = s.documentNumber;
    t._approvedById = s.approvedById;
    t._approvedAt = s.approvedAt;
    t._postedToGL = s.postedToGL;
    t._glBatchId = s.glBatchId;
    t._version = s.version;
    t._createdAt = s.createdAt;
    t._updatedAt = s.updatedAt;
    return t;
  }

  get id() { return this._id; }
  get assetId() { return this._assetId; }
  get transferNumber() { return this._transferNumber; }
  get transferDate() { return this._transferDate; }
  get toBranchId() { return this._toBranchId; }
  get fromBranchId() { return this._fromBranchId; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaTransferState {
    return {
      id: this._id.value, assetId: this._assetId,
      transferNumber: this._transferNumber, transferDate: this._transferDate,
      fromBranchId: this._fromBranchId, toBranchId: this._toBranchId,
      fromCompanyId: this._fromCompanyId, toCompanyId: this._toCompanyId,
      fromCostCenterId: this._fromCostCenterId, toCostCenterId: this._toCostCenterId,
      fromDepartmentId: this._fromDepartmentId, toDepartmentId: this._toDepartmentId,
      fromLocationId: this._fromLocationId, toLocationId: this._toLocationId,
      fromCustodianId: this._fromCustodianId, toCustodianId: this._toCustodianId,
      fromCustodianName: this._fromCustodianName, toCustodianName: this._toCustodianName,
      transferType: this._transferType, reason: this._reason,
      reference: this._reference, documentNumber: this._documentNumber,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
