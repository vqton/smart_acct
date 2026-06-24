import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { WarehouseId, LocationId } from "./inv-ids.js";
import { WarehouseType, WarehouseStatus, LocationType, LocationStatus, StorageType } from "./inv-enums.js";
import { WarehouseAddress, LocationCapacity } from "./inv-value-objects.js";
import { WarehouseCreated, LocationCreated } from "./inv-events.js";

export interface WarehouseState {
  id: string;
  code: string;
  name: string;
  type: string;
  status: string;
  address: string | null;
  city: string | null;
  district: string | null;
  ward: string | null;
  country: string;
  companyId: string;
  branchId: string | null;
  isActive: boolean;
  allowNegative: boolean;
  capacityWeight: number | null;
  capacityVolume: number | null;
  storageType: string;
  calendarId: string | null;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  email: string | null;
  managerName: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Warehouse extends AggregateRoot<WarehouseId> {
  private _id: WarehouseId;
  private _code: string;
  private _name: string;
  private _type: WarehouseType;
  private _status: WarehouseStatus;
  private _address: WarehouseAddress | null;
  private _companyId: string;
  private _branchId: string | null;
  private _isActive: boolean;
  private _allowNegative: boolean;
  private _capacityWeight: number | null;
  private _capacityVolume: number | null;
  private _storageType: StorageType;
  private _calendarId: string | null;
  private _latitude: number | null;
  private _longitude: number | null;
  private _phone: string | null;
  private _email: string | null;
  private _managerName: string | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: WarehouseId, code: string, name: string, companyId: string) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._companyId = companyId;
    this._type = WarehouseType.Main;
    this._status = WarehouseStatus.Active;
    this._address = null;
    this._branchId = null;
    this._isActive = true;
    this._allowNegative = false;
    this._capacityWeight = null;
    this._capacityVolume = null;
    this._storageType = StorageType.Dry;
    this._calendarId = null;
    this._latitude = null;
    this._longitude = null;
    this._phone = null;
    this._email = null;
    this._managerName = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(p: {
    code: string; name: string; companyId: string; branchId?: string;
    type?: WarehouseType; address?: WarehouseAddress; storageType?: StorageType;
    allowNegative?: boolean; calendarId?: string; phone?: string;
    email?: string; managerName?: string;
  }): Warehouse {
    const w = new Warehouse(WarehouseId.new(), p.code, p.name, p.companyId);
    w._branchId = p.branchId ?? null;
    w._type = p.type ?? WarehouseType.Main;
    w._address = p.address ?? null;
    w._storageType = p.storageType ?? StorageType.Dry;
    w._allowNegative = p.allowNegative ?? false;
    w._calendarId = p.calendarId ?? null;
    w._phone = p.phone ?? null;
    w._email = p.email ?? null;
    w._managerName = p.managerName ?? null;
    w.addEvent(WarehouseCreated.create(w._id.value, { code: w._code, name: w._name, companyId: w._companyId }));
    return w;
  }

  static load(s: WarehouseState): Warehouse {
    const w = new Warehouse(new WarehouseId(s.id), s.code, s.name, s.companyId);
    w._type = s.type as WarehouseType;
    w._status = s.status as WarehouseStatus;
    w._address = s.address ? new WarehouseAddress(s.address, s.city, s.district, s.ward, s.country) : null;
    w._branchId = s.branchId;
    w._isActive = s.isActive;
    w._allowNegative = s.allowNegative;
    w._capacityWeight = s.capacityWeight;
    w._capacityVolume = s.capacityVolume;
    w._storageType = s.storageType as StorageType;
    w._calendarId = s.calendarId;
    w._latitude = s.latitude;
    w._longitude = s.longitude;
    w._phone = s.phone;
    w._email = s.email;
    w._managerName = s.managerName;
    w._notes = s.notes;
    w._version = s.version;
    w._createdAt = s.createdAt;
    w._updatedAt = s.updatedAt;
    w._deletedAt = s.deletedAt;
    return w;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get status() { return this._status; }
  get type() { return this._type; }
  get isActive() { return this._isActive; }
  get allowNegative() { return this._allowNegative; }
  get version() { return this._version; }

  update(p: Partial<{ name: string; type: WarehouseType; address: WarehouseAddress | null; storageType: StorageType; allowNegative: boolean; phone: string | null; email: string | null; managerName: string | null; notes: string | null; }>): void {
    if (this._status === WarehouseStatus.Closed) {
      throw new DomainError("BusinessRule", "Cannot update closed warehouse");
    }
    if (p.name !== undefined) this._name = p.name;
    if (p.type !== undefined) this._type = p.type;
    if (p.address !== undefined) this._address = p.address;
    if (p.storageType !== undefined) this._storageType = p.storageType;
    if (p.allowNegative !== undefined) this._allowNegative = p.allowNegative;
    if (p.phone !== undefined) this._phone = p.phone;
    if (p.email !== undefined) this._email = p.email;
    if (p.managerName !== undefined) this._managerName = p.managerName;
    if (p.notes !== undefined) this._notes = p.notes;
    this._version++;
    this._updatedAt = new Date();
  }

  activate(): void {
    if (this._isActive) return;
    this._isActive = true;
    this._status = WarehouseStatus.Active;
    this._version++;
    this._updatedAt = new Date();
  }

  deactivate(): void {
    if (!this._isActive) return;
    this._isActive = false;
    this._status = WarehouseStatus.Inactive;
    this._version++;
    this._updatedAt = new Date();
  }

  close(): void {
    this._status = WarehouseStatus.Closed;
    this._isActive = false;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): WarehouseState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      type: this._type, status: this._status,
      address: this._address?.address ?? null,
      city: this._address?.city ?? null,
      district: this._address?.district ?? null,
      ward: this._address?.ward ?? null,
      country: this._address?.country ?? "VN",
      companyId: this._companyId, branchId: this._branchId,
      isActive: this._isActive, allowNegative: this._allowNegative,
      capacityWeight: this._capacityWeight, capacityVolume: this._capacityVolume,
      storageType: this._storageType, calendarId: this._calendarId,
      latitude: this._latitude, longitude: this._longitude,
      phone: this._phone, email: this._email,
      managerName: this._managerName, notes: this._notes,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}

// ─── Location ─────────────────────────────────────────────────────────

export interface LocationState {
  id: string;
  warehouseId: string;
  parentId: string | null;
  code: string;
  name: string;
  type: string;
  status: string;
  storageType: string;
  isActive: boolean;
  maxWeight: number | null;
  maxVolume: number | null;
  maxPalletCount: number | null;
  barcode: string | null;
  putawayZone: string | null;
  pickingZone: string | null;
  x: number | null;
  y: number | null;
  z: number | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class Location extends AggregateRoot<LocationId> {
  private _id: LocationId;
  private _warehouseId: string;
  private _parentId: string | null;
  private _code: string;
  private _name: string;
  private _type: LocationType;
  private _status: LocationStatus;
  private _storageType: StorageType;
  private _isActive: boolean;
  private _capacity: LocationCapacity | null;
  private _barcode: string | null;
  private _putawayZone: string | null;
  private _pickingZone: string | null;
  private _x: number | null;
  private _y: number | null;
  private _z: number | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: LocationId, warehouseId: string, code: string, name: string, type: LocationType) {
    super();
    this._id = id;
    this._warehouseId = warehouseId;
    this._code = code;
    this._name = name;
    this._type = type;
    this._status = LocationStatus.Active;
    this._storageType = StorageType.Dry;
    this._isActive = true;
    this._capacity = null;
    this._barcode = null;
    this._parentId = null;
    this._putawayZone = null;
    this._pickingZone = null;
    this._x = null;
    this._y = null;
    this._z = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(p: {
    warehouseId: string; code: string; name: string; type?: LocationType;
    parentId?: string; storageType?: StorageType; capacity?: LocationCapacity;
    barcode?: string; putawayZone?: string; pickingZone?: string;
    x?: number; y?: number; z?: number;
  }): Location {
    const loc = new Location(LocationId.new(), p.warehouseId, p.code, p.name, p.type ?? LocationType.Bin);
    loc._parentId = p.parentId ?? null;
    loc._storageType = p.storageType ?? StorageType.Dry;
    loc._capacity = p.capacity ?? null;
    loc._barcode = p.barcode ?? null;
    loc._putawayZone = p.putawayZone ?? null;
    loc._pickingZone = p.pickingZone ?? null;
    loc._x = p.x ?? null;
    loc._y = p.y ?? null;
    loc._z = p.z ?? null;
    loc.addEvent(LocationCreated.create(loc._id.value, { code: loc._code, warehouseId: loc._warehouseId }));
    return loc;
  }

  static load(s: LocationState): Location {
    const loc = new Location(new LocationId(s.id), s.warehouseId, s.code, s.name, s.type as LocationType);
    loc._parentId = s.parentId;
    loc._status = s.status as LocationStatus;
    loc._storageType = s.storageType as StorageType;
    loc._isActive = s.isActive;
    loc._capacity = new LocationCapacity(s.maxWeight, s.maxVolume, s.maxPalletCount);
    loc._barcode = s.barcode;
    loc._putawayZone = s.putawayZone;
    loc._pickingZone = s.pickingZone;
    loc._x = s.x;
    loc._y = s.y;
    loc._z = s.z;
    loc._notes = s.notes;
    loc._version = s.version;
    loc._createdAt = s.createdAt;
    loc._updatedAt = s.updatedAt;
    return loc;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get warehouseId() { return this._warehouseId; }
  get type() { return this._type; }
  get status() { return this._status; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  block(): void {
    this._status = LocationStatus.Blocked;
    this._isActive = false;
    this._version++;
    this._updatedAt = new Date();
  }

  unblock(): void {
    this._status = LocationStatus.Active;
    this._isActive = true;
    this._version++;
    this._updatedAt = new Date();
  }

  markFull(): void {
    this._status = LocationStatus.Full;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): LocationState {
    return {
      id: this._id.value, warehouseId: this._warehouseId,
      parentId: this._parentId, code: this._code, name: this._name,
      type: this._type, status: this._status, storageType: this._storageType,
      isActive: this._isActive,
      maxWeight: this._capacity?.maxWeightKg ?? null,
      maxVolume: this._capacity?.maxVolumeCm3 ?? null,
      maxPalletCount: this._capacity?.maxPalletCount ?? null,
      barcode: this._barcode, putawayZone: this._putawayZone,
      pickingZone: this._pickingZone,
      x: this._x, y: this._y, z: this._z,
      notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
