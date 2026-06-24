import { BgtSnapshotId, BgtSnapshotDetailId } from "./bgt-ids.js";
import { BgtSnapshotType } from "./bgt-enums.js";
import { BgtSnapshotCreated, BgtSnapshotRestored, BgtDomainEvent } from "./bgt-events.js";

export interface BgtBudgetSnapshotState {
  id: string;
  budgetPlanId: string;
  snapshotNumber: string;
  label: string;
  description: string | null;
  snapshotType: string;
  totalAmount: number;
  isRestorable: boolean;
  restoredAt: string | null;
  createdById: string | null;
  version: number;
  createdAt: string;
}

export class BgtBudgetSnapshot {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _details: BgtSnapshotDetail[] = [];

  private constructor(
    private _id: BgtSnapshotId,
    private _budgetPlanId: string,
    private _snapshotNumber: string,
    private _label: string,
    private _description: string | null,
    private _snapshotType: string,
    private _totalAmount: number,
    private _isRestorable: boolean,
    private _restoredAt: Date | null,
    private _createdById: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtSnapshotId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get snapshotNumber(): string { return this._snapshotNumber; }
  get label(): string { return this._label; }
  get description(): string | null { return this._description; }
  get snapshotType(): string { return this._snapshotType; }
  get totalAmount(): number { return this._totalAmount; }
  get isRestorable(): boolean { return this._isRestorable; }
  get restoredAt(): Date | null { return this._restoredAt; }
  get createdById(): string | null { return this._createdById; }
  get details(): BgtSnapshotDetail[] { return this._details; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; snapshotNumber: string; label: string;
    description?: string; snapshotType?: string; totalAmount?: number;
    isRestorable?: boolean; createdById?: string;
  }): BgtBudgetSnapshot {
    const s = new BgtBudgetSnapshot(
      BgtSnapshotId.generate(), p.budgetPlanId, p.snapshotNumber,
      p.label, p.description ?? null, p.snapshotType ?? BgtSnapshotType.Periodic,
      p.totalAmount ?? 0, p.isRestorable ?? true, null,
      p.createdById ?? null, 1,
    );
    s._events.push(new BgtSnapshotCreated(s._id.value, p.budgetPlanId, s._snapshotType));
    return s;
  }

  static load(state: BgtBudgetSnapshotState): BgtBudgetSnapshot {
    return new BgtBudgetSnapshot(
      BgtSnapshotId.from(state.id), state.budgetPlanId, state.snapshotNumber,
      state.label, state.description, state.snapshotType, state.totalAmount,
      state.isRestorable,
      state.restoredAt ? new Date(state.restoredAt) : null,
      state.createdById, state.version,
    );
  }

  toState(): BgtBudgetSnapshotState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      snapshotNumber: this._snapshotNumber, label: this._label,
      description: this._description, snapshotType: this._snapshotType,
      totalAmount: this._totalAmount, isRestorable: this._isRestorable,
      restoredAt: this._restoredAt?.toISOString() ?? null,
      createdById: this._createdById, version: this._version,
      createdAt: "",
    };
  }

  addDetail(detail: BgtSnapshotDetail): void {
    this._details.push(detail);
    this._totalAmount += detail.amount;
  }

  addDetails(details: BgtSnapshotDetail[]): void {
    for (const d of details) {
      this._details.push(d);
      this._totalAmount += d.amount;
    }
  }

  markRestored(): void {
    this._restoredAt = new Date();
    this._events.push(new BgtSnapshotRestored(this._id.value, this._budgetPlanId));
  }
}

// ─── Snapshot Detail ──────────────────────────────────────────────────────────

export interface BgtSnapshotDetailState {
  id: string;
  snapshotId: string;
  budgetDetailId: string;
  glAccountId: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  amount: number;
  period1: number; period2: number; period3: number; period4: number;
  period5: number; period6: number; period7: number; period8: number;
  period9: number; period10: number; period11: number; period12: number;
  version: number;
  createdAt: string;
}

export class BgtSnapshotDetail {
  private constructor(
    private _id: BgtSnapshotDetailId,
    private _snapshotId: string,
    private _budgetDetailId: string,
    private _glAccountId: string | null,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _projectId: string | null,
    private _amount: number,
    private _periodAmounts: number[],
    private _version: number,
  ) {}

  get id(): BgtSnapshotDetailId { return this._id; }
  get snapshotId(): string { return this._snapshotId; }
  get budgetDetailId(): string { return this._budgetDetailId; }
  get amount(): number { return this._amount; }

  static create(p: {
    snapshotId: string; budgetDetailId: string;
    glAccountId?: string; costCenterId?: string;
    departmentId?: string; projectId?: string; amount?: number;
    periodAmounts?: number[];
  }): BgtSnapshotDetail {
    return new BgtSnapshotDetail(
      BgtSnapshotDetailId.generate(), p.snapshotId, p.budgetDetailId,
      p.glAccountId ?? null, p.costCenterId ?? null,
      p.departmentId ?? null, p.projectId ?? null,
      p.amount ?? 0, p.periodAmounts ?? new Array(12).fill(0), 1,
    );
  }

  static load(state: BgtSnapshotDetailState): BgtSnapshotDetail {
    return new BgtSnapshotDetail(
      BgtSnapshotDetailId.from(state.id), state.snapshotId,
      state.budgetDetailId, state.glAccountId, state.costCenterId,
      state.departmentId, state.projectId, state.amount,
      [state.period1, state.period2, state.period3, state.period4,
        state.period5, state.period6, state.period7, state.period8,
        state.period9, state.period10, state.period11, state.period12],
      state.version,
    );
  }

  toState(): BgtSnapshotDetailState {
    return {
      id: this._id.value, snapshotId: this._snapshotId,
      budgetDetailId: this._budgetDetailId,
      glAccountId: this._glAccountId, costCenterId: this._costCenterId,
      departmentId: this._departmentId, projectId: this._projectId,
      amount: this._amount,
      period1: this._periodAmounts[0] ?? 0,
      period2: this._periodAmounts[1] ?? 0,
      period3: this._periodAmounts[2] ?? 0,
      period4: this._periodAmounts[3] ?? 0,
      period5: this._periodAmounts[4] ?? 0,
      period6: this._periodAmounts[5] ?? 0,
      period7: this._periodAmounts[6] ?? 0,
      period8: this._periodAmounts[7] ?? 0,
      period9: this._periodAmounts[8] ?? 0,
      period10: this._periodAmounts[9] ?? 0,
      period11: this._periodAmounts[10] ?? 0,
      period12: this._periodAmounts[11] ?? 0,
      version: this._version, createdAt: "",
    };
  }
}
