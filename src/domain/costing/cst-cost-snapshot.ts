import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CostSnapshotId } from "./cst-ids.js";
import { CstCostSnapshotType, CstCostMethod } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface CostSnapshotLineState {
  id: string;
  snapshotId: string;
  itemId: string;
  itemCode: string;
  itemName: string;
  warehouseId: string | null;
  uom: string;
  quantity: number;
  unitCost: number;
  totalCost: number;
  previousCost: number;
  costChange: number;
  currencyCode: string;
  costMethod: string;
  version: number;
}

export class CostSnapshotLine {
  constructor(
    private _id: string,
    private _snapshotId: string,
    private _itemId: string,
    private _itemCode: string,
    private _itemName: string,
    private _warehouseId: string | null,
    private _uom: string,
    private _quantity: number,
    private _unitCost: number,
    private _totalCost: number,
    private _previousCost: number,
    private _costChange: number,
    private _currencyCode: string,
    private _costMethod: CstCostMethod,
    private _version: number,
  ) {}

  static create(p: {
    snapshotId: string; itemId: string; itemCode: string; itemName: string;
    warehouseId?: string | null; uom?: string; quantity: number;
    unitCost: number; previousCost?: number; currencyCode?: string;
    costMethod?: CstCostMethod;
  }): CostSnapshotLine {
    const prev = p.previousCost ?? 0;
    return new CostSnapshotLine(
      crypto.randomUUID(), p.snapshotId, p.itemId, p.itemCode, p.itemName,
      p.warehouseId ?? null, p.uom ?? "pc", p.quantity, p.unitCost,
      p.quantity * p.unitCost, prev, (p.unitCost - prev) * p.quantity,
      p.currencyCode ?? "VND", p.costMethod ?? CstCostMethod.Standard, 1,
    );
  }

  static load(s: CostSnapshotLineState): CostSnapshotLine {
    return new CostSnapshotLine(
      s.id, s.snapshotId, s.itemId, s.itemCode, s.itemName,
      s.warehouseId, s.uom, s.quantity, s.unitCost, s.totalCost,
      s.previousCost, s.costChange, s.currencyCode,
      s.costMethod as CstCostMethod, s.version,
    );
  }

  get totalCost() { return this._totalCost; }
  get quantity() { return this._quantity; }

  toState(): CostSnapshotLineState {
    return {
      id: this._id, snapshotId: this._snapshotId,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      warehouseId: this._warehouseId, uom: this._uom,
      quantity: this._quantity, unitCost: this._unitCost,
      totalCost: this._totalCost, previousCost: this._previousCost,
      costChange: this._costChange, currencyCode: this._currencyCode,
      costMethod: this._costMethod, version: this._version,
    };
  }
}

export interface CostSnapshotState {
  id: string;
  snapshotNumber: string;
  snapshotType: string;
  periodId: string | null;
  fiscalYearId: string | null;
  snapshotDate: Date;
  itemCount: number;
  totalCost: number;
  totalQuantity: number;
  currencyCode: string;
  isFrozen: boolean;
  frozenAt: Date | null;
  frozenById: string | null;
  notes: string | null;
  createdById: string | null;
  lines: CostSnapshotLineState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CostSnapshot extends AggregateRoot<CostSnapshotId> {
  private _lines: CostSnapshotLine[] = [];

  private constructor(
    private _id: CostSnapshotId,
    private _snapshotNumber: string,
    private _snapshotType: CstCostSnapshotType,
    private _periodId: string | null,
    private _fiscalYearId: string | null,
    private _snapshotDate: Date,
    private _itemCount: number,
    private _totalCost: number,
    private _totalQuantity: number,
    private _currencyCode: string,
    private _isFrozen: boolean,
    private _frozenAt: Date | null,
    private _frozenById: string | null,
    private _notes: string | null,
    private _createdById: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    snapshotNumber: string; snapshotType: CstCostSnapshotType;
    periodId?: string | null; fiscalYearId?: string | null;
    snapshotDate?: Date; currencyCode?: string;
    notes?: string | null; createdById?: string | null;
  }): CostSnapshot {
    const cs = new CostSnapshot(
      CostSnapshotId.new(), p.snapshotNumber, p.snapshotType,
      p.periodId ?? null, p.fiscalYearId ?? null,
      p.snapshotDate ?? new Date(), 0, 0, 0,
      p.currencyCode ?? "VND", false, null, null,
      p.notes ?? null, p.createdById ?? null,
      1, new Date(), new Date(), null,
    );
    cs.addEvent(CostingEvents.CostSnapshotCreated(cs._id.value, {
      snapshotNumber: p.snapshotNumber, snapshotType: p.snapshotType,
    }));
    return cs;
  }

  static load(s: CostSnapshotState): CostSnapshot {
    const cs = new CostSnapshot(
      new CostSnapshotId(s.id), s.snapshotNumber,
      s.snapshotType as CstCostSnapshotType,
      s.periodId, s.fiscalYearId, s.snapshotDate,
      s.itemCount, s.totalCost, s.totalQuantity,
      s.currencyCode, s.isFrozen, s.frozenAt, s.frozenById,
      s.notes, s.createdById, s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
    cs._lines = s.lines.map(l => CostSnapshotLine.load(l));
    return cs;
  }

  get id() { return this._id; }
  get snapshotNumber() { return this._snapshotNumber; }
  get isFrozen() { return this._isFrozen; }
  get lines() { return [...this._lines]; }
  get totalCost() { return this._totalCost; }
  get totalQuantity() { return this._totalQuantity; }
  get version() { return this._version; }

  addLine(line: CostSnapshotLine): void {
    this._lines.push(line);
    this._itemCount = this._lines.length;
    this._totalCost += line.totalCost;
    this._totalQuantity += line.quantity;
    this._version++;
    this._updatedAt = new Date();
  }

  freeze(userId: string): void {
    if (this._isFrozen) throw new DomainError("BusinessRule", "Snapshot already frozen");
    this._isFrozen = true;
    this._frozenAt = new Date();
    this._frozenById = userId;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.CostSnapshotFrozen(this._id.value, { snapshotNumber: this._snapshotNumber }));
  }

  toState(): CostSnapshotState {
    return {
      id: this._id.value, snapshotNumber: this._snapshotNumber,
      snapshotType: this._snapshotType, periodId: this._periodId,
      fiscalYearId: this._fiscalYearId, snapshotDate: this._snapshotDate,
      itemCount: this._itemCount, totalCost: this._totalCost,
      totalQuantity: this._totalQuantity, currencyCode: this._currencyCode,
      isFrozen: this._isFrozen, frozenAt: this._frozenAt,
      frozenById: this._frozenById, notes: this._notes,
      createdById: this._createdById,
      lines: this._lines.map(l => l.toState()),
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
