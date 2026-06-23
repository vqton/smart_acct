import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankId, BankBranchId, BankAccountId } from "./cm-ids.js";
import { BankAccountType, BankAccountStatus } from "./cm-enums.js";

export interface BankState {
  id: string;
  companyId: string;
  code: string;
  name: string;
  nameEn: string | null;
  swiftCode: string | null;
  routingNumber: string | null;
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class Bank extends AggregateRoot<BankId> {
  private _id: BankId;
  private _companyId: string;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _swiftCode: string | null;
  private _routingNumber: string | null;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: BankId,
    companyId: string,
    code: string,
    name: string,
    swiftCode: string | null = null,
  ) {
    super();
    this._id = id;
    this._companyId = companyId;
    this._code = code;
    this._name = name;
    this._nameEn = null;
    this._swiftCode = swiftCode;
    this._routingNumber = null;
    this._isActive = true;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    companyId: string;
    code: string;
    name: string;
    nameEn?: string | null;
    swiftCode?: string | null;
    routingNumber?: string | null;
  }): Bank {
    const b = new Bank(BankId.new(), params.companyId, params.code, params.name, params.swiftCode ?? null);
    b._nameEn = params.nameEn ?? null;
    b._routingNumber = params.routingNumber ?? null;
    return b;
  }

  static load(state: BankState): Bank {
    const b = new Bank(new BankId(state.id), state.companyId, state.code, state.name, state.swiftCode);
    b._nameEn = state.nameEn;
    b._routingNumber = state.routingNumber;
    b._isActive = state.isActive;
    b._version = state.version;
    b._createdAt = state.createdAt;
    b._updatedAt = state.updatedAt;
    b._deletedAt = state.deletedAt;
    return b;
  }

  get id(): BankId { return this._id; }
  get companyId(): string { return this._companyId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get swiftCode(): string | null { return this._swiftCode; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): BankState {
    return {
      id: this._id.value,
      companyId: this._companyId,
      code: this._code,
      name: this._name,
      nameEn: this._nameEn,
      swiftCode: this._swiftCode,
      routingNumber: this._routingNumber,
      isActive: this._isActive,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export interface BankBranchState {
  id: string;
  bankId: string;
  code: string;
  name: string;
  address: string | null;
  phone: string | null;
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class BankBranch {
  private _id: BankBranchId;
  private _bankId: string;
  private _code: string;
  private _name: string;
  private _address: string | null;
  private _phone: string | null;
  private _isActive: boolean;

  constructor(
    id: BankBranchId,
    bankId: string,
    code: string,
    name: string,
  ) {
    this._id = id;
    this._bankId = bankId;
    this._code = code;
    this._name = name;
    this._address = null;
    this._phone = null;
    this._isActive = true;
  }

  get id(): BankBranchId { return this._id; }
  get bankId(): string { return this._bankId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get address(): string | null { return this._address; }
  get isActive(): boolean { return this._isActive; }

  toState(): BankBranchState {
    return {
      id: this._id.value,
      bankId: this._bankId,
      code: this._code,
      name: this._name,
      address: this._address,
      phone: this._phone,
      isActive: this._isActive,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
      deletedAt: null,
    };
  }
}

export interface BankAccountState {
  id: string;
  companyId: string;
  bankId: string;
  branchId: string | null;
  accountNumber: string;
  accountName: string;
  accountType: string;
  currencyCode: string;
  status: string;
  currentBalance: number;
  availableBalance: number;
  blockedBalance: number;
  glAccountId: string | null;
  isVirtual: boolean;
  parentAccountId: string | null;
  openingDate: Date;
  closingDate: Date | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class BankAccount extends AggregateRoot<BankAccountId> {
  private _id: BankAccountId;
  private _companyId: string;
  private _bankId: string;
  private _branchId: string | null;
  private _accountNumber: string;
  private _accountName: string;
  private _accountType: BankAccountType;
  private _currencyCode: string;
  private _status: BankAccountStatus;
  private _currentBalance: number;
  private _availableBalance: number;
  private _blockedBalance: number;
  private _glAccountId: string | null;
  private _isVirtual: boolean;
  private _parentAccountId: string | null;
  private _openingDate: Date;
  private _closingDate: Date | null;
  private _notes: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: BankAccountId,
    companyId: string,
    bankId: string,
    accountNumber: string,
    accountName: string,
    accountType: BankAccountType,
    currencyCode: string,
    openingDate: Date,
    branchId: string | null = null,
  ) {
    super();
    this._id = id;
    this._companyId = companyId;
    this._bankId = bankId;
    this._branchId = branchId;
    this._accountNumber = accountNumber;
    this._accountName = accountName;
    this._accountType = accountType;
    this._currencyCode = currencyCode;
    this._status = BankAccountStatus.Active;
    this._currentBalance = 0;
    this._availableBalance = 0;
    this._blockedBalance = 0;
    this._glAccountId = null;
    this._isVirtual = false;
    this._parentAccountId = null;
    this._openingDate = openingDate;
    this._closingDate = null;
    this._notes = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    companyId: string;
    bankId: string;
    accountNumber: string;
    accountName: string;
    accountType?: BankAccountType;
    currencyCode?: string;
    openingDate: Date;
    branchId?: string | null;
    glAccountId?: string | null;
    notes?: string | null;
  }): BankAccount {
    const a = new BankAccount(
      BankAccountId.new(),
      params.companyId,
      params.bankId,
      params.accountNumber,
      params.accountName,
      params.accountType ?? BankAccountType.Current,
      params.currencyCode ?? "VND",
      params.openingDate,
      params.branchId ?? null,
    );
    a._glAccountId = params.glAccountId ?? null;
    a._notes = params.notes ?? null;
    return a;
  }

  static load(state: BankAccountState): BankAccount {
    const a = new BankAccount(
      new BankAccountId(state.id),
      state.companyId,
      state.bankId,
      state.accountNumber,
      state.accountName,
      state.accountType as BankAccountType,
      state.currencyCode,
      state.openingDate,
      state.branchId,
    );
    a._status = state.status as BankAccountStatus;
    a._currentBalance = state.currentBalance;
    a._availableBalance = state.availableBalance;
    a._blockedBalance = state.blockedBalance;
    a._glAccountId = state.glAccountId;
    a._isVirtual = state.isVirtual;
    a._parentAccountId = state.parentAccountId;
    a._closingDate = state.closingDate;
    a._notes = state.notes;
    a._version = state.version;
    a._createdAt = state.createdAt;
    a._updatedAt = state.updatedAt;
    a._deletedAt = state.deletedAt;
    return a;
  }

  get id(): BankAccountId { return this._id; }
  get companyId(): string { return this._companyId; }
  get bankId(): string { return this._bankId; }
  get branchId(): string | null { return this._branchId; }
  get accountNumber(): string { return this._accountNumber; }
  get accountName(): string { return this._accountName; }
  get accountType(): BankAccountType { return this._accountType; }
  get currencyCode(): string { return this._currencyCode; }
  get status(): BankAccountStatus { return this._status; }
  get currentBalance(): number { return this._currentBalance; }
  get availableBalance(): number { return this._availableBalance; }
  get blockedBalance(): number { return this._blockedBalance; }
  get glAccountId(): string | null { return this._glAccountId; }
  get isVirtual(): boolean { return this._isVirtual; }
  get version(): number { return this._version; }

  credit(amount: number, reference: string): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Credit amount must be positive");
    this._currentBalance += amount;
    this._availableBalance += amount;
    this._updatedAt = new Date();
    this._version++;
  }

  debit(amount: number, reference: string): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Debit amount must be positive");
    if (amount > this._availableBalance) {
      throw new DomainError("BusinessRule", `Insufficient available balance. Available: ${this._availableBalance}`);
    }
    this._currentBalance -= amount;
    this._availableBalance -= amount;
    this._updatedAt = new Date();
    this._version++;
  }

  block(amount: number): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Block amount must be positive");
    if (amount > this._availableBalance) {
      throw new DomainError("BusinessRule", "Insufficient balance to block");
    }
    this._blockedBalance += amount;
    this._availableBalance -= amount;
    this._updatedAt = new Date();
    this._version++;
  }

  unblock(amount: number): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Unblock amount must be positive");
    if (amount > this._blockedBalance) {
      throw new DomainError("BusinessRule", "Unblock amount exceeds blocked balance");
    }
    this._blockedBalance -= amount;
    this._availableBalance += amount;
    this._updatedAt = new Date();
    this._version++;
  }

  close(): void {
    if (this._currentBalance !== 0) {
      throw new DomainError("BusinessRule", "Cannot close account with non-zero balance");
    }
    this._status = BankAccountStatus.Closed;
    this._closingDate = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): BankAccountState {
    return {
      id: this._id.value,
      companyId: this._companyId,
      bankId: this._bankId,
      branchId: this._branchId,
      accountNumber: this._accountNumber,
      accountName: this._accountName,
      accountType: this._accountType,
      currencyCode: this._currencyCode,
      status: this._status,
      currentBalance: this._currentBalance,
      availableBalance: this._availableBalance,
      blockedBalance: this._blockedBalance,
      glAccountId: this._glAccountId,
      isVirtual: this._isVirtual,
      parentAccountId: this._parentAccountId,
      openingDate: this._openingDate,
      closingDate: this._closingDate,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
