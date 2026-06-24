import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PriceListId } from "../../domain/sales/sales-ids.js";
import { PrismaService } from "../../prisma/prisma.service.js";

@Injectable()
export class SalesPricingService {
  constructor(private readonly prisma: PrismaService) {}

  async getUnitPrice(itemId: string, customerGroupId?: string, priceListId?: string, quantity?: number): Promise<{ unitPrice: number; priceListId: string; priceListItemId: string } | null> {
    if (priceListId) {
      const item = await this.prisma.slsPriceListItem.findFirst({
        where: { priceListId, itemId, isActive: true, effectiveFrom: { lte: new Date() }, OR: [{ effectiveTo: null }, { effectiveTo: { gte: new Date() } }] },
        orderBy: { createdAt: "desc" },
      });
      if (item) return { unitPrice: Number(item.unitPrice), priceListId, priceListItemId: item.id };
    }
    const defaultList = await this.prisma.slsPriceList.findFirst({
      where: { isDefault: true, isActive: true },
      include: { items: { where: { itemId, isActive: true } } },
    });
    if (defaultList && defaultList.items.length > 0) {
      const item = defaultList.items[0];
      return { unitPrice: Number(item.unitPrice), priceListId: defaultList.id, priceListItemId: item.id };
    }
    return null;
  }

  async getPriceForCustomer(itemId: string, customerId: string, quantity?: number): Promise<{ unitPrice: number; priceListId: string } | null> {
    const customer = await this.prisma.slsCustomer.findUnique({ where: { id: customerId } });
    if (!customer) return null;
    const priceGroup = customer.priceGroup;
    const customerGroupId = customer.groupId;
    const priceList = await this.prisma.slsPriceList.findFirst({
      where: { isActive: true, code: priceGroup },
      include: { items: { where: { itemId, isActive: true } } },
    });
    if (priceList && priceList.items.length > 0) {
      return { unitPrice: Number(priceList.items[0].unitPrice), priceListId: priceList.id };
    }
    return this.getUnitPrice(itemId, customerGroupId ?? undefined, undefined, quantity);
  }
}
