export class BgtMoney {
  private constructor(public readonly amount: number) {
    if (amount < 0) throw new Error("BgtMoney cannot be negative");
  }
  static from(amount: number): BgtMoney { return new BgtMoney(Math.round(amount * 100) / 100); }
  static zero(): BgtMoney { return new BgtMoney(0); }
  add(other: BgtMoney): BgtMoney { return BgtMoney.from(this.amount + other.amount); }
  subtract(other: BgtMoney): BgtMoney { return BgtMoney.from(this.amount - other.amount); }
  isZero(): boolean { return this.amount === 0; }
  greaterThan(other: BgtMoney): boolean { return this.amount > other.amount; }
  lessThan(other: BgtMoney): boolean { return this.amount < other.amount; }
  equals(other: BgtMoney): boolean { return this.amount === other.amount; }
  toNumber(): number { return this.amount; }
}

export class BgtPercentage {
  private constructor(public readonly value: number) {
    if (value < 0 || value > 100) throw new Error("Percentage must be 0-100");
  }
  static from(value: number): BgtPercentage { return new BgtPercentage(value); }
  static zero(): BgtPercentage { return new BgtPercentage(0); }
  of(amount: BgtMoney): BgtMoney { return BgtMoney.from(amount.amount * this.value / 100); }
  toDecimal(): number { return this.value / 100; }
}

export class BgtPeriodAmounts {
  constructor(
    public readonly period1: number = 0,
    public readonly period2: number = 0,
    public readonly period3: number = 0,
    public readonly period4: number = 0,
    public readonly period5: number = 0,
    public readonly period6: number = 0,
    public readonly period7: number = 0,
    public readonly period8: number = 0,
    public readonly period9: number = 0,
    public readonly period10: number = 0,
    public readonly period11: number = 0,
    public readonly period12: number = 0,
    public readonly period13: number = 0,
    public readonly period14: number = 0,
    public readonly period15: number = 0,
    public readonly period16: number = 0,
    public readonly period17: number = 0,
    public readonly period18: number = 0,
    public readonly period19: number = 0,
    public readonly period20: number = 0,
    public readonly period21: number = 0,
    public readonly period22: number = 0,
    public readonly period23: number = 0,
    public readonly period24: number = 0,
  ) {}

  total(): number {
    return this.period1 + this.period2 + this.period3 + this.period4
      + this.period5 + this.period6 + this.period7 + this.period8
      + this.period9 + this.period10 + this.period11 + this.period12
      + this.period13 + this.period14 + this.period15 + this.period16
      + this.period17 + this.period18 + this.period19 + this.period20
      + this.period21 + this.period22 + this.period23 + this.period24;
  }

  getPeriod(period: number): number {
    const map: Record<number, number> = {
      1: this.period1, 2: this.period2, 3: this.period3, 4: this.period4,
      5: this.period5, 6: this.period6, 7: this.period7, 8: this.period8,
      9: this.period9, 10: this.period10, 11: this.period11, 12: this.period12,
      13: this.period13, 14: this.period14, 15: this.period15, 16: this.period16,
      17: this.period17, 18: this.period18, 19: this.period19, 20: this.period20,
      21: this.period21, 22: this.period22, 23: this.period23, 24: this.period24,
    };
    return map[period] ?? 0;
  }

  setPeriod(period: number, amount: number): BgtPeriodAmounts {
    const vals = this.toArray();
    vals[period - 1] = amount;
    return BgtPeriodAmounts.fromArray(vals);
  }

  toArray(): number[] {
    return [
      this.period1, this.period2, this.period3, this.period4,
      this.period5, this.period6, this.period7, this.period8,
      this.period9, this.period10, this.period11, this.period12,
      this.period13, this.period14, this.period15, this.period16,
      this.period17, this.period18, this.period19, this.period20,
      this.period21, this.period22, this.period23, this.period24,
    ];
  }

  static fromArray(arr: number[]): BgtPeriodAmounts {
    return new BgtPeriodAmounts(...arr.slice(0, 24));
  }

  static fromState(state: {
    period1?: number; period2?: number; period3?: number; period4?: number;
    period5?: number; period6?: number; period7?: number; period8?: number;
    period9?: number; period10?: number; period11?: number; period12?: number;
    period13?: number; period14?: number; period15?: number; period16?: number;
    period17?: number; period18?: number; period19?: number; period20?: number;
    period21?: number; period22?: number; period23?: number; period24?: number;
  }): BgtPeriodAmounts {
    return new BgtPeriodAmounts(
      state.period1 ?? 0, state.period2 ?? 0, state.period3 ?? 0, state.period4 ?? 0,
      state.period5 ?? 0, state.period6 ?? 0, state.period7 ?? 0, state.period8 ?? 0,
      state.period9 ?? 0, state.period10 ?? 0, state.period11 ?? 0, state.period12 ?? 0,
      state.period13 ?? 0, state.period14 ?? 0, state.period15 ?? 0, state.period16 ?? 0,
      state.period17 ?? 0, state.period18 ?? 0, state.period19 ?? 0, state.period20 ?? 0,
      state.period21 ?? 0, state.period22 ?? 0, state.period23 ?? 0, state.period24 ?? 0,
    );
  }
}

export class BgtVariance {
  constructor(
    public readonly budgetAmount: number,
    public readonly actualAmount: number,
  ) {}
  get absolute(): number { return this.actualAmount - this.budgetAmount; }
  get percentage(): number {
    if (this.budgetAmount === 0) return this.actualAmount === 0 ? 0 : 100;
    return Math.round((this.absolute / this.budgetAmount) * 10000) / 100;
  }
  get isFavorable(): boolean { return this.absolute <= 0; }
}

export class BgtTolerance {
  constructor(
    public readonly amount: number = 0,
    public readonly percentage: number = 0,
  ) {}
  isWithin(actual: number, budgeted: number): boolean {
    if (this.amount > 0 && Math.abs(actual - budgeted) > this.amount) return false;
    if (this.percentage > 0 && budgeted !== 0) {
      const pct = Math.abs((actual - budgeted) / budgeted) * 100;
      if (pct > this.percentage) return false;
    }
    return true;
  }
}

export class BgtDimensionSet {
  constructor(
    public readonly glAccountId?: string,
    public readonly costCenterId?: string,
    public readonly departmentId?: string,
    public readonly projectId?: string,
    public readonly productId?: string,
    public readonly customerId?: string,
    public readonly supplierId?: string,
    public readonly employeeId?: string,
    public readonly assetId?: string,
    public readonly locationId?: string,
    public readonly activityId?: string,
    public readonly contractId?: string,
    public readonly campaignId?: string,
    public readonly dimension1Id?: string,
    public readonly dimension2Id?: string,
    public readonly dimension3Id?: string,
    public readonly dimension4Id?: string,
    public readonly dimension5Id?: string,
  ) {}
}
