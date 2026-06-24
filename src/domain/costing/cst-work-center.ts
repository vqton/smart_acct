import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { WorkCenterId } from "./cst-ids.js";
import { CostingEvents } from "./cst-events.js";

export interface WorkCenterState {
  id: string;
  code: string;
  name: string;
  workCenterType: string;
  costCenterId: string | null;
  departmentId: string | null;
  machineCount: number;
  laborCount: number;
  hourlyRate: number;
  machineRate: number;
  overheadRate: number;
  capacity: number;
  capacityUom: string;
  efficiency: number;
  isActive: boolean;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class WorkCenter extends AggregateRoot<WorkCenterId> {
  private constructor(
    private _id: WorkCenterId,
    private _code: string,
    private _name: string,
    private _workCenterType: string,
    private _costCenterId: string | null,
    private _departmentId: string | null,
    private _machineCount: number,
    private _laborCount: number,
    private _hourlyRate: number,
    private _machineRate: number,
    private _overheadRate: number,
    private _capacity: number,
    private _capacityUom: string,
    private _efficiency: number,
    private _isActive: boolean,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; workCenterType?: string;
    costCenterId?: string | null; departmentId?: string | null;
    machineCount?: number; laborCount?: number;
    hourlyRate?: number; machineRate?: number; overheadRate?: number;
    capacity?: number; capacityUom?: string; efficiency?: number;
    description?: string | null;
  }): WorkCenter {
    const wc = new WorkCenter(
      WorkCenterId.new(), p.code, p.name, p.workCenterType ?? "production",
      p.costCenterId ?? null, p.departmentId ?? null,
      p.machineCount ?? 1, p.laborCount ?? 1,
      p.hourlyRate ?? 0, p.machineRate ?? 0, p.overheadRate ?? 0,
      p.capacity ?? 0, p.capacityUom ?? "hours", p.efficiency ?? 1,
      true, p.description ?? null, 1, new Date(), new Date(), null,
    );
    wc.addEvent(CostingEvents.WorkCenterCreated(wc._id.value, { code: p.code, name: p.name }));
    return wc;
  }

  static load(s: WorkCenterState): WorkCenter {
    return new WorkCenter(
      new WorkCenterId(s.id), s.code, s.name, s.workCenterType,
      s.costCenterId, s.departmentId, s.machineCount, s.laborCount,
      s.hourlyRate, s.machineRate, s.overheadRate, s.capacity, s.capacityUom,
      s.efficiency, s.isActive, s.description, s.version,
      s.createdAt, s.updatedAt, s.deletedAt,
    );
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get hourlyRate() { return this._hourlyRate; }
  get machineRate() { return this._machineRate; }
  get overheadRate() { return this._overheadRate; }
  get version() { return this._version; }

  updateRates(p: { hourlyRate?: number; machineRate?: number; overheadRate?: number }): void {
    if (p.hourlyRate !== undefined) this._hourlyRate = p.hourlyRate;
    if (p.machineRate !== undefined) this._machineRate = p.machineRate;
    if (p.overheadRate !== undefined) this._overheadRate = p.overheadRate;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.WorkCenterRateUpdated(this._id.value, { code: this._code }));
  }

  toState(): WorkCenterState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      workCenterType: this._workCenterType, costCenterId: this._costCenterId,
      departmentId: this._departmentId, machineCount: this._machineCount,
      laborCount: this._laborCount, hourlyRate: this._hourlyRate,
      machineRate: this._machineRate, overheadRate: this._overheadRate,
      capacity: this._capacity, capacityUom: this._capacityUom,
      efficiency: this._efficiency, isActive: this._isActive,
      description: this._description, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
