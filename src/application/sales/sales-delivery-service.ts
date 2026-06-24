import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { DeliveryOrderId, SalesOrderId } from "../../domain/sales/sales-ids.js";
import { DeliveryOrder, DeliveryLine, type DeliveryOrderState } from "../../domain/sales/sales-delivery.js";
import { SlsDeliveryStatus } from "../../domain/sales/sales-enums.js";
import { OrderCanDeliverSpec } from "../../domain/sales/sales-specifications.js";
import { PrismaDeliveryOrderRepository, PrismaSalesOrderRepository } from "../../infrastructure/sales/sales-prisma-repos.js";
import { SalesOrderService } from "./sales-order-service.js";

@Injectable()
export class SalesDeliveryService {
  constructor(
    private readonly delRepo: PrismaDeliveryOrderRepository,
    private readonly orderRepo: PrismaSalesOrderRepository,
    private readonly orderService: SalesOrderService,
  ) {}

  async create(p: {
    deliveryNumber: string; companyId: string; orderId: string; orderNumber: string;
    customerId: string; customerName: string;
    branchId?: string; deliveryAddress?: string; deliveryWard?: string;
    deliveryDistrict?: string; deliveryProvince?: string;
    deliveryContact?: string; deliveryPhone?: string;
    deliveryType?: string; deliveryDate?: Date;
    carrierId?: string; carrierName?: string; trackingNumber?: string;
    shipmentMethod?: string; notes?: string;
  }): Promise<DeliveryOrder> {
    const existing = await this.delRepo.findByDeliveryNumber(p.deliveryNumber);
    if (existing) throw new DomainError("Conflict", `Delivery ${p.deliveryNumber} already exists`);
    const order = await this.orderService.getOrder(p.orderId);
    OrderCanDeliverSpec.check(order.status, order["_orderNumber"]);
    const delivery = DeliveryOrder.create(p);
    await this.delRepo.save(delivery);
    return delivery;
  }

  async addLine(deliveryId: string, line: DeliveryLine): Promise<DeliveryOrder> {
    const delivery = await this.getDelivery(deliveryId);
    delivery.addLine(line);
    await this.delRepo.saveLine(line);
    await this.delRepo.save(delivery);
    return delivery;
  }

  async createLine(p: {
    deliveryId: string; lineNumber: number; itemCode: string; itemName: string;
    quantityDelivered: number; uom: string; unitPrice: number;
    orderLineId?: string; itemId?: string; batchNumber?: string;
    serialNumber?: string; expiryDate?: Date; warehouseId?: string; notes?: string;
  }): Promise<DeliveryLine> {
    return DeliveryLine.create(p);
  }

  async createFromOrder(orderId: string, deliveryNumber: string, companyId: string): Promise<DeliveryOrder> {
    const order = await this.orderService.getOrder(orderId);
    OrderCanDeliverSpec.check(order.status, order["_orderNumber"]);
    const delivery = DeliveryOrder.create({
      deliveryNumber, companyId, orderId: order.id.value,
      orderNumber: order["_orderNumber"],
      customerId: order["_customerId"], customerName: order["_customerName"],
      branchId: order["_branchId"] ?? undefined,
      deliveryAddress: order["_deliveryAddress"] ?? undefined, deliveryWard: order["_deliveryWard"] ?? undefined,
      deliveryDistrict: order["_deliveryDistrict"] ?? undefined, deliveryProvince: order["_deliveryProvince"] ?? undefined,
      deliveryContact: order["_deliveryContact"] ?? undefined, deliveryPhone: order["_deliveryPhone"] ?? undefined,
    });
    for (const ol of order["_lines"]) {
      if (ol.remainingToDeliver <= 0) continue;
      const qtyToDeliver = ol.remainingToDeliver;
      const dl = DeliveryLine.create({
        deliveryId: delivery.id.value, lineNumber: ol["_lineNumber"],
        itemId: ol["_itemId"] ?? undefined, itemCode: ol["_itemCode"], itemName: ol["_itemName"],
        quantityDelivered: qtyToDeliver, quantityOrdered: ol["_quantity"],
        uom: ol["_uom"], unitPrice: ol["_unitPrice"],
        orderLineId: ol.id.value, warehouseId: ol["_warehouseId"] ?? undefined,
      });
      delivery.addLine(dl);
      ol.recordDelivery(qtyToDeliver);
      await this.delRepo.saveLine(dl);
    }
    await this.delRepo.save(delivery);
    order.updateDeliveryStatus();
    await this.orderRepo.save(order);
    return delivery;
  }

  async getDelivery(id: string): Promise<DeliveryOrder> {
    const d = await this.delRepo.findById(DeliveryOrderId.from(id));
    if (!d) throw new DomainError("NotFound", "Delivery not found");
    return d;
  }

  async findByDeliveryNumber(number: string): Promise<DeliveryOrder | null> {
    return this.delRepo.findByDeliveryNumber(number);
  }

  async findByOrder(orderId: string): Promise<DeliveryOrderState[]> {
    return this.delRepo.findByOrderId(orderId);
  }

  async findByStatus(status: string): Promise<DeliveryOrderState[]> {
    return this.delRepo.findByStatus(status);
  }

  async ship(id: string): Promise<DeliveryOrder> {
    const d = await this.getDelivery(id);
    d.ship();
    await this.delRepo.save(d);
    return d;
  }

  async markDelivered(id: string, podReceivedBy?: string, podNotes?: string): Promise<DeliveryOrder> {
    const d = await this.getDelivery(id);
    d.markDelivered(podReceivedBy, podNotes);
    await this.delRepo.save(d);
    return d;
  }

  async confirm(id: string): Promise<DeliveryOrder> {
    const d = await this.getDelivery(id);
    d.confirm();
    await this.delRepo.save(d);
    return d;
  }

  async reportException(id: string, exceptionType: string, reason: string): Promise<DeliveryOrder> {
    const d = await this.getDelivery(id);
    d.reportException(exceptionType, reason);
    await this.delRepo.save(d);
    return d;
  }

  async cancel(id: string, reason: string): Promise<DeliveryOrder> {
    const d = await this.getDelivery(id);
    d.cancel(reason);
    await this.delRepo.save(d);
    return d;
  }
}
