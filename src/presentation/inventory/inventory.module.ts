import { Module } from "@nestjs/common";
import { InventoryController } from "./inventory.controller.js";
import { InventoryService } from "../../application/inventory/inventory-service.js";
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
import { PrismaModule } from "../../prisma/prisma.module.js";

@Module({
  imports: [PrismaModule],
  controllers: [InventoryController],
  providers: [
    InventoryService,
    PrismaItemRepository,
    PrismaWarehouseRepository,
    PrismaLocationRepository,
    PrismaStockBalanceRepository,
    PrismaInventoryTransactionRepository,
    PrismaCostLayerRepository,
    PrismaStockCountRepository,
    PrismaInventoryReservationRepository,
  ],
  exports: [
    InventoryService,
    PrismaItemRepository,
    PrismaWarehouseRepository,
    PrismaStockBalanceRepository,
    PrismaInventoryTransactionRepository,
    PrismaCostLayerRepository,
  ],
})
export class InventoryModule {}
