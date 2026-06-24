import Decimal from "decimal.js";

export class Money {
  private readonly _amount: Decimal;

  private constructor(amount: Decimal.Value) {
    const d = amount instanceof Decimal ? amount : new Decimal(amount);
    this._amount = d.toDecimalPlaces(2, Decimal.ROUND_HALF_UP);
  }

  static fromVnd(amount: Decimal.Value): Money {
    return new Money(amount);
  }

  static zero(): Money {
    return new Money(0);
  }

  get amount(): Decimal {
    return this._amount;
  }

  get isNegative(): boolean {
    return this._amount.isNegative();
  }

  negate(): Money {
    return new Money(this._amount.negated());
  }

  add(other: Money): Money {
    return new Money(this._amount.plus(other._amount));
  }

  subtract(other: Money): Money {
    return new Money(this._amount.minus(other._amount));
  }

  multiply(factor: Decimal.Value): Money {
    const f = factor instanceof Decimal ? factor : new Decimal(factor);
    return new Money(this._amount.times(f));
  }

  divide(divisor: Decimal.Value): Money {
    const d = divisor instanceof Decimal ? divisor : new Decimal(divisor);
    if (d.isZero()) throw new Error("Division by zero");
    return new Money(this._amount.div(d));
  }

  greaterThan(other: Money): boolean {
    return this._amount.greaterThan(other._amount);
  }

  lessThan(other: Money): boolean {
    return this._amount.lessThan(other._amount);
  }

  greaterThanOrEqual(other: Money): boolean {
    return this._amount.greaterThanOrEqualTo(other._amount);
  }

  lessThanOrEqual(other: Money): boolean {
    return this._amount.lessThanOrEqualTo(other._amount);
  }

  equals(other: Money): boolean {
    return this._amount.equals(other._amount);
  }

  isZero(): boolean {
    return this._amount.isZero();
  }

  toString(): string {
    return this._amount.toFixed(2);
  }

  toNumber(): number {
    return this._amount.toNumber();
  }

  toBigInt(): bigint {
    return BigInt(this._amount.times(100).toFixed(0));
  }

  static fromBigInt(value: bigint): Money {
    return new Money(new Decimal(value.toString()).div(100));
  }

  toJSON(): string {
    return this.toString();
  }
}
