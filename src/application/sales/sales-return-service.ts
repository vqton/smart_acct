import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { SalesReturnId, SalesOrderId, SalesInvoiceId, CustomerId } from "../../domain/sales/sales-ids.js";
import { SalesReturn, ReturnLine, type SalesReturnState } from "../../domain/sales/sales-return.js";
import { SlsReturnReason, SlsReturnStatus } from "../../domain/sales/sales-enums.js";
import { OrderCanReturnSpec, ReturnQuantitySpec } from "../../domain/sales/sales-specifications.js";
import { PrismaSalesReturnRepository, PrismaSalesOrderRepository, PrismaSalesInvoiceRepository, PrismaCustomerRepository } from "../../infrastructure/sales/sales-prisma-repos.js";
import { SalesOrderService } from "./sales-order-service.js";

@Injectable()
export class SalesReturnService {
  constructor(
    private readonly retRepo: PrismaSalesReturnRepository,
    private readonly orderRepo: PrismaSalesOrderRepository,
    private readonly invRepo: PrismaSalesInvoiceRepository,
    private readonly custRepo: PrismaCustomerRepository,
    private readonly orderService: SalesOrderService,
  ) {}

  async create(p: {
    returnNumber: string; companyId: string; customerId: string; customerName: string;
    branchId?: string; orderId?: string; orderNumber?: string;
    invoiceId?: string; invoiceNumber?: string;
    returnReason: SlsReturnReason; reasonDetail?: string;
    returnType?: string; notes?: string;
  }): Promise<SalesReturn> {
    const existing = await this.retRepo.findByReturnNumber(p.returnNumber);
    if (existing) throw new DomainError("Conflict", `Return ${p.returnNumber} already exists`);
    const ret = SalesReturn.create(p);
    await this.retRepo.save(ret);
    return ret;
  }

  async createFromOrder(orderId: string, returnNumber: string, companyId: string, returnReason: SlsReturnReason, reasonDetail?: string): Promise<SalesReturn> {
    const order = await this.orderService.getOrder(orderId);
    OrderCanReturnSpec.check(order.status, order["_orderNumber"]);
    const ret = SalesReturn.create({
      returnNumber, companyId, customerId: order["_customerId"],
      customerName: order["_customerName"], branchId: order["_branchId"] ?? undefined,
      orderId: order.id.value, orderNumber: order["_orderNumber"],
      returnReason, reasonDetail,
    });
    for (const ol of order["_lines"]) {
      if (ol["_returnedQuantity"] >= ol["_deliveredQuantity"]) continue;
      const qtyCanReturn = ol["_deliveredQuantity"] - ol["_returnedQuantity"];
      const rl = ReturnLine.create({
        returnId: ret.id.value, lineNumber: ol["_lineNumber"],
        itemId: ol["_itemId"] ?? undefined, itemCode: ol["_itemCode"], itemName: ol["_itemName"],
        quantityReturned: qtyCanReturn, uom: ol["_uom"], unitPrice: ol["_unitPrice"],
        orderLineId: ol.id.value,
        taxCode: ol["_taxCode"] ?? undefined, taxRate: ol["_taxRate"],
        discountPercent: ol["_discountPercent"],
        discountAmount: Math.round(ol["_discountAmount"] * qtyCanReturn / ol["_quantity"]),
        warehouseId: ol["_warehouseId"] ?? undefined,
      });
      ret.addLine(rl);
      ol.recordReturn(qtyCanReturn);
      await this.retRepo.saveLine(rl);
    }
    await this.retRepo.save(ret);
    order.updateDeliveryStatus();
    await this.orderRepo.save(order);
    return ret;
  }

  async addLine(returnId: string, line: ReturnLine): Promise<SalesReturn> {
    const ret = await this.getReturn(returnId);
    ret.addLine(line);
    await this.retRepo.saveLine(line);
    await this.retRepo.save(ret);
    return ret;
  }

  async getReturn(id: string): Promise<SalesReturn> {
    const ret = await this.retRepo.findById(SalesReturnId.from(id));
    if (!ret) throw new DomainError("NotFound", "Return not found");
    return ret;
  }

  async findByReturnNumber(returnNumber: string): Promise<SalesReturn | null> {
    return this.retRepo.findByReturnNumber(returnNumber);
  }

  async findByCustomer(customerId: string): Promise<SalesReturnState[]> {
    return this.retRepo.findByCustomerId(customerId);
  }

  async findByStatus(status: string): Promise<SalesReturnState[]> {
    return this.retRepo.findByStatus(status);
  }

  async submit(id: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.submitForApproval();
    await this.retRepo.save(ret);
    return ret;
  }

  async approve(id: string, approvedBy: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.approve(approvedBy);
    await this.retRepo.save(ret);
    return ret;
  }

  async recordReceipt(id: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.recordReceipt();
    await this.retRepo.save(ret);
    return ret;
  }

  async recordInspection(id: string, result: string, notes?: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.recordInspection(result, notes);
    await this.retRepo.save(ret);
    return ret;
  }

  async complete(id: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.complete();
    await this.retRepo.save(ret);
    return ret;
  }

  async cancel(id: string): Promise<SalesReturn> {
    const ret = await this.getReturn(id);
    ret.cancel();
    await this.retRepo.save(ret);
    return ret;
  }
}
