export class SalesAddress {
  constructor(
    readonly street: string,
    readonly ward: string | null = null,
    readonly district: string | null = null,
    readonly province: string | null = null,
    readonly country: string = "VN",
    readonly postalCode: string | null = null,
  ) {}
  full(): string {
    return [this.street, this.ward, this.district, this.province, this.country].filter(Boolean).join(", ");
  }
}

export class CustomerTaxInfo {
  constructor(
    readonly taxCode: string,
    readonly companyName: string | null = null,
    readonly address: string | null = null,
  ) {
    if (taxCode && !/^\d{10}(-\d{3})?$/.test(taxCode)) throw new Error("Invalid tax code format");
  }
}

export class ContactInfo {
  constructor(
    readonly fullName: string,
    readonly email: string | null = null,
    readonly phone: string | null = null,
    readonly position: string | null = null,
    readonly isPrimary: boolean = false,
  ) {}
}

export class PaymentTerm {
  constructor(
    readonly code: string,
    readonly name: string,
    readonly dueDays: number,
    readonly discountDays: number | null = null,
    readonly discountPercent: number | null = null,
  ) {}
}

export class CreditLimit {
  constructor(
    readonly limit: number,
    readonly used: number = 0,
    readonly available: number = 0,
    readonly currencyCode: string = "VND",
  ) {
    if (limit < 0) throw new Error("Credit limit cannot be negative");
    this.available = limit - used;
  }
}

export class OrderDiscount {
  constructor(
    readonly type: string,
    readonly value: number,
    readonly amount: number,
    readonly reason: string | null = null,
  ) {}
}

export class TaxBreakdown {
  constructor(
    readonly taxCode: string,
    readonly taxRate: number,
    readonly taxableAmount: number,
    readonly taxAmount: number,
  ) {}
}

export class PaymentAllocation {
  constructor(
    readonly invoiceId: string,
    readonly invoiceNumber: string,
    readonly amount: number,
    readonly currencyCode: string = "VND",
  ) {}
}

export class MoneyAmount {
  constructor(
    readonly amount: number,
    readonly currencyCode: string = "VND",
  ) {
    if (amount < 0) throw new Error("Amount cannot be negative");
  }
  add(other: MoneyAmount): MoneyAmount {
    if (this.currencyCode !== other.currencyCode) throw new Error("Currency mismatch");
    return new MoneyAmount(this.amount + other.amount, this.currencyCode);
  }
  subtract(other: MoneyAmount): MoneyAmount {
    if (this.currencyCode !== other.currencyCode) throw new Error("Currency mismatch");
    return new MoneyAmount(this.amount - other.amount, this.currencyCode);
  }
}
