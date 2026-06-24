import { BgtApprovalRequestId, BgtApprovalStepId } from "./bgt-ids.js";
import { BgtApprovalStatus, BgtApprovalDecision } from "./bgt-enums.js";
import {
  BgtApprovalRequestCreated, BgtApprovalStepCompleted, BgtApprovalCompleted, BgtDomainEvent,
} from "./bgt-events.js";

export interface BgtApprovalRequestState {
  id: string;
  budgetPlanId: string;
  requestNumber: string;
  description: string | null;
  status: string;
  totalAmount: number;
  requestedById: string | null;
  requestedAt: string;
  completedAt: string | null;
  notes: string | null;
  version: number;
}

export class BgtApprovalRequest {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _steps: BgtApprovalStep[] = [];

  private constructor(
    private _id: BgtApprovalRequestId,
    private _budgetPlanId: string,
    private _requestNumber: string,
    private _description: string | null,
    private _status: string,
    private _totalAmount: number,
    private _requestedById: string | null,
    private _requestedAt: Date,
    private _completedAt: Date | null,
    private _notes: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtApprovalRequestId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get requestNumber(): string { return this._requestNumber; }
  get description(): string | null { return this._description; }
  get status(): string { return this._status; }
  get totalAmount(): number { return this._totalAmount; }
  get requestedById(): string | null { return this._requestedById; }
  get completedAt(): Date | null { return this._completedAt; }
  get steps(): BgtApprovalStep[] { return this._steps; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; requestNumber: string; totalAmount: number;
    description?: string; requestedById?: string; notes?: string;
  }): BgtApprovalRequest {
    const r = new BgtApprovalRequest(
      BgtApprovalRequestId.generate(), p.budgetPlanId, p.requestNumber,
      p.description ?? null, BgtApprovalStatus.Pending, p.totalAmount,
      p.requestedById ?? null, new Date(), null, p.notes ?? null, 1,
    );
    r._events.push(new BgtApprovalRequestCreated(r._id.value, p.budgetPlanId, p.totalAmount));
    return r;
  }

  static load(state: BgtApprovalRequestState): BgtApprovalRequest {
    return new BgtApprovalRequest(
      BgtApprovalRequestId.from(state.id), state.budgetPlanId,
      state.requestNumber, state.description, state.status,
      state.totalAmount, state.requestedById,
      new Date(state.requestedAt),
      state.completedAt ? new Date(state.completedAt) : null,
      state.notes, state.version,
    );
  }

  toState(): BgtApprovalRequestState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      requestNumber: this._requestNumber, description: this._description,
      status: this._status, totalAmount: this._totalAmount,
      requestedById: this._requestedById,
      requestedAt: this._requestedAt.toISOString(),
      completedAt: this._completedAt?.toISOString() ?? null,
      notes: this._notes, version: this._version,
    };
  }

  addStep(step: BgtApprovalStep): void {
    if (this._status !== BgtApprovalStatus.Pending) throw new Error("Cannot add steps to non-pending request");
    if (this._steps.some(s => s.stepOrder === step.stepOrder)) throw new Error(`Step order ${step.stepOrder} already exists`);
    this._steps.push(step);
  }

  processStep(stepOrder: number, decision: string, approverId: string, comments?: string): void {
    const step = this._steps.find(s => s.stepOrder === stepOrder);
    if (!step) throw new Error(`Step ${stepOrder} not found`);
    if (step.status !== BgtApprovalStatus.Pending) throw new Error(`Step ${stepOrder} already processed`);

    step.decide(decision, approverId, comments);
    this._events.push(new BgtApprovalStepCompleted(this._id.value, stepOrder, decision, approverId));

    if (decision === BgtApprovalDecision.Reject) {
      this._status = BgtApprovalStatus.Rejected;
      this._completedAt = new Date();
      this._events.push(new BgtApprovalCompleted(this._id.value, this._budgetPlanId, this._status));
      return;
    }

    if (decision === BgtApprovalDecision.ReturnForRevision) {
      this._status = BgtApprovalStatus.Returned;
      this._completedAt = new Date();
      this._events.push(new BgtApprovalCompleted(this._id.value, this._budgetPlanId, this._status));
      return;
    }

    if (decision === BgtApprovalDecision.Delegate && step.delegateId) {
      step.delegate(step.delegateId);
      return;
    }

    if (decision === BgtApprovalDecision.Escalate) {
      this._status = BgtApprovalStatus.Escalated;
      this._events.push(new BgtApprovalCompleted(this._id.value, this._budgetPlanId, this._status));
      return;
    }

    const allApproved = this._steps.every(s => s.status === BgtApprovalStatus.Approved);
    if (allApproved) {
      this._status = BgtApprovalStatus.Approved;
      this._completedAt = new Date();
      this._events.push(new BgtApprovalCompleted(this._id.value, this._budgetPlanId, this._status));
    }
  }

  resubmit(): void {
    if (this._status !== BgtApprovalStatus.Returned) throw new Error("Only returned requests can be resubmitted");
    this._status = BgtApprovalStatus.Pending;
    this._completedAt = null;
    for (const step of this._steps) {
      step.reset();
    }
  }
}

// ─── Approval Step ────────────────────────────────────────────────────────────

export interface BgtApprovalStepState {
  id: string;
  approvalRequestId: string;
  stepOrder: number;
  approverId: string;
  delegateId: string | null;
  status: string;
  decision: string | null;
  comments: string | null;
  decidedAt: string | null;
  slaDeadline: string | null;
  reminderSentAt: string | null;
  escalationAt: string | null;
  version: number;
}

export class BgtApprovalStep {
  private constructor(
    private _id: BgtApprovalStepId,
    private _approvalRequestId: string,
    private _stepOrder: number,
    private _approverId: string,
    private _delegateId: string | null,
    private _status: string,
    private _decision: string | null,
    private _comments: string | null,
    private _decidedAt: Date | null,
    private _slaDeadline: Date | null,
    private _reminderSentAt: Date | null,
    private _escalationAt: Date | null,
    private _version: number,
  ) {}

  get id(): BgtApprovalStepId { return this._id; }
  get approvalRequestId(): string { return this._approvalRequestId; }
  get stepOrder(): number { return this._stepOrder; }
  get approverId(): string { return this._approverId; }
  get delegateId(): string | null { return this._delegateId; }
  get status(): string { return this._status; }
  get decision(): string | null { return this._decision; }

  static create(p: {
    approvalRequestId: string; stepOrder: number; approverId: string;
    delegateId?: string; slaDeadline?: Date; escalationAt?: Date;
  }): BgtApprovalStep {
    return new BgtApprovalStep(
      BgtApprovalStepId.generate(), p.approvalRequestId, p.stepOrder,
      p.approverId, p.delegateId ?? null, BgtApprovalStatus.Pending,
      null, null, null, p.slaDeadline ?? null, null,
      p.escalationAt ?? null, 1,
    );
  }

  static load(state: BgtApprovalStepState): BgtApprovalStep {
    return new BgtApprovalStep(
      BgtApprovalStepId.from(state.id), state.approvalRequestId,
      state.stepOrder, state.approverId, state.delegateId, state.status,
      state.decision, state.comments,
      state.decidedAt ? new Date(state.decidedAt) : null,
      state.slaDeadline ? new Date(state.slaDeadline) : null,
      state.reminderSentAt ? new Date(state.reminderSentAt) : null,
      state.escalationAt ? new Date(state.escalationAt) : null,
      state.version,
    );
  }

  toState(): BgtApprovalStepState {
    return {
      id: this._id.value, approvalRequestId: this._approvalRequestId,
      stepOrder: this._stepOrder, approverId: this._approverId,
      delegateId: this._delegateId, status: this._status,
      decision: this._decision, comments: this._comments,
      decidedAt: this._decidedAt?.toISOString() ?? null,
      slaDeadline: this._slaDeadline?.toISOString() ?? null,
      reminderSentAt: this._reminderSentAt?.toISOString() ?? null,
      escalationAt: this._escalationAt?.toISOString() ?? null,
      version: this._version,
    };
  }

  decide(decision: string, approverId: string, comments?: string): void {
    this._status = decision === BgtApprovalDecision.Approve
      ? BgtApprovalStatus.Approved
      : decision === BgtApprovalDecision.Reject
        ? BgtApprovalStatus.Rejected
        : decision === BgtApprovalDecision.ReturnForRevision
          ? BgtApprovalStatus.Returned
          : decision === BgtApprovalDecision.Escalate
            ? BgtApprovalStatus.Escalated
            : BgtApprovalStatus.Delegated;
    this._decision = decision;
    this._comments = comments ?? null;
    this._decidedAt = new Date();
  }

  delegate(delegateId: string): void {
    this._delegateId = delegateId;
    this._status = BgtApprovalStatus.Delegated;
  }

  reset(): void {
    this._status = BgtApprovalStatus.Pending;
    this._decision = null;
    this._comments = null;
    this._decidedAt = null;
  }

  sendReminder(): void {
    this._reminderSentAt = new Date();
  }
}
