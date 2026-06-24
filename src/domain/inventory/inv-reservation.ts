import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { InventoryReservationId, ReservationLineId } from "./inv-ids.js";
import { ReservationStatus } from "./inv-enums.js";
import { InventoryReserved, ReservationReleased } from "./inv-events.js";

export interface ReservationLineState {
  id: string;
  reservationId: string;
  lineNumber: number;
  itemId: string;
  warehouseId: string;
  locationId: string | null;
  lotId: string | null;
  quantity: number;
  fulfilledQty: number;
  cancelledQty: number;
}

export class ReservationLine {
  constructor(
    private _id: ReservationLineId,
    private _reservationId: string,
    private _lineNumber: number,
    private _itemId: string,
    private _warehouseId: string,
    private _quantity: number,
    private _fulfilledQty: number = 0,
    private _cancelledQty: number = 0,
    private _locationId: string | null = null,
    private _lotId: string | null = null,
  ) {}

  static create(p: {
    reservationId: string; lineNumber: number; itemId: string;
    warehouseId: string; quantity: number; locationId?: string; lotId?: string;
  }): ReservationLine {
    return new ReservationLine(
      ReservationLineId.new(), p.reservationId, p.lineNumber, p.itemId,
      p.warehouseId, p.quantity, 0, 0, p.locationId ?? null, p.lotId ?? null,
    );
  }

  static load(s: ReservationLineState): ReservationLine {
    return new ReservationLine(
      new ReservationLineId(s.id), s.reservationId, s.lineNumber, s.itemId,
      s.warehouseId, s.quantity, s.fulfilledQty, s.cancelledQty,
      s.locationId, s.lotId,
    );
  }

  get id() { return this._id; }
  get itemId() { return this._itemId; }
  get warehouseId() { return this._warehouseId; }
  get quantity() { return this._quantity; }
  get fulfilledQty() { return this._fulfilledQty; }
  get openQty() { return this._quantity - this._fulfilledQty - this._cancelledQty; }
  get isFulfilled() { return this.openQty <= 0; }

  fulfill(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Fulfill quantity must be positive");
    if (quantity > this.openQty) throw new DomainError("BusinessRule", "Cannot fulfill more than open quantity");
    this._fulfilledQty += quantity;
  }

  cancel(quantity: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Cancel quantity must be positive");
    if (quantity > this.openQty) throw new DomainError("BusinessRule", "Cannot cancel more than open quantity");
    this._cancelledQty += quantity;
  }

  toState(): ReservationLineState {
    return {
      id: this._id.value, reservationId: this._reservationId,
      lineNumber: this._lineNumber, itemId: this._itemId,
      warehouseId: this._warehouseId, locationId: this._locationId,
      lotId: this._lotId, quantity: this._quantity,
      fulfilledQty: this._fulfilledQty, cancelledQty: this._cancelledQty,
    };
  }
}

export interface ReservationState {
  id: string;
  reservationNumber: string;
  status: string;
  orderType: string;
  orderId: string;
  orderLineId: string | null;
  companyId: string;
  customerId: string | null;
  warehouseId: string | null;
  reservedAt: Date;
  expiresAt: Date | null;
  fulfilledAt: Date | null;
  cancelledAt: Date | null;
  cancelReason: string | null;
  lines: ReservationLineState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class InventoryReservation extends AggregateRoot<InventoryReservationId> {
  private _id: InventoryReservationId;
  private _reservationNumber: string;
  private _status: ReservationStatus;
  private _orderType: string;
  private _orderId: string;
  private _orderLineId: string | null;
  private _companyId: string;
  private _customerId: string | null;
  private _warehouseId: string | null;
  private _reservedAt: Date;
  private _expiresAt: Date | null;
  private _fulfilledAt: Date | null;
  private _cancelledAt: Date | null;
  private _cancelReason: string | null;
  private _lines: ReservationLine[] = [];
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: InventoryReservationId, reservationNumber: string, orderType: string, orderId: string, companyId: string) {
    super();
    this._id = id;
    this._reservationNumber = reservationNumber;
    this._orderType = orderType;
    this._orderId = orderId;
    this._companyId = companyId;
    this._status = ReservationStatus.Active;
    this._orderLineId = null;
    this._customerId = null;
    this._warehouseId = null;
    this._reservedAt = new Date();
    this._expiresAt = null;
    this._fulfilledAt = null;
    this._cancelledAt = null;
    this._cancelReason = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(p: {
    reservationNumber: string; orderType: string; orderId: string;
    companyId: string; orderLineId?: string; customerId?: string;
    warehouseId?: string; expiresAt?: Date;
  }): InventoryReservation {
    const r = new InventoryReservation(
      InventoryReservationId.new(), p.reservationNumber, p.orderType, p.orderId, p.companyId,
    );
    r._orderLineId = p.orderLineId ?? null;
    r._customerId = p.customerId ?? null;
    r._warehouseId = p.warehouseId ?? null;
    r._expiresAt = p.expiresAt ?? null;
    r.addEvent(InventoryReserved.create(r._id.value, {
      reservationNumber: r._reservationNumber, orderType: r._orderType, orderId: r._orderId,
    }));
    return r;
  }

  static load(s: ReservationState): InventoryReservation {
    const r = new InventoryReservation(
      new InventoryReservationId(s.id), s.reservationNumber, s.orderType, s.orderId, s.companyId,
    );
    r._status = s.status as ReservationStatus;
    r._orderLineId = s.orderLineId;
    r._customerId = s.customerId;
    r._warehouseId = s.warehouseId;
    r._reservedAt = s.reservedAt;
    r._expiresAt = s.expiresAt;
    r._fulfilledAt = s.fulfilledAt;
    r._cancelledAt = s.cancelledAt;
    r._cancelReason = s.cancelReason;
    r._lines = s.lines.map(l => ReservationLine.load(l));
    r._version = s.version;
    r._createdAt = s.createdAt;
    r._updatedAt = s.updatedAt;
    return r;
  }

  get id() { return this._id; }
  get reservationNumber() { return this._reservationNumber; }
  get status() { return this._status; }
  get orderId() { return this._orderId; }
  get lines() { return [...this._lines]; }
  get version() { return this._version; }

  addLine(line: ReservationLine): void {
    if (this._status !== ReservationStatus.Active) {
      throw new DomainError("BusinessRule", "Cannot add line to non-active reservation");
    }
    this._lines.push(line);
    this._version++;
    this._updatedAt = new Date();
  }

  fulfill(): void {
    if (this._status !== ReservationStatus.Active) throw new DomainError("BusinessRule", "Only active reservations can be fulfilled");
    for (const line of this._lines) {
      if (!line.isFulfilled) throw new DomainError("BusinessRule", "All lines must be fulfilled");
    }
    this._status = ReservationStatus.Fulfilled;
    this._fulfilledAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  cancel(reason: string): void {
    if (this._status === ReservationStatus.Fulfilled || this._status === ReservationStatus.Cancelled) {
      throw new DomainError("BusinessRule", "Cannot cancel fulfilled or already cancelled reservation");
    }
    this._status = ReservationStatus.Cancelled;
    this._cancelReason = reason;
    this._cancelledAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(ReservationReleased.create(this._id.value, { reservationNumber: this._reservationNumber, reason }));
  }

  expire(): void {
    if (this._status !== ReservationStatus.Active) throw new DomainError("BusinessRule", "Only active reservations can expire");
    this._status = ReservationStatus.Expired;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(ReservationReleased.create(this._id.value, { reservationNumber: this._reservationNumber, reason: "expired" }));
  }

  toState(): ReservationState {
    return {
      id: this._id.value, reservationNumber: this._reservationNumber,
      status: this._status, orderType: this._orderType, orderId: this._orderId,
      orderLineId: this._orderLineId, companyId: this._companyId,
      customerId: this._customerId, warehouseId: this._warehouseId,
      reservedAt: this._reservedAt, expiresAt: this._expiresAt,
      fulfilledAt: this._fulfilledAt, cancelledAt: this._cancelledAt,
      cancelReason: this._cancelReason,
      lines: this._lines.map(l => l.toState()),
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
