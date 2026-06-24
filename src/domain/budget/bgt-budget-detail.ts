import { BgtBudgetDetailId } from "./bgt-ids.js";
import { BgtPeriodAmounts, BgtMoney } from "./bgt-value-objects.js";
import { BgtDomainEvent } from "./bgt-events.js";

export interface BgtBudgetDetailState {
  id: string;
  budgetPlanId: string;
  versionId: string | null;
  lineNumber: number;
  description: string | null;
  glAccountId: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  productId: string | null;
  customerId: string | null;
  supplierId: string | null;
  employeeId: string | null;
  assetId: string | null;
  locationId: string | null;
  activityId: string | null;
  contractId: string | null;
  campaignId: string | null;
  dimension1Id: string | null;
  dimension2Id: string | null;
  dimension3Id: string | null;
  dimension4Id: string | null;
  dimension5Id: string | null;
  originalAmount: number;
  currentAmount: number;
  approvedAmount: number;
  reservedAmount: number;
  consumedAmount: number;
  remainingAmount: number;
  committedAmount: number;
  encumberedAmount: number;
  availableAmount: number;
  period1: number; period2: number; period3: number; period4: number;
  period5: number; period6: number; period7: number; period8: number;
  period9: number; period10: number; period11: number; period12: number;
  period13: number; period14: number; period15: number; period16: number;
  period17: number; period18: number; period19: number; period20: number;
  period21: number; period22: number; period23: number; period24: number;
  customPeriod1: number; customPeriod2: number; customPeriod3: number;
  customPeriod4: number; customPeriod5: number; customPeriod6: number;
  isActive: boolean;
  notes: string | null;
  version: number;
}

export class BgtBudgetDetail {
  private _events: BgtDomainEvent[] = [];
  private _version: number;

  private constructor(
    private _id: BgtBudgetDetailId,
    private _budgetPlanId: string,
    private _versionId: string | null,
    private _lineNumber: number,
    private _description: string | null,
    private _glAccountId: string | null,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _projectId: string | null,
    private _productId: string | null,
    private _customerId: string | null,
    private _supplierId: string | null,
    private _employeeId: string | null,
    private _assetId: string | null,
    private _locationId: string | null,
    private _activityId: string | null,
    private _contractId: string | null,
    private _campaignId: string | null,
    private _dimension1Id: string | null,
    private _dimension2Id: string | null,
    private _dimension3Id: string | null,
    private _dimension4Id: string | null,
    private _dimension5Id: string | null,
    private _originalAmount: number,
    private _currentAmount: number,
    private _approvedAmount: number,
    private _reservedAmount: number,
    private _consumedAmount: number,
    private _remainingAmount: number,
    private _committedAmount: number,
    private _encumberedAmount: number,
    private _availableAmount: number,
    private _periods: BgtPeriodAmounts,
    private _customPeriod1: number,
    private _customPeriod2: number,
    private _customPeriod3: number,
    private _customPeriod4: number,
    private _customPeriod5: number,
    private _customPeriod6: number,
    private _isActive: boolean,
    private _notes: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtBudgetDetailId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get versionId(): string | null { return this._versionId; }
  get lineNumber(): number { return this._lineNumber; }
  get description(): string | null { return this._description; }
  get glAccountId(): string | null { return this._glAccountId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get departmentId(): string | null { return this._departmentId; }
  get projectId(): string | null { return this._projectId; }
  get productId(): string | null { return this._productId; }
  get customerId(): string | null { return this._customerId; }
  get supplierId(): string | null { return this._supplierId; }
  get employeeId(): string | null { return this._employeeId; }
  get assetId(): string | null { return this._assetId; }
  get locationId(): string | null { return this._locationId; }
  get activityId(): string | null { return this._activityId; }
  get contractId(): string | null { return this._contractId; }
  get campaignId(): string | null { return this._campaignId; }
  get dimension1Id(): string | null { return this._dimension1Id; }
  get dimension2Id(): string | null { return this._dimension2Id; }
  get dimension3Id(): string | null { return this._dimension3Id; }
  get dimension4Id(): string | null { return this._dimension4Id; }
  get dimension5Id(): string | null { return this._dimension5Id; }
  get originalAmount(): number { return this._originalAmount; }
  get currentAmount(): number { return this._currentAmount; }
  get approvedAmount(): number { return this._approvedAmount; }
  get reservedAmount(): number { return this._reservedAmount; }
  get consumedAmount(): number { return this._consumedAmount; }
  get remainingAmount(): number { return this._remainingAmount; }
  get committedAmount(): number { return this._committedAmount; }
  get encumberedAmount(): number { return this._encumberedAmount; }
  get availableAmount(): number { return this._availableAmount; }
  get periods(): BgtPeriodAmounts { return this._periods; }
  get customPeriod1(): number { return this._customPeriod1; }
  get customPeriod2(): number { return this._customPeriod2; }
  get customPeriod3(): number { return this._customPeriod3; }
  get customPeriod4(): number { return this._customPeriod4; }
  get customPeriod5(): number { return this._customPeriod5; }
  get customPeriod6(): number { return this._customPeriod6; }
  get isActive(): boolean { return this._isActive; }
  get notes(): string | null { return this._notes; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  get totalPeriodAmount(): number { return this._periods.total(); }

  static create(p: {
    budgetPlanId: string; lineNumber: number; glAccountId?: string;
    costCenterId?: string; departmentId?: string; projectId?: string;
    productId?: string; customerId?: string; supplierId?: string;
    employeeId?: string; assetId?: string; locationId?: string;
    activityId?: string; contractId?: string; campaignId?: string;
    dimension1Id?: string; dimension2Id?: string; dimension3Id?: string;
    dimension4Id?: string; dimension5Id?: string;
    originalAmount?: number; currentAmount?: number;
    description?: string; versionId?: string; notes?: string;
  }): BgtBudgetDetail {
    const orig = p.originalAmount ?? 0;
    const cur = p.currentAmount ?? orig;
    return new BgtBudgetDetail(
      BgtBudgetDetailId.generate(), p.budgetPlanId, p.versionId ?? null,
      p.lineNumber, p.description ?? null, p.glAccountId ?? null,
      p.costCenterId ?? null, p.departmentId ?? null, p.projectId ?? null,
      p.productId ?? null, p.customerId ?? null, p.supplierId ?? null,
      p.employeeId ?? null, p.assetId ?? null, p.locationId ?? null,
      p.activityId ?? null, p.contractId ?? null, p.campaignId ?? null,
      p.dimension1Id ?? null, p.dimension2Id ?? null, p.dimension3Id ?? null,
      p.dimension4Id ?? null, p.dimension5Id ?? null,
      orig, cur, 0, 0, 0, cur, 0, 0, cur,
      BgtPeriodAmounts.fromArray([]), 0, 0, 0, 0, 0, 0,
      true, p.notes ?? null, 1,
    );
  }

  static load(state: BgtBudgetDetailState): BgtBudgetDetail {
    return new BgtBudgetDetail(
      BgtBudgetDetailId.from(state.id), state.budgetPlanId, state.versionId,
      state.lineNumber, state.description, state.glAccountId,
      state.costCenterId, state.departmentId, state.projectId,
      state.productId, state.customerId, state.supplierId,
      state.employeeId, state.assetId, state.locationId,
      state.activityId, state.contractId, state.campaignId,
      state.dimension1Id, state.dimension2Id, state.dimension3Id,
      state.dimension4Id, state.dimension5Id,
      state.originalAmount, state.currentAmount, state.approvedAmount,
      state.reservedAmount, state.consumedAmount, state.remainingAmount,
      state.committedAmount, state.encumberedAmount, state.availableAmount,
      BgtPeriodAmounts.fromState(state),
      state.customPeriod1, state.customPeriod2, state.customPeriod3,
      state.customPeriod4, state.customPeriod5, state.customPeriod6,
      state.isActive, state.notes, state.version,
    );
  }

  toState(): BgtBudgetDetailState {
    const p = this._periods;
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      versionId: this._versionId, lineNumber: this._lineNumber,
      description: this._description, glAccountId: this._glAccountId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      projectId: this._projectId, productId: this._productId,
      customerId: this._customerId, supplierId: this._supplierId,
      employeeId: this._employeeId, assetId: this._assetId,
      locationId: this._locationId, activityId: this._activityId,
      contractId: this._contractId, campaignId: this._campaignId,
      dimension1Id: this._dimension1Id, dimension2Id: this._dimension2Id,
      dimension3Id: this._dimension3Id, dimension4Id: this._dimension4Id,
      dimension5Id: this._dimension5Id,
      originalAmount: this._originalAmount, currentAmount: this._currentAmount,
      approvedAmount: this._approvedAmount, reservedAmount: this._reservedAmount,
      consumedAmount: this._consumedAmount, remainingAmount: this._remainingAmount,
      committedAmount: this._committedAmount, encumberedAmount: this._encumberedAmount,
      availableAmount: this._availableAmount,
      period1: p.period1, period2: p.period2, period3: p.period3,
      period4: p.period4, period5: p.period5, period6: p.period6,
      period7: p.period7, period8: p.period8, period9: p.period9,
      period10: p.period10, period11: p.period11, period12: p.period12,
      period13: p.period13, period14: p.period14, period15: p.period15,
      period16: p.period16, period17: p.period17, period18: p.period18,
      period19: p.period19, period20: p.period20, period21: p.period21,
      period22: p.period22, period23: p.period23, period24: p.period24,
      customPeriod1: this._customPeriod1, customPeriod2: this._customPeriod2,
      customPeriod3: this._customPeriod3, customPeriod4: this._customPeriod4,
      customPeriod5: this._customPeriod5, customPeriod6: this._customPeriod6,
      isActive: this._isActive, notes: this._notes, version: this._version,
    };
  }

  updateAmount(amount: number): void {
    this._currentAmount = amount;
    this._remainingAmount = amount - this._consumedAmount - this._reservedAmount;
    this.recalcAvailable();
  }

  approve(): void {
    this._approvedAmount = this._currentAmount;
  }

  recordConsumption(amount: number, periodNumber?: number): void {
    this._consumedAmount += amount;
    this._remainingAmount = Math.max(0, this._currentAmount - this._consumedAmount - this._reservedAmount);
    this._committedAmount = Math.max(0, this._committedAmount - amount);
    this.recalcAvailable();
    if (periodNumber) {
      const current = this._periods.getPeriod(periodNumber);
      this._periods = this._periods.setPeriod(periodNumber, current + amount);
    }
  }

  recordReservation(amount: number): void {
    this._reservedAmount += amount;
    this._remainingAmount = Math.max(0, this._currentAmount - this._consumedAmount - this._reservedAmount);
    this.recalcAvailable();
  }

  releaseReservation(amount: number): void {
    this._reservedAmount = Math.max(0, this._reservedAmount - amount);
    this._committedAmount = Math.max(0, this._committedAmount - amount);
    this._remainingAmount = this._currentAmount - this._consumedAmount - this._reservedAmount;
    this.recalcAvailable();
  }

  recordCommitment(amount: number): void {
    this._committedAmount += amount;
    this._remainingAmount = Math.max(0, this._currentAmount - this._consumedAmount - this._reservedAmount);
    this.recalcAvailable();
  }

  recordEncumbrance(amount: number): void {
    this._encumberedAmount += amount;
  }

  private recalcAvailable(): void {
    this._availableAmount = this._remainingAmount - this._committedAmount - this._encumberedAmount;
  }

  setPeriodAmount(period: number, amount: number): void {
    this._periods = this._periods.setPeriod(period, amount);
    this._currentAmount = this._periods.total();
    this._remainingAmount = this._currentAmount - this._consumedAmount - this._reservedAmount;
    this.recalcAvailable();
  }

  deactivate(): void { this._isActive = false; }
  activate(): void { this._isActive = true; }
}
