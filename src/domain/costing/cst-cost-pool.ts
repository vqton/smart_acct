import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CostPoolId } from "./cst-ids.js";
import { CstCostPoolType } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface CostPoolState {
  id: string;
  code: string;
  name: string;
  poolType: string;
  costCenterId: string | null;
  departmentId: string | null;
  totalAmount: number;
  allocatedAmount: number;
  unallocatedAmount: number;
  fiscalYearId: string | null;
  periodId: string | null;
  isActive: boolean;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CostPool extends AggregateRoot<CostPoolId> {
  private constructor(
    private _id: CostPoolId,
    private _code: string,
    private _name: string,
    private _poolType: CstCostPoolType,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _totalAmount: number,
    private _allocatedAmount: number,
    private _unallocatedAmount: number,
    private _fiscalYearId: string | null,
    private _periodId: string | null,
    private _isActive: boolean,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; poolType: CstCostPoolType;
    costCenterId?: string | null; departmentId?: string | null;
    totalAmount?: number; fiscalYearId?: string | null;
    periodId?: string | null; description?: string | null;
  }): CostPool {
    const cp = new CostPool(
      CostPoolId.new(), p.code, p.name, p.poolType,
      p.costCenterId ?? null, p.departmentId ?? null,
      p.totalAmount ?? 0, 0, p.totalAmount ?? 0,
      p.fiscalYearId ?? null, p.periodId ?? null, true,
      p.description ?? null, 1, new Date(), new Date(), null,
    );
    cp.addEvent(CostingEvents.CostPoolCreated(cp._id.value, { code: p.code, poolType: p.poolType }));
    return cp;
  }

  static load(s: CostPoolState): CostPool {
    return new CostPool(
      new CostPoolId(s.id), s.code, s.name, s.poolType as CstCostPoolType,
      s.costCenterId, s.departmentId, s.totalAmount, s.allocatedAmount,
      s.unallocatedAmount, s.fiscalYearId, s.periodId, s.isActive,
      s.description, s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get poolType() { return this._poolType; }
  get totalAmount() { return this._totalAmount; }
  get allocatedAmount() { return this._allocatedAmount; }
  get unallocatedAmount() { return this._unallocatedAmount; }
  get version() { return this._version; }

  allocate(amount: number): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Allocation amount must be positive");
    if (amount > this._unallocatedAmount) {
      throw new DomainError("BusinessRule", "Allocation exceeds unallocated amount");
    }
    this._allocatedAmount += amount;
    this._unallocatedAmount -= amount;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.CostPoolAllocated(this._id.value, {
      code: this._code, amount, remaining: this._unallocatedAmount,
    }));
  }

  addToPool(amount: number): void {
    if (amount < 0) throw new DomainError("BusinessRule", "Cannot add negative amount to pool");
    this._totalAmount += amount;
    this._unallocatedAmount += amount;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): CostPoolState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      poolType: this._poolType, costCenterId: this._costCenterId,
      departmentId: this._departmentId, totalAmount: this._totalAmount,
      allocatedAmount: this._allocatedAmount,
      unallocatedAmount: this._unallocatedAmount,
      fiscalYearId: this._fiscalYearId, periodId: this._periodId,
      isActive: this._isActive, description: this._description,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
