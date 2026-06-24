import { Module } from "@nestjs/common";
import { InventoryController } from "./inventory.controller.js";
import { InventoryService } from "../../application/inventory/inventory-service.js";
import { InventoryGlService } from "../../application/inventory/inventory-gl-service.js";
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
import {
  PrismaJournalBatchRepository,
  PrismaAccountRepository,
  PrismaPeriodRepository,
  PrismaFiscalYearRepository,
} from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaModule } from "../../prisma/prisma.module.js";

@Module({
  imports: [PrismaModule],
  controllers: [InventoryController],
  providers: [
    InventoryService,
    InventoryGlService,
    PrismaItemRepository,
    PrismaWarehouseRepository,
    PrismaLocationRepository,
    PrismaStockBalanceRepository,
    PrismaInventoryTransactionRepository,
    PrismaCostLayerRepository,
    PrismaStockCountRepository,
    PrismaInventoryReservationRepository,
    PrismaJournalBatchRepository,
    PrismaAccountRepository,
    PrismaPeriodRepository,
    PrismaFiscalYearRepository,
  ],
  exports: [
    InventoryService,
    InventoryGlService,
    PrismaItemRepository,
    PrismaWarehouseRepository,
    PrismaStockBalanceRepository,
    PrismaInventoryTransactionRepository,
    PrismaCostLayerRepository,
  ],
})
export class InventoryModule {}
