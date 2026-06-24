import { BgtTransferId, BgtTransferLineId } from "./bgt-ids.js";
import { BgtTransferStatus } from "./bgt-enums.js";
import { BgtBudgetTransferCreated, BgtBudgetTransferCompleted, BgtDomainEvent } from "./bgt-events.js";

export interface BgtBudgetTransferState {
  id: string;
  transferNumber: string;
  sourceBudgetPlanId: string;
  targetBudgetPlanId: string;
  description: string | null;
  totalAmount: number;
  status: string;
  effectiveDate: string | null;
  approvedById: string | null;
  approvedAt: string | null;
  glJournalBatchId: string | null;
  postedToGL: boolean;
  postedAt: string | null;
  notes: string | null;
  createdById: string | null;
  version: number;
}

export class BgtBudgetTransfer {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _transferLines: BgtTransferLine[] = [];

  private constructor(
    private _id: BgtTransferId,
    private _transferNumber: string,
    private _sourceBudgetPlanId: string,
    private _targetBudgetPlanId: string,
    private _description: string | null,
    private _totalAmount: number,
    private _status: string,
    private _effectiveDate: Date | null,
    private _approvedById: string | null,
    private _approvedAt: Date | null,
    private _glJournalBatchId: string | null,
    private _postedToGL: boolean,
    private _postedAt: Date | null,
    private _notes: string | null,
    private _createdById: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtTransferId { return this._id; }
  get transferNumber(): string { return this._transferNumber; }
  get sourceBudgetPlanId(): string { return this._sourceBudgetPlanId; }
  get targetBudgetPlanId(): string { return this._targetBudgetPlanId; }
  get description(): string | null { return this._description; }
  get totalAmount(): number { return this._totalAmount; }
  get status(): string { return this._status; }
  get effectiveDate(): Date | null { return this._effectiveDate; }
  get approvedById(): string | null { return this._approvedById; }
  get postedToGL(): boolean { return this._postedToGL; }
  get transferLines(): BgtTransferLine[] { return this._transferLines; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    transferNumber: string; sourceBudgetPlanId: string;
    targetBudgetPlanId: string; totalAmount: number;
    description?: string; effectiveDate?: Date; notes?: string;
    createdById?: string;
  }): BgtBudgetTransfer {
    const t = new BgtBudgetTransfer(
      BgtTransferId.generate(), p.transferNumber, p.sourceBudgetPlanId,
      p.targetBudgetPlanId, p.description ?? null, p.totalAmount,
      BgtTransferStatus.Draft, p.effectiveDate ?? null,
      null, null, null, false, null, p.notes ?? null,
      p.createdById ?? null, 1,
    );
    t._events.push(new BgtBudgetTransferCreated(
      t._id.value, p.sourceBudgetPlanId, p.targetBudgetPlanId, p.totalAmount,
    ));
    return t;
  }

  static load(state: BgtBudgetTransferState): BgtBudgetTransfer {
    return new BgtBudgetTransfer(
      BgtTransferId.from(state.id), state.transferNumber,
      state.sourceBudgetPlanId, state.targetBudgetPlanId,
      state.description, state.totalAmount, state.status,
      state.effectiveDate ? new Date(state.effectiveDate) : null,
      state.approvedById, state.approvedAt ? new Date(state.approvedAt) : null,
      state.glJournalBatchId, state.postedToGL,
      state.postedAt ? new Date(state.postedAt) : null,
      state.notes, state.createdById, state.version,
    );
  }

  toState(): BgtBudgetTransferState {
    return {
      id: this._id.value, transferNumber: this._transferNumber,
      sourceBudgetPlanId: this._sourceBudgetPlanId,
      targetBudgetPlanId: this._targetBudgetPlanId,
      description: this._description, totalAmount: this._totalAmount,
      status: this._status,
      effectiveDate: this._effectiveDate?.toISOString() ?? null,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt?.toISOString() ?? null,
      glJournalBatchId: this._glJournalBatchId,
      postedToGL: this._postedToGL,
      postedAt: this._postedAt?.toISOString() ?? null,
      notes: this._notes, createdById: this._createdById,
      version: this._version,
    };
  }

  submit(): void {
    if (this._status !== BgtTransferStatus.Draft) throw new Error("Transfer must be draft to submit");
    this._status = BgtTransferStatus.Submitted;
  }

  approve(approvedById: string): void {
    if (this._status !== BgtTransferStatus.Submitted) throw new Error("Transfer must be submitted to approve");
    this._status = BgtTransferStatus.Approved;
    this._approvedById = approvedById;
    this._approvedAt = new Date();
  }

  complete(): void {
    if (this._status !== BgtTransferStatus.Approved) throw new Error("Transfer must be approved to complete");
    this._status = BgtTransferStatus.Completed;
    this._events.push(new BgtBudgetTransferCompleted(
      this._id.value, this._sourceBudgetPlanId, this._targetBudgetPlanId,
    ));
  }

  markPostedToGL(glBatchId: string): void {
    this._postedToGL = true;
    this._glJournalBatchId = glBatchId;
    this._postedAt = new Date();
  }

  cancel(): void {
    if (this._status === BgtTransferStatus.Completed) throw new Error("Cannot cancel completed transfer");
    this._status = BgtTransferStatus.Cancelled;
  }

  addLine(line: BgtTransferLine): void {
    this._transferLines.push(line);
  }
}

// ─── Transfer Line ────────────────────────────────────────────────────────────

export interface BgtTransferLineState {
  id: string;
  transferId: string;
  lineNumber: number;
  sourceBudgetDetailId: string | null;
  targetBudgetDetailId: string | null;
  sourceGlAccountId: string | null;
  targetGlAccountId: string | null;
  amount: number;
  description: string | null;
  periodNumber: number;
  version: number;
}

export class BgtTransferLine {
  private constructor(
    private _id: BgtTransferLineId,
    private _transferId: string,
    private _lineNumber: number,
    private _sourceBudgetDetailId: string | null,
    private _targetBudgetDetailId: string | null,
    private _sourceGlAccountId: string | null,
    private _targetGlAccountId: string | null,
    private _amount: number,
    private _description: string | null,
    private _periodNumber: number,
    private _version: number,
  ) {}

  get id(): BgtTransferLineId { return this._id; }
  get transferId(): string { return this._transferId; }
  get lineNumber(): number { return this._lineNumber; }
  get sourceBudgetDetailId(): string | null { return this._sourceBudgetDetailId; }
  get targetBudgetDetailId(): string | null { return this._targetBudgetDetailId; }
  get sourceGlAccountId(): string | null { return this._sourceGlAccountId; }
  get targetGlAccountId(): string | null { return this._targetGlAccountId; }
  get amount(): number { return this._amount; }

  static create(p: {
    transferId: string; lineNumber: number; amount: number;
    sourceBudgetDetailId?: string; targetBudgetDetailId?: string;
    sourceGlAccountId?: string; targetGlAccountId?: string;
    description?: string; periodNumber?: number;
  }): BgtTransferLine {
    return new BgtTransferLine(
      BgtTransferLineId.generate(), p.transferId, p.lineNumber,
      p.sourceBudgetDetailId ?? null, p.targetBudgetDetailId ?? null,
      p.sourceGlAccountId ?? null, p.targetGlAccountId ?? null,
      p.amount, p.description ?? null, p.periodNumber ?? 1, 1,
    );
  }

  static load(state: BgtTransferLineState): BgtTransferLine {
    return new BgtTransferLine(
      BgtTransferLineId.from(state.id), state.transferId, state.lineNumber,
      state.sourceBudgetDetailId, state.targetBudgetDetailId,
      state.sourceGlAccountId, state.targetGlAccountId,
      state.amount, state.description, state.periodNumber, state.version,
    );
  }

  toState(): BgtTransferLineState {
    return {
      id: this._id.value, transferId: this._transferId,
      lineNumber: this._lineNumber,
      sourceBudgetDetailId: this._sourceBudgetDetailId,
      targetBudgetDetailId: this._targetBudgetDetailId,
      sourceGlAccountId: this._sourceGlAccountId,
      targetGlAccountId: this._targetGlAccountId,
      amount: this._amount, description: this._description,
      periodNumber: this._periodNumber, version: this._version,
    };
  }
}
