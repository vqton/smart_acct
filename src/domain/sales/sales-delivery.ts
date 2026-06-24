import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DeliveryOrderId, DeliveryLineId } from "./sales-ids.js";
import { SlsDeliveryStatus } from "./sales-enums.js";
import { DeliveryOrderCreated, DeliveryOrderShipped, DeliveryOrderDelivered, DeliveryConfirmed } from "./sales-events.js";

export interface DeliveryLineState {
  id: string; deliveryId: string; orderLineId: string | null; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string;
  quantityOrdered: number; quantityDelivered: number; quantityDamaged: number; quantityReturned: number;
  uom: string; unitPrice: number; totalPrice: number; currencyCode: string;
  batchNumber: string | null; serialNumber: string | null; expiryDate: Date | null;
  warehouseId: string | null; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class DeliveryLine extends AggregateRoot<DeliveryLineId> {
  private _id: DeliveryLineId; private _deliveryId: string; private _orderLineId: string | null;
  private _lineNumber: number; private _itemId: string | null; private _itemCode: string;
  private _itemName: string; private _quantityOrdered: number; private _quantityDelivered: number;
  private _quantityDamaged: number; private _quantityReturned: number; private _uom: string;
  private _unitPrice: number; private _totalPrice: number; private _currencyCode: string;
  private _batchNumber: string | null; private _serialNumber: string | null;
  private _expiryDate: Date | null; private _warehouseId: string | null;
  private _notes: string | null; private _version: number; private _createdAt: Date;
  private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: DeliveryLineId, deliveryId: string, lineNumber: number, itemCode: string, itemName: string, quantityDelivered: number, uom: string, unitPrice: number) {
    super(); this._id = id; this._deliveryId = deliveryId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantityDelivered = quantityDelivered;
    this._uom = uom; this._unitPrice = unitPrice;
    this._totalPrice = quantityDelivered * unitPrice; this._currencyCode = "VND";
    this._quantityOrdered = 0; this._quantityDamaged = 0; this._quantityReturned = 0;
    this._orderLineId = null; this._itemId = null; this._batchNumber = null;
    this._serialNumber = null; this._expiryDate = null; this._warehouseId = null;
    this._notes = null; this._version = 1; this._createdAt = new Date();
    this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { deliveryId: string; lineNumber: number; itemCode: string; itemName: string; quantityDelivered: number; uom: string; unitPrice: number; orderLineId?: string; itemId?: string; quantityOrdered?: number; quantityDamaged?: number; batchNumber?: string; serialNumber?: string; expiryDate?: Date; warehouseId?: string; notes?: string }): DeliveryLine {
    const l = new DeliveryLine(DeliveryLineId.new(), p.deliveryId, p.lineNumber, p.itemCode, p.itemName, p.quantityDelivered, p.uom, p.unitPrice);
    l._orderLineId = p.orderLineId ?? null; l._itemId = p.itemId ?? null;
    l._quantityOrdered = p.quantityOrdered ?? 0; l._quantityDamaged = p.quantityDamaged ?? 0;
    l._batchNumber = p.batchNumber ?? null; l._serialNumber = p.serialNumber ?? null;
    l._expiryDate = p.expiryDate ?? null; l._warehouseId = p.warehouseId ?? null;
    l._notes = p.notes ?? null;
    return l;
  }

  static load(s: DeliveryLineState): DeliveryLine {
    const l = new DeliveryLine(new DeliveryLineId(s.id), s.deliveryId, s.lineNumber, s.itemCode, s.itemName, s.quantityDelivered, s.uom, s.unitPrice);
    l._orderLineId = s.orderLineId; l._itemId = s.itemId; l._quantityOrdered = s.quantityOrdered;
    l._quantityDamaged = s.quantityDamaged; l._quantityReturned = s.quantityReturned;
    l._totalPrice = s.totalPrice; l._currencyCode = s.currencyCode;
    l._batchNumber = s.batchNumber; l._serialNumber = s.serialNumber;
    l._expiryDate = s.expiryDate; l._warehouseId = s.warehouseId; l._notes = s.notes;
    l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt;
    l._deletedAt = s.deletedAt;
    return l;
  }

  get id(): DeliveryLineId { return this._id; }
  get quantityDelivered(): number { return this._quantityDelivered; }
  get itemCode(): string { return this._itemCode; }

  recordReturn(qty: number): void {
    this._quantityReturned += qty;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): DeliveryLineState {
    return { id: this._id.value, deliveryId: this._deliveryId, orderLineId: this._orderLineId,
      lineNumber: this._lineNumber, itemId: this._itemId, itemCode: this._itemCode,
      itemName: this._itemName, quantityOrdered: this._quantityOrdered,
      quantityDelivered: this._quantityDelivered, quantityDamaged: this._quantityDamaged,
      quantityReturned: this._quantityReturned, uom: this._uom, unitPrice: this._unitPrice,
      totalPrice: this._totalPrice, currencyCode: this._currencyCode,
      batchNumber: this._batchNumber, serialNumber: this._serialNumber,
      expiryDate: this._expiryDate, warehouseId: this._warehouseId, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}

export interface DeliveryOrderState {
  id: string; deliveryNumber: string; companyId: string; branchId: string | null;
  orderId: string; orderNumber: string; customerId: string; customerName: string;
  deliveryAddress: string | null; deliveryWard: string | null; deliveryDistrict: string | null;
  deliveryProvince: string | null; deliveryContact: string | null; deliveryPhone: string | null;
  deliveryType: string; status: string;
  deliveryDate: Date; requestedDate: Date | null; shippedAt: Date | null;
  deliveredAt: Date | null; confirmedAt: Date | null;
  carrierId: string | null; carrierName: string | null; trackingNumber: string | null;
  shipmentMethod: string | null;
  podReceivedBy: string | null; podSignedAt: Date | null; podImage: string | null; podNotes: string | null;
  exceptionType: string | null; exceptionReason: string | null;
  notes: string | null; internalNotes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class DeliveryOrder extends AggregateRoot<DeliveryOrderId> {
  private _id: DeliveryOrderId; private _deliveryNumber: string; private _companyId: string;
  private _branchId: string | null; private _orderId: string; private _orderNumber: string;
  private _customerId: string; private _customerName: string;
  private _deliveryAddress: string | null; private _deliveryWard: string | null;
  private _deliveryDistrict: string | null; private _deliveryProvince: string | null;
  private _deliveryContact: string | null; private _deliveryPhone: string | null;
  private _deliveryType: string; private _status: SlsDeliveryStatus;
  private _deliveryDate: Date; private _requestedDate: Date | null;
  private _shippedAt: Date | null; private _deliveredAt: Date | null;
  private _confirmedAt: Date | null;
  private _carrierId: string | null; private _carrierName: string | null;
  private _trackingNumber: string | null; private _shipmentMethod: string | null;
  private _podReceivedBy: string | null; private _podSignedAt: Date | null;
  private _podImage: string | null; private _podNotes: string | null;
  private _exceptionType: string | null; private _exceptionReason: string | null;
  private _lines: DeliveryLine[] = [];
  private _notes: string | null; private _internalNotes: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: DeliveryOrderId, deliveryNumber: string, companyId: string, orderId: string, orderNumber: string, customerId: string, customerName: string) {
    super(); this._id = id; this._deliveryNumber = deliveryNumber; this._companyId = companyId;
    this._orderId = orderId; this._orderNumber = orderNumber; this._customerId = customerId;
    this._customerName = customerName; this._deliveryType = "standard";
    this._status = SlsDeliveryStatus.draft; this._deliveryDate = new Date();
    this._branchId = null; this._deliveryAddress = null; this._deliveryWard = null;
    this._deliveryDistrict = null; this._deliveryProvince = null;
    this._deliveryContact = null; this._deliveryPhone = null;
    this._requestedDate = null; this._shippedAt = null; this._deliveredAt = null;
    this._confirmedAt = null; this._carrierId = null; this._carrierName = null;
    this._trackingNumber = null; this._shipmentMethod = null;
    this._podReceivedBy = null; this._podSignedAt = null; this._podImage = null;
    this._podNotes = null; this._exceptionType = null; this._exceptionReason = null;
    this._notes = null; this._internalNotes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { deliveryNumber: string; companyId: string; orderId: string; orderNumber: string; customerId: string; customerName: string; branchId?: string; deliveryAddress?: string; deliveryWard?: string; deliveryDistrict?: string; deliveryProvince?: string; deliveryContact?: string; deliveryPhone?: string; deliveryType?: string; deliveryDate?: Date; requestedDate?: Date; carrierId?: string; carrierName?: string; trackingNumber?: string; shipmentMethod?: string; notes?: string; internalNotes?: string }): DeliveryOrder {
    const d = new DeliveryOrder(DeliveryOrderId.new(), p.deliveryNumber, p.companyId, p.orderId, p.orderNumber, p.customerId, p.customerName);
    d._branchId = p.branchId ?? null; d._deliveryAddress = p.deliveryAddress ?? null;
    d._deliveryWard = p.deliveryWard ?? null; d._deliveryDistrict = p.deliveryDistrict ?? null;
    d._deliveryProvince = p.deliveryProvince ?? null; d._deliveryContact = p.deliveryContact ?? null;
    d._deliveryPhone = p.deliveryPhone ?? null; d._deliveryType = p.deliveryType ?? "standard";
    d._deliveryDate = p.deliveryDate ?? new Date(); d._requestedDate = p.requestedDate ?? null;
    d._carrierId = p.carrierId ?? null; d._carrierName = p.carrierName ?? null;
    d._trackingNumber = p.trackingNumber ?? null; d._shipmentMethod = p.shipmentMethod ?? null;
    d._notes = p.notes ?? null; d._internalNotes = p.internalNotes ?? null;
    d.addEvent(new DeliveryOrderCreated(d._id.value, new Date(), { deliveryNumber: d._deliveryNumber, orderNumber: d._orderNumber }));
    return d;
  }

  static load(s: DeliveryOrderState): DeliveryOrder {
    const d = new DeliveryOrder(new DeliveryOrderId(s.id), s.deliveryNumber, s.companyId, s.orderId, s.orderNumber, s.customerId, s.customerName);
    d._branchId = s.branchId; d._deliveryAddress = s.deliveryAddress;
    d._deliveryWard = s.deliveryWard; d._deliveryDistrict = s.deliveryDistrict;
    d._deliveryProvince = s.deliveryProvince; d._deliveryContact = s.deliveryContact;
    d._deliveryPhone = s.deliveryPhone; d._deliveryType = s.deliveryType;
    d._status = s.status as SlsDeliveryStatus; d._deliveryDate = s.deliveryDate;
    d._requestedDate = s.requestedDate; d._shippedAt = s.shippedAt;
    d._deliveredAt = s.deliveredAt; d._confirmedAt = s.confirmedAt;
    d._carrierId = s.carrierId; d._carrierName = s.carrierName;
    d._trackingNumber = s.trackingNumber; d._shipmentMethod = s.shipmentMethod;
    d._podReceivedBy = s.podReceivedBy; d._podSignedAt = s.podSignedAt;
    d._podImage = s.podImage; d._podNotes = s.podNotes;
    d._exceptionType = s.exceptionType; d._exceptionReason = s.exceptionReason;
    d._notes = s.notes; d._internalNotes = s.internalNotes;
    d._version = s.version; d._createdAt = s.createdAt; d._updatedAt = s.updatedAt;
    d._deletedAt = s.deletedAt;
    return d;
  }

  get id(): DeliveryOrderId { return this._id; }
  get deliveryNumber(): string { return this._deliveryNumber; }
  get status(): SlsDeliveryStatus { return this._status; }
  get orderId(): string { return this._orderId; }
  get lines(): DeliveryLine[] { return this._lines; }
  get version(): number { return this._version; }

  addLine(line: DeliveryLine): void {
    if (this._status !== SlsDeliveryStatus.draft) throw new DomainError("BusinessRule", "Cannot add lines to non-draft delivery");
    this._lines.push(line);
  }

  ship(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot ship delivery with no lines");
    if (this._status !== SlsDeliveryStatus.draft && this._status !== SlsDeliveryStatus.picking && this._status !== SlsDeliveryStatus.packed) throw new DomainError("BusinessRule", "Delivery not ready for shipping");
    this._status = SlsDeliveryStatus.shipped;
    this._shippedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new DeliveryOrderShipped(this._id.value, new Date(), { deliveryNumber: this._deliveryNumber }));
  }

  markDelivered(podReceivedBy?: string, podNotes?: string): void {
    if (this._status !== SlsDeliveryStatus.shipped && this._status !== SlsDeliveryStatus.inTransit) throw new DomainError("BusinessRule", "Delivery not in transit");
    this._status = SlsDeliveryStatus.delivered;
    this._deliveredAt = new Date();
    if (podReceivedBy) this._podReceivedBy = podReceivedBy;
    if (podNotes) this._podNotes = podNotes;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new DeliveryOrderDelivered(this._id.value, new Date(), { deliveryNumber: this._deliveryNumber }));
  }

  confirm(): void {
    if (this._status !== SlsDeliveryStatus.delivered) throw new DomainError("BusinessRule", "Only delivered delivery can be confirmed");
    this._status = SlsDeliveryStatus.confirmed;
    this._confirmedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new DeliveryConfirmed(this._id.value, new Date(), { deliveryNumber: this._deliveryNumber }));
  }

  reportException(exceptionType: string, reason: string): void {
    this._status = SlsDeliveryStatus.deliveryFailed;
    this._exceptionType = exceptionType; this._exceptionReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  cancel(reason: string): void {
    if (this._status === SlsDeliveryStatus.delivered || this._status === SlsDeliveryStatus.confirmed) throw new DomainError("BusinessRule", "Cannot cancel delivered/confirmed delivery");
    this._status = SlsDeliveryStatus.cancelled;
    this._exceptionReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): DeliveryOrderState {
    return { id: this._id.value, deliveryNumber: this._deliveryNumber, companyId: this._companyId,
      branchId: this._branchId, orderId: this._orderId, orderNumber: this._orderNumber,
      customerId: this._customerId, customerName: this._customerName,
      deliveryAddress: this._deliveryAddress, deliveryWard: this._deliveryWard,
      deliveryDistrict: this._deliveryDistrict, deliveryProvince: this._deliveryProvince,
      deliveryContact: this._deliveryContact, deliveryPhone: this._deliveryPhone,
      deliveryType: this._deliveryType, status: this._status, deliveryDate: this._deliveryDate,
      requestedDate: this._requestedDate, shippedAt: this._shippedAt,
      deliveredAt: this._deliveredAt, confirmedAt: this._confirmedAt,
      carrierId: this._carrierId, carrierName: this._carrierName,
      trackingNumber: this._trackingNumber, shipmentMethod: this._shipmentMethod,
      podReceivedBy: this._podReceivedBy, podSignedAt: this._podSignedAt,
      podImage: this._podImage, podNotes: this._podNotes,
      exceptionType: this._exceptionType, exceptionReason: this._exceptionReason,
      notes: this._notes, internalNotes: this._internalNotes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
