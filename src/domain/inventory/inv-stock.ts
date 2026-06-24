import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { InventoryBalanceId } from "./inv-ids.js";
import { StockStatus } from "./inv-enums.js";
import { StockReceived, StockIssued, StockAdjusted, StockTransferred } from "./inv-events.js";

export interface StockBalanceState {
  id: string;
  itemId: string;
  warehouseId: string;
  locationId: string | null;
  lotId: string | null;
  stockStatus: string;
  quantity: number;
  reservedQty: number;
  allocatedQty: number;
  inTransitQty: number;
  onOrderQty: number;
  unitCost: number;
  totalCost: number;
  currencyCode: string;
  lastTransactionAt: Date | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class StockBalance extends AggregateRoot<InventoryBalanceId> {
  private _id: InventoryBalanceId;
  private _itemId: string;
  private _warehouseId: string;
  private _locationId: string | null;
  private _lotId: string | null;
  private _stockStatus: StockStatus;
  private _quantity: number;
  private _reservedQty: number;
  private _allocatedQty: number;
  private _inTransitQty: number;
  private _onOrderQty: number;
  private _unitCost: number;
  private _totalCost: number;
  private _currencyCode: string;
  private _lastTransactionAt: Date | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: InventoryBalanceId, itemId: string, warehouseId: string) {
    super();
    this._id = id;
    this._itemId = itemId;
    this._warehouseId = warehouseId;
    this._locationId = null;
    this._lotId = null;
    this._stockStatus = StockStatus.Available;
    this._quantity = 0;
    this._reservedQty = 0;
    this._allocatedQty = 0;
    this._inTransitQty = 0;
    this._onOrderQty = 0;
    this._unitCost = 0;
    this._totalCost = 0;
    this._currencyCode = "VND";
    this._lastTransactionAt = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(itemId: string, warehouseId: string, locationId?: string, lotId?: string): StockBalance {
    const sb = new StockBalance(InventoryBalanceId.new(), itemId, warehouseId);
    sb._locationId = locationId ?? null;
    sb._lotId = lotId ?? null;
    return sb;
  }

  static load(s: StockBalanceState): StockBalance {
    const sb = new StockBalance(new InventoryBalanceId(s.id), s.itemId, s.warehouseId);
    sb._locationId = s.locationId;
    sb._lotId = s.lotId;
    sb._stockStatus = s.stockStatus as StockStatus;
    sb._quantity = s.quantity;
    sb._reservedQty = s.reservedQty;
    sb._allocatedQty = s.allocatedQty;
    sb._inTransitQty = s.inTransitQty;
    sb._onOrderQty = s.onOrderQty;
    sb._unitCost = s.unitCost;
    sb._totalCost = s.totalCost;
    sb._currencyCode = s.currencyCode;
    sb._lastTransactionAt = s.lastTransactionAt;
    sb._version = s.version;
    sb._createdAt = s.createdAt;
    sb._updatedAt = s.updatedAt;
    return sb;
  }

  get id() { return this._id; }
  get itemId() { return this._itemId; }
  get warehouseId() { return this._warehouseId; }
  get locationId() { return this._locationId; }
  get lotId() { return this._lotId; }
  get stockStatus() { return this._stockStatus; }
  get quantity() { return this._quantity; }
  get reservedQty() { return this._reservedQty; }
  get allocatedQty() { return this._allocatedQty; }
  get inTransitQty() { return this._inTransitQty; }
  get onOrderQty() { return this._onOrderQty; }
  get availableQty() { return this._quantity - this._reservedQty - this._allocatedQty; }
  get unitCost() { return this._unitCost; }
  get totalCost() { return this._totalCost; }
  get version() { return this._version; }

  receive(quantity: number, unitCost: number, allowNegative: boolean): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Receive quantity must be positive");
    if (!allowNegative && this._quantity + quantity < 0) {
      throw new DomainError("BusinessRule", "Negative inventory not allowed");
    }
    this._quantity += quantity;
    this._unitCost = this._quantity > 0
      ? (this._totalCost + quantity * unitCost) / this._quantity
      : unitCost;
    this._totalCost = this._quantity * this._unitCost;
    this._lastTransactionAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockReceived.create(this._id.value, { itemId: this._itemId, quantity, unitCost }));
  }

  issue(quantity: number, allowNegative: boolean): number {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Issue quantity must be positive");
    if (!allowNegative && this._quantity - quantity < 0) {
      throw new DomainError("BusinessRule", "Insufficient stock");
    }
    this._quantity -= quantity;
    this._lastTransactionAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockIssued.create(this._id.value, { itemId: this._itemId, quantity }));
    return this._unitCost;
  }

  adjust(quantity: number, unitCost: number, reason: string): void {
    if (reason === "") throw new DomainError("BusinessRule", "Adjustment reason required");
    this._quantity = quantity;
    this._unitCost = unitCost;
    this._totalCost = quantity * unitCost;
    this._lastTransactionAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockAdjusted.create(this._id.value, { itemId: this._itemId, quantity, unitCost, reason }));
  }

  transferOut(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Transfer quantity must be positive");
    if (this._quantity - quantity < 0) throw new DomainError("BusinessRule", "Insufficient stock for transfer");
    this._quantity -= quantity;
    this._inTransitQty += quantity;
    this._lastTransactionAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockTransferred.create(this._id.value, { itemId: this._itemId, quantity, direction: "out" }));
  }

  transferIn(quantity: number, unitCost: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Transfer quantity must be positive");
    this._inTransitQty -= quantity;
    this._quantity += quantity;
    this._unitCost = this._quantity > 0
      ? (this._totalCost + quantity * unitCost) / this._quantity
      : unitCost;
    this._totalCost = this._quantity * this._unitCost;
    this._lastTransactionAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockTransferred.create(this._id.value, { itemId: this._itemId, quantity, direction: "in" }));
  }

  reserve(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Reserve quantity must be positive");
    if (this.availableQty < quantity) throw new DomainError("BusinessRule", "Insufficient available stock for reservation");
    this._reservedQty += quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  unreserve(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Unreserve quantity must be positive");
    if (this._reservedQty < quantity) throw new DomainError("BusinessRule", "Cannot unreserve more than reserved");
    this._reservedQty -= quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  allocate(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Allocate quantity must be positive");
    if (this.availableQty < quantity) throw new DomainError("BusinessRule", "Insufficient available stock for allocation");
    this._allocatedQty += quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  unallocate(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Unallocate quantity must be positive");
    if (this._allocatedQty < quantity) throw new DomainError("BusinessRule", "Cannot unallocate more than allocated");
    this._allocatedQty -= quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  setOnOrder(quantity: number): void {
    this._onOrderQty = quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  block(): void {
    this._stockStatus = StockStatus.Blocked;
    this._version++;
    this._updatedAt = new Date();
  }

  release(): void {
    this._stockStatus = StockStatus.Available;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): StockBalanceState {
    return {
      id: this._id.value, itemId: this._itemId, warehouseId: this._warehouseId,
      locationId: this._locationId, lotId: this._lotId,
      stockStatus: this._stockStatus, quantity: this._quantity,
      reservedQty: this._reservedQty, allocatedQty: this._allocatedQty,
      inTransitQty: this._inTransitQty, onOrderQty: this._onOrderQty,
      unitCost: this._unitCost, totalCost: this._totalCost,
      currencyCode: this._currencyCode,
      lastTransactionAt: this._lastTransactionAt,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
