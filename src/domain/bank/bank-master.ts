import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankId, BankBranchId, BankGroupId, CorrespondentBankId } from "./bank-ids.js";
import { BankGroupType, CorrespondentType } from "./bank-enums.js";
import { SwiftCode, RoutingNumber, BankCode, Address } from "./bank-value-objects.js";
import { BankCreated, BankDeactivated } from "./bank-events.js";

// ─── Bank Group ────────────────────────────────────────────────────────────────

export interface BankGroupState {
  id: string; code: string; name: string; nameEn: string | null;
  groupType: string; isActive: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankGroup extends AggregateRoot<BankGroupId> {
  private _id: BankGroupId; private _code: string; private _name: string;
  private _nameEn: string | null; private _groupType: BankGroupType;
  private _isActive: boolean; private _version: number;
  private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: BankGroupId, code: string, name: string, groupType: BankGroupType) {
    super(); this._id = id; this._code = code; this._name = name;
    this._nameEn = null; this._groupType = groupType; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { code: string; name: string; nameEn?: string; groupType: BankGroupType }): BankGroup {
    const g = new BankGroup(BankGroupId.new(), p.code, p.name, p.groupType);
    g._nameEn = p.nameEn ?? null; return g;
  }

  static load(s: BankGroupState): BankGroup {
    const g = new BankGroup(new BankGroupId(s.id), s.code, s.name, s.groupType as BankGroupType);
    g._nameEn = s.nameEn; g._isActive = s.isActive; g._version = s.version;
    g._createdAt = s.createdAt; g._updatedAt = s.updatedAt; g._deletedAt = s.deletedAt;
    return g;
  }

  get id(): BankGroupId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get groupType(): BankGroupType { return this._groupType; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Bank group already inactive");
    this._isActive = false; this._updatedAt = new Date(); this._version++;
  }

  toState(): BankGroupState {
    return { id: this._id.value, code: this._code, name: this._name, nameEn: this._nameEn,
      groupType: this._groupType, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Bank ───────────────────────────────────────────────────────────────────────

export interface BankState {
  id: string; groupId: string | null; code: string; name: string; nameEn: string | null;
  shortName: string | null; swiftCode: string | null; routingNumber: string | null;
  bankCode: string | null; countryCode: string; address: string | null;
  phone: string | null; email: string | null; website: string | null;
  isActive: boolean; isCorrespondent: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class Bank extends AggregateRoot<BankId> {
  private _id: BankId; private _groupId: string | null; private _code: string;
  private _name: string; private _nameEn: string | null; private _shortName: string | null;
  private _swiftCode: string | null; private _routingNumber: string | null;
  private _bankCode: string | null; private _countryCode: string;
  private _address: string | null; private _phone: string | null;
  private _email: string | null; private _website: string | null;
  private _isActive: boolean; private _isCorrespondent: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: BankId, code: string, name: string, countryCode: string) {
    super(); this._id = id; this._code = code; this._name = name;
    this._nameEn = null; this._shortName = null; this._swiftCode = null;
    this._routingNumber = null; this._bankCode = null; this._countryCode = countryCode;
    this._address = null; this._phone = null; this._email = null; this._website = null;
    this._isActive = true; this._isCorrespondent = false; this._groupId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    code: string; name: string; countryCode: string; nameEn?: string; shortName?: string;
    swiftCode?: string; routingNumber?: string; bankCode?: string;
    groupId?: string; isCorrespondent?: boolean;
  }): Bank {
    const b = new Bank(BankId.new(), p.code, p.name, p.countryCode);
    b._nameEn = p.nameEn ?? null; b._shortName = p.shortName ?? null;
    b._swiftCode = p.swiftCode ?? null; b._routingNumber = p.routingNumber ?? null;
    b._bankCode = p.bankCode ?? null; b._groupId = p.groupId ?? null;
    b._isCorrespondent = p.isCorrespondent ?? false;
    b.addEvent(new BankCreated(b._id.value, new Date(), { code: b._code, name: b._name }));
    return b;
  }

  static load(s: BankState): Bank {
    const b = new Bank(new BankId(s.id), s.code, s.name, s.countryCode);
    b._nameEn = s.nameEn; b._shortName = s.shortName; b._swiftCode = s.swiftCode;
    b._routingNumber = s.routingNumber; b._bankCode = s.bankCode;
    b._groupId = s.groupId; b._address = s.address; b._phone = s.phone;
    b._email = s.email; b._website = s.website; b._isActive = s.isActive;
    b._isCorrespondent = s.isCorrespondent; b._version = s.version;
    b._createdAt = s.createdAt; b._updatedAt = s.updatedAt; b._deletedAt = s.deletedAt;
    return b;
  }

  get id(): BankId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get swiftCode(): string | null { return this._swiftCode; }
  get routingNumber(): string | null { return this._routingNumber; }
  get countryCode(): string { return this._countryCode; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  update(p: Partial<{ name: string; nameEn: string | null; shortName: string | null; swiftCode: string | null; routingNumber: string | null; bankCode: string | null; address: string | null; phone: string | null; email: string | null; website: string | null; }>): void {
    if (p.name !== undefined) this._name = p.name;
    if (p.nameEn !== undefined) this._nameEn = p.nameEn;
    if (p.shortName !== undefined) this._shortName = p.shortName;
    if (p.swiftCode !== undefined) this._swiftCode = p.swiftCode;
    if (p.routingNumber !== undefined) this._routingNumber = p.routingNumber;
    if (p.bankCode !== undefined) this._bankCode = p.bankCode;
    if (p.address !== undefined) this._address = p.address;
    if (p.phone !== undefined) this._phone = p.phone;
    if (p.email !== undefined) this._email = p.email;
    if (p.website !== undefined) this._website = p.website;
    this._updatedAt = new Date(); this._version++;
  }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Bank already inactive");
    this._isActive = false; this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankDeactivated(this._id.value, new Date(), { code: this._code }));
  }

  activate(): void {
    if (this._isActive) throw new DomainError("BusinessRule", "Bank already active");
    this._isActive = true; this._updatedAt = new Date(); this._version++;
  }

  toState(): BankState {
    return { id: this._id.value, groupId: this._groupId, code: this._code, name: this._name,
      nameEn: this._nameEn, shortName: this._shortName, swiftCode: this._swiftCode,
      routingNumber: this._routingNumber, bankCode: this._bankCode, countryCode: this._countryCode,
      address: this._address, phone: this._phone, email: this._email, website: this._website,
      isActive: this._isActive, isCorrespondent: this._isCorrespondent, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Bank Branch ────────────────────────────────────────────────────────────────

export interface BankBranchState {
  id: string; bankId: string; code: string; name: string; nameEn: string | null;
  address: string | null; phone: string | null; email: string | null;
  managerName: string | null; isActive: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankBranch extends AggregateRoot<BankBranchId> {
  private _id: BankBranchId; private _bankId: string; private _code: string;
  private _name: string; private _nameEn: string | null; private _address: string | null;
  private _phone: string | null; private _email: string | null;
  private _managerName: string | null; private _isActive: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: BankBranchId, bankId: string, code: string, name: string) {
    super(); this._id = id; this._bankId = bankId; this._code = code; this._name = name;
    this._nameEn = null; this._address = null; this._phone = null; this._email = null;
    this._managerName = null; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { bankId: string; code: string; name: string; nameEn?: string; address?: string; phone?: string; email?: string; managerName?: string }): BankBranch {
    const b = new BankBranch(BankBranchId.new(), p.bankId, p.code, p.name);
    b._nameEn = p.nameEn ?? null; b._address = p.address ?? null;
    b._phone = p.phone ?? null; b._email = p.email ?? null; b._managerName = p.managerName ?? null;
    return b;
  }

  static load(s: BankBranchState): BankBranch {
    const b = new BankBranch(new BankBranchId(s.id), s.bankId, s.code, s.name);
    b._nameEn = s.nameEn; b._address = s.address; b._phone = s.phone;
    b._email = s.email; b._managerName = s.managerName; b._isActive = s.isActive;
    b._version = s.version; b._createdAt = s.createdAt; b._updatedAt = s.updatedAt; b._deletedAt = s.deletedAt;
    return b;
  }

  get id(): BankBranchId { return this._id; }
  get bankId(): string { return this._bankId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Branch already inactive");
    this._isActive = false; this._updatedAt = new Date(); this._version++;
  }

  toState(): BankBranchState {
    return { id: this._id.value, bankId: this._bankId, code: this._code, name: this._name,
      nameEn: this._nameEn, address: this._address, phone: this._phone, email: this._email,
      managerName: this._managerName, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Correspondent Bank ─────────────────────────────────────────────────────────

export interface CorrespondentBankState {
  id: string; bankId: string; correspondentBankId: string; accountNumber: string | null;
  correspondentType: string; currencyCode: string; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class CorrespondentBank extends AggregateRoot<CorrespondentBankId> {
  private _id: CorrespondentBankId; private _bankId: string;
  private _correspondentBankId: string; private _accountNumber: string | null;
  private _correspondentType: CorrespondentType; private _currencyCode: string;
  private _isActive: boolean; private _version: number;
  private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: CorrespondentBankId, bankId: string, correspondentBankId: string,
    type: CorrespondentType, currencyCode: string) {
    super(); this._id = id; this._bankId = bankId;
    this._correspondentBankId = correspondentBankId; this._accountNumber = null;
    this._correspondentType = type; this._currencyCode = currencyCode; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { bankId: string; correspondentBankId: string; accountNumber?: string;
    correspondentType: CorrespondentType; currencyCode: string }): CorrespondentBank {
    const c = new CorrespondentBank(CorrespondentBankId.new(), p.bankId, p.correspondentBankId,
      p.correspondentType, p.currencyCode);
    c._accountNumber = p.accountNumber ?? null; return c;
  }

  static load(s: CorrespondentBankState): CorrespondentBank {
    const c = new CorrespondentBank(new CorrespondentBankId(s.id), s.bankId, s.correspondentBankId,
      s.correspondentType as CorrespondentType, s.currencyCode);
    c._accountNumber = s.accountNumber; c._isActive = s.isActive; c._version = s.version;
    c._createdAt = s.createdAt; c._updatedAt = s.updatedAt; c._deletedAt = s.deletedAt;
    return c;
  }

  get id(): CorrespondentBankId { return this._id; }
  get correspondentType(): CorrespondentType { return this._correspondentType; }
  get currencyCode(): string { return this._currencyCode; }
  get isActive(): boolean { return this._isActive; }

  toState(): CorrespondentBankState {
    return { id: this._id.value, bankId: this._bankId, correspondentBankId: this._correspondentBankId,
      accountNumber: this._accountNumber, correspondentType: this._correspondentType,
      currencyCode: this._currencyCode, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
