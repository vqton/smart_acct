import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { VendorId, PurchaseRequisitionId, RFQId, QuotationId, PurchaseOrderId, PurchaseContractId, GoodsReceiptId, SupplierInvoiceId, ImportDeclarationId } from "../../domain/purchasing/purchasing-ids.js";
import { Vendor, type VendorState } from "../../domain/purchasing/purchasing-vendor.js";
import { VendorQualification, type VendorQualificationState, VendorEvaluation, type VendorEvaluationState } from "../../domain/purchasing/purchasing-vendor.js";
import { PurchaseRequisition, type PurchaseRequisitionState, RequisitionItem, type RequisitionItemState } from "../../domain/purchasing/purchasing-requisition.js";
import { RFQ, type RFQState, RFQItem, type RFQItemState, Quotation, type QuotationState } from "../../domain/purchasing/purchasing-rfq.js";
import { PurchaseOrder, type PurchaseOrderState, POLine, type POLineState } from "../../domain/purchasing/purchasing-order.js";
import { PurchaseContract, type PurchaseContractState } from "../../domain/purchasing/purchasing-contract.js";
import { GoodsReceipt, type GoodsReceiptState, ReceiptLine, type ReceiptLineState } from "../../domain/purchasing/purchasing-receiving.js";
import { SupplierInvoice, type SupplierInvoiceState, InvoiceLine, type InvoiceLineState } from "../../domain/purchasing/purchasing-invoice.js";
import { ImportDeclaration, type ImportDeclarationState, LandedCost, type LandedCostState } from "../../domain/purchasing/purchasing-import.js";
import type { VendorRepository, VendorQualificationRepository, VendorEvaluationRepository, PurchaseRequisitionRepository, RFQRepository, QuotationRepository, PurchaseOrderRepository, PurchaseContractRepository, GoodsReceiptRepository, SupplierInvoiceRepository, ImportDeclarationRepository } from "../../domain/purchasing/purchasing-repositories.js";

function toNumber(val: bigint | number | string | { toString(): string } | null | undefined, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  if (typeof val === "number") return val;
  if (typeof val === "object" && "toString" in val) return parseFloat(val.toString());
  return val as number;
}
function toBigInt(val: number): bigint { return BigInt(Math.round(val)); }

// ─── Vendor Repository ───────────────────────────────────────────────────────────

@Injectable()
export class PrismaVendorRepository implements VendorRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(vendor: Vendor): Promise<void> {
    const s = vendor.toState();
    const data: any = { ...s };
    await this.prisma.purVendor.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: VendorId): Promise<Vendor | null> {
    const row = await this.prisma.purVendor.findUnique({ where: { id: id.value } });
    return row ? Vendor.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Vendor | null> {
    const row = await this.prisma.purVendor.findUnique({ where: { code } });
    return row ? Vendor.load(row as any) : null;
  }

  async findAll(): Promise<Vendor[]> {
    return (await this.prisma.purVendor.findMany({ orderBy: { code: "asc" } })).map(r => Vendor.load(r as any));
  }

  async findActive(): Promise<Vendor[]> {
    return (await this.prisma.purVendor.findMany({ where: { isActive: true, status: "active" }, orderBy: { code: "asc" } })).map(r => Vendor.load(r as any));
  }

  async search(criteria: Partial<{ code: string; name: string; taxCode: string; status: string; category: string }>): Promise<Vendor[]> {
    const where: any = {};
    if (criteria.code) where.code = { contains: criteria.code };
    if (criteria.name) where.name = { contains: criteria.name };
    if (criteria.taxCode) where.taxCode = { contains: criteria.taxCode };
    if (criteria.status) where.status = criteria.status;
    if (criteria.category) where.category = criteria.category;
    return (await this.prisma.purVendor.findMany({ where, orderBy: { code: "asc" } })).map(r => Vendor.load(r as any));
  }
}

// ─── Vendor Qualification Repository ─────────────────────────────────────────────

@Injectable()
export class PrismaVendorQualificationRepository implements VendorQualificationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(q: VendorQualification): Promise<void> {
    const s = q.toState();
    await this.prisma.purVendorQualification.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: string): Promise<VendorQualification | null> {
    const row = await this.prisma.purVendorQualification.findUnique({ where: { id } });
    return row ? VendorQualification.load(row as any) : null;
  }

  async findByVendorId(vendorId: string): Promise<VendorQualification[]> {
    return (await this.prisma.purVendorQualification.findMany({ where: { vendorId } })).map(r => VendorQualification.load(r as any));
  }

  async findActiveByVendorId(vendorId: string): Promise<VendorQualification | null> {
    const row = await this.prisma.purVendorQualification.findFirst({ where: { vendorId, status: "qualified" } });
    return row ? VendorQualification.load(row as any) : null;
  }
}

// ─── Vendor Evaluation Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaVendorEvaluationRepository implements VendorEvaluationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(e: VendorEvaluation): Promise<void> {
    const s = e.toState();
    await this.prisma.purVendorEvaluation.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: string): Promise<VendorEvaluation | null> {
    const row = await this.prisma.purVendorEvaluation.findUnique({ where: { id } });
    return row ? VendorEvaluation.load(row as any) : null;
  }

  async findByVendorId(vendorId: string): Promise<VendorEvaluation[]> {
    return (await this.prisma.purVendorEvaluation.findMany({ where: { vendorId }, orderBy: { evaluatedAt: "desc" } })).map(r => VendorEvaluation.load(r as any));
  }
}

// ─── Purchase Requisition Repository ─────────────────────────────────────────────

@Injectable()
export class PrismaPurchaseRequisitionRepository implements PurchaseRequisitionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(pr: PurchaseRequisition): Promise<void> {
    const s = pr.toState();
    const data: any = { ...s, totalEstimated: toBigInt(s.totalEstimated) };
    await this.prisma.purPurchaseRequisition.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: PurchaseRequisitionId): Promise<PurchaseRequisition | null> {
    const row = await this.prisma.purPurchaseRequisition.findUnique({ where: { id: id.value } });
    return row ? PurchaseRequisition.load({ ...row, totalEstimated: toNumber(row.totalEstimated) } as any) : null;
  }

  async findByPrNumber(prNumber: string): Promise<PurchaseRequisition | null> {
    const row = await this.prisma.purPurchaseRequisition.findUnique({ where: { prNumber } });
    return row ? PurchaseRequisition.load({ ...row, totalEstimated: toNumber(row.totalEstimated) } as any) : null;
  }

  async findAll(): Promise<PurchaseRequisition[]> {
    return (await this.prisma.purPurchaseRequisition.findMany({ orderBy: { createdAt: "desc" } })).map(r => PurchaseRequisition.load({ ...r, totalEstimated: toNumber(r.totalEstimated) } as any));
  }

  async findByStatus(status: string): Promise<PurchaseRequisition[]> {
    return (await this.prisma.purPurchaseRequisition.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => PurchaseRequisition.load({ ...r, totalEstimated: toNumber(r.totalEstimated) } as any));
  }

  async findPendingByRequester(requesterId: string): Promise<PurchaseRequisition[]> {
    return (await this.prisma.purPurchaseRequisition.findMany({ where: { requesterId, status: { in: ["draft", "submitted"] } as any }, orderBy: { createdAt: "desc" } })).map(r => PurchaseRequisition.load({ ...r, totalEstimated: toNumber(r.totalEstimated) } as any));
  }

  async saveItem(item: RequisitionItem): Promise<void> {
    const s = item.toState();
    const data: any = { ...s, quantity: s.quantity, estimatedUnitPrice: toBigInt(s.estimatedUnitPrice), estimatedTotal: toBigInt(s.estimatedTotal) };
    await this.prisma.purRequisitionItem.upsert({ where: { id: data.id }, create: data, update: data });
  }
}

// ─── RFQ Repository ──────────────────────────────────────────────────────────────

@Injectable()
export class PrismaRFQRepository implements RFQRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rfq: RFQ): Promise<void> {
    const s = rfq.toState();
    const data: any = { ...s, totalEstimated: toBigInt(s.totalEstimated) };
    await this.prisma.purRFQ.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: RFQId): Promise<RFQ | null> {
    const row = await this.prisma.purRFQ.findUnique({ where: { id: id.value } });
    return row ? RFQ.load({ ...row, totalEstimated: toNumber(row.totalEstimated) } as any) : null;
  }

  async findByRfqNumber(rfqNumber: string): Promise<RFQ | null> {
    const row = await this.prisma.purRFQ.findUnique({ where: { rfqNumber } });
    return row ? RFQ.load({ ...row, totalEstimated: toNumber(row.totalEstimated) } as any) : null;
  }

  async findAll(): Promise<RFQ[]> {
    return (await this.prisma.purRFQ.findMany({ orderBy: { createdAt: "desc" } })).map(r => RFQ.load({ ...r, totalEstimated: toNumber(r.totalEstimated) } as any));
  }

  async findOpen(): Promise<RFQ[]> {
    return (await this.prisma.purRFQ.findMany({ where: { status: { in: ["sent", "responses_received"] } as any }, orderBy: { createdAt: "desc" } })).map(r => RFQ.load({ ...r, totalEstimated: toNumber(r.totalEstimated) } as any));
  }

  async saveItem(item: RFQItem): Promise<void> {
    const s = item.toState();
    const data: any = { ...s, quantity: s.quantity, expectedUnitPrice: s.expectedUnitPrice != null ? toBigInt(s.expectedUnitPrice) : null };
    await this.prisma.purRFQItem.upsert({ where: { id: data.id }, create: data, update: data });
  }
}

// ─── Quotation Repository ────────────────────────────────────────────────────────

@Injectable()
export class PrismaQuotationRepository implements QuotationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(q: Quotation): Promise<void> {
    const s = q.toState();
    const data: any = { ...s, totalAmount: toBigInt(s.totalAmount) };
    await this.prisma.purQuotation.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: QuotationId): Promise<Quotation | null> {
    const row = await this.prisma.purQuotation.findUnique({ where: { id: id.value } });
    return row ? Quotation.load({ ...row, totalAmount: toNumber(row.totalAmount) } as any) : null;
  }

  async findByRfqId(rfqId: string): Promise<Quotation[]> {
    return (await this.prisma.purQuotation.findMany({ where: { rfqId }, orderBy: { totalAmount: "asc" } })).map(r => Quotation.load({ ...r, totalAmount: toNumber(r.totalAmount) } as any));
  }

  async findByVendorId(vendorId: string): Promise<Quotation[]> {
    return (await this.prisma.purQuotation.findMany({ where: { vendorId }, orderBy: { createdAt: "desc" } })).map(r => Quotation.load({ ...r, totalAmount: toNumber(r.totalAmount) } as any));
  }
}

// ─── Purchase Order Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaPurchaseOrderRepository implements PurchaseOrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(po: PurchaseOrder): Promise<void> {
    const s = po.toState();
    const data: any = { ...s, totalAmount: toBigInt(s.totalAmount), totalTax: toBigInt(s.totalTax), grandTotal: toBigInt(s.grandTotal), exchangeRate: s.exchangeRate };
    await this.prisma.purPurchaseOrder.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: PurchaseOrderId): Promise<PurchaseOrder | null> {
    const row = await this.prisma.purPurchaseOrder.findUnique({ where: { id: id.value } });
    return row ? PurchaseOrder.load({ ...row, totalAmount: toNumber(row.totalAmount), totalTax: toNumber(row.totalTax), grandTotal: toNumber(row.grandTotal), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findByPoNumber(poNumber: string): Promise<PurchaseOrder | null> {
    const row = await this.prisma.purPurchaseOrder.findUnique({ where: { poNumber } });
    return row ? PurchaseOrder.load({ ...row, totalAmount: toNumber(row.totalAmount), totalTax: toNumber(row.totalTax), grandTotal: toNumber(row.grandTotal), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findAll(): Promise<PurchaseOrder[]> {
    return (await this.prisma.purPurchaseOrder.findMany({ orderBy: { createdAt: "desc" } })).map(r => PurchaseOrder.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findByStatus(status: string): Promise<PurchaseOrder[]> {
    return (await this.prisma.purPurchaseOrder.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => PurchaseOrder.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findByVendorId(vendorId: string): Promise<PurchaseOrder[]> {
    return (await this.prisma.purPurchaseOrder.findMany({ where: { vendorId }, orderBy: { createdAt: "desc" } })).map(r => PurchaseOrder.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findOpen(): Promise<PurchaseOrder[]> {
    return (await this.prisma.purPurchaseOrder.findMany({ where: { status: { in: ["approved", "sent", "confirmed", "partly_received", "partly_invoiced"] as any } }, orderBy: { createdAt: "desc" } })).map(r => PurchaseOrder.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findBySourceDocument(sourceType: string, sourceId: string): Promise<PurchaseOrder[]> {
    return (await this.prisma.purPurchaseOrder.findMany({ where: { sourceDocumentType: sourceType, sourceDocumentId: sourceId } })).map(r => PurchaseOrder.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async saveLine(line: POLine): Promise<void> {
    const s = line.toState();
    const data: any = { ...s, quantity: s.quantity, unitPrice: toBigInt(s.unitPrice), totalPrice: toBigInt(s.totalPrice), receivedQuantity: s.receivedQuantity, invoicedQuantity: s.invoicedQuantity, taxRate: s.taxRate };
    await this.prisma.purPOLine.upsert({ where: { id: data.id }, create: data, update: data });
  }
}

// ─── Purchase Contract Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaPurchaseContractRepository implements PurchaseContractRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(c: PurchaseContract): Promise<void> {
    const s = c.toState();
    const data: any = { ...s, totalValue: toBigInt(s.totalValue), amountSpent: toBigInt(s.amountSpent), amountRemaining: toBigInt(s.amountRemaining) };
    await this.prisma.purPurchaseContract.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: PurchaseContractId): Promise<PurchaseContract | null> {
    const row = await this.prisma.purPurchaseContract.findUnique({ where: { id: id.value } });
    return row ? PurchaseContract.load({ ...row, totalValue: toNumber(row.totalValue), amountSpent: toNumber(row.amountSpent), amountRemaining: toNumber(row.amountRemaining) } as any) : null;
  }

  async findByContractNumber(number: string): Promise<PurchaseContract | null> {
    const row = await this.prisma.purPurchaseContract.findUnique({ where: { contractNumber: number } });
    return row ? PurchaseContract.load({ ...row, totalValue: toNumber(row.totalValue), amountSpent: toNumber(row.amountSpent), amountRemaining: toNumber(row.amountRemaining) } as any) : null;
  }

  async findAll(): Promise<PurchaseContract[]> {
    return (await this.prisma.purPurchaseContract.findMany({ orderBy: { createdAt: "desc" } })).map(r => PurchaseContract.load({ ...r, totalValue: toNumber(r.totalValue), amountSpent: toNumber(r.amountSpent), amountRemaining: toNumber(r.amountRemaining) } as any));
  }

  async findByVendorId(vendorId: string): Promise<PurchaseContract[]> {
    return (await this.prisma.purPurchaseContract.findMany({ where: { vendorId }, orderBy: { createdAt: "desc" } })).map(r => PurchaseContract.load({ ...r, totalValue: toNumber(r.totalValue), amountSpent: toNumber(r.amountSpent), amountRemaining: toNumber(r.amountRemaining) } as any));
  }

  async findActive(): Promise<PurchaseContract[]> {
    return (await this.prisma.purPurchaseContract.findMany({ where: { status: "active" as any }, orderBy: { createdAt: "desc" } })).map(r => PurchaseContract.load({ ...r, totalValue: toNumber(r.totalValue), amountSpent: toNumber(r.amountSpent), amountRemaining: toNumber(r.amountRemaining) } as any));
  }

  async findExpiring(days: number): Promise<PurchaseContract[]> {
    const future = new Date();
    future.setDate(future.getDate() + days);
    return (await this.prisma.purPurchaseContract.findMany({ where: { status: "active" as any, endDate: { lte: future } }, orderBy: { endDate: "asc" } })).map(r => PurchaseContract.load({ ...r, totalValue: toNumber(r.totalValue), amountSpent: toNumber(r.amountSpent), amountRemaining: toNumber(r.amountRemaining) } as any));
  }
}

// ─── Goods Receipt Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaGoodsReceiptRepository implements GoodsReceiptRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(gr: GoodsReceipt): Promise<void> {
    const s = gr.toState();
    const data: any = { ...s, totalAmount: toBigInt(s.totalAmount) };
    await this.prisma.purGoodsReceipt.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: GoodsReceiptId): Promise<GoodsReceipt | null> {
    const row = await this.prisma.purGoodsReceipt.findUnique({ where: { id: id.value } });
    return row ? GoodsReceipt.load({ ...row, totalAmount: toNumber(row.totalAmount) } as any) : null;
  }

  async findByReceiptNumber(number: string): Promise<GoodsReceipt | null> {
    const row = await this.prisma.purGoodsReceipt.findUnique({ where: { receiptNumber: number } });
    return row ? GoodsReceipt.load({ ...row, totalAmount: toNumber(row.totalAmount) } as any) : null;
  }

  async findByPoId(poId: string): Promise<GoodsReceipt[]> {
    return (await this.prisma.purGoodsReceipt.findMany({ where: { poId }, orderBy: { receiptDate: "desc" } })).map(r => GoodsReceipt.load({ ...r, totalAmount: toNumber(r.totalAmount) } as any));
  }

  async findAll(): Promise<GoodsReceipt[]> {
    return (await this.prisma.purGoodsReceipt.findMany({ orderBy: { receiptDate: "desc" } })).map(r => GoodsReceipt.load({ ...r, totalAmount: toNumber(r.totalAmount) } as any));
  }

  async saveLine(line: ReceiptLine): Promise<void> {
    const s = line.toState();
    const data: any = { ...s, quantityOrdered: s.quantityOrdered, quantityReceived: s.quantityReceived, quantityAccepted: s.quantityAccepted, quantityRejected: s.quantityRejected, unitPrice: toBigInt(s.unitPrice), totalPrice: toBigInt(s.totalPrice) };
    await this.prisma.purReceiptLine.upsert({ where: { id: data.id }, create: data, update: data });
  }
}

// ─── Supplier Invoice Repository ─────────────────────────────────────────────────

@Injectable()
export class PrismaSupplierInvoiceRepository implements SupplierInvoiceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(inv: SupplierInvoice): Promise<void> {
    const s = inv.toState();
    const data: any = { ...s, totalAmount: toBigInt(s.totalAmount), totalTax: toBigInt(s.totalTax), grandTotal: toBigInt(s.grandTotal), amountPaid: toBigInt(s.amountPaid), amountDue: toBigInt(s.amountDue), exchangeRate: s.exchangeRate };
    await this.prisma.purSupplierInvoice.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: SupplierInvoiceId): Promise<SupplierInvoice | null> {
    const row = await this.prisma.purSupplierInvoice.findUnique({ where: { id: id.value } });
    return row ? SupplierInvoice.load({ ...row, totalAmount: toNumber(row.totalAmount), totalTax: toNumber(row.totalTax), grandTotal: toNumber(row.grandTotal), amountPaid: toNumber(row.amountPaid), amountDue: toNumber(row.amountDue), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findByInvoiceNumber(invoiceNumber: string): Promise<SupplierInvoice | null> {
    const row = await this.prisma.purSupplierInvoice.findUnique({ where: { invoiceNumber } });
    return row ? SupplierInvoice.load({ ...row, totalAmount: toNumber(row.totalAmount), totalTax: toNumber(row.totalTax), grandTotal: toNumber(row.grandTotal), amountPaid: toNumber(row.amountPaid), amountDue: toNumber(row.amountDue), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findAll(): Promise<SupplierInvoice[]> {
    return (await this.prisma.purSupplierInvoice.findMany({ orderBy: { createdAt: "desc" } })).map(r => SupplierInvoice.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), amountPaid: toNumber(r.amountPaid), amountDue: toNumber(r.amountDue), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findByStatus(status: string): Promise<SupplierInvoice[]> {
    return (await this.prisma.purSupplierInvoice.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => SupplierInvoice.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), amountPaid: toNumber(r.amountPaid), amountDue: toNumber(r.amountDue), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findByVendorId(vendorId: string): Promise<SupplierInvoice[]> {
    return (await this.prisma.purSupplierInvoice.findMany({ where: { vendorId }, orderBy: { createdAt: "desc" } })).map(r => SupplierInvoice.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), amountPaid: toNumber(r.amountPaid), amountDue: toNumber(r.amountDue), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findByPoId(poId: string): Promise<SupplierInvoice[]> {
    return (await this.prisma.purSupplierInvoice.findMany({ where: { poId }, orderBy: { createdAt: "desc" } })).map(r => SupplierInvoice.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), amountPaid: toNumber(r.amountPaid), amountDue: toNumber(r.amountDue), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findPending(): Promise<SupplierInvoice[]> {
    return (await this.prisma.purSupplierInvoice.findMany({ where: { status: { in: ["registered", "verified"] as any } }, orderBy: { dueDate: "asc" } })).map(r => SupplierInvoice.load({ ...r, totalAmount: toNumber(r.totalAmount), totalTax: toNumber(r.totalTax), grandTotal: toNumber(r.grandTotal), amountPaid: toNumber(r.amountPaid), amountDue: toNumber(r.amountDue), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async saveLine(line: InvoiceLine): Promise<void> {
    const s = line.toState();
    const data: any = { ...s, quantity: s.quantity, unitPrice: toBigInt(s.unitPrice), totalPrice: toBigInt(s.totalPrice), taxAmount: toBigInt(s.taxAmount), taxRate: s.taxRate, matchedQuantity: s.matchedQuantity, matchedAmount: toBigInt(s.matchedAmount) };
    await this.prisma.purInvoiceLine.upsert({ where: { id: data.id }, create: data, update: data });
  }
}

// ─── Import Declaration Repository ───────────────────────────────────────────────

@Injectable()
export class PrismaImportDeclarationRepository implements ImportDeclarationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(d: ImportDeclaration): Promise<void> {
    const s = d.toState();
    const data: any = { ...s, totalCifValue: toBigInt(s.totalCifValue), totalDutyAmount: toBigInt(s.totalDutyAmount), totalTaxAmount: toBigInt(s.totalTaxAmount), totalLandedCost: toBigInt(s.totalLandedCost), exchangeRate: s.exchangeRate };
    await this.prisma.purImportDeclaration.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: ImportDeclarationId): Promise<ImportDeclaration | null> {
    const row = await this.prisma.purImportDeclaration.findUnique({ where: { id: id.value } });
    return row ? ImportDeclaration.load({ ...row, totalCifValue: toNumber(row.totalCifValue), totalDutyAmount: toNumber(row.totalDutyAmount), totalTaxAmount: toNumber(row.totalTaxAmount), totalLandedCost: toNumber(row.totalLandedCost), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findByDeclarationNumber(number: string): Promise<ImportDeclaration | null> {
    const row = await this.prisma.purImportDeclaration.findUnique({ where: { declarationNumber: number } });
    return row ? ImportDeclaration.load({ ...row, totalCifValue: toNumber(row.totalCifValue), totalDutyAmount: toNumber(row.totalDutyAmount), totalTaxAmount: toNumber(row.totalTaxAmount), totalLandedCost: toNumber(row.totalLandedCost), exchangeRate: toNumber(row.exchangeRate) } as any) : null;
  }

  async findByPoId(poId: string): Promise<ImportDeclaration[]> {
    return (await this.prisma.purImportDeclaration.findMany({ where: { poId }, orderBy: { createdAt: "desc" } })).map(r => ImportDeclaration.load({ ...r, totalCifValue: toNumber(r.totalCifValue), totalDutyAmount: toNumber(r.totalDutyAmount), totalTaxAmount: toNumber(r.totalTaxAmount), totalLandedCost: toNumber(r.totalLandedCost), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async findAll(): Promise<ImportDeclaration[]> {
    return (await this.prisma.purImportDeclaration.findMany({ orderBy: { createdAt: "desc" } })).map(r => ImportDeclaration.load({ ...r, totalCifValue: toNumber(r.totalCifValue), totalDutyAmount: toNumber(r.totalDutyAmount), totalTaxAmount: toNumber(r.totalTaxAmount), totalLandedCost: toNumber(r.totalLandedCost), exchangeRate: toNumber(r.exchangeRate) } as any));
  }

  async saveLandedCost(lc: LandedCost): Promise<void> {
    const s = lc.toState();
    const data: any = { ...s, amount: toBigInt(s.amount) };
    await this.prisma.purLandedCost.upsert({ where: { id: data.id }, create: data, update: data });
  }
}
