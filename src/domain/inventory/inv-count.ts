import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { StockCountId, CountLineId } from "./inv-ids.js";
import { CountType, CountStatus } from "./inv-enums.js";
import { StockCountCreated, StockCountCompleted, CountVarianceResolved } from "./inv-events.js";

export interface CountLineState {
  id: string;
  countId: string;
  lineNumber: number;
  itemId: string;
  warehouseId: string;
  locationId: string | null;
  lotId: string | null;
  expectedQty: number;
  actualQty: number | null;
  varianceQty: number;
  varianceValue: number;
  unitCost: number;
  isCounted: boolean;
  isApproved: boolean;
  notes: string | null;
  countedById: string | null;
  countedAt: Date | null;
}

export class CountLine {
  constructor(
    private _id: CountLineId,
    private _countId: string,
    private _lineNumber: number,
    private _itemId: string,
    private _warehouseId: string,
    private _expectedQty: number,
    private _unitCost: number,
    private _locationId: string | null = null,
    private _lotId: string | null = null,
    private _actualQty: number | null = null,
    private _isCounted: boolean = false,
    private _isApproved: boolean = false,
    private _notes: string | null = null,
    private _countedById: string | null = null,
    private _countedAt: Date | null = null,
  ) {}

  static create(p: {
    countId: string; lineNumber: number; itemId: string; warehouseId: string;
    expectedQty: number; unitCost: number; locationId?: string; lotId?: string;
  }): CountLine {
    return new CountLine(CountLineId.new(), p.countId, p.lineNumber, p.itemId, p.warehouseId, p.expectedQty, p.unitCost, p.locationId ?? null, p.lotId ?? null);
  }

  static load(s: CountLineState): CountLine {
    return new CountLine(new CountLineId(s.id), s.countId, s.lineNumber, s.itemId, s.warehouseId, s.expectedQty, s.unitCost, s.locationId, s.lotId, s.actualQty, s.isCounted, s.isApproved, s.notes, s.countedById, s.countedAt);
  }

  get id() { return this._id; }
  get itemId() { return this._itemId; }
  get warehouseId() { return this._warehouseId; }
  get locationId() { return this._locationId; }
  get lotId() { return this._lotId; }
  get unitCost() { return this._unitCost; }
  get expectedQty() { return this._expectedQty; }
  get actualQty() { return this._actualQty; }
  get varianceQty() { return (this._actualQty ?? 0) - this._expectedQty; }
  get varianceValue() { return Math.abs(this.varianceQty) * this._unitCost; }
  get isCounted() { return this._isCounted; }
  get isApproved() { return this._isApproved; }

  recordCount(actualQty: number, countedById: string): void {
    if (actualQty < 0) throw new DomainError("BusinessRule", "Counted quantity cannot be negative");
    this._actualQty = actualQty;
    this._isCounted = true;
    this._countedById = countedById;
    this._countedAt = new Date();
  }

  approve(): void {
    if (!this._isCounted) throw new DomainError("BusinessRule", "Cannot approve uncounted line");
    this._isApproved = true;
  }

  toState(): CountLineState {
    return {
      id: this._id.value, countId: this._countId, lineNumber: this._lineNumber,
      itemId: this._itemId, warehouseId: this._warehouseId,
      locationId: this._locationId, lotId: this._lotId,
      expectedQty: this._expectedQty, actualQty: this._actualQty,
      varianceQty: this.varianceQty, varianceValue: this.varianceValue,
      unitCost: this._unitCost, isCounted: this._isCounted,
      isApproved: this._isApproved, notes: this._notes,
      countedById: this._countedById, countedAt: this._countedAt,
    };
  }
}

export interface StockCountState {
  id: string;
  countNumber: string;
  countType: string;
  status: string;
  companyId: string;
  warehouseId: string;
  locationId: string | null;
  countedAt: Date | null;
  frozenAt: Date | null;
  completedAt: Date | null;
  approvedAt: Date | null;
  approvedById: string | null;
  cancelledAt: Date | null;
  cancelReason: string | null;
  notes: string | null;
  lines: CountLineState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class StockCount extends AggregateRoot<StockCountId> {
  private _id: StockCountId;
  private _countNumber: string;
  private _countType: CountType;
  private _status: CountStatus;
  private _companyId: string;
  private _warehouseId: string;
  private _locationId: string | null;
  private _countedAt: Date | null;
  private _frozenAt: Date | null;
  private _completedAt: Date | null;
  private _approvedAt: Date | null;
  private _approvedById: string | null;
  private _cancelledAt: Date | null;
  private _cancelReason: string | null;
  private _notes: string | null;
  private _lines: CountLine[] = [];
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: StockCountId, countNumber: string, countType: CountType, companyId: string, warehouseId: string) {
    super();
    this._id = id;
    this._countNumber = countNumber;
    this._countType = countType;
    this._companyId = companyId;
    this._warehouseId = warehouseId;
    this._status = CountStatus.Planned;
    this._locationId = null;
    this._countedAt = null;
    this._frozenAt = null;
    this._completedAt = null;
    this._approvedAt = null;
    this._approvedById = null;
    this._cancelledAt = null;
    this._cancelReason = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(p: {
    countNumber: string; countType?: CountType; companyId: string;
    warehouseId: string; locationId?: string; notes?: string;
  }): StockCount {
    const sc = new StockCount(StockCountId.new(), p.countNumber, p.countType ?? CountType.Physical, p.companyId, p.warehouseId);
    sc._locationId = p.locationId ?? null;
    sc._notes = p.notes ?? null;
    sc.addEvent(StockCountCreated.create(sc._id.value, {
      countNumber: sc._countNumber, warehouseId: sc._warehouseId,
    }));
    return sc;
  }

  static load(s: StockCountState): StockCount {
    const sc = new StockCount(new StockCountId(s.id), s.countNumber, s.countType as CountType, s.companyId, s.warehouseId);
    sc._status = s.status as CountStatus;
    sc._locationId = s.locationId;
    sc._countedAt = s.countedAt;
    sc._frozenAt = s.frozenAt;
    sc._completedAt = s.completedAt;
    sc._approvedAt = s.approvedAt;
    sc._approvedById = s.approvedById;
    sc._cancelledAt = s.cancelledAt;
    sc._cancelReason = s.cancelReason;
    sc._notes = s.notes;
    sc._lines = s.lines.map(l => CountLine.load(l));
    sc._version = s.version;
    sc._createdAt = s.createdAt;
    sc._updatedAt = s.updatedAt;
    return sc;
  }

  get id() { return this._id; }
  get countNumber() { return this._countNumber; }
  get status() { return this._status; }
  get warehouseId() { return this._warehouseId; }
  get lines() { return [...this._lines]; }
  get version() { return this._version; }

  addLine(line: CountLine): void {
    if (this._status !== CountStatus.Planned) {
      throw new DomainError("BusinessRule", "Cannot add line to non-planned count");
    }
    this._lines.push(line);
    this._version++;
    this._updatedAt = new Date();
  }

  freeze(): void {
    if (this._status !== CountStatus.Planned) throw new DomainError("BusinessRule", "Only planned count can be frozen");
    this._status = CountStatus.Frozen;
    this._frozenAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  startCounting(): void {
    if (this._status !== CountStatus.Frozen) throw new DomainError("BusinessRule", "Count must be frozen first");
    this._status = CountStatus.InProgress;
    this._version++;
    this._updatedAt = new Date();
  }

  complete(): void {
    if (this._status !== CountStatus.InProgress) throw new DomainError("BusinessRule", "Only in-progress count can be completed");
    const uncounted = this._lines.filter(l => !l.isCounted);
    if (uncounted.length > 0) throw new DomainError("BusinessRule", `Cannot complete: ${uncounted.length} uncounted lines`);
    this._status = CountStatus.Completed;
    this._completedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(StockCountCompleted.create(this._id.value, { countNumber: this._countNumber }));
  }

  approve(userId: string): void {
    if (this._status !== CountStatus.Completed) throw new DomainError("BusinessRule", "Only completed count can be approved");
    const unapproved = this._lines.filter(l => !l.isApproved);
    if (unapproved.length > 0) throw new DomainError("BusinessRule", `Cannot approve: ${unapproved.length} unapproved lines`);
    this._status = CountStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CountVarianceResolved.create(this._id.value, { countNumber: this._countNumber }));
  }

  cancel(reason: string): void {
    if (this._status === CountStatus.Approved) throw new DomainError("BusinessRule", "Cannot cancel approved count");
    this._status = CountStatus.Cancelled;
    this._cancelReason = reason;
    this._cancelledAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): StockCountState {
    return {
      id: this._id.value, countNumber: this._countNumber,
      countType: this._countType, status: this._status,
      companyId: this._companyId, warehouseId: this._warehouseId,
      locationId: this._locationId, countedAt: this._countedAt,
      frozenAt: this._frozenAt, completedAt: this._completedAt,
      approvedAt: this._approvedAt, approvedById: this._approvedById,
      cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      notes: this._notes, lines: this._lines.map(l => l.toState()),
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
