import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { AllocationRuleId } from "./cst-ids.js";
import { CstAllocationMethod, CstAllocationBasis } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface AllocationRuleState {
  id: string;
  code: string;
  name: string;
  poolId: string | null;
  sourceCostCenterId: string | null;
  targetCostCenterId: string | null;
  allocationMethod: string;
  allocationBasis: string;
  basisValue: number;
  percentage: number | null;
  fixedAmount: number | null;
  driverId: string | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  isActive: boolean;
  priority: number;
  fiscalYearId: string | null;
  periodId: string | null;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class AllocationRule extends AggregateRoot<AllocationRuleId> {
  private constructor(
    private _id: AllocationRuleId,
    private _code: string,
    private _name: string,
    private _poolId: string | null,
    private _sourceCostCenterId: string | null,
    private _targetCostCenterId: string | null,
    private _allocationMethod: CstAllocationMethod,
    private _allocationBasis: CstAllocationBasis,
    private _basisValue: number,
    private _percentage: number | null,
    private _fixedAmount: number | null,
    private _driverId: string | null,
    private _effectiveFrom: Date,
    private _effectiveTo: Date | null,
    private _isActive: boolean,
    private _priority: number,
    private _fiscalYearId: string | null,
    private _periodId: string | null,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; poolId?: string | null;
    sourceCostCenterId?: string | null; targetCostCenterId?: string | null;
    allocationMethod: CstAllocationMethod; allocationBasis: CstAllocationBasis;
    basisValue?: number; percentage?: number | null; fixedAmount?: number | null;
    driverId?: string | null; effectiveFrom?: Date; effectiveTo?: Date | null;
    priority?: number; fiscalYearId?: string | null; periodId?: string | null;
    description?: string | null;
  }): AllocationRule {
    const ar = new AllocationRule(
      AllocationRuleId.new(), p.code, p.name, p.poolId ?? null,
      p.sourceCostCenterId ?? null, p.targetCostCenterId ?? null,
      p.allocationMethod, p.allocationBasis, p.basisValue ?? 0,
      p.percentage ?? null, p.fixedAmount ?? null, p.driverId ?? null,
      p.effectiveFrom ?? new Date(), p.effectiveTo ?? null,
      true, p.priority ?? 0, p.fiscalYearId ?? null, p.periodId ?? null,
      p.description ?? null, 1, new Date(), new Date(), null,
    );
    ar.addEvent(CostingEvents.AllocationRuleCreated(ar._id.value, { code: p.code, method: p.allocationMethod }));
    return ar;
  }

  static load(s: AllocationRuleState): AllocationRule {
    return new AllocationRule(
      new AllocationRuleId(s.id), s.code, s.name, s.poolId,
      s.sourceCostCenterId, s.targetCostCenterId,
      s.allocationMethod as CstAllocationMethod,
      s.allocationBasis as CstAllocationBasis,
      s.basisValue, s.percentage, s.fixedAmount, s.driverId,
      s.effectiveFrom, s.effectiveTo, s.isActive, s.priority,
      s.fiscalYearId, s.periodId, s.description,
      s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get allocationMethod() { return this._allocationMethod; }
  get allocationBasis() { return this._allocationBasis; }
  get basisValue() { return this._basisValue; }
  get percentage() { return this._percentage; }
  get fixedAmount() { return this._fixedAmount; }
  get version() { return this._version; }

  calculateAllocation(sourceAmount: number): number {
    switch (this._allocationMethod) {
      case CstAllocationMethod.Direct:
      case CstAllocationMethod.DriverBased:
        if (this._basisValue <= 0) return 0;
        return (sourceAmount / this._basisValue);
      case CstAllocationMethod.Percentage:
        return sourceAmount * ((this._percentage ?? 0) / 100);
      case CstAllocationMethod.Fixed:
        return this._fixedAmount ?? 0;
      default:
        return sourceAmount * ((this._percentage ?? 0) / 100);
    }
  }

  toState(): AllocationRuleState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      poolId: this._poolId, sourceCostCenterId: this._sourceCostCenterId,
      targetCostCenterId: this._targetCostCenterId,
      allocationMethod: this._allocationMethod,
      allocationBasis: this._allocationBasis, basisValue: this._basisValue,
      percentage: this._percentage, fixedAmount: this._fixedAmount,
      driverId: this._driverId, effectiveFrom: this._effectiveFrom,
      effectiveTo: this._effectiveTo, isActive: this._isActive,
      priority: this._priority, fiscalYearId: this._fiscalYearId,
      periodId: this._periodId, description: this._description,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
