import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { InsuranceRateId } from "./prl-ids.js";
import { InsuranceType } from "./prl-enums.js";
import { InsuranceRateCreated } from "./prl-events.js";

export interface InsuranceRateState {
  id: string;
  insuranceType: string;
  name: string;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  eeRate: number;
  erRate: number;
  ceilingAmount: bigint | null;
  ceilingType: string | null;
  currencyCode: string;
  isActive: boolean;
  regulationRef: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class InsuranceRate extends AggregateRoot<InsuranceRateId> {
  private _id: InsuranceRateId;
  private _insuranceType: string;
  private _name: string;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _eeRate: number;
  private _erRate: number;
  private _ceilingAmount: bigint | null;
  private _ceilingType: string | null;
  private _currencyCode: string;
  private _isActive: boolean;
  private _regulationRef: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: InsuranceRateId, insuranceType: string, name: string, effectiveFrom: Date, eeRate: number, erRate: number) {
    super();
    this._id = id;
    this._insuranceType = insuranceType;
    this._name = name;
    this._effectiveFrom = effectiveFrom;
    this._eeRate = eeRate;
    this._erRate = erRate;
    this._effectiveTo = null;
    this._ceilingAmount = null;
    this._ceilingType = null;
    this._currencyCode = "VND";
    this._isActive = true;
    this._regulationRef = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    insuranceType: string; name: string; effectiveFrom: Date;
    eeRate: number; erRate: number; effectiveTo?: Date;
    ceilingAmount?: bigint; ceilingType?: string;
    currencyCode?: string; regulationRef?: string;
  }): InsuranceRate {
    if (!params.insuranceType) throw new DomainError("Validation", "Insurance type is required");
    if (!params.name) throw new DomainError("Validation", "Name is required");
    if (params.eeRate < 0 || params.erRate < 0) throw new DomainError("Validation", "Rates cannot be negative");

    const ir = new InsuranceRate(InsuranceRateId.new(), params.insuranceType, params.name, params.effectiveFrom, params.eeRate, params.erRate);
    ir._effectiveTo = params.effectiveTo ?? null;
    ir._ceilingAmount = params.ceilingAmount ?? null;
    ir._ceilingType = params.ceilingType ?? null;
    ir._currencyCode = params.currencyCode ?? "VND";
    ir._regulationRef = params.regulationRef ?? null;
    ir.addEvent(new InsuranceRateCreated(ir._id.value, new Date(), { insuranceType: ir._insuranceType, name: ir._name }));
    return ir;
  }

  static load(state: InsuranceRateState): InsuranceRate {
    const ir = new InsuranceRate(new InsuranceRateId(state.id), state.insuranceType, state.name, state.effectiveFrom, state.eeRate, state.erRate);
    ir._effectiveTo = state.effectiveTo;
    ir._ceilingAmount = state.ceilingAmount;
    ir._ceilingType = state.ceilingType;
    ir._currencyCode = state.currencyCode;
    ir._isActive = state.isActive;
    ir._regulationRef = state.regulationRef;
    ir._version = state.version;
    ir._createdAt = state.createdAt;
    ir._updatedAt = state.updatedAt;
    ir._deletedAt = state.deletedAt;
    return ir;
  }

  toState(): InsuranceRateState {
    return {
      id: this._id.value, insuranceType: this._insuranceType, name: this._name,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      eeRate: this._eeRate, erRate: this._erRate,
      ceilingAmount: this._ceilingAmount, ceilingType: this._ceilingType,
      currencyCode: this._currencyCode, isActive: this._isActive,
      regulationRef: this._regulationRef, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }

  calculateEmployeeContribution(grossSalary: bigint): bigint {
    let base = grossSalary;
    if (this._ceilingAmount && base > this._ceilingAmount) {
      base = this._ceilingAmount;
    }
    return BigInt(Math.round(Number(base) * this._eeRate / 1000));
  }

  calculateEmployerContribution(grossSalary: bigint): bigint {
    let base = grossSalary;
    if (this._ceilingAmount && base > this._ceilingAmount) {
      base = this._ceilingAmount;
    }
    return BigInt(Math.round(Number(base) * this._erRate / 1000));
  }

  get id(): InsuranceRateId { return this._id; }
  get insuranceType(): string { return this._insuranceType; }
  get eeRate(): number { return this._eeRate; }
  get erRate(): number { return this._erRate; }
  get ceilingAmount(): bigint | null { return this._ceilingAmount; }
  get isActive(): boolean { return this._isActive; }
  get regulationRef(): string | null { return this._regulationRef; }
  get version(): number { return this._version; }
}
