import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { SalesOrderId, QuotationId, OrderLineId, CustomerId } from "../../domain/sales/sales-ids.js";
import { SalesOrder, OrderLine, type SalesOrderState } from "../../domain/sales/sales-order.js";
import { Quotation, QuotationLine } from "../../domain/sales/sales-quotation.js";
import { SlsOrderStatus, SlsOrderType, SlsOrderSource, SlsPaymentMethod, SlsPaymentStatus } from "../../domain/sales/sales-enums.js";
import { PrismaSalesOrderRepository, PrismaCustomerRepository, PrismaQuotationRepository } from "../../infrastructure/sales/sales-prisma-repos.js";
import { SalesCustomerService } from "./sales-customer-service.js";

@Injectable()
export class SalesOrderService {
  constructor(
    private readonly orderRepo: PrismaSalesOrderRepository,
    private readonly custRepo: PrismaCustomerRepository,
    private readonly custService: SalesCustomerService,
    private readonly qtnRepo: PrismaQuotationRepository,
  ) {}

  async create(p: {
    orderNumber: string; companyId: string; customerId: string; customerName: string;
    branchId?: string; storeId?: string; salespersonId?: string;
    customerTaxCode?: string; customerAddress?: string; customerPhone?: string; customerEmail?: string;
    orderType?: SlsOrderType; orderSource?: SlsOrderSource;
    currencyCode?: string; exchangeRate?: number;
    deliveryAddress?: string; deliveryWard?: string; deliveryDistrict?: string;
    deliveryProvince?: string; deliveryContact?: string; deliveryPhone?: string;
    paymentTermCode?: string; paymentMethod?: SlsPaymentMethod;
    notes?: string; internalNotes?: string;
    quotationId?: string; quotationNumber?: string;
  }): Promise<SalesOrder> {
    const existing = await this.orderRepo.findByOrderNumber(p.orderNumber);
    if (existing) throw new DomainError("Conflict", `Order ${p.orderNumber} already exists`);
    const customer = await this.custService.checkActive(CustomerId.from(p.customerId));
    const order = SalesOrder.create(p);
    if (p.quotationId && p.quotationNumber) {
      order["_quotationId"] = p.quotationId;
      order["_quotationNumber"] = p.quotationNumber;
    }
    await this.orderRepo.save(order);
    return order;
  }

  async addLine(orderId: string, line: OrderLine): Promise<SalesOrder> {
    const order = await this.getOrder(orderId);
    order.addLine(line);
    await this.orderRepo.saveLine(line);
    await this.orderRepo.save(order);
    return order;
  }

  async createLine(p: {
    orderId: string; lineNumber: number; itemCode: string; itemName: string;
    quantity: number; uom: string; unitPrice: number;
    itemId?: string; description?: string; taxCode?: string; taxRate?: number;
    discountPercent?: number; discountAmount?: number; unitCost?: number;
    warehouseId?: string; projectId?: string; costCenterId?: string; departmentId?: string;
    expectedDate?: Date; promisedDate?: Date;
  }): Promise<OrderLine> {
    return OrderLine.create(p);
  }

  async fromQuotation(quotationId: string, orderNumber: string, companyId: string, orderDate?: Date): Promise<SalesOrder> {
    const qtn = await this.qtnRepo.findById(QuotationId.from(quotationId));
    if (!qtn) throw new DomainError("NotFound", "Quotation not found");
    if (qtn.status !== "accepted") throw new DomainError("BusinessRule", "Quotation must be accepted to convert");
    const order = SalesOrder.create({
      orderNumber, companyId, customerId: qtn["_customerId"], customerName: qtn["_customerName"],
      customerTaxCode: qtn["_customerTaxCode"] ?? undefined, branchId: qtn["_branchId"] ?? undefined,
      storeId: qtn["_storeId"] ?? undefined, salespersonId: qtn["_salespersonId"] ?? undefined,
      orderSource: qtn["_orderSource"], currencyCode: qtn["_currencyCode"],
      exchangeRate: qtn["_exchangeRate"],
      quotationId: qtn.id.value, quotationNumber: qtn["_quotationNumber"],
      notes: qtn["_notes"] ?? undefined,
    });
    for (const ql of qtn["_lines"]) {
      const line = OrderLine.create({
        orderId: order.id.value, lineNumber: ql["_lineNumber"],
        itemId: ql["_itemId"] ?? undefined, itemCode: ql["_itemCode"], itemName: ql["_itemName"],
        description: ql["_description"] ?? undefined, quantity: ql["_quantity"], uom: ql["_uom"],
        unitPrice: ql["_unitPrice"], taxCode: ql["_taxCode"] ?? undefined, taxRate: ql["_taxRate"],
        discountPercent: ql["_discountPercent"], discountAmount: ql["_discountAmount"],
        warehouseId: ql["_warehouseId"] ?? undefined, expectedDate: ql["_expectedDate"] ?? undefined,
      });
      order.addLine(line);
      await this.orderRepo.saveLine(line);
    }
    await this.orderRepo.save(order);
    qtn.markConverted(order.id.value);
    await this.qtnRepo.save(qtn);
    return order;
  }

  async getOrder(id: string): Promise<SalesOrder> {
    const order = await this.orderRepo.findById(SalesOrderId.from(id));
    if (!order) throw new DomainError("NotFound", "Order not found");
    return order;
  }

  async getByOrderNumber(orderNumber: string): Promise<SalesOrder | null> {
    return this.orderRepo.findByOrderNumber(orderNumber);
  }

  async findByCustomer(customerId: string): Promise<SalesOrderState[]> {
    return this.orderRepo.findByCustomerId(customerId);
  }

  async findByStatus(status: string): Promise<SalesOrderState[]> {
    return this.orderRepo.findByStatus(status);
  }

  async findOpen(): Promise<SalesOrderState[]> {
    return this.orderRepo.findOpen();
  }

  async submit(id: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.submitForApproval();
    await this.orderRepo.save(order);
    return order;
  }

  async approve(id: string, approvedBy: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    const customer = await this.custRepo.findById(CustomerId.from(order["_customerId"]));
    if (customer && customer.creditLimit > 0 && customer.creditLimit - customer.creditUsed < order.grandTotal) {
      throw new DomainError("BusinessRule", `Customer ${customer.code} credit limit exceeded`);
    }
    order.approve(approvedBy);
    await this.orderRepo.save(order);
    return order;
  }

  async confirm(id: string, confirmedBy: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.confirm(confirmedBy);
    await this.orderRepo.save(order);
    return order;
  }

  async cancel(id: string, reason: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.cancel(reason);
    await this.orderRepo.save(order);
    return order;
  }

  async hold(id: string, reason: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.hold(reason);
    await this.orderRepo.save(order);
    return order;
  }

  async releaseHold(id: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.releaseHold();
    await this.orderRepo.save(order);
    return order;
  }

  async startProcessing(id: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.startProcessing();
    await this.orderRepo.save(order);
    return order;
  }

  async complete(id: string): Promise<SalesOrder> {
    const order = await this.getOrder(id);
    order.markCompleted();
    await this.orderRepo.save(order);
    return order;
  }
}
