import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { TaxBracketId } from "./prl-ids.js";
import { TaxBracketCreated } from "./prl-events.js";

export interface TaxBracketState {
  id: string;
  name: string;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  bracketOrder: number;
  fromAmount: bigint;
  toAmount: bigint | null;
  rate: number;
  deductAmount: bigint;
  currencyCode: string;
  isActive: boolean;
  regulationRef: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class TaxBracket extends AggregateRoot<TaxBracketId> {
  private _id: TaxBracketId;
  private _name: string;
  private _effectiveFrom!: Date;
  private _effectiveTo: Date | null = null;
  private _bracketOrder: number;
  private _fromAmount: bigint;
  private _toAmount: bigint | null;
  private _rate: number;
  private _deductAmount: bigint;
  private _currencyCode: string;
  private _isActive: boolean;
  private _regulationRef: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: TaxBracketId, name: string, bracketOrder: number, fromAmount: bigint, rate: number, deductAmount: bigint) {
    super();
    this._id = id;
    this._name = name;
    this._bracketOrder = bracketOrder;
    this._fromAmount = fromAmount;
    this._rate = rate;
    this._deductAmount = deductAmount;
    this._toAmount = null;
    this._currencyCode = "VND";
    this._isActive = true;
    this._regulationRef = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    name: string; effectiveFrom: Date; bracketOrder: number;
    fromAmount: bigint; toAmount?: bigint; rate: number;
    deductAmount: bigint; currencyCode?: string; regulationRef?: string;
  }): TaxBracket {
    if (params.rate < 0 || params.rate > 1) throw new DomainError("Validation", "Tax rate must be between 0 and 1");
    if (params.deductAmount < 0n) throw new DomainError("Validation", "Deduct amount cannot be negative");

    const tb = new TaxBracket(TaxBracketId.new(), params.name, params.bracketOrder, params.fromAmount, params.rate, params.deductAmount);
    tb._toAmount = params.toAmount ?? null;
    tb._currencyCode = params.currencyCode ?? "VND";
    tb._regulationRef = params.regulationRef ?? null;
    tb.addEvent(new TaxBracketCreated(tb._id.value, new Date(), { name: tb._name, bracketOrder: tb._bracketOrder }));
    return tb;
  }

  static load(state: TaxBracketState): TaxBracket {
    const tb = new TaxBracket(new TaxBracketId(state.id), state.name, state.bracketOrder, state.fromAmount, state.rate, state.deductAmount);
    tb._effectiveFrom = state.effectiveFrom;
    tb._effectiveTo = state.effectiveTo;
    tb._toAmount = state.toAmount;
    tb._currencyCode = state.currencyCode;
    tb._isActive = state.isActive;
    tb._regulationRef = state.regulationRef;
    tb._version = state.version;
    tb._createdAt = state.createdAt;
    tb._updatedAt = state.updatedAt;
    tb._deletedAt = state.deletedAt;
    return tb;
  }

  toState(): TaxBracketState {
    return {
      id: this._id.value, name: this._name,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      bracketOrder: this._bracketOrder, fromAmount: this._fromAmount,
      toAmount: this._toAmount, rate: this._rate, deductAmount: this._deductAmount,
      currencyCode: this._currencyCode, isActive: this._isActive,
      regulationRef: this._regulationRef, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }

  contains(taxableIncome: bigint): boolean {
    if (taxableIncome < this._fromAmount) return false;
    if (this._toAmount === null) return true;
    return taxableIncome <= this._toAmount;
  }

  calculateTax(taxableIncome: bigint): bigint {
    if (!this.contains(taxableIncome)) return 0n;
    const bracketIncome = this._toAmount === null
      ? taxableIncome - this._fromAmount + 1n
      : (taxableIncome > this._toAmount ? this._toAmount - this._fromAmount + 1n : taxableIncome - this._fromAmount + 1n);
    if (bracketIncome <= 0n) return 0n;
    return BigInt(Math.round(Number(bracketIncome) * this._rate));
  }

  get id(): TaxBracketId { return this._id; }
  get bracketOrder(): number { return this._bracketOrder; }
  get fromAmount(): bigint { return this._fromAmount; }
  get toAmount(): bigint | null { return this._toAmount; }
  get rate(): number { return this._rate; }
  get deductAmount(): bigint { return this._deductAmount; }
  get version(): number { return this._version; }
}
