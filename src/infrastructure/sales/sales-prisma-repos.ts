import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { CustomerId, QuotationId, SalesOrderId, DeliveryOrderId, SalesInvoiceId, SalesReturnId, CustomerReceiptId, ReceivableAccountId } from "../../domain/sales/sales-ids.js";
import { Customer, type CustomerState } from "../../domain/sales/sales-customer.js";
import { Quotation, QuotationLine, type QuotationState, type QuotationLineState } from "../../domain/sales/sales-quotation.js";
import { SalesOrder, OrderLine, type SalesOrderState, type OrderLineState } from "../../domain/sales/sales-order.js";
import { DeliveryOrder, DeliveryLine, type DeliveryOrderState, type DeliveryLineState } from "../../domain/sales/sales-delivery.js";
import { SalesInvoice, InvoiceLine, type SalesInvoiceState, type InvoiceLineState } from "../../domain/sales/sales-invoice.js";
import { SalesReturn, ReturnLine, type SalesReturnState, type ReturnLineState } from "../../domain/sales/sales-return.js";
import { CustomerReceipt, ReceiptAllocation, type CustomerReceiptState, type ReceiptAllocationState } from "../../domain/sales/sales-payment.js";
import { ReceivableAccount, type ReceivableAccountState } from "../../domain/sales/sales-receivable.js";
import type { CustomerRepository, QuotationRepository, SalesOrderRepository, DeliveryOrderRepository, SalesInvoiceRepository, SalesReturnRepository, CustomerReceiptRepository, ReceivableAccountRepository } from "../../domain/sales/sales-repositories.js";

function toNumber(val: any, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  if (typeof val === "number") return val;
  if (typeof val === "object" && "toString" in val) return parseFloat(val.toString());
  return Number(val);
}

function toBigInt(val: number): bigint { return BigInt(Math.round(val)); }

// ─── Customer Repository ─────────────────────────────────────────────────────────

@Injectable()
export class PrismaCustomerRepository implements CustomerRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(customer: Customer): Promise<void> {
    const s = customer.toState();
    const data: any = { ...s };
    await this.prisma.slsCustomer.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: CustomerId): Promise<Customer | null> {
    const row = await this.prisma.slsCustomer.findUnique({ where: { id: id.value } });
    return row ? Customer.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Customer | null> {
    const row = await this.prisma.slsCustomer.findUnique({ where: { code } });
    return row ? Customer.load(row as any) : null;
  }

  async findByTaxCode(taxCode: string): Promise<Customer | null> {
    const row = await this.prisma.slsCustomer.findFirst({ where: { taxCode } });
    return row ? Customer.load(row as any) : null;
  }

  async findAll(): Promise<CustomerState[]> {
    return (await this.prisma.slsCustomer.findMany({ orderBy: { code: "asc" } })) as any;
  }

  async search(criteria: Partial<{ code: string; name: string; taxCode: string; status: string; phone: string; email: string }>): Promise<CustomerState[]> {
    const where: any = {};
    if (criteria.code) where.code = { contains: criteria.code };
    if (criteria.name) where.name = { contains: criteria.name };
    if (criteria.taxCode) where.taxCode = { contains: criteria.taxCode };
    if (criteria.status) where.status = criteria.status;
    if (criteria.phone) where.phone = { contains: criteria.phone };
    if (criteria.email) where.email = { contains: criteria.email };
    return (await this.prisma.slsCustomer.findMany({ where, orderBy: { code: "asc" } })) as any;
  }
}

// ─── Quotation Repository ─────────────────────────────────────────────────────────

@Injectable()
export class PrismaQuotationRepository implements QuotationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(q: Quotation): Promise<void> {
    const s = q.toState();
    await this.prisma.slsQuotation.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: QuotationId): Promise<Quotation | null> {
    const row = await this.prisma.slsQuotation.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    const q = Quotation.load(row as any);
    if (row.lines) q["_lines"] = row.lines.map((l: any) => QuotationLine.load(l as QuotationLineState));
    return q;
  }

  async findByQuotationNumber(number: string): Promise<Quotation | null> {
    const row = await this.prisma.slsQuotation.findUnique({ where: { quotationNumber: number }, include: { lines: true } });
    if (!row) return null;
    const q = Quotation.load(row as any);
    if (row.lines) q["_lines"] = row.lines.map((l: any) => QuotationLine.load(l as QuotationLineState));
    return q;
  }

  async findByCustomerId(customerId: string): Promise<QuotationState[]> {
    return (await this.prisma.slsQuotation.findMany({ where: { customerId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findOpen(): Promise<QuotationState[]> {
    return (await this.prisma.slsQuotation.findMany({ where: { status: { in: ["draft", "sent"] } }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findExpired(): Promise<QuotationState[]> {
    return (await this.prisma.slsQuotation.findMany({ where: { status: "sent", validUntil: { lt: new Date() } } })) as any;
  }

  async saveLine(line: QuotationLine): Promise<void> {
    const s = line.toState();
    await this.prisma.slsQuotationLine.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Sales Order Repository ───────────────────────────────────────────────────────

@Injectable()
export class PrismaSalesOrderRepository implements SalesOrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(order: SalesOrder): Promise<void> {
    const s = order.toState();
    await this.prisma.slsSalesOrder.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: SalesOrderId): Promise<SalesOrder | null> {
    const row = await this.prisma.slsSalesOrder.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    const o = SalesOrder.load(row as any);
    if (row.lines) o["_lines"] = row.lines.map((l: any) => OrderLine.load(l as OrderLineState));
    return o;
  }

  async findByOrderNumber(orderNumber: string): Promise<SalesOrder | null> {
    const row = await this.prisma.slsSalesOrder.findUnique({ where: { orderNumber }, include: { lines: true } });
    if (!row) return null;
    const o = SalesOrder.load(row as any);
    if (row.lines) o["_lines"] = row.lines.map((l: any) => OrderLine.load(l as OrderLineState));
    return o;
  }

  async findByCustomerId(customerId: string): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { customerId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByStatus(status: string): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findOpen(): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { status: { notIn: ["cancelled", "completed"] } }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByStoreId(storeId: string): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { storeId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findBySalespersonId(salespersonId: string): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { salespersonId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByDateRange(from: Date, to: Date): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { orderDate: { gte: from, lte: to } }, orderBy: { orderDate: "asc" } })) as any;
  }

  async findBySourceDocument(sourceType: string, sourceId: string): Promise<SalesOrderState[]> {
    return (await this.prisma.slsSalesOrder.findMany({ where: { sourceOrderId: sourceId } })) as any;
  }

  async saveLine(line: OrderLine): Promise<void> {
    const s = line.toState();
    await this.prisma.slsOrderLine.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Delivery Repository ──────────────────────────────────────────────────────────

@Injectable()
export class PrismaDeliveryOrderRepository implements DeliveryOrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(delivery: DeliveryOrder): Promise<void> {
    const s = delivery.toState();
    await this.prisma.slsDeliveryOrder.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: DeliveryOrderId): Promise<DeliveryOrder | null> {
    const row = await this.prisma.slsDeliveryOrder.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    const d = DeliveryOrder.load(row as any);
    if (row.lines) d["_lines"] = row.lines.map((l: any) => DeliveryLine.load(l as DeliveryLineState));
    return d;
  }

  async findByDeliveryNumber(number: string): Promise<DeliveryOrder | null> {
    const row = await this.prisma.slsDeliveryOrder.findUnique({ where: { deliveryNumber: number }, include: { lines: true } });
    if (!row) return null;
    const d = DeliveryOrder.load(row as any);
    if (row.lines) d["_lines"] = row.lines.map((l: any) => DeliveryLine.load(l as DeliveryLineState));
    return d;
  }

  async findByOrderId(orderId: string): Promise<DeliveryOrderState[]> {
    return (await this.prisma.slsDeliveryOrder.findMany({ where: { orderId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByStatus(status: string): Promise<DeliveryOrderState[]> {
    return (await this.prisma.slsDeliveryOrder.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })) as any;
  }

  async saveLine(line: DeliveryLine): Promise<void> {
    const s = line.toState();
    await this.prisma.slsDeliveryLine.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Invoice Repository ───────────────────────────────────────────────────────────

@Injectable()
export class PrismaSalesInvoiceRepository implements SalesInvoiceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(invoice: SalesInvoice): Promise<void> {
    const s = invoice.toState();
    await this.prisma.slsSalesInvoice.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: SalesInvoiceId): Promise<SalesInvoice | null> {
    const row = await this.prisma.slsSalesInvoice.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    const i = SalesInvoice.load(row as any);
    if (row.lines) i["_lines"] = row.lines.map((l: any) => InvoiceLine.load(l as InvoiceLineState));
    return i;
  }

  async findByInvoiceNumber(invoiceNumber: string): Promise<SalesInvoice | null> {
    const row = await this.prisma.slsSalesInvoice.findUnique({ where: { invoiceNumber }, include: { lines: true } });
    if (!row) return null;
    const i = SalesInvoice.load(row as any);
    if (row.lines) i["_lines"] = row.lines.map((l: any) => InvoiceLine.load(l as InvoiceLineState));
    return i;
  }

  async findByCustomerId(customerId: string): Promise<SalesInvoiceState[]> {
    return (await this.prisma.slsSalesInvoice.findMany({ where: { customerId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByOrderId(orderId: string): Promise<SalesInvoiceState[]> {
    return (await this.prisma.slsSalesInvoice.findMany({ where: { orderId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByStatus(status: string): Promise<SalesInvoiceState[]> {
    return (await this.prisma.slsSalesInvoice.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findPending(): Promise<SalesInvoiceState[]> {
    return (await this.prisma.slsSalesInvoice.findMany({ where: { status: { in: ["draft", "issued"] } }, orderBy: { createdAt: "asc" } })) as any;
  }

  async saveLine(line: InvoiceLine): Promise<void> {
    const s = line.toState();
    await this.prisma.slsInvoiceLine.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Return Repository ────────────────────────────────────────────────────────────

@Injectable()
export class PrismaSalesReturnRepository implements SalesReturnRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(ret: SalesReturn): Promise<void> {
    const s = ret.toState();
    await this.prisma.slsSalesReturn.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: SalesReturnId): Promise<SalesReturn | null> {
    const row = await this.prisma.slsSalesReturn.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    const r = SalesReturn.load(row as any);
    if (row.lines) r["_lines"] = row.lines.map((l: any) => ReturnLine.load(l as ReturnLineState));
    return r;
  }

  async findByReturnNumber(returnNumber: string): Promise<SalesReturn | null> {
    const row = await this.prisma.slsSalesReturn.findUnique({ where: { returnNumber }, include: { lines: true } });
    if (!row) return null;
    const r = SalesReturn.load(row as any);
    if (row.lines) r["_lines"] = row.lines.map((l: any) => ReturnLine.load(l as ReturnLineState));
    return r;
  }

  async findByCustomerId(customerId: string): Promise<SalesReturnState[]> {
    return (await this.prisma.slsSalesReturn.findMany({ where: { customerId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByOrderId(orderId: string): Promise<SalesReturnState[]> {
    return (await this.prisma.slsSalesReturn.findMany({ where: { orderId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByInvoiceId(invoiceId: string): Promise<SalesReturnState[]> {
    return (await this.prisma.slsSalesReturn.findMany({ where: { invoiceId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByStatus(status: string): Promise<SalesReturnState[]> {
    return (await this.prisma.slsSalesReturn.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })) as any;
  }

  async saveLine(line: ReturnLine): Promise<void> {
    const s = line.toState();
    await this.prisma.slsReturnLine.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Customer Receipt Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaCustomerReceiptRepository implements CustomerReceiptRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(receipt: CustomerReceipt): Promise<void> {
    const s = receipt.toState();
    await this.prisma.slsCustomerReceipt.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: CustomerReceiptId): Promise<CustomerReceipt | null> {
    const row = await this.prisma.slsCustomerReceipt.findUnique({ where: { id: id.value }, include: { allocations: true } });
    if (!row) return null;
    const r = CustomerReceipt.load(row as any);
    if (row.allocations) r["_allocations"] = row.allocations.map((a: any) => ReceiptAllocation.load(a as ReceiptAllocationState));
    return r;
  }

  async findByReceiptNumber(number: string): Promise<CustomerReceipt | null> {
    const row = await this.prisma.slsCustomerReceipt.findUnique({ where: { receiptNumber: number }, include: { allocations: true } });
    if (!row) return null;
    const r = CustomerReceipt.load(row as any);
    if (row.allocations) r["_allocations"] = row.allocations.map((a: any) => ReceiptAllocation.load(a as ReceiptAllocationState));
    return r;
  }

  async findByCustomerId(customerId: string): Promise<CustomerReceiptState[]> {
    return (await this.prisma.slsCustomerReceipt.findMany({ where: { customerId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByInvoiceId(invoiceId: string): Promise<CustomerReceiptState[]> {
    return (await this.prisma.slsCustomerReceipt.findMany({ where: { invoiceId }, orderBy: { createdAt: "desc" } })) as any;
  }

  async findByDateRange(from: Date, to: Date): Promise<CustomerReceiptState[]> {
    return (await this.prisma.slsCustomerReceipt.findMany({ where: { paymentDate: { gte: from, lte: to } }, orderBy: { paymentDate: "asc" } })) as any;
  }

  async saveAllocation(allocation: ReceiptAllocation): Promise<void> {
    const s = allocation.toState();
    await this.prisma.slsReceiptAllocation.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }
}

// ─── Receivable Account Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaReceivableAccountRepository implements ReceivableAccountRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(account: ReceivableAccount): Promise<void> {
    const s = account.toState();
    await this.prisma.slsReceivableAccount.upsert({ where: { id: s.id }, create: s as any, update: s as any });
  }

  async findById(id: ReceivableAccountId): Promise<ReceivableAccount | null> {
    const row = await this.prisma.slsReceivableAccount.findUnique({ where: { id: id.value } });
    return row ? ReceivableAccount.load(row as any) : null;
  }

  async findByCustomerId(customerId: string): Promise<ReceivableAccountState[]> {
    return (await this.prisma.slsReceivableAccount.findMany({ where: { customerId }, orderBy: { dueDate: "asc" } })) as any;
  }

  async findByInvoiceId(invoiceId: string): Promise<ReceivableAccountState[]> {
    return (await this.prisma.slsReceivableAccount.findMany({ where: { invoiceId } })) as any;
  }

  async findOverdue(): Promise<ReceivableAccountState[]> {
    return (await this.prisma.slsReceivableAccount.findMany({ where: { isOverdue: true, status: { notIn: ["paid", "written_off"] } }, orderBy: { dueDate: "asc" } })) as any;
  }

  async findByAgingBucket(bucket: string): Promise<ReceivableAccountState[]> {
    return (await this.prisma.slsReceivableAccount.findMany({ where: { agingBucket: bucket, status: { notIn: ["paid", "written_off"] } }, orderBy: { dueDate: "asc" } })) as any;
  }
}
