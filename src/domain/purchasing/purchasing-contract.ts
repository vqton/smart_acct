import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PurchaseContractId, ContractAmendmentId, PricingAgreementId } from "./purchasing-ids.js";
import { ContractStatus, ContractType } from "./purchasing-enums.js";
import { PurchaseContractCreated, PurchaseContractAmended, PurchaseContractExpired } from "./purchasing-events.js";

// ─── Purchase Contract ───────────────────────────────────────────────────────────

export interface PurchaseContractState {
  id: string; contractNumber: string; companyId: string; vendorId: string;
  vendorName: string; contractType: string; status: string;
  title: string; description: string | null; currencyCode: string;
  totalValue: number; amountSpent: number; amountRemaining: number;
  startDate: Date; endDate: Date; renewalDate: Date | null;
  maxOrderQty: number | null; orderedQty: number;
  paymentTermCode: string | null; incoterm: string | null;
  notes: string | null; amendmentNumber: number;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class PurchaseContract extends AggregateRoot<PurchaseContractId> {
  private _id: PurchaseContractId; private _contractNumber: string; private _companyId: string;
  private _vendorId: string; private _vendorName: string;
  private _contractType: ContractType; private _status: ContractStatus;
  private _title: string; private _description: string | null;
  private _currencyCode: string; private _totalValue: number;
  private _amountSpent: number; private _amountRemaining: number;
  private _startDate: Date; private _endDate: Date; private _renewalDate: Date | null;
  private _maxOrderQty: number | null; private _orderedQty: number;
  private _paymentTermCode: string | null; private _incoterm: string | null;
  private _notes: string | null; private _amendmentNumber: number;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: PurchaseContractId, contractNumber: string, companyId: string, vendorId: string, vendorName: string, title: string, startDate: Date, endDate: Date) {
    super(); this._id = id; this._contractNumber = contractNumber; this._companyId = companyId;
    this._vendorId = vendorId; this._vendorName = vendorName; this._title = title;
    this._startDate = startDate; this._endDate = endDate;
    this._contractType = ContractType.fixedPrice; this._status = ContractStatus.draft;
    this._currencyCode = "VND"; this._totalValue = 0; this._amountSpent = 0;
    this._amountRemaining = 0; this._orderedQty = 0; this._amendmentNumber = 0;
    this._description = null; this._renewalDate = null; this._maxOrderQty = null;
    this._paymentTermCode = null; this._incoterm = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    contractNumber: string; companyId: string; vendorId: string; vendorName: string;
    title: string; startDate: Date; endDate: Date; contractType?: ContractType;
    currencyCode?: string; totalValue?: number; description?: string;
    renewalDate?: Date; maxOrderQty?: number; paymentTermCode?: string;
    incoterm?: string; notes?: string;
  }): PurchaseContract {
    const c = new PurchaseContract(PurchaseContractId.new(), p.contractNumber, p.companyId, p.vendorId, p.vendorName, p.title, p.startDate, p.endDate);
    c._contractType = p.contractType ?? ContractType.fixedPrice;
    c._currencyCode = p.currencyCode ?? "VND"; c._totalValue = p.totalValue ?? 0;
    c._amountRemaining = p.totalValue ?? 0; c._description = p.description ?? null;
    c._renewalDate = p.renewalDate ?? null; c._maxOrderQty = p.maxOrderQty ?? null;
    c._paymentTermCode = p.paymentTermCode ?? null; c._incoterm = p.incoterm ?? null;
    c._notes = p.notes ?? null;
    c.addEvent(new PurchaseContractCreated(c._id.value, new Date(), { contractNumber: c._contractNumber }));
    return c;
  }

  static load(s: PurchaseContractState): PurchaseContract {
    const c = new PurchaseContract(new PurchaseContractId(s.id), s.contractNumber, s.companyId, s.vendorId, s.vendorName, s.title, s.startDate, s.endDate);
    c._contractType = s.contractType as ContractType; c._status = s.status as ContractStatus;
    c._description = s.description; c._currencyCode = s.currencyCode;
    c._totalValue = s.totalValue; c._amountSpent = s.amountSpent; c._amountRemaining = s.amountRemaining;
    c._renewalDate = s.renewalDate; c._maxOrderQty = s.maxOrderQty; c._orderedQty = s.orderedQty;
    c._paymentTermCode = s.paymentTermCode; c._incoterm = s.incoterm; c._notes = s.notes;
    c._amendmentNumber = s.amendmentNumber; c._version = s.version; c._createdAt = s.createdAt;
    c._updatedAt = s.updatedAt; c._deletedAt = s.deletedAt;
    return c;
  }

  get id(): PurchaseContractId { return this._id; }
  get contractNumber(): string { return this._contractNumber; }
  get status(): ContractStatus { return this._status; }
  get totalValue(): number { return this._totalValue; }
  get amountSpent(): number { return this._amountSpent; }
  get amountRemaining(): number { return this._amountRemaining; }
  get version(): number { return this._version; }

  activate(): void {
    if (this._status !== ContractStatus.draft) throw new DomainError("BusinessRule", "Only draft contracts can be activated");
    this._status = ContractStatus.active;
    this._updatedAt = new Date(); this._version++;
  }

  amend(p: { contractType?: ContractType; title?: string; description?: string | null; totalValue?: number; endDate?: Date; renewalDate?: Date | null; maxOrderQty?: number | null; notes?: string | null }): void {
    if (this._status !== ContractStatus.active) throw new DomainError("BusinessRule", "Only active contracts can be amended");
    if (p.contractType !== undefined) this._contractType = p.contractType;
    if (p.title !== undefined) this._title = p.title;
    if (p.description !== undefined) this._description = p.description;
    if (p.totalValue !== undefined) { this._totalValue = p.totalValue; this._amountRemaining = p.totalValue - this._amountSpent; }
    if (p.endDate !== undefined) this._endDate = p.endDate;
    if (p.renewalDate !== undefined) this._renewalDate = p.renewalDate;
    if (p.maxOrderQty !== undefined) this._maxOrderQty = p.maxOrderQty;
    if (p.notes !== undefined) this._notes = p.notes;
    this._amendmentNumber++; this._status = ContractStatus.amended;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseContractAmended(this._id.value, new Date(), { contractNumber: this._contractNumber, amendment: this._amendmentNumber }));
  }

  terminate(): void {
    if (this._status === ContractStatus.terminated) throw new DomainError("BusinessRule", "Contract already terminated");
    this._status = ContractStatus.terminated;
    this._updatedAt = new Date(); this._version++;
  }

  recordSpend(amount: number, qty: number = 0): void {
    this._amountSpent += amount;
    this._amountRemaining = this._totalValue - this._amountSpent;
    this._orderedQty += qty;
    if (this._amountRemaining < 0) this._amountRemaining = 0;
    this._updatedAt = new Date(); this._version++;
  }

  checkExpiry(): void {
    if (this._status === ContractStatus.active && new Date() > this._endDate) {
      this._status = ContractStatus.expired;
      this._updatedAt = new Date(); this._version++;
      this.addEvent(new PurchaseContractExpired(this._id.value, new Date(), { contractNumber: this._contractNumber }));
    }
  }

  toState(): PurchaseContractState {
    return { id: this._id.value, contractNumber: this._contractNumber, companyId: this._companyId,
      vendorId: this._vendorId, vendorName: this._vendorName, contractType: this._contractType,
      status: this._status, title: this._title, description: this._description,
      currencyCode: this._currencyCode, totalValue: this._totalValue, amountSpent: this._amountSpent,
      amountRemaining: this._amountRemaining, startDate: this._startDate, endDate: this._endDate,
      renewalDate: this._renewalDate, maxOrderQty: this._maxOrderQty, orderedQty: this._orderedQty,
      paymentTermCode: this._paymentTermCode, incoterm: this._incoterm, notes: this._notes,
      amendmentNumber: this._amendmentNumber, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
