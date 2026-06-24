import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PayrollGroupId } from "./prl-ids.js";
import { PayFrequency } from "./prl-enums.js";
import { PayrollGroupCreated, PayrollGroupUpdated } from "./prl-events.js";

export interface PayrollGroupState {
  id: string;
  code: string;
  name: string;
  description: string | null;
  companyId: string;
  branchId: string | null;
  payFrequency: string;
  currencyCode: string;
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class PayrollGroup extends AggregateRoot<PayrollGroupId> {
  private _id: PayrollGroupId;
  private _code: string;
  private _name: string;
  private _description: string | null;
  private _companyId: string;
  private _branchId: string | null;
  private _payFrequency: string;
  private _currencyCode: string;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(
    id: PayrollGroupId,
    code: string,
    name: string,
    companyId: string,
    payFrequency: string,
    currencyCode: string,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._companyId = companyId;
    this._payFrequency = payFrequency;
    this._currencyCode = currencyCode;
    this._description = null;
    this._branchId = null;
    this._isActive = true;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    code: string;
    name: string;
    description?: string;
    companyId: string;
    branchId?: string;
    payFrequency?: string;
    currencyCode?: string;
  }): PayrollGroup {
    if (!params.code || params.code.trim().length === 0) {
      throw new DomainError("Validation", "Payroll group code is required");
    }
    if (!params.name || params.name.trim().length === 0) {
      throw new DomainError("Validation", "Payroll group name is required");
    }
    const group = new PayrollGroup(
      PayrollGroupId.new(),
      params.code.trim(),
      params.name.trim(),
      params.companyId,
      params.payFrequency ?? PayFrequency.MONTHLY,
      params.currencyCode ?? "VND",
    );
    group._description = params.description ?? null;
    group._branchId = params.branchId ?? null;
    group.addEvent(new PayrollGroupCreated(group._id.value, new Date(), {
      code: group._code, name: group._name, companyId: group._companyId,
    }));
    return group;
  }

  static load(state: PayrollGroupState): PayrollGroup {
    const g = new PayrollGroup(
      new PayrollGroupId(state.id),
      state.code, state.name, state.companyId,
      state.payFrequency, state.currencyCode,
    );
    g._description = state.description;
    g._branchId = state.branchId;
    g._isActive = state.isActive;
    g._version = state.version;
    g._createdAt = state.createdAt;
    g._updatedAt = state.updatedAt;
    g._deletedAt = state.deletedAt;
    return g;
  }

  toState(): PayrollGroupState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      description: this._description,
      companyId: this._companyId,
      branchId: this._branchId,
      payFrequency: this._payFrequency,
      currencyCode: this._currencyCode,
      isActive: this._isActive,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }

  update(params: { name?: string; description?: string; payFrequency?: string; currencyCode?: string }): void {
    if (params.name !== undefined) this._name = params.name;
    if (params.description !== undefined) this._description = params.description;
    if (params.payFrequency !== undefined) this._payFrequency = params.payFrequency;
    if (params.currencyCode !== undefined) this._currencyCode = params.currencyCode;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollGroupUpdated(this._id.value, new Date(), { id: this._id.value }));
  }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Payroll group already inactive");
    this._isActive = false;
    this._version++;
    this._updatedAt = new Date();
  }

  activate(): void {
    if (this._isActive) throw new DomainError("BusinessRule", "Payroll group already active");
    this._isActive = true;
    this._version++;
    this._updatedAt = new Date();
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  get id(): PayrollGroupId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get companyId(): string { return this._companyId; }
  get branchId(): string | null { return this._branchId; }
  get payFrequency(): string { return this._payFrequency; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }
}
