import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { AccountClassId } from "./coa-ids.js";
import { AccountClassType } from "./coa-enums.js";

export interface AccountClassState {
  id: string;
  code: string;
  name: string;
  nameEn: string | null;
  classType: AccountClassType;
  description: string | null;
  displayOrder: number;
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class AccountClass extends AggregateRoot<AccountClassId> {
  private _id: AccountClassId;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _classType: AccountClassType;
  private _description: string | null;
  private _displayOrder: number;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(
    id: AccountClassId,
    code: string,
    name: string,
    classType: AccountClassType,
    displayOrder: number = 0,
    description: string | null = null,
  ) {
    super();
    if (!/^\d{1}$/.test(code)) throw new DomainError("Validation", `Account class code must be single digit: ${code}`);
    this._id = id;
    this._code = code;
    this._name = name;
    this._nameEn = null;
    this._classType = classType;
    this._description = description;
    this._displayOrder = displayOrder;
    this._isActive = true;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(params: {
    code: string;
    name: string;
    classType: AccountClassType;
    displayOrder?: number;
    description?: string;
  }): AccountClass {
    return new AccountClass(
      AccountClassId.new(),
      params.code,
      params.name,
      params.classType,
      params.displayOrder ?? 0,
      params.description ?? null,
    );
  }

  static load(state: AccountClassState): AccountClass {
    const c = new AccountClass(
      new AccountClassId(state.id),
      state.code,
      state.name,
      state.classType,
      state.displayOrder,
      state.description,
    );
    c._nameEn = state.nameEn;
    c._isActive = state.isActive;
    c._version = state.version;
    c._createdAt = state.createdAt;
    c._updatedAt = state.updatedAt;
    return c;
  }

  get id(): AccountClassId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get nameEn(): string | null { return this._nameEn; }
  get classType(): AccountClassType { return this._classType; }
  get description(): string | null { return this._description; }
  get displayOrder(): number { return this._displayOrder; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }

  toState(): AccountClassState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      nameEn: this._nameEn,
      classType: this._classType,
      description: this._description,
      displayOrder: this._displayOrder,
      isActive: this._isActive,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
