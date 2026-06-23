import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { AccountMappingId } from "./coa-ids.js";
import { AccountMappingStandard, AccountMappingType } from "./coa-enums.js";

export interface AccountMappingState {
  id: string;
  accountId: string;
  mappingStandard: AccountMappingStandard;
  mappingType: AccountMappingType;
  targetCode: string;
  targetName: string | null;
  mappingRule: string | null;
  percentage: number | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  isActive: boolean;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class AccountMappingCreated implements DomainEvent {
  readonly eventName = "AccountMappingCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AccountMapping extends AggregateRoot<AccountMappingId> {
  private _id: AccountMappingId;
  private _accountId: string;
  private _mappingStandard: AccountMappingStandard;
  private _mappingType: AccountMappingType;
  private _targetCode: string;
  private _targetName: string | null;
  private _mappingRule: string | null;
  private _percentage: number | null;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _isActive: boolean;
  private _description: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(
    id: AccountMappingId,
    accountId: string,
    mappingStandard: AccountMappingStandard,
    mappingType: AccountMappingType,
    targetCode: string,
    effectiveFrom: Date,
    targetName: string | null = null,
    mappingRule: string | null = null,
    percentage: number | null = null,
    effectiveTo: Date | null = null,
    description: string | null = null,
  ) {
    super();
    this._id = id;
    this._accountId = accountId;
    this._mappingStandard = mappingStandard;
    this._mappingType = mappingType;
    this._targetCode = targetCode;
    this._targetName = targetName;
    this._mappingRule = mappingRule;
    this._percentage = percentage;
    this._effectiveFrom = effectiveFrom;
    this._effectiveTo = effectiveTo;
    this._isActive = true;
    this._description = description;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(params: {
    accountId: string;
    mappingStandard: AccountMappingStandard;
    mappingType: AccountMappingType;
    targetCode: string;
    targetName?: string;
    mappingRule?: string;
    percentage?: number;
    effectiveFrom: Date;
    effectiveTo?: Date;
    description?: string;
  }): AccountMapping {
    const m = new AccountMapping(
      AccountMappingId.new(),
      params.accountId,
      params.mappingStandard,
      params.mappingType,
      params.targetCode,
      params.effectiveFrom,
      params.targetName ?? null,
      params.mappingRule ?? null,
      params.percentage ?? null,
      params.effectiveTo ?? null,
      params.description ?? null,
    );
    m.addEvent(new AccountMappingCreated(m._id.value, new Date(), {
      accountId: params.accountId,
      standard: params.mappingStandard,
      targetCode: params.targetCode,
    }));
    return m;
  }

  static load(state: AccountMappingState): AccountMapping {
    const m = new AccountMapping(
      new AccountMappingId(state.id),
      state.accountId,
      state.mappingStandard,
      state.mappingType,
      state.targetCode,
      state.effectiveFrom,
      state.targetName,
      state.mappingRule,
      state.percentage,
      state.effectiveTo,
      state.description,
    );
    m._isActive = state.isActive;
    m._version = state.version;
    m._createdAt = state.createdAt;
    m._updatedAt = state.updatedAt;
    return m;
  }

  get id(): AccountMappingId { return this._id; }
  get accountId(): string { return this._accountId; }
  get mappingStandard(): AccountMappingStandard { return this._mappingStandard; }
  get mappingType(): AccountMappingType { return this._mappingType; }
  get targetCode(): string { return this._targetCode; }
  get targetName(): string | null { return this._targetName; }
  get mappingRule(): string | null { return this._mappingRule; }
  get percentage(): number | null { return this._percentage; }
  get effectiveFrom(): Date { return this._effectiveFrom; }
  get effectiveTo(): Date | null { return this._effectiveTo; }
  get isActive(): boolean { return this._isActive; }
  get description(): string | null { return this._description; }
  get version(): number { return this._version; }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): AccountMappingState {
    return {
      id: this._id.value,
      accountId: this._accountId,
      mappingStandard: this._mappingStandard,
      mappingType: this._mappingType,
      targetCode: this._targetCode,
      targetName: this._targetName,
      mappingRule: this._mappingRule,
      percentage: this._percentage,
      effectiveFrom: this._effectiveFrom,
      effectiveTo: this._effectiveTo,
      isActive: this._isActive,
      description: this._description,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
