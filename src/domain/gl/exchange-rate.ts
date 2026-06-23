import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class ExchangeRateId extends Identifier {
  static new(): ExchangeRateId {
    return new ExchangeRateId(IdGenerator.uuid());
  }
}

export enum ExchangeRateType {
  Buy = "buy",
  Sell = "sell",
  Transfer = "transfer",
  Reference = "reference",
}

export interface ExchangeRateState {
  id: string;
  fromCurrency: string;
  toCurrency: string;
  rate: number;
  rateType: ExchangeRateType;
  validFrom: Date;
  validTo: Date;
  source: string | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class ExchangeRate extends AggregateRoot<ExchangeRateId> {
  private _id: ExchangeRateId;
  private _fromCurrency: string;
  private _toCurrency: string;
  private _rate: number;
  private _rateType: ExchangeRateType;
  private _validFrom: Date;
  private _validTo: Date;
  private _source: string | null;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(
    id: ExchangeRateId,
    fromCurrency: string,
    toCurrency: string,
    rate: number,
    rateType: ExchangeRateType,
    validFrom: Date,
    validTo: Date,
    source: string | null = null,
  ) {
    super();
    if (rate <= 0) throw new DomainError("Validation", "Exchange rate must be positive");
    this._id = id;
    this._fromCurrency = fromCurrency;
    this._toCurrency = toCurrency;
    this._rate = rate;
    this._rateType = rateType;
    this._validFrom = validFrom;
    this._validTo = validTo;
    this._source = source;
    this._isActive = true;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static create(params: {
    fromCurrency: string;
    toCurrency: string;
    rate: number;
    rateType: ExchangeRateType;
    validFrom: Date;
    validTo: Date;
    source?: string;
  }): ExchangeRate {
    return new ExchangeRate(
      ExchangeRateId.new(),
      params.fromCurrency.toUpperCase(),
      params.toCurrency.toUpperCase(),
      params.rate,
      params.rateType,
      params.validFrom,
      params.validTo,
      params.source ?? null,
    );
  }

  static load(state: ExchangeRateState): ExchangeRate {
    const er = new ExchangeRate(
      new ExchangeRateId(state.id),
      state.fromCurrency,
      state.toCurrency,
      state.rate,
      state.rateType,
      state.validFrom,
      state.validTo,
      state.source,
    );
    er._isActive = state.isActive;
    er._createdAt = state.createdAt;
    er._updatedAt = state.updatedAt;
    er._version = state.version;
    return er;
  }

  get id(): ExchangeRateId { return this._id; }
  get fromCurrency(): string { return this._fromCurrency; }
  get toCurrency(): string { return this._toCurrency; }
  get rate(): number { return this._rate; }
  get rateType(): ExchangeRateType { return this._rateType; }
  get validFrom(): Date { return this._validFrom; }
  get validTo(): Date { return this._validTo; }
  get source(): string | null { return this._source; }
  get isActive(): boolean { return this._isActive; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }

  isValidAt(date: Date): boolean {
    return date >= this._validFrom && date <= this._validTo && this._isActive;
  }

  convert(amount: number): number {
    return amount * this._rate;
  }

  modify(rate: number): void {
    if (rate <= 0) throw new DomainError("Validation", "Exchange rate must be positive");
    this._rate = rate;
    this._updatedAt = new Date();
    this._version++;
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): ExchangeRateState {
    return {
      id: this._id.value,
      fromCurrency: this._fromCurrency,
      toCurrency: this._toCurrency,
      rate: this._rate,
      rateType: this._rateType,
      validFrom: this._validFrom,
      validTo: this._validTo,
      source: this._source,
      isActive: this._isActive,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
