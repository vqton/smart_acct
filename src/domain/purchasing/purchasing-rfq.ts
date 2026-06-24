import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { RFQId, RFQItemId, QuotationId, QuotationItemId, VendorResponseId } from "./purchasing-ids.js";
import { RFQStatus, QuotationStatus } from "./purchasing-enums.js";
import { RFQCreated, RFQSent, QuotationReceived } from "./purchasing-events.js";

// ─── RFQ Item ────────────────────────────────────────────────────────────────────

export interface RFQItemState {
  id: string; rfqId: string; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string;
  description: string | null; quantity: number; uom: string;
  expectedUnitPrice: number | null; currencyCode: string;
  requiredDate: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class RFQItem extends AggregateRoot<RFQItemId> {
  private _id: RFQItemId; private _rfqId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _expectedUnitPrice: number | null; private _currencyCode: string;
  private _requiredDate: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: RFQItemId, rfqId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string) {
    super(); this._id = id; this._rfqId = rfqId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity; this._uom = uom;
    this._expectedUnitPrice = null; this._currencyCode = "VND";
    this._itemId = null; this._description = null; this._requiredDate = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { rfqId: string; lineNumber: number; itemCode: string; itemName: string; quantity: number; uom: string; itemId?: string; description?: string; expectedUnitPrice?: number; requiredDate?: Date }): RFQItem {
    const i = new RFQItem(RFQItemId.new(), p.rfqId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom);
    i._itemId = p.itemId ?? null; i._description = p.description ?? null;
    i._expectedUnitPrice = p.expectedUnitPrice ?? null; i._requiredDate = p.requiredDate ?? null;
    return i;
  }

  static load(s: RFQItemState): RFQItem {
    const i = new RFQItem(new RFQItemId(s.id), s.rfqId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom);
    i._itemId = s.itemId; i._description = s.description; i._expectedUnitPrice = s.expectedUnitPrice;
    i._currencyCode = s.currencyCode; i._requiredDate = s.requiredDate;
    i._version = s.version; i._createdAt = s.createdAt; i._updatedAt = s.updatedAt; i._deletedAt = s.deletedAt;
    return i;
  }

  get id(): RFQItemId { return this._id; }
  get quantity(): number { return this._quantity; }
  get expectedUnitPrice(): number | null { return this._expectedUnitPrice; }
  get version(): number { return this._version; }

  toState(): RFQItemState {
    return { id: this._id.value, rfqId: this._rfqId, lineNumber: this._lineNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      description: this._description, quantity: this._quantity, uom: this._uom,
      expectedUnitPrice: this._expectedUnitPrice, currencyCode: this._currencyCode,
      requiredDate: this._requiredDate, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── RFQ ─────────────────────────────────────────────────────────────────────────

export interface RFQState {
  id: string; rfqNumber: string; companyId: string; branchId: string | null;
  title: string; description: string | null; status: string;
  currencyCode: string; totalEstimated: number;
  issueDate: Date | null; responseDeadline: Date | null;
  evaluatorId: string | null; awardRecommendation: string | null;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class RFQ extends AggregateRoot<RFQId> {
  private _id: RFQId; private _rfqNumber: string; private _companyId: string;
  private _branchId: string | null; private _title: string; private _description: string | null;
  private _status: RFQStatus; private _currencyCode: string;
  private _totalEstimated: number; private _issueDate: Date | null;
  private _responseDeadline: Date | null; private _evaluatorId: string | null;
  private _awardRecommendation: string | null; private _notes: string | null;
  private _items: RFQItem[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: RFQId, rfqNumber: string, companyId: string, title: string) {
    super(); this._id = id; this._rfqNumber = rfqNumber; this._companyId = companyId; this._title = title;
    this._status = RFQStatus.draft; this._currencyCode = "VND"; this._totalEstimated = 0;
    this._branchId = null; this._description = null; this._issueDate = null;
    this._responseDeadline = null; this._evaluatorId = null; this._awardRecommendation = null;
    this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { rfqNumber: string; companyId: string; title: string; branchId?: string; description?: string; currencyCode?: string; responseDeadline?: Date; notes?: string }): RFQ {
    const r = new RFQ(RFQId.new(), p.rfqNumber, p.companyId, p.title);
    r._branchId = p.branchId ?? null; r._description = p.description ?? null;
    r._currencyCode = p.currencyCode ?? "VND"; r._responseDeadline = p.responseDeadline ?? null;
    r._notes = p.notes ?? null;
    r.addEvent(new RFQCreated(r._id.value, new Date(), { rfqNumber: r._rfqNumber }));
    return r;
  }

  static load(s: RFQState): RFQ {
    const r = new RFQ(new RFQId(s.id), s.rfqNumber, s.companyId, s.title);
    r._branchId = s.branchId; r._description = s.description; r._status = s.status as RFQStatus;
    r._currencyCode = s.currencyCode; r._totalEstimated = s.totalEstimated;
    r._issueDate = s.issueDate; r._responseDeadline = s.responseDeadline;
    r._evaluatorId = s.evaluatorId; r._awardRecommendation = s.awardRecommendation; r._notes = s.notes;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt; r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): RFQId { return this._id; }
  get rfqNumber(): string { return this._rfqNumber; }
  get status(): RFQStatus { return this._status; }
  get items(): RFQItem[] { return this._items; }
  get version(): number { return this._version; }

  addItem(item: RFQItem): void {
    if (this._status !== RFQStatus.draft) throw new DomainError("BusinessRule", "Cannot add items to non-draft RFQ");
    this._items.push(item);
    this._totalEstimated = this._items.reduce((s, i) => s + (i.expectedUnitPrice ?? 0) * i.quantity, 0);
    this._updatedAt = new Date(); this._version++;
  }

  send(): void {
    if (this._items.length === 0) throw new DomainError("Validation", "Cannot send RFQ with no items");
    if (this._status !== RFQStatus.draft) throw new DomainError("BusinessRule", "Only draft RFQ can be sent");
    this._status = RFQStatus.sent; this._issueDate = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new RFQSent(this._id.value, new Date(), { rfqNumber: this._rfqNumber }));
  }

  markEvaluated(evaluatorId: string, recommendation: string): void {
    this._status = RFQStatus.evaluated; this._evaluatorId = evaluatorId;
    this._awardRecommendation = recommendation;
    this._updatedAt = new Date(); this._version++;
  }

  markAwarded(): void {
    this._status = RFQStatus.awarded;
    this._updatedAt = new Date(); this._version++;
  }

  cancel(): void {
    if (this._status === RFQStatus.cancelled) throw new DomainError("BusinessRule", "RFQ already cancelled");
    this._status = RFQStatus.cancelled;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): RFQState {
    return { id: this._id.value, rfqNumber: this._rfqNumber, companyId: this._companyId,
      branchId: this._branchId, title: this._title, description: this._description,
      status: this._status, currencyCode: this._currencyCode, totalEstimated: this._totalEstimated,
      issueDate: this._issueDate, responseDeadline: this._responseDeadline,
      evaluatorId: this._evaluatorId, awardRecommendation: this._awardRecommendation,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Quotation ───────────────────────────────────────────────────────────────────

export interface QuotationState {
  id: string; rfqId: string; vendorId: string; vendorName: string;
  quotationNumber: string; status: string; currencyCode: string;
  totalAmount: number; validUntil: Date | null; notes: string | null;
  submittedAt: Date | null; acceptedAt: Date | null; rejectionReason: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class Quotation extends AggregateRoot<QuotationId> {
  private _id: QuotationId; private _rfqId: string; private _vendorId: string;
  private _vendorName: string; private _quotationNumber: string;
  private _status: QuotationStatus; private _currencyCode: string;
  private _totalAmount: number; private _validUntil: Date | null;
  private _notes: string | null; private _submittedAt: Date | null;
  private _acceptedAt: Date | null; private _rejectionReason: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: QuotationId, rfqId: string, vendorId: string, vendorName: string, quotationNumber: string) {
    super(); this._id = id; this._rfqId = rfqId; this._vendorId = vendorId;
    this._vendorName = vendorName; this._quotationNumber = quotationNumber;
    this._status = QuotationStatus.draft; this._currencyCode = "VND"; this._totalAmount = 0;
    this._validUntil = null; this._notes = null; this._submittedAt = null;
    this._acceptedAt = null; this._rejectionReason = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { rfqId: string; vendorId: string; vendorName: string; quotationNumber: string; currencyCode?: string; validUntil?: Date; notes?: string }): Quotation {
    const q = new Quotation(QuotationId.new(), p.rfqId, p.vendorId, p.vendorName, p.quotationNumber);
    q._currencyCode = p.currencyCode ?? "VND"; q._validUntil = p.validUntil ?? null; q._notes = p.notes ?? null;
    return q;
  }

  static load(s: QuotationState): Quotation {
    const q = new Quotation(new QuotationId(s.id), s.rfqId, s.vendorId, s.vendorName, s.quotationNumber);
    q._status = s.status as QuotationStatus; q._currencyCode = s.currencyCode;
    q._totalAmount = s.totalAmount; q._validUntil = s.validUntil; q._notes = s.notes;
    q._submittedAt = s.submittedAt; q._acceptedAt = s.acceptedAt; q._rejectionReason = s.rejectionReason;
    q._version = s.version; q._createdAt = s.createdAt; q._updatedAt = s.updatedAt; q._deletedAt = s.deletedAt;
    return q;
  }

  get id(): QuotationId { return this._id; }
  get quotationNumber(): string { return this._quotationNumber; }
  get status(): QuotationStatus { return this._status; }
  get vendorId(): string { return this._vendorId; }
  get totalAmount(): number { return this._totalAmount; }
  get version(): number { return this._version; }

  submit(): void {
    if (this._status !== QuotationStatus.draft) throw new DomainError("BusinessRule", "Only draft quotation can be submitted");
    this._status = QuotationStatus.submitted; this._submittedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationReceived(this._id.value, new Date(), { quotationNumber: this._quotationNumber, vendorId: this._vendorId }));
  }

  accept(): void {
    this._status = QuotationStatus.accepted; this._acceptedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  reject(reason: string): void {
    this._status = QuotationStatus.rejected; this._rejectionReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): QuotationState {
    return { id: this._id.value, rfqId: this._rfqId, vendorId: this._vendorId,
      vendorName: this._vendorName, quotationNumber: this._quotationNumber, status: this._status,
      currencyCode: this._currencyCode, totalAmount: this._totalAmount, validUntil: this._validUntil,
      notes: this._notes, submittedAt: this._submittedAt, acceptedAt: this._acceptedAt,
      rejectionReason: this._rejectionReason, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
