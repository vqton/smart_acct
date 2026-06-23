import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { AccountId } from "./account-id.js";
import { AccountCategory, AccountNature } from "./account-category.js";

export interface AccountState {
  id: string;
  code: string;
  name: string;
  nameEn: string | null;
  category: AccountCategory;
  nature: AccountNature;
  parentId: string | null;
  isActive: boolean;
  isControl: boolean;
  isPosting: boolean;
  allowManualEntry: boolean;
  balance: number;
  foreignBalance: number;
  currencyCode: string | null;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export class AccountCreated implements DomainEvent {
  readonly eventName = "AccountCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AccountModified implements DomainEvent {
  readonly eventName = "AccountModified";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AccountDeactivated implements DomainEvent {
  readonly eventName = "AccountDeactivated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class Account extends AggregateRoot<AccountId> {
  private _id: AccountId;
  private _code: string;
  private _name: string;
  private _nameEn: string | null;
  private _category: AccountCategory;
  private _nature: AccountNature;
  private _parentId: string | null;
  private _isActive: boolean;
  private _isControl: boolean;
  private _isPosting: boolean;
  private _allowManualEntry: boolean;
  private _balance: number;
  private _foreignBalance: number;
  private _currencyCode: string | null;
  private _description: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;
  private _deletedAt: Date | null;

  constructor(
    id: AccountId,
    code: string,
    name: string,
    category: AccountCategory,
    nature: AccountNature,
    parentId: string | null = null,
    currencyCode: string | null = null,
    description: string | null = null,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._category = category;
    this._nature = nature;
    this._parentId = parentId;
    this._currencyCode = currencyCode;
    this._description = description;
    this._isActive = true;
    this._isControl = false;
    this._isPosting = true;
    this._allowManualEntry = true;
    this._balance = 0;
    this._foreignBalance = 0;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
    this._deletedAt = null;
    this._nameEn = null;
  }

  static create(params: {
    code: string;
    name: string;
    category: AccountCategory;
    nature: AccountNature;
    parentId?: string | null | undefined;
    currencyCode?: string | null;
    description?: string | null;
    isControl?: boolean;
    isPosting?: boolean;
  }): Account {
    Account.validateCode(params.code);
    Account.validateParentCategory(params.category, params.parentId);

    const account = new Account(
      AccountId.new(),
      params.code,
      params.name,
      params.category,
      params.nature,
      params.parentId ?? null,
      params.currencyCode ?? null,
      params.description ?? null,
    );

    if (params.isControl === true) {
      account._isControl = true;
      account._isPosting = false;
    }
    if (params.isPosting === false) {
      account._isPosting = false;
    }

    account.addEvent(new AccountCreated(account._id.value, new Date(), {
      code: params.code,
      name: params.name,
      category: params.category,
    }));

    return account;
  }

  static load(state: AccountState): Account {
    const a = new Account(
      new AccountId(state.id),
      state.code,
      state.name,
      state.category,
      state.nature,
      state.parentId,
      state.currencyCode,
      state.description,
    );
    a._nameEn = state.nameEn;
    a._isActive = state.isActive;
    a._isControl = state.isControl;
    a._isPosting = state.isPosting;
    a._allowManualEntry = state.allowManualEntry;
    a._balance = state.balance;
    a._foreignBalance = state.foreignBalance;
    a._createdAt = state.createdAt;
    a._updatedAt = state.updatedAt;
    a._version = state.version;
    a._deletedAt = state.deletedAt;
    return a;
  }

  get id(): AccountId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get nameEn(): string | null { return this._nameEn; }
  get category(): AccountCategory { return this._category; }
  get nature(): AccountNature { return this._nature; }
  get parentId(): string | null { return this._parentId; }
  get isActive(): boolean { return this._isActive; }
  get isControl(): boolean { return this._isControl; }
  get isPosting(): boolean { return this._isPosting; }
  get allowManualEntry(): boolean { return this._allowManualEntry; }
  get balance(): number { return this._balance; }
  get foreignBalance(): number { return this._foreignBalance; }
  get currencyCode(): string | null { return this._currencyCode; }
  get description(): string | null { return this._description; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  modify(params: { name?: string; nameEn?: string; description?: string; isActive?: boolean }): void {
    if (params.name !== undefined) this._name = params.name;
    if (params.nameEn !== undefined) this._nameEn = params.nameEn;
    if (params.description !== undefined) this._description = params.description;
    if (params.isActive !== undefined) this._isActive = params.isActive;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new AccountModified(this._id.value, new Date(), params as Record<string, unknown>));
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new AccountDeactivated(this._id.value, new Date(), {}));
  }

  updateBalance(debitAmount: number, creditAmount: number): void {
    if (this._nature === AccountNature.Debit) {
      this._balance += debitAmount - creditAmount;
    } else {
      this._balance += creditAmount - debitAmount;
    }
  }

  updateForeignBalance(debitAmount: number, creditAmount: number): void {
    if (this._nature === AccountNature.Debit) {
      this._foreignBalance += debitAmount - creditAmount;
    } else {
      this._foreignBalance += creditAmount - debitAmount;
    }
  }

  canPost(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", `Account ${this._code} is inactive`);
    if (!this._isPosting) throw new DomainError("BusinessRule", `Account ${this._code} is not a posting account`);
    if (this._deletedAt) throw new DomainError("BusinessRule", `Account ${this._code} is deleted`);
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  private static validateCode(code: string): void {
    if (!/^\d{1,7}$/.test(code)) throw new DomainError("Validation", `Invalid account code: ${code}`);
  }

  private static validateParentCategory(category: AccountCategory, parentId: string | null | undefined): void {
    if (parentId) {
      const parentClass = Account.getClassCode(category);
      if (!parentClass) throw new DomainError("Validation", `Invalid category: ${category}`);
    }
  }

  static getClassCode(category: AccountCategory): string {
    const map: Record<AccountCategory, string> = {
      [AccountCategory.ShortTermAsset]: "1",
      [AccountCategory.LongTermAsset]: "1",
      [AccountCategory.ShortTermLiability]: "2",
      [AccountCategory.LongTermLiability]: "2",
      [AccountCategory.Equity]: "3",
      [AccountCategory.Revenue]: "4",
      [AccountCategory.OperatingExpense]: "5",
      [AccountCategory.CostOfGoodsSold]: "6",
      [AccountCategory.OtherIncome]: "7",
      [AccountCategory.OtherExpense]: "8",
      [AccountCategory.ManufacturingCost]: "9",
    };
    return map[category];
  }

  toState(): AccountState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      nameEn: this._nameEn,
      category: this._category,
      nature: this._nature,
      parentId: this._parentId,
      isActive: this._isActive,
      isControl: this._isControl,
      isPosting: this._isPosting,
      allowManualEntry: this._allowManualEntry,
      balance: this._balance,
      foreignBalance: this._foreignBalance,
      currencyCode: this._currencyCode,
      description: this._description,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}
