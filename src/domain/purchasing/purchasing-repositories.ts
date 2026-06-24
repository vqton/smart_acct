import {
  VendorId, VendorGroupId, PurchaseRequisitionId, RFQId, QuotationId,
  PurchaseOrderId, PurchaseContractId, GoodsReceiptId, SupplierInvoiceId,
  ImportDeclarationId, PurchasePlanId,
} from "./purchasing-ids.js";
import { Vendor, VendorQualification, VendorEvaluation } from "./purchasing-vendor.js";
import { PurchaseRequisition, RequisitionItem } from "./purchasing-requisition.js";
import { RFQ, RFQItem, Quotation } from "./purchasing-rfq.js";
import { PurchaseOrder, POLine } from "./purchasing-order.js";
import { PurchaseContract } from "./purchasing-contract.js";
import { GoodsReceipt, ReceiptLine } from "./purchasing-receiving.js";
import { SupplierInvoice, InvoiceLine } from "./purchasing-invoice.js";
import { ImportDeclaration, LandedCost } from "./purchasing-import.js";

export interface VendorRepository {
  save(vendor: Vendor): Promise<void>;
  findById(id: VendorId): Promise<Vendor | null>;
  findByCode(code: string): Promise<Vendor | null>;
  findAll(): Promise<Vendor[]>;
  findActive(): Promise<Vendor[]>;
  search(criteria: Partial<{ code: string; name: string; taxCode: string; status: string; category: string }>): Promise<Vendor[]>;
}

export interface VendorQualificationRepository {
  save(q: VendorQualification): Promise<void>;
  findById(id: string): Promise<VendorQualification | null>;
  findByVendorId(vendorId: string): Promise<VendorQualification[]>;
  findActiveByVendorId(vendorId: string): Promise<VendorQualification | null>;
}

export interface VendorEvaluationRepository {
  save(e: VendorEvaluation): Promise<void>;
  findById(id: string): Promise<VendorEvaluation | null>;
  findByVendorId(vendorId: string): Promise<VendorEvaluation[]>;
}

export interface PurchaseRequisitionRepository {
  save(pr: PurchaseRequisition): Promise<void>;
  findById(id: PurchaseRequisitionId): Promise<PurchaseRequisition | null>;
  findByPrNumber(prNumber: string): Promise<PurchaseRequisition | null>;
  findAll(): Promise<PurchaseRequisition[]>;
  findByStatus(status: string): Promise<PurchaseRequisition[]>;
  findPendingByRequester(requesterId: string): Promise<PurchaseRequisition[]>;
  saveItem(item: RequisitionItem): Promise<void>;
}

export interface RFQRepository {
  save(rfq: RFQ): Promise<void>;
  findById(id: RFQId): Promise<RFQ | null>;
  findByRfqNumber(rfqNumber: string): Promise<RFQ | null>;
  findAll(): Promise<RFQ[]>;
  findOpen(): Promise<RFQ[]>;
  saveItem(item: RFQItem): Promise<void>;
}

export interface QuotationRepository {
  save(q: Quotation): Promise<void>;
  findById(id: QuotationId): Promise<Quotation | null>;
  findByRfqId(rfqId: string): Promise<Quotation[]>;
  findByVendorId(vendorId: string): Promise<Quotation[]>;
}

export interface PurchaseOrderRepository {
  save(po: PurchaseOrder): Promise<void>;
  findById(id: PurchaseOrderId): Promise<PurchaseOrder | null>;
  findByPoNumber(poNumber: string): Promise<PurchaseOrder | null>;
  findAll(): Promise<PurchaseOrder[]>;
  findByStatus(status: string): Promise<PurchaseOrder[]>;
  findByVendorId(vendorId: string): Promise<PurchaseOrder[]>;
  findOpen(): Promise<PurchaseOrder[]>;
  findBySourceDocument(sourceType: string, sourceId: string): Promise<PurchaseOrder[]>;
  saveLine(line: POLine): Promise<void>;
}

export interface PurchaseContractRepository {
  save(c: PurchaseContract): Promise<void>;
  findById(id: PurchaseContractId): Promise<PurchaseContract | null>;
  findByContractNumber(number: string): Promise<PurchaseContract | null>;
  findAll(): Promise<PurchaseContract[]>;
  findByVendorId(vendorId: string): Promise<PurchaseContract[]>;
  findActive(): Promise<PurchaseContract[]>;
  findExpiring(days: number): Promise<PurchaseContract[]>;
}

export interface GoodsReceiptRepository {
  save(gr: GoodsReceipt): Promise<void>;
  findById(id: GoodsReceiptId): Promise<GoodsReceipt | null>;
  findByReceiptNumber(number: string): Promise<GoodsReceipt | null>;
  findByPoId(poId: string): Promise<GoodsReceipt[]>;
  findAll(): Promise<GoodsReceipt[]>;
  saveLine(line: ReceiptLine): Promise<void>;
}

export interface SupplierInvoiceRepository {
  save(inv: SupplierInvoice): Promise<void>;
  findById(id: SupplierInvoiceId): Promise<SupplierInvoice | null>;
  findByInvoiceNumber(invoiceNumber: string): Promise<SupplierInvoice | null>;
  findAll(): Promise<SupplierInvoice[]>;
  findByStatus(status: string): Promise<SupplierInvoice[]>;
  findByVendorId(vendorId: string): Promise<SupplierInvoice[]>;
  findByPoId(poId: string): Promise<SupplierInvoice[]>;
  findPending(): Promise<SupplierInvoice[]>;
  saveLine(line: InvoiceLine): Promise<void>;
}

export interface ImportDeclarationRepository {
  save(d: ImportDeclaration): Promise<void>;
  findById(id: ImportDeclarationId): Promise<ImportDeclaration | null>;
  findByDeclarationNumber(number: string): Promise<ImportDeclaration | null>;
  findByPoId(poId: string): Promise<ImportDeclaration[]>;
  findAll(): Promise<ImportDeclaration[]>;
  saveLandedCost(lc: LandedCost): Promise<void>;
}
