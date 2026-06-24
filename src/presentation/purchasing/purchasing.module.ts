import { Module } from "@nestjs/common";
import { PurchasingVendorController } from "./purchasing-vendor.controller.js";
import { PurchasingOrderController } from "./purchasing-order.controller.js";
import { PurchasingVendorService } from "../../application/purchasing/purchasing-vendor-service.js";
import { PurchasingOrderService } from "../../application/purchasing/purchasing-order-service.js";
import {
  PrismaVendorRepository, PrismaVendorQualificationRepository, PrismaVendorEvaluationRepository,
  PrismaPurchaseRequisitionRepository, PrismaRFQRepository, PrismaQuotationRepository,
  PrismaPurchaseOrderRepository, PrismaPurchaseContractRepository,
  PrismaGoodsReceiptRepository, PrismaSupplierInvoiceRepository,
  PrismaImportDeclarationRepository,
} from "../../infrastructure/purchasing/purchasing-prisma-repos.js";

@Module({
  controllers: [PurchasingVendorController, PurchasingOrderController],
  providers: [
    PurchasingVendorService, PurchasingOrderService,
    PrismaVendorRepository, PrismaVendorQualificationRepository, PrismaVendorEvaluationRepository,
    PrismaPurchaseRequisitionRepository, PrismaRFQRepository, PrismaQuotationRepository,
    PrismaPurchaseOrderRepository, PrismaPurchaseContractRepository,
    PrismaGoodsReceiptRepository, PrismaSupplierInvoiceRepository,
    PrismaImportDeclarationRepository,
  ],
})
export class PurchasingModule {}
