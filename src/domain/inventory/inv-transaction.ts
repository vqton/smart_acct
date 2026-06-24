import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { InventoryTransactionId, TransactionLineId } from "./inv-ids.js";
import { InventoryTransactionType, InventoryTransactionStatus, MovementStatus } from "./inv-enums.js";
import { InventoryTransactionCreated, InventoryTransactionPosted, InventoryTransactionReversed } from "./inv-events.js";

export interface TransactionLineState {
  id: string;
  transactionId: string;
  lineNumber: number;
  itemId: string;
  warehouseId: string;
  locationId: string | null;
  lotId: string | null;
  serialNumber: string | null;
  quantity: number;
  unitCost: number;
  totalCost: number;
  currencyCode: string;
  exchangeRate: number;
  referenceType: string | null;
  referenceId: string | null;
  description: string | null;
}

export class TransactionLine {
  constructor(
    private _id: TransactionLineId,
    private _transactionId: string,
    private _lineNumber: number,
    private _itemId: string,
    private _warehouseId: string,
    private _quantity: number,
    private _unitCost: number,
    private _totalCost: number,
    private _currencyCode: string,
    private _exchangeRate: number,
    private _locationId: string | null = null,
    private _lotId: string | null = null,
    private _serialNumber: string | null = null,
    private _referenceType: string | null = null,
    private _referenceId: string | null = null,
    private _description: string | null = null,
  ) {}

  static create(p: {
    transactionId: string; lineNumber: number; itemId: string; warehouseId: string;
    quantity: number; unitCost: number; totalCost: number;
    currencyCode?: string; exchangeRate?: number;
    locationId?: string | null; lotId?: string | null; serialNumber?: string | null;
    referenceType?: string | null; referenceId?: string | null; description?: string | null;
  }): TransactionLine {
    return new TransactionLine(
      TransactionLineId.new(), p.transactionId, p.lineNumber, p.itemId,
      p.warehouseId, p.quantity, p.unitCost, p.totalCost,
      p.currencyCode ?? "VND", p.exchangeRate ?? 1,
      p.locationId ?? null, p.lotId ?? null, p.serialNumber ?? null,
      p.referenceType ?? null, p.referenceId ?? null, p.description ?? null,
    );
  }

  static load(s: TransactionLineState): TransactionLine {
    return new TransactionLine(
      new TransactionLineId(s.id), s.transactionId, s.lineNumber,
      s.itemId, s.warehouseId, s.quantity, s.unitCost, s.totalCost,
      s.currencyCode, s.exchangeRate, s.locationId, s.lotId,
      s.serialNumber, s.referenceType, s.referenceId, s.description,
    );
  }

  get id() { return this._id; }
  get itemId() { return this._itemId; }
  get warehouseId() { return this._warehouseId; }
  get locationId() { return this._locationId; }
  get lotId() { return this._lotId; }
  get quantity() { return this._quantity; }
  get unitCost() { return this._unitCost; }
  get totalCost() { return this._totalCost; }
  get lineNumber() { return this._lineNumber; }

  toState(): TransactionLineState {
    return {
      id: this._id.value, transactionId: this._transactionId,
      lineNumber: this._lineNumber, itemId: this._itemId,
      warehouseId: this._warehouseId, locationId: this._locationId,
      lotId: this._lotId, serialNumber: this._serialNumber,
      quantity: this._quantity, unitCost: this._unitCost,
      totalCost: this._totalCost, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, referenceType: this._referenceType,
      referenceId: this._referenceId, description: this._description,
    };
  }
}

export interface InventoryTransactionState {
  id: string;
  transactionNumber: string;
  transactionType: string;
  status: string;
  companyId: string;
  branchId: string | null;
  warehouseId: string;
  transactionDate: Date;
  postingDate: Date;
  currencyCode: string;
  exchangeRate: number;
  totalQuantity: number;
  totalAmount: number;
  description: string | null;
  referenceType: string | null;
  referenceId: string | null;
  sourceDocumentType: string | null;
  sourceDocumentId: string | null;
  createdById: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  postedById: string | null;
  postedAt: Date | null;
  reversedById: string | null;
  reversedAt: Date | null;
  reverseOfId: string | null;
  cancelledById: string | null;
  cancelledAt: Date | null;
  cancelReason: string | null;
  lines: TransactionLineState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class InventoryTransaction extends AggregateRoot<InventoryTransactionId> {
  private _id: InventoryTransactionId;
  private _transactionNumber: string;
  private _transactionType: InventoryTransactionType;
  private _status: InventoryTransactionStatus;
  private _companyId: string;
  private _branchId: string | null;
  private _warehouseId: string;
  private _transactionDate: Date;
  private _postingDate: Date;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _totalQuantity: number;
  private _totalAmount: number;
  private _description: string | null;
  private _referenceType: string | null;
  private _referenceId: string | null;
  private _sourceDocumentType: string | null;
  private _sourceDocumentId: string | null;
  private _createdById: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _postedById: string | null;
  private _postedAt: Date | null;
  private _reversedById: string | null;
  private _reversedAt: Date | null;
  private _reverseOfId: string | null;
  private _cancelledById: string | null;
  private _cancelledAt: Date | null;
  private _cancelReason: string | null;
  private _lines: TransactionLine[] = [];
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: InventoryTransactionId, transactionNumber: string, transactionType: InventoryTransactionType, companyId: string, warehouseId: string) {
    super();
    this._id = id;
    this._transactionNumber = transactionNumber;
    this._transactionType = transactionType;
    this._companyId = companyId;
    this._warehouseId = warehouseId;
    this._status = InventoryTransactionStatus.Draft;
    this._branchId = null;
    this._transactionDate = new Date();
    this._postingDate = new Date();
    this._currencyCode = "VND";
    this._exchangeRate = 1;
    this._totalQuantity = 0;
    this._totalAmount = 0;
    this._description = null;
    this._referenceType = null;
    this._referenceId = null;
    this._sourceDocumentType = null;
    this._sourceDocumentId = null;
    this._createdById = null;
    this._approvedById = null;
    this._approvedAt = null;
    this._postedById = null;
    this._postedAt = null;
    this._reversedById = null;
    this._reversedAt = null;
    this._reverseOfId = null;
    this._cancelledById = null;
    this._cancelledAt = null;
    this._cancelReason = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(p: {
    transactionNumber: string; transactionType: InventoryTransactionType;
    companyId: string; warehouseId: string; branchId?: string | null;
    transactionDate?: Date; postingDate?: Date; description?: string | null;
    currencyCode?: string; exchangeRate?: number;
    referenceType?: string | null; referenceId?: string | null;
    sourceDocumentType?: string | null; sourceDocumentId?: string | null;
    createdById?: string | null;
  }): InventoryTransaction {
    const t = new InventoryTransaction(
      InventoryTransactionId.new(), p.transactionNumber, p.transactionType,
      p.companyId, p.warehouseId,
    );
    t._branchId = p.branchId ?? null;
    t._transactionDate = p.transactionDate ?? new Date();
    t._postingDate = p.postingDate ?? new Date();
    t._description = p.description ?? null;
    t._currencyCode = p.currencyCode ?? "VND";
    t._exchangeRate = p.exchangeRate ?? 1;
    t._referenceType = p.referenceType ?? null;
    t._referenceId = p.referenceId ?? null;
    t._sourceDocumentType = p.sourceDocumentType ?? null;
    t._sourceDocumentId = p.sourceDocumentId ?? null;
    t._createdById = p.createdById ?? null;
    t.addEvent(InventoryTransactionCreated.create(t._id.value, {
      transactionNumber: t._transactionNumber,
      transactionType: t._transactionType,
    }));
    return t;
  }

  static load(s: InventoryTransactionState): InventoryTransaction {
    const t = new InventoryTransaction(
      new InventoryTransactionId(s.id), s.transactionNumber,
      s.transactionType as InventoryTransactionType, s.companyId, s.warehouseId,
    );
    t._status = s.status as InventoryTransactionStatus;
    t._branchId = s.branchId;
    t._transactionDate = s.transactionDate;
    t._postingDate = s.postingDate;
    t._currencyCode = s.currencyCode;
    t._exchangeRate = s.exchangeRate;
    t._totalQuantity = s.totalQuantity;
    t._totalAmount = s.totalAmount;
    t._description = s.description;
    t._referenceType = s.referenceType;
    t._referenceId = s.referenceId;
    t._sourceDocumentType = s.sourceDocumentType;
    t._sourceDocumentId = s.sourceDocumentId;
    t._createdById = s.createdById;
    t._approvedById = s.approvedById;
    t._approvedAt = s.approvedAt;
    t._postedById = s.postedById;
    t._postedAt = s.postedAt;
    t._reversedById = s.reversedById;
    t._reversedAt = s.reversedAt;
    t._reverseOfId = s.reverseOfId;
    t._cancelledById = s.cancelledById;
    t._cancelledAt = s.cancelledAt;
    t._cancelReason = s.cancelReason;
    t._lines = s.lines.map(l => TransactionLine.load(l));
    t._version = s.version;
    t._createdAt = s.createdAt;
    t._updatedAt = s.updatedAt;
    return t;
  }

  get id() { return this._id; }
  get transactionNumber() { return this._transactionNumber; }
  get transactionType() { return this._transactionType; }
  get status() { return this._status; }
  get warehouseId() { return this._warehouseId; }
  get lines() { return [...this._lines]; }
  get version() { return this._version; }

  addLine(line: TransactionLine): void {
    if (this._status !== InventoryTransactionStatus.Draft) {
      throw new DomainError("BusinessRule", "Cannot add line to non-draft transaction");
    }
    this._lines.push(line);
    this._totalQuantity += line.quantity;
    this._totalAmount += line.totalCost;
    this._version++;
    this._updatedAt = new Date();
  }

  submit(userId: string): void {
    if (this._status !== InventoryTransactionStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft transactions can be submitted");
    }
    if (this._lines.length === 0) {
      throw new DomainError("BusinessRule", "Cannot submit empty transaction");
    }
    this._status = InventoryTransactionStatus.Submitted;
    this._createdById = userId;
    this._version++;
    this._updatedAt = new Date();
  }

  approve(userId: string): void {
    if (this._status !== InventoryTransactionStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only submitted transactions can be approved");
    }
    this._status = InventoryTransactionStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  post(userId: string): void {
    if (this._status !== InventoryTransactionStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved transactions can be posted");
    }
    this._status = InventoryTransactionStatus.Posted;
    this._postedById = userId;
    this._postedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(InventoryTransactionPosted.create(this._id.value, {
      transactionNumber: this._transactionNumber,
      transactionType: this._transactionType,
    }));
  }

  reverse(userId: string, reason: string): InventoryTransaction {
    if (this._status !== InventoryTransactionStatus.Posted) {
      throw new DomainError("BusinessRule", "Only posted transactions can be reversed");
    }
    if (!reason) throw new DomainError("BusinessRule", "Reversal requires a reason");
    this._status = InventoryTransactionStatus.Reversed;
    this._reversedById = userId;
    this._reversedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(InventoryTransactionReversed.create(this._id.value, {
      transactionNumber: this._transactionNumber,
      reason,
    }));
    // Return a reversal transaction
    const rev = InventoryTransaction.create({
      transactionNumber: `REV-${this._transactionNumber}`,
      transactionType: InventoryTransactionType.Reversal,
      companyId: this._companyId,
      warehouseId: this._warehouseId,
      branchId: this._branchId,
      referenceType: "REVERSAL",
      referenceId: this._id.value,
      description: `Reversal of ${this._transactionNumber}: ${reason}`,
      createdById: userId,
    });
    for (const line of this._lines) {
      rev.addLine(TransactionLine.create({
        transactionId: rev._id.value,
        lineNumber: line.lineNumber,
        itemId: line.itemId,
        warehouseId: line.warehouseId,
        quantity: -line.quantity,
        unitCost: line.unitCost,
        totalCost: -line.totalCost,
        locationId: line.locationId,
        lotId: line.lotId,
        referenceType: "REVERSAL",
        referenceId: line.id.value,
        description: `Reversal of ${this._transactionNumber}`,
      }));
    }
    return rev;
  }

  cancel(userId: string, reason: string): void {
    if (this._status === InventoryTransactionStatus.Posted ||
        this._status === InventoryTransactionStatus.Reversed) {
      throw new DomainError("BusinessRule", "Cannot cancel posted or reversed transaction");
    }
    this._status = InventoryTransactionStatus.Cancelled;
    this._cancelledById = userId;
    this._cancelledAt = new Date();
    this._cancelReason = reason;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): InventoryTransactionState {
    return {
      id: this._id.value, transactionNumber: this._transactionNumber,
      transactionType: this._transactionType, status: this._status,
      companyId: this._companyId, branchId: this._branchId,
      warehouseId: this._warehouseId,
      transactionDate: this._transactionDate, postingDate: this._postingDate,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      totalQuantity: this._totalQuantity, totalAmount: this._totalAmount,
      description: this._description, referenceType: this._referenceType,
      referenceId: this._referenceId, sourceDocumentType: this._sourceDocumentType,
      sourceDocumentId: this._sourceDocumentId, createdById: this._createdById,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      postedById: this._postedById, postedAt: this._postedAt,
      reversedById: this._reversedById, reversedAt: this._reversedAt,
      reverseOfId: this._reverseOfId, cancelledById: this._cancelledById,
      cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      lines: this._lines.map(l => l.toState()),
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
