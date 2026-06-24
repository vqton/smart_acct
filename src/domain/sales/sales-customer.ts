import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CustomerId } from "./sales-ids.js";
import { SlsCustomerStatus, SlsCustomerType, SlsCustomerCategory, SlsPriceGroup, SlsDiscountGroup } from "./sales-enums.js";
import { CustomerCreated, CustomerUpdated, CustomerBlocked, CustomerCreditLimitChanged, CustomerBlacklisted } from "./sales-events.js";

export interface CustomerState {
  id: string; code: string; name: string; nameEn: string | null;
  groupId: string | null; customerType: string; category: string; classification: string | null;
  taxCode: string | null; taxAuthority: string | null; taxOffice: string | null;
  address: string | null; ward: string | null; district: string | null; province: string | null;
  country: string; postalCode: string | null;
  phone: string | null; email: string | null; website: string | null;
  paymentTermCode: string | null; priceGroup: string; discountGroup: string;
  currencyCode: string; creditLimit: number; creditUsed: number; creditAvailable: number;
  creditStatus: string; allowNegativeDebt: boolean;
  status: string; isActive: boolean; isBlacklisted: boolean; blacklistReason: string | null;
  storeId: string | null; salespersonId: string | null; branchId: string | null;
  registeredAt: Date | null; lastPurchaseAt: Date | null;
  totalPurchases: number; totalReturns: number; totalOrders: number;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class Customer extends AggregateRoot<CustomerId> {
  private _id: CustomerId; private _code: string; private _name: string;
  private _nameEn: string | null; private _groupId: string | null;
  private _customerType: SlsCustomerType; private _category: SlsCustomerCategory;
  private _classification: string | null; private _taxCode: string | null;
  private _taxAuthority: string | null; private _taxOffice: string | null;
  private _address: string | null; private _ward: string | null; private _district: string | null;
  private _province: string | null; private _country: string; private _postalCode: string | null;
  private _phone: string | null; private _email: string | null; private _website: string | null;
  private _paymentTermCode: string | null; private _priceGroup: SlsPriceGroup;
  private _discountGroup: SlsDiscountGroup; private _currencyCode: string;
  private _creditLimit: number; private _creditUsed: number; private _creditAvailable: number;
  private _creditStatus: string; private _allowNegativeDebt: boolean;
  private _status: SlsCustomerStatus; private _isActive: boolean;
  private _isBlacklisted: boolean; private _blacklistReason: string | null;
  private _storeId: string | null; private _salespersonId: string | null;
  private _branchId: string | null; private _registeredAt: Date | null;
  private _lastPurchaseAt: Date | null; private _totalPurchases: number;
  private _totalReturns: number; private _totalOrders: number;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: CustomerId, code: string, name: string) {
    super(); this._id = id; this._code = code; this._name = name;
    this._customerType = SlsCustomerType.retail; this._category = SlsCustomerCategory.standard;
    this._priceGroup = SlsPriceGroup.retail; this._discountGroup = SlsDiscountGroup.none;
    this._currencyCode = "VND"; this._creditLimit = 0; this._creditUsed = 0;
    this._creditAvailable = 0; this._creditStatus = "good"; this._allowNegativeDebt = false;
    this._status = SlsCustomerStatus.active; this._isActive = true; this._isBlacklisted = false;
    this._country = "VN"; this._totalPurchases = 0; this._totalReturns = 0; this._totalOrders = 0;
    this._nameEn = null; this._groupId = null; this._classification = null;
    this._taxCode = null; this._taxAuthority = null; this._taxOffice = null;
    this._address = null; this._ward = null; this._district = null; this._province = null;
    this._postalCode = null; this._phone = null; this._email = null; this._website = null;
    this._paymentTermCode = null; this._blacklistReason = null; this._storeId = null;
    this._salespersonId = null; this._branchId = null; this._registeredAt = null;
    this._lastPurchaseAt = null; this._version = 1; this._createdAt = new Date();
    this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { code: string; name: string; nameEn?: string; groupId?: string; customerType?: SlsCustomerType; category?: SlsCustomerCategory; taxCode?: string; phone?: string; email?: string; address?: string; ward?: string; district?: string; province?: string; country?: string; priceGroup?: SlsPriceGroup; discountGroup?: SlsDiscountGroup; creditLimit?: number; currencyCode?: string; paymentTermCode?: string; storeId?: string; salespersonId?: string; branchId?: string }): Customer {
    const c = new Customer(CustomerId.new(), p.code, p.name);
    c._nameEn = p.nameEn ?? null; c._groupId = p.groupId ?? null;
    c._customerType = p.customerType ?? SlsCustomerType.retail;
    c._category = p.category ?? SlsCustomerCategory.standard;
    c._taxCode = p.taxCode ?? null; c._phone = p.phone ?? null; c._email = p.email ?? null;
    c._address = p.address ?? null; c._ward = p.ward ?? null; c._district = p.district ?? null;
    c._province = p.province ?? null; c._country = p.country ?? "VN";
    c._priceGroup = p.priceGroup ?? SlsPriceGroup.retail;
    c._discountGroup = p.discountGroup ?? SlsDiscountGroup.none;
    c._creditLimit = p.creditLimit ?? 0; c._creditAvailable = c._creditLimit;
    c._currencyCode = p.currencyCode ?? "VND"; c._paymentTermCode = p.paymentTermCode ?? null;
    c._storeId = p.storeId ?? null; c._salespersonId = p.salespersonId ?? null;
    c._branchId = p.branchId ?? null; c._registeredAt = new Date();
    c.addEvent(new CustomerCreated(c._id.value, new Date(), { code: c._code, name: c._name }));
    return c;
  }

  static load(s: CustomerState): Customer {
    const c = new Customer(new CustomerId(s.id), s.code, s.name);
    c._nameEn = s.nameEn; c._groupId = s.groupId;
    c._customerType = s.customerType as SlsCustomerType;
    c._category = s.category as SlsCustomerCategory;
    c._classification = s.classification; c._taxCode = s.taxCode;
    c._taxAuthority = s.taxAuthority; c._taxOffice = s.taxOffice;
    c._address = s.address; c._ward = s.ward; c._district = s.district;
    c._province = s.province; c._country = s.country; c._postalCode = s.postalCode;
    c._phone = s.phone; c._email = s.email; c._website = s.website;
    c._paymentTermCode = s.paymentTermCode;
    c._priceGroup = s.priceGroup as SlsPriceGroup;
    c._discountGroup = s.discountGroup as SlsDiscountGroup;
    c._currencyCode = s.currencyCode; c._creditLimit = s.creditLimit;
    c._creditUsed = s.creditUsed; c._creditAvailable = s.creditAvailable;
    c._creditStatus = s.creditStatus; c._allowNegativeDebt = s.allowNegativeDebt;
    c._status = s.status as SlsCustomerStatus; c._isActive = s.isActive;
    c._isBlacklisted = s.isBlacklisted; c._blacklistReason = s.blacklistReason;
    c._storeId = s.storeId; c._salespersonId = s.salespersonId; c._branchId = s.branchId;
    c._registeredAt = s.registeredAt; c._lastPurchaseAt = s.lastPurchaseAt;
    c._totalPurchases = s.totalPurchases; c._totalReturns = s.totalReturns;
    c._totalOrders = s.totalOrders; c._version = s.version; c._createdAt = s.createdAt;
    c._updatedAt = s.updatedAt; c._deletedAt = s.deletedAt;
    return c;
  }

  get id(): CustomerId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get status(): SlsCustomerStatus { return this._status; }
  get isActive(): boolean { return this._isActive; }
  get isBlacklisted(): boolean { return this._isBlacklisted; }
  get creditLimit(): number { return this._creditLimit; }
  get creditUsed(): number { return this._creditUsed; }
  get creditAvailable(): number { return this._creditAvailable; }
  get customerType(): SlsCustomerType { return this._customerType; }
  get priceGroup(): SlsPriceGroup { return this._priceGroup; }
  get discountGroup(): SlsDiscountGroup { return this._discountGroup; }
  get taxCode(): string | null { return this._taxCode; }
  get version(): number { return this._version; }

  update(p: Partial<{ name: string; nameEn: string; phone: string; email: string; address: string; ward: string; district: string; province: string; priceGroup: SlsPriceGroup; discountGroup: SlsDiscountGroup; paymentTermCode: string; salespersonId: string; branchId: string }>): void {
    if (p.name) this._name = p.name; if (p.nameEn !== undefined) this._nameEn = p.nameEn;
    if (p.phone !== undefined) this._phone = p.phone; if (p.email !== undefined) this._email = p.email;
    if (p.address !== undefined) this._address = p.address; if (p.ward !== undefined) this._ward = p.ward;
    if (p.district !== undefined) this._district = p.district;
    if (p.province !== undefined) this._province = p.province;
    if (p.priceGroup) this._priceGroup = p.priceGroup;
    if (p.discountGroup) this._discountGroup = p.discountGroup;
    if (p.paymentTermCode !== undefined) this._paymentTermCode = p.paymentTermCode;
    if (p.salespersonId !== undefined) this._salespersonId = p.salespersonId;
    if (p.branchId !== undefined) this._branchId = p.branchId;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new CustomerUpdated(this._id.value, new Date(), { code: this._code }));
  }

  setCreditLimit(newLimit: number, reason?: string): void {
    const oldLimit = this._creditLimit;
    this._creditLimit = newLimit;
    this._creditAvailable = newLimit - this._creditUsed;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new CustomerCreditLimitChanged(this._id.value, new Date(), { code: this._code, oldLimit, newLimit, reason }));
  }

  recordPurchase(amount: number): void {
    this._totalPurchases += amount; this._totalOrders++;
    this._creditUsed += amount; this._creditAvailable = this._creditLimit - this._creditUsed;
    this._lastPurchaseAt = new Date();
    if (this._creditAvailable < 0 && !this._allowNegativeDebt) this._creditStatus = "exceeded";
    this._updatedAt = new Date(); this._version++;
  }

  recordReturn(amount: number): void {
    this._totalReturns += amount;
    this._creditUsed = Math.max(0, this._creditUsed - amount);
    this._creditAvailable = this._creditLimit - this._creditUsed;
    if (this._creditAvailable >= 0) this._creditStatus = "good";
    this._updatedAt = new Date(); this._version++;
  }

  recordPayment(amount: number): void {
    this._creditUsed = Math.max(0, this._creditUsed - amount);
    this._creditAvailable = this._creditLimit - this._creditUsed;
    if (this._creditAvailable >= 0) this._creditStatus = "good";
    this._updatedAt = new Date(); this._version++;
  }

  block(reason: string): void {
    if (this._status === SlsCustomerStatus.blocked) throw new DomainError("BusinessRule", "Customer already blocked");
    this._status = SlsCustomerStatus.blocked; this._isActive = false;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new CustomerBlocked(this._id.value, new Date(), { code: this._code, reason }));
  }

  unblock(): void {
    if (this._status !== SlsCustomerStatus.blocked) throw new DomainError("BusinessRule", "Customer not blocked");
    this._status = SlsCustomerStatus.active; this._isActive = true;
    this._updatedAt = new Date(); this._version++;
  }

  blacklist(reason: string): void {
    this._isBlacklisted = true; this._blacklistReason = reason;
    this._isActive = false;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new CustomerBlacklisted(this._id.value, new Date(), { code: this._code, reason }));
  }

  removeBlacklist(): void {
    this._isBlacklisted = false; this._blacklistReason = null;
    this._isActive = true;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): CustomerState {
    return { id: this._id.value, code: this._code, name: this._name,
      nameEn: this._nameEn, groupId: this._groupId, customerType: this._customerType,
      category: this._category, classification: this._classification, taxCode: this._taxCode,
      taxAuthority: this._taxAuthority, taxOffice: this._taxOffice,
      address: this._address, ward: this._ward, district: this._district,
      province: this._province, country: this._country, postalCode: this._postalCode,
      phone: this._phone, email: this._email, website: this._website,
      paymentTermCode: this._paymentTermCode, priceGroup: this._priceGroup,
      discountGroup: this._discountGroup, currencyCode: this._currencyCode,
      creditLimit: this._creditLimit, creditUsed: this._creditUsed,
      creditAvailable: this._creditAvailable, creditStatus: this._creditStatus,
      allowNegativeDebt: this._allowNegativeDebt, status: this._status,
      isActive: this._isActive, isBlacklisted: this._isBlacklisted,
      blacklistReason: this._blacklistReason, storeId: this._storeId,
      salespersonId: this._salespersonId, branchId: this._branchId,
      registeredAt: this._registeredAt, lastPurchaseAt: this._lastPurchaseAt,
      totalPurchases: this._totalPurchases, totalReturns: this._totalReturns,
      totalOrders: this._totalOrders, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
