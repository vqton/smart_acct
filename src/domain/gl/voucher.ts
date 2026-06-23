import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class VoucherTypeId extends Identifier {
  static new(): VoucherTypeId {
    return new VoucherTypeId(IdGenerator.uuid());
  }
}

export class VoucherSeriesId extends Identifier {
  static new(): VoucherSeriesId {
    return new VoucherSeriesId(IdGenerator.uuid());
  }
}

export enum VoucherTypeCategory {
  Payment = "payment",
  Receipt = "receipt",
  Journal = "journal",
  Sales = "sales",
  Purchase = "purchase",
  Payroll = "payroll",
  Inventory = "inventory",
  FixedAsset = "fixed_asset",
  Tax = "tax",
  Other = "other",
}

export enum SequenceMethod {
  Annual = "annual",
  Monthly = "monthly",
  Continuous = "continuous",
}

export interface VoucherTypeState {
  id: string;
  code: string;
  name: string;
  category: VoucherTypeCategory;
  description: string | null;
  requiresApproval: boolean;
  requiresAttachment: boolean;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export interface VoucherSeriesState {
  id: string;
  voucherTypeId: string;
  code: string;
  name: string;
  prefix: string;
  suffix: string | null;
  currentNumber: number;
  nextNumber: number;
  minDigits: number;
  sequenceMethod: SequenceMethod;
  fiscalYearId: string | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class VoucherType extends AggregateRoot<VoucherTypeId> {
  private _id: VoucherTypeId;
  private _code: string;
  private _name: string;
  private _category: VoucherTypeCategory;
  private _description: string | null;
  private _requiresApproval: boolean;
  private _requiresAttachment: boolean;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(
    id: VoucherTypeId,
    code: string,
    name: string,
    category: VoucherTypeCategory,
    requiresApproval = true,
    requiresAttachment = false,
    description: string | null = null,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._category = category;
    this._requiresApproval = requiresApproval;
    this._requiresAttachment = requiresAttachment;
    this._description = description;
    this._isActive = true;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: VoucherTypeState): VoucherType {
    const vt = new VoucherType(
      new VoucherTypeId(state.id),
      state.code,
      state.name,
      state.category,
      state.requiresApproval,
      state.requiresAttachment,
      state.description,
    );
    vt._isActive = state.isActive;
    vt._createdAt = state.createdAt;
    vt._updatedAt = state.updatedAt;
    vt._version = state.version;
    return vt;
  }

  get id(): VoucherTypeId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get category(): VoucherTypeCategory { return this._category; }
  get description(): string | null { return this._description; }
  get requiresApproval(): boolean { return this._requiresApproval; }
  get requiresAttachment(): boolean { return this._requiresAttachment; }
  get isActive(): boolean { return this._isActive; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }

  modify(params: { name?: string; description?: string; requiresApproval?: boolean; requiresAttachment?: boolean }): void {
    if (params.name !== undefined) this._name = params.name;
    if (params.description !== undefined) this._description = params.description;
    if (params.requiresApproval !== undefined) this._requiresApproval = params.requiresApproval;
    if (params.requiresAttachment !== undefined) this._requiresAttachment = params.requiresAttachment;
    this._updatedAt = new Date();
    this._version++;
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): VoucherTypeState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      category: this._category,
      description: this._description,
      requiresApproval: this._requiresApproval,
      requiresAttachment: this._requiresAttachment,
      isActive: this._isActive,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}

export class VoucherSeries extends AggregateRoot<VoucherSeriesId> {
  private _id: VoucherSeriesId;
  private _voucherTypeId: string;
  private _code: string;
  private _name: string;
  private _prefix: string;
  private _suffix: string | null;
  private _currentNumber: number;
  private _nextNumber: number;
  private _minDigits: number;
  private _sequenceMethod: SequenceMethod;
  private _fiscalYearId: string | null;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(
    id: VoucherSeriesId,
    voucherTypeId: string,
    code: string,
    name: string,
    prefix: string,
    sequenceMethod: SequenceMethod = SequenceMethod.Annual,
    minDigits = 4,
    suffix: string | null = null,
    fiscalYearId: string | null = null,
  ) {
    super();
    this._id = id;
    this._voucherTypeId = voucherTypeId;
    this._code = code;
    this._name = name;
    this._prefix = prefix;
    this._sequenceMethod = sequenceMethod;
    this._minDigits = minDigits;
    this._suffix = suffix;
    this._fiscalYearId = fiscalYearId;
    this._currentNumber = 0;
    this._nextNumber = 1;
    this._isActive = true;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: VoucherSeriesState): VoucherSeries {
    const vs = new VoucherSeries(
      new VoucherSeriesId(state.id),
      state.voucherTypeId,
      state.code,
      state.name,
      state.prefix,
      state.sequenceMethod,
      state.minDigits,
      state.suffix,
      state.fiscalYearId,
    );
    vs._currentNumber = state.currentNumber;
    vs._nextNumber = state.nextNumber;
    vs._isActive = state.isActive;
    vs._createdAt = state.createdAt;
    vs._updatedAt = state.updatedAt;
    vs._version = state.version;
    return vs;
  }

  get id(): VoucherSeriesId { return this._id; }
  get voucherTypeId(): string { return this._voucherTypeId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get prefix(): string { return this._prefix; }
  get suffix(): string | null { return this._suffix; }
  get currentNumber(): number { return this._currentNumber; }
  get nextNumber(): number { return this._nextNumber; }
  get minDigits(): number { return this._minDigits; }
  get sequenceMethod(): SequenceMethod { return this._sequenceMethod; }
  get fiscalYearId(): string | null { return this._fiscalYearId; }
  get isActive(): boolean { return this._isActive; }

  reserve(): string {
    if (!this._isActive) throw new DomainError("BusinessRule", "Voucher series is inactive");
    const num = this._nextNumber;
    this._nextNumber++;
    this._currentNumber = num;
    this._updatedAt = new Date();
    this._version++;
    return this.formatNumber(num);
  }

  private formatNumber(num: number): string {
    const year = this._fiscalYearId?.slice(0, 4) ?? new Date().getFullYear().toString();
    const padded = num.toString().padStart(this._minDigits, "0");
    const suffix = this._suffix ?? "";
    if (this._sequenceMethod === SequenceMethod.Annual) {
      return `${this._prefix}${year}${padded}${suffix}`;
    }
    return `${this._prefix}${padded}${suffix}`;
  }

  toState(): VoucherSeriesState {
    return {
      id: this._id.value,
      voucherTypeId: this._voucherTypeId,
      code: this._code,
      name: this._name,
      prefix: this._prefix,
      suffix: this._suffix,
      currentNumber: this._currentNumber,
      nextNumber: this._nextNumber,
      minDigits: this._minDigits,
      sequenceMethod: this._sequenceMethod,
      fiscalYearId: this._fiscalYearId,
      isActive: this._isActive,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
