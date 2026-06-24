import { Module } from "@nestjs/common";
import { EinvController } from "./einv.controller.js";
import { EinvService } from "../../application/einvoice/einv-service.js";
import {
  PrismaEinvInvoiceRepository, PrismaEinvTemplateRepository,
  PrismaEinvSeriesRepository, PrismaEinvInvoiceTypeRepository,
  PrismaEinvProviderRepository, PrismaEinvCertificateRepository,
  PrismaEinvProviderTemplateRepository, PrismaEinvReasonCodeRepository,
  PrismaEinvAdjustmentRepository, PrismaEinvTransmissionRepository,
  PrismaEinvArchiveRepository,
} from "../../infrastructure/einvoice/einv-prisma-repos.js";

@Module({
  controllers: [EinvController],
  providers: [
    EinvService,
    PrismaEinvInvoiceRepository, PrismaEinvTemplateRepository,
    PrismaEinvSeriesRepository, PrismaEinvInvoiceTypeRepository,
    PrismaEinvProviderRepository, PrismaEinvCertificateRepository,
    PrismaEinvProviderTemplateRepository, PrismaEinvReasonCodeRepository,
    PrismaEinvAdjustmentRepository, PrismaEinvTransmissionRepository,
    PrismaEinvArchiveRepository,
  ],
  exports: [
    EinvService,
    PrismaEinvInvoiceRepository, PrismaEinvTemplateRepository,
    PrismaEinvSeriesRepository, PrismaEinvInvoiceTypeRepository,
    PrismaEinvProviderRepository, PrismaEinvCertificateRepository,
    PrismaEinvReasonCodeRepository,
  ],
})
export class EinvModule {}
