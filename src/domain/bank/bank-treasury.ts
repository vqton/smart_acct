import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashPositionId, CashForecastId, FXRateId, FXRevaluationId, InterestCalculationId } from "./bank-ids.js";
import { CashPositionStatus, FXRateType, InterestCalculationMethod, InterestBasis } from "./bank-enums.js";
import { CashPositionUpdated, FXRevaluationPosted } from "./bank-events.js";

// ─── Cash Position ──────────────────────────────────────────────────────────────

export interface CashPositionState {
  id: string; companyId: string; positionDate: Date;
  currencyCode: string; openingBalance: number; totalInflows: number;
  totalOutflows: number; netFlow: number; closingBalance: number;
  availableBalance: number; blockedBalance: number; pendingInflows: number;
  pendingOutflows: number; projectedBalance: number; minimumBalance: number;
  maximumBalance: number; status: string;
  isReconciled: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class CashPosition extends AggregateRoot<CashPositionId> {
  private _id: CashPositionId; private _companyId: string; private _positionDate: Date;
  private _currencyCode: string; private _openingBalance: number;
  private _totalInflows: number; private _totalOutflows: number;
  private _netFlow: number; private _closingBalance: number;
  private _availableBalance: number; private _blockedBalance: number;
  private _pendingInflows: number; private _pendingOutflows: number;
  private _projectedBalance: number; private _minimumBalance: number;
  private _maximumBalance: number; private _status: CashPositionStatus;
  private _isReconciled: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: CashPositionId, companyId: string, positionDate: Date, currencyCode: string) {
    super(); this._id = id; this._companyId = companyId; this._positionDate = positionDate; this._currencyCode = currencyCode;
    this._openingBalance = 0; this._totalInflows = 0; this._totalOutflows = 0; this._netFlow = 0;
    this._closingBalance = 0; this._availableBalance = 0; this._blockedBalance = 0;
    this._pendingInflows = 0; this._pendingOutflows = 0; this._projectedBalance = 0;
    this._minimumBalance = 0; this._maximumBalance = 0;
    this._status = CashPositionStatus.Draft; this._isReconciled = false;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { companyId: string; positionDate: Date; currencyCode?: string; openingBalance?: number }): CashPosition {
    const c = new CashPosition(CashPositionId.new(), p.companyId, p.positionDate, p.currencyCode ?? "VND");
    c._openingBalance = p.openingBalance ?? 0; return c;
  }

  static load(s: CashPositionState): CashPosition {
    const c = new CashPosition(new CashPositionId(s.id), s.companyId, s.positionDate, s.currencyCode);
    c._openingBalance = s.openingBalance; c._totalInflows = s.totalInflows; c._totalOutflows = s.totalOutflows;
    c._netFlow = s.netFlow; c._closingBalance = s.closingBalance; c._availableBalance = s.availableBalance;
    c._blockedBalance = s.blockedBalance; c._pendingInflows = s.pendingInflows; c._pendingOutflows = s.pendingOutflows;
    c._projectedBalance = s.projectedBalance; c._minimumBalance = s.minimumBalance; c._maximumBalance = s.maximumBalance;
    c._status = s.status as CashPositionStatus; c._isReconciled = s.isReconciled;
    c._version = s.version; c._createdAt = s.createdAt; c._updatedAt = s.updatedAt; c._deletedAt = s.deletedAt;
    return c;
  }

  get id(): CashPositionId { return this._id; }
  get closingBalance(): number { return this._closingBalance; }
  get projectedBalance(): number { return this._projectedBalance; }
  get status(): CashPositionStatus { return this._status; }

  addInflow(amount: number, isPending: boolean = false): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Inflow must be positive");
    this._totalInflows += amount;
    if (isPending) this._pendingInflows += amount;
    this._calculate(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new CashPositionUpdated(this._id.value, new Date(), { type: "inflow", amount }));
  }

  addOutflow(amount: number, isPending: boolean = false): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Outflow must be positive");
    this._totalOutflows += amount;
    if (isPending) this._pendingOutflows += amount;
    this._calculate(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new CashPositionUpdated(this._id.value, new Date(), { type: "outflow", amount }));
  }

  confirm(): void { this._status = CashPositionStatus.Confirmed; this._updatedAt = new Date(); this._version++; }

  approve(): void { this._status = CashPositionStatus.Approved; this._updatedAt = new Date(); this._version++; }

  lock(): void { this._status = CashPositionStatus.Locked; this._updatedAt = new Date(); this._version++; }

  private _calculate(): void {
    this._netFlow = this._totalInflows - this._totalOutflows;
    this._closingBalance = this._openingBalance + this._netFlow;
    this._availableBalance = this._closingBalance - this._blockedBalance;
    this._projectedBalance = this._closingBalance + this._pendingInflows - this._pendingOutflows;
  }

  toState(): CashPositionState {
    return { id: this._id.value, companyId: this._companyId, positionDate: this._positionDate,
      currencyCode: this._currencyCode, openingBalance: this._openingBalance,
      totalInflows: this._totalInflows, totalOutflows: this._totalOutflows,
      netFlow: this._netFlow, closingBalance: this._closingBalance,
      availableBalance: this._availableBalance, blockedBalance: this._blockedBalance,
      pendingInflows: this._pendingInflows, pendingOutflows: this._pendingOutflows,
      projectedBalance: this._projectedBalance, minimumBalance: this._minimumBalance,
      maximumBalance: this._maximumBalance, status: this._status, isReconciled: this._isReconciled,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}

// ─── Cash Forecast ──────────────────────────────────────────────────────────────

export interface CashForecastState {
  id: string; companyId: string; forecastNumber: string; name: string;
  periodStart: Date; periodEnd: Date; currencyCode: string;
  openingBalance: number; projectedInflows: number; projectedOutflows: number;
  netProjected: number; closingBalance: number; minimumRequired: number;
  surplusDeficit: number; confidenceLevel: number; status: string;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class CashForecast extends AggregateRoot<CashForecastId> {
  private _id: CashForecastId; private _companyId: string; private _forecastNumber: string;
  private _name: string; private _periodStart: Date; private _periodEnd: Date;
  private _currencyCode: string; private _openingBalance: number;
  private _projectedInflows: number; private _projectedOutflows: number;
  private _netProjected: number; private _closingBalance: number;
  private _minimumRequired: number; private _surplusDeficit: number;
  private _confidenceLevel: number; private _status: CashPositionStatus;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: CashForecastId, companyId: string, forecastNumber: string,
    name: string, periodStart: Date, periodEnd: Date, currencyCode: string) {
    super(); this._id = id; this._companyId = companyId; this._forecastNumber = forecastNumber;
    this._name = name; this._periodStart = periodStart; this._periodEnd = periodEnd;
    this._currencyCode = currencyCode;
    this._openingBalance = 0; this._projectedInflows = 0; this._projectedOutflows = 0;
    this._netProjected = 0; this._closingBalance = 0; this._minimumRequired = 0;
    this._surplusDeficit = 0; this._confidenceLevel = 0;
    this._status = CashPositionStatus.Draft;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { companyId: string; forecastNumber: string; name: string;
    periodStart: Date; periodEnd: Date; currencyCode?: string;
    openingBalance?: number; minimumRequired?: number }): CashForecast {
    const f = new CashForecast(CashForecastId.new(), p.companyId, p.forecastNumber,
      p.name, p.periodStart, p.periodEnd, p.currencyCode ?? "VND");
    f._openingBalance = p.openingBalance ?? 0; f._minimumRequired = p.minimumRequired ?? 0;
    return f;
  }

  static load(s: CashForecastState): CashForecast {
    const f = new CashForecast(new CashForecastId(s.id), s.companyId, s.forecastNumber,
      s.name, s.periodStart, s.periodEnd, s.currencyCode);
    f._openingBalance = s.openingBalance; f._projectedInflows = s.projectedInflows;
    f._projectedOutflows = s.projectedOutflows; f._netProjected = s.netProjected;
    f._closingBalance = s.closingBalance; f._minimumRequired = s.minimumRequired;
    f._surplusDeficit = s.surplusDeficit; f._confidenceLevel = s.confidenceLevel;
    f._status = s.status as CashPositionStatus;
    f._version = s.version; f._createdAt = s.createdAt; f._updatedAt = s.updatedAt; f._deletedAt = s.deletedAt;
    return f;
  }

  get id(): CashForecastId { return this._id; }

  addProjection(inflow: number, outflow: number): void {
    this._projectedInflows += inflow; this._projectedOutflows += outflow;
    this._netProjected = this._projectedInflows - this._projectedOutflows;
    this._closingBalance = this._openingBalance + this._netProjected;
    this._surplusDeficit = this._closingBalance - this._minimumRequired;
    this._updatedAt = new Date(); this._version++;
  }

  confirm(): void { this._status = CashPositionStatus.Confirmed; this._updatedAt = new Date(); this._version++; }

  toState(): CashForecastState {
    return { id: this._id.value, companyId: this._companyId, forecastNumber: this._forecastNumber,
      name: this._name, periodStart: this._periodStart, periodEnd: this._periodEnd,
      currencyCode: this._currencyCode, openingBalance: this._openingBalance,
      projectedInflows: this._projectedInflows, projectedOutflows: this._projectedOutflows,
      netProjected: this._netProjected, closingBalance: this._closingBalance,
      minimumRequired: this._minimumRequired, surplusDeficit: this._surplusDeficit,
      confidenceLevel: this._confidenceLevel, status: this._status,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── FX Rate ────────────────────────────────────────────────────────────────────

export interface FXRateState {
  id: string; fromCurrency: string; toCurrency: string; rate: number;
  rateType: string; validFrom: Date; validTo: Date; source: string | null;
  isActive: boolean; version: number;
  createdAt: Date; updatedAt: Date;
}

export class FXRate {
  constructor(
    private _id: FXRateId, private _fromCurrency: string, private _toCurrency: string,
    private _rate: number, private _rateType: FXRateType, private _validFrom: Date,
    private _validTo: Date, private _source: string | null, private _isActive: boolean = true,
  ) {}

  get id(): FXRateId { return this._id; }
  get rate(): number { return this._rate; }
  get fromCurrency(): string { return this._fromCurrency; }
  get toCurrency(): string { return this._toCurrency; }
  get rateType(): FXRateType { return this._rateType; }
  get isActive(): boolean { return this._isActive; }

  isEffective(date: Date): boolean { return date >= this._validFrom && date <= this._validTo; }

  toState(): FXRateState {
    return { id: this._id.value, fromCurrency: this._fromCurrency, toCurrency: this._toCurrency,
      rate: this._rate, rateType: this._rateType, validFrom: this._validFrom, validTo: this._validTo,
      source: this._source, isActive: this._isActive, version: 1, createdAt: new Date(), updatedAt: new Date() };
  }
}

// ─── FX Revaluation ─────────────────────────────────────────────────────────────

export interface FXRevaluationState {
  id: string; companyId: string; revaluationDate: Date;
  currencyCode: string; exchangeRate: number; previousRate: number;
  accountId: string; accountBalance: number; fxGainLoss: number;
  gainLossType: string; isRealized: boolean;
  sourceTransactionId: string | null; glBatchId: string | null;
  postedToGL: boolean; version: number;
  createdAt: Date; updatedAt: Date;
}

export class FXRevaluation extends AggregateRoot<FXRevaluationId> {
  private _id: FXRevaluationId; private _companyId: string; private _revaluationDate: Date;
  private _currencyCode: string; private _exchangeRate: number; private _previousRate: number;
  private _accountId: string; private _accountBalance: number; private _fxGainLoss: number;
  private _gainLossType: "gain" | "loss"; private _isRealized: boolean;
  private _sourceTransactionId: string | null; private _glBatchId: string | null;
  private _postedToGL: boolean; private _version: number;
  private _createdAt: Date; private _updatedAt: Date;

  private constructor(id: FXRevaluationId, companyId: string, revaluationDate: Date,
    currencyCode: string, exchangeRate: number, accountId: string, accountBalance: number) {
    super(); this._id = id; this._companyId = companyId; this._revaluationDate = revaluationDate;
    this._currencyCode = currencyCode; this._exchangeRate = exchangeRate;
    this._previousRate = 0; this._accountId = accountId; this._accountBalance = accountBalance;
    this._fxGainLoss = 0; this._gainLossType = "gain"; this._isRealized = false;
    this._sourceTransactionId = null; this._glBatchId = null; this._postedToGL = false;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { companyId: string; revaluationDate: Date; currencyCode: string;
    exchangeRate: number; previousRate: number; accountId: string;
    accountBalance: number; isRealized?: boolean; sourceTransactionId?: string | null }): FXRevaluation {
    const r = new FXRevaluation(FXRevaluationId.new(), p.companyId, p.revaluationDate,
      p.currencyCode, p.exchangeRate, p.accountId, p.accountBalance);
    r._previousRate = p.previousRate;
    const vndValueCurrent = p.accountBalance * p.exchangeRate;
    const vndValuePrev = p.accountBalance * p.previousRate;
    r._fxGainLoss = vndValueCurrent - vndValuePrev;
    r._gainLossType = r._fxGainLoss >= 0 ? "gain" : "loss";
    r._isRealized = p.isRealized ?? false;
    r._sourceTransactionId = p.sourceTransactionId ?? null;
    return r;
  }

  static load(s: FXRevaluationState): FXRevaluation {
    const r = new FXRevaluation(new FXRevaluationId(s.id), s.companyId, s.revaluationDate,
      s.currencyCode, s.exchangeRate, s.accountId, s.accountBalance);
    r._previousRate = s.previousRate; r._fxGainLoss = s.fxGainLoss;
    r._gainLossType = s.gainLossType as "gain" | "loss"; r._isRealized = s.isRealized;
    r._sourceTransactionId = s.sourceTransactionId; r._glBatchId = s.glBatchId;
    r._postedToGL = s.postedToGL; r._version = s.version;
    r._createdAt = s.createdAt; r._updatedAt = s.updatedAt;
    return r;
  }

  get id(): FXRevaluationId { return this._id; }
  get fxGainLoss(): number { return this._fxGainLoss; }
  get gainLossType(): string { return this._gainLossType; }

  markGLPosted(batchId: string): void {
    this._postedToGL = true; this._glBatchId = batchId;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new FXRevaluationPosted(this._id.value, new Date(), {
      accountId: this._accountId, currencyCode: this._currencyCode,
      fxGainLoss: this._fxGainLoss, gainLossType: this._gainLossType,
    }));
  }

  toState(): FXRevaluationState {
    return { id: this._id.value, companyId: this._companyId, revaluationDate: this._revaluationDate,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      previousRate: this._previousRate, accountId: this._accountId,
      accountBalance: this._accountBalance, fxGainLoss: this._fxGainLoss,
      gainLossType: this._gainLossType, isRealized: this._isRealized,
      sourceTransactionId: this._sourceTransactionId, glBatchId: this._glBatchId,
      postedToGL: this._postedToGL, version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}
