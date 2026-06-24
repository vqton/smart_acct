import { BgtAllocationRuleId, BgtAllocationRuleLineId, BgtAllocationResultId } from "./bgt-ids.js";
import { BgtAllocationMethod, BgtAllocationStatus, BgtPeriodType } from "./bgt-enums.js";
import { BgtAllocationExecuted, BgtAllocationPostedToGL, BgtDomainEvent } from "./bgt-events.js";
import { BgtAllocationTotalMatchesSpec } from "./bgt-specifications.js";

export interface BgtAllocationRuleState {
  id: string;
  code: string;
  name: string;
  description: string | null;
  allocationMethod: string;
  status: string;
  sourceBudgetPlanId: string | null;
  targetBudgetPlanId: string | null;
  sourceDimensionType: string | null;
  sourceDimensionId: string | null;
  targetDimensionType: string | null;
  targetDimensionId: string | null;
  totalAmount: number;
  allocatedAmount: number;
  remainingAmount: number;
  fiscalYearId: string | null;
  periodType: string;
  isRecurring: boolean;
  recurrenceInterval: string | null;
  lastRunAt: string | null;
  nextRunAt: string | null;
  notes: string | null;
  createdById: string | null;
  approvedById: string | null;
  version: number;
}

export class BgtAllocationRule {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _ruleLines: BgtAllocationRuleLine[] = [];

  private constructor(
    private _id: BgtAllocationRuleId,
    private _code: string,
    private _name: string,
    private _description: string | null,
    private _allocationMethod: string,
    private _status: string,
    private _sourceBudgetPlanId: string | null,
    private _targetBudgetPlanId: string | null,
    private _sourceDimensionType: string | null,
    private _sourceDimensionId: string | null,
    private _targetDimensionType: string | null,
    private _targetDimensionId: string | null,
    private _totalAmount: number,
    private _allocatedAmount: number,
    private _remainingAmount: number,
    private _fiscalYearId: string | null,
    private _periodType: string,
    private _isRecurring: boolean,
    private _recurrenceInterval: string | null,
    private _lastRunAt: Date | null,
    private _nextRunAt: Date | null,
    private _notes: string | null,
    private _createdById: string | null,
    private _approvedById: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtAllocationRuleId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get description(): string | null { return this._description; }
  get allocationMethod(): string { return this._allocationMethod; }
  get status(): string { return this._status; }
  get sourceBudgetPlanId(): string | null { return this._sourceBudgetPlanId; }
  get targetBudgetPlanId(): string | null { return this._targetBudgetPlanId; }
  get totalAmount(): number { return this._totalAmount; }
  get allocatedAmount(): number { return this._allocatedAmount; }
  get remainingAmount(): number { return this._remainingAmount; }
  get fiscalYearId(): string | null { return this._fiscalYearId; }
  get isRecurring(): boolean { return this._isRecurring; }
  get notes(): string | null { return this._notes; }
  get ruleLines(): BgtAllocationRuleLine[] { return this._ruleLines; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    code: string; name: string; allocationMethod?: string;
    description?: string; sourceBudgetPlanId?: string;
    targetBudgetPlanId?: string; sourceDimensionType?: string;
    sourceDimensionId?: string; targetDimensionType?: string;
    targetDimensionId?: string; totalAmount?: number;
    fiscalYearId?: string; periodType?: string; isRecurring?: boolean;
    recurrenceInterval?: string; notes?: string; createdById?: string;
  }): BgtAllocationRule {
    const total = p.totalAmount ?? 0;
    return new BgtAllocationRule(
      BgtAllocationRuleId.generate(), p.code, p.name, p.description ?? null,
      p.allocationMethod ?? BgtAllocationMethod.Percentage,
      BgtAllocationStatus.Draft, p.sourceBudgetPlanId ?? null,
      p.targetBudgetPlanId ?? null, p.sourceDimensionType ?? null,
      p.sourceDimensionId ?? null, p.targetDimensionType ?? null,
      p.targetDimensionId ?? null, total, 0, total,
      p.fiscalYearId ?? null, p.periodType ?? BgtPeriodType.Monthly,
      p.isRecurring ?? false, p.recurrenceInterval ?? null,
      null, null, p.notes ?? null, p.createdById ?? null, null, 1,
    );
  }

  static load(state: BgtAllocationRuleState): BgtAllocationRule {
    return new BgtAllocationRule(
      BgtAllocationRuleId.from(state.id), state.code, state.name,
      state.description, state.allocationMethod, state.status,
      state.sourceBudgetPlanId, state.targetBudgetPlanId,
      state.sourceDimensionType, state.sourceDimensionId,
      state.targetDimensionType, state.targetDimensionId,
      state.totalAmount, state.allocatedAmount, state.remainingAmount,
      state.fiscalYearId, state.periodType, state.isRecurring,
      state.recurrenceInterval,
      state.lastRunAt ? new Date(state.lastRunAt) : null,
      state.nextRunAt ? new Date(state.nextRunAt) : null,
      state.notes, state.createdById, state.approvedById, state.version,
    );
  }

  toState(): BgtAllocationRuleState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      description: this._description, allocationMethod: this._allocationMethod,
      status: this._status, sourceBudgetPlanId: this._sourceBudgetPlanId,
      targetBudgetPlanId: this._targetBudgetPlanId,
      sourceDimensionType: this._sourceDimensionType,
      sourceDimensionId: this._sourceDimensionId,
      targetDimensionType: this._targetDimensionType,
      targetDimensionId: this._targetDimensionId,
      totalAmount: this._totalAmount, allocatedAmount: this._allocatedAmount,
      remainingAmount: this._remainingAmount, fiscalYearId: this._fiscalYearId,
      periodType: this._periodType, isRecurring: this._isRecurring,
      recurrenceInterval: this._recurrenceInterval,
      lastRunAt: this._lastRunAt?.toISOString() ?? null,
      nextRunAt: this._nextRunAt?.toISOString() ?? null,
      notes: this._notes, createdById: this._createdById,
      approvedById: this._approvedById, version: this._version,
    };
  }

  addLine(line: BgtAllocationRuleLine): void {
    this._ruleLines.push(line);
    if (!new BgtAllocationTotalMatchesSpec(this._totalAmount).isSatisfiedBy(
      this._ruleLines.map(l => ({ allocationPct: l.allocationPct, allocationAmount: l.allocationAmount })),
    )) {
      this._ruleLines.pop();
      throw new Error("Allocation line total does not match rule total");
    }
  }

  execute(periodId?: string): BgtAllocationResult {
    if (this._status !== BgtAllocationStatus.Draft && this._status !== BgtAllocationStatus.Calculated) {
      throw new Error(`Cannot execute rule in status ${this._status}`);
    }
    const result = BgtAllocationResult.create({
      ruleId: this._id.value, runNumber: `RUN-${Date.now()}`,
      periodId, sourceAmount: this._totalAmount,
      allocatedAmount: this._totalAmount,
    });
    this._allocatedAmount = this._totalAmount;
    this._remainingAmount = 0;
    this._lastRunAt = new Date();
    this._status = BgtAllocationStatus.Calculated;
    this._events.push(new BgtAllocationExecuted(this._id.value, result.id.value, this._totalAmount));
    return result;
  }
}

// ─── Allocation Rule Line ─────────────────────────────────────────────────────

export interface BgtAllocationRuleLineState {
  id: string;
  ruleId: string;
  lineNumber: number;
  sourceGlAccountId: string | null;
  targetGlAccountId: string | null;
  sourceCostCenterId: string | null;
  targetCostCenterId: string | null;
  sourceDepartmentId: string | null;
  targetDepartmentId: string | null;
  sourceProjectId: string | null;
  targetProjectId: string | null;
  allocationPct: number;
  allocationAmount: number;
  driverId: string | null;
  driverValue: number | null;
  description: string | null;
  isActive: boolean;
  version: number;
}

export class BgtAllocationRuleLine {
  private constructor(
    private _id: BgtAllocationRuleLineId,
    private _ruleId: string,
    private _lineNumber: number,
    private _sourceGlAccountId: string | null,
    private _targetGlAccountId: string | null,
    private _sourceCostCenterId: string | null,
    private _targetCostCenterId: string | null,
    private _sourceDepartmentId: string | null,
    private _targetDepartmentId: string | null,
    private _sourceProjectId: string | null,
    private _targetProjectId: string | null,
    private _allocationPct: number,
    private _allocationAmount: number,
    private _driverId: string | null,
    private _driverValue: number | null,
    private _description: string | null,
    private _isActive: boolean,
    private _version: number,
  ) {}

  get id(): BgtAllocationRuleLineId { return this._id; }
  get ruleId(): string { return this._ruleId; }
  get lineNumber(): number { return this._lineNumber; }
  get allocationPct(): number { return this._allocationPct; }
  get allocationAmount(): number { return this._allocationAmount; }
  get isActive(): boolean { return this._isActive; }

  static create(p: {
    ruleId: string; lineNumber: number;
    sourceGlAccountId?: string; targetGlAccountId?: string;
    sourceCostCenterId?: string; targetCostCenterId?: string;
    sourceDepartmentId?: string; targetDepartmentId?: string;
    sourceProjectId?: string; targetProjectId?: string;
    allocationPct?: number; allocationAmount?: number;
    driverId?: string; driverValue?: number; description?: string;
  }): BgtAllocationRuleLine {
    return new BgtAllocationRuleLine(
      BgtAllocationRuleLineId.generate(), p.ruleId, p.lineNumber,
      p.sourceGlAccountId ?? null, p.targetGlAccountId ?? null,
      p.sourceCostCenterId ?? null, p.targetCostCenterId ?? null,
      p.sourceDepartmentId ?? null, p.targetDepartmentId ?? null,
      p.sourceProjectId ?? null, p.targetProjectId ?? null,
      p.allocationPct ?? 0, p.allocationAmount ?? 0,
      p.driverId ?? null, p.driverValue ?? null,
      p.description ?? null, true, 1,
    );
  }

  static load(state: BgtAllocationRuleLineState): BgtAllocationRuleLine {
    return new BgtAllocationRuleLine(
      BgtAllocationRuleLineId.from(state.id), state.ruleId, state.lineNumber,
      state.sourceGlAccountId, state.targetGlAccountId,
      state.sourceCostCenterId, state.targetCostCenterId,
      state.sourceDepartmentId, state.targetDepartmentId,
      state.sourceProjectId, state.targetProjectId,
      state.allocationPct, state.allocationAmount,
      state.driverId, state.driverValue, state.description,
      state.isActive, state.version,
    );
  }

  toState(): BgtAllocationRuleLineState {
    return {
      id: this._id.value, ruleId: this._ruleId, lineNumber: this._lineNumber,
      sourceGlAccountId: this._sourceGlAccountId,
      targetGlAccountId: this._targetGlAccountId,
      sourceCostCenterId: this._sourceCostCenterId,
      targetCostCenterId: this._targetCostCenterId,
      sourceDepartmentId: this._sourceDepartmentId,
      targetDepartmentId: this._targetDepartmentId,
      sourceProjectId: this._sourceProjectId,
      targetProjectId: this._targetProjectId,
      allocationPct: this._allocationPct,
      allocationAmount: this._allocationAmount,
      driverId: this._driverId, driverValue: this._driverValue,
      description: this._description, isActive: this._isActive,
      version: this._version,
    };
  }
}

// ─── Allocation Result ────────────────────────────────────────────────────────

export interface BgtAllocationResultState {
  id: string;
  ruleId: string;
  runNumber: string;
  periodId: string | null;
  sourceAmount: number;
  allocatedAmount: number;
  sourceAccountId: string | null;
  targetAccountId: string | null;
  sourceCostCenterId: string | null;
  targetCostCenterId: string | null;
  sourceDepartmentId: string | null;
  targetDepartmentId: string | null;
  sourceProjectId: string | null;
  targetProjectId: string | null;
  glJournalBatchId: string | null;
  postedToGL: boolean;
  postedAt: string | null;
  version: number;
}

export class BgtAllocationResult {
  private _events: BgtDomainEvent[] = [];

  private constructor(
    private _id: BgtAllocationResultId,
    private _ruleId: string,
    private _runNumber: string,
    private _periodId: string | null,
    private _sourceAmount: number,
    private _allocatedAmount: number,
    private _sourceAccountId: string | null,
    private _targetAccountId: string | null,
    private _sourceCostCenterId: string | null,
    private _targetCostCenterId: string | null,
    private _sourceDepartmentId: string | null,
    private _targetDepartmentId: string | null,
    private _sourceProjectId: string | null,
    private _targetProjectId: string | null,
    private _glJournalBatchId: string | null,
    private _postedToGL: boolean,
    private _postedAt: Date | null,
    private _version: number,
  ) {}

  get id(): BgtAllocationResultId { return this._id; }
  get ruleId(): string { return this._ruleId; }
  get runNumber(): string { return this._runNumber; }
  get allocatedAmount(): number { return this._allocatedAmount; }
  get postedToGL(): boolean { return this._postedToGL; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    ruleId: string; runNumber: string; periodId?: string;
    sourceAmount: number; allocatedAmount: number;
    sourceAccountId?: string; targetAccountId?: string;
    sourceCostCenterId?: string; targetCostCenterId?: string;
    sourceDepartmentId?: string; targetDepartmentId?: string;
    sourceProjectId?: string; targetProjectId?: string;
  }): BgtAllocationResult {
    return new BgtAllocationResult(
      BgtAllocationResultId.generate(), p.ruleId, p.runNumber,
      p.periodId ?? null, p.sourceAmount, p.allocatedAmount,
      p.sourceAccountId ?? null, p.targetAccountId ?? null,
      p.sourceCostCenterId ?? null, p.targetCostCenterId ?? null,
      p.sourceDepartmentId ?? null, p.targetDepartmentId ?? null,
      p.sourceProjectId ?? null, p.targetProjectId ?? null,
      null, false, null, 1,
    );
  }

  static load(state: BgtAllocationResultState): BgtAllocationResult {
    return new BgtAllocationResult(
      BgtAllocationResultId.from(state.id), state.ruleId, state.runNumber,
      state.periodId, state.sourceAmount, state.allocatedAmount,
      state.sourceAccountId, state.targetAccountId,
      state.sourceCostCenterId, state.targetCostCenterId,
      state.sourceDepartmentId, state.targetDepartmentId,
      state.sourceProjectId, state.targetProjectId,
      state.glJournalBatchId, state.postedToGL,
      state.postedAt ? new Date(state.postedAt) : null, state.version,
    );
  }

  toState(): BgtAllocationResultState {
    return {
      id: this._id.value, ruleId: this._ruleId, runNumber: this._runNumber,
      periodId: this._periodId, sourceAmount: this._sourceAmount,
      allocatedAmount: this._allocatedAmount,
      sourceAccountId: this._sourceAccountId,
      targetAccountId: this._targetAccountId,
      sourceCostCenterId: this._sourceCostCenterId,
      targetCostCenterId: this._targetCostCenterId,
      sourceDepartmentId: this._sourceDepartmentId,
      targetDepartmentId: this._targetDepartmentId,
      sourceProjectId: this._sourceProjectId,
      targetProjectId: this._targetProjectId,
      glJournalBatchId: this._glJournalBatchId,
      postedToGL: this._postedToGL,
      postedAt: this._postedAt?.toISOString() ?? null,
      version: this._version,
    };
  }

  markPosted(glBatchId: string): void {
    this._postedToGL = true;
    this._glJournalBatchId = glBatchId;
    this._postedAt = new Date();
    this._events.push(new BgtAllocationPostedToGL(this._id.value, glBatchId));
  }
}
