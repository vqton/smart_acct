import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ApprovalMatrixId, ApprovalRequestId, ApprovalStepId } from "./bank-ids.js";
import { ApprovalStatus, ApprovalMode } from "./bank-enums.js";

// ─── Approval Matrix ───────────────────────────────────────────────────────────

export interface ApprovalMatrixState {
  id: string; companyId: string; name: string; entityType: string;
  minAmount: number; maxAmount: number; currencyCode: string;
  approvalMode: string; levels: number; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export interface ApprovalMatrixLevel {
  level: number; approverId: string; approverName: string;
  minAmount: number; maxAmount: number; isRequired: boolean;
}

export class ApprovalMatrix extends AggregateRoot<ApprovalMatrixId> {
  private _id: ApprovalMatrixId; private _companyId: string; private _name: string;
  private _entityType: string; private _minAmount: number; private _maxAmount: number;
  private _currencyCode: string; private _approvalMode: ApprovalMode;
  private _levels: ApprovalMatrixLevel[] = [];
  private _isActive: boolean; private _version: number;
  private _createdAt: Date; private _updatedAt: Date;

  private constructor(id: ApprovalMatrixId, companyId: string, name: string, entityType: string) {
    super(); this._id = id; this._companyId = companyId; this._name = name; this._entityType = entityType;
    this._minAmount = 0; this._maxAmount = 0; this._currencyCode = "VND";
    this._approvalMode = ApprovalMode.Sequential; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { companyId: string; name: string; entityType: string; minAmount?: number;
    maxAmount?: number; currencyCode?: string; approvalMode?: ApprovalMode }): ApprovalMatrix {
    const m = new ApprovalMatrix(ApprovalMatrixId.new(), p.companyId, p.name, p.entityType);
    m._minAmount = p.minAmount ?? 0; m._maxAmount = p.maxAmount ?? 0;
    m._currencyCode = p.currencyCode ?? "VND"; m._approvalMode = p.approvalMode ?? ApprovalMode.Sequential;
    return m;
  }

  static load(s: ApprovalMatrixState): ApprovalMatrix {
    const m = new ApprovalMatrix(new ApprovalMatrixId(s.id), s.companyId, s.name, s.entityType);
    m._minAmount = s.minAmount; m._maxAmount = s.maxAmount; m._currencyCode = s.currencyCode;
    m._approvalMode = s.approvalMode as ApprovalMode; m._isActive = s.isActive;
    m._version = s.version; m._createdAt = s.createdAt; m._updatedAt = s.updatedAt;
    return m;
  }

  get id(): ApprovalMatrixId { return this._id; }
  get isActive(): boolean { return this._isActive; }
  get levels(): ApprovalMatrixLevel[] { return this._levels; }
  get approvalMode(): ApprovalMode { return this._approvalMode; }

  addLevel(level: ApprovalMatrixLevel): void {
    this._levels.push(level); this._updatedAt = new Date(); this._version++;
  }

  isInRange(amount: number): boolean {
    if (this._minAmount > 0 && amount < this._minAmount) return false;
    if (this._maxAmount > 0 && amount > this._maxAmount) return false;
    return true;
  }

  toState(): ApprovalMatrixState {
    return { id: this._id.value, companyId: this._companyId, name: this._name,
      entityType: this._entityType, minAmount: this._minAmount, maxAmount: this._maxAmount,
      currencyCode: this._currencyCode, approvalMode: this._approvalMode,
      levels: this._levels.length, isActive: this._isActive,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Approval Request ───────────────────────────────────────────────────────────

export interface ApprovalRequestState {
  id: string; requestNumber: string; entityType: string; entityId: string;
  amount: number; currencyCode: string; status: string;
  currentLevel: number; maxLevel: number; approvalMode: string;
  requestedById: string; requestedAt: Date; completedAt: Date | null;
  notes: string | null; version: number;
  createdAt: Date; updatedAt: Date;
}

export class ApprovalRequest extends AggregateRoot<ApprovalRequestId> {
  private _id: ApprovalRequestId; private _requestNumber: string; private _entityType: string;
  private _entityId: string; private _amount: number; private _currencyCode: string;
  private _status: ApprovalStatus; private _currentLevel: number; private _maxLevel: number;
  private _approvalMode: ApprovalMode; private _requestedById: string;
  private _requestedAt: Date; private _completedAt: Date | null;
  private _notes: string | null; private _steps: ApprovalStep[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;

  private constructor(id: ApprovalRequestId, requestNumber: string, entityType: string,
    entityId: string, amount: number, currencyCode: string, requestedById: string) {
    super(); this._id = id; this._requestNumber = requestNumber; this._entityType = entityType;
    this._entityId = entityId; this._amount = amount; this._currencyCode = currencyCode;
    this._status = ApprovalStatus.Pending; this._currentLevel = 1; this._maxLevel = 1;
    this._approvalMode = ApprovalMode.Sequential; this._requestedById = requestedById;
    this._requestedAt = new Date(); this._completedAt = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { requestNumber: string; entityType: string; entityId: string;
    amount: number; currencyCode?: string; requestedById: string }): ApprovalRequest {
    return new ApprovalRequest(ApprovalRequestId.new(), p.requestNumber, p.entityType,
      p.entityId, p.amount, p.currencyCode ?? "VND", p.requestedById);
  }

  static load(s: ApprovalRequestState): ApprovalRequest {
    const a = new ApprovalRequest(new ApprovalRequestId(s.id), s.requestNumber, s.entityType,
      s.entityId, s.amount, s.currencyCode, s.requestedById);
    a._status = s.status as ApprovalStatus; a._currentLevel = s.currentLevel;
    a._maxLevel = s.maxLevel; a._approvalMode = s.approvalMode as ApprovalMode;
    a._requestedAt = s.requestedAt; a._completedAt = s.completedAt; a._notes = s.notes;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt;
    return a;
  }

  get id(): ApprovalRequestId { return this._id; }
  get status(): ApprovalStatus { return this._status; }
  get currentLevel(): number { return this._currentLevel; }

  addStep(approverId: string, approverName: string | null, level: number): ApprovalStep {
    const step = new ApprovalStep(ApprovalStepId.new(), this._id.value, approverId, approverName, level);
    this._steps.push(step); if (level > this._maxLevel) this._maxLevel = level;
    this._updatedAt = new Date(); this._version++;
    return step;
  }

  approve(userId: string, comment?: string): void {
    if (this._status !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Request already processed");
    this._currentLevel++;
    if (this._currentLevel > this._maxLevel || this._approvalMode === ApprovalMode.Any) {
      this._status = ApprovalStatus.Approved; this._completedAt = new Date();
    }
    this._updatedAt = new Date(); this._version++;
  }

  reject(userId: string, reason: string): void {
    if (this._status !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Request already processed");
    this._status = ApprovalStatus.Rejected; this._notes = reason; this._completedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  delegate(fromUserId: string, toUserId: string): void {
    if (this._status !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Cannot delegate processed request");
    this._status = ApprovalStatus.Delegated;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): ApprovalRequestState {
    return { id: this._id.value, requestNumber: this._requestNumber, entityType: this._entityType,
      entityId: this._entityId, amount: this._amount, currencyCode: this._currencyCode,
      status: this._status, currentLevel: this._currentLevel, maxLevel: this._maxLevel,
      approvalMode: this._approvalMode, requestedById: this._requestedById,
      requestedAt: this._requestedAt, completedAt: this._completedAt, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

export class ApprovalStep {
  constructor(
    private _id: ApprovalStepId, private _approvalId: string,
    private _approverId: string, private _approverName: string | null,
    private _level: number, private _status: ApprovalStatus = ApprovalStatus.Pending,
    private _actionAt: Date | null = null, private _comment: string | null = null,
  ) {}

  get id(): ApprovalStepId { return this._id; }
  get level(): number { return this._level; }
  get status(): ApprovalStatus { return this._status; }

  approve(comment?: string): void {
    if (this._status !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Step already processed");
    this._status = ApprovalStatus.Approved; this._actionAt = new Date(); this._comment = comment ?? null;
  }

  reject(comment: string): void {
    if (this._status !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Step already processed");
    this._status = ApprovalStatus.Rejected; this._actionAt = new Date(); this._comment = comment;
  }
}
