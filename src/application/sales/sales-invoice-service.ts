import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { SalesInvoiceId, SalesOrderId, CustomerId } from "../../domain/sales/sales-ids.js";
import { SalesInvoice, InvoiceLine, type SalesInvoiceState } from "../../domain/sales/sales-invoice.js";
import { SlsInvoiceType, SlsInvoiceStatus } from "../../domain/sales/sales-enums.js";
import { OrderCanInvoiceSpec, DuplicateInvoiceSpec, InvoiceCanPostSpec } from "../../domain/sales/sales-specifications.js";
import { PrismaSalesInvoiceRepository, PrismaSalesOrderRepository, PrismaCustomerRepository } from "../../infrastructure/sales/sales-prisma-repos.js";
import { SalesOrderService } from "./sales-order-service.js";
import { ReceivableService } from "./sales-receivable-service.js";
import { SalesGlService } from "./sales-gl-service.js";

@Injectable()
export class SalesInvoiceService {
  constructor(
    private readonly invRepo: PrismaSalesInvoiceRepository,
    private readonly orderRepo: PrismaSalesOrderRepository,
    private readonly custRepo: PrismaCustomerRepository,
    private readonly orderService: SalesOrderService,
    private readonly receivableService: ReceivableService,
    private readonly glService: SalesGlService,
  ) {}

  async create(p: {
    invoiceNumber: string; companyId: string; customerId: string; customerName: string;
    branchId?: string; customerTaxCode?: string; customerAddress?: string;
    orderId?: string; orderNumber?: string;
    invoiceType?: SlsInvoiceType; currencyCode?: string; exchangeRate?: number;
    invoiceDate?: Date; notes?: string;
  }): Promise<SalesInvoice> {
    const existing = await this.invRepo.findByInvoiceNumber(p.invoiceNumber);
    if (existing) throw new DomainError("Conflict", `Invoice ${p.invoiceNumber} already exists`);
    const invoice = SalesInvoice.create(p);
    await this.invRepo.save(invoice);
    return invoice;
  }

  async createFromOrder(orderId: string, invoiceNumber: string, companyId: string): Promise<SalesInvoice> {
    const order = await this.orderService.getOrder(orderId);
    OrderCanInvoiceSpec.check(order.status, order["_orderNumber"]);
    const invoice = SalesInvoice.create({
      invoiceNumber, companyId, customerId: order["_customerId"],
      customerName: order["_customerName"], customerTaxCode: order["_customerTaxCode"] ?? undefined,
      customerAddress: order["_customerAddress"] ?? undefined, branchId: order["_branchId"] ?? undefined,
      orderId: order.id.value, orderNumber: order["_orderNumber"],
      currencyCode: order["_currencyCode"], exchangeRate: order["_exchangeRate"],
    });
    for (const ol of order["_lines"]) {
      if (ol["_deliveredQuantity"] <= ol["_invoicedQuantity"]) continue;
      const qtyToInvoice = ol["_deliveredQuantity"] - ol["_invoicedQuantity"];
      const line = InvoiceLine.create({
        invoiceId: invoice.id.value, lineNumber: ol["_lineNumber"],
        itemId: ol["_itemId"] ?? undefined, itemCode: ol["_itemCode"], itemName: ol["_itemName"],
        description: ol["_description"] ?? undefined, quantity: qtyToInvoice, uom: ol["_uom"],
        unitPrice: ol["_unitPrice"], orderLineId: ol.id.value,
        taxCode: ol["_taxCode"] ?? undefined, taxRate: ol["_taxRate"],
        discountPercent: ol["_discountPercent"], discountAmount: Math.round(ol["_discountAmount"] * qtyToInvoice / ol["_quantity"]),
        warehouseId: ol["_warehouseId"] ?? undefined, projectId: ol["_projectId"] ?? undefined,
        costCenterId: ol["_costCenterId"] ?? undefined, departmentId: ol["_departmentId"] ?? undefined,
      });
      invoice.addLine(line);
      ol.recordInvoice(qtyToInvoice);
      await this.invRepo.saveLine(line);
    }
    await this.invRepo.save(invoice);
    order.updateInvoiceStatus();
    await this.orderRepo.save(order);
    return invoice;
  }

  async addLine(invoiceId: string, line: InvoiceLine): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    invoice.addLine(line);
    await this.invRepo.saveLine(line);
    await this.invRepo.save(invoice);
    return invoice;
  }

  async getInvoice(id: string): Promise<SalesInvoice> {
    const invoice = await this.invRepo.findById(SalesInvoiceId.from(id));
    if (!invoice) throw new DomainError("NotFound", "Invoice not found");
    return invoice;
  }

  async findByInvoiceNumber(invoiceNumber: string): Promise<SalesInvoice | null> {
    return this.invRepo.findByInvoiceNumber(invoiceNumber);
  }

  async findByOrder(orderId: string): Promise<SalesInvoiceState[]> {
    return this.invRepo.findByOrderId(orderId);
  }

  async findByCustomer(customerId: string): Promise<SalesInvoiceState[]> {
    return this.invRepo.findByCustomerId(customerId);
  }

  async findByStatus(status: string): Promise<SalesInvoiceState[]> {
    return this.invRepo.findByStatus(status);
  }

  async approve(invoiceId: string, approvedBy: string): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    invoice.approve(approvedBy);
    await this.invRepo.save(invoice);
    return invoice;
  }

  async post(invoiceId: string, postedById: string, dueDays?: number): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    InvoiceCanPostSpec.check(invoice.status, invoice["_invoiceNumber"]);
    invoice.post(postedById);
    await this.invRepo.save(invoice);
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + (dueDays ?? 30));
    await this.glService.postInvoiceGl(invoice, postedById).catch((err) => {
      throw new DomainError("Infrastructure", `GL posting failed: ${err.message}`);
    });
    await this.receivableService.createReceivable(
      invoice["_customerId"], invoice.id.value, invoice["_invoiceNumber"],
      invoice["_companyId"], invoice.grandTotal, dueDate, invoice["_branchId"] ?? undefined,
    );
    return invoice;
  }

  async cancel(invoiceId: string, reason: string): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    invoice.cancel(reason);
    await this.invRepo.save(invoice);
    return invoice;
  }

  async createCreditNote(invoiceId: string, creditNoteNumber: string, reason: string): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    const cn = invoice.createCreditNote(creditNoteNumber, reason);
    for (const l of invoice["_lines"]) {
      const cnLine = InvoiceLine.create({
        invoiceId: cn.id.value, lineNumber: l["_lineNumber"],
        itemId: l["_itemId"] ?? undefined, itemCode: l["_itemCode"], itemName: l["_itemName"],
        quantity: l["_quantity"], uom: l["_uom"], unitPrice: l["_unitPrice"],
        taxCode: l["_taxCode"] ?? undefined, taxRate: l["_taxRate"],
        discountPercent: l["_discountPercent"], discountAmount: l["_discountAmount"],
        orderLineId: l["_orderLineId"] ?? undefined,
      });
      cn.addLine(cnLine);
      await this.invRepo.saveLine(cnLine);
    }
    await this.invRepo.save(cn);
    await this.invRepo.save(invoice);
    return cn;
  }

  async updateEinvoice(invoiceId: string, einvoiceNumber: string, einvoiceCode: string, verifyCode: string, issueDate: Date): Promise<SalesInvoice> {
    const invoice = await this.getInvoice(invoiceId);
    invoice.updateEinvoiceInfo(einvoiceNumber, einvoiceCode, verifyCode, issueDate);
    await this.invRepo.save(invoice);
    return invoice;
  }
}
