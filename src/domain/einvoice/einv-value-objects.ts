import { DomainError } from "../../shared/domain-error.js";

export class SellerInfo {
  constructor(
    readonly name: string,
    readonly taxCode: string,
    readonly address: string | null = null,
    readonly phone: string | null = null,
    readonly email: string | null = null,
    readonly bankName: string | null = null,
    readonly bankAccount: string | null = null,
  ) {
    if (!name) throw new DomainError("Validation", "Seller name is required");
    if (!taxCode) throw new DomainError("Validation", "Seller tax code is required");
  }
}

export class BuyerInfo {
  constructor(
    readonly name: string,
    readonly taxCode: string | null = null,
    readonly address: string | null = null,
    readonly phone: string | null = null,
    readonly email: string | null = null,
    readonly bankName: string | null = null,
    readonly bankAccount: string | null = null,
  ) {
    if (!name) throw new DomainError("Validation", "Buyer name is required");
  }
}

export class InvoiceParty {
  constructor(
    readonly seller: SellerInfo,
    readonly buyer: BuyerInfo,
  ) {}
}

export class TaxBreakdown {
  constructor(
    readonly taxCode: string,
    readonly taxRate: number,
    readonly taxableAmount: bigint,
    readonly taxAmount: bigint,
  ) {}
}

export class InvoiceTotals {
  constructor(
    readonly subtotal: bigint,
    readonly discountAmount: bigint,
    readonly taxAmount: bigint,
    readonly grandTotal: bigint,
  ) {
    if (grandTotal !== subtotal - discountAmount + taxAmount) {
      throw new DomainError("Validation", "Grand total mismatch");
    }
  }
}

export class SeriesCode {
  private static readonly PATTERN = /^[A-Z0-9]{1,10}$/;
  constructor(readonly value: string) {
    if (!SeriesCode.PATTERN.test(value)) throw new DomainError("Validation", "Invalid series code format");
  }
}

export class InvoiceNumber {
  constructor(readonly value: string) {
    if (!value || value.length > 50) throw new DomainError("Validation", "Invalid invoice number");
  }
}

export class TaxAuthorityCode {
  constructor(readonly value: string) {
    if (!value || value.length < 1) throw new DomainError("Validation", "Invalid tax authority code");
  }
}

export class VerificationCode {
  constructor(readonly value: string) {
    if (!value) throw new DomainError("Validation", "Verification code is required");
  }
}

export class AmountInWords {
  constructor(readonly value: string) {
    if (!value) throw new DomainError("Validation", "Amount in words is required");
  }
}

export class TransmissionResult {
  constructor(
    readonly status: string,
    readonly statusCode: string | null = null,
    readonly statusMessage: string | null = null,
    readonly transmissionId: string | null = null,
    readonly acknowledgedAt: Date | null = null,
    readonly responseData: string | null = null,
  ) {}
}
