import { DomainEvent } from "../../shared/domain-event.js";

export class VendorCreated implements DomainEvent {
  readonly eventName = "VendorCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class VendorUpdated implements DomainEvent {
  readonly eventName = "VendorUpdated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class VendorBlocked implements DomainEvent {
  readonly eventName = "VendorBlocked";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class VendorUnblocked implements DomainEvent {
  readonly eventName = "VendorUnblocked";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class VendorQualified implements DomainEvent {
  readonly eventName = "VendorQualified";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class VendorEvaluationCompleted implements DomainEvent {
  readonly eventName = "VendorEvaluationCompleted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RequisitionCreated implements DomainEvent {
  readonly eventName = "RequisitionCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RequisitionSubmitted implements DomainEvent {
  readonly eventName = "RequisitionSubmitted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RequisitionApproved implements DomainEvent {
  readonly eventName = "RequisitionApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RequisitionRejected implements DomainEvent {
  readonly eventName = "RequisitionRejected";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RequisitionCancelled implements DomainEvent {
  readonly eventName = "RequisitionCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RFQCreated implements DomainEvent {
  readonly eventName = "RFQCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class RFQSent implements DomainEvent {
  readonly eventName = "RFQSent";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationReceived implements DomainEvent {
  readonly eventName = "QuotationReceived";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderCreated implements DomainEvent {
  readonly eventName = "PurchaseOrderCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderApproved implements DomainEvent {
  readonly eventName = "PurchaseOrderApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderSent implements DomainEvent {
  readonly eventName = "PurchaseOrderSent";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderConfirmed implements DomainEvent {
  readonly eventName = "PurchaseOrderConfirmed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderCancelled implements DomainEvent {
  readonly eventName = "PurchaseOrderCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderClosed implements DomainEvent {
  readonly eventName = "PurchaseOrderClosed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderOnHold implements DomainEvent {
  readonly eventName = "PurchaseOrderOnHold";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseOrderRevisionCreated implements DomainEvent {
  readonly eventName = "PurchaseOrderRevisionCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class GoodsReceiptCreated implements DomainEvent {
  readonly eventName = "GoodsReceiptCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class GoodsReceiptReversed implements DomainEvent {
  readonly eventName = "GoodsReceiptReversed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReturnToVendorCreated implements DomainEvent {
  readonly eventName = "ReturnToVendorCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class InspectionCompleted implements DomainEvent {
  readonly eventName = "InspectionCompleted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QualityHoldApplied implements DomainEvent {
  readonly eventName = "QualityHoldApplied";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SupplierInvoiceRegistered implements DomainEvent {
  readonly eventName = "SupplierInvoiceRegistered";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SupplierInvoiceVerified implements DomainEvent {
  readonly eventName = "SupplierInvoiceVerified";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SupplierInvoiceMatched implements DomainEvent {
  readonly eventName = "SupplierInvoiceMatched";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class InvoiceMatchingException implements DomainEvent {
  readonly eventName = "InvoiceMatchingException";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CreditMemoCreated implements DomainEvent {
  readonly eventName = "CreditMemoCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DebitMemoCreated implements DomainEvent {
  readonly eventName = "DebitMemoCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PrepaymentCreated implements DomainEvent {
  readonly eventName = "PrepaymentCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PrepaymentApplied implements DomainEvent {
  readonly eventName = "PrepaymentApplied";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PaymentScheduled implements DomainEvent {
  readonly eventName = "PaymentScheduled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PaymentHoldApplied implements DomainEvent {
  readonly eventName = "PaymentHoldApplied";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ImportDeclarationCreated implements DomainEvent {
  readonly eventName = "ImportDeclarationCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class LandedCostPosted implements DomainEvent {
  readonly eventName = "LandedCostPosted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseContractCreated implements DomainEvent {
  readonly eventName = "PurchaseContractCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseContractAmended implements DomainEvent {
  readonly eventName = "PurchaseContractAmended";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchaseContractExpired implements DomainEvent {
  readonly eventName = "PurchaseContractExpired";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ApprovalRequestCreated implements DomainEvent {
  readonly eventName = "ApprovalRequestCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ApprovalRequestApproved implements DomainEvent {
  readonly eventName = "ApprovalRequestApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ApprovalRequestRejected implements DomainEvent {
  readonly eventName = "ApprovalRequestRejected";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ApprovalRequestDelegated implements DomainEvent {
  readonly eventName = "ApprovalRequestDelegated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ApprovalRequestEscalated implements DomainEvent {
  readonly eventName = "ApprovalRequestEscalated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PurchasePlanCreated implements DomainEvent {
  readonly eventName = "PurchasePlanCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BudgetConsumed implements DomainEvent {
  readonly eventName = "BudgetConsumed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BudgetExceeded implements DomainEvent {
  readonly eventName = "BudgetExceeded";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
