import { BgtBudgetPlanId } from "./bgt-ids.js";
import {
  BgtBudgetType, BgtBudgetStatus, BgtPeriodType,
} from "./bgt-enums.js";
import {
  BgtBudgetPlanCreated, BgtBudgetPlanSubmitted, BgtBudgetPlanApproved,
  BgtBudgetPlanRejected, BgtBudgetPlanPublished, BgtBudgetPlanActivated,
  BgtBudgetPlanFrozen, BgtBudgetPlanClosed, BgtDomainEvent,
} from "./bgt-events.js";
import { BgtCanSubmitSpec, BgtCanApproveSpec, BgtCanModifySpec, BgtIsActiveSpec } from "./bgt-specifications.js";

export interface BgtBudgetPlanState {
  id: string;
  code: string;
  name: string;
  description: string | null;
  budgetType: string;
  status: string;
  fiscalYearId: string;
  currencyCode: string;
  totalPlannedAmount: number;
  totalApprovedAmount: number;
  totalRemainingAmount: number;
  totalReservedAmount: number;
  totalConsumedAmount: number;
  startDate: string | null;
  endDate: string | null;
  notes: string | null;
  isTemplate: boolean;
  parentId: string | null;
  createdById: string | null;
  approvedById: string | null;
  approvedAt: string | null;
  publishedAt: string | null;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export class BgtBudgetPlan {
  private _events: BgtDomainEvent[] = [];
  private _version: number;

  private constructor(
    private _id: BgtBudgetPlanId,
    private _code: string,
    private _name: string,
    private _description: string | null,
    private _budgetType: string,
    private _status: string,
    private _fiscalYearId: string,
    private _currencyCode: string,
    private _totalPlannedAmount: number,
    private _totalApprovedAmount: number,
    private _totalRemainingAmount: number,
    private _totalReservedAmount: number,
    private _totalConsumedAmount: number,
    private _startDate: Date | null,
    private _endDate: Date | null,
    private _notes: string | null,
    private _isTemplate: boolean,
    private _parentId: string | null,
    private _createdById: string | null,
    private _approvedById: string | null,
    private _approvedAt: Date | null,
    private _publishedAt: Date | null,
    version: number,
  ) {
    this._version = version;
  }

  get id(): BgtBudgetPlanId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get description(): string | null { return this._description; }
  get budgetType(): string { return this._budgetType; }
  get status(): string { return this._status; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get currencyCode(): string { return this._currencyCode; }
  get totalPlannedAmount(): number { return this._totalPlannedAmount; }
  get totalApprovedAmount(): number { return this._totalApprovedAmount; }
  get totalRemainingAmount(): number { return this._totalRemainingAmount; }
  get totalReservedAmount(): number { return this._totalReservedAmount; }
  get totalConsumedAmount(): number { return this._totalConsumedAmount; }
  get startDate(): Date | null { return this._startDate; }
  get endDate(): Date | null { return this._endDate; }
  get notes(): string | null { return this._notes; }
  get isTemplate(): boolean { return this._isTemplate; }
  get parentId(): string | null { return this._parentId; }
  get createdById(): string | null { return this._createdById; }
  get approvedById(): string | null { return this._approvedById; }
  get approvedAt(): Date | null { return this._approvedAt; }
  get publishedAt(): Date | null { return this._publishedAt; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  get availableBalance(): number {
    return this._totalRemainingAmount - this._totalReservedAmount;
  }

  get utilizationPct(): number {
    if (this._totalApprovedAmount === 0) return 0;
    return Math.round((this._totalConsumedAmount / this._totalApprovedAmount) * 10000) / 100;
  }

  static create(p: {
    code: string; name: string; budgetType: string; fiscalYearId: string;
    description?: string; currencyCode?: string; startDate?: Date; endDate?: Date;
    notes?: string; isTemplate?: boolean; parentId?: string; createdById?: string;
  }): BgtBudgetPlan {
    const plan = new BgtBudgetPlan(
      BgtBudgetPlanId.generate(), p.code, p.name, p.description ?? null,
      p.budgetType, BgtBudgetStatus.Draft, p.fiscalYearId,
      p.currencyCode ?? "VND", 0, 0, 0, 0, 0,
      p.startDate ?? null, p.endDate ?? null, p.notes ?? null,
      p.isTemplate ?? false, p.parentId ?? null, p.createdById ?? null,
      null, null, null, 1,
    );
    plan._events.push(new BgtBudgetPlanCreated(plan._id.value, plan._code, plan._name, plan._budgetType, plan._fiscalYearId));
    return plan;
  }

  static load(state: BgtBudgetPlanState): BgtBudgetPlan {
    return new BgtBudgetPlan(
      BgtBudgetPlanId.from(state.id), state.code, state.name, state.description,
      state.budgetType, state.status, state.fiscalYearId, state.currencyCode,
      state.totalPlannedAmount, state.totalApprovedAmount, state.totalRemainingAmount,
      state.totalReservedAmount, state.totalConsumedAmount,
      state.startDate ? new Date(state.startDate) : null,
      state.endDate ? new Date(state.endDate) : null,
      state.notes, state.isTemplate, state.parentId,
      state.createdById, state.approvedById,
      state.approvedAt ? new Date(state.approvedAt) : null,
      state.publishedAt ? new Date(state.publishedAt) : null,
      state.version,
    );
  }

  toState(): BgtBudgetPlanState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      description: this._description, budgetType: this._budgetType,
      status: this._status, fiscalYearId: this._fiscalYearId,
      currencyCode: this._currencyCode,
      totalPlannedAmount: this._totalPlannedAmount,
      totalApprovedAmount: this._totalApprovedAmount,
      totalRemainingAmount: this._totalRemainingAmount,
      totalReservedAmount: this._totalReservedAmount,
      totalConsumedAmount: this._totalConsumedAmount,
      startDate: this._startDate?.toISOString() ?? null,
      endDate: this._endDate?.toISOString() ?? null,
      notes: this._notes, isTemplate: this._isTemplate, parentId: this._parentId,
      createdById: this._createdById, approvedById: this._approvedById,
      approvedAt: this._approvedAt?.toISOString() ?? null,
      publishedAt: this._publishedAt?.toISOString() ?? null,
      version: this._version, createdAt: "", updatedAt: "",
    };
  }

  update(p: { name?: string; description?: string; notes?: string; startDate?: Date; endDate?: Date }): void {
    if (!new BgtCanModifySpec().isSatisfiedBy(this._status)) {
      throw new Error(`Budget plan ${this._id.value} cannot be modified in status ${this._status}`);
    }
    if (p.name !== undefined) this._name = p.name;
    if (p.description !== undefined) this._description = p.description;
    if (p.notes !== undefined) this._notes = p.notes;
    if (p.startDate !== undefined) this._startDate = p.startDate;
    if (p.endDate !== undefined) this._endDate = p.endDate;
  }

  submit(submittedById: string): void {
    if (!new BgtCanSubmitSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot submit budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Submitted;
    this._events.push(new BgtBudgetPlanSubmitted(this._id.value, submittedById));
  }

  approve(approvedById: string): void {
    if (!new BgtCanApproveSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot approve budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Approved;
    this._approvedById = approvedById;
    this._approvedAt = new Date();
    this._totalApprovedAmount = this._totalPlannedAmount;
    this._totalRemainingAmount = this._totalPlannedAmount;
    this._events.push(new BgtBudgetPlanApproved(this._id.value, approvedById, this._totalApprovedAmount));
  }

  reject(rejectedById: string, reason: string): void {
    if (!new BgtCanApproveSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot reject budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Rejected;
    this._events.push(new BgtBudgetPlanRejected(this._id.value, rejectedById, reason));
  }

  review(): void {
    if (this._status !== BgtBudgetStatus.Submitted) {
      throw new Error(`Cannot move to review from status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Review;
  }

  revise(): void {
    if (this._status !== BgtBudgetStatus.Review) {
      throw new Error(`Cannot revise budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Revision;
  }

  publish(publishedById: string): void {
    if (this._status !== BgtBudgetStatus.Approved) {
      throw new Error(`Cannot publish budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Published;
    this._publishedAt = new Date();
    this._events.push(new BgtBudgetPlanPublished(this._id.value, publishedById));
  }

  activate(): void {
    if (this._status !== BgtBudgetStatus.Published) {
      throw new Error(`Cannot activate budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Activated;
    this._events.push(new BgtBudgetPlanActivated(this._id.value));
  }

  freeze(frozenById: string): void {
    if (!new BgtIsActiveSpec().isSatisfiedBy(this._status)) {
      throw new Error(`Cannot freeze budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Frozen;
    this._events.push(new BgtBudgetPlanFrozen(this._id.value, frozenById));
  }

  close(closedById: string): void {
    if (this._status === BgtBudgetStatus.Closed) {
      throw new Error("Budget already closed");
    }
    this._status = BgtBudgetStatus.Closed;
    this._events.push(new BgtBudgetPlanClosed(this._id.value, closedById));
  }

  reopen(): void {
    if (this._status !== BgtBudgetStatus.Closed) {
      throw new Error(`Cannot reopen budget in status ${this._status}`);
    }
    this._status = BgtBudgetStatus.Reopened;
  }

  adjustTotalPlanned(amount: number): void {
    if (!new BgtCanModifySpec().isSatisfiedBy(this._status) && this._status !== BgtBudgetStatus.Adjustment) {
      throw new Error(`Cannot adjust budget in status ${this._status}`);
    }
    const diff = amount - this._totalPlannedAmount;
    this._totalPlannedAmount = amount;
    if (this._totalApprovedAmount > 0) {
      this._totalApprovedAmount = Math.max(0, this._totalApprovedAmount + diff);
      this._totalRemainingAmount = Math.max(0, this._totalRemainingAmount + diff);
    }
  }

  recordConsumption(amount: number): void {
    this._totalConsumedAmount += amount;
    this._totalRemainingAmount = Math.max(0, this._totalRemainingAmount - amount);
  }

  recordReservation(amount: number): void {
    this._totalReservedAmount += amount;
  }

  releaseReservation(amount: number): void {
    this._totalReservedAmount = Math.max(0, this._totalReservedAmount - amount);
  }
}
