import { BgtReservationId, BgtReservationLineId } from "./bgt-ids.js";
import { BgtReservationStatus, BgtCommitmentType } from "./bgt-enums.js";
import { BgtReservationCreated, BgtReservationConsumed, BgtReservationReleased, BgtDomainEvent } from "./bgt-events.js";

export interface BgtBudgetReservationState {
  id: string;
  budgetPlanId: string;
  reservationNumber: string;
  commitmentType: string;
  status: string;
  sourceDocumentType: string | null;
  sourceDocumentId: string | null;
  sourceLineId: string | null;
  description: string | null;
  totalAmount: number;
  consumedAmount: number;
  releasedAmount: number;
  remainingAmount: number;
  currencyCode: string;
  reservedAt: string | null;
  releasedAt: string | null;
  expiresAt: string | null;
  cancelledAt: string | null;
  cancelReason: string | null;
  createdById: string | null;
  version: number;
}

export class BgtBudgetReservation {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _lines: BgtReservationLine[] = [];

  private constructor(
    private _id: BgtReservationId,
    private _budgetPlanId: string,
    private _reservationNumber: string,
    private _commitmentType: string,
    private _status: string,
    private _sourceDocumentType: string | null,
    private _sourceDocumentId: string | null,
    private _sourceLineId: string | null,
    private _description: string | null,
    private _totalAmount: number,
    private _consumedAmount: number,
    private _releasedAmount: number,
    private _remainingAmount: number,
    private _currencyCode: string,
    private _reservedAt: Date | null,
    private _releasedAt: Date | null,
    private _expiresAt: Date | null,
    private _cancelledAt: Date | null,
    private _cancelReason: string | null,
    private _createdById: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtReservationId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get reservationNumber(): string { return this._reservationNumber; }
  get commitmentType(): string { return this._commitmentType; }
  get status(): string { return this._status; }
  get sourceDocumentType(): string | null { return this._sourceDocumentType; }
  get sourceDocumentId(): string | null { return this._sourceDocumentId; }
  get totalAmount(): number { return this._totalAmount; }
  get consumedAmount(): number { return this._consumedAmount; }
  get releasedAmount(): number { return this._releasedAmount; }
  get remainingAmount(): number { return this._remainingAmount; }
  get expiresAt(): Date | null { return this._expiresAt; }
  get lines(): BgtReservationLine[] { return this._lines; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; reservationNumber: string;
    commitmentType?: string; sourceDocumentType?: string;
    sourceDocumentId?: string; sourceLineId?: string;
    description?: string; totalAmount: number; currencyCode?: string;
    expiresAt?: Date; createdById?: string;
  }): BgtBudgetReservation {
    const r = new BgtBudgetReservation(
      BgtReservationId.generate(), p.budgetPlanId, p.reservationNumber,
      p.commitmentType ?? BgtCommitmentType.Reservation,
      BgtReservationStatus.Draft, p.sourceDocumentType ?? null,
      p.sourceDocumentId ?? null, p.sourceLineId ?? null,
      p.description ?? null, p.totalAmount, 0, 0, p.totalAmount,
      p.currencyCode ?? "VND", null, null, p.expiresAt ?? null,
      null, null, p.createdById ?? null, 1,
    );
    r._events.push(new BgtReservationCreated(r._id.value, p.budgetPlanId, p.totalAmount));
    return r;
  }

  static load(state: BgtBudgetReservationState): BgtBudgetReservation {
    return new BgtBudgetReservation(
      BgtReservationId.from(state.id), state.budgetPlanId,
      state.reservationNumber, state.commitmentType, state.status,
      state.sourceDocumentType, state.sourceDocumentId, state.sourceLineId,
      state.description, state.totalAmount, state.consumedAmount,
      state.releasedAmount, state.remainingAmount, state.currencyCode,
      state.reservedAt ? new Date(state.reservedAt) : null,
      state.releasedAt ? new Date(state.releasedAt) : null,
      state.expiresAt ? new Date(state.expiresAt) : null,
      state.cancelledAt ? new Date(state.cancelledAt) : null,
      state.cancelReason, state.createdById, state.version,
    );
  }

  toState(): BgtBudgetReservationState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      reservationNumber: this._reservationNumber,
      commitmentType: this._commitmentType, status: this._status,
      sourceDocumentType: this._sourceDocumentType,
      sourceDocumentId: this._sourceDocumentId,
      sourceLineId: this._sourceLineId, description: this._description,
      totalAmount: this._totalAmount, consumedAmount: this._consumedAmount,
      releasedAmount: this._releasedAmount,
      remainingAmount: this._remainingAmount,
      currencyCode: this._currencyCode,
      reservedAt: this._reservedAt?.toISOString() ?? null,
      releasedAt: this._releasedAt?.toISOString() ?? null,
      expiresAt: this._expiresAt?.toISOString() ?? null,
      cancelledAt: this._cancelledAt?.toISOString() ?? null,
      cancelReason: this._cancelReason, createdById: this._createdById,
      version: this._version,
    };
  }

  activate(): void {
    if (this._status !== BgtReservationStatus.Draft) throw new Error("Reservation must be draft to activate");
    this._status = BgtReservationStatus.Active;
    this._reservedAt = new Date();
  }

  consume(amount: number): void {
    if (this._status !== BgtReservationStatus.Active && this._status !== BgtReservationStatus.PartiallyConsumed) {
      throw new Error("Reservation must be active to consume");
    }
    if (amount > this._remainingAmount) throw new Error(`Cannot consume ${amount}, only ${this._remainingAmount} remaining`);
    this._consumedAmount += amount;
    this._remainingAmount = this._totalAmount - this._consumedAmount - this._releasedAmount;
    this._status = this._remainingAmount <= 0 ? BgtReservationStatus.FullyConsumed : BgtReservationStatus.PartiallyConsumed;
    this._events.push(new BgtReservationConsumed(this._id.value, amount, this._remainingAmount));
  }

  release(amount: number): void {
    if (this._status !== BgtReservationStatus.Active && this._status !== BgtReservationStatus.PartiallyConsumed) {
      throw new Error("Cannot release from reservation in current status");
    }
    this._releasedAmount += amount;
    this._remainingAmount = this._totalAmount - this._consumedAmount - this._releasedAmount;
    if (this._remainingAmount <= 0) {
      this._status = BgtReservationStatus.Released;
      this._releasedAt = new Date();
    }
    this._events.push(new BgtReservationReleased(this._id.value, this._budgetPlanId, amount));
  }

  cancel(reason: string): void {
    if (this._status === BgtReservationStatus.Released || this._status === BgtReservationStatus.Cancelled) {
      throw new Error("Reservation already released or cancelled");
    }
    this._status = BgtReservationStatus.Cancelled;
    this._cancelledAt = new Date();
    this._cancelReason = reason;
  }

  expire(): void {
    if (this._status !== BgtReservationStatus.Active && this._status !== BgtReservationStatus.PartiallyConsumed) return;
    this._status = BgtReservationStatus.Expired;
  }

  addLine(line: BgtReservationLine): void {
    this._lines.push(line);
  }
}

// ─── Reservation Line ─────────────────────────────────────────────────────────

export interface BgtReservationLineState {
  id: string;
  reservationId: string;
  budgetDetailId: string;
  budgetControlId: string | null;
  lineNumber: number;
  amount: number;
  consumedAmount: number;
  releasedAmount: number;
  remainingAmount: number;
  glAccountId: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  description: string | null;
  periodNumber: number;
  isActive: boolean;
  version: number;
}

export class BgtReservationLine {
  private constructor(
    private _id: BgtReservationLineId,
    private _reservationId: string,
    private _budgetDetailId: string,
    private _budgetControlId: string | null,
    private _lineNumber: number,
    private _amount: number,
    private _consumedAmount: number,
    private _releasedAmount: number,
    private _remainingAmount: number,
    private _glAccountId: string | null,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _projectId: string | null,
    private _description: string | null,
    private _periodNumber: number,
    private _isActive: boolean,
    private _version: number,
  ) {}

  get id(): BgtReservationLineId { return this._id; }
  get reservationId(): string { return this._reservationId; }
  get budgetDetailId(): string { return this._budgetDetailId; }
  get lineNumber(): number { return this._lineNumber; }
  get amount(): number { return this._amount; }
  get consumedAmount(): number { return this._consumedAmount; }
  get remainingAmount(): number { return this._remainingAmount; }
  get periodNumber(): number { return this._periodNumber; }

  static create(p: {
    reservationId: string; budgetDetailId: string;
    budgetControlId?: string; lineNumber: number; amount: number;
    glAccountId?: string; costCenterId?: string; departmentId?: string;
    projectId?: string; description?: string; periodNumber?: number;
  }): BgtReservationLine {
    return new BgtReservationLine(
      BgtReservationLineId.generate(), p.reservationId, p.budgetDetailId,
      p.budgetControlId ?? null, p.lineNumber, p.amount, 0, 0, p.amount,
      p.glAccountId ?? null, p.costCenterId ?? null, p.departmentId ?? null,
      p.projectId ?? null, p.description ?? null, p.periodNumber ?? 1,
      true, 1,
    );
  }

  static load(state: BgtReservationLineState): BgtReservationLine {
    return new BgtReservationLine(
      BgtReservationLineId.from(state.id), state.reservationId,
      state.budgetDetailId, state.budgetControlId, state.lineNumber,
      state.amount, state.consumedAmount, state.releasedAmount,
      state.remainingAmount, state.glAccountId, state.costCenterId,
      state.departmentId, state.projectId, state.description,
      state.periodNumber, state.isActive, state.version,
    );
  }

  toState(): BgtReservationLineState {
    return {
      id: this._id.value, reservationId: this._reservationId,
      budgetDetailId: this._budgetDetailId,
      budgetControlId: this._budgetControlId,
      lineNumber: this._lineNumber, amount: this._amount,
      consumedAmount: this._consumedAmount,
      releasedAmount: this._releasedAmount,
      remainingAmount: this._remainingAmount,
      glAccountId: this._glAccountId, costCenterId: this._costCenterId,
      departmentId: this._departmentId, projectId: this._projectId,
      description: this._description, periodNumber: this._periodNumber,
      isActive: this._isActive, version: this._version,
    };
  }
}
