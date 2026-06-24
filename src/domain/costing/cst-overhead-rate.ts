import { Entity } from "../../shared/entity.js";
import { OverheadRateId } from "./cst-ids.js";
import { CstCostPoolType, CstCostElementType, CstAllocationBasis } from "./cst-enums.js";

export interface OverheadRateState {
  id: string;
  code: string;
  name: string;
  costPoolType: string;
  costElement: string;
  allocationBasis: string;
  rate: number;
  rateType: string;
  workCenterId: string | null;
  costCenterId: string | null;
  departmentId: string | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  isActive: boolean;
  fiscalYearId: string | null;
  costVersionId: string | null;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class OverheadRate extends Entity<OverheadRateId> {
  private constructor(
    private _id: OverheadRateId,
    private _code: string,
    private _name: string,
    private _costPoolType: CstCostPoolType,
    private _costElement: CstCostElementType,
    private _allocationBasis: CstAllocationBasis,
    private _rate: number,
    private _rateType: string,
    private _workCenterId: string | null,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _effectiveFrom: Date,
    private _effectiveTo: Date | null,
    private _isActive: boolean,
    private _fiscalYearId: string | null,
    private _costVersionId: string | null,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; costPoolType: CstCostPoolType;
    costElement?: CstCostElementType; allocationBasis: CstAllocationBasis;
    rate: number; rateType?: string;
    workCenterId?: string | null; costCenterId?: string | null;
    departmentId?: string | null; effectiveFrom?: Date;
    effectiveTo?: Date | null; fiscalYearId?: string | null;
    costVersionId?: string | null; description?: string | null;
  }): OverheadRate {
    return new OverheadRate(
      OverheadRateId.new(), p.code, p.name, p.costPoolType,
      p.costElement ?? CstCostElementType.Overhead, p.allocationBasis,
      p.rate, p.rateType ?? "percentage",
      p.workCenterId ?? null, p.costCenterId ?? null,
      p.departmentId ?? null, p.effectiveFrom ?? new Date(),
      p.effectiveTo ?? null, true, p.fiscalYearId ?? null,
      p.costVersionId ?? null, p.description ?? null,
      1, new Date(), new Date(), null,
    );
  }

  static load(s: OverheadRateState): OverheadRate {
    return new OverheadRate(
      new OverheadRateId(s.id), s.code, s.name,
      s.costPoolType as CstCostPoolType,
      s.costElement as CstCostElementType,
      s.allocationBasis as CstAllocationBasis,
      s.rate, s.rateType, s.workCenterId, s.costCenterId,
      s.departmentId, s.effectiveFrom, s.effectiveTo, s.isActive,
      s.fiscalYearId, s.costVersionId, s.description,
      s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
  }

  get id() { return this._id; }
  get rate() { return this._rate; }
  get rateType() { return this._rateType; }
  get code() { return this._code; }

  toState(): OverheadRateState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      costPoolType: this._costPoolType, costElement: this._costElement,
      allocationBasis: this._allocationBasis, rate: this._rate,
      rateType: this._rateType, workCenterId: this._workCenterId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      isActive: this._isActive, fiscalYearId: this._fiscalYearId,
      costVersionId: this._costVersionId, description: this._description,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
