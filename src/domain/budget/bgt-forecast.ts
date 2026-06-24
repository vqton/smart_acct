import { BgtForecastHeaderId, BgtForecastLineId, BgtForecastDriverId } from "./bgt-ids.js";
import { BgtForecastMethod, BgtForecastStatus, BgtPeriodType } from "./bgt-enums.js";
import { BgtForecastCreated, BgtForecastApproved, BgtDomainEvent } from "./bgt-events.js";

export interface BgtForecastHeaderState {
  id: string;
  budgetPlanId: string;
  scenarioId: string | null;
  forecastNumber: string;
  forecastMethod: string;
  status: string;
  description: string | null;
  forecastPeriods: number;
  periodType: string;
  startDate: string | null;
  endDate: string | null;
  totalForecastAmount: number;
  confidencePct: number | null;
  notes: string | null;
  createdById: string | null;
  approvedById: string | null;
  approvedAt: string | null;
  version: number;
}

export class BgtForecastHeader {
  private _events: BgtDomainEvent[] = [];
  private _version: number;
  private _lines: BgtForecastLine[] = [];
  private _drivers: BgtForecastDriver[] = [];

  private constructor(
    private _id: BgtForecastHeaderId,
    private _budgetPlanId: string,
    private _scenarioId: string | null,
    private _forecastNumber: string,
    private _forecastMethod: string,
    private _status: string,
    private _description: string | null,
    private _forecastPeriods: number,
    private _periodType: string,
    private _startDate: Date | null,
    private _endDate: Date | null,
    private _totalForecastAmount: number,
    private _confidencePct: number | null,
    private _notes: string | null,
    private _createdById: string | null,
    private _approvedById: string | null,
    private _approvedAt: Date | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtForecastHeaderId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get scenarioId(): string | null { return this._scenarioId; }
  get forecastNumber(): string { return this._forecastNumber; }
  get forecastMethod(): string { return this._forecastMethod; }
  get status(): string { return this._status; }
  get description(): string | null { return this._description; }
  get forecastPeriods(): number { return this._forecastPeriods; }
  get periodType(): string { return this._periodType; }
  get startDate(): Date | null { return this._startDate; }
  get endDate(): Date | null { return this._endDate; }
  get totalForecastAmount(): number { return this._totalForecastAmount; }
  get confidencePct(): number | null { return this._confidencePct; }
  get notes(): string | null { return this._notes; }
  get createdById(): string | null { return this._createdById; }
  get approvedById(): string | null { return this._approvedById; }
  get approvedAt(): Date | null { return this._approvedAt; }
  get version(): number { return this._version; }
  get lines(): BgtForecastLine[] { return this._lines; }
  get drivers(): BgtForecastDriver[] { return this._drivers; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; forecastNumber: string; forecastMethod?: string;
    scenarioId?: string; description?: string; forecastPeriods?: number;
    periodType?: string; startDate?: Date; endDate?: Date;
    totalForecastAmount?: number; confidencePct?: number;
    notes?: string; createdById?: string;
  }): BgtForecastHeader {
    const f = new BgtForecastHeader(
      BgtForecastHeaderId.generate(), p.budgetPlanId, p.scenarioId ?? null,
      p.forecastNumber, p.forecastMethod ?? BgtForecastMethod.Manual,
      BgtForecastStatus.Draft, p.description ?? null,
      p.forecastPeriods ?? 12, p.periodType ?? BgtPeriodType.Monthly,
      p.startDate ?? null, p.endDate ?? null, p.totalForecastAmount ?? 0,
      p.confidencePct ?? null, p.notes ?? null, p.createdById ?? null,
      null, null, 1,
    );
    f._events.push(new BgtForecastCreated(f._id.value, p.budgetPlanId, p.forecastMethod ?? BgtForecastMethod.Manual));
    return f;
  }

  static load(state: BgtForecastHeaderState): BgtForecastHeader {
    return new BgtForecastHeader(
      BgtForecastHeaderId.from(state.id), state.budgetPlanId, state.scenarioId,
      state.forecastNumber, state.forecastMethod, state.status,
      state.description, state.forecastPeriods, state.periodType,
      state.startDate ? new Date(state.startDate) : null,
      state.endDate ? new Date(state.endDate) : null,
      state.totalForecastAmount, state.confidencePct, state.notes,
      state.createdById, state.approvedById,
      state.approvedAt ? new Date(state.approvedAt) : null,
      state.version,
    );
  }

  toState(): BgtForecastHeaderState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      scenarioId: this._scenarioId, forecastNumber: this._forecastNumber,
      forecastMethod: this._forecastMethod, status: this._status,
      description: this._description, forecastPeriods: this._forecastPeriods,
      periodType: this._periodType,
      startDate: this._startDate?.toISOString() ?? null,
      endDate: this._endDate?.toISOString() ?? null,
      totalForecastAmount: this._totalForecastAmount,
      confidencePct: this._confidencePct, notes: this._notes,
      createdById: this._createdById, approvedById: this._approvedById,
      approvedAt: this._approvedAt?.toISOString() ?? null,
      version: this._version,
    };
  }

  addLine(line: BgtForecastLine): void {
    this._lines.push(line);
    this.recalcTotal();
  }

  removeLine(lineId: string): void {
    this._lines = this._lines.filter(l => l.id.value !== lineId);
    this.recalcTotal();
  }

  addDriver(driver: BgtForecastDriver): void {
    this._drivers.push(driver);
  }

  submit(): void {
    if (this._status !== BgtForecastStatus.Draft) throw new Error("Forecast must be draft to submit");
    this._status = BgtForecastStatus.Submitted;
  }

  approve(approvedById: string): void {
    if (this._status !== BgtForecastStatus.Submitted) throw new Error("Forecast must be submitted to approve");
    this._status = BgtForecastStatus.Approved;
    this._approvedById = approvedById;
    this._approvedAt = new Date();
    this._events.push(new BgtForecastApproved(this._id.value, approvedById));
  }

  publish(): void {
    if (this._status !== BgtForecastStatus.Approved) throw new Error("Forecast must be approved to publish");
    this._status = BgtForecastStatus.Published;
  }

  private recalcTotal(): void {
    this._totalForecastAmount = this._lines.reduce((s, l) => s + l.forecastAmount, 0);
  }
}

// ─── Forecast Line ────────────────────────────────────────────────────────────

export interface BgtForecastLineState {
  id: string;
  forecastHeaderId: string;
  lineNumber: number;
  glAccountId: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  productId: string | null;
  description: string | null;
  forecastAmount: number;
  actualAmount: number;
  varianceAmount: number;
  variancePct: number;
  notes: string | null;
  version: number;
}

export class BgtForecastLine {
  private constructor(
    private _id: BgtForecastLineId,
    private _forecastHeaderId: string,
    private _lineNumber: number,
    private _glAccountId: string | null,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _projectId: string | null,
    private _productId: string | null,
    private _description: string | null,
    private _forecastAmount: number,
    private _actualAmount: number,
    private _notes: string | null,
    private _version: number,
  ) {}

  get id(): BgtForecastLineId { return this._id; }
  get forecastHeaderId(): string { return this._forecastHeaderId; }
  get lineNumber(): number { return this._lineNumber; }
  get glAccountId(): string | null { return this._glAccountId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get departmentId(): string | null { return this._departmentId; }
  get projectId(): string | null { return this._projectId; }
  get productId(): string | null { return this._productId; }
  get description(): string | null { return this._description; }
  get forecastAmount(): number { return this._forecastAmount; }
  get actualAmount(): number { return this._actualAmount; }
  get varianceAmount(): number { return this._actualAmount - this._forecastAmount; }
  get variancePct(): number {
    if (this._forecastAmount === 0) return this._actualAmount === 0 ? 0 : 100;
    return Math.round((this.varianceAmount / this._forecastAmount) * 10000) / 100;
  }
  get notes(): string | null { return this._notes; }
  get version(): number { return this._version; }

  static create(p: {
    forecastHeaderId: string; lineNumber: number;
    glAccountId?: string; costCenterId?: string; departmentId?: string;
    projectId?: string; productId?: string; description?: string;
    forecastAmount?: number; actualAmount?: number; notes?: string;
  }): BgtForecastLine {
    return new BgtForecastLine(
      BgtForecastLineId.generate(), p.forecastHeaderId, p.lineNumber,
      p.glAccountId ?? null, p.costCenterId ?? null, p.departmentId ?? null,
      p.projectId ?? null, p.productId ?? null, p.description ?? null,
      p.forecastAmount ?? 0, p.actualAmount ?? 0, p.notes ?? null, 1,
    );
  }

  static load(state: BgtForecastLineState): BgtForecastLine {
    return new BgtForecastLine(
      BgtForecastLineId.from(state.id), state.forecastHeaderId,
      state.lineNumber, state.glAccountId, state.costCenterId,
      state.departmentId, state.projectId, state.productId,
      state.description, state.forecastAmount, state.actualAmount,
      state.notes, state.version,
    );
  }

  toState(): BgtForecastLineState {
    return {
      id: this._id.value, forecastHeaderId: this._forecastHeaderId,
      lineNumber: this._lineNumber, glAccountId: this._glAccountId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      projectId: this._projectId, productId: this._productId,
      description: this._description, forecastAmount: this._forecastAmount,
      actualAmount: this._actualAmount,
      varianceAmount: this.varianceAmount, variancePct: this.variancePct,
      notes: this._notes, version: this._version,
    };
  }

  updateForecast(amount: number): void {
    this._forecastAmount = amount;
  }

  updateActual(amount: number): void {
    this._actualAmount = amount;
  }
}

// ─── Forecast Driver ──────────────────────────────────────────────────────────

export interface BgtForecastDriverState {
  id: string;
  forecastHeaderId: string;
  driverName: string;
  driverType: string;
  baseValue: number;
  growthRate: number;
  seasonalFactor: number;
  period1Value: number; period2Value: number; period3Value: number;
  period4Value: number; period5Value: number; period6Value: number;
  period7Value: number; period8Value: number; period9Value: number;
  period10Value: number; period11Value: number; period12Value: number;
  isActive: boolean;
  version: number;
}

export class BgtForecastDriver {
  private constructor(
    private _id: BgtForecastDriverId,
    private _forecastHeaderId: string,
    private _driverName: string,
    private _driverType: string,
    private _baseValue: number,
    private _growthRate: number,
    private _seasonalFactor: number,
    private _periodValues: number[],
    private _isActive: boolean,
    private _version: number,
  ) {}

  get id(): BgtForecastDriverId { return this._id; }
  get forecastHeaderId(): string { return this._forecastHeaderId; }
  get driverName(): string { return this._driverName; }
  get driverType(): string { return this._driverType; }
  get baseValue(): number { return this._baseValue; }
  get growthRate(): number { return this._growthRate; }
  get seasonalFactor(): number { return this._seasonalFactor; }
  get periodValues(): number[] { return this._periodValues; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  get projectedTotal(): number {
    let total = 0;
    for (let i = 0; i < this._periodValues.length; i++) {
      const growthFactor = Math.pow(1 + this._growthRate, i);
      total += this._periodValues[i] * growthFactor * this._seasonalFactor;
    }
    return total;
  }

  static create(p: {
    forecastHeaderId: string; driverName: string; driverType: string;
    baseValue?: number; growthRate?: number; seasonalFactor?: number;
    periodValues?: number[]; isActive?: boolean;
  }): BgtForecastDriver {
    const pv = p.periodValues ?? new Array(12).fill(p.baseValue ?? 0);
    return new BgtForecastDriver(
      BgtForecastDriverId.generate(), p.forecastHeaderId, p.driverName,
      p.driverType, p.baseValue ?? 0, p.growthRate ?? 0,
      p.seasonalFactor ?? 1, pv, p.isActive ?? true, 1,
    );
  }

  static load(state: BgtForecastDriverState): BgtForecastDriver {
    return new BgtForecastDriver(
      BgtForecastDriverId.from(state.id), state.forecastHeaderId,
      state.driverName, state.driverType, state.baseValue, state.growthRate,
      state.seasonalFactor,
      [state.period1Value, state.period2Value, state.period3Value,
        state.period4Value, state.period5Value, state.period6Value,
        state.period7Value, state.period8Value, state.period9Value,
        state.period10Value, state.period11Value, state.period12Value],
      state.isActive, state.version,
    );
  }

  toState(): BgtForecastDriverState {
    return {
      id: this._id.value, forecastHeaderId: this._forecastHeaderId,
      driverName: this._driverName, driverType: this._driverType,
      baseValue: this._baseValue, growthRate: this._growthRate,
      seasonalFactor: this._seasonalFactor,
      period1Value: this._periodValues[0] ?? 0,
      period2Value: this._periodValues[1] ?? 0,
      period3Value: this._periodValues[2] ?? 0,
      period4Value: this._periodValues[3] ?? 0,
      period5Value: this._periodValues[4] ?? 0,
      period6Value: this._periodValues[5] ?? 0,
      period7Value: this._periodValues[6] ?? 0,
      period8Value: this._periodValues[7] ?? 0,
      period9Value: this._periodValues[8] ?? 0,
      period10Value: this._periodValues[9] ?? 0,
      period11Value: this._periodValues[10] ?? 0,
      period12Value: this._periodValues[11] ?? 0,
      isActive: this._isActive, version: this._version,
    };
  }
}
