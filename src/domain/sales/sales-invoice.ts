import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { SalesInvoiceId, InvoiceLineId } from "./sales-ids.js";
import { SlsInvoiceStatus, SlsInvoiceType } from "./sales-enums.js";
import { SalesInvoiceCreated, SalesInvoiceApproved, SalesInvoicePosted, SalesInvoiceCancelled, CreditNoteCreated, DebitNoteCreated } from "./sales-events.js";

export interface InvoiceLineState {
  id: string; invoiceId: string; orderLineId: string | null; deliveryLineId: string | null;
  lineNumber: number; itemId: string | null; itemCode: string; itemName: string;
  description: string | null; quantity: number; uom: string;
  unitPrice: number; totalPrice: number; currencyCode: string;
  discountPercent: number; discountAmount: number;
  taxCode: string | null; taxRate: number; taxAmount: number; netAmount: number;
  warehouseId: string | null; projectId: string | null; costCenterId: string | null;
  departmentId: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class InvoiceLine extends AggregateRoot<InvoiceLineId> {
  private _id: InvoiceLineId; private _invoiceId: string; private _orderLineId: string | null;
  private _deliveryLineId: string | null; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _discountPercent: number; private _discountAmount: number;
  private _taxCode: string | null; private _taxRate: number; private _taxAmount: number;
  private _netAmount: number; private _warehouseId: string | null;
  private _projectId: string | null; private _costCenterId: string | null;
  private _departmentId: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: InvoiceLineId, invoiceId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._invoiceId = invoiceId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantity * unitPrice; this._currencyCode = "VND";
    this._discountPercent = 0; this._discountAmount = 0; this._taxCode = null;
    this._taxRate = 0; this._taxAmount = 0; this._netAmount = this._totalPrice;
    this._orderLineId = null; this._deliveryLineId = null; this._itemId = null;
    this._description = null; this._warehouseId = null; this._projectId = null;
    this._costCenterId = null; this._departmentId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { invoiceId: string; lineNumber: number; itemCode: string; itemName: string; quantity: number; uom: string; unitPrice: number; orderLineId?: string; deliveryLineId?: string; itemId?: string; description?: string; taxCode?: string; taxRate?: number; discountPercent?: number; discountAmount?: number; warehouseId?: string; projectId?: string; costCenterId?: string; departmentId?: string }): InvoiceLine {
    const l = new InvoiceLine(InvoiceLineId.new(), p.invoiceId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.unitPrice);
    l._orderLineId = p.orderLineId ?? null; l._deliveryLineId = p.deliveryLineId ?? null;
    l._itemId = p.itemId ?? null; l._description = p.description ?? null;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    if (p.discountPercent) { l._discountPercent = p.discountPercent; l._discountAmount = Math.round(l._totalPrice * p.discountPercent / 100); }
    if (p.discountAmount) l._discountAmount = p.discountAmount;
    l._taxAmount = Math.round((l._totalPrice - l._discountAmount) * l._taxRate / 100);
    l._netAmount = l._totalPrice - l._discountAmount + l._taxAmount;
    l._warehouseId = p.warehouseId ?? null; l._projectId = p.projectId ?? null;
    l._costCenterId = p.costCenterId ?? null; l._departmentId = p.departmentId ?? null;
    return l;
  }

  static load(s: InvoiceLineState): InvoiceLine {
    const l = new InvoiceLine(new InvoiceLineId(s.id), s.invoiceId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.unitPrice);
    l._orderLineId = s.orderLineId; l._deliveryLineId = s.deliveryLineId; l._itemId = s.itemId;
    l._description = s.description; l._totalPrice = s.totalPrice; l._currencyCode = s.currencyCode;
    l._discountPercent = s.discountPercent; l._discountAmount = s.discountAmount;
    l._taxCode = s.taxCode; l._taxRate = s.taxRate; l._taxAmount = s.taxAmount;
    l._netAmount = s.netAmount; l._warehouseId = s.warehouseId; l._projectId = s.projectId;
    l._costCenterId = s.costCenterId; l._departmentId = s.departmentId;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt;
    l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): InvoiceLineId { return this._id; }
  get quantity(): number { return this._quantity; }
  get unitPrice(): number { return this._unitPrice; }
  get totalPrice(): number { return this._totalPrice; }
  get netAmount(): number { return this._netAmount; }
  get taxAmount(): number { return this._taxAmount; }
  get taxRate(): number { return this._taxRate; }
  get itemCode(): string { return this._itemCode; }

  toState(): InvoiceLineState {
    return { id: this._id.value, invoiceId: this._invoiceId, orderLineId: this._orderLineId,
      deliveryLineId: this._deliveryLineId, lineNumber: this._lineNumber, itemId: this._itemId,
      itemCode: this._itemCode, itemName: this._itemName, description: this._description,
      quantity: this._quantity, uom: this._uom, unitPrice: this._unitPrice,
      totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      discountPercent: this._discountPercent, discountAmount: this._discountAmount,
      taxCode: this._taxCode, taxRate: this._taxRate, taxAmount: this._taxAmount,
      netAmount: this._netAmount, warehouseId: this._warehouseId, projectId: this._projectId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}

export interface SalesInvoiceState {
  id: string; invoiceNumber: string; invoiceDate: Date; companyId: string; branchId: string | null;
  customerId: string; customerName: string; customerTaxCode: string | null; customerAddress: string | null;
  orderId: string | null; orderNumber: string | null; deliveryId: string | null; deliveryNumber: string | null;
  invoiceType: string; status: string;
  currencyCode: string; exchangeRate: number;
  subtotal: number; discountAmount: number; taxAmount: number; grandTotal: number;
  amountPaid: number; amountDue: number;
  einvoiceNumber: string | null; einvoiceCode: string | null; einvoiceIssueDate: Date | null;
  einvoiceVerifyCode: string | null; einvoiceStatus: string | null;
  approvedBy: string | null; approvedAt: Date | null;
  postedById: string | null; postedAt: Date | null;
  cancelledAt: Date | null; cancelReason: string | null;
  replacedById: string | null; adjustedInvoiceId: string | null;
  notes: string | null; glBatchId: string | null; postedToGL: boolean;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class SalesInvoice extends AggregateRoot<SalesInvoiceId> {
  private _id: SalesInvoiceId; private _invoiceNumber: string; private _invoiceDate: Date;
  private _companyId: string; private _branchId: string | null;
  private _customerId: string; private _customerName: string;
  private _customerTaxCode: string | null; private _customerAddress: string | null;
  private _orderId: string | null; private _orderNumber: string | null;
  private _deliveryId: string | null; private _deliveryNumber: string | null;
  private _invoiceType: SlsInvoiceType; private _status: SlsInvoiceStatus;
  private _currencyCode: string; private _exchangeRate: number;
  private _subtotal: number; private _discountAmount: number; private _taxAmount: number;
  private _grandTotal: number; private _amountPaid: number; private _amountDue: number;
  private _einvoiceNumber: string | null; private _einvoiceCode: string | null;
  private _einvoiceIssueDate: Date | null; private _einvoiceVerifyCode: string | null;
  private _einvoiceStatus: string | null;
  private _approvedBy: string | null; private _approvedAt: Date | null;
  private _postedById: string | null; private _postedAt: Date | null;
  private _cancelledAt: Date | null; private _cancelReason: string | null;
  private _replacedById: string | null; private _adjustedInvoiceId: string | null;
  private _notes: string | null; private _glBatchId: string | null; private _postedToGL: boolean;
  private _lines: InvoiceLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: SalesInvoiceId, invoiceNumber: string, companyId: string, customerId: string, customerName: string) {
    super(); this._id = id; this._invoiceNumber = invoiceNumber; this._companyId = companyId;
    this._customerId = customerId; this._customerName = customerName;
    this._invoiceType = SlsInvoiceType.salesInvoice; this._status = SlsInvoiceStatus.draft;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._subtotal = 0;
    this._discountAmount = 0; this._taxAmount = 0; this._grandTotal = 0;
    this._amountPaid = 0; this._amountDue = 0; this._invoiceDate = new Date();
    this._postedToGL = false;
    this._branchId = null; this._customerTaxCode = null; this._customerAddress = null;
    this._orderId = null; this._orderNumber = null; this._deliveryId = null;
    this._deliveryNumber = null; this._einvoiceNumber = null; this._einvoiceCode = null;
    this._einvoiceIssueDate = null; this._einvoiceVerifyCode = null; this._einvoiceStatus = null;
    this._approvedBy = null; this._approvedAt = null; this._postedById = null;
    this._postedAt = null; this._cancelledAt = null; this._cancelReason = null;
    this._replacedById = null; this._adjustedInvoiceId = null; this._notes = null;
    this._glBatchId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { invoiceNumber: string; companyId: string; customerId: string; customerName: string; branchId?: string; customerTaxCode?: string; customerAddress?: string; orderId?: string; orderNumber?: string; deliveryId?: string; deliveryNumber?: string; invoiceType?: SlsInvoiceType; currencyCode?: string; exchangeRate?: number; invoiceDate?: Date; notes?: string }): SalesInvoice {
    const i = new SalesInvoice(SalesInvoiceId.new(), p.invoiceNumber, p.companyId, p.customerId, p.customerName);
    i._branchId = p.branchId ?? null; i._customerTaxCode = p.customerTaxCode ?? null;
    i._customerAddress = p.customerAddress ?? null; i._orderId = p.orderId ?? null;
    i._orderNumber = p.orderNumber ?? null; i._deliveryId = p.deliveryId ?? null;
    i._deliveryNumber = p.deliveryNumber ?? null;
    i._invoiceType = p.invoiceType ?? SlsInvoiceType.salesInvoice;
    i._currencyCode = p.currencyCode ?? "VND"; i._exchangeRate = p.exchangeRate ?? 1;
    i._invoiceDate = p.invoiceDate ?? new Date(); i._notes = p.notes ?? null;
    i.addEvent(new SalesInvoiceCreated(i._id.value, new Date(), { invoiceNumber: i._invoiceNumber, customerId: i._customerId }));
    return i;
  }

  static load(s: SalesInvoiceState): SalesInvoice {
    const i = new SalesInvoice(new SalesInvoiceId(s.id), s.invoiceNumber, s.companyId, s.customerId, s.customerName);
    i._branchId = s.branchId; i._customerTaxCode = s.customerTaxCode;
    i._customerAddress = s.customerAddress; i._orderId = s.orderId; i._orderNumber = s.orderNumber;
    i._deliveryId = s.deliveryId; i._deliveryNumber = s.deliveryNumber;
    i._invoiceType = s.invoiceType as SlsInvoiceType; i._status = s.status as SlsInvoiceStatus;
    i._currencyCode = s.currencyCode; i._exchangeRate = s.exchangeRate;
    i._subtotal = s.subtotal; i._discountAmount = s.discountAmount; i._taxAmount = s.taxAmount;
    i._grandTotal = s.grandTotal; i._amountPaid = s.amountPaid; i._amountDue = s.amountDue;
    i._invoiceDate = s.invoiceDate; i._einvoiceNumber = s.einvoiceNumber;
    i._einvoiceCode = s.einvoiceCode; i._einvoiceIssueDate = s.einvoiceIssueDate;
    i._einvoiceVerifyCode = s.einvoiceVerifyCode; i._einvoiceStatus = s.einvoiceStatus;
    i._approvedBy = s.approvedBy; i._approvedAt = s.approvedAt;
    i._postedById = s.postedById; i._postedAt = s.postedAt;
    i._cancelledAt = s.cancelledAt; i._cancelReason = s.cancelReason;
    i._replacedById = s.replacedById; i._adjustedInvoiceId = s.adjustedInvoiceId;
    i._notes = s.notes; i._glBatchId = s.glBatchId; i._postedToGL = s.postedToGL;
    i._version = s.version; i._createdAt = s.createdAt; i._updatedAt = s.updatedAt;
    i._deletedAt = s.deletedAt;
    return i;
  }

  get id(): SalesInvoiceId { return this._id; }
  get invoiceNumber(): string { return this._invoiceNumber; }
  get status(): SlsInvoiceStatus { return this._status; }
  get customerId(): string { return this._customerId; }
  get subtotal(): number { return this._subtotal; }
  get grandTotal(): number { return this._grandTotal; }
  get amountPaid(): number { return this._amountPaid; }
  get amountDue(): number { return this._amountDue; }
  get lines(): InvoiceLine[] { return this._lines; }
  get invoiceType(): SlsInvoiceType { return this._invoiceType; }
  get version(): number { return this._version; }
  get orderId(): string | null { return this._orderId; }
  get postedToGL(): boolean { return this._postedToGL; }

  addLine(line: InvoiceLine): void {
    if (this._status !== SlsInvoiceStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft invoice");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._subtotal = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._taxAmount = this._lines.reduce((s, l) => s + l.taxAmount, 0);
    this._grandTotal = this._subtotal - this._discountAmount + this._taxAmount;
    this._amountDue = this._grandTotal - this._amountPaid;
  }

  submitForApproval(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot submit invoice with no lines");
    if (this._status !== SlsInvoiceStatus.draft && this._status !== SlsInvoiceStatus.issued) throw new DomainError("BusinessRule", "Only draft/issued invoice can be submitted");
    this._status = SlsInvoiceStatus.approved;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesInvoiceApproved(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  approve(approvedBy: string): void {
    if (this._status !== SlsInvoiceStatus.draft && this._status !== SlsInvoiceStatus.issued) throw new DomainError("BusinessRule", "Invoice not in submittable status");
    this._status = SlsInvoiceStatus.approved;
    this._approvedAt = new Date(); this._approvedBy = approvedBy;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesInvoiceApproved(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, approvedBy }));
  }

  post(postedById: string, glBatchId?: string): void {
    if (this._status !== SlsInvoiceStatus.approved) throw new DomainError("BusinessRule", "Only approved invoice can be posted");
    this._status = SlsInvoiceStatus.posted;
    this._postedById = postedById; this._postedAt = new Date();
    if (glBatchId) this._glBatchId = glBatchId;
    this._postedToGL = true;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesInvoicePosted(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, postedById }));
  }

  recordPayment(amount: number): void {
    this._amountPaid += amount;
    this._amountDue = this._grandTotal - this._amountPaid;
    if (this._amountDue <= 0) {
      this._status = SlsInvoiceStatus.fullyPaid;
    } else {
      this._status = SlsInvoiceStatus.partiallyPaid;
    }
    this._updatedAt = new Date(); this._version++;
  }

  cancel(reason: string): void {
    if (this._status === SlsInvoiceStatus.posted || this._status === SlsInvoiceStatus.fullyPaid) throw new DomainError("BusinessRule", "Cannot cancel posted/paid invoice. Use credit note.");
    this._status = SlsInvoiceStatus.cancelled;
    this._cancelledAt = new Date(); this._cancelReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesInvoiceCancelled(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, reason }));
  }

  createCreditNote(creditNoteNumber: string, reason: string): SalesInvoice {
    if (this._status !== SlsInvoiceStatus.posted && this._status !== SlsInvoiceStatus.fullyPaid && this._status !== SlsInvoiceStatus.partiallyPaid) throw new DomainError("BusinessRule", "Only posted/paid invoice can have credit note");
    const cn = SalesInvoice.create({
      invoiceNumber: creditNoteNumber, companyId: this._companyId,
      customerId: this._customerId, customerName: this._customerName,
      branchId: this._branchId ?? undefined, customerTaxCode: this._customerTaxCode ?? undefined,
      orderId: this._orderId ?? undefined, orderNumber: this._orderNumber ?? undefined,
      invoiceType: SlsInvoiceType.creditNote,
    });
    cn._adjustedInvoiceId = this._id.value;
    cn._notes = reason;
    cn.addEvent(new CreditNoteCreated(cn._id.value, new Date(), { invoiceNumber: creditNoteNumber, originalInvoice: this._invoiceNumber, reason }));
    return cn;
  }

  createDebitNote(debitNoteNumber: string, reason: string): SalesInvoice {
    const dn = SalesInvoice.create({
      invoiceNumber: debitNoteNumber, companyId: this._companyId,
      customerId: this._customerId, customerName: this._customerName,
      branchId: this._branchId ?? undefined, customerTaxCode: this._customerTaxCode ?? undefined,
      orderId: this._orderId ?? undefined, orderNumber: this._orderNumber ?? undefined,
      invoiceType: SlsInvoiceType.debitNote,
    });
    dn._adjustedInvoiceId = this._id.value;
    dn._notes = reason;
    dn.addEvent(new DebitNoteCreated(dn._id.value, new Date(), { invoiceNumber: debitNoteNumber, originalInvoice: this._invoiceNumber, reason }));
    return dn;
  }

  updateEinvoiceInfo(einvoiceNumber: string, einvoiceCode: string, verifyCode: string, issueDate: Date): void {
    this._einvoiceNumber = einvoiceNumber; this._einvoiceCode = einvoiceCode;
    this._einvoiceVerifyCode = verifyCode; this._einvoiceIssueDate = issueDate;
    this._einvoiceStatus = "issued";
    this._status = SlsInvoiceStatus.issued;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): SalesInvoiceState {
    return { id: this._id.value, invoiceNumber: this._invoiceNumber, invoiceDate: this._invoiceDate,
      companyId: this._companyId, branchId: this._branchId,
      customerId: this._customerId, customerName: this._customerName,
      customerTaxCode: this._customerTaxCode, customerAddress: this._customerAddress,
      orderId: this._orderId, orderNumber: this._orderNumber,
      deliveryId: this._deliveryId, deliveryNumber: this._deliveryNumber,
      invoiceType: this._invoiceType, status: this._status,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      subtotal: this._subtotal, discountAmount: this._discountAmount, taxAmount: this._taxAmount,
      grandTotal: this._grandTotal, amountPaid: this._amountPaid, amountDue: this._amountDue,
      einvoiceNumber: this._einvoiceNumber, einvoiceCode: this._einvoiceCode,
      einvoiceIssueDate: this._einvoiceIssueDate, einvoiceVerifyCode: this._einvoiceVerifyCode,
      einvoiceStatus: this._einvoiceStatus, approvedBy: this._approvedBy,
      approvedAt: this._approvedAt, postedById: this._postedById, postedAt: this._postedAt,
      cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      replacedById: this._replacedById, adjustedInvoiceId: this._adjustedInvoiceId,
      notes: this._notes, glBatchId: this._glBatchId, postedToGL: this._postedToGL,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
