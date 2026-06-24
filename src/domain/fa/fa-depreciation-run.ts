import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FaDepreciationRunId } from "./fa-ids.js";
import { FaDepreciationArea, FaDepreciationRunStatus } from "./fa-enums.js";
import { FaDepreciationRunCompleted } from "./fa-events.js";

export interface FaDepreciationRunState {
  id: string; runNumber: string; depreciationArea: FaDepreciationArea;
  periodId: string; fiscalYearId: string; runDate: Date;
  status: FaDepreciationRunStatus;
  totalAssets: number; totalDepreciation: number;
  processedAssets: number; failedAssets: number;
  startedAt: Date | null; completedAt: Date | null;
  errorMessage: string | null;
  createdById: string | null; postedToGL: boolean;
  glBatchId: string | null; isSimulation: boolean;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaDepreciationRun extends AggregateRoot<FaDepreciationRunId> {
  private _id: FaDepreciationRunId;
  private _runNumber: string;
  private _depreciationArea: FaDepreciationArea;
  private _periodId: string;
  private _fiscalYearId: string;
  private _runDate: Date;
  private _status: FaDepreciationRunStatus;
  private _totalAssets: number;
  private _totalDepreciation: number;
  private _processedAssets: number;
  private _failedAssets: number;
  private _startedAt: Date | null;
  private _completedAt: Date | null;
  private _errorMessage: string | null;
  private _createdById: string | null;
  private _postedToGL: boolean;
  private _glBatchId: string | null;
  private _isSimulation: boolean;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(runNumber: string, depreciationArea: FaDepreciationArea, periodId: string, fiscalYearId: string) {
    super();
    this._id = FaDepreciationRunId.new();
    this._runNumber = runNumber;
    this._depreciationArea = depreciationArea;
    this._periodId = periodId;
    this._fiscalYearId = fiscalYearId;
    this._runDate = new Date();
    this._status = FaDepreciationRunStatus.Pending;
    this._isSimulation = false;
    this._postedToGL = false;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._totalAssets = 0;
    this._totalDepreciation = 0;
    this._processedAssets = 0;
    this._failedAssets = 0;
    this._startedAt = null;
    this._completedAt = null;
    this._errorMessage = null;
    this._createdById = null;
    this._glBatchId = null;
    this._notes = null;
  }

  static create(p: {
    runNumber: string; depreciationArea: FaDepreciationArea;
    periodId: string; fiscalYearId: string;
    isSimulation?: boolean; createdById?: string; notes?: string;
  }): FaDepreciationRun {
    const r = new FaDepreciationRun(p.runNumber, p.depreciationArea, p.periodId, p.fiscalYearId);
    if (p.isSimulation) r._isSimulation = true;
    if (p.createdById) r._createdById = p.createdById;
    if (p.notes) r._notes = p.notes;
    return r;
  }

  static load(s: FaDepreciationRunState): FaDepreciationRun {
    const r = new FaDepreciationRun(s.runNumber, s.depreciationArea, s.periodId, s.fiscalYearId);
    r._id = FaDepreciationRunId.from(s.id);
    r._runDate = s.runDate;
    r._status = s.status;
    r._totalAssets = s.totalAssets;
    r._totalDepreciation = s.totalDepreciation;
    r._processedAssets = s.processedAssets;
    r._failedAssets = s.failedAssets;
    r._startedAt = s.startedAt;
    r._completedAt = s.completedAt;
    r._errorMessage = s.errorMessage;
    r._createdById = s.createdById;
    r._postedToGL = s.postedToGL;
    r._glBatchId = s.glBatchId;
    r._isSimulation = s.isSimulation;
    r._notes = s.notes;
    r._version = s.version;
    r._createdAt = s.createdAt;
    r._updatedAt = s.updatedAt;
    return r;
  }

  get id() { return this._id; }
  get runNumber() { return this._runNumber; }
  get depreciationArea() { return this._depreciationArea; }
  get periodId() { return this._periodId; }
  get status() { return this._status; }
  get totalDepreciation() { return this._totalDepreciation; }
  get totalAssets() { return this._totalAssets; }
  get processedAssets() { return this._processedAssets; }
  get failedAssets() { return this._failedAssets; }
  get isSimulation() { return this._isSimulation; }
  get postedToGL() { return this._postedToGL; }
  get version() { return this._version; }

  start(): void {
    if (this._status !== FaDepreciationRunStatus.Pending) {
      throw new DomainError("BusinessRule", "Run must be pending");
    }
    this._status = FaDepreciationRunStatus.InProgress;
    this._startedAt = new Date();
    this._updatedAt = new Date();
  }

  complete(totalDepreciation: number): void {
    if (this._status !== FaDepreciationRunStatus.InProgress) {
      throw new DomainError("BusinessRule", "Run must be in progress");
    }
    this._totalDepreciation = totalDepreciation;
    this._status = FaDepreciationRunStatus.Completed;
    this._completedAt = new Date();
    this._updatedAt = new Date();
    this.addEvent(FaDepreciationRunCompleted.create(this._id.value, {
      runNumber: this._runNumber, totalDepreciation,
    }));
  }

  fail(error: string): void {
    this._status = FaDepreciationRunStatus.Failed;
    this._errorMessage = error;
    this._completedAt = new Date();
    this._updatedAt = new Date();
  }

  markPostedToGL(batchId: string): void {
    this._postedToGL = true;
    this._glBatchId = batchId;
    this._updatedAt = new Date();
  }

  incrementProcessed(): void {
    this._processedAssets++;
  }

  incrementFailed(): void {
    this._failedAssets++;
  }

  setTotalAssets(count: number): void {
    this._totalAssets = count;
  }

  toState(): FaDepreciationRunState {
    return {
      id: this._id.value, runNumber: this._runNumber,
      depreciationArea: this._depreciationArea,
      periodId: this._periodId, fiscalYearId: this._fiscalYearId,
      runDate: this._runDate, status: this._status,
      totalAssets: this._totalAssets,
      totalDepreciation: this._totalDepreciation,
      processedAssets: this._processedAssets,
      failedAssets: this._failedAssets,
      startedAt: this._startedAt, completedAt: this._completedAt,
      errorMessage: this._errorMessage,
      createdById: this._createdById,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      isSimulation: this._isSimulation, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
