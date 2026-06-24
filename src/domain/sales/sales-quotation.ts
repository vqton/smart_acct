import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { QuotationId, QuotationLineId } from "./sales-ids.js";
import { SlsQuotationStatus, SlsOrderSource } from "./sales-enums.js";
import { QuotationCreated, QuotationSent, QuotationAccepted, QuotationRejected, QuotationConverted, QuotationExpired } from "./sales-events.js";

export interface QuotationLineState {
  id: string; quotationId: string; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string; description: string | null;
  quantity: number; uom: string; unitPrice: number; totalPrice: number; currencyCode: string;
  discountPercent: number; discountAmount: number;
  taxCode: string | null; taxRate: number; taxAmount: number; netAmount: number;
  warehouseId: string | null; projectId: string | null; costCenterId: string | null;
  departmentId: string | null; expectedDate: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class QuotationLine extends AggregateRoot<QuotationLineId> {
  private _id: QuotationLineId; private _quotationId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _discountPercent: number; private _discountAmount: number;
  private _taxCode: string | null; private _taxRate: number; private _taxAmount: number;
  private _netAmount: number; private _warehouseId: string | null;
  private _projectId: string | null; private _costCenterId: string | null;
  private _departmentId: string | null; private _expectedDate: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: QuotationLineId, quotationId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._quotationId = quotationId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantity * unitPrice; this._currencyCode = "VND";
    this._discountPercent = 0; this._discountAmount = 0;
    this._taxCode = null; this._taxRate = 0; this._taxAmount = 0;
    this._netAmount = this._totalPrice; this._itemId = null; this._description = null;
    this._warehouseId = null; this._projectId = null; this._costCenterId = null;
    this._departmentId = null; this._expectedDate = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { quotationId: string; lineNumber: number; itemCode: string; itemName: string; quantity: number; uom: string; unitPrice: number; itemId?: string; description?: string; taxCode?: string; taxRate?: number; warehouseId?: string; projectId?: string; costCenterId?: string; departmentId?: string; expectedDate?: Date; discountPercent?: number; discountAmount?: number }): QuotationLine {
    const l = new QuotationLine(QuotationLineId.new(), p.quotationId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.unitPrice);
    l._itemId = p.itemId ?? null; l._description = p.description ?? null;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    l._warehouseId = p.warehouseId ?? null; l._projectId = p.projectId ?? null;
    l._costCenterId = p.costCenterId ?? null; l._departmentId = p.departmentId ?? null;
    l._expectedDate = p.expectedDate ?? null;
    if (p.discountPercent) { l._discountPercent = p.discountPercent; l._discountAmount = Math.round(l._totalPrice * p.discountPercent / 100); }
    if (p.discountAmount) l._discountAmount = p.discountAmount;
    l._taxAmount = Math.round((l._totalPrice - l._discountAmount) * l._taxRate / 100);
    l._netAmount = l._totalPrice - l._discountAmount + l._taxAmount;
    return l;
  }

  static load(s: QuotationLineState): QuotationLine {
    const l = new QuotationLine(new QuotationLineId(s.id), s.quotationId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.unitPrice);
    l._itemId = s.itemId; l._description = s.description; l._totalPrice = s.totalPrice;
    l._currencyCode = s.currencyCode; l._discountPercent = s.discountPercent;
    l._discountAmount = s.discountAmount; l._taxCode = s.taxCode; l._taxRate = s.taxRate;
    l._taxAmount = s.taxAmount; l._netAmount = s.netAmount; l._warehouseId = s.warehouseId;
    l._projectId = s.projectId; l._costCenterId = s.costCenterId; l._departmentId = s.departmentId;
    l._expectedDate = s.expectedDate; l._version = s.version; l._createdAt = s.createdAt;
    l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): QuotationLineId { return this._id; }
  get quantity(): number { return this._quantity; }
  get unitPrice(): number { return this._unitPrice; }
  get totalPrice(): number { return this._totalPrice; }
  get netAmount(): number { return this._netAmount; }
  get taxRate(): number { return this._taxRate; }
  get itemCode(): string { return this._itemCode; }
  get taxAmount(): number { return this._taxAmount; }
  get discountAmount(): number { return this._discountAmount; }

  toState(): QuotationLineState {
    return { id: this._id.value, quotationId: this._quotationId, lineNumber: this._lineNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      description: this._description, quantity: this._quantity, uom: this._uom,
      unitPrice: this._unitPrice, totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      discountPercent: this._discountPercent, discountAmount: this._discountAmount,
      taxCode: this._taxCode, taxRate: this._taxRate, taxAmount: this._taxAmount,
      netAmount: this._netAmount, warehouseId: this._warehouseId, projectId: this._projectId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      expectedDate: this._expectedDate, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

export interface QuotationState {
  id: string; quotationNumber: string; companyId: string; branchId: string | null;
  customerId: string; customerName: string; customerTaxCode: string | null;
  storeId: string | null; salespersonId: string | null; orderSource: string;
  status: string; revisionNumber: number;
  currencyCode: string; exchangeRate: number; subtotal: number;
  discountAmount: number; taxAmount: number; grandTotal: number;
  quotationDate: Date; validUntil: Date | null; expectedDeliveryDate: Date | null;
  approvedBy: string | null; approvedAt: Date | null;
  rejectedBy: string | null; rejectedAt: Date | null; rejectReason: string | null;
  convertedToOrderId: string | null; convertedAt: Date | null;
  notes: string | null; termsAndConditions: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class Quotation extends AggregateRoot<QuotationId> {
  private _id: QuotationId; private _quotationNumber: string; private _companyId: string;
  private _branchId: string | null; private _customerId: string; private _customerName: string;
  private _customerTaxCode: string | null; private _storeId: string | null;
  private _salespersonId: string | null; private _orderSource: SlsOrderSource;
  private _status: SlsQuotationStatus; private _revisionNumber: number;
  private _currencyCode: string; private _exchangeRate: number;
  private _subtotal: number; private _discountAmount: number; private _taxAmount: number;
  private _grandTotal: number;   private _quotationDate!: Date; private _validUntil: Date | null;
  private _expectedDeliveryDate: Date | null;
  private _approvedBy: string | null; private _approvedAt: Date | null;
  private _rejectedBy: string | null; private _rejectedAt: Date | null;
  private _rejectReason: string | null;
  private _convertedToOrderId: string | null; private _convertedAt: Date | null;
  private _notes: string | null; private _termsAndConditions: string | null;
  private _lines: QuotationLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: QuotationId, quotationNumber: string, companyId: string, customerId: string, customerName: string) {
    super(); this._id = id; this._quotationNumber = quotationNumber; this._companyId = companyId;
    this._customerId = customerId; this._customerName = customerName;
    this._orderSource = SlsOrderSource.manual; this._status = SlsQuotationStatus.draft;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._subtotal = 0;
    this._discountAmount = 0; this._taxAmount = 0; this._grandTotal = 0; this._revisionNumber = 0;
    this._branchId = null; this._customerTaxCode = null; this._storeId = null;
    this._salespersonId = null; this._validUntil = null; this._expectedDeliveryDate = null;
    this._approvedBy = null; this._approvedAt = null; this._rejectedBy = null;
    this._rejectedAt = null; this._rejectReason = null; this._convertedToOrderId = null;
    this._convertedAt = null; this._notes = null; this._termsAndConditions = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { quotationNumber: string; companyId: string; customerId: string; customerName: string; branchId?: string; customerTaxCode?: string; storeId?: string; salespersonId?: string; orderSource?: SlsOrderSource; currencyCode?: string; exchangeRate?: number; quotationDate?: Date; validUntil?: Date; expectedDeliveryDate?: Date; notes?: string; termsAndConditions?: string }): Quotation {
    const q = new Quotation(QuotationId.new(), p.quotationNumber, p.companyId, p.customerId, p.customerName);
    q._branchId = p.branchId ?? null; q._customerTaxCode = p.customerTaxCode ?? null;
    q._storeId = p.storeId ?? null; q._salespersonId = p.salespersonId ?? null;
    q._orderSource = p.orderSource ?? SlsOrderSource.manual;
    q._currencyCode = p.currencyCode ?? "VND"; q._exchangeRate = p.exchangeRate ?? 1;
    q._quotationDate = p.quotationDate ?? new Date(); q._validUntil = p.validUntil ?? null;
    q._expectedDeliveryDate = p.expectedDeliveryDate ?? null;
    q._notes = p.notes ?? null; q._termsAndConditions = p.termsAndConditions ?? null;
    q.addEvent(new QuotationCreated(q._id.value, new Date(), { quotationNumber: q._quotationNumber, customerId: q._customerId }));
    return q;
  }

  static load(s: QuotationState): Quotation {
    const q = new Quotation(new QuotationId(s.id), s.quotationNumber, s.companyId, s.customerId, s.customerName);
    q._branchId = s.branchId; q._customerTaxCode = s.customerTaxCode; q._storeId = s.storeId;
    q._salespersonId = s.salespersonId; q._orderSource = s.orderSource as SlsOrderSource;
    q._status = s.status as SlsQuotationStatus; q._revisionNumber = s.revisionNumber;
    q._currencyCode = s.currencyCode; q._exchangeRate = s.exchangeRate;
    q._subtotal = s.subtotal; q._discountAmount = s.discountAmount; q._taxAmount = s.taxAmount;
    q._grandTotal = s.grandTotal; q._quotationDate = s.quotationDate;
    q._validUntil = s.validUntil; q._expectedDeliveryDate = s.expectedDeliveryDate;
    q._approvedBy = s.approvedBy; q._approvedAt = s.approvedAt; q._rejectedBy = s.rejectedBy;
    q._rejectedAt = s.rejectedAt; q._rejectReason = s.rejectReason;
    q._convertedToOrderId = s.convertedToOrderId; q._convertedAt = s.convertedAt;
    q._notes = s.notes; q._termsAndConditions = s.termsAndConditions;
    q._version = s.version; q._createdAt = s.createdAt; q._updatedAt = s.updatedAt;
    q._deletedAt = s.deletedAt;
    return q;
  }

  get id(): QuotationId { return this._id; }
  get quotationNumber(): string { return this._quotationNumber; }
  get status(): SlsQuotationStatus { return this._status; }
  get customerId(): string { return this._customerId; }
  get subtotal(): number { return this._subtotal; }
  get grandTotal(): number { return this._grandTotal; }
  get lines(): QuotationLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(line: QuotationLine): void {
    if (this._status !== SlsQuotationStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft quotation");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._subtotal = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._taxAmount = this._lines.reduce((s, l) => s + l.taxAmount, 0);
    this._grandTotal = this._subtotal - this._discountAmount + this._taxAmount;
  }

  send(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot send quotation with no lines");
    if (this._status !== SlsQuotationStatus.draft) throw new DomainError("BusinessRule", "Only draft quotation can be sent");
    if (this._validUntil && this._validUntil < new Date()) throw new DomainError("BusinessRule", "Quotation has expired");
    this._status = SlsQuotationStatus.sent;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationSent(this._id.value, new Date(), { quotationNumber: this._quotationNumber }));
  }

  accept(): void {
    if (this._status !== SlsQuotationStatus.sent) throw new DomainError("BusinessRule", "Only sent quotation can be accepted");
    this._status = SlsQuotationStatus.accepted;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationAccepted(this._id.value, new Date(), { quotationNumber: this._quotationNumber }));
  }

  reject(reason: string, rejectedBy: string): void {
    if (this._status === SlsQuotationStatus.cancelled || this._status === SlsQuotationStatus.converted) throw new DomainError("BusinessRule", "Quotation already closed");
    this._status = SlsQuotationStatus.rejected;
    this._rejectReason = reason; this._rejectedBy = rejectedBy; this._rejectedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationRejected(this._id.value, new Date(), { quotationNumber: this._quotationNumber, reason }));
  }

  markExpired(): void {
    this._status = SlsQuotationStatus.expired;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationExpired(this._id.value, new Date(), { quotationNumber: this._quotationNumber }));
  }

  markConverted(orderId: string): void {
    this._status = SlsQuotationStatus.converted;
    this._convertedToOrderId = orderId; this._convertedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new QuotationConverted(this._id.value, new Date(), { quotationNumber: this._quotationNumber, orderId }));
  }

  cancel(): void {
    if (this._status === SlsQuotationStatus.cancelled || this._status === SlsQuotationStatus.converted) throw new DomainError("BusinessRule", "Quotation already closed");
    this._status = SlsQuotationStatus.cancelled;
    this._updatedAt = new Date(); this._version++;
  }

  createRevision(): number {
    this._revisionNumber++;
    this._status = SlsQuotationStatus.revised;
    this._updatedAt = new Date(); this._version++;
    return this._revisionNumber;
  }

  toState(): QuotationState {
    return { id: this._id.value, quotationNumber: this._quotationNumber, companyId: this._companyId,
      branchId: this._branchId, customerId: this._customerId, customerName: this._customerName,
      customerTaxCode: this._customerTaxCode, storeId: this._storeId,
      salespersonId: this._salespersonId, orderSource: this._orderSource,
      status: this._status, revisionNumber: this._revisionNumber,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      subtotal: this._subtotal, discountAmount: this._discountAmount, taxAmount: this._taxAmount,
      grandTotal: this._grandTotal, quotationDate: this._quotationDate,
      validUntil: this._validUntil, expectedDeliveryDate: this._expectedDeliveryDate,
      approvedBy: this._approvedBy, approvedAt: this._approvedAt,
      rejectedBy: this._rejectedBy, rejectedAt: this._rejectedAt, rejectReason: this._rejectReason,
      convertedToOrderId: this._convertedToOrderId, convertedAt: this._convertedAt,
      notes: this._notes, termsAndConditions: this._termsAndConditions,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
