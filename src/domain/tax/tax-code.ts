import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxRateId extends Identifier {
  static new(): TaxRateId { return new TaxRateId(IdGenerator.uuid()); }
}

export class TaxCodeId extends Identifier {
  static new(): TaxCodeId { return new TaxCodeId(IdGenerator.uuid()); }
  static from(value: string): TaxCodeId { return new TaxCodeId(value); }
}

export enum TaxRateType {
  Percentage = "percentage",
  Fixed = "fixed",
  PerUnit = "per_unit",
  Progressive = "progressive",
  Bracket = "bracket",
  Mixed = "mixed",
}

export enum TaxRateApplication {
  Inclusive = "inclusive",
  Exclusive = "exclusive",
  Compound = "compound",
  PerUnit = "per_unit",
}

export enum RoundingMethod {
  Round = "round",
  Floor = "floor",
  Ceil = "ceil",
  Truncate = "truncate",
}

export interface TaxRateState {
  id: string;
  taxCodeId: string;
  rate: number;
  rateType: TaxRateType;
  minimumAmount: number | null;
  maximumAmount: number | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  priority: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxRate extends AggregateRoot<TaxRateId> {
  private _id: TaxRateId;
  private _taxCodeId: string;
  private _rate: number;
  private _rateType: TaxRateType;
  private _minimumAmount: number | null;
  private _maximumAmount: number | null;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _priority: number;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(id: TaxRateId, taxCodeId: string, rate: number, rateType: TaxRateType, effectiveFrom: Date) {
    super();
    this._id = id;
    this._taxCodeId = taxCodeId;
    this._rate = rate;
    this._rateType = rateType;
    this._effectiveFrom = effectiveFrom;
    this._minimumAmount = null;
    this._maximumAmount = null;
    this._priority = 0;
    this._isActive = true;
    this._effectiveTo = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static create(taxCodeId: string, rate: number, rateType: TaxRateType, effectiveFrom: Date): TaxRate {
    return new TaxRate(TaxRateId.new(), taxCodeId, rate, rateType, effectiveFrom);
  }

  static load(state: TaxRateState): TaxRate {
    const r = new TaxRate(new TaxRateId(state.id), state.taxCodeId, state.rate, state.rateType, state.effectiveFrom);
    r._minimumAmount = state.minimumAmount;
    r._maximumAmount = state.maximumAmount;
    r._effectiveTo = state.effectiveTo;
    r._priority = state.priority;
    r._isActive = state.isActive;
    r._createdAt = state.createdAt;
    r._updatedAt = state.updatedAt;
    r._version = state.version;
    return r;
  }

  get id() { return this._id; }
  get taxCodeId() { return this._taxCodeId; }
  get rate() { return this._rate; }
  get rateType() { return this._rateType; }
  get minimumAmount() { return this._minimumAmount; }
  get maximumAmount() { return this._maximumAmount; }
  get effectiveFrom() { return this._effectiveFrom; }
  get effectiveTo() { return this._effectiveTo; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  isEffective(date: Date): boolean {
    return date >= this._effectiveFrom && (!this._effectiveTo || date <= this._effectiveTo) && this._isActive;
  }

  calculate(amount: number, quantity?: number): number {
    if (this._rateType === TaxRateType.Percentage) {
      return amount * (this._rate / 100);
    }
    if (this._rateType === TaxRateType.Fixed || this._rateType === TaxRateType.PerUnit) {
      return this._rate * (quantity ?? 1);
    }
    return amount * (this._rate / 100);
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): TaxRateState {
    return {
      id: this._id.value, taxCodeId: this._taxCodeId, rate: this._rate,
      rateType: this._rateType, minimumAmount: this._minimumAmount,
      maximumAmount: this._maximumAmount, effectiveFrom: this._effectiveFrom,
      effectiveTo: this._effectiveTo, priority: this._priority,
      isActive: this._isActive, createdAt: this._createdAt,
      updatedAt: this._updatedAt, version: this._version,
    };
  }
}

export interface TaxCodeState {
  id: string;
  code: string;
  name: string;
  taxTypeId: string;
  taxRateType: TaxRateType;
  application: TaxRateApplication;
  roundingMethod: RoundingMethod;
  precision: number;
  description: string | null;
  isActive: boolean;
  isRecoverable: boolean;
  isRefundable: boolean;
  isDeductible: boolean;
  glTaxAccountId: string | null;
  glRecoverableAccountId: string | null;
  glExpenseAccountId: string | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  rates: TaxRateState[];
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxCode extends AggregateRoot<TaxCodeId> {
  private _id: TaxCodeId;
  private _code: string;
  private _name: string;
  private _taxTypeId: string;
  private _taxRateType: TaxRateType;
  private _application: TaxRateApplication;
  private _roundingMethod: RoundingMethod;
  private _precision: number;
  private _isActive: boolean;
  private _isRecoverable: boolean;
  private _isRefundable: boolean;
  private _isDeductible: boolean;
  private _glTaxAccountId: string | null;
  private _glRecoverableAccountId: string | null;
  private _glExpenseAccountId: string | null;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _rates: TaxRate[];
  private _description: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(code: string, name: string, taxTypeId: string, taxRateType: TaxRateType, application: TaxRateApplication, effectiveFrom: Date) {
    super();
    this._id = TaxCodeId.new();
    this._code = code;
    this._name = name;
    this._taxTypeId = taxTypeId;
    this._taxRateType = taxRateType;
    this._application = application;
    this._effectiveFrom = effectiveFrom;
    this._roundingMethod = RoundingMethod.Round;
    this._precision = 0;
    this._isActive = true;
    this._isRecoverable = true;
    this._isRefundable = false;
    this._isDeductible = true;
    this._glTaxAccountId = null;
    this._glRecoverableAccountId = null;
    this._glExpenseAccountId = null;
    this._rates = [];
    this._effectiveTo = null;
    this._description = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: TaxCodeState): TaxCode {
    const tc = new TaxCode(state.code, state.name, state.taxTypeId, state.taxRateType, state.application, state.effectiveFrom);
    tc._id = new TaxCodeId(state.id);
    tc._roundingMethod = state.roundingMethod;
    tc._precision = state.precision;
    tc._isActive = state.isActive;
    tc._isRecoverable = state.isRecoverable;
    tc._isRefundable = state.isRefundable;
    tc._isDeductible = state.isDeductible;
    tc._glTaxAccountId = state.glTaxAccountId;
    tc._glRecoverableAccountId = state.glRecoverableAccountId;
    tc._glExpenseAccountId = state.glExpenseAccountId;
    tc._rates = state.rates.map(r => TaxRate.load(r));
    tc._effectiveTo = state.effectiveTo;
    tc._description = state.description;
    tc._createdAt = state.createdAt;
    tc._updatedAt = state.updatedAt;
    tc._version = state.version;
    return tc;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get taxTypeId() { return this._taxTypeId; }
  get taxRateType() { return this._taxRateType; }
  get application() { return this._application; }
  get roundingMethod() { return this._roundingMethod; }
  get precision() { return this._precision; }
  get isActive() { return this._isActive; }
  get isRecoverable() { return this._isRecoverable; }
  get isRefundable() { return this._isRefundable; }
  get isDeductible() { return this._isDeductible; }
  get rates() { return [...this._rates]; }
  get version() { return this._version; }
  get glTaxAccountId() { return this._glTaxAccountId; }
  get glRecoverableAccountId() { return this._glRecoverableAccountId; }
  get glExpenseAccountId() { return this._glExpenseAccountId; }

  setGlAccounts(accounts: { glTaxAccountId?: string | null; glRecoverableAccountId?: string | null; glExpenseAccountId?: string | null }): void {
    if (accounts.glTaxAccountId !== undefined) this._glTaxAccountId = accounts.glTaxAccountId;
    if (accounts.glRecoverableAccountId !== undefined) this._glRecoverableAccountId = accounts.glRecoverableAccountId;
    if (accounts.glExpenseAccountId !== undefined) this._glExpenseAccountId = accounts.glExpenseAccountId;
    this._updatedAt = new Date();
    this._version++;
  }

  addRate(rate: TaxRate): void {
    this._rates.push(rate);
    this._updatedAt = new Date();
    this._version++;
  }

  getEffectiveRate(date: Date): TaxRate | undefined {
    return this._rates.find(r => r.isEffective(date));
  }

  calculate(amount: number, date: Date, quantity?: number): {
    taxableAmount: number;
    taxAmount: number;
    totalAmount: number;
    rate: TaxRate;
  } {
    const rate = this.getEffectiveRate(date);
    if (!rate) throw new DomainError("BusinessRule", `No effective tax rate for ${this._code} on ${date.toISOString()}`);

    let taxAmount: number;

    if (this._application === TaxRateApplication.Inclusive) {
      const grossUp = amount / (1 + rate.rate / 100);
      taxAmount = rate.calculate(grossUp, quantity);
    } else if (this._application === TaxRateApplication.Compound) {
      const baseTax = rate.calculate(amount, quantity);
      taxAmount = baseTax + rate.calculate(amount + baseTax, quantity);
    } else {
      taxAmount = rate.calculate(amount, quantity);
    }

    taxAmount = this.applyRounding(taxAmount, this._precision);

    return {
      taxableAmount: amount,
      taxAmount,
      totalAmount: this._application === TaxRateApplication.Inclusive ? amount : amount + taxAmount,
      rate,
    };
  }

  private applyRounding(amount: number, precision: number): number {
    const factor = Math.pow(10, precision);
    switch (this._roundingMethod) {
      case RoundingMethod.Floor: return Math.floor(amount * factor) / factor;
      case RoundingMethod.Ceil: return Math.ceil(amount * factor) / factor;
      case RoundingMethod.Truncate: return Math.trunc(amount * factor) / factor;
      default: return Math.round(amount * factor) / factor;
    }
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): TaxCodeState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      taxTypeId: this._taxTypeId, taxRateType: this._taxRateType,
      application: this._application, roundingMethod: this._roundingMethod,
      precision: this._precision, description: this._description,
      isActive: this._isActive, isRecoverable: this._isRecoverable,
      isRefundable: this._isRefundable, isDeductible: this._isDeductible,
      glTaxAccountId: this._glTaxAccountId,
      glRecoverableAccountId: this._glRecoverableAccountId,
      glExpenseAccountId: this._glExpenseAccountId,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      rates: this._rates.map(r => r.toState()),
      createdAt: this._createdAt, updatedAt: this._updatedAt, version: this._version,
    };
  }
}
