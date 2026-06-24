import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class ItemId extends Identifier { static new(): ItemId { return new ItemId(IdGenerator.uuid()); } static from(id: string): ItemId { return new ItemId(id); } }
export class ItemGroupId extends Identifier { static new(): ItemGroupId { return new ItemGroupId(IdGenerator.uuid()); } static from(id: string): ItemGroupId { return new ItemGroupId(id); } }
export class ItemCategoryId extends Identifier { static new(): ItemCategoryId { return new ItemCategoryId(IdGenerator.uuid()); } static from(id: string): ItemCategoryId { return new ItemCategoryId(id); } }
export class BrandId extends Identifier { static new(): BrandId { return new BrandId(IdGenerator.uuid()); } }
export class UomId extends Identifier { static new(): UomId { return new UomId(IdGenerator.uuid()); } }
export class WarehouseId extends Identifier { static new(): WarehouseId { return new WarehouseId(IdGenerator.uuid()); } static from(id: string): WarehouseId { return new WarehouseId(id); } }
export class LocationId extends Identifier { static new(): LocationId { return new LocationId(IdGenerator.uuid()); } static from(id: string): LocationId { return new LocationId(id); } }
export class InventoryBalanceId extends Identifier { static new(): InventoryBalanceId { return new InventoryBalanceId(IdGenerator.uuid()); } }
export class InventoryTransactionId extends Identifier { static new(): InventoryTransactionId { return new InventoryTransactionId(IdGenerator.uuid()); } static from(id: string): InventoryTransactionId { return new InventoryTransactionId(id); } }
export class TransactionLineId extends Identifier { static new(): TransactionLineId { return new TransactionLineId(IdGenerator.uuid()); } }
export class CostLayerId extends Identifier { static new(): CostLayerId { return new CostLayerId(IdGenerator.uuid()); } }
export class StockCountId extends Identifier { static new(): StockCountId { return new StockCountId(IdGenerator.uuid()); } static from(id: string): StockCountId { return new StockCountId(id); } }
export class CountLineId extends Identifier { static new(): CountLineId { return new CountLineId(IdGenerator.uuid()); } }
export class InventoryReservationId extends Identifier { static new(): InventoryReservationId { return new InventoryReservationId(IdGenerator.uuid()); } static from(id: string): InventoryReservationId { return new InventoryReservationId(id); } }
export class ReservationLineId extends Identifier { static new(): ReservationLineId { return new ReservationLineId(IdGenerator.uuid()); } }
export class LotId extends Identifier { static new(): LotId { return new LotId(IdGenerator.uuid()); } }
export class SerialId extends Identifier { static new(): SerialId { return new SerialId(IdGenerator.uuid()); } }
export class QualityInspectionId extends Identifier { static new(): QualityInspectionId { return new QualityInspectionId(IdGenerator.uuid()); } }
