import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxExemptionId extends Identifier {
  static new(): TaxExemptionId { return new TaxExemptionId(IdGenerator.uuid()); }
}

export class TaxIncentiveId extends Identifier {
  static new(): TaxIncentiveId { return new TaxIncentiveId(IdGenerator.uuid()); }
}

export enum IncentiveType {
  Exemption = "exemption",
  Reduction = "reduction",
  Holiday = "holiday",
  Credit = "credit",
  Deduction = "deduction",
  PreferentialRate = "preferential_rate",
  AcceleratedDepreciation = "accelerated_depreciation",
  CarryForward = "carry_forward",
  Rebate = "rebate",
}

export enum IncentiveApplicationLevel {
  TaxType = "tax_type",
  TaxCode = "tax_code",
  Transaction = "transaction",
  Product = "product",
  Region = "region",
  Industry = "industry",
  Taxpayer = "taxpayer",
}

export interface TaxExemptionState {
  id: string;
  code: string;
  name: string;
  incentiveType: IncentiveType;
  taxTypeId: string;
  taxCodeId: string | null;
  taxpayerId: string | null;
  regionId: string | null;
  certificateNumber: string | null;
  reductionPercent: number | null;
  reductionAmount: number | null;
  maxAmount: number | null;
  applicationLevel: IncentiveApplicationLevel;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  legalReference: string | null;
  conditions: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxExemption extends AggregateRoot<TaxExemptionId> {
  private _id: TaxExemptionId;
  private _code: string;
  private _name: string;
  private _incentiveType: IncentiveType;
  private _taxTypeId: string;
  private _taxCodeId: string | null;
  private _taxpayerId: string | null;
  private _regionId: string | null;
  private _certificateNumber: string | null;
  private _reductionPercent: number | null;
  private _reductionAmount: number | null;
  private _maxAmount: number | null;
  private _applicationLevel: IncentiveApplicationLevel;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _legalReference: string | null;
  private _conditions: string[];
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(code: string, name: string, incentiveType: IncentiveType, taxTypeId: string, applicationLevel: IncentiveApplicationLevel, effectiveFrom: Date) {
    super();
    this._id = TaxExemptionId.new();
    this._code = code; this._name = name; this._incentiveType = incentiveType;
    this._taxTypeId = taxTypeId; this._applicationLevel = applicationLevel;
    this._effectiveFrom = effectiveFrom;
    this._taxCodeId = null; this._taxpayerId = null; this._regionId = null;
    this._certificateNumber = null; this._reductionPercent = null; this._reductionAmount = null;
    this._maxAmount = null; this._effectiveTo = null; this._legalReference = null;
    this._conditions = []; this._isActive = true;
    this._createdAt = new Date(); this._updatedAt = new Date(); this._version = 1;
  }

  static load(s: TaxExemptionState): TaxExemption {
    const e = new TaxExemption(s.code, s.name, s.incentiveType, s.taxTypeId, s.applicationLevel, s.effectiveFrom);
    e._id = new TaxExemptionId(s.id);
    e._taxCodeId = s.taxCodeId; e._taxpayerId = s.taxpayerId; e._regionId = s.regionId;
    e._certificateNumber = s.certificateNumber; e._reductionPercent = s.reductionPercent;
    e._reductionAmount = s.reductionAmount; e._maxAmount = s.maxAmount;
    e._effectiveTo = s.effectiveTo; e._legalReference = s.legalReference;
    e._conditions = s.conditions; e._isActive = s.isActive;
    e._createdAt = s.createdAt; e._updatedAt = s.updatedAt; e._version = s.version;
    return e;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get incentiveType() { return this._incentiveType; }
  get taxTypeId() { return this._taxTypeId; }
  get reductionPercent() { return this._reductionPercent; }
  get reductionAmount() { return this._reductionAmount; }
  get maxAmount() { return this._maxAmount; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  apply(taxAmount: number, date: Date): number {
    if (!this._isActive) return taxAmount;
    if (date < this._effectiveFrom) return taxAmount;
    if (this._effectiveTo && date > this._effectiveTo) return taxAmount;

    if (this._incentiveType === IncentiveType.Exemption) return 0;
    if (this._incentiveType === IncentiveType.Holiday) return 0;

    let result = taxAmount;
    if (this._reductionPercent) result -= taxAmount * (this._reductionPercent / 100);
    if (this._reductionAmount) result -= this._reductionAmount;
    if (this._maxAmount && result < 0) result = 0;

    return Math.max(result, 0);
  }

  toState(): TaxExemptionState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      incentiveType: this._incentiveType, taxTypeId: this._taxTypeId,
      taxCodeId: this._taxCodeId, taxpayerId: this._taxpayerId,
      regionId: this._regionId, certificateNumber: this._certificateNumber,
      reductionPercent: this._reductionPercent, reductionAmount: this._reductionAmount,
      maxAmount: this._maxAmount, applicationLevel: this._applicationLevel,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      legalReference: this._legalReference, conditions: this._conditions,
      isActive: this._isActive, createdAt: this._createdAt, updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
