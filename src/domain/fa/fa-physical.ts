import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaPhysicalVerificationId } from "./fa-ids.js";
import { FaVerificationMethod, FaVerificationStatus, FaAssetStatus } from "./fa-enums.js";
import { FaPhysicalVerificationCompleted } from "./fa-events.js";

export interface FaPhysicalVerificationState {
  id: string; verificationNumber: string; companyId: string;
  branchId: string | null; verificationDate: Date;
  verificationMethod: FaVerificationMethod; status: FaVerificationStatus;
  totalAssets: number; verifiedAssets: number;
  matchedAssets: number; discrepancyAssets: number;
  missingAssets: number; verifiedById: string | null;
  verifiedByName: string | null; approvedById: string | null;
  approvedAt: Date | null; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaPhysicalVerification extends AggregateRoot<FaPhysicalVerificationId> {
  private _id: FaPhysicalVerificationId;
  private _verificationNumber: string;
  private _companyId: string;
  private _branchId: string | null;
  private _verificationDate: Date;
  private _verificationMethod: FaVerificationMethod;
  private _status: FaVerificationStatus;
  private _totalAssets: number;
  private _verifiedAssets: number;
  private _matchedAssets: number;
  private _discrepancyAssets: number;
  private _missingAssets: number;
  private _verifiedById: string | null;
  private _verifiedByName: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(verificationNumber: string, companyId: string, verificationDate: Date) {
    super();
    this._id = FaPhysicalVerificationId.new();
    this._verificationNumber = verificationNumber;
    this._companyId = companyId;
    this._verificationDate = verificationDate;
    this._verificationMethod = FaVerificationMethod.Manual;
    this._status = FaVerificationStatus.Planned;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._branchId = null;
    this._totalAssets = 0;
    this._verifiedAssets = 0;
    this._matchedAssets = 0;
    this._discrepancyAssets = 0;
    this._missingAssets = 0;
    this._verifiedById = null;
    this._verifiedByName = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._notes = null;
  }

  static create(p: {
    verificationNumber: string; companyId: string; verificationDate: Date;
    verificationMethod?: FaVerificationMethod; branchId?: string;
    verifiedById?: string; verifiedByName?: string; notes?: string;
  }): FaPhysicalVerification {
    const v = new FaPhysicalVerification(p.verificationNumber, p.companyId, p.verificationDate);
    if (p.verificationMethod) v._verificationMethod = p.verificationMethod;
    if (p.branchId) v._branchId = p.branchId;
    if (p.verifiedById) v._verifiedById = p.verifiedById;
    if (p.verifiedByName) v._verifiedByName = p.verifiedByName;
    if (p.notes) v._notes = p.notes;
    return v;
  }

  static load(s: FaPhysicalVerificationState): FaPhysicalVerification {
    const v = new FaPhysicalVerification(s.verificationNumber, s.companyId, s.verificationDate);
    v._id = FaPhysicalVerificationId.from(s.id);
    v._branchId = s.branchId;
    v._verificationMethod = s.verificationMethod;
    v._status = s.status;
    v._totalAssets = s.totalAssets;
    v._verifiedAssets = s.verifiedAssets;
    v._matchedAssets = s.matchedAssets;
    v._discrepancyAssets = s.discrepancyAssets;
    v._missingAssets = s.missingAssets;
    v._verifiedById = s.verifiedById;
    v._verifiedByName = s.verifiedByName;
    v._approvedById = s.approvedById;
    v._approvedAt = s.approvedAt;
    v._notes = s.notes;
    v._version = s.version;
    v._createdAt = s.createdAt;
    v._updatedAt = s.updatedAt;
    return v;
  }

  get id() { return this._id; }
  get verificationNumber() { return this._verificationNumber; }
  get status() { return this._status; }
  get totalAssets() { return this._totalAssets; }
  get verifiedAssets() { return this._verifiedAssets; }
  get matchedAssets() { return this._matchedAssets; }
  get discrepancyAssets() { return this._discrepancyAssets; }
  get missingAssets() { return this._missingAssets; }
  get version() { return this._version; }

  setTotalAssets(count: number): void {
    this._totalAssets = count;
    this._updatedAt = new Date();
  }

  recordVerification(isMatched: boolean): void {
    this._verifiedAssets++;
    if (isMatched) {
      this._matchedAssets++;
    } else {
      this._discrepancyAssets++;
    }
    this._updatedAt = new Date();
  }

  recordMissing(): void {
    this._missingAssets++;
    this._updatedAt = new Date();
  }

  complete(): void {
    this._status = FaVerificationStatus.Completed;
    this._updatedAt = new Date();
    this.addEvent(FaPhysicalVerificationCompleted.create(this._id.value, {
      verificationNumber: this._verificationNumber,
      totalAssets: this._totalAssets,
      matchedAssets: this._matchedAssets,
      discrepancyAssets: this._discrepancyAssets,
      missingAssets: this._missingAssets,
    }));
  }

  approve(userId: string): void {
    this._status = FaVerificationStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
  }

  toState(): FaPhysicalVerificationState {
    return {
      id: this._id.value, verificationNumber: this._verificationNumber,
      companyId: this._companyId, branchId: this._branchId,
      verificationDate: this._verificationDate,
      verificationMethod: this._verificationMethod, status: this._status,
      totalAssets: this._totalAssets, verifiedAssets: this._verifiedAssets,
      matchedAssets: this._matchedAssets,
      discrepancyAssets: this._discrepancyAssets,
      missingAssets: this._missingAssets,
      verifiedById: this._verifiedById, verifiedByName: this._verifiedByName,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
