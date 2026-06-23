import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CashBoxId } from "./cm-ids.js";
import { CashBoxType, CashBoxStatus } from "./cm-enums.js";
import { CashBoxBalanceChanged, CashBoxClosed } from "./cm-domain-events.js";

export interface CashBoxState {
  id: string;
  locationId: string;
  code: string;
  name: string;
  boxType: string;
  currencyCode: string;
  minBalance: number;
  maxBalance: number | null;
  currentBalance: number;
  allowNegative: boolean;
  status: string;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CashBox extends AggregateRoot<CashBoxId> {
  private _id: CashBoxId;
  private _locationId: string;
  private _code: string;
  private _name: string;
  private _boxType: CashBoxType;
  private _currencyCode: string;
  private _minBalance: number;
  private _maxBalance: number | null;
  private _currentBalance: number;
  private _allowNegative: boolean;
  private _status: CashBoxStatus;
  private _description: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: CashBoxId,
    locationId: string,
    code: string,
    name: string,
    boxType: CashBoxType,
    currencyCode: string,
    minBalance: number = 0,
    maxBalance: number | null = null,
    allowNegative: boolean = false,
  ) {
    super();
    this._id = id;
    this._locationId = locationId;
    this._code = code;
    this._name = name;
    this._boxType = boxType;
    this._currencyCode = currencyCode;
    this._minBalance = minBalance;
    this._maxBalance = maxBalance;
    this._currentBalance = 0;
    this._allowNegative = allowNegative;
    this._status = CashBoxStatus.Active;
    this._description = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    locationId: string;
    code: string;
    name: string;
    boxType: CashBoxType;
    currencyCode?: string;
    minBalance?: number;
    maxBalance?: number | null;
    allowNegative?: boolean;
    description?: string | null;
  }): CashBox {
    const box = new CashBox(
      CashBoxId.new(),
      params.locationId,
      params.code,
      params.name,
      params.boxType,
      params.currencyCode ?? "VND",
      params.minBalance ?? 0,
      params.maxBalance ?? null,
      params.allowNegative ?? false,
    );
    box._description = params.description ?? null;
    return box;
  }

  static load(state: CashBoxState): CashBox {
    const b = new CashBox(
      new CashBoxId(state.id),
      state.locationId,
      state.code,
      state.name,
      state.boxType as CashBoxType,
      state.currencyCode,
      state.minBalance,
      state.maxBalance,
      state.allowNegative,
    );
    b._currentBalance = state.currentBalance;
    b._status = state.status as CashBoxStatus;
    b._description = state.description;
    b._version = state.version;
    b._createdAt = state.createdAt;
    b._updatedAt = state.updatedAt;
    b._deletedAt = state.deletedAt;
    return b;
  }

  get id(): CashBoxId { return this._id; }
  get locationId(): string { return this._locationId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get boxType(): CashBoxType { return this._boxType; }
  get currencyCode(): string { return this._currencyCode; }
  get minBalance(): number { return this._minBalance; }
  get maxBalance(): number | null { return this._maxBalance; }
  get currentBalance(): number { return this._currentBalance; }
  get allowNegative(): boolean { return this._allowNegative; }
  get status(): CashBoxStatus { return this._status; }
  get description(): string | null { return this._description; }
  get version(): number { return this._version; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get deletedAt(): Date | null { return this._deletedAt; }

  canAcceptTransaction(): void {
    if (this._status !== CashBoxStatus.Active) {
      throw new DomainError("BusinessRule", `CashBox ${this._code} is ${this._status}, not active`);
    }
  }

  deposit(amount: number, reference: string): void {
    this.canAcceptTransaction();
    if (amount <= 0) throw new DomainError("BusinessRule", "Deposit amount must be positive");
    const newBalance = this._currentBalance + amount;
    if (this._maxBalance !== null && newBalance > this._maxBalance) {
      throw new DomainError("BusinessRule", `Deposit would exceed max balance ${this._maxBalance}`);
    }
    this._currentBalance = newBalance;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashBoxBalanceChanged(this._id.value, new Date(), {
      amount, reference, newBalance, direction: "in",
    }));
  }

  withdraw(amount: number, reference: string): void {
    this.canAcceptTransaction();
    if (amount <= 0) throw new DomainError("BusinessRule", "Withdrawal amount must be positive");
    const newBalance = this._currentBalance - amount;
    if (!this._allowNegative) {
      if (newBalance < 0) {
        throw new DomainError("BusinessRule", `Insufficient balance. Available: ${this._currentBalance}, requested: ${amount}`);
      }
      if (newBalance < this._minBalance) {
        throw new DomainError("BusinessRule", `Withdrawal would bring balance below minimum ${this._minBalance}`);
      }
    }
    this._currentBalance = newBalance;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashBoxBalanceChanged(this._id.value, new Date(), {
      amount, reference, newBalance, direction: "out",
    }));
  }

  close(): void {
    if (this._currentBalance !== 0) {
      throw new DomainError("BusinessRule", `Cannot close CashBox with non-zero balance: ${this._currentBalance}`);
    }
    this._status = CashBoxStatus.Closed;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new CashBoxClosed(this._id.value, new Date(), {}));
  }

  toState(): CashBoxState {
    return {
      id: this._id.value,
      locationId: this._locationId,
      code: this._code,
      name: this._name,
      boxType: this._boxType,
      currencyCode: this._currencyCode,
      minBalance: this._minBalance,
      maxBalance: this._maxBalance,
      currentBalance: this._currentBalance,
      allowNegative: this._allowNegative,
      status: this._status,
      description: this._description,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
