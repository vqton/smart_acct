import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BomId, BomLineId, BomRoutingId } from "./cst-ids.js";
import { CstCostElementType } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface BomLineState {
  id: string;
  bomId: string;
  lineNumber: number;
  componentItemId: string;
  componentCode: string;
  componentName: string;
  quantity: number;
  uom: string;
  scrapRate: number;
  yieldRate: number;
  costElement: string;
  unitCost: number;
  extendedCost: number;
  costVersionId: string | null;
  isPhantom: boolean;
  effectivityStart: Date | null;
  effectivityEnd: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class BomLine {
  constructor(
    private _id: BomLineId,
    private _bomId: string,
    private _lineNumber: number,
    private _componentItemId: string,
    private _componentCode: string,
    private _componentName: string,
    private _quantity: number,
    private _uom: string,
    private _scrapRate: number,
    private _yieldRate: number,
    private _costElement: CstCostElementType,
    private _unitCost: number,
    private _extendedCost: number,
    private _costVersionId: string | null,
    private _isPhantom: boolean,
    private _effectivityStart: Date | null,
    private _effectivityEnd: Date | null,
    private _notes: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
  ) {}

  static create(p: {
    bomId: string; lineNumber: number; componentItemId: string;
    componentCode: string; componentName: string; quantity: number;
    uom?: string; scrapRate?: number; yieldRate?: number;
    costElement?: CstCostElementType; unitCost?: number;
    costVersionId?: string | null; isPhantom?: boolean;
    effectivityStart?: Date | null; effectivityEnd?: Date | null; notes?: string | null;
  }): BomLine {
    const q = p.quantity;
    const uc = p.unitCost ?? 0;
    return new BomLine(
      BomLineId.new(), p.bomId, p.lineNumber, p.componentItemId,
      p.componentCode, p.componentName, q,
      p.uom ?? "pc", p.scrapRate ?? 0, p.yieldRate ?? 100,
      p.costElement ?? CstCostElementType.Material, uc, q * uc,
      p.costVersionId ?? null, p.isPhantom ?? false,
      p.effectivityStart ?? null, p.effectivityEnd ?? null,
      p.notes ?? null, 1, new Date(), new Date(),
    );
  }

  static load(s: BomLineState): BomLine {
    return new BomLine(
      new BomLineId(s.id), s.bomId, s.lineNumber, s.componentItemId,
      s.componentCode, s.componentName, s.quantity, s.uom,
      s.scrapRate, s.yieldRate, s.costElement as CstCostElementType,
      s.unitCost, s.extendedCost, s.costVersionId, s.isPhantom,
      s.effectivityStart, s.effectivityEnd, s.notes, s.version,
      s.createdAt, s.updatedAt,
    );
  }

  get id() { return this._id; }
  get componentItemId() { return this._componentItemId; }
  get quantity() { return this._quantity; }
  get unitCost() { return this._unitCost; }
  get extendedCost() { return this._extendedCost; }
  get costElement() { return this._costElement; }
  get isPhantom() { return this._isPhantom; }

  updateCost(unitCost: number): void {
    this._unitCost = unitCost;
    this._extendedCost = this._quantity * unitCost;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): BomLineState {
    return {
      id: this._id.value, bomId: this._bomId, lineNumber: this._lineNumber,
      componentItemId: this._componentItemId, componentCode: this._componentCode,
      componentName: this._componentName, quantity: this._quantity,
      uom: this._uom, scrapRate: this._scrapRate, yieldRate: this._yieldRate,
      costElement: this._costElement, unitCost: this._unitCost,
      extendedCost: this._extendedCost, costVersionId: this._costVersionId,
      isPhantom: this._isPhantom, effectivityStart: this._effectivityStart,
      effectivityEnd: this._effectivityEnd, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}

export interface BomRoutingState {
  id: string;
  bomId: string;
  operationSeq: number;
  workCenterId: string | null;
  operationDescription: string;
  setupTime: number;
  runTime: number;
  queueTime: number;
  moveTime: number;
  laborCount: number;
  machineCount: number;
  laborRate: number;
  machineRate: number;
  overheadRate: number;
  setupCost: number;
  laborCost: number;
  machineCost: number;
  overheadCost: number;
  totalCost: number;
  costVersionId: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class BomRouting {
  constructor(
    private _id: BomRoutingId,
    private _bomId: string,
    private _operationSeq: number,
    private _workCenterId: string | null,
    private _operationDescription: string,
    private _setupTime: number,
    private _runTime: number,
    private _queueTime: number,
    private _moveTime: number,
    private _laborCount: number,
    private _machineCount: number,
    private _laborRate: number,
    private _machineRate: number,
    private _overheadRate: number,
    private _setupCost: number,
    private _laborCost: number,
    private _machineCost: number,
    private _overheadCost: number,
    private _totalCost: number,
    private _costVersionId: string | null,
    private _notes: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
  ) {}

  static create(p: {
    bomId: string; operationSeq: number; operationDescription: string;
    workCenterId?: string | null; setupTime?: number; runTime?: number;
    queueTime?: number; moveTime?: number; laborCount?: number; machineCount?: number;
    laborRate?: number; machineRate?: number; overheadRate?: number;
    costVersionId?: string | null; notes?: string | null;
  }): BomRouting {
    const st = p.setupTime ?? 0;
    const rt = p.runTime ?? 0;
    const lr = p.laborRate ?? 0;
    const mr = p.machineRate ?? 0;
    const or = p.overheadRate ?? 0;
    const lc = p.laborCount ?? 1;
    const mc = p.machineCount ?? 1;
    const setupCost = st * lr;
    const laborCost = rt * lr * lc;
    const machineCost = rt * mr * mc;
    const overheadCost = rt * or;
    const totalCost = setupCost + laborCost + machineCost + overheadCost;

    return new BomRouting(
      BomRoutingId.new(), p.bomId, p.operationSeq, p.workCenterId ?? null,
      p.operationDescription, st, rt, p.queueTime ?? 0, p.moveTime ?? 0,
      lc, mc, lr, mr, or, setupCost, laborCost, machineCost, overheadCost,
      totalCost, p.costVersionId ?? null, p.notes ?? null,
      1, new Date(), new Date(),
    );
  }

  static load(s: BomRoutingState): BomRouting {
    return new BomRouting(
      new BomRoutingId(s.id), s.bomId, s.operationSeq, s.workCenterId,
      s.operationDescription, s.setupTime, s.runTime, s.queueTime, s.moveTime,
      s.laborCount, s.machineCount, s.laborRate, s.machineRate, s.overheadRate,
      s.setupCost, s.laborCost, s.machineCost, s.overheadCost, s.totalCost,
      s.costVersionId, s.notes, s.version, s.createdAt, s.updatedAt,
    );
  }

  get id() { return this._id; }
  get operationSeq() { return this._operationSeq; }
  get totalCost() { return this._totalCost; }

  toState(): BomRoutingState {
    return {
      id: this._id.value, bomId: this._bomId, operationSeq: this._operationSeq,
      workCenterId: this._workCenterId,
      operationDescription: this._operationDescription,
      setupTime: this._setupTime, runTime: this._runTime,
      queueTime: this._queueTime, moveTime: this._moveTime,
      laborCount: this._laborCount, machineCount: this._machineCount,
      laborRate: this._laborRate, machineRate: this._machineRate,
      overheadRate: this._overheadRate, setupCost: this._setupCost,
      laborCost: this._laborCost, machineCost: this._machineCost,
      overheadCost: this._overheadCost, totalCost: this._totalCost,
      costVersionId: this._costVersionId, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}

export interface BomState {
  id: string;
  code: string;
  name: string;
  itemId: string;
  itemCode: string;
  itemName: string;
  bomType: string;
  quantity: number;
  uom: string;
  scrapRate: number;
  yieldRate: number;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  isActive: boolean;
  isDefault: boolean;
  revision: number;
  description: string | null;
  lines: BomLineState[];
  routings: BomRoutingState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Bom extends AggregateRoot<BomId> {
  private _lines: BomLine[] = [];
  private _routings: BomRouting[] = [];

  private constructor(
    private _id: BomId,
    private _code: string,
    private _name: string,
    private _itemId: string,
    private _itemCode: string,
    private _itemName: string,
    private _bomType: string,
    private _quantity: number,
    private _uom: string,
    private _scrapRate: number,
    private _yieldRate: number,
    private _effectiveFrom: Date,
    private _effectiveTo: Date | null,
    private _isActive: boolean,
    private _isDefault: boolean,
    private _revision: number,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; itemId: string; itemCode: string; itemName: string;
    bomType?: string; quantity?: number; uom?: string;
    scrapRate?: number; yieldRate?: number; effectiveFrom?: Date;
    effectiveTo?: Date | null; isDefault?: boolean; description?: string | null;
  }): Bom {
    const bom = new Bom(
      BomId.new(), p.code, p.name, p.itemId, p.itemCode, p.itemName,
      p.bomType ?? "manufacturing", p.quantity ?? 1, p.uom ?? "pc",
      p.scrapRate ?? 0, p.yieldRate ?? 100, p.effectiveFrom ?? new Date(),
      p.effectiveTo ?? null, true, p.isDefault ?? false, 0,
      p.description ?? null, 1, new Date(), new Date(), null,
    );
    bom.addEvent(CostingEvents.BomCreated(bom._id.value, { code: p.code, itemId: p.itemId }));
    return bom;
  }

  static load(s: BomState): Bom {
    const bom = new Bom(
      new BomId(s.id), s.code, s.name, s.itemId, s.itemCode, s.itemName,
      s.bomType, s.quantity, s.uom, s.scrapRate, s.yieldRate,
      s.effectiveFrom, s.effectiveTo, s.isActive, s.isDefault, s.revision,
      s.description, s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
    bom._lines = s.lines.map(l => BomLine.load(l));
    bom._routings = s.routings.map(r => BomRouting.load(r));
    return bom;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get itemId() { return this._itemId; }
  get lines() { return [...this._lines]; }
  get routings() { return [...this._routings]; }
  get revision() { return this._revision; }
  get version() { return this._version; }

  addLine(line: BomLine): void {
    this._lines.push(line);
    this._version++;
    this._updatedAt = new Date();
  }

  addRouting(routing: BomRouting): void {
    this._routings.push(routing);
    this._version++;
    this._updatedAt = new Date();
  }

  revise(): void {
    this._revision++;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.BomRevised(this._id.value, { code: this._code, revision: this._revision }));
  }

  totalMaterialCost(): number {
    return this._lines.reduce((s, l) => s + l.extendedCost, 0);
  }

  totalRoutingCost(): number {
    return this._routings.reduce((s, r) => s + r.totalCost, 0);
  }

  totalCost(): number {
    return this.totalMaterialCost() + this.totalRoutingCost();
  }

  toState(): BomState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      bomType: this._bomType, quantity: this._quantity, uom: this._uom,
      scrapRate: this._scrapRate, yieldRate: this._yieldRate,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      isActive: this._isActive, isDefault: this._isDefault, revision: this._revision,
      description: this._description, lines: this._lines.map(l => l.toState()),
      routings: this._routings.map(r => r.toState()),
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
