import { AggregateRoot } from "../../shared/aggregate-root.js";
import { FaMaintenanceRecordId } from "./fa-ids.js";
import { FaMaintenanceType } from "./fa-enums.js";
import { FaMaintenanceCompleted } from "./fa-events.js";

export interface FaMaintenanceRecordState {
  id: string; assetId: string; planId: string | null;
  scheduleId: string | null; recordNumber: string;
  maintenanceType: FaMaintenanceType; maintenanceDate: Date;
  completedDate: Date | null; cost: number; currencyCode: string;
  vendorId: string | null; vendorName: string | null;
  technicianId: string | null; technicianName: string | null;
  description: string | null; findings: string | null;
  resolution: string | null; partsReplaced: string | null;
  downtimeHours: number | null; warrantyClaim: boolean;
  reference: string | null; documentFile: string | null;
  postedToGL: boolean; glBatchId: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaMaintenanceRecord extends AggregateRoot<FaMaintenanceRecordId> {
  private _id: FaMaintenanceRecordId;
  private _assetId: string;
  private _planId: string | null;
  private _scheduleId: string | null;
  private _recordNumber: string;
  private _maintenanceType: FaMaintenanceType;
  private _maintenanceDate: Date;
  private _completedDate: Date | null;
  private _cost: number;
  private _currencyCode: string;
  private _vendorId: string | null;
  private _vendorName: string | null;
  private _technicianId: string | null;
  private _technicianName: string | null;
  private _description: string | null;
  private _findings: string | null;
  private _resolution: string | null;
  private _partsReplaced: string | null;
  private _downtimeHours: number | null;
  private _warrantyClaim: boolean;
  private _reference: string | null;
  private _documentFile: string | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(assetId: string, recordNumber: string, maintenanceType: FaMaintenanceType, maintenanceDate: Date) {
    super();
    this._id = FaMaintenanceRecordId.new();
    this._assetId = assetId;
    this._recordNumber = recordNumber;
    this._maintenanceType = maintenanceType;
    this._maintenanceDate = maintenanceDate;
    this._cost = 0;
    this._currencyCode = "VND";
    this._warrantyClaim = false;
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._planId = null;
    this._scheduleId = null;
    this._completedDate = null;
    this._vendorId = null;
    this._vendorName = null;
    this._technicianId = null;
    this._technicianName = null;
    this._description = null;
    this._findings = null;
    this._resolution = null;
    this._partsReplaced = null;
    this._downtimeHours = null;
    this._reference = null;
    this._documentFile = null;
    this._glBatchId = null;
  }

  static create(p: {
    assetId: string; recordNumber: string; maintenanceType: FaMaintenanceType;
    maintenanceDate: Date; cost: number; description?: string;
    planId?: string; scheduleId?: string; vendorId?: string;
    vendorName?: string; technicianId?: string; technicianName?: string;
    reference?: string;
  }): FaMaintenanceRecord {
    const r = new FaMaintenanceRecord(p.assetId, p.recordNumber, p.maintenanceType, p.maintenanceDate);
    r._cost = p.cost;
    if (p.description) r._description = p.description;
    if (p.planId) r._planId = p.planId;
    if (p.scheduleId) r._scheduleId = p.scheduleId;
    if (p.vendorId) r._vendorId = p.vendorId;
    if (p.vendorName) r._vendorName = p.vendorName;
    if (p.technicianId) r._technicianId = p.technicianId;
    if (p.technicianName) r._technicianName = p.technicianName;
    if (p.reference) r._reference = p.reference;
    return r;
  }

  static load(s: FaMaintenanceRecordState): FaMaintenanceRecord {
    const r = new FaMaintenanceRecord(s.assetId, s.recordNumber, s.maintenanceType, s.maintenanceDate);
    r._id = FaMaintenanceRecordId.from(s.id);
    r._planId = s.planId;
    r._scheduleId = s.scheduleId;
    r._completedDate = s.completedDate;
    r._cost = s.cost;
    r._currencyCode = s.currencyCode;
    r._vendorId = s.vendorId;
    r._vendorName = s.vendorName;
    r._technicianId = s.technicianId;
    r._technicianName = s.technicianName;
    r._description = s.description;
    r._findings = s.findings;
    r._resolution = s.resolution;
    r._partsReplaced = s.partsReplaced;
    r._downtimeHours = s.downtimeHours;
    r._warrantyClaim = s.warrantyClaim;
    r._reference = s.reference;
    r._documentFile = s.documentFile;
    r._postedToGL = s.postedToGL;
    r._glBatchId = s.glBatchId;
    r._version = s.version;
    r._createdAt = s.createdAt;
    r._updatedAt = s.updatedAt;
    return r;
  }

  get id() { return this._id; }
  get assetId() { return this._assetId; }
  get recordNumber() { return this._recordNumber; }
  get cost() { return this._cost; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  complete(completedDate: Date, findings?: string, resolution?: string): void {
    this._completedDate = completedDate;
    if (findings) this._findings = findings;
    if (resolution) this._resolution = resolution;
    this._updatedAt = new Date();
    this.addEvent(FaMaintenanceCompleted.create(this._id.value, {
      assetId: this._assetId, recordNumber: this._recordNumber,
    }));
  }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  toState(): FaMaintenanceRecordState {
    return {
      id: this._id.value, assetId: this._assetId,
      planId: this._planId, scheduleId: this._scheduleId,
      recordNumber: this._recordNumber,
      maintenanceType: this._maintenanceType,
      maintenanceDate: this._maintenanceDate,
      completedDate: this._completedDate, cost: this._cost,
      currencyCode: this._currencyCode,
      vendorId: this._vendorId, vendorName: this._vendorName,
      technicianId: this._technicianId, technicianName: this._technicianName,
      description: this._description, findings: this._findings,
      resolution: this._resolution, partsReplaced: this._partsReplaced,
      downtimeHours: this._downtimeHours, warrantyClaim: this._warrantyClaim,
      reference: this._reference, documentFile: this._documentFile,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
