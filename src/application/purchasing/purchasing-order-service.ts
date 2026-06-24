import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PurchaseRequisitionId, RFQId, PurchaseOrderId, PurchaseContractId, GoodsReceiptId, SupplierInvoiceId, ImportDeclarationId, VendorId } from "../../domain/purchasing/purchasing-ids.js";
import { PurchaseRequisition, RequisitionItem } from "../../domain/purchasing/purchasing-requisition.js";
import { RFQ, RFQItem, Quotation } from "../../domain/purchasing/purchasing-rfq.js";
import { PurchaseOrder, POLine } from "../../domain/purchasing/purchasing-order.js";
import { PurchaseContract } from "../../domain/purchasing/purchasing-contract.js";
import { GoodsReceipt, ReceiptLine } from "../../domain/purchasing/purchasing-receiving.js";
import { SupplierInvoice, InvoiceLine } from "../../domain/purchasing/purchasing-invoice.js";
import { ImportDeclaration, LandedCost } from "../../domain/purchasing/purchasing-import.js";
import { RequisitionStatus, POStatus, POType, InvoiceStatus, Incoterm, FreightTerm, LandedCostType } from "../../domain/purchasing/purchasing-enums.js";
import {
  PrismaPurchaseRequisitionRepository,
  PrismaRFQRepository, PrismaQuotationRepository,
  PrismaPurchaseOrderRepository,
  PrismaPurchaseContractRepository,
  PrismaGoodsReceiptRepository,
  PrismaSupplierInvoiceRepository,
  PrismaImportDeclarationRepository,
  PrismaVendorRepository,
} from "../../infrastructure/purchasing/purchasing-prisma-repos.js";

@Injectable()
export class PurchasingOrderService {
  constructor(
    private readonly prRepo: PrismaPurchaseRequisitionRepository,
    private readonly rfqRepo: PrismaRFQRepository,
    private readonly qtnRepo: PrismaQuotationRepository,
    private readonly poRepo: PrismaPurchaseOrderRepository,
    private readonly contractRepo: PrismaPurchaseContractRepository,
    private readonly grRepo: PrismaGoodsReceiptRepository,
    private readonly invRepo: PrismaSupplierInvoiceRepository,
    private readonly importRepo: PrismaImportDeclarationRepository,
    private readonly vendorRepo: PrismaVendorRepository,
  ) {}

  // ─── Purchase Requisition ─────────────────────────────────────────────────────

  async createRequisition(p: {
    prNumber: string; companyId: string; requesterId: string; branchId?: string;
    departmentId?: string; description?: string; priority?: string; notes?: string;
  }): Promise<PurchaseRequisition> {
    const existing = await this.prRepo.findByPrNumber(p.prNumber);
    if (existing) throw new DomainError("Conflict", `PR ${p.prNumber} already exists`);
    return PurchaseRequisition.create(p as any);
  }

  async saveRequisition(pr: PurchaseRequisition): Promise<void> {
    await this.prRepo.save(pr);
  }

  async getRequisition(id: string): Promise<PurchaseRequisition | null> {
    return this.prRepo.findById(PurchaseRequisitionId.from(id));
  }

  async listRequisitions(status?: string): Promise<PurchaseRequisition[]> {
    return status ? this.prRepo.findByStatus(status) : this.prRepo.findAll();
  }

  async submitRequisition(id: string): Promise<PurchaseRequisition> {
    const pr = await this.prRepo.findById(PurchaseRequisitionId.from(id));
    if (!pr) throw new DomainError("NotFound", "Requisition not found");
    pr.submit();
    await this.prRepo.save(pr);
    return pr;
  }

  async approveRequisition(id: string, approvedBy: string): Promise<PurchaseRequisition> {
    const pr = await this.prRepo.findById(PurchaseRequisitionId.from(id));
    if (!pr) throw new DomainError("NotFound", "Requisition not found");
    pr.approve(approvedBy);
    await this.prRepo.save(pr);
    return pr;
  }

  // ─── RFQ ──────────────────────────────────────────────────────────────────────

  async createRFQ(p: { rfqNumber: string; companyId: string; title: string; branchId?: string; description?: string; responseDeadline?: Date; notes?: string }): Promise<RFQ> {
    const existing = await this.rfqRepo.findByRfqNumber(p.rfqNumber);
    if (existing) throw new DomainError("Conflict", `RFQ ${p.rfqNumber} already exists`);
    return RFQ.create(p);
  }

  async saveRFQ(rfq: RFQ): Promise<void> { await this.rfqRepo.save(rfq); }

  async sendRFQ(id: string): Promise<RFQ> {
    const rfq = await this.rfqRepo.findById(RFQId.from(id));
    if (!rfq) throw new DomainError("NotFound", "RFQ not found");
    rfq.send();
    await this.rfqRepo.save(rfq);
    return rfq;
  }

  async submitQuotation(p: { rfqId: string; vendorId: string; vendorName: string; quotationNumber: string; totalAmount: number; validUntil?: Date; notes?: string }): Promise<Quotation> {
    const q = Quotation.create(p);
    q.submit();
    await this.qtnRepo.save(q);
    return q;
  }

  // ─── Purchase Order ───────────────────────────────────────────────────────────

  async createPO(p: {
    poNumber: string; companyId: string; vendorId: string; vendorName: string;
    branchId?: string; poType?: POType; currencyCode?: string; description?: string;
    paymentTermCode?: string; incoterm?: string; requestedDate?: Date;
    sourceDocumentType?: string; sourceDocumentId?: string;
  }): Promise<PurchaseOrder> {
    const vendor = await this.vendorRepo.findById(VendorId.from(p.vendorId));
    if (vendor && (!vendor.isActive || vendor.status !== "active")) throw new DomainError("BusinessRule", `Vendor ${p.vendorId} is not active`);

    const existing = await this.poRepo.findByPoNumber(p.poNumber);
    if (existing) throw new DomainError("Conflict", `PO ${p.poNumber} already exists`);
    return PurchaseOrder.create(p as any);
  }

  async savePO(po: PurchaseOrder): Promise<void> { await this.poRepo.save(po); }

  async getPO(id: string): Promise<PurchaseOrder | null> {
    return this.poRepo.findById(PurchaseOrderId.from(id));
  }

  async getPOByNumber(poNumber: string): Promise<PurchaseOrder | null> {
    return this.poRepo.findByPoNumber(poNumber);
  }

  async listPOs(status?: string): Promise<PurchaseOrder[]> {
    return status ? this.poRepo.findByStatus(status) : this.poRepo.findAll();
  }

  async submitPO(id: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.submitForApproval();
    await this.poRepo.save(po);
    return po;
  }

  async approvePO(id: string, approvedBy: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.approve(approvedBy);
    await this.poRepo.save(po);
    return po;
  }

  async sendPO(id: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.send();
    await this.poRepo.save(po);
    return po;
  }

  async confirmPO(id: string, confirmedBy: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.confirm(confirmedBy);
    await this.poRepo.save(po);
    return po;
  }

  async cancelPO(id: string, reason: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.cancel(reason);
    await this.poRepo.save(po);
    return po;
  }

  async closePO(id: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.close();
    await this.poRepo.save(po);
    return po;
  }

  async holdPO(id: string, reason: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.hold(reason);
    await this.poRepo.save(po);
    return po;
  }

  async releasePO(id: string): Promise<PurchaseOrder> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(id));
    if (!po) throw new DomainError("NotFound", "PO not found");
    po.release();
    await this.poRepo.save(po);
    return po;
  }

  // ─── Contract ─────────────────────────────────────────────────────────────────

  async createContract(p: {
    contractNumber: string; companyId: string; vendorId: string; vendorName: string;
    title: string; startDate: Date; endDate: Date; contractType?: string;
    totalValue?: number; description?: string; paymentTermCode?: string; notes?: string;
  }): Promise<PurchaseContract> {
    const existing = await this.contractRepo.findByContractNumber(p.contractNumber);
    if (existing) throw new DomainError("Conflict", `Contract ${p.contractNumber} already exists`);
    return PurchaseContract.create(p as any);
  }

  async activateContract(id: string): Promise<PurchaseContract> {
    const c = await this.contractRepo.findById(PurchaseContractId.from(id));
    if (!c) throw new DomainError("NotFound", "Contract not found");
    c.activate();
    await this.contractRepo.save(c);
    return c;
  }

  // ─── Goods Receipt ────────────────────────────────────────────────────────────

  async createReceipt(p: {
    receiptNumber: string; companyId: string; vendorId: string; vendorName: string;
    poId: string; poNumber: string; receiptDate: Date; receivedBy: string;
    branchId?: string; warehouseId?: string; notes?: string;
  }): Promise<GoodsReceipt> {
    const po = await this.poRepo.findById(PurchaseOrderId.from(p.poId));
    if (!po) throw new DomainError("NotFound", "PO not found");
    const existing = await this.grRepo.findByReceiptNumber(p.receiptNumber);
    if (existing) throw new DomainError("Conflict", `Receipt ${p.receiptNumber} already exists`);
    return GoodsReceipt.create(p);
  }

  async saveReceipt(gr: GoodsReceipt): Promise<void> { await this.grRepo.save(gr); }

  async reverseReceipt(id: string, reason: string): Promise<GoodsReceipt> {
    const gr = await this.grRepo.findById(GoodsReceiptId.from(id));
    if (!gr) throw new DomainError("NotFound", "Receipt not found");
    gr.reverse(reason);
    await this.grRepo.save(gr);
    return gr;
  }

  // ─── Supplier Invoice ─────────────────────────────────────────────────────────

  async createInvoice(p: {
    invoiceNumber: string; invoiceDate: Date; companyId: string;
    vendorId: string; vendorName: string; poId?: string; poNumber?: string;
    matchingRule?: string; currencyCode?: string; paymentTermCode?: string;
    dueDate?: Date; description?: string; notes?: string;
  }): Promise<SupplierInvoice> {
    const existing = await this.invRepo.findByInvoiceNumber(p.invoiceNumber);
    if (existing) throw new DomainError("Conflict", `Invoice ${p.invoiceNumber} already exists`);
    return SupplierInvoice.create(p);
  }

  async saveInvoice(inv: SupplierInvoice): Promise<void> { await this.invRepo.save(inv); }

  async verifyInvoice(id: string): Promise<SupplierInvoice> {
    const inv = await this.invRepo.findById(SupplierInvoiceId.from(id));
    if (!inv) throw new DomainError("NotFound", "Invoice not found");
    inv.verify();
    await this.invRepo.save(inv);
    return inv;
  }

  async approveInvoice(id: string, approvedBy: string): Promise<SupplierInvoice> {
    const inv = await this.invRepo.findById(SupplierInvoiceId.from(id));
    if (!inv) throw new DomainError("NotFound", "Invoice not found");
    inv.approve(approvedBy);
    await this.invRepo.save(inv);
    return inv;
  }

  async cancelInvoice(id: string, reason: string): Promise<SupplierInvoice> {
    const inv = await this.invRepo.findById(SupplierInvoiceId.from(id));
    if (!inv) throw new DomainError("NotFound", "Invoice not found");
    inv.cancel(reason);
    await this.invRepo.save(inv);
    return inv;
  }

  // ─── Import Declaration ───────────────────────────────────────────────────────

  async createImportDeclaration(p: {
    declarationNumber: string; companyId: string; poId: string; poNumber: string;
    vendorId: string; vendorName: string; incoterm?: Incoterm; freightTerm?: FreightTerm;
    currencyCode?: string; portOfLoading?: string; portOfDischarge?: string; notes?: string;
  }): Promise<ImportDeclaration> {
    const existing = await this.importRepo.findByDeclarationNumber(p.declarationNumber);
    if (existing) throw new DomainError("Conflict", `Declaration ${p.declarationNumber} already exists`);
    return ImportDeclaration.create(p);
  }

  async addLandedCost(declarationId: string, cost: LandedCost): Promise<ImportDeclaration> {
    const d = await this.importRepo.findById(ImportDeclarationId.from(declarationId));
    if (!d) throw new DomainError("NotFound", "Import declaration not found");
    d.addLandedCost(cost);
    await this.importRepo.save(d);
    await this.importRepo.saveLandedCost(cost);
    return d;
  }
}
