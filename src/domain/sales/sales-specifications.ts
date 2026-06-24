import { DomainError } from "../../shared/domain-error.js";
import { SlsCustomerStatus, SlsOrderStatus, SlsInvoiceStatus, SlsReturnStatus } from "./sales-enums.js";

export class ActiveCustomerSpec {
  static isSatisfiedBy(status: SlsCustomerStatus, isBlacklisted: boolean): boolean {
    return status === SlsCustomerStatus.active && !isBlacklisted;
  }
  static check(status: SlsCustomerStatus, isBlacklisted: boolean, customerCode: string): void {
    if (!this.isSatisfiedBy(status, isBlacklisted)) {
      if (isBlacklisted) throw new DomainError("BusinessRule", `Customer ${customerCode} is blacklisted`);
      throw new DomainError("BusinessRule", `Customer ${customerCode} is not active. Status: ${status}`);
    }
  }
}

export class CustomerCreditLimitSpec {
  static check(creditLimit: number, creditUsed: number, orderAmount: number, customerCode: string): void {
    const available = creditLimit - creditUsed;
    if (available < orderAmount) throw new DomainError("BusinessRule", `Customer ${customerCode} credit limit exceeded. Available: ${available}, Required: ${orderAmount}`);
  }
}

export class OrderApprovedForProcessingSpec {
  static isSatisfiedBy(status: SlsOrderStatus): boolean {
    return status === SlsOrderStatus.approved || status === SlsOrderStatus.confirmed || status === SlsOrderStatus.processing;
  }
  static check(status: SlsOrderStatus, orderNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Order ${orderNumber} has status ${status} - must be approved for processing`);
  }
}

export class OrderCanDeliverSpec {
  static isSatisfiedBy(status: SlsOrderStatus): boolean {
    return status === SlsOrderStatus.approved || status === SlsOrderStatus.confirmed || status === SlsOrderStatus.processing || status === SlsOrderStatus.partlyDelivered;
  }
  static check(status: SlsOrderStatus, orderNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Order ${orderNumber} status ${status} does not allow delivery`);
  }
}

export class OrderCanInvoiceSpec {
  static isSatisfiedBy(status: SlsOrderStatus): boolean {
    return status === SlsOrderStatus.partlyDelivered || status === SlsOrderStatus.fullyDelivered;
  }
  static check(status: SlsOrderStatus, orderNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Order ${orderNumber} status ${status} - must be at least partly delivered to invoice`);
  }
}

export class OrderNotCancelledSpec {
  static isSatisfiedBy(status: SlsOrderStatus): boolean {
    return status !== SlsOrderStatus.cancelled && status !== SlsOrderStatus.completed;
  }
  static check(status: SlsOrderStatus, orderNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Order ${orderNumber} is ${status} - operation not allowed`);
  }
}

export class OrderCanReturnSpec {
  static isSatisfiedBy(status: SlsOrderStatus): boolean {
    return status === SlsOrderStatus.fullyDelivered || status === SlsOrderStatus.fullyInvoiced || status === SlsOrderStatus.fullyPaid || status === SlsOrderStatus.completed;
  }
  static check(status: SlsOrderStatus, orderNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Order ${orderNumber} status ${status} does not allow returns`);
  }
}

export class ReturnQuantitySpec {
  static check(deliveredQty: number, returnedQty: number, returnQty: number, itemCode: string): void {
    const maxReturnable = deliveredQty - returnedQty;
    if (returnQty > maxReturnable) throw new DomainError("BusinessRule", `Return quantity ${returnQty} exceeds remaining returnable ${maxReturnable} for item ${itemCode}`);
  }
}

export class InvoiceCanPostSpec {
  static isSatisfiedBy(status: SlsInvoiceStatus): boolean {
    return status === SlsInvoiceStatus.approved;
  }
  static check(status: SlsInvoiceStatus, invoiceNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Invoice ${invoiceNumber} status ${status} - must be approved for posting`);
  }
}

export class DuplicateInvoiceSpec {
  static check(customerId: string, invoiceNumber: string, existing: { customerId: string; invoiceNumber: string }[]): void {
    const dup = existing.find(i => i.customerId === customerId && i.invoiceNumber === invoiceNumber);
    if (dup) throw new DomainError("Conflict", `Duplicate invoice ${invoiceNumber} for customer ${customerId}`);
  }
}

export class ReturnCanRefundSpec {
  static isSatisfiedBy(status: SlsReturnStatus): boolean {
    return status === SlsReturnStatus.approved || status === SlsReturnStatus.inspected;
  }
  static check(status: SlsReturnStatus, returnNumber: string): void {
    if (!this.isSatisfiedBy(status)) throw new DomainError("BusinessRule", `Return ${returnNumber} status ${status} - must be approved for refund`);
  }
}

export class ClosedPeriodSpec {
  static check(transactionDate: Date, periodStatus: string): void {
    if (periodStatus === "closed") throw new DomainError("BusinessRule", `Period containing ${transactionDate.toISOString()} is closed`);
  }
}
