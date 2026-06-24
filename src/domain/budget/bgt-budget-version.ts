import { BgtBudgetVersionId } from "./bgt-ids.js";
import { BgtVersionStatus } from "./bgt-enums.js";
import {
  BgtBudgetVersionCreated, BgtBudgetVersionApproved, BgtBudgetVersionFrozen, BgtDomainEvent,
} from "./bgt-events.js";
import { BgtVersionCanApproveSpec, BgtVersionIsWorkingSpec } from "./bgt-specifications.js";

export interface BgtBudgetVersionState {
  id: string;
  budgetPlanId: string;
  versionNumber: number;
  label: string;
  description: string | null;
  status: string;
  totalAmount: number;
  isCurrent: boolean;
  isApproved: boolean;
  frozenAt: string | null;
  approvedById: string | null;
  approvedAt: string | null;
  createdById: string | null;
  sourceVersionId: string | null;
  notes: string | null;
  version: number;
}

export class BgtBudgetVersion {
  private _events: BgtDomainEvent[] = [];
  private _version: number;

  private constructor(
    private _id: BgtBudgetVersionId,
    private _budgetPlanId: string,
    private _versionNumber: number,
    private _label: string,
    private _description: string | null,
    private _status: string,
    private _totalAmount: number,
    private _isCurrent: boolean,
    private _isApproved: boolean,
    private _frozenAt: Date | null,
    private _approvedById: string | null,
    private _approvedAt: Date | null,
    private _createdById: string | null,
    private _sourceVersionId: string | null,
    private _notes: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtBudgetVersionId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get versionNumber(): number { return this._versionNumber; }
  get label(): string { return this._label; }
  get description(): string | null { return this._description; }
  get status(): string { return this._status; }
  get totalAmount(): number { return this._totalAmount; }
  get isCurrent(): boolean { return this._isCurrent; }
  get isApproved(): boolean { return this._isApproved; }
  get frozenAt(): Date | null { return this._frozenAt; }
  get approvedById(): string | null { return this._approvedById; }
  get approvedAt(): Date | null { return this._approvedAt; }
  get createdById(): string | null { return this._createdById; }
  get sourceVersionId(): string | null { return this._sourceVersionId; }
  get notes(): string | null { return this._notes; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; versionNumber: number; label: string;
    description?: string; totalAmount?: number; createdById?: string;
    sourceVersionId?: string; notes?: string;
  }): BgtBudgetVersion {
    const v = new BgtBudgetVersion(
      BgtBudgetVersionId.generate(), p.budgetPlanId, p.versionNumber, p.label,
      p.description ?? null, BgtVersionStatus.Working, p.totalAmount ?? 0,
      false, false, null, null, null, p.createdById ?? null,
      p.sourceVersionId ?? null, p.notes ?? null, 1,
    );
    v._events.push(new BgtBudgetVersionCreated(p.budgetPlanId, v._id.value, p.versionNumber));
    return v;
  }

  static load(state: BgtBudgetVersionState): BgtBudgetVersion {
    return new BgtBudgetVersion(
      BgtBudgetVersionId.from(state.id), state.budgetPlanId, state.versionNumber,
      state.label, state.description, state.status, state.totalAmount,
      state.isCurrent, state.isApproved,
      state.frozenAt ? new Date(state.frozenAt) : null,
      state.approvedById, state.approvedAt ? new Date(state.approvedAt) : null,
      state.createdById, state.sourceVersionId, state.notes, state.version,
    );
  }

  toState(): BgtBudgetVersionState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      versionNumber: this._versionNumber, label: this._label,
      description: this._description, status: this._status,
      totalAmount: this._totalAmount, isCurrent: this._isCurrent,
      isApproved: this._isApproved,
      frozenAt: this._frozenAt?.toISOString() ?? null,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt?.toISOString() ?? null,
      createdById: this._createdById, sourceVersionId: this._sourceVersionId,
      notes: this._notes, version: this._version,
    };
  }

  submitForReview(): void {
    if (!new BgtVersionIsWorkingSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot submit version in status ${this._status}`);
    }
    this._status = BgtVersionStatus.InReview;
  }

  approve(approvedById: string): void {
    if (!new BgtVersionCanApproveSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot approve version in status ${this._status}`);
    }
    this._status = BgtVersionStatus.Approved;
    this._isApproved = true;
    this._approvedById = approvedById;
    this._approvedAt = new Date();
    this._events.push(new BgtBudgetVersionApproved(this._id.value, this._budgetPlanId, approvedById));
  }

  reject(): void {
    if (!new BgtVersionCanApproveSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot reject version in status ${this._status}`);
    }
    this._status = BgtVersionStatus.Working;
  }

  publish(): void {
    if (this._status !== BgtVersionStatus.Approved) {
      throw new Error(`Cannot publish version in status ${this._status}`);
    }
    this._status = BgtVersionStatus.Published;
    this._isCurrent = true;
  }

  freeze(): void {
    this._status = BgtVersionStatus.Frozen;
    this._frozenAt = new Date();
    this._events.push(new BgtBudgetVersionFrozen(this._id.value, this._budgetPlanId));
  }

  setCurrent(): void {
    this._isCurrent = true;
  }

  updateTotalAmount(amount: number): void {
    if (!new BgtVersionIsWorkingSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot update version amount in status ${this._status}`);
    }
    this._totalAmount = amount;
  }

  clone(newVersionNumber: number, label: string, createdById?: string): BgtBudgetVersion {
    return BgtBudgetVersion.create({
      budgetPlanId: this._budgetPlanId, versionNumber: newVersionNumber,
      label, totalAmount: this._totalAmount, createdById,
      sourceVersionId: this._id.value,
      description: `Cloned from version ${this._versionNumber}`,
    });
  }
}
