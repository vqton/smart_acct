import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { GoodsReceiptId, ReceiptLineId, ReceiptReversalId } from "./purchasing-ids.js";
import { ReceiptStatus, InspectionStatus } from "./purchasing-enums.js";
import { GoodsReceiptCreated, GoodsReceiptReversed, ReturnToVendorCreated } from "./purchasing-events.js";

// ─── Goods Receipt Line ──────────────────────────────────────────────────────────

export interface ReceiptLineState {
  id: string; receiptId: string; poId: string; poLineId: string;
  lineNumber: number; itemId: string | null; itemCode: string; itemName: string;
  quantityOrdered: number; quantityReceived: number; quantityAccepted: number;
  quantityRejected: number; uom: string; unitPrice: number; totalPrice: number;
  currencyCode: string; warehouseId: string | null; locationId: string | null;
  batchNumber: string | null; serialNumber: string | null; expiryDate: Date | null;
  inspectionStatus: string; inspectionNotes: string | null;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class ReceiptLine extends AggregateRoot<ReceiptLineId> {
  private _id: ReceiptLineId; private _receiptId: string; private _poId: string;
  private _poLineId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _quantityOrdered: number; private _quantityReceived: number;
  private _quantityAccepted: number; private _quantityRejected: number;
  private _uom: string; private _unitPrice: number; private _totalPrice: number;
  private _currencyCode: string; private _warehouseId: string | null;
  private _locationId: string | null; private _batchNumber: string | null;
  private _serialNumber: string | null; private _expiryDate: Date | null;
  private _inspectionStatus: string; private _inspectionNotes: string | null;
  private _notes: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: ReceiptLineId, receiptId: string, poId: string, poLineId: string, lineNumber: number, itemCode: string, itemName: string, quantityReceived: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._receiptId = receiptId; this._poId = poId;
    this._poLineId = poLineId; this._lineNumber = lineNumber; this._itemCode = itemCode;
    this._itemName = itemName; this._quantityReceived = quantityReceived;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantityReceived * unitPrice;
    this._quantityOrdered = 0; this._quantityAccepted = quantityReceived;
    this._quantityRejected = 0; this._currencyCode = "VND";
    this._itemId = null; this._warehouseId = null; this._locationId = null;
    this._batchNumber = null; this._serialNumber = null; this._expiryDate = null;
    this._inspectionStatus = "pending"; this._inspectionNotes = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    receiptId: string; poId: string; poLineId: string; lineNumber: number;
    itemCode: string; itemName: string; quantityReceived: number; uom: string;
    unitPrice: number; itemId?: string; quantityOrdered?: number;
    warehouseId?: string; locationId?: string; batchNumber?: string;
    serialNumber?: string; expiryDate?: Date; notes?: string;
  }): ReceiptLine {
    const l = new ReceiptLine(ReceiptLineId.new(), p.receiptId, p.poId, p.poLineId, p.lineNumber, p.itemCode, p.itemName, p.quantityReceived, p.uom, p.unitPrice);
    l._itemId = p.itemId ?? null; l._quantityOrdered = p.quantityOrdered ?? 0;
    l._warehouseId = p.warehouseId ?? null; l._locationId = p.locationId ?? null;
    l._batchNumber = p.batchNumber ?? null; l._serialNumber = p.serialNumber ?? null;
    l._expiryDate = p.expiryDate ?? null; l._notes = p.notes ?? null;
    return l;
  }

  static load(s: ReceiptLineState): ReceiptLine {
    const l = new ReceiptLine(new ReceiptLineId(s.id), s.receiptId, s.poId, s.poLineId, s.lineNumber, s.itemCode, s.itemName, s.quantityReceived, s.uom, s.unitPrice);
    l._itemId = s.itemId; l._quantityOrdered = s.quantityOrdered; l._quantityAccepted = s.quantityAccepted;
    l._quantityRejected = s.quantityRejected; l._currencyCode = s.currencyCode;
    l._totalPrice = s.totalPrice; l._warehouseId = s.warehouseId; l._locationId = s.locationId;
    l._batchNumber = s.batchNumber; l._serialNumber = s.serialNumber; l._expiryDate = s.expiryDate;
    l._inspectionStatus = s.inspectionStatus; l._inspectionNotes = s.inspectionNotes; l._notes = s.notes;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): ReceiptLineId { return this._id; }
  get quantityReceived(): number { return this._quantityReceived; }
  get quantityAccepted(): number { return this._quantityAccepted; }
  get totalPrice(): number { return this._totalPrice; }
  get poLineId(): string { return this._poLineId; }
  get version(): number { return this._version; }

  accept(qty: number): void {
    if (qty > this._quantityReceived) throw new DomainError("Validation", "Cannot accept more than received");
    this._quantityAccepted = qty;
    this._quantityRejected = this._quantityReceived - qty;
    this._inspectionStatus = qty === 0 ? "failed" : qty < this._quantityReceived ? "partial_pass" : "passed";
    this._updatedAt = new Date(); this._version++;
  }

  reject(qty: number, reason: string): void {
    if (qty > this._quantityReceived) throw new DomainError("Validation", "Cannot reject more than received");
    this._quantityRejected = qty;
    this._quantityAccepted = this._quantityReceived - qty;
    this._inspectionStatus = this._quantityAccepted === 0 ? "failed" : "partial_pass";
    this._inspectionNotes = reason;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): ReceiptLineState {
    return { id: this._id.value, receiptId: this._receiptId, poId: this._poId,
      poLineId: this._poLineId, lineNumber: this._lineNumber, itemId: this._itemId,
      itemCode: this._itemCode, itemName: this._itemName, quantityOrdered: this._quantityOrdered,
      quantityReceived: this._quantityReceived, quantityAccepted: this._quantityAccepted,
      quantityRejected: this._quantityRejected, uom: this._uom, unitPrice: this._unitPrice,
      totalPrice: this._totalPrice, currencyCode: this._currencyCode, warehouseId: this._warehouseId,
      locationId: this._locationId, batchNumber: this._batchNumber, serialNumber: this._serialNumber,
      expiryDate: this._expiryDate, inspectionStatus: this._inspectionStatus,
      inspectionNotes: this._inspectionNotes, notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Goods Receipt ───────────────────────────────────────────────────────────────

export interface GoodsReceiptState {
  id: string; receiptNumber: string; companyId: string; branchId: string | null;
  warehouseId: string | null; vendorId: string; vendorName: string;
  poId: string; poNumber: string; receiptType: string;
  status: string; currencyCode: string;
  totalAmount: number; notes: string | null;
  receiptDate: Date; receivedBy: string;
  reversedAt: Date | null; reverseReason: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class GoodsReceipt extends AggregateRoot<GoodsReceiptId> {
  private _id: GoodsReceiptId; private _receiptNumber: string; private _companyId: string;
  private _branchId: string | null; private _warehouseId: string | null;
  private _vendorId: string; private _vendorName: string; private _poId: string;
  private _poNumber: string; private _receiptType: string; private _status: string;
  private _currencyCode: string; private _totalAmount: number;
  private _notes: string | null; private _receiptDate: Date; private _receivedBy: string;
  private _lines: ReceiptLine[] = [];
  private _reversedAt: Date | null; private _reverseReason: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: GoodsReceiptId, receiptNumber: string, companyId: string, vendorId: string, vendorName: string, poId: string, poNumber: string, receiptDate: Date, receivedBy: string) {
    super(); this._id = id; this._receiptNumber = receiptNumber; this._companyId = companyId;
    this._vendorId = vendorId; this._vendorName = vendorName; this._poId = poId;
    this._poNumber = poNumber; this._receiptDate = receiptDate; this._receivedBy = receivedBy;
    this._status = "fully_received"; this._receiptType = "standard";
    this._currencyCode = "VND"; this._totalAmount = 0; this._branchId = null;
    this._warehouseId = null; this._notes = null; this._reversedAt = null; this._reverseReason = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    receiptNumber: string; companyId: string; vendorId: string; vendorName: string;
    poId: string; poNumber: string; receiptDate: Date; receivedBy: string;
    branchId?: string; warehouseId?: string; receiptType?: string;
    currencyCode?: string; notes?: string;
  }): GoodsReceipt {
    const gr = new GoodsReceipt(GoodsReceiptId.new(), p.receiptNumber, p.companyId, p.vendorId, p.vendorName, p.poId, p.poNumber, p.receiptDate, p.receivedBy);
    gr._branchId = p.branchId ?? null; gr._warehouseId = p.warehouseId ?? null;
    gr._receiptType = p.receiptType ?? "standard"; gr._currencyCode = p.currencyCode ?? "VND";
    gr._notes = p.notes ?? null;
    gr.addEvent(new GoodsReceiptCreated(gr._id.value, new Date(), { receiptNumber: gr._receiptNumber, poNumber: gr._poNumber }));
    return gr;
  }

  static load(s: GoodsReceiptState): GoodsReceipt {
    const gr = new GoodsReceipt(new GoodsReceiptId(s.id), s.receiptNumber, s.companyId, s.vendorId, s.vendorName, s.poId, s.poNumber, s.receiptDate, s.receivedBy);
    gr._branchId = s.branchId; gr._warehouseId = s.warehouseId; gr._receiptType = s.receiptType;
    gr._status = s.status; gr._currencyCode = s.currencyCode; gr._totalAmount = s.totalAmount;
    gr._notes = s.notes; gr._reversedAt = s.reversedAt; gr._reverseReason = s.reverseReason;
    gr._version = s.version; gr._createdAt = s.createdAt; gr._updatedAt = s.updatedAt; gr._deletedAt = s.deletedAt;
    return gr;
  }

  get id(): GoodsReceiptId { return this._id; }
  get receiptNumber(): string { return this._receiptNumber; }
  get poId(): string { return this._poId; }
  get lines(): ReceiptLine[] { return this._lines; }
  get status(): string { return this._status; }
  get version(): number { return this._version; }

  addLine(line: ReceiptLine): void {
    if (this._status === "reversed") throw new DomainError("BusinessRule", "Cannot add lines to reversed receipt");
    this._lines.push(line);
    this._totalAmount = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._updatedAt = new Date(); this._version++;
  }

  reverse(reason: string): void {
    if (this._status === "reversed") throw new DomainError("BusinessRule", "Receipt already reversed");
    this._status = "reversed";
    this._reversedAt = new Date(); this._reverseReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new GoodsReceiptReversed(this._id.value, new Date(), { receiptNumber: this._receiptNumber, reason }));
  }

  toState(): GoodsReceiptState {
    return { id: this._id.value, receiptNumber: this._receiptNumber, companyId: this._companyId,
      branchId: this._branchId, warehouseId: this._warehouseId, vendorId: this._vendorId,
      vendorName: this._vendorName, poId: this._poId, poNumber: this._poNumber,
      receiptType: this._receiptType, status: this._status, currencyCode: this._currencyCode,
      totalAmount: this._totalAmount, notes: this._notes, receiptDate: this._receiptDate,
      receivedBy: this._receivedBy, reversedAt: this._reversedAt, reverseReason: this._reverseReason,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
