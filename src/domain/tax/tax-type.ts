import { AggregateRoot } from "../../shared/aggregate-root.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxTypeId extends Identifier {
  static new(): TaxTypeId { return new TaxTypeId(IdGenerator.uuid()); }
}

export enum TaxCategory {
  Consumption = "consumption",
  Income = "income",
  Property = "property",
  NaturalResource = "natural_resource",
  Environmental = "environmental",
  Customs = "customs",
  Registration = "registration",
  License = "license",
  Withholding = "withholding",
  Digital = "digital",
  Other = "other",
}

export enum TaxNature {
  Direct = "direct",
  Indirect = "indirect",
}

export enum TaxBasis {
  GrossRevenue = "gross_revenue",
  ValueAdded = "value_added",
  TaxableIncome = "taxable_income",
  Turnover = "turnover",
  Quantity = "quantity",
  Weight = "weight",
  Volume = "volume",
  Unit = "unit",
  ContractValue = "contract_value",
  TransactionValue = "transaction_value",
  AssessedValue = "assessed_value",
  Other = "other",
}

export enum TaxPaymentMethod {
  Deduction = "deduction",
  Direct = "direct",
  Withholding = "withholding",
  Stamp = "stamp",
  Electronic = "electronic",
}

export enum TaxFilingFrequency {
  Monthly = "monthly",
  Quarterly = "quarterly",
  SemiAnnual = "semi_annual",
  Annual = "annual",
  PerTransaction = "per_transaction",
  Event = "event",
}

export enum TaxCalculationMethod {
  CreditMethod = "credit_method",
  DirectMethod = "direct_method",
  Progressive = "progressive",
  Flat = "flat",
  Bracket = "bracket",
  Compound = "compound",
  Cascading = "cascading",
  Mixed = "mixed",
}

export interface TaxTypeState {
  id: string;
  code: string;
  name: string;
  nameEn: string | null;
  category: TaxCategory;
  nature: TaxNature;
  basis: TaxBasis;
  calculationMethod: TaxCalculationMethod;
  paymentMethod: TaxPaymentMethod;
  filingFrequency: TaxFilingFrequency;
  description: string | null;
  legalReference: string | null;
  isActive: boolean;
  requiresRegistration: boolean;
  requiresDeclaration: boolean;
  requiresPayment: boolean;
  hasWithholding: boolean;
  hasExemption: boolean;
  hasIncentive: boolean;
  priority: number;
  parentTaxTypeId: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxType extends AggregateRoot<TaxTypeId> {
  private _id: TaxTypeId;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _category: TaxCategory;
  private _nature: TaxNature;
  private _basis: TaxBasis;
  private _calculationMethod: TaxCalculationMethod;
  private _paymentMethod: TaxPaymentMethod;
  private _filingFrequency: TaxFilingFrequency;
  private _description: string | null;
  private _legalReference: string | null;
  private _isActive: boolean;
  private _requiresRegistration: boolean;
  private _requiresDeclaration: boolean;
  private _requiresPayment: boolean;
  private _hasWithholding: boolean;
  private _hasExemption: boolean;
  private _hasIncentive: boolean;
  private _priority: number;
  private _parentTaxTypeId: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(params: {
    id?: TaxTypeId;
    code: string;
    name: string;
    category: TaxCategory;
    nature: TaxNature;
    basis: TaxBasis;
    calculationMethod: TaxCalculationMethod;
    paymentMethod: TaxPaymentMethod;
    filingFrequency: TaxFilingFrequency;
    parentTaxTypeId?: string | null;
  }) {
    super();
    this._id = params.id ?? TaxTypeId.new();
    this._code = params.code;
    this._name = params.name;
    this._nameEn = null;
    this._category = params.category;
    this._nature = params.nature;
    this._basis = params.basis;
    this._calculationMethod = params.calculationMethod;
    this._paymentMethod = params.paymentMethod;
    this._filingFrequency = params.filingFrequency;
    this._parentTaxTypeId = params.parentTaxTypeId ?? null;
    this._description = null;
    this._legalReference = null;
    this._isActive = true;
    this._requiresRegistration = true;
    this._requiresDeclaration = true;
    this._requiresPayment = true;
    this._hasWithholding = false;
    this._hasExemption = false;
    this._hasIncentive = false;
    this._priority = 0;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: TaxTypeState): TaxType {
    const t = new TaxType({ code: state.code, name: state.name, category: state.category, nature: state.nature, basis: state.basis, calculationMethod: state.calculationMethod, paymentMethod: state.paymentMethod, filingFrequency: state.filingFrequency });
    t._id = new TaxTypeId(state.id);
    t._nameEn = state.nameEn;
    t._description = state.description;
    t._legalReference = state.legalReference;
    t._isActive = state.isActive;
    t._requiresRegistration = state.requiresRegistration;
    t._requiresDeclaration = state.requiresDeclaration;
    t._requiresPayment = state.requiresPayment;
    t._hasWithholding = state.hasWithholding;
    t._hasExemption = state.hasExemption;
    t._hasIncentive = state.hasIncentive;
    t._priority = state.priority;
    t._parentTaxTypeId = state.parentTaxTypeId;
    t._createdAt = state.createdAt;
    t._updatedAt = state.updatedAt;
    t._version = state.version;
    return t;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get category() { return this._category; }
  get nature() { return this._nature; }
  get basis() { return this._basis; }
  get calculationMethod() { return this._calculationMethod; }
  get paymentMethod() { return this._paymentMethod; }
  get filingFrequency() { return this._filingFrequency; }
  get isActive() { return this._isActive; }
  get priority() { return this._priority; }
  get version() { return this._version; }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): TaxTypeState {
    return {
      id: this._id.value, code: this._code, name: this._name, nameEn: this._nameEn,
      category: this._category, nature: this._nature, basis: this._basis,
      calculationMethod: this._calculationMethod, paymentMethod: this._paymentMethod,
      filingFrequency: this._filingFrequency, description: this._description,
      legalReference: this._legalReference, isActive: this._isActive,
      requiresRegistration: this._requiresRegistration,
      requiresDeclaration: this._requiresDeclaration,
      requiresPayment: this._requiresPayment,
      hasWithholding: this._hasWithholding, hasExemption: this._hasExemption,
      hasIncentive: this._hasIncentive, priority: this._priority,
      parentTaxTypeId: this._parentTaxTypeId,
      createdAt: this._createdAt, updatedAt: this._updatedAt, version: this._version,
    };
  }
}
