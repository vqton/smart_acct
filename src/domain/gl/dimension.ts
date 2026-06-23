import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class CostCenterId extends Identifier {
  static new(): CostCenterId {
    return new CostCenterId(IdGenerator.uuid());
  }
}

export class DepartmentId extends Identifier {
  static new(): DepartmentId {
    return new DepartmentId(IdGenerator.uuid());
  }
}

export class ProjectId extends Identifier {
  static new(): ProjectId {
    return new ProjectId(IdGenerator.uuid());
  }
}

export class BranchId extends Identifier {
  static new(): BranchId {
    return new BranchId(IdGenerator.uuid());
  }
}

export enum DimensionStatus {
  Active = "active",
  Inactive = "inactive",
}

export interface CostCenterState {
  id: string;
  code: string;
  name: string;
  parentId: string | null;
  managerId: string | null;
  budgetHolderId: string | null;
  status: DimensionStatus;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export interface DepartmentState {
  id: string;
  code: string;
  name: string;
  parentId: string | null;
  headId: string | null;
  status: DimensionStatus;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export class CostCenter extends AggregateRoot<CostCenterId> {
  private _id: CostCenterId;
  private _code: string;
  private _name: string;
  private _parentId: string | null;
  private _managerId: string | null;
  private _budgetHolderId: string | null;
  private _status: DimensionStatus;
  private _description: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;
  private _deletedAt: Date | null;

  constructor(
    id: CostCenterId,
    code: string,
    name: string,
    parentId: string | null = null,
    managerId: string | null = null,
    budgetHolderId: string | null = null,
    description: string | null = null,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._parentId = parentId;
    this._managerId = managerId;
    this._budgetHolderId = budgetHolderId;
    this._status = DimensionStatus.Active;
    this._description = description;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
    this._deletedAt = null;
  }

  static create(params: {
    code: string;
    name: string;
    parentId?: string;
    managerId?: string;
    budgetHolderId?: string;
    description?: string;
  }): CostCenter {
    return new CostCenter(
      CostCenterId.new(),
      params.code,
      params.name,
      params.parentId ?? null,
      params.managerId ?? null,
      params.budgetHolderId ?? null,
      params.description ?? null,
    );
  }

  static load(state: CostCenterState): CostCenter {
    const cc = new CostCenter(
      new CostCenterId(state.id),
      state.code,
      state.name,
      state.parentId,
      state.managerId,
      state.budgetHolderId,
      state.description,
    );
    cc._status = state.status;
    cc._createdAt = state.createdAt;
    cc._updatedAt = state.updatedAt;
    cc._version = state.version;
    cc._deletedAt = state.deletedAt;
    return cc;
  }

  get id(): CostCenterId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get parentId(): string | null { return this._parentId; }
  get managerId(): string | null { return this._managerId; }
  get budgetHolderId(): string | null { return this._budgetHolderId; }
  get status(): DimensionStatus { return this._status; }
  get description(): string | null { return this._description; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  deactivate(): void {
    this._status = DimensionStatus.Inactive;
    this._updatedAt = new Date();
    this._version++;
  }

  activate(): void {
    this._status = DimensionStatus.Active;
    this._updatedAt = new Date();
    this._version++;
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._status = DimensionStatus.Inactive;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): CostCenterState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      parentId: this._parentId,
      managerId: this._managerId,
      budgetHolderId: this._budgetHolderId,
      status: this._status,
      description: this._description,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}

export class Department extends AggregateRoot<DepartmentId> {
  private _id: DepartmentId;
  private _code: string;
  private _name: string;
  private _parentId: string | null;
  private _headId: string | null;
  private _status: DimensionStatus;
  private _description: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;
  private _deletedAt: Date | null;

  constructor(
    id: DepartmentId,
    code: string,
    name: string,
    parentId: string | null = null,
    headId: string | null = null,
    description: string | null = null,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._parentId = parentId;
    this._headId = headId;
    this._status = DimensionStatus.Active;
    this._description = description;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
    this._deletedAt = null;
  }

  static create(params: {
    code: string;
    name: string;
    parentId?: string;
    headId?: string;
    description?: string;
  }): Department {
    return new Department(
      DepartmentId.new(),
      params.code,
      params.name,
      params.parentId ?? null,
      params.headId ?? null,
      params.description ?? null,
    );
  }

  static load(state: DepartmentState): Department {
    const d = new Department(
      new DepartmentId(state.id),
      state.code,
      state.name,
      state.parentId,
      state.headId,
      state.description,
    );
    d._status = state.status;
    d._createdAt = state.createdAt;
    d._updatedAt = state.updatedAt;
    d._version = state.version;
    d._deletedAt = state.deletedAt;
    return d;
  }

  get id(): DepartmentId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get parentId(): string | null { return this._parentId; }
  get headId(): string | null { return this._headId; }
  get status(): DimensionStatus { return this._status; }
  get description(): string | null { return this._description; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  deactivate(): void {
    this._status = DimensionStatus.Inactive;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): DepartmentState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      parentId: this._parentId,
      headId: this._headId,
      status: this._status,
      description: this._description,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}
