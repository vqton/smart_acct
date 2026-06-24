import { DomainError } from "../../shared/domain-error.js";
import { Vendor, type VendorState } from "./purchasing-vendor.js";
import { PurchaseOrder, type PurchaseOrderState } from "./purchasing-order.js";
import { SupplierInvoice, type SupplierInvoiceState } from "./purchasing-invoice.js";
import { VendorStatus, POStatus, InvoiceStatus } from "./purchasing-enums.js";

export class ActiveVendorSpec {
  static isSatisfiedBy(v: Vendor): boolean {
    return v.isActive && v.status === VendorStatus.active;
  }
  static check(v: Vendor): void {
    if (!this.isSatisfiedBy(v)) throw new DomainError("BusinessRule", `Vendor ${v.code} is not active. Status: ${v.status}`);
  }
}

export class VendorNotBlockedSpec {
  static isSatisfiedBy(v: Vendor): boolean {
    return v.status !== VendorStatus.blocked;
  }
  static check(v: Vendor): void {
    if (!this.isSatisfiedBy(v)) throw new DomainError("BusinessRule", `Vendor ${v.code} is blocked`);
  }
}

export class POApprovedForReceivingSpec {
  static isSatisfiedBy(po: PurchaseOrder): boolean {
    return po.status === POStatus.approved || po.status === POStatus.confirmed ||
      po.status === POStatus.partlyReceived || po.status === POStatus.sent;
  }
  static check(po: PurchaseOrder): void {
    if (!this.isSatisfiedBy(po)) throw new DomainError("BusinessRule", `PO ${po.poNumber} has status ${po.status} - must be approved or confirmed for receiving`);
  }
}

export class PONotCancelledSpec {
  static isSatisfiedBy(po: PurchaseOrder): boolean {
    return po.status !== POStatus.cancelled && po.status !== POStatus.closed;
  }
  static check(po: PurchaseOrder): void {
    if (!this.isSatisfiedBy(po)) throw new DomainError("BusinessRule", `PO ${po.poNumber} is ${po.status} - cannot receive`);
  }
}

export class InvoiceApprovedForPaymentSpec {
  static isSatisfiedBy(inv: SupplierInvoice): boolean {
    return inv.status === InvoiceStatus.approved;
  }
  static check(inv: SupplierInvoice): void {
    if (!this.isSatisfiedBy(inv)) throw new DomainError("BusinessRule", `Invoice ${inv.invoiceNumber} has status ${inv.status} - must be approved for payment`);
  }
}

export class ReceiptOverToleranceSpec {
  static check(orderedQty: number, receivedQty: number, tolerancePercent: number = 10): void {
    if (orderedQty <= 0) throw new DomainError("Validation", "Ordered quantity must be positive");
    const maxQty = orderedQty * (1 + tolerancePercent / 100);
    if (receivedQty > maxQty) throw new DomainError("BusinessRule", `Receipt quantity ${receivedQty} exceeds tolerance ${tolerancePercent}% of ordered ${orderedQty}`);
  }
}

export class InvoiceOverPOToleranceSpec {
  static check(poTotal: number, invoiceTotal: number, tolerancePercent: number = 5): void {
    if (poTotal <= 0) return;
    const maxAmount = poTotal * (1 + tolerancePercent / 100);
    if (invoiceTotal > maxAmount) throw new DomainError("BusinessRule", `Invoice amount ${invoiceTotal} exceeds PO amount ${poTotal} by more than ${tolerancePercent}%`);
  }
}

export class DuplicateInvoiceSpec {
  static check(vendorId: string, invoiceNumber: string, existingInvoices: { vendorId: string; invoiceNumber: string }[]): void {
    const dup = existingInvoices.find(i => i.vendorId === vendorId && i.invoiceNumber === invoiceNumber);
    if (dup) throw new DomainError("Conflict", `Duplicate invoice ${invoiceNumber} from vendor ${vendorId}`);
  }
}

export class ClosedPeriodSpec {
  static check(transactionDate: Date, fiscalYearStart: Date, fiscalYearEnd: Date, periodStatus: string): void {
    if (periodStatus === "closed") throw new DomainError("BusinessRule", `Period ${fiscalYearStart.toISOString()} to ${fiscalYearEnd.toISOString()} is closed`);
  }
}
