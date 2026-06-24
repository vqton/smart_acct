import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class VendorId extends Identifier { static new(): VendorId { return new VendorId(IdGenerator.uuid()); } static from(id: string): VendorId { return new VendorId(id); } }
export class VendorGroupId extends Identifier { static new(): VendorGroupId { return new VendorGroupId(IdGenerator.uuid()); } }
export class VendorCategoryId extends Identifier { static new(): VendorCategoryId { return new VendorCategoryId(IdGenerator.uuid()); } }
export class VendorContactId extends Identifier { static new(): VendorContactId { return new VendorContactId(IdGenerator.uuid()); } }
export class VendorBankAccountId extends Identifier { static new(): VendorBankAccountId { return new VendorBankAccountId(IdGenerator.uuid()); } }
export class VendorTaxInfoId extends Identifier { static new(): VendorTaxInfoId { return new VendorTaxInfoId(IdGenerator.uuid()); } }
export class VendorCertificateId extends Identifier { static new(): VendorCertificateId { return new VendorCertificateId(IdGenerator.uuid()); } }
export class VendorEvaluationId extends Identifier { static new(): VendorEvaluationId { return new VendorEvaluationId(IdGenerator.uuid()); } }
export class VendorPerformanceId extends Identifier { static new(): VendorPerformanceId { return new VendorPerformanceId(IdGenerator.uuid()); } }
export class VendorScorecardId extends Identifier { static new(): VendorScorecardId { return new VendorScorecardId(IdGenerator.uuid()); } }
export class VendorRegistrationId extends Identifier { static new(): VendorRegistrationId { return new VendorRegistrationId(IdGenerator.uuid()); } }
export class VendorQualificationId extends Identifier { static new(): VendorQualificationId { return new VendorQualificationId(IdGenerator.uuid()); } }
export class PurchaseRequisitionId extends Identifier { static new(): PurchaseRequisitionId { return new PurchaseRequisitionId(IdGenerator.uuid()); } static from(id: string): PurchaseRequisitionId { return new PurchaseRequisitionId(id); } }
export class RequisitionItemId extends Identifier { static new(): RequisitionItemId { return new RequisitionItemId(IdGenerator.uuid()); } }
export class RFQId extends Identifier { static new(): RFQId { return new RFQId(IdGenerator.uuid()); } static from(id: string): RFQId { return new RFQId(id); } }
export class RFQItemId extends Identifier { static new(): RFQItemId { return new RFQItemId(IdGenerator.uuid()); } }
export class QuotationId extends Identifier { static new(): QuotationId { return new QuotationId(IdGenerator.uuid()); } }
export class QuotationItemId extends Identifier { static new(): QuotationItemId { return new QuotationItemId(IdGenerator.uuid()); } }
export class VendorResponseId extends Identifier { static new(): VendorResponseId { return new VendorResponseId(IdGenerator.uuid()); } }
export class PurchaseOrderId extends Identifier { static new(): PurchaseOrderId { return new PurchaseOrderId(IdGenerator.uuid()); } static from(id: string): PurchaseOrderId { return new PurchaseOrderId(id); } }
export class POLineId extends Identifier { static new(): POLineId { return new POLineId(IdGenerator.uuid()); } }
export class PORevisionId extends Identifier { static new(): PORevisionId { return new PORevisionId(IdGenerator.uuid()); } }
export class POTermId extends Identifier { static new(): POTermId { return new POTermId(IdGenerator.uuid()); } }
export class PurchaseContractId extends Identifier { static new(): PurchaseContractId { return new PurchaseContractId(IdGenerator.uuid()); } static from(id: string): PurchaseContractId { return new PurchaseContractId(id); } }
export class ContractAmendmentId extends Identifier { static new(): ContractAmendmentId { return new ContractAmendmentId(IdGenerator.uuid()); } }
export class PricingAgreementId extends Identifier { static new(): PricingAgreementId { return new PricingAgreementId(IdGenerator.uuid()); } }
export class GoodsReceiptId extends Identifier { static new(): GoodsReceiptId { return new GoodsReceiptId(IdGenerator.uuid()); } static from(id: string): GoodsReceiptId { return new GoodsReceiptId(id); } }
export class ReceiptLineId extends Identifier { static new(): ReceiptLineId { return new ReceiptLineId(IdGenerator.uuid()); } }
export class ReceiptReversalId extends Identifier { static new(): ReceiptReversalId { return new ReceiptReversalId(IdGenerator.uuid()); } }
export class InspectionPlanId extends Identifier { static new(): InspectionPlanId { return new InspectionPlanId(IdGenerator.uuid()); } }
export class InspectionLotId extends Identifier { static new(): InspectionLotId { return new InspectionLotId(IdGenerator.uuid()); } }
export class InspectionResultId extends Identifier { static new(): InspectionResultId { return new InspectionResultId(IdGenerator.uuid()); } }
export class SupplierInvoiceId extends Identifier { static new(): SupplierInvoiceId { return new SupplierInvoiceId(IdGenerator.uuid()); } static from(id: string): SupplierInvoiceId { return new SupplierInvoiceId(id); } }
export class InvoiceLineId extends Identifier { static new(): InvoiceLineId { return new InvoiceLineId(IdGenerator.uuid()); } }
export class DebitMemoId extends Identifier { static new(): DebitMemoId { return new DebitMemoId(IdGenerator.uuid()); } }
export class CreditMemoId extends Identifier { static new(): CreditMemoId { return new CreditMemoId(IdGenerator.uuid()); } }
export class PrepaymentId extends Identifier { static new(): PrepaymentId { return new PrepaymentId(IdGenerator.uuid()); } }
export class PaymentScheduleId extends Identifier { static new(): PaymentScheduleId { return new PaymentScheduleId(IdGenerator.uuid()); } }
export class ImportDeclarationId extends Identifier { static new(): ImportDeclarationId { return new ImportDeclarationId(IdGenerator.uuid()); } static from(id: string): ImportDeclarationId { return new ImportDeclarationId(id); } }
export class ShipmentId extends Identifier { static new(): ShipmentId { return new ShipmentId(IdGenerator.uuid()); } }
export class ContainerId extends Identifier { static new(): ContainerId { return new ContainerId(IdGenerator.uuid()); } }
export class LandedCostId extends Identifier { static new(): LandedCostId { return new LandedCostId(IdGenerator.uuid()); } }
export class PurchaseBudgetId extends Identifier { static new(): PurchaseBudgetId { return new PurchaseBudgetId(IdGenerator.uuid()); } }
export class ApprovalRequestId extends Identifier { static new(): ApprovalRequestId { return new ApprovalRequestId(IdGenerator.uuid()); } }
export class ApprovalMatrixId extends Identifier { static new(): ApprovalMatrixId { return new ApprovalMatrixId(IdGenerator.uuid()); } }
export class PurchasePlanId extends Identifier { static new(): PurchasePlanId { return new PurchasePlanId(IdGenerator.uuid()); } }
export class PlanItemId extends Identifier { static new(): PlanItemId { return new PlanItemId(IdGenerator.uuid()); } }
export class PurchaseForecastId extends Identifier { static new(): PurchaseForecastId { return new PurchaseForecastId(IdGenerator.uuid()); } }
export class DemandId extends Identifier { static new(): DemandId { return new DemandId(IdGenerator.uuid()); } }
