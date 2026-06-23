import { DomainError } from "../../shared/domain-error.js";

export class SwiftCode {
  private constructor(readonly value: string) {}

  static create(code: string): SwiftCode {
    const c = code.toUpperCase().trim();
    if (!/^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$/.test(c)) {
      throw new DomainError("Validation", `Invalid SWIFT/BIC code: ${code}`);
    }
    return new SwiftCode(c);
  }

  static fromExisting(value: string): SwiftCode {
    return new SwiftCode(value);
  }

  equals(other: SwiftCode): boolean {
    return this.value === other.value;
  }

  get bankCode(): string { return this.value.substring(0, 4); }
  get countryCode(): string { return this.value.substring(4, 6); }
  get locationCode(): string { return this.value.substring(6, 8); }
  get branchCode(): string | null { return this.value.length === 11 ? this.value.substring(8) : null; }
}

export class Iban {
  private constructor(readonly value: string) {}

  static create(iban: string): Iban {
    const c = iban.replace(/\s/g, "").toUpperCase();
    if (!/^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$/.test(c)) {
      throw new DomainError("Validation", `Invalid IBAN: ${iban}`);
    }
    return new Iban(c);
  }

  static fromExisting(value: string): Iban {
    return new Iban(value);
  }

  equals(other: Iban): boolean {
    return this.value === other.value;
  }

  get countryCode(): string { return this.value.substring(0, 2); }
  get checkDigits(): string { return this.value.substring(2, 4); }
}

export class AccountNumber {
  private constructor(readonly value: string) {}

  static create(accountNumber: string): AccountNumber {
    const c = accountNumber.trim();
    if (!/^[A-Za-z0-9\-]{4,50}$/.test(c)) {
      throw new DomainError("Validation", `Invalid account number format: ${accountNumber}`);
    }
    return new AccountNumber(c);
  }

  static fromExisting(value: string): AccountNumber {
    return new AccountNumber(value);
  }

  equals(other: AccountNumber): boolean {
    return this.value === other.value;
  }

  get masked(): string {
    if (this.value.length <= 4) return this.value;
    return "*".repeat(this.value.length - 4) + this.value.slice(-4);
  }
}

export class RoutingNumber {
  private constructor(readonly value: string) {}

  static create(number: string): RoutingNumber {
    const c = number.trim();
    if (!/^\d{8,11}$/.test(c)) {
      throw new DomainError("Validation", `Invalid routing number: ${number}`);
    }
    return new RoutingNumber(c);
  }

  static fromExisting(value: string): RoutingNumber {
    return new RoutingNumber(value);
  }

  equals(other: RoutingNumber): boolean {
    return this.value === other.value;
  }
}

export class SortCode {
  private constructor(readonly value: string) {}

  static create(code: string): SortCode {
    const c = code.trim();
    if (!/^\d{6}$/.test(c)) {
      throw new DomainError("Validation", `Invalid sort code: ${code} (must be 6 digits)`);
    }
    return new SortCode(c);
  }

  static fromExisting(value: string): SortCode {
    return new SortCode(value);
  }

  get formatted(): string {
    return `${this.value.substring(0, 2)}-${this.value.substring(2, 4)}-${this.value.substring(4)}`;
  }
}

export class BankCode {
  private constructor(readonly value: string) {}

  static create(code: string): BankCode {
    const c = code.trim().toUpperCase();
    if (!/^[A-Z0-9]{3,20}$/.test(c)) {
      throw new DomainError("Validation", `Invalid bank code: ${code}`);
    }
    return new BankCode(c);
  }

  static fromExisting(value: string): BankCode {
    return new BankCode(value);
  }

  equals(other: BankCode): boolean {
    return this.value === other.value;
  }
}

export class CurrencyAmount {
  constructor(readonly amount: number, readonly currencyCode: string) {
    if (amount < 0) throw new DomainError("Validation", "Amount cannot be negative");
    if (currencyCode.length !== 3) throw new DomainError("Validation", "Currency code must be 3 characters");
    this.amount = Math.round(amount * 100) / 100;
    this.currencyCode = currencyCode.toUpperCase();
  }

  add(other: CurrencyAmount): CurrencyAmount {
    if (this.currencyCode !== other.currencyCode) throw new DomainError("Validation", "Currency mismatch");
    return new CurrencyAmount(this.amount + other.amount, this.currencyCode);
  }

  subtract(other: CurrencyAmount): CurrencyAmount {
    if (this.currencyCode !== other.currencyCode) throw new DomainError("Validation", "Currency mismatch");
    return new CurrencyAmount(this.amount - other.amount, this.currencyCode);
  }

  equals(other: CurrencyAmount): boolean {
    return this.amount === other.amount && this.currencyCode === other.currencyCode;
  }

  isZero(): boolean { return this.amount === 0; }
}

export class ExchangeRate {
  constructor(readonly rate: number, readonly fromCurrency: string, readonly toCurrency: string) {
    if (rate <= 0) throw new DomainError("Validation", "Exchange rate must be positive");
    this.rate = rate;
    this.fromCurrency = fromCurrency.toUpperCase();
    this.toCurrency = toCurrency.toUpperCase();
  }

  convert(amount: CurrencyAmount): CurrencyAmount {
    if (amount.currencyCode !== this.fromCurrency) throw new DomainError("Validation", "Currency mismatch for conversion");
    return new CurrencyAmount(amount.amount * this.rate, this.toCurrency);
  }
}

export class Address {
  constructor(
    readonly line1: string,
    readonly line2: string | null,
    readonly city: string,
    readonly state: string | null,
    readonly postalCode: string | null,
    readonly countryCode: string,
  ) {}
}

export class Signatory {
  constructor(
    readonly userId: string,
    readonly name: string,
    readonly title: string | null,
    readonly signatureRule: string,
    readonly signingLimit: number,
    readonly isActive: boolean,
  ) {}
}

export class BankAccountLimit {
  constructor(
    readonly limitType: string,
    readonly maxAmount: number,
    readonly minAmount: number,
    readonly currencyCode: string,
    readonly isEnforced: boolean,
  ) {}
}

export class MatchingRule {
  constructor(
    readonly field: string,
    readonly operator: string,
    readonly tolerance: number,
    readonly priority: number,
  ) {}
}
