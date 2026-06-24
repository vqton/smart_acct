import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { LoyaltyAccountId } from "./sales-ids.js";
import { SlsLoyaltyTier, SlsLoyaltyStatus } from "./sales-enums.js";
import { LoyaltyPointsEarned, LoyaltyPointsRedeemed, LoyaltyTierChanged } from "./sales-events.js";

export interface LoyaltyAccountState {
  id: string; customerId: string; tier: string;
  totalPoints: number; currentPoints: number; lifetimePoints: number;
  lifetimeRevenue: number; currencyCode: string;
  status: string; enrolledAt: Date; tierUpgradedAt: Date | null;
  lastActivityAt: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

const TIER_THRESHOLDS: Record<SlsLoyaltyTier, number> = {
  [SlsLoyaltyTier.bronze]: 0,
  [SlsLoyaltyTier.silver]: 1000,
  [SlsLoyaltyTier.gold]: 5000,
  [SlsLoyaltyTier.platinum]: 15000,
  [SlsLoyaltyTier.diamond]: 50000,
  [SlsLoyaltyTier.elite]: 150000,
};

const TIER_ORDER: SlsLoyaltyTier[] = [
  SlsLoyaltyTier.bronze, SlsLoyaltyTier.silver, SlsLoyaltyTier.gold,
  SlsLoyaltyTier.platinum, SlsLoyaltyTier.diamond, SlsLoyaltyTier.elite,
];

export class LoyaltyAccount extends AggregateRoot<LoyaltyAccountId> {
  private _id: LoyaltyAccountId; private _customerId: string; private _tier: SlsLoyaltyTier;
  private _totalPoints: number; private _currentPoints: number;
  private _lifetimePoints: number; private _lifetimeRevenue: number;
  private _currencyCode: string; private _status: SlsLoyaltyStatus;
  private _enrolledAt: Date; private _tierUpgradedAt: Date | null;
  private _lastActivityAt: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: LoyaltyAccountId, customerId: string) {
    super(); this._id = id; this._customerId = customerId;
    this._tier = SlsLoyaltyTier.bronze; this._status = SlsLoyaltyStatus.active;
    this._totalPoints = 0; this._currentPoints = 0; this._lifetimePoints = 0;
    this._lifetimeRevenue = 0; this._currencyCode = "VND";
    this._enrolledAt = new Date(); this._tierUpgradedAt = null; this._lastActivityAt = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(customerId: string): LoyaltyAccount {
    const a = new LoyaltyAccount(LoyaltyAccountId.new(), customerId);
    return a;
  }

  static load(s: LoyaltyAccountState): LoyaltyAccount {
    const a = new LoyaltyAccount(new LoyaltyAccountId(s.id), s.customerId);
    a._tier = s.tier as SlsLoyaltyTier; a._totalPoints = s.totalPoints;
    a._currentPoints = s.currentPoints; a._lifetimePoints = s.lifetimePoints;
    a._lifetimeRevenue = s.lifetimeRevenue; a._currencyCode = s.currencyCode;
    a._status = s.status as SlsLoyaltyStatus; a._enrolledAt = s.enrolledAt;
    a._tierUpgradedAt = s.tierUpgradedAt; a._lastActivityAt = s.lastActivityAt;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt;
    a._deletedAt = s.deletedAt;
    return a;
  }

  get id(): LoyaltyAccountId { return this._id; }
  get currentPoints(): number { return this._currentPoints; }
  get tier(): SlsLoyaltyTier { return this._tier; }
  get status(): SlsLoyaltyStatus { return this._status; }
  get version(): number { return this._version; }

  earnPoints(points: number, revenue: number, reason?: string): void {
    if (points <= 0) throw new DomainError("Validation", "Points must be positive");
    if (this._status !== SlsLoyaltyStatus.active) throw new DomainError("BusinessRule", "Loyalty account not active");
    this._totalPoints += points; this._currentPoints += points; this._lifetimePoints += points;
    this._lifetimeRevenue += revenue; this._lastActivityAt = new Date();
    this.recalculateTier();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new LoyaltyPointsEarned(this._id.value, new Date(), { customerId: this._customerId, points, revenue, reason }));
  }

  redeemPoints(points: number, reason?: string): void {
    if (points <= 0) throw new DomainError("Validation", "Points must be positive");
    if (points > this._currentPoints) throw new DomainError("BusinessRule", "Insufficient loyalty points");
    this._currentPoints -= points; this._lastActivityAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new LoyaltyPointsRedeemed(this._id.value, new Date(), { customerId: this._customerId, points, reason }));
  }

  private recalculateTier(): void {
    const oldTier = this._tier;
    let newTier = this._tier;
    for (let i = TIER_ORDER.length - 1; i >= 0; i--) {
      if (this._lifetimePoints >= TIER_THRESHOLDS[TIER_ORDER[i]]) {
        newTier = TIER_ORDER[i];
        break;
      }
    }
    if (newTier !== oldTier) {
      this._tier = newTier;
      this._tierUpgradedAt = new Date();
      this.addEvent(new LoyaltyTierChanged(this._id.value, new Date(), { customerId: this._customerId, oldTier, newTier }));
    }
  }

  suspend(): void {
    this._status = SlsLoyaltyStatus.suspended;
    this._updatedAt = new Date(); this._version++;
  }

  reactivate(): void {
    this._status = SlsLoyaltyStatus.active;
    this._updatedAt = new Date(); this._version++;
  }

  close(): void {
    this._status = SlsLoyaltyStatus.closed;
    this._currentPoints = 0;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): LoyaltyAccountState {
    return { id: this._id.value, customerId: this._customerId, tier: this._tier,
      totalPoints: this._totalPoints, currentPoints: this._currentPoints,
      lifetimePoints: this._lifetimePoints, lifetimeRevenue: this._lifetimeRevenue,
      currencyCode: this._currencyCode, status: this._status, enrolledAt: this._enrolledAt,
      tierUpgradedAt: this._tierUpgradedAt, lastActivityAt: this._lastActivityAt,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
