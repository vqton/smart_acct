import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { SupplierInvoiceId, InvoiceLineId, DebitMemoId, CreditMemoId, PrepaymentId, PaymentScheduleId } from "./purchasing-ids.js";
import { InvoiceStatus, InvoiceMatchStatus, PaymentStatus, MatchingRule } from "./purchasing-enums.js";
import {
  SupplierInvoiceRegistered, SupplierInvoiceVerified, SupplierInvoiceMatched,
  InvoiceMatchingException, CreditMemoCreated, DebitMemoCreated,
  PrepaymentCreated, PrepaymentApplied, PaymentScheduled, PaymentHoldApplied,
} from "./purchasing-events.js";

// ─── Invoice Line ────────────────────────────────────────────────────────────────

export interface InvoiceLineState {
  id: string; invoiceId: string; lineNumber: number;
  poId: string | null; poLineId: string | null;
  itemId: string | null; itemCode: string; itemName: string;
  quantity: number; uom: string; unitPrice: number; totalPrice: number;
  taxCode: string | null; taxRate: number; taxAmount: number;
  currencyCode: string;
  matchedQuantity: number; matchedAmount: number; matchStatus: string;
  projectId: string | null; costCenterId: string | null;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class InvoiceLine extends AggregateRoot<InvoiceLineId> {
  private _id: InvoiceLineId; private _invoiceId: string; private _lineNumber: number;
  private _poId: string | null; private _poLineId: string | null;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _quantity: number; private _uom: string; private _unitPrice: number;
  private _totalPrice: number; private _taxCode: string | null; private _taxRate: number;
  private _taxAmount: number; private _currencyCode: string;
  private _matchedQuantity: number; private _matchedAmount: number;
  private _matchStatus: string; private _projectId: string | null;
  private _costCenterId: string | null; private _notes: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: InvoiceLineId, invoiceId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._invoiceId = invoiceId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._unitPrice = unitPrice; this._totalPrice = quantity * unitPrice;
    this._taxCode = null; this._taxRate = 0; this._taxAmount = 0;
    this._currencyCode = "VND"; this._matchedQuantity = 0; this._matchedAmount = 0;
    this._matchStatus = "unmatched"; this._poId = null; this._poLineId = null;
    this._itemId = null; this._projectId = null; this._costCenterId = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    invoiceId: string; lineNumber: number; itemCode: string; itemName: string;
    quantity: number; uom: string; unitPrice: number; poId?: string; poLineId?: string;
    itemId?: string; taxCode?: string; taxRate?: number; projectId?: string;
    costCenterId?: string; notes?: string;
  }): InvoiceLine {
    const l = new InvoiceLine(InvoiceLineId.new(), p.invoiceId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.unitPrice);
    l._poId = p.poId ?? null; l._poLineId = p.poLineId ?? null; l._itemId = p.itemId ?? null;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    l._taxAmount = l._totalPrice * (l._taxRate / 100);
    l._projectId = p.projectId ?? null; l._costCenterId = p.costCenterId ?? null; l._notes = p.notes ?? null;
    return l;
  }

  static load(s: InvoiceLineState): InvoiceLine {
    const l = new InvoiceLine(new InvoiceLineId(s.id), s.invoiceId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.unitPrice);
    l._poId = s.poId; l._poLineId = s.poLineId; l._itemId = s.itemId; l._totalPrice = s.totalPrice;
    l._taxCode = s.taxCode; l._taxRate = s.taxRate; l._taxAmount = s.taxAmount;
    l._currencyCode = s.currencyCode; l._matchedQuantity = s.matchedQuantity;
    l._matchedAmount = s.matchedAmount; l._matchStatus = s.matchStatus;
    l._projectId = s.projectId; l._costCenterId = s.costCenterId; l._notes = s.notes;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt; l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): InvoiceLineId { return this._id; }
  get quantity(): number { return this._quantity; }
  get unitPrice(): number { return this._unitPrice; }
  get totalPrice(): number { return this._totalPrice; }
  get taxAmount(): number { return this._taxAmount; }
  get poLineId(): string | null { return this._poLineId; }
  get matchedQuantity(): number { return this._matchedQuantity; }
  get version(): number { return this._version; }

  updateMatch(qty: number, amount: number, status: string): void {
    this._matchedQuantity = qty;
    this._matchedAmount = amount;
    this._matchStatus = status;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): InvoiceLineState {
    return { id: this._id.value, invoiceId: this._invoiceId, lineNumber: this._lineNumber,
      poId: this._poId, poLineId: this._poLineId, itemId: this._itemId, itemCode: this._itemCode,
      itemName: this._itemName, quantity: this._quantity, uom: this._uom, unitPrice: this._unitPrice,
      totalPrice: this._totalPrice, taxCode: this._taxCode, taxRate: this._taxRate,
      taxAmount: this._taxAmount, currencyCode: this._currencyCode, matchedQuantity: this._matchedQuantity,
      matchedAmount: this._matchedAmount, matchStatus: this._matchStatus, projectId: this._projectId,
      costCenterId: this._costCenterId, notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Supplier Invoice ────────────────────────────────────────────────────────────

export interface SupplierInvoiceState {
  id: string; invoiceNumber: string; invoiceDate: Date; companyId: string;
  branchId: string | null; vendorId: string; vendorName: string; vendorTaxCode: string | null;
  poId: string | null; poNumber: string | null;
  status: string; matchStatus: string; matchingRule: string;
  currencyCode: string; exchangeRate: number;
  totalAmount: number; totalTax: number; grandTotal: number;
  amountPaid: number; amountDue: number;
  paymentStatus: string; paymentTermCode: string | null; dueDate: Date | null;
  description: string | null; notes: string | null;
  holdReason: string | null;
  approvedAt: Date | null; approvedBy: string | null;
  paidAt: Date | null; cancelledAt: Date | null; cancelReason: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class SupplierInvoice extends AggregateRoot<SupplierInvoiceId> {
  private _id: SupplierInvoiceId; private _invoiceNumber: string; private _invoiceDate: Date;
  private _companyId: string; private _branchId: string | null;
  private _vendorId: string; private _vendorName: string; private _vendorTaxCode: string | null;
  private _poId: string | null; private _poNumber: string | null;
  private _status: InvoiceStatus; private _matchStatus: string;
  private _matchingRule: string; private _currencyCode: string;
  private _exchangeRate: number; private _totalAmount: number;
  private _totalTax: number; private _grandTotal: number;
  private _amountPaid: number; private _amountDue: number;
  private _paymentStatus: string; private _paymentTermCode: string | null;
  private _dueDate: Date | null; private _description: string | null;
  private _notes: string | null; private _holdReason: string | null;
  private _approvedAt: Date | null; private _approvedBy: string | null;
  private _paidAt: Date | null; private _cancelledAt: Date | null;
  private _cancelReason: string | null;
  private _lines: InvoiceLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: SupplierInvoiceId, invoiceNumber: string, invoiceDate: Date, companyId: string, vendorId: string, vendorName: string) {
    super(); this._id = id; this._invoiceNumber = invoiceNumber; this._invoiceDate = invoiceDate;
    this._companyId = companyId; this._vendorId = vendorId; this._vendorName = vendorName;
    this._status = InvoiceStatus.draft; this._matchStatus = "unmatched";
    this._matchingRule = "three_way"; this._currencyCode = "VND"; this._exchangeRate = 1;
    this._totalAmount = 0; this._totalTax = 0; this._grandTotal = 0;
    this._amountPaid = 0; this._amountDue = 0; this._paymentStatus = "pending";
    this._branchId = null; this._vendorTaxCode = null; this._poId = null; this._poNumber = null;
    this._paymentTermCode = null; this._dueDate = null; this._description = null;
    this._notes = null; this._holdReason = null; this._approvedAt = null;
    this._approvedBy = null; this._paidAt = null; this._cancelledAt = null; this._cancelReason = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    invoiceNumber: string; invoiceDate: Date; companyId: string; vendorId: string; vendorName: string;
    branchId?: string; vendorTaxCode?: string; poId?: string; poNumber?: string;
    matchingRule?: string; currencyCode?: string; exchangeRate?: number;
    paymentTermCode?: string; dueDate?: Date; description?: string; notes?: string;
  }): SupplierInvoice {
    const inv = new SupplierInvoice(SupplierInvoiceId.new(), p.invoiceNumber, p.invoiceDate, p.companyId, p.vendorId, p.vendorName);
    inv._branchId = p.branchId ?? null; inv._vendorTaxCode = p.vendorTaxCode ?? null;
    inv._poId = p.poId ?? null; inv._poNumber = p.poNumber ?? null;
    inv._matchingRule = p.matchingRule ?? "three_way";
    inv._currencyCode = p.currencyCode ?? "VND"; inv._exchangeRate = p.exchangeRate ?? 1;
    inv._paymentTermCode = p.paymentTermCode ?? null; inv._dueDate = p.dueDate ?? null;
    inv._description = p.description ?? null; inv._notes = p.notes ?? null;
    inv.addEvent(new SupplierInvoiceRegistered(inv._id.value, new Date(), { invoiceNumber: inv._invoiceNumber, vendorId: inv._vendorId }));
    return inv;
  }

  static load(s: SupplierInvoiceState): SupplierInvoice {
    const inv = new SupplierInvoice(new SupplierInvoiceId(s.id), s.invoiceNumber, s.invoiceDate, s.companyId, s.vendorId, s.vendorName);
    inv._branchId = s.branchId; inv._vendorTaxCode = s.vendorTaxCode;
    inv._poId = s.poId; inv._poNumber = s.poNumber; inv._status = s.status as InvoiceStatus;
    inv._matchStatus = s.matchStatus; inv._matchingRule = s.matchingRule;
    inv._currencyCode = s.currencyCode; inv._exchangeRate = s.exchangeRate;
    inv._totalAmount = s.totalAmount; inv._totalTax = s.totalTax; inv._grandTotal = s.grandTotal;
    inv._amountPaid = s.amountPaid; inv._amountDue = s.amountDue;
    inv._paymentStatus = s.paymentStatus; inv._paymentTermCode = s.paymentTermCode;
    inv._dueDate = s.dueDate; inv._description = s.description; inv._notes = s.notes;
    inv._holdReason = s.holdReason; inv._approvedAt = s.approvedAt; inv._approvedBy = s.approvedBy;
    inv._paidAt = s.paidAt; inv._cancelledAt = s.cancelledAt; inv._cancelReason = s.cancelReason;
    inv._version = s.version; inv._createdAt = s.createdAt; inv._updatedAt = s.updatedAt; inv._deletedAt = s.deletedAt;
    return inv;
  }

  get id(): SupplierInvoiceId { return this._id; }
  get invoiceNumber(): string { return this._invoiceNumber; }
  get status(): InvoiceStatus { return this._status; }
  get totalAmount(): number { return this._totalAmount; }
  get totalTax(): number { return this._totalTax; }
  get grandTotal(): number { return this._grandTotal; }
  get amountDue(): number { return this._amountDue; }
  get lines(): InvoiceLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(line: InvoiceLine): void {
    if (this._status !== InvoiceStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft invoice");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._totalAmount = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._totalTax = this._lines.reduce((s, l) => s + l.taxAmount, 0);
    this._grandTotal = this._totalAmount + this._totalTax;
    this._amountDue = this._grandTotal - this._amountPaid;
  }

  register(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot register invoice with no lines");
    if (this._status !== InvoiceStatus.draft) throw new DomainError("BusinessRule", "Only draft invoices can be registered");
    this._status = InvoiceStatus.registered;
    this._updatedAt = new Date(); this._version++;
  }

  verify(): void {
    if (this._status !== InvoiceStatus.registered) throw new DomainError("BusinessRule", "Only registered invoices can be verified");
    this._status = InvoiceStatus.verified;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SupplierInvoiceVerified(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  approve(approvedBy: string): void {
    if (this._status !== InvoiceStatus.verified) throw new DomainError("BusinessRule", "Only verified invoices can be approved");
    this._status = InvoiceStatus.approved;
    this._approvedAt = new Date(); this._approvedBy = approvedBy;
    this._updatedAt = new Date(); this._version++;
  }

  markMatched(matchStatus: string): void {
    this._matchStatus = matchStatus;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SupplierInvoiceMatched(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, matchStatus }));
  }

  recordPayment(amount: number): void {
    this._amountPaid += amount;
    this._amountDue = this._grandTotal - this._amountPaid;
    this._paymentStatus = this._amountDue <= 0 ? "paid" : "partial";
    if (this._amountDue <= 0) this._paidAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  hold(reason: string): void {
    this._status = InvoiceStatus.onHold;
    this._holdReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  release(): void {
    if (this._status !== InvoiceStatus.onHold) throw new DomainError("BusinessRule", "Invoice not on hold");
    this._status = InvoiceStatus.verified;
    this._holdReason = null;
    this._updatedAt = new Date(); this._version++;
  }

  cancel(reason: string): void {
    if (this._status === InvoiceStatus.cancelled || this._status === InvoiceStatus.paid) throw new DomainError("BusinessRule", "Cannot cancel paid/already cancelled invoice");
    this._status = InvoiceStatus.cancelled;
    this._cancelledAt = new Date(); this._cancelReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): SupplierInvoiceState {
    return { id: this._id.value, invoiceNumber: this._invoiceNumber, invoiceDate: this._invoiceDate,
      companyId: this._companyId, branchId: this._branchId, vendorId: this._vendorId,
      vendorName: this._vendorName, vendorTaxCode: this._vendorTaxCode, poId: this._poId,
      poNumber: this._poNumber, status: this._status, matchStatus: this._matchStatus,
      matchingRule: this._matchingRule, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, totalAmount: this._totalAmount, totalTax: this._totalTax,
      grandTotal: this._grandTotal, amountPaid: this._amountPaid, amountDue: this._amountDue,
      paymentStatus: this._paymentStatus, paymentTermCode: this._paymentTermCode,
      dueDate: this._dueDate, description: this._description, notes: this._notes,
      holdReason: this._holdReason, approvedAt: this._approvedAt, approvedBy: this._approvedBy,
      paidAt: this._paidAt, cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
