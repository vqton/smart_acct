import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CostLayerId } from "./inv-ids.js";
import { CostMethod } from "./inv-enums.js";
import { CostLayerCreated, CostLayerConsumed } from "./inv-events.js";

export interface CostLayerState {
  id: string;
  itemId: string;
  warehouseId: string;
  lotId: string | null;
  costMethod: string;
  quantity: number;
  unitCost: number;
  totalCost: number;
  remainingQty: number;
  remainingCost: number;
  receivedAt: Date;
  transactionId: string;
  transactionLineId: string | null;
  isConsumed: boolean;
  consumedAt: Date | null;
  consumedByTransactionId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class CostLayer extends AggregateRoot<CostLayerId> {
  private _id: CostLayerId;
  private _itemId: string;
  private _warehouseId: string;
  private _lotId: string | null;
  private _costMethod: CostMethod;
  private _quantity: number;
  private _unitCost: number;
  private _totalCost: number;
  private _remainingQty: number;
  private _remainingCost: number;
  private _receivedAt: Date;
  private _transactionId: string;
  private _transactionLineId: string | null;
  private _isConsumed: boolean;
  private _consumedAt: Date | null;
  private _consumedByTransactionId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: CostLayerId, itemId: string, warehouseId: string, transactionId: string) {
    super();
    this._id = id;
    this._itemId = itemId;
    this._warehouseId = warehouseId;
    this._lotId = null;
    this._costMethod = CostMethod.FIFO;
    this._quantity = 0;
    this._unitCost = 0;
    this._totalCost = 0;
    this._remainingQty = 0;
    this._remainingCost = 0;
    this._receivedAt = new Date();
    this._transactionId = transactionId;
    this._transactionLineId = null;
    this._isConsumed = false;
    this._consumedAt = null;
    this._consumedByTransactionId = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(p: {
    itemId: string; warehouseId: string; quantity: number; unitCost: number;
    transactionId: string; transactionLineId?: string | null; lotId?: string | null;
    costMethod?: CostMethod; receivedAt?: Date;
  }): CostLayer {
    if (p.quantity <= 0) throw new DomainError("BusinessRule", "Layer quantity must be positive");
    if (p.unitCost < 0) throw new DomainError("BusinessRule", "Unit cost cannot be negative");
    const cl = new CostLayer(CostLayerId.new(), p.itemId, p.warehouseId, p.transactionId);
    cl._quantity = p.quantity;
    cl._unitCost = p.unitCost;
    cl._totalCost = p.quantity * p.unitCost;
    cl._remainingQty = p.quantity;
    cl._remainingCost = cl._totalCost;
    cl._lotId = p.lotId ?? null;
    cl._costMethod = p.costMethod ?? CostMethod.FIFO;
    cl._receivedAt = p.receivedAt ?? new Date();
    cl._transactionLineId = p.transactionLineId ?? null;
    cl.addEvent(CostLayerCreated.create(cl._id.value, {
      itemId: p.itemId, quantity: p.quantity, unitCost: p.unitCost,
    }));
    return cl;
  }

  static load(s: CostLayerState): CostLayer {
    const cl = new CostLayer(new CostLayerId(s.id), s.itemId, s.warehouseId, s.transactionId);
    cl._lotId = s.lotId;
    cl._costMethod = s.costMethod as CostMethod;
    cl._quantity = s.quantity;
    cl._unitCost = s.unitCost;
    cl._totalCost = s.totalCost;
    cl._remainingQty = s.remainingQty;
    cl._remainingCost = s.remainingCost;
    cl._receivedAt = s.receivedAt;
    cl._transactionLineId = s.transactionLineId;
    cl._isConsumed = s.isConsumed;
    cl._consumedAt = s.consumedAt;
    cl._consumedByTransactionId = s.consumedByTransactionId;
    cl._version = s.version;
    cl._createdAt = s.createdAt;
    cl._updatedAt = s.updatedAt;
    return cl;
  }

  get id() { return this._id; }
  get itemId() { return this._itemId; }
  get warehouseId() { return this._warehouseId; }
  get lotId() { return this._lotId; }
  get unitCost() { return this._unitCost; }
  get remainingQty() { return this._remainingQty; }
  get remainingCost() { return this._remainingCost; }
  get isConsumed() { return this._isConsumed; }
  get version() { return this._version; }

  consume(quantity: number, transactionId: string): number {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Consume quantity must be positive");
    if (quantity > this._remainingQty) throw new DomainError("BusinessRule", "Cannot consume more than remaining layer quantity");
    const cost = quantity * this._unitCost;
    this._remainingQty -= quantity;
    this._remainingCost -= cost;
    if (this._remainingQty <= 0) {
      this._isConsumed = true;
      this._consumedAt = new Date();
      this._consumedByTransactionId = transactionId;
    }
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostLayerConsumed.create(this._id.value, {
      itemId: this._itemId, quantity, unitCost: this._unitCost, totalCost: cost,
    }));
    return cost;
  }

  split(quantity: number): CostLayer {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Split quantity must be positive");
    if (quantity >= this._remainingQty) throw new DomainError("BusinessRule", "Split quantity must be less than remaining");
    const newLayer = CostLayer.create({
      itemId: this._itemId, warehouseId: this._warehouseId,
      quantity, unitCost: this._unitCost,
      transactionId: this._transactionId,
      transactionLineId: this._transactionLineId,
      lotId: this._lotId, costMethod: this._costMethod,
      receivedAt: this._receivedAt,
    });
    this._remainingQty -= quantity;
    this._remainingCost -= quantity * this._unitCost;
    this._version++;
    this._updatedAt = new Date();
    return newLayer;
  }

  toState(): CostLayerState {
    return {
      id: this._id.value, itemId: this._itemId, warehouseId: this._warehouseId,
      lotId: this._lotId, costMethod: this._costMethod,
      quantity: this._quantity, unitCost: this._unitCost,
      totalCost: this._totalCost, remainingQty: this._remainingQty,
      remainingCost: this._remainingCost, receivedAt: this._receivedAt,
      transactionId: this._transactionId,
      transactionLineId: this._transactionLineId,
      isConsumed: this._isConsumed, consumedAt: this._consumedAt,
      consumedByTransactionId: this._consumedByTransactionId,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
