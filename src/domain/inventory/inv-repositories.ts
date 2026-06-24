import { Item, ItemState } from "./inv-item.js";
import { ItemId } from "./inv-ids.js";
import { Warehouse, WarehouseState } from "./inv-warehouse.js";
import { WarehouseId } from "./inv-ids.js";
import { Location, LocationState } from "./inv-warehouse.js";
import { LocationId } from "./inv-ids.js";
import { StockBalance, StockBalanceState } from "./inv-stock.js";
import { InventoryBalanceId } from "./inv-ids.js";
import { InventoryTransaction, InventoryTransactionState } from "./inv-transaction.js";
import { InventoryTransactionId } from "./inv-ids.js";
import { CostLayer, CostLayerState } from "./inv-cost-layer.js";
import { CostLayerId } from "./inv-ids.js";
import { StockCount, StockCountState } from "./inv-count.js";
import { StockCountId } from "./inv-ids.js";
import { InventoryReservation, ReservationState } from "./inv-reservation.js";
import { InventoryReservationId } from "./inv-ids.js";

export interface ItemRepository {
  save(item: Item): Promise<void>;
  findById(id: ItemId): Promise<Item | null>;
  findByCode(code: string): Promise<Item | null>;
  findBySku(sku: string): Promise<Item | null>;
  findAll(): Promise<Item[]>;
  findByCategory(categoryId: string): Promise<Item[]>;
  findActive(): Promise<Item[]>;
}

export interface WarehouseRepository {
  save(warehouse: Warehouse): Promise<void>;
  findById(id: WarehouseId): Promise<Warehouse | null>;
  findByCode(code: string): Promise<Warehouse | null>;
  findAll(): Promise<Warehouse[]>;
  findByType(type: string): Promise<Warehouse[]>;
}

export interface LocationRepository {
  save(location: Location): Promise<void>;
  findById(id: LocationId): Promise<Location | null>;
  findByCode(warehouseId: string, code: string): Promise<Location | null>;
  findByWarehouse(warehouseId: string): Promise<Location[]>;
  findAvailable(): Promise<Location[]>;
}

export interface StockBalanceRepository {
  save(balance: StockBalance): Promise<void>;
  findById(id: InventoryBalanceId): Promise<StockBalance | null>;
  findByItemAndLocation(itemId: string, warehouseId: string, locationId: string | null, lotId: string | null): Promise<StockBalance | null>;
  findByItem(itemId: string): Promise<StockBalance[]>;
  findByWarehouse(warehouseId: string): Promise<StockBalance[]>;
  findLowStock(threshold: number): Promise<StockBalance[]>;
  findBlocked(): Promise<StockBalance[]>;
}

export interface InventoryTransactionRepository {
  save(transaction: InventoryTransaction): Promise<void>;
  findById(id: InventoryTransactionId): Promise<InventoryTransaction | null>;
  findByDocumentNumber(docNumber: string): Promise<InventoryTransaction | null>;
  findByItem(itemId: string, limit?: number, offset?: number): Promise<InventoryTransaction[]>;
  findByWarehouse(warehouseId: string, limit?: number, offset?: number): Promise<InventoryTransaction[]>;
  findByReference(sourceType: string, sourceId: string): Promise<InventoryTransaction[]>;
  findByStatus(status: string): Promise<InventoryTransaction[]>;
  findReversals(originalTransactionId: string): Promise<InventoryTransaction[]>;
}

export interface CostLayerRepository {
  save(layer: CostLayer): Promise<void>;
  findById(id: CostLayerId): Promise<CostLayer | null>;
  findByItemAndWarehouse(itemId: string, warehouseId: string): Promise<CostLayer[]>;
  findActiveLayers(itemId: string, warehouseId: string): Promise<CostLayer[]>;
  findOldestLayers(itemId: string, warehouseId: string, quantity: number): Promise<CostLayer[]>;
  delete(id: CostLayerId): Promise<void>;
}

export interface StockCountRepository {
  save(count: StockCount): Promise<void>;
  findById(id: StockCountId): Promise<StockCount | null>;
  findByCountNumber(countNumber: string): Promise<StockCount | null>;
  findByWarehouse(warehouseId: string): Promise<StockCount[]>;
  findByStatus(status: string): Promise<StockCount[]>;
  findPendingApproval(): Promise<StockCount[]>;
}

export interface InventoryReservationRepository {
  save(reservation: InventoryReservation): Promise<void>;
  findById(id: InventoryReservationId): Promise<InventoryReservation | null>;
  findByItem(itemId: string): Promise<InventoryReservation[]>;
  findByOrderReference(orderType: string, orderId: string): Promise<InventoryReservation[]>;
  findActive(): Promise<InventoryReservation[]>;
  findExpired(): Promise<InventoryReservation[]>;
}
