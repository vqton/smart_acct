import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { Money } from "../shared/money.js";
import { FaAssetId, FaAssetGroupId, FaAssetClassId, FaAssetCategoryId } from "./fa-ids.js";
import {
  FaAssetType, FaAssetStatus, FaAcquisitionType, FaDepreciationMethod,
  FaDepreciationArea, FaRevaluationType, FaImpairmentType, FaDisposalType,
} from "./fa-enums.js";
import { DepreciationSchedule, AssetLocation, AssetTagInfo } from "./fa-value-objects.js";
import {
  FaAssetCreated, FaAssetAcquired, FaAssetCapitalized, FaAssetDisposed,
  FaAssetTransferred, FaAssetRevalued, FaAssetImpaired, FaAssetWrittenOff,
  FaAssetDonated, FaAssetReopened,
} from "./fa-events.js";
import {
  AssetMustBeCapitalized, AssetMustNotBeDisposed, AssetMustNotBeFullyDepreciated,
  AssetMustHavePositiveValue, DepreciationStartDateMustBeSet, UsefulLifeMustBePositive,
  DisposalMustBeAfterAcquisition,
} from "./fa-specifications.js";

export interface FaAssetState {
  id: string;
  companyId: string;
  branchId: string | null;
  assetCode: string;
  assetName: string;
  assetNameEn: string | null;
  description: string | null;
  assetType: FaAssetType;
  assetStatus: FaAssetStatus;
  groupId: string | null;
  classId: string | null;
  categoryId: string | null;
  parentId: string | null;
  rootAssetId: string | null;
  isComponent: boolean;
  isLeased: boolean;
  isCip: boolean;
  isInvestmentProperty: boolean;
  acquisitionType: FaAcquisitionType | null;
  acquisitionDate: Date | null;
  capitalizationDate: Date | null;
  inUseDate: Date | null;
  disposalDate: Date | null;
  retirementDate: Date | null;
  originalCost: number;
  accumulatedDepreciation: number;
  netBookValue: number;
  residualValue: number;
  revaluationAmount: number;
  impairmentAmount: number;
  revaluationReserve: number;
  currencyCode: string;
  exchangeRate: number;
  depreciationMethod: FaDepreciationMethod;
  usefulLifeYears: number;
  usefulLifeMonths: number;
  usefulLifeUnits: number | null;
  unitsProduced: number | null;
  depreciationRate: number | null;
  depreciationStartDate: Date | null;
  depreciationEndDate: Date | null;
  isFullyDepreciated: boolean;
  isSuspended: boolean;
  suspensionStartDate: Date | null;
  suspensionEndDate: Date | null;
  costCenterId: string | null;
  profitCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  businessUnitId: string | null;
  locationId: string | null;
  custodianId: string | null;
  custodianName: string | null;
  ownerId: string | null;
  serialNumber: string | null;
  modelNumber: string | null;
  manufacturer: string | null;
  manufacturerYear: number | null;
  manufactureCountry: string | null;
  supplierId: string | null;
  supplierName: string | null;
  warrantyExpiryDate: Date | null;
  insurancePolicyNumber: string | null;
  insuranceExpiryDate: Date | null;
  insuredValue: number | null;
  address: string | null;
  ward: string | null;
  district: string | null;
  province: string | null;
  country: string | null;
  gpsCoordinates: string | null;
  building: string | null;
  floor: string | null;
  room: string | null;
  taxCode: string | null;
  taxAuthority: string | null;
  vatRate: number | null;
  importDutyPaid: number | null;
  nonRefundableTax: number | null;
  cipProjectId: string | null;
  poNumber: string | null;
  invoiceNumber: string | null;
  contractNumber: string | null;
  approvalStatus: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class FaAsset extends AggregateRoot<FaAssetId> {
  private _id: FaAssetId;
  private _companyId: string;
  private _branchId: string | null;
  private _assetCode: string;
  private _assetName: string;
  private _assetNameEn: string | null;
  private _description: string | null;
  private _assetType: FaAssetType;
  private _assetStatus: FaAssetStatus;
  private _groupId: string | null;
  private _classId: string | null;
  private _categoryId: string | null;
  private _parentId: string | null;
  private _rootAssetId: string | null;
  private _isComponent: boolean;
  private _isLeased: boolean;
  private _isCip: boolean;
  private _isInvestmentProperty: boolean;
  private _acquisitionType: FaAcquisitionType | null;
  private _acquisitionDate: Date | null;
  private _capitalizationDate: Date | null;
  private _inUseDate: Date | null;
  private _disposalDate: Date | null;
  private _retirementDate: Date | null;
  private _originalCost: number;
  private _accumulatedDepreciation: number;
  private _netBookValue: number;
  private _residualValue: number;
  private _revaluationAmount: number;
  private _impairmentAmount: number;
  private _revaluationReserve: number;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _depreciationMethod: FaDepreciationMethod;
  private _usefulLifeYears: number;
  private _usefulLifeMonths: number;
  private _usefulLifeUnits: number | null;
  private _unitsProduced: number | null;
  private _depreciationRate: number | null;
  private _depreciationStartDate: Date | null;
  private _depreciationEndDate: Date | null;
  private _isFullyDepreciated: boolean;
  private _isSuspended: boolean;
  private _suspensionStartDate: Date | null;
  private _suspensionEndDate: Date | null;
  private _costCenterId: string | null;
  private _profitCenterId: string | null;
  private _departmentId: string | null;
  private _projectId: string | null;
  private _businessUnitId: string | null;
  private _locationId: string | null;
  private _custodianId: string | null;
  private _custodianName: string | null;
  private _ownerId: string | null;
  private _serialNumber: string | null;
  private _modelNumber: string | null;
  private _manufacturer: string | null;
  private _manufacturerYear: number | null;
  private _manufactureCountry: string | null;
  private _supplierId: string | null;
  private _supplierName: string | null;
  private _warrantyExpiryDate: Date | null;
  private _insurancePolicyNumber: string | null;
  private _insuranceExpiryDate: Date | null;
  private _insuredValue: number | null;
  private _address: string | null;
  private _ward: string | null;
  private _district: string | null;
  private _province: string | null;
  private _country: string | null;
  private _gpsCoordinates: string | null;
  private _building: string | null;
  private _floor: string | null;
  private _room: string | null;
  private _taxCode: string | null;
  private _taxAuthority: string | null;
  private _vatRate: number | null;
  private _importDutyPaid: number | null;
  private _nonRefundableTax: number | null;
  private _cipProjectId: string | null;
  private _poNumber: string | null;
  private _invoiceNumber: string | null;
  private _contractNumber: string | null;
  private _approvalStatus: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(
    companyId: string, assetCode: string, assetName: string, assetType: FaAssetType,
    depreciationMethod: FaDepreciationMethod, usefulLifeYears: number, usefulLifeMonths: number,
  ) {
    super();
    this._id = FaAssetId.new();
    this._companyId = companyId;
    this._assetCode = assetCode;
    this._assetName = assetName;
    this._assetType = assetType;
    this._assetStatus = FaAssetStatus.Draft;
    this._depreciationMethod = depreciationMethod;
    this._usefulLifeYears = usefulLifeYears;
    this._usefulLifeMonths = usefulLifeMonths;
    this._originalCost = 0;
    this._accumulatedDepreciation = 0;
    this._netBookValue = 0;
    this._residualValue = 0;
    this._revaluationAmount = 0;
    this._impairmentAmount = 0;
    this._revaluationReserve = 0;
    this._currencyCode = "VND";
    this._exchangeRate = 1;
    this._isFullyDepreciated = false;
    this._isSuspended = false;
    this._isComponent = false;
    this._isLeased = false;
    this._isCip = false;
    this._isInvestmentProperty = false;
    this._country = "VN";
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._branchId = null;
    this._assetNameEn = null;
    this._description = null;
    this._groupId = null;
    this._classId = null;
    this._categoryId = null;
    this._parentId = null;
    this._rootAssetId = null;
    this._acquisitionType = null;
    this._acquisitionDate = null;
    this._capitalizationDate = null;
    this._inUseDate = null;
    this._disposalDate = null;
    this._retirementDate = null;
    this._usefulLifeUnits = null;
    this._unitsProduced = null;
    this._depreciationRate = null;
    this._depreciationStartDate = null;
    this._depreciationEndDate = null;
    this._suspensionStartDate = null;
    this._suspensionEndDate = null;
    this._costCenterId = null;
    this._profitCenterId = null;
    this._departmentId = null;
    this._projectId = null;
    this._businessUnitId = null;
    this._locationId = null;
    this._custodianId = null;
    this._custodianName = null;
    this._ownerId = null;
    this._serialNumber = null;
    this._modelNumber = null;
    this._manufacturer = null;
    this._manufacturerYear = null;
    this._manufactureCountry = null;
    this._supplierId = null;
    this._supplierName = null;
    this._warrantyExpiryDate = null;
    this._insurancePolicyNumber = null;
    this._insuranceExpiryDate = null;
    this._insuredValue = null;
    this._address = null;
    this._ward = null;
    this._district = null;
    this._province = null;
    this._gpsCoordinates = null;
    this._building = null;
    this._floor = null;
    this._room = null;
    this._taxCode = null;
    this._taxAuthority = null;
    this._vatRate = null;
    this._importDutyPaid = null;
    this._nonRefundableTax = null;
    this._cipProjectId = null;
    this._poNumber = null;
    this._invoiceNumber = null;
    this._contractNumber = null;
    this._approvalStatus = null;
    this._approvedById = null;
    this._approvedAt = null;
  }

  static create(p: {
    companyId: string; assetCode: string; assetName: string; assetType: FaAssetType;
    depreciationMethod: FaDepreciationMethod; usefulLifeYears: number; usefulLifeMonths: number;
    branchId?: string; groupId?: string; classId?: string; categoryId?: string;
    description?: string; serialNumber?: string; modelNumber?: string;
    manufacturer?: string; costCenterId?: string; profitCenterId?: string;
    departmentId?: string; projectId?: string; custodianId?: string;
    custodianName?: string; locationId?: string;
  }): FaAsset {
    const a = new FaAsset(p.companyId, p.assetCode, p.assetName, p.assetType, p.depreciationMethod, p.usefulLifeYears, p.usefulLifeMonths);
    if (p.branchId) a._branchId = p.branchId;
    if (p.groupId) a._groupId = p.groupId;
    if (p.classId) a._classId = p.classId;
    if (p.categoryId) a._categoryId = p.categoryId;
    if (p.description) a._description = p.description;
    if (p.serialNumber) a._serialNumber = p.serialNumber;
    if (p.modelNumber) a._modelNumber = p.modelNumber;
    if (p.manufacturer) a._manufacturer = p.manufacturer;
    if (p.costCenterId) a._costCenterId = p.costCenterId;
    if (p.profitCenterId) a._profitCenterId = p.profitCenterId;
    if (p.departmentId) a._departmentId = p.departmentId;
    if (p.projectId) a._projectId = p.projectId;
    if (p.custodianId) a._custodianId = p.custodianId;
    if (p.custodianName) a._custodianName = p.custodianName;
    if (p.locationId) a._locationId = p.locationId;
    a.addEvent(FaAssetCreated.create(a._id.value, { assetCode: p.assetCode, assetName: p.assetName, assetType: p.assetType }));
    return a;
  }

  static load(state: FaAssetState): FaAsset {
    const a = new FaAsset(state.companyId, state.assetCode, state.assetName, state.assetType, state.depreciationMethod, state.usefulLifeYears, state.usefulLifeMonths);
    a._id = FaAssetId.from(state.id);
    a._branchId = state.branchId;
    a._assetNameEn = state.assetNameEn;
    a._description = state.description;
    a._assetStatus = state.assetStatus;
    a._groupId = state.groupId;
    a._classId = state.classId;
    a._categoryId = state.categoryId;
    a._parentId = state.parentId;
    a._rootAssetId = state.rootAssetId;
    a._isComponent = state.isComponent;
    a._isLeased = state.isLeased;
    a._isCip = state.isCip;
    a._isInvestmentProperty = state.isInvestmentProperty;
    a._acquisitionType = state.acquisitionType;
    a._acquisitionDate = state.acquisitionDate;
    a._capitalizationDate = state.capitalizationDate;
    a._inUseDate = state.inUseDate;
    a._disposalDate = state.disposalDate;
    a._retirementDate = state.retirementDate;
    a._originalCost = state.originalCost;
    a._accumulatedDepreciation = state.accumulatedDepreciation;
    a._netBookValue = state.netBookValue;
    a._residualValue = state.residualValue;
    a._revaluationAmount = state.revaluationAmount;
    a._impairmentAmount = state.impairmentAmount;
    a._revaluationReserve = state.revaluationReserve;
    a._currencyCode = state.currencyCode;
    a._exchangeRate = state.exchangeRate;
    a._usefulLifeUnits = state.usefulLifeUnits;
    a._unitsProduced = state.unitsProduced;
    a._depreciationRate = state.depreciationRate;
    a._depreciationStartDate = state.depreciationStartDate;
    a._depreciationEndDate = state.depreciationEndDate;
    a._isFullyDepreciated = state.isFullyDepreciated;
    a._isSuspended = state.isSuspended;
    a._suspensionStartDate = state.suspensionStartDate;
    a._suspensionEndDate = state.suspensionEndDate;
    a._costCenterId = state.costCenterId;
    a._profitCenterId = state.profitCenterId;
    a._departmentId = state.departmentId;
    a._projectId = state.projectId;
    a._businessUnitId = state.businessUnitId;
    a._locationId = state.locationId;
    a._custodianId = state.custodianId;
    a._custodianName = state.custodianName;
    a._ownerId = state.ownerId;
    a._serialNumber = state.serialNumber;
    a._modelNumber = state.modelNumber;
    a._manufacturer = state.manufacturer;
    a._manufacturerYear = state.manufacturerYear;
    a._manufactureCountry = state.manufactureCountry;
    a._supplierId = state.supplierId;
    a._supplierName = state.supplierName;
    a._warrantyExpiryDate = state.warrantyExpiryDate;
    a._insurancePolicyNumber = state.insurancePolicyNumber;
    a._insuranceExpiryDate = state.insuranceExpiryDate;
    a._insuredValue = state.insuredValue;
    a._address = state.address;
    a._ward = state.ward;
    a._district = state.district;
    a._province = state.province;
    a._country = state.country ?? "VN";
    a._gpsCoordinates = state.gpsCoordinates;
    a._building = state.building;
    a._floor = state.floor;
    a._room = state.room;
    a._taxCode = state.taxCode;
    a._taxAuthority = state.taxAuthority;
    a._vatRate = state.vatRate;
    a._importDutyPaid = state.importDutyPaid;
    a._nonRefundableTax = state.nonRefundableTax;
    a._cipProjectId = state.cipProjectId;
    a._poNumber = state.poNumber;
    a._invoiceNumber = state.invoiceNumber;
    a._contractNumber = state.contractNumber;
    a._approvalStatus = state.approvalStatus;
    a._approvedById = state.approvedById;
    a._approvedAt = state.approvedAt;
    a._version = state.version;
    a._createdAt = state.createdAt;
    a._updatedAt = state.updatedAt;
    return a;
  }

  get id() { return this._id; }
  get companyId() { return this._companyId; }
  get branchId() { return this._branchId; }
  get assetCode() { return this._assetCode; }
  get assetName() { return this._assetName; }
  get assetType() { return this._assetType; }
  get assetStatus() { return this._assetStatus; }
  get groupId() { return this._groupId; }
  get classId() { return this._classId; }
  get categoryId() { return this._categoryId; }
  get parentId() { return this._parentId; }
  get isComponent() { return this._isComponent; }
  get isCip() { return this._isCip; }
  get acquisitionType() { return this._acquisitionType; }
  get acquisitionDate() { return this._acquisitionDate; }
  get capitalizationDate() { return this._capitalizationDate; }
  get inUseDate() { return this._inUseDate; }
  get disposalDate() { return this._disposalDate; }
  get originalCost() { return this._originalCost; }
  get accumulatedDepreciation() { return this._accumulatedDepreciation; }
  get netBookValue() { return this._netBookValue; }
  get residualValue() { return this._residualValue; }
  get revaluationAmount() { return this._revaluationAmount; }
  get impairmentAmount() { return this._impairmentAmount; }
  get revaluationReserve() { return this._revaluationReserve; }
  get currencyCode() { return this._currencyCode; }
  get depreciationMethod() { return this._depreciationMethod; }
  get usefulLifeYears() { return this._usefulLifeYears; }
  get usefulLifeMonths() { return this._usefulLifeMonths; }
  get usefulLifeUnits() { return this._usefulLifeUnits; }
  get depreciationRate() { return this._depreciationRate; }
  get depreciationStartDate() { return this._depreciationStartDate; }
  get depreciationEndDate() { return this._depreciationEndDate; }
  get isFullyDepreciated() { return this._isFullyDepreciated; }
  get isSuspended() { return this._isSuspended; }
  get costCenterId() { return this._costCenterId; }
  get profitCenterId() { return this._profitCenterId; }
  get departmentId() { return this._departmentId; }
  get projectId() { return this._projectId; }
  get custodianId() { return this._custodianId; }
  get custodianName() { return this._custodianName; }
  get locationId() { return this._locationId; }
  get serialNumber() { return this._serialNumber; }
  get supplierId() { return this._supplierId; }
  get cipProjectId() { return this._cipProjectId; }
  get version() { return this._version; }

  // ─── Lifecycle ──────────────────────────────────────────────────────────────────

  acquire(p: {
    acquisitionType: FaAcquisitionType; acquisitionDate: Date; originalCost: number;
    residualValue?: number; supplierId?: string; supplierName?: string;
    poNumber?: string; invoiceNumber?: string; contractNumber?: string;
    serialNumber?: string; taxCode?: string; taxAuthority?: string; vatRate?: number;
    importDutyPaid?: number; nonRefundableTax?: number;
  }): void {
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });
    if (this._assetStatus !== FaAssetStatus.Draft && this._assetStatus !== FaAssetStatus.PendingAcquisition) {
      throw new DomainError("BusinessRule", "Asset must be in draft or pending acquisition status");
    }
    this._acquisitionType = p.acquisitionType;
    this._acquisitionDate = p.acquisitionDate;
    this._originalCost = p.originalCost;
    this._residualValue = p.residualValue ?? 0;
    this._netBookValue = p.originalCost;
    if (p.supplierId) this._supplierId = p.supplierId;
    if (p.supplierName) this._supplierName = p.supplierName;
    if (p.poNumber) this._poNumber = p.poNumber;
    if (p.invoiceNumber) this._invoiceNumber = p.invoiceNumber;
    if (p.contractNumber) this._contractNumber = p.contractNumber;
    if (p.serialNumber) this._serialNumber = p.serialNumber;
    if (p.taxCode) this._taxCode = p.taxCode;
    if (p.taxAuthority) this._taxAuthority = p.taxAuthority;
    if (p.vatRate) this._vatRate = p.vatRate;
    if (p.importDutyPaid) this._importDutyPaid = p.importDutyPaid;
    if (p.nonRefundableTax) this._nonRefundableTax = p.nonRefundableTax;
    this._assetStatus = FaAssetStatus.Acquired;
    this._updatedAt = new Date();
    this.addEvent(FaAssetAcquired.create(this._id.value, { originalCost: p.originalCost, acquisitionType: p.acquisitionType }));
  }

  capitalize(capitalizationDate: Date): void {
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });
    new AssetMustHavePositiveValue().check({ originalCost: this._originalCost });
    if (this._assetStatus !== FaAssetStatus.Acquired) {
      throw new DomainError("BusinessRule", "Asset must be acquired before capitalization");
    }
    this._capitalizationDate = capitalizationDate;
    this._assetStatus = FaAssetStatus.Capitalized;
    this._updatedAt = new Date();
    this.addEvent(FaAssetCapitalized.create(this._id.value, { capitalizationDate: capitalizationDate.toISOString() }));
  }

  putInUse(inUseDate: Date): void {
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });
    if (this._assetStatus !== FaAssetStatus.Capitalized) {
      throw new DomainError("BusinessRule", "Asset must be capitalized before putting in use");
    }
    this._inUseDate = inUseDate;
    this._assetStatus = FaAssetStatus.InUse;
    if (!this._depreciationStartDate) {
      this._depreciationStartDate = inUseDate;
    }
    this._updatedAt = new Date();
  }

  suspend(from: Date, to?: Date): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    this._isSuspended = true;
    this._suspensionStartDate = from;
    this._suspensionEndDate = to ?? null;
    this._assetStatus = FaAssetStatus.Suspended;
    this._updatedAt = new Date();
  }

  resume(): void {
    if (!this._isSuspended) throw new DomainError("BusinessRule", "Asset is not suspended");
    this._isSuspended = false;
    this._assetStatus = FaAssetStatus.InUse;
    this._updatedAt = new Date();
  }

  markFullyDepreciated(): void {
    this._isFullyDepreciated = true;
    this._assetStatus = FaAssetStatus.FullyDepreciated;
    this._accumulatedDepreciation = this._originalCost - this._residualValue;
    this._netBookValue = this._residualValue;
    this._updatedAt = new Date();
  }

  // ─── Depreciation ──────────────────────────────────────────────────────────────

  applyDepreciation(amount: number, entryDate: Date): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    new AssetMustNotBeFullyDepreciated().check({ isFullyDepreciated: this._isFullyDepreciated });
    new DepreciationStartDateMustBeSet().check({ depreciationStartDate: this._depreciationStartDate });

    const deprAmount = Math.min(amount, this._netBookValue - this._residualValue);
    this._accumulatedDepreciation += deprAmount;
    this._netBookValue = this._originalCost - this._accumulatedDepreciation;
    this._updatedAt = new Date();

    if (this._netBookValue <= this._residualValue) {
      this.markFullyDepreciated();
    }
  }

  getDepreciationSchedule(): DepreciationSchedule {
    return new DepreciationSchedule(
      this._depreciationMethod, this._usefulLifeYears, this._usefulLifeMonths,
      this._usefulLifeUnits, Money.fromVnd(this._residualValue), this._depreciationRate,
    );
  }

  calculateMonthlyDepreciation(): number {
    if (this._isFullyDepreciated || this._isSuspended) return 0;
    const totalMonths = this._usefulLifeYears * 12 + this._usefulLifeMonths;
    if (totalMonths <= 0) return 0;
    const depreciableAmount = this._netBookValue - this._residualValue;
    if (depreciableAmount <= 0) return 0;

    switch (this._depreciationMethod) {
      case FaDepreciationMethod.StraightLine: {
        return Math.round(depreciableAmount / totalMonths);
      }
      case FaDepreciationMethod.DecliningBalance: {
        const rate = this._depreciationRate ?? (2 / totalMonths);
        return Math.round(this._netBookValue * rate);
      }
      case FaDepreciationMethod.DoubleDecliningBalance: {
        const ddbRate = 2 / totalMonths;
        return Math.round(this._netBookValue * ddbRate);
      }
      case FaDepreciationMethod.UnitsOfProduction: {
        if (!this._usefulLifeUnits || this._usefulLifeUnits <= 0) return 0;
        const unitRate = depreciableAmount / Number(this._usefulLifeUnits);
        const unitsThisPeriod = this._unitsProduced ?? 0;
        return Math.round(unitRate * unitsThisPeriod);
      }
      default:
        return 0;
    }
  }

  // ─── Revaluation ────────────────────────────────────────────────────────────────

  revalue(revaluationType: FaRevaluationType, newValue: number, revaluationDate: Date): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });

    const oldValue = this._netBookValue;
    const change = newValue - oldValue;
    this._revaluationAmount += change;
    this._netBookValue = newValue;
    this._originalCost = newValue + this._accumulatedDepreciation;

    if (change > 0) {
      this._revaluationReserve += change;
    } else if (this._revaluationReserve > 0) {
      const reserveConsumed = Math.min(Math.abs(change), this._revaluationReserve);
      this._revaluationReserve -= reserveConsumed;
    }

    this._updatedAt = new Date();
    this.addEvent(FaAssetRevalued.create(this._id.value, {
      revaluationType, oldValue, newValue, change, revaluationDate: revaluationDate.toISOString(),
    }));
  }

  // ─── Impairment ─────────────────────────────────────────────────────────────────

  impair(impairmentType: FaImpairmentType, impairmentLoss: number, impairmentDate: Date): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });

    this._impairmentAmount += impairmentLoss;
    this._netBookValue -= impairmentLoss;
    this._updatedAt = new Date();
    this.addEvent(FaAssetImpaired.create(this._id.value, {
      impairmentType, impairmentLoss, impairmentDate: impairmentDate.toISOString(),
    }));
  }

  reverseImpairment(reversalAmount: number): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    const actualReversal = Math.min(reversalAmount, this._impairmentAmount);
    this._impairmentAmount -= actualReversal;
    this._netBookValue += actualReversal;
    this._updatedAt = new Date();
  }

  // ─── Disposal ───────────────────────────────────────────────────────────────────

  dispose(p: {
    disposalType: FaDisposalType; disposalDate: Date; proceeds: number;
    costs: number; reason?: string; customerId?: string; customerName?: string;
    invoiceNumber?: string;
  }): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    new DisposalMustBeAfterAcquisition().check({
      disposalDate: p.disposalDate, acquisitionDate: this._acquisitionDate ?? p.disposalDate,
    });

    this._disposalDate = p.disposalDate;
    this._assetStatus = this.mapDisposalStatus(p.disposalType);
    this._updatedAt = new Date();
    this.addEvent(FaAssetDisposed.create(this._id.value, {
      disposalType: p.disposalType, proceeds: p.proceeds, costs: p.costs,
      netBookValue: this._netBookValue, gainLoss: p.proceeds - p.costs - this._netBookValue,
    }));
  }

  private mapDisposalStatus(type: FaDisposalType): FaAssetStatus {
    switch (type) {
      case FaDisposalType.Sale: return FaAssetStatus.Sold;
      case FaDisposalType.Scrap: return FaAssetStatus.Scrapped;
      case FaDisposalType.Donation: return FaAssetStatus.Donated;
      case FaDisposalType.Destruction: return FaAssetStatus.Destroyed;
      case FaDisposalType.Theft: return FaAssetStatus.Lost;
      case FaDisposalType.Loss: return FaAssetStatus.Lost;
      case FaDisposalType.Retirement: return FaAssetStatus.Retired;
      case FaDisposalType.Transfer: return FaAssetStatus.Transferred;
      case FaDisposalType.Bulk: return FaAssetStatus.Disposed;
      case FaDisposalType.Partial: return FaAssetStatus.Disposed;
      default: return FaAssetStatus.Disposed;
    }
  }

  writeOff(reason: string): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    this._assetStatus = FaAssetStatus.WrittenOff;
    this._updatedAt = new Date();
    this.addEvent(FaAssetWrittenOff.create(this._id.value, { reason }));
  }

  donate(donationDate: Date, recipientName?: string): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    this._assetStatus = FaAssetStatus.Donated;
    this._disposalDate = donationDate;
    this._updatedAt = new Date();
    this.addEvent(FaAssetDonated.create(this._id.value, { recipientName }));
  }

  // ─── Transfer ───────────────────────────────────────────────────────────────────

  transfer(p: {
    toBranchId?: string; toCompanyId?: string; toCostCenterId?: string;
    toDepartmentId?: string; toLocationId?: string; toCustodianId?: string;
    toCustodianName?: string; transferDate: Date;
  }): void {
    new AssetMustBeCapitalized().check({ status: this._assetStatus });
    if (p.toBranchId) this._branchId = p.toBranchId;
    if (p.toCostCenterId) this._costCenterId = p.toCostCenterId;
    if (p.toDepartmentId) this._departmentId = p.toDepartmentId;
    if (p.toLocationId) this._locationId = p.toLocationId;
    if (p.toCustodianId) this._custodianId = p.toCustodianId;
    if (p.toCustodianName) this._custodianName = p.toCustodianName;
    this._updatedAt = new Date();
    this.addEvent(FaAssetTransferred.create(this._id.value, { transferDate: p.transferDate.toISOString() }));
  }

  // ─── Update ─────────────────────────────────────────────────────────────────────

  update(p: Partial<{
    assetName: string; assetNameEn: string | null; description: string | null;
    serialNumber: string | null; modelNumber: string | null; manufacturer: string | null;
    costCenterId: string | null; profitCenterId: string | null;
    departmentId: string | null; projectId: string | null;
    custodianId: string | null; custodianName: string | null;
    locationId: string | null; address: string | null; building: string | null;
    floor: string | null; room: string | null;
    groupId: string | null; classId: string | null; categoryId: string | null;
  }>): void {
    new AssetMustNotBeDisposed().check({ status: this._assetStatus });
    if (p.assetName !== undefined) this._assetName = p.assetName;
    if (p.assetNameEn !== undefined) this._assetNameEn = p.assetNameEn;
    if (p.description !== undefined) this._description = p.description;
    if (p.serialNumber !== undefined) this._serialNumber = p.serialNumber;
    if (p.modelNumber !== undefined) this._modelNumber = p.modelNumber;
    if (p.manufacturer !== undefined) this._manufacturer = p.manufacturer;
    if (p.costCenterId !== undefined) this._costCenterId = p.costCenterId;
    if (p.profitCenterId !== undefined) this._profitCenterId = p.profitCenterId;
    if (p.departmentId !== undefined) this._departmentId = p.departmentId;
    if (p.projectId !== undefined) this._projectId = p.projectId;
    if (p.custodianId !== undefined) this._custodianId = p.custodianId;
    if (p.custodianName !== undefined) this._custodianName = p.custodianName;
    if (p.locationId !== undefined) this._locationId = p.locationId;
    if (p.address !== undefined) this._address = p.address;
    if (p.building !== undefined) this._building = p.building;
    if (p.floor !== undefined) this._floor = p.floor;
    if (p.room !== undefined) this._room = p.room;
    if (p.groupId !== undefined) this._groupId = p.groupId;
    if (p.classId !== undefined) this._classId = p.classId;
    if (p.categoryId !== undefined) this._categoryId = p.categoryId;
    this._updatedAt = new Date();
  }

  reopen(): void {
    if (this._assetStatus === FaAssetStatus.InUse || this._assetStatus === FaAssetStatus.Capitalized) {
      throw new DomainError("BusinessRule", "Asset is already active");
    }
    this._assetStatus = FaAssetStatus.InUse;
    this._isFullyDepreciated = false;
    this._updatedAt = new Date();
    this.addEvent(FaAssetReopened.create(this._id.value, {}));
  }

  // ─── Serialization ──────────────────────────────────────────────────────────────

  toState(): FaAssetState {
    return {
      id: this._id.value,
      companyId: this._companyId,
      branchId: this._branchId,
      assetCode: this._assetCode,
      assetName: this._assetName,
      assetNameEn: this._assetNameEn,
      description: this._description,
      assetType: this._assetType,
      assetStatus: this._assetStatus,
      groupId: this._groupId,
      classId: this._classId,
      categoryId: this._categoryId,
      parentId: this._parentId,
      rootAssetId: this._rootAssetId,
      isComponent: this._isComponent,
      isLeased: this._isLeased,
      isCip: this._isCip,
      isInvestmentProperty: this._isInvestmentProperty,
      acquisitionType: this._acquisitionType,
      acquisitionDate: this._acquisitionDate,
      capitalizationDate: this._capitalizationDate,
      inUseDate: this._inUseDate,
      disposalDate: this._disposalDate,
      retirementDate: this._retirementDate,
      originalCost: this._originalCost,
      accumulatedDepreciation: this._accumulatedDepreciation,
      netBookValue: this._netBookValue,
      residualValue: this._residualValue,
      revaluationAmount: this._revaluationAmount,
      impairmentAmount: this._impairmentAmount,
      revaluationReserve: this._revaluationReserve,
      currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      depreciationMethod: this._depreciationMethod,
      usefulLifeYears: this._usefulLifeYears,
      usefulLifeMonths: this._usefulLifeMonths,
      usefulLifeUnits: this._usefulLifeUnits,
      unitsProduced: this._unitsProduced,
      depreciationRate: this._depreciationRate,
      depreciationStartDate: this._depreciationStartDate,
      depreciationEndDate: this._depreciationEndDate,
      isFullyDepreciated: this._isFullyDepreciated,
      isSuspended: this._isSuspended,
      suspensionStartDate: this._suspensionStartDate,
      suspensionEndDate: this._suspensionEndDate,
      costCenterId: this._costCenterId,
      profitCenterId: this._profitCenterId,
      departmentId: this._departmentId,
      projectId: this._projectId,
      businessUnitId: this._businessUnitId,
      locationId: this._locationId,
      custodianId: this._custodianId,
      custodianName: this._custodianName,
      ownerId: this._ownerId,
      serialNumber: this._serialNumber,
      modelNumber: this._modelNumber,
      manufacturer: this._manufacturer,
      manufacturerYear: this._manufacturerYear,
      manufactureCountry: this._manufactureCountry,
      supplierId: this._supplierId,
      supplierName: this._supplierName,
      warrantyExpiryDate: this._warrantyExpiryDate,
      insurancePolicyNumber: this._insurancePolicyNumber,
      insuranceExpiryDate: this._insuranceExpiryDate,
      insuredValue: this._insuredValue,
      address: this._address,
      ward: this._ward,
      district: this._district,
      province: this._province,
      country: this._country,
      gpsCoordinates: this._gpsCoordinates,
      building: this._building,
      floor: this._floor,
      room: this._room,
      taxCode: this._taxCode,
      taxAuthority: this._taxAuthority,
      vatRate: this._vatRate,
      importDutyPaid: this._importDutyPaid,
      nonRefundableTax: this._nonRefundableTax,
      cipProjectId: this._cipProjectId,
      poNumber: this._poNumber,
      invoiceNumber: this._invoiceNumber,
      contractNumber: this._contractNumber,
      approvalStatus: this._approvalStatus,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
