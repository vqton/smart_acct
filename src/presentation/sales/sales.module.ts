import { Module } from "@nestjs/common";
import { GlModule } from "../gl/gl.module.js";
import { SalesCustomerController } from "./sales-customer.controller.js";
import { SalesOrderController } from "./sales-order.controller.js";
import { SalesInvoiceController } from "./sales-invoice.controller.js";
import { SalesDeliveryController } from "./sales-delivery.controller.js";
import { SalesReturnController } from "./sales-return.controller.js";
import { SalesPaymentController } from "./sales-payment.controller.js";
import { SalesReceivableController } from "./sales-receivable.controller.js";
import { SalesPricingController } from "./sales-pricing.controller.js";
import { SalesCustomerService } from "../../application/sales/sales-customer-service.js";
import { SalesOrderService } from "../../application/sales/sales-order-service.js";
import { SalesInvoiceService } from "../../application/sales/sales-invoice-service.js";
import { SalesDeliveryService } from "../../application/sales/sales-delivery-service.js";
import { SalesReturnService } from "../../application/sales/sales-return-service.js";
import { SalesPaymentService } from "../../application/sales/sales-payment-service.js";
import { ReceivableService } from "../../application/sales/sales-receivable-service.js";
import { SalesPricingService } from "../../application/sales/sales-pricing-service.js";
import { SalesGlService } from "../../application/sales/sales-gl-service.js";
import {
  PrismaCustomerRepository, PrismaQuotationRepository,
  PrismaSalesOrderRepository, PrismaDeliveryOrderRepository,
  PrismaSalesInvoiceRepository, PrismaSalesReturnRepository,
  PrismaCustomerReceiptRepository, PrismaReceivableAccountRepository,
} from "../../infrastructure/sales/sales-prisma-repos.js";

@Module({
  imports: [GlModule],
  controllers: [
    SalesCustomerController, SalesOrderController, SalesInvoiceController,
    SalesDeliveryController, SalesReturnController, SalesPaymentController,
    SalesReceivableController, SalesPricingController,
  ],
  providers: [
    SalesCustomerService, SalesOrderService, SalesInvoiceService,
    SalesDeliveryService, SalesReturnService, SalesPaymentService,
    ReceivableService, SalesPricingService, SalesGlService,
    PrismaCustomerRepository, PrismaQuotationRepository,
    PrismaSalesOrderRepository, PrismaDeliveryOrderRepository,
    PrismaSalesInvoiceRepository, PrismaSalesReturnRepository,
    PrismaCustomerReceiptRepository, PrismaReceivableAccountRepository,
  ],
})
export class SalesModule {}
