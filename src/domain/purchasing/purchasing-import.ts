import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ImportDeclarationId, ShipmentId, ContainerId, LandedCostId } from "./purchasing-ids.js";
import { ImportStatus, Incoterm, FreightTerm, LandedCostType, ShipmentStatus } from "./purchasing-enums.js";
import { ImportDeclarationCreated, LandedCostPosted } from "./purchasing-events.js";

// ─── Landed Cost ─────────────────────────────────────────────────────────────────

export interface LandedCostState {
  id: string; importDeclarationId: string; costType: string;
  description: string; amount: number; currencyCode: string;
  allocationBasis: string; postedToInventory: boolean;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class LandedCost extends AggregateRoot<LandedCostId> {
  private _id: LandedCostId; private _importDeclarationId: string;
  private _costType: LandedCostType; private _description: string;
  private _amount: number; private _currencyCode: string;
  private _allocationBasis: string; private _postedToInventory: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: LandedCostId, importDeclarationId: string, costType: LandedCostType, description: string, amount: number) {
    super(); this._id = id; this._importDeclarationId = importDeclarationId;
    this._costType = costType; this._description = description; this._amount = amount;
    this._currencyCode = "VND"; this._allocationBasis = "value"; this._postedToInventory = false;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { importDeclarationId: string; costType: LandedCostType; description: string; amount: number; currencyCode?: string; allocationBasis?: string }): LandedCost {
    const l = new LandedCost(LandedCostId.new(), p.importDeclarationId, p.costType, p.description, p.amount);
    l._currencyCode = p.currencyCode ?? "VND"; l._allocationBasis = p.allocationBasis ?? "value";
    return l;
  }

  static load(s: LandedCostState): LandedCost {
    const l = new LandedCost(new LandedCostId(s.id), s.importDeclarationId, s.costType as LandedCostType, s.description, s.amount);
    l._currencyCode = s.currencyCode; l._allocationBasis = s.allocationBasis;
    l._postedToInventory = s.postedToInventory;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): LandedCostId { return this._id; }
  get amount(): number { return this._amount; }
  get postedToInventory(): boolean { return this._postedToInventory; }
  get version(): number { return this._version; }

  markPosted(): void {
    this._postedToInventory = true;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): LandedCostState {
    return { id: this._id.value, importDeclarationId: this._importDeclarationId,
      costType: this._costType, description: this._description, amount: this._amount,
      currencyCode: this._currencyCode, allocationBasis: this._allocationBasis,
      postedToInventory: this._postedToInventory, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Import Declaration ──────────────────────────────────────────────────────────

export interface ImportDeclarationState {
  id: string; declarationNumber: string; companyId: string; branchId: string | null;
  poId: string; poNumber: string; vendorId: string; vendorName: string;
  shipmentId: string | null; status: string;
  incoterm: string; freightTerm: string;
  portOfLoading: string | null; portOfDischarge: string | null;
  currencyCode: string; exchangeRate: number;
  totalCifValue: number; totalDutyAmount: number; totalTaxAmount: number;
  totalLandedCost: number; customsClearanceDate: Date | null;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class ImportDeclaration extends AggregateRoot<ImportDeclarationId> {
  private _id: ImportDeclarationId; private _declarationNumber: string; private _companyId: string;
  private _branchId: string | null; private _poId: string; private _poNumber: string;
  private _vendorId: string; private _vendorName: string; private _shipmentId: string | null;
  private _status: ImportStatus; private _incoterm: Incoterm; private _freightTerm: FreightTerm;
  private _portOfLoading: string | null; private _portOfDischarge: string | null;
  private _currencyCode: string; private _exchangeRate: number;
  private _totalCifValue: number; private _totalDutyAmount: number;
  private _totalTaxAmount: number; private _totalLandedCost: number;
  private _customsClearanceDate: Date | null; private _notes: string | null;
  private _landedCosts: LandedCost[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: ImportDeclarationId, declarationNumber: string, companyId: string, poId: string, poNumber: string, vendorId: string, vendorName: string) {
    super(); this._id = id; this._declarationNumber = declarationNumber; this._companyId = companyId;
    this._poId = poId; this._poNumber = poNumber; this._vendorId = vendorId; this._vendorName = vendorName;
    this._status = ImportStatus.declared; this._incoterm = Incoterm.cif;
    this._freightTerm = FreightTerm.prepaid; this._currencyCode = "VND";
    this._exchangeRate = 1; this._totalCifValue = 0; this._totalDutyAmount = 0;
    this._totalTaxAmount = 0; this._totalLandedCost = 0;
    this._branchId = null; this._shipmentId = null; this._portOfLoading = null;
    this._portOfDischarge = null; this._customsClearanceDate = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    declarationNumber: string; companyId: string; poId: string; poNumber: string;
    vendorId: string; vendorName: string; branchId?: string; shipmentId?: string;
    incoterm?: Incoterm; freightTerm?: FreightTerm; currencyCode?: string;
    exchangeRate?: number; portOfLoading?: string; portOfDischarge?: string; notes?: string;
  }): ImportDeclaration {
    const d = new ImportDeclaration(ImportDeclarationId.new(), p.declarationNumber, p.companyId, p.poId, p.poNumber, p.vendorId, p.vendorName);
    d._branchId = p.branchId ?? null; d._shipmentId = p.shipmentId ?? null;
    d._incoterm = p.incoterm ?? Incoterm.cif; d._freightTerm = p.freightTerm ?? FreightTerm.prepaid;
    d._currencyCode = p.currencyCode ?? "VND"; d._exchangeRate = p.exchangeRate ?? 1;
    d._portOfLoading = p.portOfLoading ?? null; d._portOfDischarge = p.portOfDischarge ?? null;
    d._notes = p.notes ?? null;
    d.addEvent(new ImportDeclarationCreated(d._id.value, new Date(), { declarationNumber: d._declarationNumber }));
    return d;
  }

  static load(s: ImportDeclarationState): ImportDeclaration {
    const d = new ImportDeclaration(new ImportDeclarationId(s.id), s.declarationNumber, s.companyId, s.poId, s.poNumber, s.vendorId, s.vendorName);
    d._branchId = s.branchId; d._shipmentId = s.shipmentId; d._status = s.status as ImportStatus;
    d._incoterm = s.incoterm as Incoterm; d._freightTerm = s.freightTerm as FreightTerm;
    d._portOfLoading = s.portOfLoading; d._portOfDischarge = s.portOfDischarge;
    d._currencyCode = s.currencyCode; d._exchangeRate = s.exchangeRate;
    d._totalCifValue = s.totalCifValue; d._totalDutyAmount = s.totalDutyAmount;
    d._totalTaxAmount = s.totalTaxAmount; d._totalLandedCost = s.totalLandedCost;
    d._customsClearanceDate = s.customsClearanceDate; d._notes = s.notes;
    d._version = s.version; d._createdAt = s.createdAt; d._updatedAt = s.updatedAt; d._deletedAt = s.deletedAt;
    return d;
  }

  get id(): ImportDeclarationId { return this._id; }
  get declarationNumber(): string { return this._declarationNumber; }
  get status(): ImportStatus { return this._status; }
  get totalLandedCost(): number { return this._totalLandedCost; }
  get landedCosts(): LandedCost[] { return this._landedCosts; }
  get version(): number { return this._version; }

  addLandedCost(cost: LandedCost): void {
    this._landedCosts.push(cost);
    this._totalLandedCost = this._landedCosts.reduce((s, l) => s + l.amount, 0);
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new LandedCostPosted(this._id.value, new Date(), { declarationNumber: this._declarationNumber }));
  }

  markCustomsCleared(): void {
    this._status = ImportStatus.customsCleared;
    this._customsClearanceDate = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  markGoodsReleased(): void {
    this._status = ImportStatus.goodsReleased;
    this._updatedAt = new Date(); this._version++;
  }

  markCompleted(): void {
    this._status = ImportStatus.completed;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): ImportDeclarationState {
    return { id: this._id.value, declarationNumber: this._declarationNumber,
      companyId: this._companyId, branchId: this._branchId, poId: this._poId,
      poNumber: this._poNumber, vendorId: this._vendorId, vendorName: this._vendorName,
      shipmentId: this._shipmentId, status: this._status, incoterm: this._incoterm,
      freightTerm: this._freightTerm, portOfLoading: this._portOfLoading,
      portOfDischarge: this._portOfDischarge, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, totalCifValue: this._totalCifValue,
      totalDutyAmount: this._totalDutyAmount, totalTaxAmount: this._totalTaxAmount,
      totalLandedCost: this._totalLandedCost, customsClearanceDate: this._customsClearanceDate,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
