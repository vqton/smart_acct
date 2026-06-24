import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { GiftCardId } from "./sales-ids.js";
import { SlsGiftCardStatus } from "./sales-enums.js";
import { GiftCardIssued, GiftCardRedeemed } from "./sales-events.js";

export interface GiftCardState {
  id: string; cardNumber: string; pinCode: string | null;
  initialBalance: number; currentBalance: number; currencyCode: string;
  status: string; customerId: string | null;
  issuedBy: string; issuedAt: Date; activatedAt: Date | null;
  expiredAt: Date | null; lastUsedAt: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class GiftCard extends AggregateRoot<GiftCardId> {
  private _id: GiftCardId; private _cardNumber: string; private _pinCode: string | null;
  private _initialBalance: number; private _currentBalance: number;
  private _currencyCode: string; private _status: SlsGiftCardStatus;
  private _customerId: string | null; private _issuedBy: string; private _issuedAt: Date;
  private _activatedAt: Date | null; private _expiredAt: Date | null;
  private _lastUsedAt: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: GiftCardId, cardNumber: string, initialBalance: number, issuedBy: string) {
    super(); this._id = id; this._cardNumber = cardNumber;
    this._initialBalance = initialBalance; this._currentBalance = initialBalance;
    this._issuedBy = issuedBy; this._issuedAt = new Date();
    this._currencyCode = "VND"; this._status = SlsGiftCardStatus.active;
    this._pinCode = null; this._customerId = null; this._activatedAt = null;
    this._expiredAt = null; this._lastUsedAt = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(cardNumber: string, initialBalance: number, issuedBy: string, customerId?: string, pinCode?: string, expiredAt?: Date): GiftCard {
    if (initialBalance <= 0) throw new DomainError("Validation", "Initial balance must be positive");
    const gc = new GiftCard(GiftCardId.new(), cardNumber, initialBalance, issuedBy);
    gc._customerId = customerId ?? null; gc._pinCode = pinCode ?? null;
    gc._expiredAt = expiredAt ?? null; gc._activatedAt = new Date();
    gc.addEvent(new GiftCardIssued(gc._id.value, new Date(), { cardNumber: gc._cardNumber, initialBalance, issuedBy }));
    return gc;
  }

  static load(s: GiftCardState): GiftCard {
    const gc = new GiftCard(new GiftCardId(s.id), s.cardNumber, s.initialBalance, s.issuedBy);
    gc._pinCode = s.pinCode; gc._currentBalance = s.currentBalance;
    gc._currencyCode = s.currencyCode; gc._status = s.status as SlsGiftCardStatus;
    gc._customerId = s.customerId; gc._issuedAt = s.issuedAt;
    gc._activatedAt = s.activatedAt; gc._expiredAt = s.expiredAt;
    gc._lastUsedAt = s.lastUsedAt; gc._version = s.version; gc._createdAt = s.createdAt;
    gc._updatedAt = s.updatedAt; gc._deletedAt = s.deletedAt;
    return gc;
  }

  get id(): GiftCardId { return this._id; }
  get cardNumber(): string { return this._cardNumber; }
  get currentBalance(): number { return this._currentBalance; }
  get status(): SlsGiftCardStatus { return this._status; }
  get version(): number { return this._version; }

  redeem(amount: number, referenceType?: string, referenceId?: string): void {
    if (this._status !== SlsGiftCardStatus.active && this._status !== SlsGiftCardStatus.partiallyUsed) throw new DomainError("BusinessRule", "Gift card not active");
    if (this._expiredAt && new Date() > this._expiredAt) throw new DomainError("BusinessRule", "Gift card has expired");
    if (amount <= 0) throw new DomainError("Validation", "Redeem amount must be positive");
    if (amount > this._currentBalance) throw new DomainError("BusinessRule", "Insufficient gift card balance");
    this._currentBalance -= amount;
    this._lastUsedAt = new Date();
    this._status = this._currentBalance <= 0 ? SlsGiftCardStatus.fullyUsed : SlsGiftCardStatus.partiallyUsed;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new GiftCardRedeemed(this._id.value, new Date(), { cardNumber: this._cardNumber, amount, remaining: this._currentBalance }));
  }

  topUp(amount: number): void {
    if (amount <= 0) throw new DomainError("Validation", "Top-up amount must be positive");
    if (this._status === SlsGiftCardStatus.fullyUsed || this._status === SlsGiftCardStatus.expired || this._status === SlsGiftCardStatus.cancelled) throw new DomainError("BusinessRule", "Cannot top-up gift card in current status");
    this._currentBalance += amount;
    this._status = SlsGiftCardStatus.active;
    this._updatedAt = new Date(); this._version++;
  }

  cancel(): void {
    this._status = SlsGiftCardStatus.cancelled;
    this._currentBalance = 0;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): GiftCardState {
    return { id: this._id.value, cardNumber: this._cardNumber, pinCode: this._pinCode,
      initialBalance: this._initialBalance, currentBalance: this._currentBalance,
      currencyCode: this._currencyCode, status: this._status, customerId: this._customerId,
      issuedBy: this._issuedBy, issuedAt: this._issuedAt, activatedAt: this._activatedAt,
      expiredAt: this._expiredAt, lastUsedAt: this._lastUsedAt,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
