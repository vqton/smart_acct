import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CustomerReceiptId, ReceiptAllocationId } from "./sales-ids.js";
import { SlsPaymentMethod, SlsPaymentStatus } from "./sales-enums.js";
import { CustomerReceiptCreated, CustomerReceiptAllocated } from "./sales-events.js";

export interface ReceiptAllocationState {
  id: string; receiptId: string; invoiceId: string; invoiceNumber: string;
  amount: number; currencyCode: string; createdAt: Date;
}

export class ReceiptAllocation extends AggregateRoot<ReceiptAllocationId> {
  private _id: ReceiptAllocationId; private _receiptId: string; private _invoiceId: string;
  private _invoiceNumber: string; private _amount: number; private _currencyCode: string;
  private _createdAt: Date;

  private constructor(id: ReceiptAllocationId, receiptId: string, invoiceId: string, invoiceNumber: string, amount: number, currencyCode: string) {
    super(); this._id = id; this._receiptId = receiptId; this._invoiceId = invoiceId;
    this._invoiceNumber = invoiceNumber; this._amount = amount; this._currencyCode = currencyCode;
    this._createdAt = new Date();
  }

  static create(receiptId: string, invoiceId: string, invoiceNumber: string, amount: number, currencyCode: string = "VND"): ReceiptAllocation {
    if (amount <= 0) throw new DomainError("Validation", "Allocation amount must be positive");
    return new ReceiptAllocation(ReceiptAllocationId.new(), receiptId, invoiceId, invoiceNumber, amount, currencyCode);
  }

  static load(s: ReceiptAllocationState): ReceiptAllocation {
    const a = new ReceiptAllocation(new ReceiptAllocationId(s.id), s.receiptId, s.invoiceId, s.invoiceNumber, s.amount, s.currencyCode);
    a._createdAt = s.createdAt;
    return a;
  }

  get id(): ReceiptAllocationId { return this._id; }
  get invoiceId(): string { return this._invoiceId; }
  get amount(): number { return this._amount; }

  toState(): ReceiptAllocationState {
    return { id: this._id.value, receiptId: this._receiptId, invoiceId: this._invoiceId,
      invoiceNumber: this._invoiceNumber, amount: this._amount, currencyCode: this._currencyCode,
      createdAt: this._createdAt };
  }
}

export interface CustomerReceiptState {
  id: string; receiptNumber: string; companyId: string; branchId: string | null;
  customerId: string; customerName: string;
  orderId: string | null; orderNumber: string | null;
  invoiceId: string | null; invoiceNumber: string | null;
  returnId: string | null; returnNumber: string | null;
  paymentDate: Date; amount: number; currencyCode: string;
  exchangeRate: number; vndAmount: number; paymentMethod: string;
  paymentRef: string | null;
  isSplitPayment: boolean; splitCount: number;
  status: string;
  approvedBy: string | null; approvedAt: Date | null;
  glBatchId: string | null; postedToGL: boolean;
  notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class CustomerReceipt extends AggregateRoot<CustomerReceiptId> {
  private _id: CustomerReceiptId; private _receiptNumber: string; private _companyId: string;
  private _branchId: string | null; private _customerId: string; private _customerName: string;
  private _orderId: string | null; private _orderNumber: string | null;
  private _invoiceId: string | null; private _invoiceNumber: string | null;
  private _returnId: string | null; private _returnNumber: string | null;
  private _paymentDate: Date; private _amount: number; private _currencyCode: string;
  private _exchangeRate: number; private _vndAmount: number;
  private _paymentMethod: SlsPaymentMethod; private _paymentRef: string | null;
  private _isSplitPayment: boolean; private _splitCount: number;
  private _status: SlsPaymentStatus;
  private _approvedBy: string | null; private _approvedAt: Date | null;
  private _glBatchId: string | null; private _postedToGL: boolean;
  private _allocations: ReceiptAllocation[] = [];
  private _notes: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: CustomerReceiptId, receiptNumber: string, companyId: string, customerId: string, customerName: string, amount: number, paymentMethod: SlsPaymentMethod) {
    super(); this._id = id; this._receiptNumber = receiptNumber; this._companyId = companyId;
    this._customerId = customerId; this._customerName = customerName;
    this._amount = amount; this._paymentMethod = paymentMethod;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._vndAmount = amount;
    this._status = SlsPaymentStatus.pending; this._paymentDate = new Date();
    this._isSplitPayment = false; this._splitCount = 1; this._postedToGL = false;
    this._branchId = null; this._orderId = null; this._orderNumber = null;
    this._invoiceId = null; this._invoiceNumber = null; this._returnId = null;
    this._returnNumber = null; this._paymentRef = null;
    this._approvedBy = null; this._approvedAt = null; this._glBatchId = null;
    this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { receiptNumber: string; companyId: string; customerId: string; customerName: string; amount: number; paymentMethod: SlsPaymentMethod; branchId?: string; orderId?: string; orderNumber?: string; invoiceId?: string; invoiceNumber?: string; returnId?: string; returnNumber?: string; paymentDate?: Date; currencyCode?: string; exchangeRate?: number; paymentRef?: string; isSplitPayment?: boolean; splitCount?: number; notes?: string }): CustomerReceipt {
    const r = new CustomerReceipt(CustomerReceiptId.new(), p.receiptNumber, p.companyId, p.customerId, p.customerName, p.amount, p.paymentMethod);
    r._branchId = p.branchId ?? null; r._orderId = p.orderId ?? null;
    r._orderNumber = p.orderNumber ?? null; r._invoiceId = p.invoiceId ?? null;
    r._invoiceNumber = p.invoiceNumber ?? null; r._returnId = p.returnId ?? null;
    r._returnNumber = p.returnNumber ?? null; r._paymentDate = p.paymentDate ?? new Date();
    r._currencyCode = p.currencyCode ?? "VND"; r._exchangeRate = p.exchangeRate ?? 1;
    r._vndAmount = Math.round(r._amount * r._exchangeRate);
    r._paymentRef = p.paymentRef ?? null; r._isSplitPayment = p.isSplitPayment ?? false;
    r._splitCount = p.splitCount ?? 1; r._notes = p.notes ?? null;
    r.addEvent(new CustomerReceiptCreated(r._id.value, new Date(), { receiptNumber: r._receiptNumber, amount: r._amount, paymentMethod: r._paymentMethod }));
    return r;
  }

  static load(s: CustomerReceiptState): CustomerReceipt {
    const r = new CustomerReceipt(new CustomerReceiptId(s.id), s.receiptNumber, s.companyId, s.customerId, s.customerName, s.amount, s.paymentMethod as SlsPaymentMethod);
    r._branchId = s.branchId; r._orderId = s.orderId; r._orderNumber = s.orderNumber;
    r._invoiceId = s.invoiceId; r._invoiceNumber = s.invoiceNumber;
    r._returnId = s.returnId; r._returnNumber = s.returnNumber;
    r._paymentDate = s.paymentDate; r._currencyCode = s.currencyCode;
    r._exchangeRate = s.exchangeRate; r._vndAmount = s.vndAmount;
    r._paymentRef = s.paymentRef; r._isSplitPayment = s.isSplitPayment;
    r._splitCount = s.splitCount; r._status = s.status as SlsPaymentStatus;
    r._approvedBy = s.approvedBy; r._approvedAt = s.approvedAt;
    r._glBatchId = s.glBatchId; r._postedToGL = s.postedToGL; r._notes = s.notes;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt;
    r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): CustomerReceiptId { return this._id; }
  get receiptNumber(): string { return this._receiptNumber; }
  get amount(): number { return this._amount; }
  get status(): SlsPaymentStatus { return this._status; }
  get invoiceId(): string | null { return this._invoiceId; }
  get allocations(): ReceiptAllocation[] { return this._allocations; }
  get version(): number { return this._version; }

  approve(approvedBy: string): void {
    this._status = SlsPaymentStatus.fullyPaid;
    this._approvedBy = approvedBy; this._approvedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  addAllocation(allocation: ReceiptAllocation): void {
    const totalAllocated = this._allocations.reduce((s, a) => s + a.amount, 0) + allocation.amount;
    if (totalAllocated > this._amount) throw new DomainError("BusinessRule", "Total allocation exceeds receipt amount");
    this._allocations.push(allocation);
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new CustomerReceiptAllocated(this._id.value, new Date(), { receiptNumber: this._receiptNumber, invoiceId: allocation.invoiceId, amount: allocation.amount }));
  }

  markPosted(glBatchId: string): void {
    this._glBatchId = glBatchId; this._postedToGL = true;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): CustomerReceiptState {
    return { id: this._id.value, receiptNumber: this._receiptNumber, companyId: this._companyId,
      branchId: this._branchId, customerId: this._customerId, customerName: this._customerName,
      orderId: this._orderId, orderNumber: this._orderNumber,
      invoiceId: this._invoiceId, invoiceNumber: this._invoiceNumber,
      returnId: this._returnId, returnNumber: this._returnNumber,
      paymentDate: this._paymentDate, amount: this._amount, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, vndAmount: this._vndAmount,
      paymentMethod: this._paymentMethod, paymentRef: this._paymentRef,
      isSplitPayment: this._isSplitPayment, splitCount: this._splitCount,
      status: this._status, approvedBy: this._approvedBy, approvedAt: this._approvedAt,
      glBatchId: this._glBatchId, postedToGL: this._postedToGL, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
