import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FrFormulaId } from "./fr-ids.js";
import { FrFormulaType } from "./fr-enums.js";

export interface FormulaState {
  id: string;
  code: string;
  name: string;
  formulaType: FrFormulaType;
  expression: string;
  description: string | null;
  returnType: string;
  minValue: number | null;
  maxValue: number | null;
  validationRule: string | null;
  isActive: boolean;
  version: number;
  createdById: string;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Formula extends AggregateRoot<FrFormulaId> {
  private _id!: FrFormulaId;
  private _code!: string;
  private _name!: string;
  private _formulaType: FrFormulaType = FrFormulaType.Simple;
  private _expression!: string;
  private _description: string | null = null;
  private _returnType = "number";
  private _minValue: number | null = null;
  private _maxValue: number | null = null;
  private _validationRule: string | null = null;
  private _isActive = true;
  private _version = 1;
  private _createdById!: string;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _deletedAt: Date | null = null;

  private constructor(id: FrFormulaId) { super(); this._id = id; }

  static create(params: {
    code: string;
    name: string;
    formulaType?: FrFormulaType;
    expression: string;
    returnType?: string;
    description?: string;
    createdById: string;
  }): Formula {
    const f = new Formula(FrFormulaId.new());
    f._code = params.code;
    f._name = params.name;
    f._formulaType = params.formulaType ?? FrFormulaType.Simple;
    f._expression = params.expression;
    f._returnType = params.returnType ?? "number";
    f._description = params.description ?? null;
    f._createdById = params.createdById;
    return f;
  }

  static load(state: FormulaState): Formula {
    const f = new Formula(new FrFormulaId(state.id));
    f._code = state.code;
    f._name = state.name;
    f._formulaType = state.formulaType;
    f._expression = state.expression;
    f._description = state.description;
    f._returnType = state.returnType;
    f._minValue = state.minValue;
    f._maxValue = state.maxValue;
    f._validationRule = state.validationRule;
    f._isActive = state.isActive;
    f._version = state.version;
    f._createdById = state.createdById;
    f._createdAt = state.createdAt;
    f._updatedAt = state.updatedAt;
    f._deletedAt = state.deletedAt;
    return f;
  }

  get id(): FrFormulaId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get formulaType(): FrFormulaType { return this._formulaType; }
  get expression(): string { return this._expression; }
  get returnType(): string { return this._returnType; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }
  get createdById(): string { return this._createdById; }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  updateExpression(expression: string): void {
    this._expression = expression;
    this._updatedAt = new Date();
    this._version++;
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): FormulaState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      formulaType: this._formulaType,
      expression: this._expression,
      description: this._description,
      returnType: this._returnType,
      minValue: this._minValue,
      maxValue: this._maxValue,
      validationRule: this._validationRule,
      isActive: this._isActive,
      version: this._version,
      createdById: this._createdById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
