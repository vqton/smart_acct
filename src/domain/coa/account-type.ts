import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { AccountTypeId } from "./coa-ids.js";
import { AccountTypeCategory, AccountSubType } from "./coa-enums.js";
import { AccountNature } from "../gl/account-category.js";

export interface AccountTypeState {
  id: string;
  classId: string;
  code: string;
  name: string;
  nameEn: string | null;
  category: AccountTypeCategory;
  subType: AccountSubType | null;
  nature: AccountNature;
  description: string | null;
  parentTypeId: string | null;
  isActive: boolean;
  displayOrder: number;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class AccountTypeCreated implements DomainEvent {
  readonly eventName = "AccountTypeCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AccountType extends AggregateRoot<AccountTypeId> {
  private _id: AccountTypeId;
  private _classId: string;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _category: AccountTypeCategory;
  private _subType: AccountSubType | null;
  private _nature: AccountNature;
  private _description: string | null;
  private _parentTypeId: string | null;
  private _isActive: boolean;
  private _displayOrder: number;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(
    id: AccountTypeId,
    classId: string,
    code: string,
    name: string,
    category: AccountTypeCategory,
    nature: AccountNature,
    subType: AccountSubType | null = null,
    description: string | null = null,
    parentTypeId: string | null = null,
  ) {
    super();
    this._id = id;
    this._classId = classId;
    this._code = code;
    this._name = name;
    this._nameEn = null;
    this._category = category;
    this._subType = subType;
    this._nature = nature;
    this._description = description;
    this._parentTypeId = parentTypeId;
    this._isActive = true;
    this._displayOrder = 0;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(params: {
    classId: string;
    code: string;
    name: string;
    category: AccountTypeCategory;
    nature: AccountNature;
    subType?: AccountSubType;
    description?: string;
    parentTypeId?: string;
  }): AccountType {
    const t = new AccountType(
      AccountTypeId.new(),
      params.classId,
      params.code,
      params.name,
      params.category,
      params.nature,
      params.subType ?? null,
      params.description ?? null,
      params.parentTypeId ?? null,
    );
    t.addEvent(new AccountTypeCreated(t._id.value, new Date(), { code: params.code, name: params.name }));
    return t;
  }

  static load(state: AccountTypeState): AccountType {
    const t = new AccountType(
      new AccountTypeId(state.id),
      state.classId,
      state.code,
      state.name,
      state.category,
      state.nature,
      state.subType,
      state.description,
      state.parentTypeId,
    );
    t._nameEn = state.nameEn;
    t._isActive = state.isActive;
    t._displayOrder = state.displayOrder;
    t._version = state.version;
    t._createdAt = state.createdAt;
    t._updatedAt = state.updatedAt;
    return t;
  }

  get id(): AccountTypeId { return this._id; }
  get classId(): string { return this._classId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get nameEn(): string | null { return this._nameEn; }
  get category(): AccountTypeCategory { return this._category; }
  get subType(): AccountSubType | null { return this._subType; }
  get nature(): AccountNature { return this._nature; }
  get description(): string | null { return this._description; }
  get parentTypeId(): string | null { return this._parentTypeId; }
  get isActive(): boolean { return this._isActive; }
  get displayOrder(): number { return this._displayOrder; }
  get version(): number { return this._version; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }

  toState(): AccountTypeState {
    return {
      id: this._id.value,
      classId: this._classId,
      code: this._code,
      name: this._name,
      nameEn: this._nameEn,
      category: this._category,
      subType: this._subType,
      nature: this._nature,
      description: this._description,
      parentTypeId: this._parentTypeId,
      isActive: this._isActive,
      displayOrder: this._displayOrder,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
