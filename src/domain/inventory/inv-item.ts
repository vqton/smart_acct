import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ItemId } from "./inv-ids.js";
import { ItemType, ItemStatus, ItemCategory, ItemValuationMethod, LotControl } from "./inv-enums.js";
import { ItemDimensions } from "./inv-value-objects.js";
import { ItemCreated, ItemUpdated, ItemStatusChanged } from "./inv-events.js";

export interface ItemState {
  id: string;
  code: string;
  sku: string;
  barcode: string | null;
  plu: string | null;
  name: string;
  nameEn: string | null;
  description: string | null;
  itemType: string;
  status: string;
  category: string;
  itemGroupId: string | null;
  brandId: string | null;
  uomId: string;
  valuationMethod: string;
  lotControl: string;
  shelfLifeDays: number | null;
  isHazardous: boolean;
  isConsignment: boolean;
  isSerialized: boolean;
  isLotControlled: boolean;
  dimensions: string | null;
  taxCodeId: string | null;
  glInventoryAccountId: string | null;
  glRevenueAccountId: string | null;
  glCogsAccountId: string | null;
  glExpenseAccountId: string | null;
  glPurchaseAccountId: string | null;
  glTransferAccountId: string | null;
  standardCost: number | null;
  minStock: number | null;
  maxStock: number | null;
  reorderPoint: number | null;
  leadTimeDays: number | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Item extends AggregateRoot<ItemId> {
  private _id: ItemId;
  private _code: string;
  private _sku: string;
  private _barcode: string | null;
  private _plu: string | null;
  private _name: string;
  private _nameEn: string | null;
  private _description: string | null;
  private _itemType: ItemType;
  private _status: ItemStatus;
  private _category: ItemCategory;
  private _itemGroupId: string | null;
  private _brandId: string | null;
  private _uomId: string;
  private _valuationMethod: ItemValuationMethod;
  private _lotControl: LotControl;
  private _shelfLifeDays: number | null;
  private _isHazardous: boolean;
  private _isConsignment: boolean;
  private _isSerialized: boolean;
  private _isLotControlled: boolean;
  private _dimensions: ItemDimensions | null;
  private _taxCodeId: string | null;
  private _glInventoryAccountId: string | null;
  private _glRevenueAccountId: string | null;
  private _glCogsAccountId: string | null;
  private _glExpenseAccountId: string | null;
  private _glPurchaseAccountId: string | null;
  private _glTransferAccountId: string | null;
  private _standardCost: number | null;
  private _minStock: number | null;
  private _maxStock: number | null;
  private _reorderPoint: number | null;
  private _leadTimeDays: number | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: ItemId, code: string, sku: string, name: string, itemType: ItemType, category: ItemCategory, uomId: string) {
    super();
    this._id = id;
    this._code = code;
    this._sku = sku;
    this._name = name;
    this._itemType = itemType;
    this._category = category;
    this._uomId = uomId;
    this._barcode = null;
    this._plu = null;
    this._nameEn = null;
    this._description = null;
    this._status = ItemStatus.Active;
    this._itemGroupId = null;
    this._brandId = null;
    this._valuationMethod = ItemValuationMethod.MovingAverage;
    this._lotControl = LotControl.None;
    this._shelfLifeDays = null;
    this._isHazardous = false;
    this._isConsignment = false;
    this._isSerialized = false;
    this._isLotControlled = false;
    this._dimensions = null;
    this._taxCodeId = null;
    this._glInventoryAccountId = null;
    this._glRevenueAccountId = null;
    this._glCogsAccountId = null;
    this._glExpenseAccountId = null;
    this._glPurchaseAccountId = null;
    this._glTransferAccountId = null;
    this._standardCost = null;
    this._minStock = null;
    this._maxStock = null;
    this._reorderPoint = null;
    this._leadTimeDays = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(p: {
    code: string; sku: string; name: string; itemType?: ItemType; category?: ItemCategory; uomId: string;
    barcode?: string; plu?: string; itemGroupId?: string; brandId?: string;
    valuationMethod?: ItemValuationMethod; lotControl?: LotControl;
    shelfLifeDays?: number; isHazardous?: boolean; isConsignment?: boolean;
    glInventoryAccountId?: string; glRevenueAccountId?: string; glCogsAccountId?: string;
    glExpenseAccountId?: string; glPurchaseAccountId?: string; glTransferAccountId?: string;
    standardCost?: number; minStock?: number; maxStock?: number; reorderPoint?: number; leadTimeDays?: number;
    taxCodeId?: string;
  }): Item {
    const item = new Item(ItemId.new(), p.code, p.sku, p.name, p.itemType ?? ItemType.Inventory, p.category ?? ItemCategory.Trading, p.uomId);
    item._barcode = p.barcode ?? null;
    item._plu = p.plu ?? null;
    item._itemGroupId = p.itemGroupId ?? null;
    item._brandId = p.brandId ?? null;
    item._valuationMethod = p.valuationMethod ?? ItemValuationMethod.MovingAverage;
    item._lotControl = p.lotControl ?? LotControl.None;
    item._shelfLifeDays = p.shelfLifeDays ?? null;
    item._isHazardous = p.isHazardous ?? false;
    item._isConsignment = p.isConsignment ?? false;
    item._isSerialized = item._lotControl === LotControl.Serial || item._lotControl === LotControl.Both;
    item._isLotControlled = item._lotControl === LotControl.Lot || item._lotControl === LotControl.Both;
    item._taxCodeId = p.taxCodeId ?? null;
    item._glInventoryAccountId = p.glInventoryAccountId ?? null;
    item._glRevenueAccountId = p.glRevenueAccountId ?? null;
    item._glCogsAccountId = p.glCogsAccountId ?? null;
    item._glExpenseAccountId = p.glExpenseAccountId ?? null;
    item._glPurchaseAccountId = p.glPurchaseAccountId ?? null;
    item._glTransferAccountId = p.glTransferAccountId ?? null;
    item._standardCost = p.standardCost ?? null;
    item._minStock = p.minStock ?? null;
    item._maxStock = p.maxStock ?? null;
    item._reorderPoint = p.reorderPoint ?? null;
    item._leadTimeDays = p.leadTimeDays ?? null;
    item.addEvent(ItemCreated.create(item._id.value, { code: item._code, sku: item._sku, name: item._name }));
    return item;
  }

  static load(s: ItemState): Item {
    const item = new Item(new ItemId(s.id), s.code, s.sku, s.name, s.itemType as ItemType, s.category as ItemCategory, s.uomId);
    item._barcode = s.barcode;
    item._plu = s.plu;
    item._nameEn = s.nameEn;
    item._description = s.description;
    item._status = s.status as ItemStatus;
    item._itemGroupId = s.itemGroupId;
    item._brandId = s.brandId;
    item._valuationMethod = s.valuationMethod as ItemValuationMethod;
    item._lotControl = s.lotControl as LotControl;
    item._shelfLifeDays = s.shelfLifeDays;
    item._isHazardous = s.isHazardous;
    item._isConsignment = s.isConsignment;
    item._isSerialized = s.isSerialized;
    item._isLotControlled = s.isLotControlled;
    item._dimensions = s.dimensions ? JSON.parse(s.dimensions) : null;
    item._taxCodeId = s.taxCodeId;
    item._glInventoryAccountId = s.glInventoryAccountId;
    item._glRevenueAccountId = s.glRevenueAccountId;
    item._glCogsAccountId = s.glCogsAccountId;
    item._glExpenseAccountId = s.glExpenseAccountId;
    item._glPurchaseAccountId = s.glPurchaseAccountId;
    item._glTransferAccountId = s.glTransferAccountId;
    item._standardCost = s.standardCost;
    item._minStock = s.minStock;
    item._maxStock = s.maxStock;
    item._reorderPoint = s.reorderPoint;
    item._leadTimeDays = s.leadTimeDays;
    item._version = s.version;
    item._createdAt = s.createdAt;
    item._updatedAt = s.updatedAt;
    item._deletedAt = s.deletedAt;
    return item;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get sku() { return this._sku; }
  get name() { return this._name; }
  get status() { return this._status; }
  get itemType() { return this._itemType; }
  get category() { return this._category; }
  get valuationMethod() { return this._valuationMethod; }
  get lotControl() { return this._lotControl; }
  get isSerialized() { return this._isSerialized; }
  get isLotControlled() { return this._isLotControlled; }
  get isConsignment() { return this._isConsignment; }
  get standardCost() { return this._standardCost; }
  get glInventoryAccountId() { return this._glInventoryAccountId; }
  get glCogsAccountId() { return this._glCogsAccountId; }
  get glExpenseAccountId() { return this._glExpenseAccountId; }
  get glPurchaseAccountId() { return this._glPurchaseAccountId; }
  get glTransferAccountId() { return this._glTransferAccountId; }
  get version() { return this._version; }

  update(p: Partial<{
    name: string; barcode: string | null; plu: string | null; description: string | null;
    itemGroupId: string | null; brandId: string | null; valuationMethod: ItemValuationMethod;
    shelfLifeDays: number | null; isHazardous: boolean; taxCodeId: string | null;
    glInventoryAccountId: string | null; glRevenueAccountId: string | null;
    glCogsAccountId: string | null; glExpenseAccountId: string | null;
    glPurchaseAccountId: string | null; glTransferAccountId: string | null;
    standardCost: number | null; minStock: number | null; maxStock: number | null;
    reorderPoint: number | null; leadTimeDays: number | null;
  }>): void {
    if (this._status === ItemStatus.Discontinued || this._status === ItemStatus.Obsolete) {
      throw new DomainError("BusinessRule", "Cannot update discontinued or obsolete item");
    }
    if (p.name !== undefined) this._name = p.name;
    if (p.barcode !== undefined) this._barcode = p.barcode;
    if (p.plu !== undefined) this._plu = p.plu;
    if (p.description !== undefined) this._description = p.description;
    if (p.itemGroupId !== undefined) this._itemGroupId = p.itemGroupId;
    if (p.brandId !== undefined) this._brandId = p.brandId;
    if (p.valuationMethod !== undefined) this._valuationMethod = p.valuationMethod;
    if (p.shelfLifeDays !== undefined) this._shelfLifeDays = p.shelfLifeDays;
    if (p.isHazardous !== undefined) this._isHazardous = p.isHazardous;
    if (p.taxCodeId !== undefined) this._taxCodeId = p.taxCodeId;
    if (p.glInventoryAccountId !== undefined) this._glInventoryAccountId = p.glInventoryAccountId;
    if (p.glRevenueAccountId !== undefined) this._glRevenueAccountId = p.glRevenueAccountId;
    if (p.glCogsAccountId !== undefined) this._glCogsAccountId = p.glCogsAccountId;
    if (p.glExpenseAccountId !== undefined) this._glExpenseAccountId = p.glExpenseAccountId;
    if (p.glPurchaseAccountId !== undefined) this._glPurchaseAccountId = p.glPurchaseAccountId;
    if (p.glTransferAccountId !== undefined) this._glTransferAccountId = p.glTransferAccountId;
    if (p.standardCost !== undefined) this._standardCost = p.standardCost;
    if (p.minStock !== undefined) this._minStock = p.minStock;
    if (p.maxStock !== undefined) this._maxStock = p.maxStock;
    if (p.reorderPoint !== undefined) this._reorderPoint = p.reorderPoint;
    if (p.leadTimeDays !== undefined) this._leadTimeDays = p.leadTimeDays;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(ItemUpdated.create(this._id.value, { name: this._name }));
  }

  changeStatus(status: ItemStatus): void {
    if (this._status === status) return;
    if (this._status === ItemStatus.Obsolete) {
      throw new DomainError("BusinessRule", "Cannot change status of obsolete item");
    }
    this._status = status;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(ItemStatusChanged.create(this._id.value, status));
  }

  setDimensions(dimensions: ItemDimensions): void {
    this._dimensions = dimensions;
    this._version++;
    this._updatedAt = new Date();
  }

  delete(): void {
    if (this._deletedAt) throw new DomainError("BusinessRule", "Item already deleted");
    this._deletedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): ItemState {
    return {
      id: this._id.value, code: this._code, sku: this._sku, barcode: this._barcode,
      plu: this._plu, name: this._name, nameEn: this._nameEn, description: this._description,
      itemType: this._itemType, status: this._status, category: this._category,
      itemGroupId: this._itemGroupId, brandId: this._brandId, uomId: this._uomId,
      valuationMethod: this._valuationMethod, lotControl: this._lotControl,
      shelfLifeDays: this._shelfLifeDays, isHazardous: this._isHazardous,
      isConsignment: this._isConsignment, isSerialized: this._isSerialized,
      isLotControlled: this._isLotControlled,
      dimensions: this._dimensions ? JSON.stringify(this._dimensions) : null,
      taxCodeId: this._taxCodeId, glInventoryAccountId: this._glInventoryAccountId,
      glRevenueAccountId: this._glRevenueAccountId, glCogsAccountId: this._glCogsAccountId,
      glExpenseAccountId: this._glExpenseAccountId, glPurchaseAccountId: this._glPurchaseAccountId,
      glTransferAccountId: this._glTransferAccountId, standardCost: this._standardCost,
      minStock: this._minStock, maxStock: this._maxStock, reorderPoint: this._reorderPoint,
      leadTimeDays: this._leadTimeDays, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
