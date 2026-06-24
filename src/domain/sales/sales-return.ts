import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { SalesReturnId, ReturnLineId } from "./sales-ids.js";
import { SlsReturnStatus, SlsReturnReason } from "./sales-enums.js";
import { SalesReturnCreated, SalesReturnApproved, SalesReturnCompleted } from "./sales-events.js";

export interface ReturnLineState {
  id: string; returnId: string; orderLineId: string | null; invoiceLineId: string | null;
  deliveryLineId: string | null; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string;
  quantityOrdered: number; quantityReturned: number; quantityAccepted: number; quantityRejected: number;
  uom: string; unitPrice: number; totalPrice: number; currencyCode: string;
  discountPercent: number; discountAmount: number; taxCode: string | null;
  taxRate: number; taxAmount: number; netAmount: number;
  condition: string | null; damageDescription: string | null;
  disposition: string; warehouseId: string | null;
  batchNumber: string | null; serialNumber: string | null; expiryDate: Date | null;
  projectId: string | null; costCenterId: string | null; departmentId: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class ReturnLine extends AggregateRoot<ReturnLineId> {
  private _id: ReturnLineId; private _returnId: string; private _orderLineId: string | null;
  private _invoiceLineId: string | null; private _deliveryLineId: string | null;
  private _lineNumber: number; private _itemId: string | null; private _itemCode: string;
  private _itemName: string; private _quantityOrdered: number; private _quantityReturned: number;
  private _quantityAccepted: number; private _quantityRejected: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _discountPercent: number; private _discountAmount: number;
  private _taxCode: string | null; private _taxRate: number; private _taxAmount: number;
  private _netAmount: number; private _condition: string | null;
  private _damageDescription: string | null; private _disposition: string;
  private _warehouseId: string | null; private _batchNumber: string | null;
  private _serialNumber: string | null; private _expiryDate: Date | null;
  private _projectId: string | null; private _costCenterId: string | null;
  private _departmentId: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: ReturnLineId, returnId: string, lineNumber: number, itemCode: string, itemName: string, quantityReturned: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._returnId = returnId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantityReturned = quantityReturned;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantityReturned * unitPrice; this._currencyCode = "VND";
    this._discountPercent = 0; this._discountAmount = 0; this._taxCode = null;
    this._taxRate = 0; this._taxAmount = 0; this._netAmount = this._totalPrice;
    this._quantityOrdered = 0; this._quantityAccepted = 0; this._quantityRejected = 0;
    this._orderLineId = null; this._invoiceLineId = null; this._deliveryLineId = null;
    this._itemId = null; this._condition = null; this._damageDescription = null;
    this._disposition = "return_to_stock"; this._warehouseId = null;
    this._batchNumber = null; this._serialNumber = null; this._expiryDate = null;
    this._projectId = null; this._costCenterId = null; this._departmentId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { returnId: string; lineNumber: number; itemCode: string; itemName: string; quantityReturned: number; uom: string; unitPrice: number; orderLineId?: string; invoiceLineId?: string; deliveryLineId?: string; itemId?: string; quantityOrdered?: number; taxCode?: string; taxRate?: number; discountPercent?: number; discountAmount?: number; condition?: string; damageDescription?: string; disposition?: string; warehouseId?: string; batchNumber?: string; serialNumber?: string; expiryDate?: Date; projectId?: string; costCenterId?: string; departmentId?: string }): ReturnLine {
    const l = new ReturnLine(ReturnLineId.new(), p.returnId, p.lineNumber, p.itemCode, p.itemName, p.quantityReturned, p.uom, p.unitPrice);
    l._orderLineId = p.orderLineId ?? null; l._invoiceLineId = p.invoiceLineId ?? null;
    l._deliveryLineId = p.deliveryLineId ?? null; l._itemId = p.itemId ?? null;
    l._quantityOrdered = p.quantityOrdered ?? 0; l._taxCode = p.taxCode ?? null;
    l._taxRate = p.taxRate ?? 0;
    if (p.discountPercent) { l._discountPercent = p.discountPercent; l._discountAmount = Math.round(l._totalPrice * p.discountPercent / 100); }
    if (p.discountAmount) l._discountAmount = p.discountAmount;
    l._taxAmount = Math.round((l._totalPrice - l._discountAmount) * l._taxRate / 100);
    l._netAmount = l._totalPrice - l._discountAmount + l._taxAmount;
    l._condition = p.condition ?? null; l._damageDescription = p.damageDescription ?? null;
    l._disposition = p.disposition ?? "return_to_stock"; l._warehouseId = p.warehouseId ?? null;
    l._batchNumber = p.batchNumber ?? null; l._serialNumber = p.serialNumber ?? null;
    l._expiryDate = p.expiryDate ?? null; l._projectId = p.projectId ?? null;
    l._costCenterId = p.costCenterId ?? null; l._departmentId = p.departmentId ?? null;
    return l;
  }

  static load(s: ReturnLineState): ReturnLine {
    const l = new ReturnLine(new ReturnLineId(s.id), s.returnId, s.lineNumber, s.itemCode, s.itemName, s.quantityReturned, s.uom, s.unitPrice);
    l._orderLineId = s.orderLineId; l._invoiceLineId = s.invoiceLineId;
    l._deliveryLineId = s.deliveryLineId; l._itemId = s.itemId;
    l._quantityOrdered = s.quantityOrdered; l._quantityAccepted = s.quantityAccepted;
    l._quantityRejected = s.quantityRejected; l._totalPrice = s.totalPrice;
    l._currencyCode = s.currencyCode; l._discountPercent = s.discountPercent;
    l._discountAmount = s.discountAmount; l._taxCode = s.taxCode; l._taxRate = s.taxRate;
    l._taxAmount = s.taxAmount; l._netAmount = s.netAmount; l._condition = s.condition;
    l._damageDescription = s.damageDescription; l._disposition = s.disposition;
    l._warehouseId = s.warehouseId; l._batchNumber = s.batchNumber;
    l._serialNumber = s.serialNumber; l._expiryDate = s.expiryDate;
    l._projectId = s.projectId; l._costCenterId = s.costCenterId;
    l._departmentId = s.departmentId; l._version = s.version; l._createdAt = s.createdAt;
    l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): ReturnLineId { return this._id; }
  get quantityReturned(): number { return this._quantityReturned; }
  get netAmount(): number { return this._netAmount; }
  get totalPrice(): number { return this._totalPrice; }
  get taxAmount(): number { return this._taxAmount; }
  get discountAmount(): number { return this._discountAmount; }
  get itemCode(): string { return this._itemCode; }

  toState(): ReturnLineState {
    return { id: this._id.value, returnId: this._returnId, orderLineId: this._orderLineId,
      invoiceLineId: this._invoiceLineId, deliveryLineId: this._deliveryLineId,
      lineNumber: this._lineNumber, itemId: this._itemId, itemCode: this._itemCode,
      itemName: this._itemName, quantityOrdered: this._quantityOrdered,
      quantityReturned: this._quantityReturned, quantityAccepted: this._quantityAccepted,
      quantityRejected: this._quantityRejected, uom: this._uom, unitPrice: this._unitPrice,
      totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      discountPercent: this._discountPercent, discountAmount: this._discountAmount,
      taxCode: this._taxCode, taxRate: this._taxRate, taxAmount: this._taxAmount,
      netAmount: this._netAmount, condition: this._condition,
      damageDescription: this._damageDescription, disposition: this._disposition,
      warehouseId: this._warehouseId, batchNumber: this._batchNumber,
      serialNumber: this._serialNumber, expiryDate: this._expiryDate,
      projectId: this._projectId, costCenterId: this._costCenterId,
      departmentId: this._departmentId, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

export interface SalesReturnState {
  id: string; returnNumber: string; companyId: string; branchId: string | null;
  customerId: string; customerName: string;
  orderId: string | null; orderNumber: string | null;
  invoiceId: string | null; invoiceNumber: string | null;
  deliveryId: string | null; deliveryNumber: string | null;
  returnType: string; returnReason: string; reasonDetail: string | null; status: string;
  currencyCode: string; exchangeRate: number;
  subtotal: number; discountAmount: number; taxAmount: number; grandTotal: number; refundAmount: number;
  approvedBy: string | null; approvedAt: Date | null;
  receivedAt: Date | null; inspectedAt: Date | null;
  inspectionResult: string | null; inspectionNotes: string | null;
  notes: string | null; glBatchId: string | null; postedToGL: boolean;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class SalesReturn extends AggregateRoot<SalesReturnId> {
  private _id: SalesReturnId; private _returnNumber: string; private _companyId: string;
  private _branchId: string | null; private _customerId: string; private _customerName: string;
  private _orderId: string | null; private _orderNumber: string | null;
  private _invoiceId: string | null; private _invoiceNumber: string | null;
  private _deliveryId: string | null; private _deliveryNumber: string | null;
  private _returnType: string; private _returnReason: SlsReturnReason;
  private _reasonDetail: string | null; private _status: SlsReturnStatus;
  private _currencyCode: string; private _exchangeRate: number;
  private _subtotal: number; private _discountAmount: number; private _taxAmount: number;
  private _grandTotal: number; private _refundAmount: number;
  private _approvedBy: string | null; private _approvedAt: Date | null;
  private _receivedAt: Date | null; private _inspectedAt: Date | null;
  private _inspectionResult: string | null; private _inspectionNotes: string | null;
  private _lines: ReturnLine[] = [];
  private _notes: string | null; private _glBatchId: string | null; private _postedToGL: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: SalesReturnId, returnNumber: string, companyId: string, customerId: string, customerName: string) {
    super(); this._id = id; this._returnNumber = returnNumber; this._companyId = companyId;
    this._customerId = customerId; this._customerName = customerName;
    this._returnType = "standard"; this._status = SlsReturnStatus.draft;
    this._returnReason = SlsReturnReason.other;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._subtotal = 0;
    this._discountAmount = 0; this._taxAmount = 0; this._grandTotal = 0; this._refundAmount = 0;
    this._postedToGL = false;
    this._branchId = null; this._orderId = null; this._orderNumber = null;
    this._invoiceId = null; this._invoiceNumber = null; this._deliveryId = null;
    this._deliveryNumber = null; this._reasonDetail = null;
    this._approvedBy = null; this._approvedAt = null; this._receivedAt = null;
    this._inspectedAt = null; this._inspectionResult = null; this._inspectionNotes = null;
    this._notes = null; this._glBatchId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { returnNumber: string; companyId: string; customerId: string; customerName: string; branchId?: string; orderId?: string; orderNumber?: string; invoiceId?: string; invoiceNumber?: string; deliveryId?: string; deliveryNumber?: string; returnType?: string; returnReason: SlsReturnReason; reasonDetail?: string; currencyCode?: string; exchangeRate?: number; notes?: string }): SalesReturn {
    const r = new SalesReturn(SalesReturnId.new(), p.returnNumber, p.companyId, p.customerId, p.customerName);
    r._branchId = p.branchId ?? null; r._orderId = p.orderId ?? null;
    r._orderNumber = p.orderNumber ?? null; r._invoiceId = p.invoiceId ?? null;
    r._invoiceNumber = p.invoiceNumber ?? null; r._deliveryId = p.deliveryId ?? null;
    r._deliveryNumber = p.deliveryNumber ?? null; r._returnType = p.returnType ?? "standard";
    r._returnReason = p.returnReason; r._reasonDetail = p.reasonDetail ?? null;
    r._currencyCode = p.currencyCode ?? "VND"; r._exchangeRate = p.exchangeRate ?? 1;
    r._notes = p.notes ?? null;
    r.addEvent(new SalesReturnCreated(r._id.value, new Date(), { returnNumber: r._returnNumber, customerId: r._customerId }));
    return r;
  }

  static load(s: SalesReturnState): SalesReturn {
    const r = new SalesReturn(new SalesReturnId(s.id), s.returnNumber, s.companyId, s.customerId, s.customerName);
    r._branchId = s.branchId; r._orderId = s.orderId; r._orderNumber = s.orderNumber;
    r._invoiceId = s.invoiceId; r._invoiceNumber = s.invoiceNumber;
    r._deliveryId = s.deliveryId; r._deliveryNumber = s.deliveryNumber;
    r._returnType = s.returnType; r._returnReason = s.returnReason as SlsReturnReason;
    r._reasonDetail = s.reasonDetail; r._status = s.status as SlsReturnStatus;
    r._currencyCode = s.currencyCode; r._exchangeRate = s.exchangeRate;
    r._subtotal = s.subtotal; r._discountAmount = s.discountAmount; r._taxAmount = s.taxAmount;
    r._grandTotal = s.grandTotal; r._refundAmount = s.refundAmount;
    r._approvedBy = s.approvedBy; r._approvedAt = s.approvedAt;
    r._receivedAt = s.receivedAt; r._inspectedAt = s.inspectedAt;
    r._inspectionResult = s.inspectionResult; r._inspectionNotes = s.inspectionNotes;
    r._notes = s.notes; r._glBatchId = s.glBatchId; r._postedToGL = s.postedToGL;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt;
    r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): SalesReturnId { return this._id; }
  get returnNumber(): string { return this._returnNumber; }
  get status(): SlsReturnStatus { return this._status; }
  get customerId(): string { return this._customerId; }
  get lines(): ReturnLine[] { return this._lines; }
  get grandTotal(): number { return this._grandTotal; }
  get version(): number { return this._version; }

  addLine(line: ReturnLine): void {
    if (this._status !== SlsReturnStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft return");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._subtotal = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._taxAmount = this._lines.reduce((s, l) => s + l.taxAmount, 0);
    this._grandTotal = this._subtotal - this._discountAmount + this._taxAmount;
    this._refundAmount = this._grandTotal;
  }

  submitForApproval(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot submit return with no lines");
    if (this._status !== SlsReturnStatus.draft) throw new DomainError("BusinessRule", "Only draft return can be submitted");
    this._status = SlsReturnStatus.pendingApproval;
    this._updatedAt = new Date(); this._version++;
  }

  approve(approvedBy: string): void {
    if (this._status !== SlsReturnStatus.pendingApproval) throw new DomainError("BusinessRule", "Return not pending approval");
    this._status = SlsReturnStatus.approved;
    this._approvedAt = new Date(); this._approvedBy = approvedBy;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesReturnApproved(this._id.value, new Date(), { returnNumber: this._returnNumber, approvedBy }));
  }

  recordReceipt(): void {
    if (this._status !== SlsReturnStatus.approved) throw new DomainError("BusinessRule", "Only approved return can be received");
    this._status = SlsReturnStatus.received;
    this._receivedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  recordInspection(result: string, notes?: string): void {
    if (this._status !== SlsReturnStatus.received) throw new DomainError("BusinessRule", "Only received return can be inspected");
    this._status = SlsReturnStatus.inspected;
    this._inspectedAt = new Date(); this._inspectionResult = result;
    this._inspectionNotes = notes ?? null;
    this._updatedAt = new Date(); this._version++;
  }

  complete(): void {
    this._status = SlsReturnStatus.completed;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesReturnCompleted(this._id.value, new Date(), { returnNumber: this._returnNumber }));
  }

  cancel(): void {
    if (this._status === SlsReturnStatus.completed || this._status === SlsReturnStatus.fullyRefunded) throw new DomainError("BusinessRule", "Cannot cancel completed/refunded return");
    this._status = SlsReturnStatus.cancelled;
    this._updatedAt = new Date(); this._version++;
  }

  setRefundAmount(amount: number): void {
    if (amount > this._grandTotal) throw new DomainError("BusinessRule", "Refund cannot exceed return total");
    this._refundAmount = amount;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): SalesReturnState {
    return { id: this._id.value, returnNumber: this._returnNumber, companyId: this._companyId,
      branchId: this._branchId, customerId: this._customerId, customerName: this._customerName,
      orderId: this._orderId, orderNumber: this._orderNumber,
      invoiceId: this._invoiceId, invoiceNumber: this._invoiceNumber,
      deliveryId: this._deliveryId, deliveryNumber: this._deliveryNumber,
      returnType: this._returnType, returnReason: this._returnReason,
      reasonDetail: this._reasonDetail, status: this._status,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      subtotal: this._subtotal, discountAmount: this._discountAmount, taxAmount: this._taxAmount,
      grandTotal: this._grandTotal, refundAmount: this._refundAmount,
      approvedBy: this._approvedBy, approvedAt: this._approvedAt,
      receivedAt: this._receivedAt, inspectedAt: this._inspectedAt,
      inspectionResult: this._inspectionResult, inspectionNotes: this._inspectionNotes,
      notes: this._notes, glBatchId: this._glBatchId, postedToGL: this._postedToGL,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
