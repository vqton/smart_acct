import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankAccountId, AuthorizedSignerId, AccountLimitId } from "./bank-ids.js";
import { BankAccountCategory, BankAccountStatus, SignatureRule, AccountLimitType } from "./bank-enums.js";
import { AccountNumber, CurrencyAmount } from "./bank-value-objects.js";
import {
  BankAccountOpened, BankAccountClosed, BankAccountSuspended,
  BankAccountActivated, BankAccountBalanceChanged,
} from "./bank-events.js";

// ─── Authorized Signer ─────────────────────────────────────────────────────────

export interface AuthorizedSignerState {
  id: string; bankAccountId: string; userId: string; name: string;
  title: string | null; signatureRule: string; signingLimit: number;
  currencyCode: string; isActive: boolean; startDate: Date; endDate: Date | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class AuthorizedSigner extends AggregateRoot<AuthorizedSignerId> {
  private _id: AuthorizedSignerId; private _bankAccountId: string;
  private _userId: string; private _name: string; private _title: string | null;
  private _signatureRule: SignatureRule; private _signingLimit: number;
  private _currencyCode: string; private _isActive: boolean;
  private _startDate: Date; private _endDate: Date | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;

  private constructor(id: AuthorizedSignerId, bankAccountId: string, userId: string, name: string) {
    super(); this._id = id; this._bankAccountId = bankAccountId; this._userId = userId; this._name = name;
    this._title = null; this._signatureRule = SignatureRule.Single; this._signingLimit = 0;
    this._currencyCode = "VND"; this._isActive = true;
    this._startDate = new Date(); this._endDate = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { bankAccountId: string; userId: string; name: string; title?: string;
    signatureRule?: SignatureRule; signingLimit?: number; currencyCode?: string;
    startDate?: Date; endDate?: Date | null }): AuthorizedSigner {
    const s = new AuthorizedSigner(AuthorizedSignerId.new(), p.bankAccountId, p.userId, p.name);
    s._title = p.title ?? null; s._signatureRule = p.signatureRule ?? SignatureRule.Single;
    s._signingLimit = p.signingLimit ?? 0; s._currencyCode = p.currencyCode ?? "VND";
    s._startDate = p.startDate ?? new Date(); s._endDate = p.endDate ?? null;
    return s;
  }

  static load(s: AuthorizedSignerState): AuthorizedSigner {
    const a = new AuthorizedSigner(new AuthorizedSignerId(s.id), s.bankAccountId, s.userId, s.name);
    a._title = s.title; a._signatureRule = s.signatureRule as SignatureRule;
    a._signingLimit = s.signingLimit; a._currencyCode = s.currencyCode;
    a._isActive = s.isActive; a._startDate = s.startDate; a._endDate = s.endDate;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt;
    return a;
  }

  get id(): AuthorizedSignerId { return this._id; }
  get signingLimit(): number { return this._signingLimit; }
  get signatureRule(): SignatureRule { return this._signatureRule; }
  get isActive(): boolean { return this._isActive; }

  canSign(amount: number): boolean {
    if (!this._isActive) return false;
    if (this._endDate && this._endDate < new Date()) return false;
    if (this._signingLimit > 0 && amount > this._signingLimit) return false;
    return true;
  }

  deactivate(): void { this._isActive = false; this._updatedAt = new Date(); this._version++; }

  toState(): AuthorizedSignerState {
    return { id: this._id.value, bankAccountId: this._bankAccountId, userId: this._userId,
      name: this._name, title: this._title, signatureRule: this._signatureRule,
      signingLimit: this._signingLimit, currencyCode: this._currencyCode, isActive: this._isActive,
      startDate: this._startDate, endDate: this._endDate, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Account Limit ──────────────────────────────────────────────────────────────

export interface AccountLimitState {
  id: string; bankAccountId: string; limitType: string; maxAmount: number;
  minAmount: number; currencyCode: string; isEnforced: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class AccountLimit extends AggregateRoot<AccountLimitId> {
  private _id: AccountLimitId; private _bankAccountId: string;
  private _limitType: AccountLimitType; private _maxAmount: number;
  private _minAmount: number; private _currencyCode: string;
  private _isEnforced: boolean; private _version: number;
  private _createdAt: Date; private _updatedAt: Date;

  private constructor(id: AccountLimitId, bankAccountId: string, limitType: AccountLimitType) {
    super(); this._id = id; this._bankAccountId = bankAccountId; this._limitType = limitType;
    this._maxAmount = 0; this._minAmount = 0; this._currencyCode = "VND";
    this._isEnforced = true; this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { bankAccountId: string; limitType: AccountLimitType; maxAmount?: number;
    minAmount?: number; currencyCode?: string; isEnforced?: boolean }): AccountLimit {
    const l = new AccountLimit(AccountLimitId.new(), p.bankAccountId, p.limitType);
    l._maxAmount = p.maxAmount ?? 0; l._minAmount = p.minAmount ?? 0;
    l._currencyCode = p.currencyCode ?? "VND"; l._isEnforced = p.isEnforced ?? true;
    return l;
  }

  static load(s: AccountLimitState): AccountLimit {
    const l = new AccountLimit(new AccountLimitId(s.id), s.bankAccountId, s.limitType as AccountLimitType);
    l._maxAmount = s.maxAmount; l._minAmount = s.minAmount; l._currencyCode = s.currencyCode;
    l._isEnforced = s.isEnforced; l._version = s.version; l._createdAt = s.createdAt; l._updatedAt = s.updatedAt;
    return l;
  }

  get id(): AccountLimitId { return this._id; }
  get limitType(): AccountLimitType { return this._limitType; }
  get maxAmount(): number { return this._maxAmount; }
  get minAmount(): number { return this._minAmount; }

  exceedsLimit(amount: number): boolean {
    if (!this._isEnforced) return false;
    if (this._maxAmount > 0 && amount > this._maxAmount) return true;
    if (this._minAmount > 0 && amount < this._minAmount) return true;
    return false;
  }

  toState(): AccountLimitState {
    return { id: this._id.value, bankAccountId: this._bankAccountId, limitType: this._limitType,
      maxAmount: this._maxAmount, minAmount: this._minAmount, currencyCode: this._currencyCode,
      isEnforced: this._isEnforced, version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Account Mapping ───────────────────────────────────────────────────────────

export interface AccountMappingState {
  id: string; bankAccountId: string; mappingType: string;
  glAccountId: string | null; branchId: string | null; costCenterId: string | null;
  departmentId: string | null; projectId: string | null; isDefault: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class AccountMapping {
  constructor(
    private _id: string, private _bankAccountId: string, private _mappingType: string,
    private _glAccountId: string | null, private _branchId: string | null,
    private _costCenterId: string | null, private _departmentId: string | null,
    private _projectId: string | null, private _isDefault: boolean,
  ) {}

  static create(p: { bankAccountId: string; mappingType: string; glAccountId?: string;
    branchId?: string; costCenterId?: string; departmentId?: string; projectId?: string; isDefault?: boolean }): AccountMapping {
    return new AccountMapping(crypto.randomUUID(), p.bankAccountId, p.mappingType,
      p.glAccountId ?? null, p.branchId ?? null, p.costCenterId ?? null,
      p.departmentId ?? null, p.projectId ?? null, p.isDefault ?? false);
  }

  get id(): string { return this._id; }
  get glAccountId(): string | null { return this._glAccountId; }
  get branchId(): string | null { return this._branchId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get isDefault(): boolean { return this._isDefault; }

  toState(): AccountMappingState {
    return { id: this._id, bankAccountId: this._bankAccountId, mappingType: this._mappingType,
      glAccountId: this._glAccountId, branchId: this._branchId, costCenterId: this._costCenterId,
      departmentId: this._departmentId, projectId: this._projectId, isDefault: this._isDefault,
      version: 1, createdAt: new Date(), updatedAt: new Date() };
  }
}

// ─── Bank Account Aggregate Root ──────────────────────────────────────────────

export interface BankAccountState {
  id: string; companyId: string; bankId: string; branchId: string | null;
  accountNumber: string; accountName: string; accountNameEn: string | null;
  accountCategory: string; currencyCode: string; countryCode: string;
  iban: string | null; swiftCode: string | null; routingNumber: string | null;
  status: string; currentBalance: number; availableBalance: number;
  blockedBalance: number; creditLimit: number; minimumBalance: number;
  maximumBalance: number; overdraftLimit: number; interestRate: number;
  glAccountId: string | null; glBankChargeAccountId: string | null;
  glInterestAccountId: string | null; glFXAccountId: string | null;
  isVirtual: boolean; parentAccountId: string | null;
  classification: string | null; openingDate: Date; closingDate: Date | null;
  lastActivityDate: Date | null; lastReconciliationDate: Date | null;
  notes: string | null; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankAccount extends AggregateRoot<BankAccountId> {
  private _id: BankAccountId;
  private _companyId: string; private _bankId: string; private _branchId: string | null;
  private _accountNumber: AccountNumber; private _accountName: string; private _accountNameEn: string | null;
  private _accountCategory: BankAccountCategory; private _currencyCode: string;
  private _countryCode: string; private _iban: string | null; private _swiftCode: string | null;
  private _routingNumber: string | null; private _status: BankAccountStatus;
  private _currentBalance: number; private _availableBalance: number; private _blockedBalance: number;
  private _creditLimit: number; private _minimumBalance: number; private _maximumBalance: number;
  private _overdraftLimit: number; private _interestRate: number;
  private _glAccountId: string | null; private _glBankChargeAccountId: string | null;
  private _glInterestAccountId: string | null; private _glFXAccountId: string | null;
  private _isVirtual: boolean; private _parentAccountId: string | null;
  private _classification: string | null;
  private _openingDate: Date; private _closingDate: Date | null;
  private _lastActivityDate: Date | null; private _lastReconciliationDate: Date | null;
  private _notes: string | null;
  private _signers: AuthorizedSigner[] = [];
  private _limits: AccountLimit[] = [];
  private _mappings: AccountMapping[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: BankAccountId, companyId: string, bankId: string,
    accountNumber: AccountNumber, accountName: string, category: BankAccountCategory,
    currencyCode: string) {
    super(); this._id = id; this._companyId = companyId; this._bankId = bankId;
    this._accountNumber = accountNumber; this._accountName = accountName;
    this._accountNameEn = null; this._branchId = null;
    this._accountCategory = category; this._currencyCode = currencyCode;
    this._countryCode = "VN"; this._iban = null; this._swiftCode = null; this._routingNumber = null;
    this._status = BankAccountStatus.Pending; this._currentBalance = 0;
    this._availableBalance = 0; this._blockedBalance = 0; this._creditLimit = 0;
    this._minimumBalance = 0; this._maximumBalance = 0; this._overdraftLimit = 0;
    this._interestRate = 0; this._glAccountId = null;
    this._glBankChargeAccountId = null; this._glInterestAccountId = null; this._glFXAccountId = null;
    this._isVirtual = false; this._parentAccountId = null; this._classification = null;
    this._openingDate = new Date(); this._closingDate = null;
    this._lastActivityDate = null; this._lastReconciliationDate = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    companyId: string; bankId: string; accountNumber: string; accountName: string;
    accountCategory?: BankAccountCategory; currencyCode?: string; branchId?: string | null;
    countryCode?: string; iban?: string | null; swiftCode?: string | null;
    routingNumber?: string | null; glAccountId?: string | null;
    glBankChargeAccountId?: string | null; glInterestAccountId?: string | null;
    glFXAccountId?: string | null; openingDate?: Date; notes?: string | null;
    classification?: string | null; isVirtual?: boolean; parentAccountId?: string | null;
  }): BankAccount {
    const a = new BankAccount(BankAccountId.new(), p.companyId, p.bankId,
      AccountNumber.create(p.accountNumber), p.accountName,
      p.accountCategory ?? BankAccountCategory.Current, p.currencyCode ?? "VND");
    a._branchId = p.branchId ?? null; a._countryCode = p.countryCode ?? "VN";
    a._iban = p.iban ?? null; a._swiftCode = p.swiftCode ?? null;
    a._routingNumber = p.routingNumber ?? null; a._glAccountId = p.glAccountId ?? null;
    a._glBankChargeAccountId = p.glBankChargeAccountId ?? null;
    a._glInterestAccountId = p.glInterestAccountId ?? null;
    a._glFXAccountId = p.glFXAccountId ?? null;
    a._openingDate = p.openingDate ?? new Date(); a._notes = p.notes ?? null;
    a._classification = p.classification ?? null; a._isVirtual = p.isVirtual ?? false;
    a._parentAccountId = p.parentAccountId ?? null;
    a._status = BankAccountStatus.Active;
    a.addEvent(new BankAccountOpened(a._id.value, new Date(), {
      accountNumber: a._accountNumber.value, bankId: a._bankId, companyId: a._companyId,
    }));
    return a;
  }

  static load(s: BankAccountState): BankAccount {
    const a = new BankAccount(new BankAccountId(s.id), s.companyId, s.bankId,
      AccountNumber.fromExisting(s.accountNumber), s.accountName,
      s.accountCategory as BankAccountCategory, s.currencyCode);
    a._accountNameEn = s.accountNameEn; a._branchId = s.branchId;
    a._countryCode = s.countryCode; a._iban = s.iban; a._swiftCode = s.swiftCode;
    a._routingNumber = s.routingNumber; a._status = s.status as BankAccountStatus;
    a._currentBalance = s.currentBalance; a._availableBalance = s.availableBalance;
    a._blockedBalance = s.blockedBalance; a._creditLimit = s.creditLimit;
    a._minimumBalance = s.minimumBalance; a._maximumBalance = s.maximumBalance;
    a._overdraftLimit = s.overdraftLimit; a._interestRate = s.interestRate;
    a._glAccountId = s.glAccountId; a._glBankChargeAccountId = s.glBankChargeAccountId;
    a._glInterestAccountId = s.glInterestAccountId; a._glFXAccountId = s.glFXAccountId;
    a._isVirtual = s.isVirtual; a._parentAccountId = s.parentAccountId;
    a._classification = s.classification; a._openingDate = s.openingDate;
    a._closingDate = s.closingDate; a._lastActivityDate = s.lastActivityDate;
    a._lastReconciliationDate = s.lastReconciliationDate; a._notes = s.notes;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt; a._deletedAt = s.deletedAt;
    return a;
  }

  get id(): BankAccountId { return this._id; }
  get companyId(): string { return this._companyId; }
  get bankId(): string { return this._bankId; }
  get branchId(): string | null { return this._branchId; }
  get accountNumber(): AccountNumber { return this._accountNumber; }
  get accountName(): string { return this._accountName; }
  get accountCategory(): BankAccountCategory { return this._accountCategory; }
  get currencyCode(): string { return this._currencyCode; }
  get status(): BankAccountStatus { return this._status; }
  get currentBalance(): number { return this._currentBalance; }
  get availableBalance(): number { return this._availableBalance; }
  get blockedBalance(): number { return this._blockedBalance; }
  get overdraftLimit(): number { return this._overdraftLimit; }
  get glAccountId(): string | null { return this._glAccountId; }
  get isVirtual(): boolean { return this._isVirtual; }
  get version(): number { return this._version; }
  get signers(): readonly AuthorizedSigner[] { return this._signers; }
  get limits(): readonly AccountLimit[] { return this._limits; }
  get mappings(): readonly AccountMapping[] { return this._mappings; }

  activate(): void {
    if (this._status !== BankAccountStatus.Pending && this._status !== BankAccountStatus.Suspended) {
      throw new DomainError("BusinessRule", `Cannot activate account in status ${this._status}`);
    }
    this._status = BankAccountStatus.Active; this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankAccountActivated(this._id.value, new Date(), { accountNumber: this._accountNumber.value }));
  }

  suspend(reason: string): void {
    if (this._status !== BankAccountStatus.Active) throw new DomainError("BusinessRule", "Only active accounts can be suspended");
    this._status = BankAccountStatus.Suspended; this._notes = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankAccountSuspended(this._id.value, new Date(), { reason }));
  }

  block(reason: string): void {
    if (this._status === BankAccountStatus.Closed) throw new DomainError("BusinessRule", "Cannot block closed account");
    this._status = BankAccountStatus.Blocked; this._notes = reason;
    this._updatedAt = new Date(); this._version++;
  }

  close(force: boolean = false): void {
    if (!force && this._currentBalance !== 0) {
      throw new DomainError("BusinessRule",
        `Cannot close account with non-zero balance: ${this._currentBalance}`);
    }
    this._status = BankAccountStatus.Closed; this._closingDate = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankAccountClosed(this._id.value, new Date(), { accountNumber: this._accountNumber.value }));
  }

  canTransact(): boolean {
    return this._status === BankAccountStatus.Active;
  }

  credit(amount: number, reference: string): void {
    this.requireActive();
    if (amount <= 0) throw new DomainError("BusinessRule", "Credit amount must be positive");
    this._currentBalance += amount; this._availableBalance += amount;
    this._lastActivityDate = new Date(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankAccountBalanceChanged(this._id.value, new Date(), {
      change: amount, type: "credit", reference, newBalance: this._currentBalance,
    }));
  }

  debit(amount: number, reference: string): void {
    this.requireActive();
    if (amount <= 0) throw new DomainError("BusinessRule", "Debit amount must be positive");
    const effectiveAvailable = this._availableBalance + this._overdraftLimit;
    if (amount > effectiveAvailable) {
      throw new DomainError("BusinessRule",
        `Insufficient available balance. Available: ${this._availableBalance}, Overdraft: ${this._overdraftLimit}`);
    }
    this._currentBalance -= amount; this._availableBalance -= amount;
    this._lastActivityDate = new Date(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new BankAccountBalanceChanged(this._id.value, new Date(), {
      change: amount, type: "debit", reference, newBalance: this._currentBalance,
    }));
  }

  blockBalance(amount: number, reference: string): void {
    this.requireActive();
    if (amount <= 0) throw new DomainError("BusinessRule", "Block amount must be positive");
    if (amount > this._availableBalance) {
      throw new DomainError("BusinessRule", "Insufficient available balance to block");
    }
    this._blockedBalance += amount; this._availableBalance -= amount;
    this._updatedAt = new Date(); this._version++;
  }

  unblockBalance(amount: number, reference: string): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Unblock amount must be positive");
    if (amount > this._blockedBalance) {
      throw new DomainError("BusinessRule", "Unblock amount exceeds blocked balance");
    }
    this._blockedBalance -= amount; this._availableBalance += amount;
    this._updatedAt = new Date(); this._version++;
  }

  addSigner(signer: AuthorizedSigner): void {
    this._signers.push(signer); this._updatedAt = new Date(); this._version++;
  }

  addLimit(limit: AccountLimit): void {
    this._limits.push(limit); this._updatedAt = new Date(); this._version++;
  }

  addMapping(mapping: AccountMapping): void {
    this._mappings.push(mapping); this._updatedAt = new Date(); this._version++;
  }

  private requireActive(): void {
    if (!this.canTransact()) {
      throw new DomainError("BusinessRule",
        `Account ${this._accountNumber.value} is ${this._status}. Cannot transact.`);
    }
  }

  toState(): BankAccountState {
    return {
      id: this._id.value, companyId: this._companyId, bankId: this._bankId,
      branchId: this._branchId, accountNumber: this._accountNumber.value,
      accountName: this._accountName, accountNameEn: this._accountNameEn,
      accountCategory: this._accountCategory, currencyCode: this._currencyCode,
      countryCode: this._countryCode, iban: this._iban, swiftCode: this._swiftCode,
      routingNumber: this._routingNumber, status: this._status,
      currentBalance: this._currentBalance, availableBalance: this._availableBalance,
      blockedBalance: this._blockedBalance, creditLimit: this._creditLimit,
      minimumBalance: this._minimumBalance, maximumBalance: this._maximumBalance,
      overdraftLimit: this._overdraftLimit, interestRate: this._interestRate,
      glAccountId: this._glAccountId, glBankChargeAccountId: this._glBankChargeAccountId,
      glInterestAccountId: this._glInterestAccountId, glFXAccountId: this._glFXAccountId,
      isVirtual: this._isVirtual, parentAccountId: this._parentAccountId,
      classification: this._classification, openingDate: this._openingDate,
      closingDate: this._closingDate, lastActivityDate: this._lastActivityDate,
      lastReconciliationDate: this._lastReconciliationDate, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
