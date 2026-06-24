import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { SalaryComponentId } from "./prl-ids.js";
import { ElementType, ElementCategory } from "./prl-enums.js";
import { SalaryComponentCreated } from "./prl-events.js";

export interface SalaryComponentState {
  id: string;
  code: string;
  name: string;
  nameEn: string | null;
  elementType: string;
  category: string;
  isActive: boolean;
  isTaxable: boolean;
  isInsurable: boolean;
  isPITable: boolean;
  priority: number;
  formula: string | null;
  defaultValue: bigint | null;
  currencyCode: string;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class SalaryComponent extends AggregateRoot<SalaryComponentId> {
  private _id: SalaryComponentId;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _elementType: string;
  private _category: string;
  private _isActive: boolean;
  private _isTaxable: boolean;
  private _isInsurable: boolean;
  private _isPITable: boolean;
  private _priority: number;
  private _formula: string | null;
  private _defaultValue: bigint | null;
  private _currencyCode: string;
  private _description: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: SalaryComponentId, code: string, name: string, elementType: string, category: string) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._elementType = elementType;
    this._category = category;
    this._nameEn = null;
    this._isActive = true;
    this._isTaxable = true;
    this._isInsurable = false;
    this._isPITable = true;
    this._priority = 0;
    this._formula = null;
    this._defaultValue = null;
    this._currencyCode = "VND";
    this._description = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    code: string; name: string; nameEn?: string;
    elementType: string; category: string;
    isTaxable?: boolean; isInsurable?: boolean; isPITable?: boolean;
    priority?: number; formula?: string; defaultValue?: bigint;
    currencyCode?: string; description?: string;
  }): SalaryComponent {
    if (!params.code) throw new DomainError("Validation", "Salary component code is required");
    if (!params.name) throw new DomainError("Validation", "Salary component name is required");
    if (!params.elementType) throw new DomainError("Validation", "Element type is required");
    if (!params.category) throw new DomainError("Validation", "Category is required");

    const sc = new SalaryComponent(SalaryComponentId.new(), params.code, params.name, params.elementType, params.category);
    sc._nameEn = params.nameEn ?? null;
    sc._isTaxable = params.isTaxable ?? true;
    sc._isInsurable = params.isInsurable ?? false;
    sc._isPITable = params.isPITable ?? true;
    sc._priority = params.priority ?? 0;
    sc._formula = params.formula ?? null;
    sc._defaultValue = params.defaultValue ?? null;
    sc._currencyCode = params.currencyCode ?? "VND";
    sc._description = params.description ?? null;
    sc.addEvent(new SalaryComponentCreated(sc._id.value, new Date(), { code: sc._code, name: sc._name }));
    return sc;
  }

  static load(state: SalaryComponentState): SalaryComponent {
    const sc = new SalaryComponent(new SalaryComponentId(state.id), state.code, state.name, state.elementType, state.category);
    sc._nameEn = state.nameEn;
    sc._isActive = state.isActive;
    sc._isTaxable = state.isTaxable;
    sc._isInsurable = state.isInsurable;
    sc._isPITable = state.isPITable;
    sc._priority = state.priority;
    sc._formula = state.formula;
    sc._defaultValue = state.defaultValue;
    sc._currencyCode = state.currencyCode;
    sc._description = state.description;
    sc._version = state.version;
    sc._createdAt = state.createdAt;
    sc._updatedAt = state.updatedAt;
    sc._deletedAt = state.deletedAt;
    return sc;
  }

  toState(): SalaryComponentState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      nameEn: this._nameEn, elementType: this._elementType, category: this._category,
      isActive: this._isActive, isTaxable: this._isTaxable, isInsurable: this._isInsurable,
      isPITable: this._isPITable, priority: this._priority, formula: this._formula,
      defaultValue: this._defaultValue, currencyCode: this._currencyCode,
      description: this._description, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }

  update(params: { name?: string; isActive?: boolean; isTaxable?: boolean; isInsurable?: boolean; isPITable?: boolean; priority?: number; formula?: string; defaultValue?: bigint }): void {
    if (params.name !== undefined) this._name = params.name;
    if (params.isActive !== undefined) this._isActive = params.isActive;
    if (params.isTaxable !== undefined) this._isTaxable = params.isTaxable;
    if (params.isInsurable !== undefined) this._isInsurable = params.isInsurable;
    if (params.isPITable !== undefined) this._isPITable = params.isPITable;
    if (params.priority !== undefined) this._priority = params.priority;
    if (params.formula !== undefined) this._formula = params.formula;
    if (params.defaultValue !== undefined) this._defaultValue = params.defaultValue;
    this._version++;
    this._updatedAt = new Date();
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  get id(): SalaryComponentId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get elementType(): string { return this._elementType; }
  get category(): string { return this._category; }
  get isTaxable(): boolean { return this._isTaxable; }
  get isInsurable(): boolean { return this._isInsurable; }
  get isPITable(): boolean { return this._isPITable; }
  get priority(): number { return this._priority; }
  get isActive(): boolean { return this._isActive; }
  get defaultValue(): bigint | null { return this._defaultValue; }
  get version(): number { return this._version; }
}
