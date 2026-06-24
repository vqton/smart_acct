import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PurchaseOrderId, POLineId, PORevisionId } from "./purchasing-ids.js";
import { POStatus, POType, ReceiptStatus, PriceUnit } from "./purchasing-enums.js";
import {
  PurchaseOrderCreated, PurchaseOrderApproved, PurchaseOrderSent,
  PurchaseOrderConfirmed, PurchaseOrderCancelled, PurchaseOrderClosed,
  PurchaseOrderOnHold, PurchaseOrderRevisionCreated,
} from "./purchasing-events.js";

// ─── PO Line ─────────────────────────────────────────────────────────────────────

export interface POLineState {
  id: string; poId: string; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string;
  description: string | null; quantity: number; uom: string;
  unitPrice: number; totalPrice: number; currencyCode: string;
  taxCode: string | null; taxRate: number;
  receivedQuantity: number; invoicedQuantity: number;
  expectedDate: Date | null; promiseDate: Date | null;
  projectId: string | null; costCenterId: string | null; departmentId: string | null;
  branchId: string | null; warehouseId: string | null;
  receiptStatus: string; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class POLine extends AggregateRoot<POLineId> {
  private _id: POLineId; private _poId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _taxCode: string | null; private _taxRate: number;
  private _receivedQuantity: number; private _invoicedQuantity: number;
  private _expectedDate: Date | null; private _promiseDate: Date | null;
  private _projectId: string | null; private _costCenterId: string | null;
  private _departmentId: string | null; private _branchId: string | null;
  private _warehouseId: string | null; private _receiptStatus: string;
  private _notes: string | null; private _version: number; private _createdAt: Date;
  private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: POLineId, poId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._poId = poId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantity * unitPrice; this._currencyCode = "VND";
    this._taxCode = null; this._taxRate = 0; this._receivedQuantity = 0;
    this._invoicedQuantity = 0; this._expectedDate = null; this._promiseDate = null;
    this._itemId = null; this._description = null; this._projectId = null;
    this._costCenterId = null; this._departmentId = null; this._branchId = null;
    this._warehouseId = null; this._receiptStatus = "pending"; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    poId: string; lineNumber: number; itemCode: string; itemName: string;
    quantity: number; uom: string; unitPrice: number; itemId?: string;
    description?: string; taxCode?: string; taxRate?: number;
    expectedDate?: Date; promiseDate?: Date; projectId?: string;
    costCenterId?: string; departmentId?: string; branchId?: string;
    warehouseId?: string; notes?: string;
  }): POLine {
    const l = new POLine(POLineId.new(), p.poId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.unitPrice);
    l._itemId = p.itemId ?? null; l._description = p.description ?? null;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    l._expectedDate = p.expectedDate ?? null; l._promiseDate = p.promiseDate ?? null;
    l._projectId = p.projectId ?? null; l._costCenterId = p.costCenterId ?? null;
    l._departmentId = p.departmentId ?? null; l._branchId = p.branchId ?? null;
    l._warehouseId = p.warehouseId ?? null; l._notes = p.notes ?? null;
    return l;
  }

  static load(s: POLineState): POLine {
    const l = new POLine(new POLineId(s.id), s.poId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.unitPrice);
    l._itemId = s.itemId; l._description = s.description; l._totalPrice = s.totalPrice;
    l._currencyCode = s.currencyCode; l._taxCode = s.taxCode; l._taxRate = s.taxRate;
    l._receivedQuantity = s.receivedQuantity; l._invoicedQuantity = s.invoicedQuantity;
    l._expectedDate = s.expectedDate; l._promiseDate = s.promiseDate;
    l._projectId = s.projectId; l._costCenterId = s.costCenterId; l._departmentId = s.departmentId;
    l._branchId = s.branchId; l._warehouseId = s.warehouseId; l._receiptStatus = s.receiptStatus;
    l._notes = s.notes; l._version = s.version; l._createdAt = s.createdAt;
    l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): POLineId { return this._id; }
  get quantity(): number { return this._quantity; }
  get unitPrice(): number { return this._unitPrice; }
  get totalPrice(): number { return this._totalPrice; }
  get taxRate(): number { return this._taxRate; }
  get receivedQuantity(): number { return this._receivedQuantity; }
  get invoicedQuantity(): number { return this._invoicedQuantity; }
  get receiptStatus(): string { return this._receiptStatus; }
  get version(): number { return this._version; }

  recordReceipt(qty: number): void {
    const newReceived = this._receivedQuantity + qty;
    if (newReceived > this._quantity) throw new DomainError("BusinessRule", "Receipt exceeds ordered quantity");
    this._receivedQuantity = newReceived;
    this._receiptStatus = this._receivedQuantity >= this._quantity ? "fully_received" : "partly_received";
    this._updatedAt = new Date(); this._version++;
  }

  reverseReceipt(qty: number): void {
    const newReceived = this._receivedQuantity - qty;
    if (newReceived < 0) throw new DomainError("Validation", "Cannot reverse more than received");
    this._receivedQuantity = newReceived;
    this._receiptStatus = this._receivedQuantity <= 0 ? "pending" : "partly_received";
    this._updatedAt = new Date(); this._version++;
  }

  recordInvoice(qty: number): void {
    const newInvoiced = this._invoicedQuantity + qty;
    if (newInvoiced > this._quantity) throw new DomainError("BusinessRule", "Invoice quantity exceeds ordered quantity");
    this._invoicedQuantity = newInvoiced;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): POLineState {
    return { id: this._id.value, poId: this._poId, lineNumber: this._lineNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      description: this._description, quantity: this._quantity, uom: this._uom,
      unitPrice: this._unitPrice, totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      taxCode: this._taxCode, taxRate: this._taxRate, receivedQuantity: this._receivedQuantity,
      invoicedQuantity: this._invoicedQuantity, expectedDate: this._expectedDate,
      promiseDate: this._promiseDate, projectId: this._projectId, costCenterId: this._costCenterId,
      departmentId: this._departmentId, branchId: this._branchId, warehouseId: this._warehouseId,
      receiptStatus: this._receiptStatus, notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Purchase Order ──────────────────────────────────────────────────────────────

export interface PurchaseOrderState {
  id: string; poNumber: string; companyId: string; branchId: string | null;
  vendorId: string; vendorName: string; vendorTaxCode: string | null;
  poType: string; status: string; currencyCode: string;
  exchangeRate: number; totalAmount: number; totalTax: number; grandTotal: number;
  description: string | null; notes: string | null;
  paymentTermCode: string | null; incoterm: string | null;
  freightTerm: string | null; shipmentMethod: string | null;
  requestedDate: Date | null; promisedDate: Date | null;
  approvedAt: Date | null; approvedBy: string | null;
  sentAt: Date | null; confirmedAt: Date | null; confirmedBy: string | null;
  closedAt: Date | null; cancelledAt: Date | null; cancelReason: string | null;
  holdReason: string | null; revisionNumber: number;
  sourceDocumentType: string | null; sourceDocumentId: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class PurchaseOrder extends AggregateRoot<PurchaseOrderId> {
  private _id: PurchaseOrderId; private _poNumber: string; private _companyId: string;
  private _branchId: string | null; private _vendorId: string; private _vendorName: string;
  private _vendorTaxCode: string | null; private _poType: POType; private _status: POStatus;
  private _currencyCode: string; private _exchangeRate: number;
  private _totalAmount: number; private _totalTax: number; private _grandTotal: number;
  private _description: string | null; private _notes: string | null;
  private _paymentTermCode: string | null; private _incoterm: string | null;
  private _freightTerm: string | null; private _shipmentMethod: string | null;
  private _requestedDate: Date | null; private _promisedDate: Date | null;
  private _approvedAt: Date | null; private _approvedBy: string | null;
  private _sentAt: Date | null; private _confirmedAt: Date | null; private _confirmedBy: string | null;
  private _closedAt: Date | null; private _cancelledAt: Date | null; private _cancelReason: string | null;
  private _holdReason: string | null; private _revisionNumber: number;
  private _sourceDocumentType: string | null; private _sourceDocumentId: string | null;
  private _lines: POLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: PurchaseOrderId, poNumber: string, companyId: string, vendorId: string, vendorName: string) {
    super(); this._id = id; this._poNumber = poNumber; this._companyId = companyId;
    this._vendorId = vendorId; this._vendorName = vendorName;
    this._poType = POType.standard; this._status = POStatus.draft;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._totalAmount = 0;
    this._totalTax = 0; this._grandTotal = 0; this._revisionNumber = 0;
    this._branchId = null; this._vendorTaxCode = null; this._description = null;
    this._notes = null; this._paymentTermCode = null; this._incoterm = null;
    this._freightTerm = null; this._shipmentMethod = null; this._requestedDate = null;
    this._promisedDate = null; this._approvedAt = null; this._approvedBy = null;
    this._sentAt = null; this._confirmedAt = null; this._confirmedBy = null;
    this._closedAt = null; this._cancelledAt = null; this._cancelReason = null;
    this._holdReason = null; this._sourceDocumentType = null; this._sourceDocumentId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    poNumber: string; companyId: string; vendorId: string; vendorName: string;
    branchId?: string; vendorTaxCode?: string; poType?: POType;
    currencyCode?: string; exchangeRate?: number; description?: string; notes?: string;
    paymentTermCode?: string; incoterm?: string; freightTerm?: string; shipmentMethod?: string;
    requestedDate?: Date; promisedDate?: Date;
    sourceDocumentType?: string; sourceDocumentId?: string;
  }): PurchaseOrder {
    const po = new PurchaseOrder(PurchaseOrderId.new(), p.poNumber, p.companyId, p.vendorId, p.vendorName);
    po._branchId = p.branchId ?? null; po._vendorTaxCode = p.vendorTaxCode ?? null;
    po._poType = p.poType ?? POType.standard; po._currencyCode = p.currencyCode ?? "VND";
    po._exchangeRate = p.exchangeRate ?? 1; po._description = p.description ?? null;
    po._notes = p.notes ?? null; po._paymentTermCode = p.paymentTermCode ?? null;
    po._incoterm = p.incoterm ?? null; po._freightTerm = p.freightTerm ?? null;
    po._shipmentMethod = p.shipmentMethod ?? null; po._requestedDate = p.requestedDate ?? null;
    po._promisedDate = p.promisedDate ?? null;
    po._sourceDocumentType = p.sourceDocumentType ?? null; po._sourceDocumentId = p.sourceDocumentId ?? null;
    po.addEvent(new PurchaseOrderCreated(po._id.value, new Date(), { poNumber: po._poNumber, vendorId: po._vendorId }));
    return po;
  }

  static load(s: PurchaseOrderState): PurchaseOrder {
    const po = new PurchaseOrder(new PurchaseOrderId(s.id), s.poNumber, s.companyId, s.vendorId, s.vendorName);
    po._branchId = s.branchId; po._vendorTaxCode = s.vendorTaxCode;
    po._poType = s.poType as POType; po._status = s.status as POStatus;
    po._currencyCode = s.currencyCode; po._exchangeRate = s.exchangeRate;
    po._totalAmount = s.totalAmount; po._totalTax = s.totalTax; po._grandTotal = s.grandTotal;
    po._description = s.description; po._notes = s.notes;
    po._paymentTermCode = s.paymentTermCode; po._incoterm = s.incoterm;
    po._freightTerm = s.freightTerm; po._shipmentMethod = s.shipmentMethod;
    po._requestedDate = s.requestedDate; po._promisedDate = s.promisedDate;
    po._approvedAt = s.approvedAt; po._approvedBy = s.approvedBy;
    po._sentAt = s.sentAt; po._confirmedAt = s.confirmedAt; po._confirmedBy = s.confirmedBy;
    po._closedAt = s.closedAt; po._cancelledAt = s.cancelledAt; po._cancelReason = s.cancelReason;
    po._holdReason = s.holdReason; po._revisionNumber = s.revisionNumber;
    po._sourceDocumentType = s.sourceDocumentType; po._sourceDocumentId = s.sourceDocumentId;
    po._version = s.version; po._createdAt = s.createdAt; po._updatedAt = s.updatedAt; po._deletedAt = s.deletedAt;
    return po;
  }

  get id(): PurchaseOrderId { return this._id; }
  get poNumber(): string { return this._poNumber; }
  get status(): POStatus { return this._status; }
  get poType(): POType { return this._poType; }
  get vendorId(): string { return this._vendorId; }
  get totalAmount(): number { return this._totalAmount; }
  get grandTotal(): number { return this._grandTotal; }
  get lines(): POLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(line: POLine): void {
    if (this._status !== POStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft PO");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._totalAmount = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._totalTax = this._lines.reduce((s, l) => s + l.totalPrice * (l.taxRate / 100), 0);
    this._grandTotal = this._totalAmount + this._totalTax;
  }

  submitForApproval(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot submit PO with no lines");
    if (this._status !== POStatus.draft) throw new DomainError("BusinessRule", "Only draft PO can be submitted");
    this._status = POStatus.pendingApproval;
    this._updatedAt = new Date(); this._version++;
  }

  approve(approvedBy: string): void {
    if (this._status !== POStatus.pendingApproval) throw new DomainError("BusinessRule", "PO not pending approval");
    this._status = POStatus.approved;
    this._approvedAt = new Date(); this._approvedBy = approvedBy;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderApproved(this._id.value, new Date(), { poNumber: this._poNumber, approvedBy }));
  }

  send(): void {
    if (this._status !== POStatus.approved) throw new DomainError("BusinessRule", "Only approved PO can be sent");
    this._status = POStatus.sent;
    this._sentAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderSent(this._id.value, new Date(), { poNumber: this._poNumber }));
  }

  confirm(confirmedBy: string): void {
    if (this._status !== POStatus.sent) throw new DomainError("BusinessRule", "Only sent PO can be confirmed");
    this._status = POStatus.confirmed;
    this._confirmedAt = new Date(); this._confirmedBy = confirmedBy;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderConfirmed(this._id.value, new Date(), { poNumber: this._poNumber, confirmedBy }));
  }

  cancel(reason: string): void {
    if (this._status === POStatus.cancelled || this._status === POStatus.closed) throw new DomainError("BusinessRule", "PO already cancelled/closed");
    this._status = POStatus.cancelled;
    this._cancelledAt = new Date(); this._cancelReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderCancelled(this._id.value, new Date(), { poNumber: this._poNumber, reason }));
  }

  close(): void {
    if (this._status === POStatus.closed) throw new DomainError("BusinessRule", "PO already closed");
    this._status = POStatus.closed;
    this._closedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderClosed(this._id.value, new Date(), { poNumber: this._poNumber }));
  }

  hold(reason: string): void {
    if (this._status === POStatus.onHold) throw new DomainError("BusinessRule", "PO already on hold");
    this._status = POStatus.onHold;
    this._holdReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderOnHold(this._id.value, new Date(), { poNumber: this._poNumber, reason }));
  }

  release(): void {
    if (this._status !== POStatus.onHold) throw new DomainError("BusinessRule", "PO not on hold");
    this._status = POStatus.approved;
    this._holdReason = null;
    this._updatedAt = new Date(); this._version++;
  }

  updateReceiptStatus(): void {
    const allFullyReceived = this._lines.every(l => l.receiptStatus === "fully_received");
    const anyReceived = this._lines.some(l => l.receiptStatus !== "pending");
    if (allFullyReceived) {
      this._status = POStatus.fullyReceived;
    } else if (anyReceived) {
      this._status = POStatus.partlyReceived;
    }
    this._updatedAt = new Date(); this._version++;
  }

  createRevision(): number {
    this._revisionNumber++;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PurchaseOrderRevisionCreated(this._id.value, new Date(), { poNumber: this._poNumber, revision: this._revisionNumber }));
    return this._revisionNumber;
  }

  toState(): PurchaseOrderState {
    return { id: this._id.value, poNumber: this._poNumber, companyId: this._companyId,
      branchId: this._branchId, vendorId: this._vendorId, vendorName: this._vendorName,
      vendorTaxCode: this._vendorTaxCode, poType: this._poType, status: this._status,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      totalAmount: this._totalAmount, totalTax: this._totalTax, grandTotal: this._grandTotal,
      description: this._description, notes: this._notes, paymentTermCode: this._paymentTermCode,
      incoterm: this._incoterm, freightTerm: this._freightTerm, shipmentMethod: this._shipmentMethod,
      requestedDate: this._requestedDate, promisedDate: this._promisedDate,
      approvedAt: this._approvedAt, approvedBy: this._approvedBy,
      sentAt: this._sentAt, confirmedAt: this._confirmedAt, confirmedBy: this._confirmedBy,
      closedAt: this._closedAt, cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      holdReason: this._holdReason, revisionNumber: this._revisionNumber,
      sourceDocumentType: this._sourceDocumentType, sourceDocumentId: this._sourceDocumentId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
