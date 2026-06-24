import { BgtBudgetControlId } from "./bgt-ids.js";
import { BgtControlLevel, BgtControlAction } from "./bgt-enums.js";
import { BgtBudgetCheckPerformed, BgtBudgetExceeded, BgtDomainEvent } from "./bgt-events.js";
import { BgtBudgetCheckSpec } from "./bgt-specifications.js";

export interface BgtBudgetControlState {
  id: string;
  budgetDetailId: string;
  controlLevel: string;
  controlAction: string;
  toleranceAmount: number;
  tolerancePct: number;
  effectiveFrom: string | null;
  effectiveTo: string | null;
  isActive: boolean;
  checkedAt: string | null;
  checkedById: string | null;
  checkResult: string | null;
  checkMessage: string | null;
  version: number;
}

export class BgtBudgetControl {
  private _events: BgtDomainEvent[] = [];
  private _version: number;

  private constructor(
    private _id: BgtBudgetControlId,
    private _budgetDetailId: string,
    private _controlLevel: string,
    private _controlAction: string,
    private _toleranceAmount: number,
    private _tolerancePct: number,
    private _effectiveFrom: Date | null,
    private _effectiveTo: Date | null,
    private _isActive: boolean,
    private _checkedAt: Date | null,
    private _checkedById: string | null,
    private _checkResult: string | null,
    private _checkMessage: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtBudgetControlId { return this._id; }
  get budgetDetailId(): string { return this._budgetDetailId; }
  get controlLevel(): string { return this._controlLevel; }
  get controlAction(): string { return this._controlAction; }
  get toleranceAmount(): number { return this._toleranceAmount; }
  get tolerancePct(): number { return this._tolerancePct; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetDetailId: string; controlLevel?: string; controlAction?: string;
    toleranceAmount?: number; tolerancePct?: number;
    effectiveFrom?: Date; effectiveTo?: Date; isActive?: boolean;
  }): BgtBudgetControl {
    return new BgtBudgetControl(
      BgtBudgetControlId.generate(), p.budgetDetailId,
      p.controlLevel ?? BgtControlLevel.None,
      p.controlAction ?? BgtControlAction.Block,
      p.toleranceAmount ?? 0, p.tolerancePct ?? 0,
      p.effectiveFrom ?? null, p.effectiveTo ?? null,
      p.isActive ?? true, null, null, null, null, 1,
    );
  }

  static load(state: BgtBudgetControlState): BgtBudgetControl {
    return new BgtBudgetControl(
      BgtBudgetControlId.from(state.id), state.budgetDetailId,
      state.controlLevel, state.controlAction,
      state.toleranceAmount, state.tolerancePct,
      state.effectiveFrom ? new Date(state.effectiveFrom) : null,
      state.effectiveTo ? new Date(state.effectiveTo) : null,
      state.isActive,
      state.checkedAt ? new Date(state.checkedAt) : null,
      state.checkedById, state.checkResult, state.checkMessage,
      state.version,
    );
  }

  toState(): BgtBudgetControlState {
    return {
      id: this._id.value, budgetDetailId: this._budgetDetailId,
      controlLevel: this._controlLevel, controlAction: this._controlAction,
      toleranceAmount: this._toleranceAmount, tolerancePct: this._tolerancePct,
      effectiveFrom: this._effectiveFrom?.toISOString() ?? null,
      effectiveTo: this._effectiveTo?.toISOString() ?? null,
      isActive: this._isActive,
      checkedAt: this._checkedAt?.toISOString() ?? null,
      checkedById: this._checkedById, checkResult: this._checkResult,
      checkMessage: this._checkMessage, version: this._version,
    };
  }

  check(availableAmount: number, requestedAmount: number, checkedById?: string): { passed: boolean; action: string; message: string } {
    const spec = new BgtBudgetCheckSpec(
      this._controlLevel as BgtControlLevel,
      this._toleranceAmount, this._tolerancePct,
    );
    const result = spec.check(requestedAmount, availableAmount);
    this._checkedAt = new Date();
    this._checkedById = checkedById ?? null;
    this._checkResult = result.passed ? "passed" : "failed";
    this._checkMessage = result.message;
    this._events.push(new BgtBudgetCheckPerformed(
      this._budgetDetailId, requestedAmount, availableAmount, result.passed, this._controlLevel,
    ));
    if (!result.passed) {
      this._events.push(new BgtBudgetExceeded(
        this._budgetDetailId, requestedAmount, availableAmount, this._controlLevel,
      ));
    }
    return result;
  }

  update(p: {
    controlLevel?: string; controlAction?: string;
    toleranceAmount?: number; tolerancePct?: number;
    effectiveFrom?: Date; effectiveTo?: Date;
  }): void {
    if (p.controlLevel !== undefined) this._controlLevel = p.controlLevel;
    if (p.controlAction !== undefined) this._controlAction = p.controlAction;
    if (p.toleranceAmount !== undefined) this._toleranceAmount = p.toleranceAmount;
    if (p.tolerancePct !== undefined) this._tolerancePct = p.tolerancePct;
    if (p.effectiveFrom !== undefined) this._effectiveFrom = p.effectiveFrom;
    if (p.effectiveTo !== undefined) this._effectiveTo = p.effectiveTo;
  }

  deactivate(): void { this._isActive = false; }
  activate(): void { this._isActive = true; }
}
