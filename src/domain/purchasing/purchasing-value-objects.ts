export class Address {
  constructor(
    readonly street: string,
    readonly ward: string,
    readonly district: string,
    readonly province: string,
    readonly country: string,
    readonly postalCode: string | null = null,
  ) {}
  full(): string { return `${this.street}, ${this.ward}, ${this.district}, ${this.province}, ${this.country}`; }
}

export class TaxCode {
  constructor(readonly value: string) {
    if (!/^\d{10}(-\d{3})?$/.test(value)) throw new Error("Invalid tax code format 10 digits or 13 digits");
  }
  toString(): string { return this.value; }
}

export class Quantity {
  constructor(readonly value: number) {
    if (value < 0) throw new Error("Quantity cannot be negative");
  }
  add(q: Quantity): Quantity { return new Quantity(this.value + q.value); }
  subtract(q: Quantity): Quantity { return new Quantity(this.value - q.value); }
  isZero(): boolean { return this.value === 0; }
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

export class BankInfo {
  constructor(
    readonly bankName: string,
    readonly branch: string | null,
    readonly accountNumber: string,
    readonly accountName: string,
    readonly swiftCode: string | null = null,
  ) {}
}

export class ContactInfo {
  constructor(
    readonly fullName: string,
    readonly email: string,
    readonly phone: string,
    readonly position: string | null = null,
    readonly isPrimary: boolean = false,
  ) {}
}

export class CertificateInfo {
  constructor(
    readonly type: string,
    readonly number: string,
    readonly issuedDate: Date,
    readonly expiryDate: Date | null,
    readonly issuingBody: string,
  ) {}
}
