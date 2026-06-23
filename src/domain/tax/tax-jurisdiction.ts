import { AggregateRoot } from "../../shared/aggregate-root.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxJurisdictionId extends Identifier {
  static new(): TaxJurisdictionId { return new TaxJurisdictionId(IdGenerator.uuid()); }
}

export class TaxRegionId extends Identifier {
  static new(): TaxRegionId { return new TaxRegionId(IdGenerator.uuid()); }
}

export class TaxAuthorityId extends Identifier {
  static new(): TaxAuthorityId { return new TaxAuthorityId(IdGenerator.uuid()); }
}

export enum JurisdictionLevel {
  National = "national",
  Provincial = "provincial",
  District = "district",
  Commune = "commune",
  SpecialZone = "special_zone",
}

export enum TaxRegionType {
  EconomicZone = "economic_zone",
  HighTechZone = "high_tech_zone",
  IndustrialZone = "industrial_zone",
  DifficultArea = "difficult_area",
  VeryDifficultArea = "very_difficult_area",
  Normal = "normal",
}

export interface TaxAuthorityState {
  id: string;
  code: string;
  name: string;
  taxOfficeCode: string;
  jurisdictionLevel: JurisdictionLevel;
  parentId: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxAuthority extends AggregateRoot<TaxAuthorityId> {
  private _id: TaxAuthorityId;
  private _code: string;
  private _name: string;
  private _taxOfficeCode: string;
  private _jurisdictionLevel: JurisdictionLevel;
  private _parentId: string | null;
  private _address: string | null;
  private _phone: string | null;
  private _email: string | null;
  private _website: string | null;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(code: string, name: string, taxOfficeCode: string, jurisdictionLevel: JurisdictionLevel) {
    super();
    this._id = TaxAuthorityId.new();
    this._code = code;
    this._name = name;
    this._taxOfficeCode = taxOfficeCode;
    this._jurisdictionLevel = jurisdictionLevel;
    this._parentId = null;
    this._address = null;
    this._phone = null;
    this._email = null;
    this._website = null;
    this._isActive = true;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(s: TaxAuthorityState): TaxAuthority {
    const a = new TaxAuthority(s.code, s.name, s.taxOfficeCode, s.jurisdictionLevel);
    a._id = new TaxAuthorityId(s.id);
    a._parentId = s.parentId;
    a._address = s.address; a._phone = s.phone; a._email = s.email; a._website = s.website;
    a._isActive = s.isActive; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt; a._version = s.version;
    return a;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get taxOfficeCode() { return this._taxOfficeCode; }
  get jurisdictionLevel() { return this._jurisdictionLevel; }

  toState(): TaxAuthorityState {
    return { id: this._id.value, code: this._code, name: this._name, taxOfficeCode: this._taxOfficeCode, jurisdictionLevel: this._jurisdictionLevel, parentId: this._parentId, address: this._address, phone: this._phone, email: this._email, website: this._website, isActive: this._isActive, createdAt: this._createdAt, updatedAt: this._updatedAt, version: this._version };
  }
}

export interface TaxRegionState {
  id: string;
  code: string;
  name: string;
  regionType: TaxRegionType;
  parentId: string | null;
  countryCode: string;
  provinceCode: string | null;
  districtCode: string | null;
  communeCode: string | null;
  isActive: boolean;
  incentiveDescription: string | null;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxRegion extends AggregateRoot<TaxRegionId> {
  private _id: TaxRegionId;
  private _code: string;
  private _name: string;
  private _regionType: TaxRegionType;
  private _parentId: string | null;
  private _countryCode: string;
  private _provinceCode: string | null;
  private _districtCode: string | null;
  private _communeCode: string | null;
  private _isActive: boolean;
  private _incentiveDescription: string | null;
  private _effectiveFrom: Date;
  private _effectiveTo: Date | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(code: string, name: string, regionType: TaxRegionType, countryCode: string) {
    super();
    this._id = TaxRegionId.new();
    this._code = code; this._name = name; this._regionType = regionType;
    this._countryCode = countryCode; this._effectiveFrom = new Date();
    this._parentId = null; this._provinceCode = null; this._districtCode = null;
    this._communeCode = null; this._isActive = true; this._incentiveDescription = null;
    this._effectiveTo = null; this._createdAt = new Date(); this._updatedAt = new Date(); this._version = 1;
  }

  static load(s: TaxRegionState): TaxRegion {
    const r = new TaxRegion(s.code, s.name, s.regionType, s.countryCode);
    r._id = new TaxRegionId(s.id);
    r._parentId = s.parentId; r._provinceCode = s.provinceCode; r._districtCode = s.districtCode;
    r._communeCode = s.communeCode; r._isActive = s.isActive; r._incentiveDescription = s.incentiveDescription;
    r._effectiveFrom = s.effectiveFrom; r._effectiveTo = s.effectiveTo;
    r._createdAt = s.createdAt; r._updatedAt = s.updatedAt; r._version = s.version;
    return r;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get regionType() { return this._regionType; }

  toState(): TaxRegionState {
    return { id: this._id.value, code: this._code, name: this._name, regionType: this._regionType, parentId: this._parentId, countryCode: this._countryCode, provinceCode: this._provinceCode, districtCode: this._districtCode, communeCode: this._communeCode, isActive: this._isActive, incentiveDescription: this._incentiveDescription, effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo, createdAt: this._createdAt, updatedAt: this._updatedAt, version: this._version };
  }
}
