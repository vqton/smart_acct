import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  ItemId, WarehouseId, LocationId, InventoryBalanceId, InventoryTransactionId,
  CostLayerId, StockCountId, InventoryReservationId, TransactionLineId,
  CountLineId, ReservationLineId, LotId,
} from "../../domain/inventory/inv-ids.js";
import { Item, type ItemState } from "../../domain/inventory/inv-item.js";
import { Warehouse, type WarehouseState } from "../../domain/inventory/inv-warehouse.js";
import { Location, type LocationState } from "../../domain/inventory/inv-warehouse.js";
import { StockBalance, type StockBalanceState } from "../../domain/inventory/inv-stock.js";
import { InventoryTransaction, type InventoryTransactionState, TransactionLine, type TransactionLineState } from "../../domain/inventory/inv-transaction.js";
import { CostLayer, type CostLayerState } from "../../domain/inventory/inv-cost-layer.js";
import { StockCount, type StockCountState, CountLine, type CountLineState } from "../../domain/inventory/inv-count.js";
import { InventoryReservation, type ReservationState, ReservationLine, type ReservationLineState } from "../../domain/inventory/inv-reservation.js";
import type {
  ItemRepository, WarehouseRepository, LocationRepository, StockBalanceRepository,
  InventoryTransactionRepository, CostLayerRepository, StockCountRepository,
  InventoryReservationRepository,
} from "../../domain/inventory/inv-repositories.js";

function toNumber(val: unknown, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  if (typeof val === "number") return val;
  if (typeof val === "object" && "toString" in (val as object)) return parseFloat((val as any).toString());
  return fallback;
}

// ─── Item Repository ─────────────────────────────────────────────────────────

@Injectable()
export class PrismaItemRepository implements ItemRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(item: Item): Promise<void> {
    const s = item.toState();
    const data: any = {
      ...s,
      standardCost: s.standardCost ? toNumber(s.standardCost) : null,
      minStock: s.minStock ? toNumber(s.minStock) : null,
      maxStock: s.maxStock ? toNumber(s.maxStock) : null,
      reorderPoint: s.reorderPoint ? toNumber(s.reorderPoint) : null,
    };
    delete data.balances; delete data.transactions; delete data.costLayers;
    delete data.countLines; delete data.reservationLines; delete data.transactionLines;
    await this.prisma.invItem.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: ItemId): Promise<Item | null> {
    const row = await this.prisma.invItem.findUnique({ where: { id: id.value } });
    return row ? Item.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Item | null> {
    const row = await this.prisma.invItem.findUnique({ where: { code } });
    return row ? Item.load(row as any) : null;
  }

  async findBySku(sku: string): Promise<Item | null> {
    const row = await this.prisma.invItem.findUnique({ where: { sku } });
    return row ? Item.load(row as any) : null;
  }

  async findAll(): Promise<Item[]> {
    return (await this.prisma.invItem.findMany({ orderBy: { code: "asc" } })).map(r => Item.load(r as any));
  }

  async findByCategory(categoryId: string): Promise<Item[]> {
    return (await this.prisma.invItem.findMany({ where: { itemGroupId: categoryId }, orderBy: { code: "asc" } })).map(r => Item.load(r as any));
  }

  async findActive(): Promise<Item[]> {
    return (await this.prisma.invItem.findMany({ where: { status: "active", deletedAt: null }, orderBy: { code: "asc" } })).map(r => Item.load(r as any));
  }
}

// ─── Warehouse Repository ────────────────────────────────────────────────────

@Injectable()
export class PrismaWarehouseRepository implements WarehouseRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(warehouse: Warehouse): Promise<void> {
    const s = warehouse.toState();
    const data: any = { ...s };
    await this.prisma.invWarehouse.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: WarehouseId): Promise<Warehouse | null> {
    const row = await this.prisma.invWarehouse.findUnique({ where: { id: id.value } });
    return row ? Warehouse.load(row as any) : null;
  }

  async findByCode(code: string): Promise<Warehouse | null> {
    const row = await this.prisma.invWarehouse.findUnique({ where: { code } });
    return row ? Warehouse.load(row as any) : null;
  }

  async findAll(): Promise<Warehouse[]> {
    return (await this.prisma.invWarehouse.findMany({ orderBy: { code: "asc" } })).map(r => Warehouse.load(r as any));
  }

  async findByType(type: string): Promise<Warehouse[]> {
    return (await this.prisma.invWarehouse.findMany({ where: { type: type as any }, orderBy: { code: "asc" } })).map(r => Warehouse.load(r as any));
  }
}

// ─── Location Repository ─────────────────────────────────────────────────────

@Injectable()
export class PrismaLocationRepository implements LocationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(location: Location): Promise<void> {
    const s = location.toState();
    const data: any = { ...s };
    await this.prisma.invLocation.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: LocationId): Promise<Location | null> {
    const row = await this.prisma.invLocation.findUnique({ where: { id: id.value } });
    return row ? Location.load(row as any) : null;
  }

  async findByCode(warehouseId: string, code: string): Promise<Location | null> {
    const row = await this.prisma.invLocation.findUnique({ where: { warehouseId_code: { warehouseId, code } } });
    return row ? Location.load(row as any) : null;
  }

  async findByWarehouse(warehouseId: string): Promise<Location[]> {
    return (await this.prisma.invLocation.findMany({ where: { warehouseId }, orderBy: { code: "asc" } })).map(r => Location.load(r as any));
  }

  async findAvailable(): Promise<Location[]> {
    return (await this.prisma.invLocation.findMany({ where: { status: "active", isActive: true }, orderBy: { code: "asc" } })).map(r => Location.load(r as any));
  }
}

// ─── Stock Balance Repository ─────────────────────────────────────────────────

@Injectable()
export class PrismaStockBalanceRepository implements StockBalanceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(balance: StockBalance): Promise<void> {
    const s = balance.toState();
    const data: any = {
      ...s,
      quantity: toNumber(s.quantity),
      reservedQty: toNumber(s.reservedQty),
      allocatedQty: toNumber(s.allocatedQty),
      inTransitQty: toNumber(s.inTransitQty),
      onOrderQty: toNumber(s.onOrderQty),
      unitCost: toNumber(s.unitCost),
      totalCost: toNumber(s.totalCost),
    };
    await this.prisma.invStockBalance.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: InventoryBalanceId): Promise<StockBalance | null> {
    const row = await this.prisma.invStockBalance.findUnique({ where: { id: id.value } });
    return row ? StockBalance.load(row as any) : null;
  }

  async findByItemAndLocation(itemId: string, warehouseId: string, locationId: string | null, lotId: string | null): Promise<StockBalance | null> {
    const row = await this.prisma.invStockBalance.findUnique({
      where: { itemId_warehouseId_locationId_lotId: { itemId, warehouseId, locationId: locationId ?? "", lotId: lotId ?? "" } },
    });
    return row ? StockBalance.load(row as any) : null;
  }

  async findByItem(itemId: string): Promise<StockBalance[]> {
    return (await this.prisma.invStockBalance.findMany({ where: { itemId } })).map(r => StockBalance.load(r as any));
  }

  async findByWarehouse(warehouseId: string): Promise<StockBalance[]> {
    return (await this.prisma.invStockBalance.findMany({ where: { warehouseId } })).map(r => StockBalance.load(r as any));
  }

  async findLowStock(threshold: number): Promise<StockBalance[]> {
    return (await this.prisma.invStockBalance.findMany({ where: { quantity: { lte: threshold } } })).map(r => StockBalance.load(r as any));
  }

  async findBlocked(): Promise<StockBalance[]> {
    return (await this.prisma.invStockBalance.findMany({ where: { stockStatus: "blocked" } })).map(r => StockBalance.load(r as any));
  }
}

// ─── Inventory Transaction Repository ─────────────────────────────────────────

@Injectable()
export class PrismaInventoryTransactionRepository implements InventoryTransactionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transaction: InventoryTransaction): Promise<void> {
    const s = transaction.toState();
    const data: any = {
      ...s,
      totalQuantity: toNumber(s.totalQuantity),
      totalAmount: toNumber(s.totalAmount),
      exchangeRate: toNumber(s.exchangeRate),
    };
    delete data.lines;
    await this.prisma.invTransaction.upsert({ where: { id: data.id }, create: data, update: data });
    for (const line of s.lines) {
      const lineData: any = {
        ...line,
        quantity: toNumber(line.quantity),
        unitCost: toNumber(line.unitCost),
        totalCost: toNumber(line.totalCost),
        exchangeRate: toNumber(line.exchangeRate),
      };
      await this.prisma.invTransactionLine.upsert({ where: { id: lineData.id }, create: lineData, update: lineData });
    }
  }

  async findById(id: InventoryTransactionId): Promise<InventoryTransaction | null> {
    const row = await this.prisma.invTransaction.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    return InventoryTransaction.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByDocumentNumber(docNumber: string): Promise<InventoryTransaction | null> {
    const row = await this.prisma.invTransaction.findUnique({ where: { transactionNumber: docNumber }, include: { lines: true } });
    if (!row) return null;
    return InventoryTransaction.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByItem(itemId: string, limit = 50, offset = 0): Promise<InventoryTransaction[]> {
    const rows = await this.prisma.invTransaction.findMany({
      where: { lines: { some: { itemId } } },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
      take: limit, skip: offset,
    });
    return rows.map(r => InventoryTransaction.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByWarehouse(warehouseId: string, limit = 50, offset = 0): Promise<InventoryTransaction[]> {
    const rows = await this.prisma.invTransaction.findMany({
      where: { warehouseId },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
      take: limit, skip: offset,
    });
    return rows.map(r => InventoryTransaction.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByReference(sourceType: string, sourceId: string): Promise<InventoryTransaction[]> {
    const rows = await this.prisma.invTransaction.findMany({
      where: { referenceType: sourceType, referenceId: sourceId },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => InventoryTransaction.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByStatus(status: string): Promise<InventoryTransaction[]> {
    const rows = await this.prisma.invTransaction.findMany({
      where: { status: status as any },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => InventoryTransaction.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findReversals(originalTransactionId: string): Promise<InventoryTransaction[]> {
    const rows = await this.prisma.invTransaction.findMany({
      where: { reverseOfId: originalTransactionId },
      include: { lines: true },
    });
    return rows.map(r => InventoryTransaction.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }
}

// ─── Cost Layer Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaCostLayerRepository implements CostLayerRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(layer: CostLayer): Promise<void> {
    const s = layer.toState();
    const data: any = {
      ...s,
      quantity: toNumber(s.quantity),
      unitCost: toNumber(s.unitCost),
      totalCost: toNumber(s.totalCost),
      remainingQty: toNumber(s.remainingQty),
      remainingCost: toNumber(s.remainingCost),
    };
    await this.prisma.invCostLayer.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: CostLayerId): Promise<CostLayer | null> {
    const row = await this.prisma.invCostLayer.findUnique({ where: { id: id.value } });
    return row ? CostLayer.load(row as any) : null;
  }

  async findByItemAndWarehouse(itemId: string, warehouseId: string): Promise<CostLayer[]> {
    return (await this.prisma.invCostLayer.findMany({
      where: { itemId, warehouseId },
      orderBy: { receivedAt: "asc" },
    })).map(r => CostLayer.load(r as any));
  }

  async findActiveLayers(itemId: string, warehouseId: string): Promise<CostLayer[]> {
    return (await this.prisma.invCostLayer.findMany({
      where: { itemId, warehouseId, isConsumed: false, remainingQty: { gt: 0 } },
      orderBy: { receivedAt: "asc" },
    })).map(r => CostLayer.load(r as any));
  }

  async findOldestLayers(itemId: string, warehouseId: string, quantity: number): Promise<CostLayer[]> {
    return (await this.prisma.invCostLayer.findMany({
      where: { itemId, warehouseId, isConsumed: false, remainingQty: { gt: 0 } },
      orderBy: { receivedAt: "asc" },
      take: 100,
    })).map(r => CostLayer.load(r as any));
  }

  async delete(id: CostLayerId): Promise<void> {
    await this.prisma.invCostLayer.delete({ where: { id: id.value } });
  }
}

// ─── Stock Count Repository ──────────────────────────────────────────────────

@Injectable()
export class PrismaStockCountRepository implements StockCountRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(count: StockCount): Promise<void> {
    const s = count.toState();
    const data: any = { ...s };
    delete data.lines;
    await this.prisma.invStockCount.upsert({ where: { id: data.id }, create: data, update: data });
    for (const line of s.lines) {
      const lineData: any = {
        ...line,
        expectedQty: toNumber(line.expectedQty),
        actualQty: line.actualQty != null ? toNumber(line.actualQty) : null,
        varianceQty: toNumber(line.varianceQty),
        varianceValue: toNumber(line.varianceValue),
        unitCost: toNumber(line.unitCost),
      };
      await this.prisma.invCountLine.upsert({ where: { id: lineData.id }, create: lineData, update: lineData });
    }
  }

  async findById(id: StockCountId): Promise<StockCount | null> {
    const row = await this.prisma.invStockCount.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    return StockCount.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByCountNumber(countNumber: string): Promise<StockCount | null> {
    const row = await this.prisma.invStockCount.findUnique({ where: { countNumber }, include: { lines: true } });
    if (!row) return null;
    return StockCount.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByWarehouse(warehouseId: string): Promise<StockCount[]> {
    const rows = await this.prisma.invStockCount.findMany({
      where: { warehouseId }, include: { lines: true }, orderBy: { createdAt: "desc" },
    });
    return rows.map(r => StockCount.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByStatus(status: string): Promise<StockCount[]> {
    const rows = await this.prisma.invStockCount.findMany({
      where: { status: status as any }, include: { lines: true }, orderBy: { createdAt: "desc" },
    });
    return rows.map(r => StockCount.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findPendingApproval(): Promise<StockCount[]> {
    const rows = await this.prisma.invStockCount.findMany({
      where: { status: "completed" }, include: { lines: true }, orderBy: { createdAt: "asc" },
    });
    return rows.map(r => StockCount.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }
}

// ─── Inventory Reservation Repository ────────────────────────────────────────

@Injectable()
export class PrismaInventoryReservationRepository implements InventoryReservationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(reservation: InventoryReservation): Promise<void> {
    const s = reservation.toState();
    const data: any = { ...s };
    delete data.lines;
    await this.prisma.invReservation.upsert({ where: { id: data.id }, create: data, update: data });
    for (const line of s.lines) {
      const lineData: any = {
        ...line,
        quantity: toNumber(line.quantity),
        fulfilledQty: toNumber(line.fulfilledQty),
        cancelledQty: toNumber(line.cancelledQty),
      };
      await this.prisma.invReservationLine.upsert({ where: { id: lineData.id }, create: lineData, update: lineData });
    }
  }

  async findById(id: InventoryReservationId): Promise<InventoryReservation | null> {
    const row = await this.prisma.invReservation.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    return InventoryReservation.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByItem(itemId: string): Promise<InventoryReservation[]> {
    const rows = await this.prisma.invReservation.findMany({
      where: { lines: { some: { itemId } } },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => InventoryReservation.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByOrderReference(orderType: string, orderId: string): Promise<InventoryReservation[]> {
    const rows = await this.prisma.invReservation.findMany({
      where: { orderType, orderId },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => InventoryReservation.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findActive(): Promise<InventoryReservation[]> {
    const rows = await this.prisma.invReservation.findMany({
      where: { status: "active" },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => InventoryReservation.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findExpired(): Promise<InventoryReservation[]> {
    const rows = await this.prisma.invReservation.findMany({
      where: { status: "active", expiresAt: { lte: new Date() } },
      include: { lines: true },
    });
    return rows.map(r => InventoryReservation.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }
}
