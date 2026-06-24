import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PromotionId } from "./sales-ids.js";
import { SlsPromotionType, SlsPromotionStatus, SlsDiscountType, SlsCouponStatus } from "./sales-enums.js";
import { PromotionApplied, CouponRedeemed } from "./sales-events.js";

export interface PromotionState {
  id: string; code: string; name: string; promotionType: string; status: string;
  description: string | null; appliesTo: string;
  customerGroupIds: string | null; storeIds: string | null; itemIds: string | null;
  startDate: Date; endDate: Date;
  discountType: string; discountValue: number; discountPercent: number;
  maxDiscount: number | null; minOrderAmount: number | null; maxQuantity: number | null;
  budgetAmount: number | null; usedAmount: number; usageLimit: number | null;
  usageCount: number; perCustomerLimit: number | null;
  requiresApproval: boolean; approvedBy: string | null; approvedAt: Date | null;
  termsAndConditions: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class Promotion extends AggregateRoot<PromotionId> {
  private _id: PromotionId; private _code: string; private _name: string;
  private _promotionType: SlsPromotionType; private _status: SlsPromotionStatus;
  private _description: string | null; private _appliesTo: string;
  private _customerGroupIds: string | null; private _storeIds: string | null;
  private _itemIds: string | null;
  private _startDate: Date; private _endDate: Date;
  private _discountType: SlsDiscountType; private _discountValue: number;
  private _discountPercent: number; private _maxDiscount: number | null;
  private _minOrderAmount: number | null; private _maxQuantity: number | null;
  private _budgetAmount: number | null; private _usedAmount: number;
  private _usageLimit: number | null; private _usageCount: number;
  private _perCustomerLimit: number | null;
  private _requiresApproval: boolean; private _approvedBy: string | null;
  private _approvedAt: Date | null; private _termsAndConditions: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: PromotionId, code: string, name: string, promotionType: SlsPromotionType, startDate: Date, endDate: Date) {
    super(); this._id = id; this._code = code; this._name = name;
    this._promotionType = promotionType; this._status = SlsPromotionStatus.draft;
    this._startDate = startDate; this._endDate = endDate;
    this._appliesTo = "all"; this._discountType = SlsDiscountType.percentage;
    this._discountValue = 0; this._discountPercent = 0; this._usedAmount = 0; this._usageCount = 0;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
    this._description = null; this._customerGroupIds = null; this._storeIds = null;
    this._itemIds = null; this._maxDiscount = null; this._minOrderAmount = null;
    this._maxQuantity = null; this._budgetAmount = null; this._usageLimit = null;
    this._perCustomerLimit = null; this._requiresApproval = false;
    this._approvedBy = null; this._approvedAt = null; this._termsAndConditions = null;
  }

  static create(p: { code: string; name: string; promotionType: SlsPromotionType; startDate: Date; endDate: Date; description?: string; appliesTo?: string; customerGroupIds?: string; storeIds?: string; itemIds?: string; discountType?: SlsDiscountType; discountValue?: number; discountPercent?: number; maxDiscount?: number; minOrderAmount?: number; maxQuantity?: number; budgetAmount?: number; usageLimit?: number; perCustomerLimit?: number; requiresApproval?: boolean; termsAndConditions?: string }): Promotion {
    const pro = new Promotion(PromotionId.new(), p.code, p.name, p.promotionType, p.startDate, p.endDate);
    pro._description = p.description ?? null; pro._appliesTo = p.appliesTo ?? "all";
    pro._customerGroupIds = p.customerGroupIds ?? null; pro._storeIds = p.storeIds ?? null;
    pro._itemIds = p.itemIds ?? null;
    pro._discountType = p.discountType ?? SlsDiscountType.percentage;
    pro._discountValue = p.discountValue ?? 0; pro._discountPercent = p.discountPercent ?? 0;
    pro._maxDiscount = p.maxDiscount ?? null; pro._minOrderAmount = p.minOrderAmount ?? null;
    pro._maxQuantity = p.maxQuantity ?? null; pro._budgetAmount = p.budgetAmount ?? null;
    pro._usageLimit = p.usageLimit ?? null; pro._perCustomerLimit = p.perCustomerLimit ?? null;
    pro._requiresApproval = p.requiresApproval ?? false;
    pro._termsAndConditions = p.termsAndConditions ?? null;
    return pro;
  }

  static load(s: PromotionState): Promotion {
    const pro = new Promotion(new PromotionId(s.id), s.code, s.name, s.promotionType as SlsPromotionType, s.startDate, s.endDate);
    pro._status = s.status as SlsPromotionStatus; pro._description = s.description;
    pro._appliesTo = s.appliesTo; pro._customerGroupIds = s.customerGroupIds;
    pro._storeIds = s.storeIds; pro._itemIds = s.itemIds;
    pro._discountType = s.discountType as SlsDiscountType; pro._discountValue = s.discountValue;
    pro._discountPercent = s.discountPercent; pro._maxDiscount = s.maxDiscount;
    pro._minOrderAmount = s.minOrderAmount; pro._maxQuantity = s.maxQuantity;
    pro._budgetAmount = s.budgetAmount; pro._usedAmount = s.usedAmount;
    pro._usageLimit = s.usageLimit; pro._usageCount = s.usageCount;
    pro._perCustomerLimit = s.perCustomerLimit; pro._requiresApproval = s.requiresApproval;
    pro._approvedBy = s.approvedBy; pro._approvedAt = s.approvedAt;
    pro._termsAndConditions = s.termsAndConditions;
    pro._version = s.version; pro._createdAt = s.createdAt; pro._updatedAt = s.updatedAt;
    pro._deletedAt = s.deletedAt;
    return pro;
  }

  get id(): PromotionId { return this._id; }
  get code(): string { return this._code; }
  get status(): SlsPromotionStatus { return this._status; }
  get discountPercent(): number { return this._discountPercent; }
  get discountType(): SlsDiscountType { return this._discountType; }
  get version(): number { return this._version; }

  isApplicable(orderAmount: number, customerGroupId?: string, storeId?: string): boolean {
    if (this._status !== SlsPromotionStatus.active) return false;
    const now = new Date();
    if (now < this._startDate || now > this._endDate) return false;
    if (this._usageLimit && this._usageCount >= this._usageLimit) return false;
    if (this._budgetAmount && this._usedAmount >= this._budgetAmount) return false;
    if (this._minOrderAmount && orderAmount < this._minOrderAmount) return false;
    return true;
  }

  activate(): void {
    if (this._status !== SlsPromotionStatus.draft && this._status !== SlsPromotionStatus.scheduled && this._status !== SlsPromotionStatus.paused) throw new DomainError("BusinessRule", "Cannot activate promotion in current status");
    this._status = SlsPromotionStatus.active;
    this._updatedAt = new Date(); this._version++;
  }

  pause(): void {
    if (this._status !== SlsPromotionStatus.active) throw new DomainError("BusinessRule", "Only active promotion can be paused");
    this._status = SlsPromotionStatus.paused;
    this._updatedAt = new Date(); this._version++;
  }

  recordUsage(amount: number): void {
    if (this._usageLimit && this._usageCount >= this._usageLimit) throw new DomainError("BusinessRule", "Promotion usage limit reached");
    this._usageCount++;
    this._usedAmount += amount;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PromotionApplied(this._id.value, new Date(), { code: this._code, amount }));
  }

  markExpired(): void {
    this._status = SlsPromotionStatus.expired;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): PromotionState {
    return { id: this._id.value, code: this._code, name: this._name,
      promotionType: this._promotionType, status: this._status, description: this._description,
      appliesTo: this._appliesTo, customerGroupIds: this._customerGroupIds,
      storeIds: this._storeIds, itemIds: this._itemIds,
      startDate: this._startDate, endDate: this._endDate,
      discountType: this._discountType, discountValue: this._discountValue,
      discountPercent: this._discountPercent, maxDiscount: this._maxDiscount,
      minOrderAmount: this._minOrderAmount, maxQuantity: this._maxQuantity,
      budgetAmount: this._budgetAmount, usedAmount: this._usedAmount,
      usageLimit: this._usageLimit, usageCount: this._usageCount,
      perCustomerLimit: this._perCustomerLimit, requiresApproval: this._requiresApproval,
      approvedBy: this._approvedBy, approvedAt: this._approvedAt,
      termsAndConditions: this._termsAndConditions,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt };
  }
}
