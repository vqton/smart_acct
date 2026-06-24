import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  ItemId, WarehouseId, LocationId, InventoryBalanceId, InventoryTransactionId,
  CostLayerId, StockCountId, InventoryReservationId, CountLineId,
} from "../../domain/inventory/inv-ids.js";
import { Item, type ItemState } from "../../domain/inventory/inv-item.js";
import { Warehouse, Location } from "../../domain/inventory/inv-warehouse.js";
import { StockBalance } from "../../domain/inventory/inv-stock.js";
import { InventoryTransaction, TransactionLine } from "../../domain/inventory/inv-transaction.js";
import { CostLayer } from "../../domain/inventory/inv-cost-layer.js";
import { StockCount, CountLine } from "../../domain/inventory/inv-count.js";
import { InventoryReservation, ReservationLine } from "../../domain/inventory/inv-reservation.js";
import {
  ItemType, ItemStatus, ItemCategory, ItemValuationMethod, LotControl,
  WarehouseType, LocationType, InventoryTransactionType,
  InventoryTransactionStatus, StockStatus, CountType, CountStatus,
  CostMethod, ReservationStatus,
} from "../../domain/inventory/inv-enums.js";
import {
  PrismaItemRepository,
  PrismaWarehouseRepository,
  PrismaLocationRepository,
  PrismaStockBalanceRepository,
  PrismaInventoryTransactionRepository,
  PrismaCostLayerRepository,
  PrismaStockCountRepository,
  PrismaInventoryReservationRepository,
} from "../../infrastructure/inventory/inventory-prisma-repos.js";
import { InventoryGlService } from "./inventory-gl-service.js";

@Injectable()
export class InventoryService {
  constructor(
    private readonly itemRepo: PrismaItemRepository,
    private readonly warehouseRepo: PrismaWarehouseRepository,
    private readonly locationRepo: PrismaLocationRepository,
    private readonly stockRepo: PrismaStockBalanceRepository,
    private readonly txRepo: PrismaInventoryTransactionRepository,
    private readonly costRepo: PrismaCostLayerRepository,
    private readonly countRepo: PrismaStockCountRepository,
    private readonly resvRepo: PrismaInventoryReservationRepository,
    private readonly glService: InventoryGlService,
  ) {}

  // ─── Item Master ──────────────────────────────────────────────────────────

  async createItem(p: {
    code: string; sku: string; name: string; uomId: string;
    itemType?: string; category?: string; barcode?: string; plu?: string;
    itemGroupId?: string; brandId?: string; valuationMethod?: string;
    lotControl?: string; shelfLifeDays?: number; isHazardous?: boolean;
    glInventoryAccountId?: string; glRevenueAccountId?: string;
    glCogsAccountId?: string; glExpenseAccountId?: string;
    glPurchaseAccountId?: string; glTransferAccountId?: string;
    standardCost?: number; minStock?: number; maxStock?: number;
    reorderPoint?: number; leadTimeDays?: number; taxCodeId?: string;
  }): Promise<Item> {
    const existing = await this.itemRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Item code ${p.code} already exists`);
    const item = Item.create({ ...p, itemType: p.itemType as ItemType, category: p.category as ItemCategory, valuationMethod: p.valuationMethod as ItemValuationMethod, lotControl: p.lotControl as LotControl });
    await this.itemRepo.save(item);
    return item;
  }

  async getItem(id: string): Promise<Item | null> {
    return this.itemRepo.findById(ItemId.from(id));
  }

  async getItemByCode(code: string): Promise<Item | null> {
    return this.itemRepo.findByCode(code);
  }

  async listItems(status?: string): Promise<Item[]> {
    if (status === "active") return this.itemRepo.findActive();
    return this.itemRepo.findAll();
  }

  async updateItem(id: string, p: Partial<Parameters<typeof Item.prototype.update>[0]>): Promise<Item> {
    const item = await this.itemRepo.findById(ItemId.from(id));
    if (!item) throw new DomainError("NotFound", "Item not found");
    item.update(p);
    await this.itemRepo.save(item);
    return item;
  }

  async changeItemStatus(id: string, status: string): Promise<Item> {
    const item = await this.itemRepo.findById(ItemId.from(id));
    if (!item) throw new DomainError("NotFound", "Item not found");
    item.changeStatus(status as ItemStatus);
    await this.itemRepo.save(item);
    return item;
  }

  async deleteItem(id: string): Promise<void> {
    const item = await this.itemRepo.findById(ItemId.from(id));
    if (!item) throw new DomainError("NotFound", "Item not found");
    item.delete();
    await this.itemRepo.save(item);
  }

  // ─── Warehouse ─────────────────────────────────────────────────────────────

  async createWarehouse(p: {
    code: string; name: string; companyId: string; branchId?: string;
    type?: string; storageType?: string; allowNegative?: boolean;
    phone?: string; email?: string; managerName?: string;
  }): Promise<Warehouse> {
    const existing = await this.warehouseRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Warehouse code ${p.code} already exists`);
    const wh = Warehouse.create({ ...p, type: p.type as WarehouseType, storageType: p.storageType as any });
    await this.warehouseRepo.save(wh);
    return wh;
  }

  async getWarehouse(id: string): Promise<Warehouse | null> {
    return this.warehouseRepo.findById(WarehouseId.from(id));
  }

  async listWarehouses(): Promise<Warehouse[]> {
    return this.warehouseRepo.findAll();
  }

  async updateWarehouse(id: string, p: Partial<Parameters<typeof Warehouse.prototype.update>[0]>): Promise<Warehouse> {
    const wh = await this.warehouseRepo.findById(WarehouseId.from(id));
    if (!wh) throw new DomainError("NotFound", "Warehouse not found");
    wh.update(p);
    await this.warehouseRepo.save(wh);
    return wh;
  }

  // ─── Location ──────────────────────────────────────────────────────────────

  async createLocation(p: {
    warehouseId: string; code: string; name: string; type?: string;
    parentId?: string; storageType?: string; barcode?: string;
    putawayZone?: string; pickingZone?: string;
  }): Promise<Location> {
    const existing = await this.locationRepo.findByCode(p.warehouseId, p.code);
    if (existing) throw new DomainError("Conflict", `Location code ${p.code} exists in warehouse`);
    const loc = Location.create({ ...p, type: p.type as LocationType, storageType: p.storageType as any });
    await this.locationRepo.save(loc);
    return loc;
  }

  async getLocation(id: string): Promise<Location | null> {
    return this.locationRepo.findById(LocationId.from(id));
  }

  async listLocations(warehouseId: string): Promise<Location[]> {
    return this.locationRepo.findByWarehouse(warehouseId);
  }

  // ─── Stock Balance ─────────────────────────────────────────────────────────

  async getStockBalance(itemId: string, warehouseId: string, locationId?: string, lotId?: string): Promise<StockBalance | null> {
    return this.stockRepo.findByItemAndLocation(itemId, warehouseId, locationId ?? null, lotId ?? null);
  }

  async listStockByItem(itemId: string): Promise<StockBalance[]> {
    return this.stockRepo.findByItem(itemId);
  }

  async listStockByWarehouse(warehouseId: string): Promise<StockBalance[]> {
    return this.stockRepo.findByWarehouse(warehouseId);
  }

  async findLowStock(threshold: number): Promise<StockBalance[]> {
    return this.stockRepo.findLowStock(threshold);
  }

  // ─── Inventory Transaction ─────────────────────────────────────────────────

  async createTransaction(p: {
    transactionNumber: string; transactionType: string; companyId: string;
    warehouseId: string; branchId?: string; transactionDate?: Date;
    postingDate?: Date; description?: string; currencyCode?: string;
    exchangeRate?: number; referenceType?: string; referenceId?: string;
    sourceDocumentType?: string; sourceDocumentId?: string; createdById?: string;
  }): Promise<InventoryTransaction> {
    const existing = await this.txRepo.findByDocumentNumber(p.transactionNumber);
    if (existing) throw new DomainError("Conflict", `Transaction ${p.transactionNumber} already exists`);
    return InventoryTransaction.create({ ...p, transactionType: p.transactionType as InventoryTransactionType });
  }

  async saveTransaction(tx: InventoryTransaction): Promise<void> {
    await this.txRepo.save(tx);
  }

  async getTransaction(id: string): Promise<InventoryTransaction | null> {
    return this.txRepo.findById(InventoryTransactionId.from(id));
  }

  async listTransactions(warehouseId?: string, status?: string): Promise<InventoryTransaction[]> {
    if (status) return this.txRepo.findByStatus(status);
    if (warehouseId) return this.txRepo.findByWarehouse(warehouseId);
    return this.txRepo.findByStatus("draft");
  }

  async submitTransaction(id: string, userId: string): Promise<InventoryTransaction> {
    const tx = await this.txRepo.findById(InventoryTransactionId.from(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.submit(userId);
    await this.txRepo.save(tx);
    return tx;
  }

  async approveTransaction(id: string, userId: string): Promise<InventoryTransaction> {
    const tx = await this.txRepo.findById(InventoryTransactionId.from(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.approve(userId);
    await this.txRepo.save(tx);
    return tx;
  }

  async postTransaction(id: string, userId: string): Promise<InventoryTransaction> {
    const tx = await this.txRepo.findById(InventoryTransactionId.from(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");

    // Post the transaction
    tx.post(userId);

    // Update stock balances for each line
    for (const line of tx.lines) {
      const balance = await this.stockRepo.findByItemAndLocation(
        line.itemId, line.warehouseId, line.locationId, null,
      );
      if (!balance) {
        // Create new balance entry if it doesn't exist (receipt / inbound)
        const newBal = StockBalance.create(line.itemId, line.warehouseId, line.locationId ?? undefined);
        if (line.quantity > 0) {
          newBal.receive(line.quantity, line.unitCost, false);
        }
        await this.stockRepo.save(newBal);

        // Create cost layer for inbound
        if (line.quantity > 0) {
          const cl = CostLayer.create({
            itemId: line.itemId, warehouseId: line.warehouseId,
            quantity: line.quantity, unitCost: line.unitCost,
            transactionId: tx.id.value, transactionLineId: line.id.value,
          });
          await this.costRepo.save(cl);
        }
      } else {
        if (line.quantity > 0) {
          balance.receive(line.quantity, line.unitCost, true);
          await this.stockRepo.save(balance);

          const cl = CostLayer.create({
            itemId: line.itemId, warehouseId: line.warehouseId,
            quantity: line.quantity, unitCost: line.unitCost,
            transactionId: tx.id.value, transactionLineId: line.id.value,
          });
          await this.costRepo.save(cl);
        } else if (line.quantity < 0) {
          const issueQty = Math.abs(line.quantity);
          // Consume FIFO cost layers
          const layers = await this.costRepo.findActiveLayers(line.itemId, line.warehouseId);
          let remaining = issueQty;
          for (const layer of layers) {
            if (remaining <= 0) break;
            const consume = Math.min(remaining, layer.remainingQty);
            layer.consume(consume, tx.id.value);
            await this.costRepo.save(layer);
            remaining -= consume;
          }
          balance.issue(issueQty, true);
          await this.stockRepo.save(balance);
        }
      }
    }

    await this.txRepo.save(tx);

    // Post to GL
    try {
      await this.glService.postTransactionGl(tx, userId);
    } catch (e) {
      throw new DomainError("Infrastructure", `GL posting failed for transaction ${tx.transactionNumber}: ${(e as Error).message}`);
    }

    return tx;
  }

  async reverseTransaction(id: string, userId: string, reason: string): Promise<InventoryTransaction> {
    const tx = await this.txRepo.findById(InventoryTransactionId.from(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    const reversal = tx.reverse(userId, reason);
    await this.txRepo.save(tx);
    await this.txRepo.save(reversal);
    // Post the reversal automatically
    await this.postTransaction(reversal.id.value, userId);
    return reversal;
  }

  async cancelTransaction(id: string, userId: string, reason: string): Promise<void> {
    const tx = await this.txRepo.findById(InventoryTransactionId.from(id));
    if (!tx) throw new DomainError("NotFound", "Transaction not found");
    tx.cancel(userId, reason);
    await this.txRepo.save(tx);
  }

  // ─── Stock Count ───────────────────────────────────────────────────────────

  async createStockCount(p: {
    countNumber: string; companyId: string; warehouseId: string;
    countType?: string; locationId?: string; notes?: string;
  }): Promise<StockCount> {
    const existing = await this.countRepo.findByCountNumber(p.countNumber);
    if (existing) throw new DomainError("Conflict", `Count ${p.countNumber} already exists`);
    return StockCount.create({ ...p, countType: p.countType as CountType });
  }

  async saveStockCount(sc: StockCount): Promise<void> {
    await this.countRepo.save(sc);
  }

  async getStockCount(id: string): Promise<StockCount | null> {
    return this.countRepo.findById(StockCountId.from(id));
  }

  async listStockCounts(warehouseId?: string, status?: string): Promise<StockCount[]> {
    if (status) return this.countRepo.findByStatus(status);
    if (warehouseId) return this.countRepo.findByWarehouse(warehouseId);
    return this.countRepo.findByStatus("planned");
  }

  async freezeStockCount(id: string): Promise<StockCount> {
    const sc = await this.countRepo.findById(StockCountId.from(id));
    if (!sc) throw new DomainError("NotFound", "Stock count not found");
    sc.freeze();
    await this.countRepo.save(sc);
    return sc;
  }

  async completeStockCount(id: string): Promise<StockCount> {
    const sc = await this.countRepo.findById(StockCountId.from(id));
    if (!sc) throw new DomainError("NotFound", "Stock count not found");
    sc.complete();
    await this.countRepo.save(sc);
    return sc;
  }

  async approveStockCount(id: string, userId: string): Promise<StockCount> {
    const sc = await this.countRepo.findById(StockCountId.from(id));
    if (!sc) throw new DomainError("NotFound", "Stock count not found");
    sc.approve(userId);
    await this.countRepo.save(sc);

    // Post adjustments for count variances
    for (const line of sc.lines) {
      if (line.varianceQty === 0) continue;
      const balance = await this.stockRepo.findByItemAndLocation(
        line.itemId, line.warehouseId, line.locationId, line.lotId,
      );
      if (balance) {
        balance.adjust(line.expectedQty + line.varianceQty, line.unitCost, "Count variance");
        await this.stockRepo.save(balance);
      }
    }

    return sc;
  }

  async cancelStockCount(id: string, reason: string): Promise<void> {
    const sc = await this.countRepo.findById(StockCountId.from(id));
    if (!sc) throw new DomainError("NotFound", "Stock count not found");
    sc.cancel(reason);
    await this.countRepo.save(sc);
  }

  // ─── Inventory Reservation ─────────────────────────────────────────────────

  async createReservation(p: {
    reservationNumber: string; orderType: string; orderId: string;
    companyId: string; orderLineId?: string; customerId?: string;
    warehouseId?: string; expiresAt?: Date;
  }): Promise<InventoryReservation> {
    const existing = await this.resvRepo.findByOrderReference(p.orderType, p.orderId);
    if (existing.length > 0) throw new DomainError("Conflict", "Reservation already exists for this order");
    const resv = InventoryReservation.create(p);
    await this.resvRepo.save(resv);
    return resv;
  }

  async fulfillReservation(id: string): Promise<InventoryReservation> {
    const resv = await this.resvRepo.findById(InventoryReservationId.from(id));
    if (!resv) throw new DomainError("NotFound", "Reservation not found");
    resv.fulfill();
    await this.resvRepo.save(resv);
    return resv;
  }

  async cancelReservation(id: string, reason: string): Promise<void> {
    const resv = await this.resvRepo.findById(InventoryReservationId.from(id));
    if (!resv) throw new DomainError("NotFound", "Reservation not found");
    resv.cancel(reason);
    await this.resvRepo.save(resv);
  }

  async getReservation(id: string): Promise<InventoryReservation | null> {
    return this.resvRepo.findById(InventoryReservationId.from(id));
  }

  async listActiveReservations(): Promise<InventoryReservation[]> {
    return this.resvRepo.findActive();
  }

  async addReservationLine(id: string, line: ReservationLine): Promise<InventoryReservation> {
    const resv = await this.resvRepo.findById(InventoryReservationId.from(id));
    if (!resv) throw new DomainError("NotFound", "Reservation not found");
    resv.addLine(line);
    await this.resvRepo.save(resv);
    return resv;
  }

  async expireReservations(): Promise<number> {
    const expired = await this.resvRepo.findExpired();
    for (const r of expired) {
      r.expire();
      await this.resvRepo.save(r);
    }
    return expired.length;
  }
}
