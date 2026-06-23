import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashForecastId, LiquidityForecastId } from "./cm-ids.js";
import { CashForecastStatus } from "./cm-enums.js";

export interface CashForecastState {
  id: string;
  companyId: string;
  forecastNumber: string;
  forecastName: string;
  periodType: string;
  periodStart: Date;
  periodEnd: Date;
  status: string;
  totalInflow: number;
  totalOutflow: number;
  netFlow: number;
  openingBalance: number;
  closingBalance: number;
  currencyCode: string;
  preparedById: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashForecast extends AggregateRoot<CashForecastId> {
  private _id: CashForecastId;
  private _companyId: string;
  private _forecastNumber: string;
  private _forecastName: string;
  private _periodType: string;
  private _periodStart: Date;
  private _periodEnd: Date;
  private _status: CashForecastStatus;
  private _totalInflow: number;
  private _totalOutflow: number;
  private _netFlow: number;
  private _openingBalance: number;
  private _closingBalance: number;
  private _currencyCode: string;
  private _preparedById: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private _lines: CashForecastLine[] = [];

  constructor(
    id: CashForecastId,
    companyId: string,
    forecastNumber: string,
    forecastName: string,
    periodType: string,
    periodStart: Date,
    periodEnd: Date,
    currencyCode: string,
  ) {
    super();
    this._id = id;
    this._companyId = companyId;
    this._forecastNumber = forecastNumber;
    this._forecastName = forecastName;
    this._periodType = periodType;
    this._periodStart = periodStart;
    this._periodEnd = periodEnd;
    this._currencyCode = currencyCode;
    this._status = CashForecastStatus.Draft;
    this._totalInflow = 0;
    this._totalOutflow = 0;
    this._netFlow = 0;
    this._openingBalance = 0;
    this._closingBalance = 0;
    this._preparedById = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    companyId: string;
    forecastNumber: string;
    forecastName: string;
    periodType: string;
    periodStart: Date;
    periodEnd: Date;
    currencyCode?: string;
    openingBalance?: number;
    notes?: string | null;
  }): CashForecast {
    const f = new CashForecast(
      CashForecastId.new(),
      params.companyId,
      params.forecastNumber,
      params.forecastName,
      params.periodType,
      params.periodStart,
      params.periodEnd,
      params.currencyCode ?? "VND",
    );
    f._openingBalance = params.openingBalance ?? 0;
    f._notes = params.notes ?? null;
    return f;
  }

  static load(state: CashForecastState): CashForecast {
    const f = new CashForecast(
      new CashForecastId(state.id),
      state.companyId,
      state.forecastNumber,
      state.forecastName,
      state.periodType,
      state.periodStart,
      state.periodEnd,
      state.currencyCode,
    );
    f._status = state.status as CashForecastStatus;
    f._totalInflow = state.totalInflow;
    f._totalOutflow = state.totalOutflow;
    f._netFlow = state.netFlow;
    f._openingBalance = state.openingBalance;
    f._closingBalance = state.closingBalance;
    f._preparedById = state.preparedById;
    f._approvedById = state.approvedById;
    f._approvedAt = state.approvedAt;
    f._notes = state.notes;
    f._version = state.version;
    f._createdAt = state.createdAt;
    f._updatedAt = state.updatedAt;
    f._deletedAt = state.deletedAt;
    return f;
  }

  get id(): CashForecastId { return this._id; }
  get companyId(): string { return this._companyId; }
  get forecastNumber(): string { return this._forecastNumber; }
  get forecastName(): string { return this._forecastName; }
  get periodStart(): Date { return this._periodStart; }
  get periodEnd(): Date { return this._periodEnd; }
  get status(): CashForecastStatus { return this._status; }
  get totalInflow(): number { return this._totalInflow; }
  get totalOutflow(): number { return this._totalOutflow; }
  get netFlow(): number { return this._netFlow; }
  get openingBalance(): number { return this._openingBalance; }
  get closingBalance(): number { return this._closingBalance; }
  get lines(): readonly CashForecastLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(lineData: {
    lineDate: Date;
    description: string;
    inflowAmount?: number;
    outflowAmount?: number;
    category?: string | null;
    source?: string | null;
  }): void {
    const inflow = lineData.inflowAmount ?? 0;
    const outflow = lineData.outflowAmount ?? 0;
    const line = new CashForecastLine(
      this._id.value,
      lineData.lineDate,
      lineData.description,
      inflow,
      outflow,
      lineData.category ?? null,
      lineData.source ?? null,
    );
    this._lines.push(line);
    this._totalInflow += inflow;
    this._totalOutflow += outflow;
    this._netFlow = this._totalInflow - this._totalOutflow;
    this._closingBalance = this._openingBalance + this._netFlow;
    this._updatedAt = new Date();
    this._version++;
  }

  confirm(): void {
    if (this._status !== CashForecastStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft forecasts can be confirmed");
    }
    this._status = CashForecastStatus.Confirmed;
    this._updatedAt = new Date();
    this._version++;
  }

  lock(): void {
    if (this._status !== CashForecastStatus.Confirmed) {
      throw new DomainError("BusinessRule", "Only confirmed forecasts can be locked");
    }
    this._status = CashForecastStatus.Locked;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CashForecastState {
    return {
      id: this._id.value,
      companyId: this._companyId,
      forecastNumber: this._forecastNumber,
      forecastName: this._forecastName,
      periodType: this._periodType,
      periodStart: this._periodStart,
      periodEnd: this._periodEnd,
      status: this._status,
      totalInflow: this._totalInflow,
      totalOutflow: this._totalOutflow,
      netFlow: this._netFlow,
      openingBalance: this._openingBalance,
      closingBalance: this._closingBalance,
      currencyCode: this._currencyCode,
      preparedById: this._preparedById,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export class CashForecastLine {
  private _forecastId: string;
  private _lineDate: Date;
  private _description: string;
  private _inflowAmount: number;
  private _outflowAmount: number;
  private _netAmount: number;
  private _category: string | null;
  private _source: string | null;

  constructor(
    forecastId: string,
    lineDate: Date,
    description: string,
    inflowAmount: number,
    outflowAmount: number,
    category: string | null,
    source: string | null,
  ) {
    this._forecastId = forecastId;
    this._lineDate = lineDate;
    this._description = description;
    this._inflowAmount = inflowAmount;
    this._outflowAmount = outflowAmount;
    this._netAmount = inflowAmount - outflowAmount;
    this._category = category;
    this._source = source;
  }

  get lineDate(): Date { return this._lineDate; }
  get description(): string { return this._description; }
  get inflowAmount(): number { return this._inflowAmount; }
  get outflowAmount(): number { return this._outflowAmount; }
  get netAmount(): number { return this._netAmount; }
}

export interface LiquidityForecastState {
  id: string;
  companyId: string;
  forecastNumber: string;
  forecastName: string;
  forecastDate: Date;
  periodDays: number;
  totalInflow: number;
  totalOutflow: number;
  netLiquidity: number;
  currentCash: number;
  projectedCash: number;
  minimumRequired: number;
  surplusDeficit: number;
  currencyCode: string;
  status: string;
  preparedById: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class LiquidityForecast extends AggregateRoot<LiquidityForecastId> {
  private _id: LiquidityForecastId;
  private _companyId: string;
  private _forecastNumber: string;
  private _forecastName: string;
  private _forecastDate: Date;
  private _periodDays: number;
  private _totalInflow: number;
  private _totalOutflow: number;
  private _netLiquidity: number;
  private _currentCash: number;
  private _projectedCash: number;
  private _minimumRequired: number;
  private _surplusDeficit: number;
  private _currencyCode: string;
  private _status: CashForecastStatus;
  private _preparedById: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: LiquidityForecastId,
    companyId: string,
    forecastNumber: string,
    forecastName: string,
    forecastDate: Date,
    periodDays: number,
    currentCash: number,
    minimumRequired: number,
    currencyCode: string,
  ) {
    super();
    this._id = id;
    this._companyId = companyId;
    this._forecastNumber = forecastNumber;
    this._forecastName = forecastName;
    this._forecastDate = forecastDate;
    this._periodDays = periodDays;
    this._currentCash = currentCash;
    this._minimumRequired = minimumRequired;
    this._currencyCode = currencyCode;
    this._totalInflow = 0;
    this._totalOutflow = 0;
    this._netLiquidity = 0;
    this._projectedCash = currentCash;
    this._surplusDeficit = currentCash - minimumRequired;
    this._status = CashForecastStatus.Draft;
    this._preparedById = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  get id(): LiquidityForecastId { return this._id; }
  get forecastNumber(): string { return this._forecastNumber; }
  get status(): CashForecastStatus { return this._status; }
  get surplusDeficit(): number { return this._surplusDeficit; }
  get version(): number { return this._version; }

  static load(state: LiquidityForecastState): LiquidityForecast {
    const f = new LiquidityForecast(
      new LiquidityForecastId(state.id),
      state.companyId,
      state.forecastNumber,
      state.forecastName,
      state.forecastDate,
      state.periodDays,
      state.currentCash,
      state.minimumRequired,
      state.currencyCode,
    );
    f._totalInflow = state.totalInflow;
    f._totalOutflow = state.totalOutflow;
    f._netLiquidity = state.netLiquidity;
    f._projectedCash = state.projectedCash;
    f._surplusDeficit = state.surplusDeficit;
    f._status = state.status as CashForecastStatus;
    f._preparedById = state.preparedById;
    f._approvedById = state.approvedById;
    f._approvedAt = state.approvedAt;
    f._notes = state.notes;
    f._version = state.version;
    f._createdAt = state.createdAt;
    f._updatedAt = state.updatedAt;
    f._deletedAt = state.deletedAt;
    return f;
  }

  toState(): LiquidityForecastState {
    return {
      id: this._id.value,
      companyId: this._companyId,
      forecastNumber: this._forecastNumber,
      forecastName: this._forecastName,
      forecastDate: this._forecastDate,
      periodDays: this._periodDays,
      totalInflow: this._totalInflow,
      totalOutflow: this._totalOutflow,
      netLiquidity: this._netLiquidity,
      currentCash: this._currentCash,
      projectedCash: this._projectedCash,
      minimumRequired: this._minimumRequired,
      surplusDeficit: this._surplusDeficit,
      currencyCode: this._currencyCode,
      status: this._status,
      preparedById: this._preparedById,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
