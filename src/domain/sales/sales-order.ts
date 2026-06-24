import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { SalesOrderId, OrderLineId } from "./sales-ids.js";
import { SlsOrderStatus, SlsOrderType, SlsOrderSource, SlsPaymentStatus, SlsPaymentMethod, SlsReservationStatus } from "./sales-enums.js";
import { SalesOrderCreated, SalesOrderApproved, SalesOrderConfirmed, SalesOrderCancelled, SalesOrderOnHold, SalesOrderCompleted } from "./sales-events.js";

export interface OrderLineState {
  id: string; orderId: string; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string; description: string | null;
  quantity: number; uom: string; unitPrice: number; totalPrice: number; currencyCode: string;
  discountPercent: number; discountAmount: number;
  taxCode: string | null; taxRate: number; taxAmount: number; netAmount: number;
  deliveredQuantity: number; returnedQuantity: number; invoicedQuantity: number; reservedQuantity: number;
  unitCost: number; totalCost: number;
  warehouseId: string | null; projectId: string | null; costCenterId: string | null; departmentId: string | null;
  expectedDate: Date | null; promisedDate: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class OrderLine extends AggregateRoot<OrderLineId> {
  private _id: OrderLineId; private _orderId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _discountPercent: number; private _discountAmount: number;
  private _taxCode: string | null; private _taxRate: number; private _taxAmount: number;
  private _netAmount: number;
  private _deliveredQuantity: number; private _returnedQuantity: number;
  private _invoicedQuantity: number; private _reservedQuantity: number;
  private _unitCost: number; private _totalCost: number;
  private _warehouseId: string | null; private _projectId: string | null;
  private _costCenterId: string | null; private _departmentId: string | null;
  private _expectedDate: Date | null; private _promisedDate: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: OrderLineId, orderId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._orderId = orderId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantity * unitPrice; this._currencyCode = "VND";
    this._discountPercent = 0; this._discountAmount = 0; this._taxCode = null;
    this._taxRate = 0; this._taxAmount = 0; this._netAmount = this._totalPrice;
    this._deliveredQuantity = 0; this._returnedQuantity = 0; this._invoicedQuantity = 0;
    this._reservedQuantity = 0; this._unitCost = 0; this._totalCost = 0;
    this._itemId = null; this._description = null; this._warehouseId = null;
    this._projectId = null; this._costCenterId = null; this._departmentId = null;
    this._expectedDate = null; this._promisedDate = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { orderId: string; lineNumber: number; itemCode: string; itemName: string; quantity: number; uom: string; unitPrice: number; itemId?: string; description?: string; taxCode?: string; taxRate?: number; discountPercent?: number; discountAmount?: number; unitCost?: number; warehouseId?: string; projectId?: string; costCenterId?: string; departmentId?: string; expectedDate?: Date; promisedDate?: Date }): OrderLine {
    const l = new OrderLine(OrderLineId.new(), p.orderId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.unitPrice);
    l._itemId = p.itemId ?? null; l._description = p.description ?? null;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    if (p.discountPercent) { l._discountPercent = p.discountPercent; l._discountAmount = Math.round(l._totalPrice * p.discountPercent / 100); }
    if (p.discountAmount) l._discountAmount = p.discountAmount;
    l._taxAmount = Math.round((l._totalPrice - l._discountAmount) * l._taxRate / 100);
    l._netAmount = l._totalPrice - l._discountAmount + l._taxAmount;
    l._unitCost = p.unitCost ?? 0; l._totalCost = l._unitCost * l._quantity;
    l._warehouseId = p.warehouseId ?? null; l._projectId = p.projectId ?? null;
    l._costCenterId = p.costCenterId ?? null; l._departmentId = p.departmentId ?? null;
    l._expectedDate = p.expectedDate ?? null; l._promisedDate = p.promisedDate ?? null;
    return l;
  }

  static load(s: OrderLineState): OrderLine {
    const l = new OrderLine(new OrderLineId(s.id), s.orderId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.unitPrice);
    l._itemId = s.itemId; l._description = s.description; l._totalPrice = s.totalPrice;
    l._currencyCode = s.currencyCode; l._discountPercent = s.discountPercent;
    l._discountAmount = s.discountAmount; l._taxCode = s.taxCode; l._taxRate = s.taxRate;
    l._taxAmount = s.taxAmount; l._netAmount = s.netAmount;
    l._deliveredQuantity = s.deliveredQuantity; l._returnedQuantity = s.returnedQuantity;
    l._invoicedQuantity = s.invoicedQuantity; l._reservedQuantity = s.reservedQuantity;
    l._unitCost = s.unitCost; l._totalCost = s.totalCost; l._warehouseId = s.warehouseId;
    l._projectId = s.projectId; l._costCenterId = s.costCenterId; l._departmentId = s.departmentId;
    l._expectedDate = s.expectedDate; l._promisedDate = s.promisedDate;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt;
    l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): OrderLineId { return this._id; }
  get quantity(): number { return this._quantity; }
  get unitPrice(): number { return this._unitPrice; }
  get totalPrice(): number { return this._totalPrice; }
  get netAmount(): number { return this._netAmount; }
  get taxAmount(): number { return this._taxAmount; }
  get taxRate(): number { return this._taxRate; }
  get itemCode(): string { return this._itemCode; }
  get deliveredQuantity(): number { return this._deliveredQuantity; }
  get returnedQuantity(): number { return this._returnedQuantity; }
  get invoicedQuantity(): number { return this._invoicedQuantity; }
  get reservedQuantity(): number { return this._reservedQuantity; }
  get unitCost(): number { return this._unitCost; }
  get totalCost(): number { return this._totalCost; }
  get version(): number { return this._version; }
  get warehouseId(): string | null { return this._warehouseId; }
  get itemId(): string | null { return this._itemId; }
  get remainingToDeliver(): number { return this._quantity - this._deliveredQuantity; }

  recordDelivery(qty: number): void {
    const newDelivered = this._deliveredQuantity + qty;
    if (newDelivered > this._quantity) throw new DomainError("BusinessRule", "Delivery exceeds ordered quantity");
    this._deliveredQuantity = newDelivered;
    this._updatedAt = new Date(); this._version++;
  }

  reverseDelivery(qty: number): void {
    const newDelivered = this._deliveredQuantity - qty;
    if (newDelivered < 0) throw new DomainError("Validation", "Cannot reverse more than delivered");
    this._deliveredQuantity = newDelivered;
    this._updatedAt = new Date(); this._version++;
  }

  recordInvoice(qty: number): void {
    const newInvoiced = this._invoicedQuantity + qty;
    if (newInvoiced > this._quantity) throw new DomainError("BusinessRule", "Invoice quantity exceeds ordered quantity");
    this._invoicedQuantity = newInvoiced;
    this._updatedAt = new Date(); this._version++;
  }

  recordReturn(qty: number): void {
    const newReturned = this._returnedQuantity + qty;
    if (newReturned > this._deliveredQuantity) throw new DomainError("BusinessRule", "Return exceeds delivered quantity");
    this._returnedQuantity = newReturned;
    this._updatedAt = new Date(); this._version++;
  }

  recordReservation(qty: number): void {
    const newReserved = this._reservedQuantity + qty;
    if (newReserved > this._quantity) throw new DomainError("BusinessRule", "Reservation exceeds ordered quantity");
    this._reservedQuantity = newReserved;
    this._updatedAt = new Date(); this._version++;
  }

  releaseReservation(qty: number): void {
    const newReserved = this._reservedQuantity - qty;
    if (newReserved < 0) throw new DomainError("Validation", "Cannot release more than reserved");
    this._reservedQuantity = newReserved;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): OrderLineState {
    return { id: this._id.value, orderId: this._orderId, lineNumber: this._lineNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      description: this._description, quantity: this._quantity, uom: this._uom,
      unitPrice: this._unitPrice, totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      discountPercent: this._discountPercent, discountAmount: this._discountAmount,
      taxCode: this._taxCode, taxRate: this._taxRate, taxAmount: this._taxAmount,
      netAmount: this._netAmount, deliveredQuantity: this._deliveredQuantity,
      returnedQuantity: this._returnedQuantity, invoicedQuantity: this._invoicedQuantity,
      reservedQuantity: this._reservedQuantity, unitCost: this._unitCost,
      totalCost: this._totalCost, warehouseId: this._warehouseId, projectId: this._projectId,
      costCenterId: this._costCenterId, departmentId: this._departmentId,
      expectedDate: this._expectedDate, promisedDate: this._promisedDate,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}

export interface SalesOrderState {
  id: string; orderNumber: string; companyId: string; branchId: string | null;
  storeId: string | null; salespersonId: string | null;
  customerId: string; customerName: string; customerTaxCode: string | null;
  customerAddress: string | null; customerPhone: string | null; customerEmail: string | null;
  orderType: string; orderSource: string; status: string;
  currencyCode: string; exchangeRate: number;
  subtotal: number; discountAmount: number; taxAmount: number;
  shippingAmount: number; grandTotal: number; totalPaid: number; totalDue: number;
  orderDate: Date; requestedDate: Date | null; promisedDate: Date | null; deliveredDate: Date | null;
  approvedBy: string | null; approvedAt: Date | null;
  rejectedBy: string | null; rejectedAt: Date | null; rejectReason: string | null;
  cancelledAt: Date | null; cancelReason: string | null; holdReason: string | null;
  quotationId: string | null; quotationNumber: string | null; sourceOrderId: string | null;
  notes: string | null; internalNotes: string | null;
  deliveryAddress: string | null; deliveryWard: string | null; deliveryDistrict: string | null;
  deliveryProvince: string | null; deliveryContact: string | null; deliveryPhone: string | null;
  paymentTermCode: string | null; paymentMethod: string | null; paymentStatus: string;
  reservationStatus: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class SalesOrder extends AggregateRoot<SalesOrderId> {
  private _id: SalesOrderId; private _orderNumber: string; private _companyId: string;
  private _branchId: string | null; private _storeId: string | null;
  private _salespersonId: string | null; private _customerId: string;
  private _customerName: string; private _customerTaxCode: string | null;
  private _customerAddress: string | null; private _customerPhone: string | null;
  private _customerEmail: string | null; private _orderType: SlsOrderType;
  private _orderSource: SlsOrderSource; private _status: SlsOrderStatus;
  private _currencyCode: string; private _exchangeRate: number;
  private _subtotal: number; private _discountAmount: number; private _taxAmount: number;
  private _shippingAmount: number; private _grandTotal: number;
  private _totalPaid: number; private _totalDue: number;
  private _orderDate: Date; private _requestedDate: Date | null;
  private _promisedDate: Date | null; private _deliveredDate: Date | null;
  private _approvedBy: string | null; private _approvedAt: Date | null;
  private _rejectedBy: string | null; private _rejectedAt: Date | null;
  private _rejectReason: string | null; private _cancelledAt: Date | null;
  private _cancelReason: string | null; private _holdReason: string | null;
  private _quotationId: string | null; private _quotationNumber: string | null;
  private _sourceOrderId: string | null; private _notes: string | null;
  private _internalNotes: string | null;
  private _deliveryAddress: string | null; private _deliveryWard: string | null;
  private _deliveryDistrict: string | null; private _deliveryProvince: string | null;
  private _deliveryContact: string | null; private _deliveryPhone: string | null;
  private _paymentTermCode: string | null; private _paymentMethod: SlsPaymentMethod | null;
  private _paymentStatus: SlsPaymentStatus; private _reservationStatus: SlsReservationStatus | null;
  private _lines: OrderLine[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: SalesOrderId, orderNumber: string, companyId: string, customerId: string, customerName: string) {
    super(); this._id = id; this._orderNumber = orderNumber; this._companyId = companyId;
    this._customerId = customerId; this._customerName = customerName;
    this._orderType = SlsOrderType.standard; this._orderSource = SlsOrderSource.manual;
    this._status = SlsOrderStatus.draft;
    this._currencyCode = "VND"; this._exchangeRate = 1; this._subtotal = 0;
    this._discountAmount = 0; this._taxAmount = 0; this._shippingAmount = 0;
    this._grandTotal = 0; this._totalPaid = 0; this._totalDue = 0;
    this._orderDate = new Date(); this._paymentStatus = SlsPaymentStatus.pending;
    this._branchId = null; this._storeId = null; this._salespersonId = null;
    this._customerTaxCode = null; this._customerAddress = null; this._customerPhone = null;
    this._customerEmail = null; this._requestedDate = null; this._promisedDate = null;
    this._deliveredDate = null; this._approvedBy = null; this._approvedAt = null;
    this._rejectedBy = null; this._rejectedAt = null; this._rejectReason = null;
    this._cancelledAt = null; this._cancelReason = null; this._holdReason = null;
    this._quotationId = null; this._quotationNumber = null; this._sourceOrderId = null;
    this._notes = null; this._internalNotes = null;
    this._deliveryAddress = null; this._deliveryWard = null; this._deliveryDistrict = null;
    this._deliveryProvince = null; this._deliveryContact = null; this._deliveryPhone = null;
    this._paymentTermCode = null; this._paymentMethod = null; this._reservationStatus = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { orderNumber: string; companyId: string; customerId: string; customerName: string; branchId?: string; storeId?: string; salespersonId?: string; customerTaxCode?: string; customerAddress?: string; customerPhone?: string; customerEmail?: string; orderType?: SlsOrderType; orderSource?: SlsOrderSource; currencyCode?: string; exchangeRate?: number; orderDate?: Date; requestedDate?: Date; promisedDate?: Date; deliveryAddress?: string; deliveryWard?: string; deliveryDistrict?: string; deliveryProvince?: string; deliveryContact?: string; deliveryPhone?: string; paymentTermCode?: string; paymentMethod?: SlsPaymentMethod; notes?: string; internalNotes?: string; quotationId?: string; quotationNumber?: string; sourceOrderId?: string }): SalesOrder {
    const o = new SalesOrder(SalesOrderId.new(), p.orderNumber, p.companyId, p.customerId, p.customerName);
    o._branchId = p.branchId ?? null; o._storeId = p.storeId ?? null; o._salespersonId = p.salespersonId ?? null;
    o._customerTaxCode = p.customerTaxCode ?? null; o._customerAddress = p.customerAddress ?? null;
    o._customerPhone = p.customerPhone ?? null; o._customerEmail = p.customerEmail ?? null;
    o._orderType = p.orderType ?? SlsOrderType.standard;
    o._orderSource = p.orderSource ?? SlsOrderSource.manual;
    o._currencyCode = p.currencyCode ?? "VND"; o._exchangeRate = p.exchangeRate ?? 1;
    o._requestedDate = p.requestedDate ?? null; o._promisedDate = p.promisedDate ?? null;
    o._deliveryAddress = p.deliveryAddress ?? null; o._deliveryWard = p.deliveryWard ?? null;
    o._deliveryDistrict = p.deliveryDistrict ?? null; o._deliveryProvince = p.deliveryProvince ?? null;
    o._deliveryContact = p.deliveryContact ?? null; o._deliveryPhone = p.deliveryPhone ?? null;
    o._paymentTermCode = p.paymentTermCode ?? null; o._paymentMethod = p.paymentMethod ?? null;
    o._notes = p.notes ?? null; o._internalNotes = p.internalNotes ?? null;
    o._quotationId = p.quotationId ?? null; o._quotationNumber = p.quotationNumber ?? null;
    o._sourceOrderId = p.sourceOrderId ?? null;
    o.addEvent(new SalesOrderCreated(o._id.value, new Date(), { orderNumber: o._orderNumber, customerId: o._customerId }));
    return o;
  }

  static load(s: SalesOrderState): SalesOrder {
    const o = new SalesOrder(new SalesOrderId(s.id), s.orderNumber, s.companyId, s.customerId, s.customerName);
    o._branchId = s.branchId; o._storeId = s.storeId; o._salespersonId = s.salespersonId;
    o._customerTaxCode = s.customerTaxCode; o._customerAddress = s.customerAddress;
    o._customerPhone = s.customerPhone; o._customerEmail = s.customerEmail;
    o._orderType = s.orderType as SlsOrderType; o._orderSource = s.orderSource as SlsOrderSource;
    o._status = s.status as SlsOrderStatus;
    o._currencyCode = s.currencyCode; o._exchangeRate = s.exchangeRate;
    o._subtotal = s.subtotal; o._discountAmount = s.discountAmount; o._taxAmount = s.taxAmount;
    o._shippingAmount = s.shippingAmount; o._grandTotal = s.grandTotal;
    o._totalPaid = s.totalPaid; o._totalDue = s.totalDue;
    o._orderDate = s.orderDate; o._requestedDate = s.requestedDate; o._promisedDate = s.promisedDate;
    o._deliveredDate = s.deliveredDate; o._approvedBy = s.approvedBy; o._approvedAt = s.approvedAt;
    o._rejectedBy = s.rejectedBy; o._rejectedAt = s.rejectedAt; o._rejectReason = s.rejectReason;
    o._cancelledAt = s.cancelledAt; o._cancelReason = s.cancelReason; o._holdReason = s.holdReason;
    o._quotationId = s.quotationId; o._quotationNumber = s.quotationNumber;
    o._sourceOrderId = s.sourceOrderId; o._notes = s.notes; o._internalNotes = s.internalNotes;
    o._deliveryAddress = s.deliveryAddress; o._deliveryWard = s.deliveryWard;
    o._deliveryDistrict = s.deliveryDistrict; o._deliveryProvince = s.deliveryProvince;
    o._deliveryContact = s.deliveryContact; o._deliveryPhone = s.deliveryPhone;
    o._paymentTermCode = s.paymentTermCode;
    o._paymentMethod = s.paymentMethod as SlsPaymentMethod | null;
    o._paymentStatus = s.paymentStatus as SlsPaymentStatus;
    o._reservationStatus = s.reservationStatus as SlsReservationStatus | null;
    o._version = s.version; o._createdAt = s.createdAt; o._updatedAt = s.updatedAt;
    o._deletedAt = s.deletedAt;
    return o;
  }

  get id(): SalesOrderId { return this._id; }
  get orderNumber(): string { return this._orderNumber; }
  get status(): SlsOrderStatus { return this._status; }
  get customerId(): string { return this._customerId; }
  get subtotal(): number { return this._subtotal; }
  get grandTotal(): number { return this._grandTotal; }
  get totalPaid(): number { return this._totalPaid; }
  get totalDue(): number { return this._totalDue; }
  get lines(): OrderLine[] { return this._lines; }
  get version(): number { return this._version; }
  get paymentStatus(): SlsPaymentStatus { return this._paymentStatus; }
  get orderType(): SlsOrderType { return this._orderType; }

  addLine(line: OrderLine): void {
    if (this._status !== SlsOrderStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft order");
    this._lines.push(line);
    this.recalculate();
  }

  private recalculate(): void {
    this._subtotal = this._lines.reduce((s, l) => s + l.totalPrice, 0);
    this._taxAmount = this._lines.reduce((s, l) => s + l.taxAmount, 0);
    this._grandTotal = this._subtotal - this._discountAmount + this._taxAmount + this._shippingAmount;
    this._totalDue = this._grandTotal - this._totalPaid;
  }

  submitForApproval(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot submit order with no lines");
    if (this._status !== SlsOrderStatus.draft) throw new DomainError("BusinessRule", "Only draft order can be submitted");
    this._status = SlsOrderStatus.pendingApproval;
    this._updatedAt = new Date(); this._version++;
  }

  approve(approvedBy: string): void {
    if (this._status !== SlsOrderStatus.pendingApproval) throw new DomainError("BusinessRule", "Order not pending approval");
    this._status = SlsOrderStatus.approved;
    this._approvedAt = new Date(); this._approvedBy = approvedBy;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesOrderApproved(this._id.value, new Date(), { orderNumber: this._orderNumber, approvedBy }));
  }

  confirm(confirmedBy: string): void {
    if (this._status !== SlsOrderStatus.approved) throw new DomainError("BusinessRule", "Only approved order can be confirmed");
    this._status = SlsOrderStatus.confirmed;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesOrderConfirmed(this._id.value, new Date(), { orderNumber: this._orderNumber, confirmedBy }));
  }

  startProcessing(): void {
    if (this._status !== SlsOrderStatus.confirmed && this._status !== SlsOrderStatus.approved) throw new DomainError("BusinessRule", "Order must be confirmed to start processing");
    this._status = SlsOrderStatus.processing;
    this._updatedAt = new Date(); this._version++;
  }

  cancel(reason: string): void {
    if (this._status === SlsOrderStatus.cancelled || this._status === SlsOrderStatus.completed) throw new DomainError("BusinessRule", "Order already cancelled/completed");
    this._status = SlsOrderStatus.cancelled;
    this._cancelledAt = new Date(); this._cancelReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesOrderCancelled(this._id.value, new Date(), { orderNumber: this._orderNumber, reason }));
  }

  hold(reason: string): void {
    if (this._status === SlsOrderStatus.onHold) throw new DomainError("BusinessRule", "Order already on hold");
    this._status = SlsOrderStatus.onHold;
    this._holdReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesOrderOnHold(this._id.value, new Date(), { orderNumber: this._orderNumber, reason }));
  }

  releaseHold(): void {
    if (this._status !== SlsOrderStatus.onHold) throw new DomainError("BusinessRule", "Order not on hold");
    this._status = SlsOrderStatus.approved; this._holdReason = null;
    this._updatedAt = new Date(); this._version++;
  }

  updateDeliveryStatus(): void {
    const allDelivered = this._lines.every(l => l.deliveredQuantity >= l.quantity);
    const anyDelivered = this._lines.some(l => l.deliveredQuantity > 0);
    if (allDelivered) {
      this._status = SlsOrderStatus.fullyDelivered;
      this._deliveredDate = new Date();
    } else if (anyDelivered) {
      this._status = SlsOrderStatus.partlyDelivered;
    }
    this._updatedAt = new Date(); this._version++;
  }

  updateInvoiceStatus(): void {
    const allInvoiced = this._lines.every(l => l.invoicedQuantity >= l.quantity);
    const anyInvoiced = this._lines.some(l => l.invoicedQuantity > 0);
    if (allInvoiced) this._status = SlsOrderStatus.fullyInvoiced;
    else if (anyInvoiced) this._status = SlsOrderStatus.partlyInvoiced;
    this._updatedAt = new Date(); this._version++;
  }

  recordPayment(amount: number): void {
    this._totalPaid += amount;
    this._totalDue = this._grandTotal - this._totalPaid;
    if (this._totalDue <= 0) this._paymentStatus = SlsPaymentStatus.fullyPaid;
    else this._paymentStatus = SlsPaymentStatus.partiallyPaid;
    this._updatedAt = new Date(); this._version++;
  }

  markCompleted(): void {
    if (this._status === SlsOrderStatus.completed) throw new DomainError("BusinessRule", "Order already completed");
    if (this._paymentStatus !== SlsPaymentStatus.fullyPaid) throw new DomainError("BusinessRule", "Order must be fully paid to complete");
    this._status = SlsOrderStatus.completed;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new SalesOrderCompleted(this._id.value, new Date(), { orderNumber: this._orderNumber }));
  }

  toState(): SalesOrderState {
    return { id: this._id.value, orderNumber: this._orderNumber, companyId: this._companyId,
      branchId: this._branchId, storeId: this._storeId, salespersonId: this._salespersonId,
      customerId: this._customerId, customerName: this._customerName,
      customerTaxCode: this._customerTaxCode, customerAddress: this._customerAddress,
      customerPhone: this._customerPhone, customerEmail: this._customerEmail,
      orderType: this._orderType, orderSource: this._orderSource, status: this._status,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      subtotal: this._subtotal, discountAmount: this._discountAmount, taxAmount: this._taxAmount,
      shippingAmount: this._shippingAmount, grandTotal: this._grandTotal,
      totalPaid: this._totalPaid, totalDue: this._totalDue,
      orderDate: this._orderDate, requestedDate: this._requestedDate,
      promisedDate: this._promisedDate, deliveredDate: this._deliveredDate,
      approvedBy: this._approvedBy, approvedAt: this._approvedAt,
      rejectedBy: this._rejectedBy, rejectedAt: this._rejectedAt,
      rejectReason: this._rejectReason, cancelledAt: this._cancelledAt,
      cancelReason: this._cancelReason, holdReason: this._holdReason,
      quotationId: this._quotationId, quotationNumber: this._quotationNumber,
      sourceOrderId: this._sourceOrderId, notes: this._notes, internalNotes: this._internalNotes,
      deliveryAddress: this._deliveryAddress, deliveryWard: this._deliveryWard,
      deliveryDistrict: this._deliveryDistrict, deliveryProvince: this._deliveryProvince,
      deliveryContact: this._deliveryContact, deliveryPhone: this._deliveryPhone,
      paymentTermCode: this._paymentTermCode, paymentMethod: this._paymentMethod?.toString() ?? null,
      paymentStatus: this._paymentStatus, reservationStatus: this._reservationStatus?.toString() ?? null,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
