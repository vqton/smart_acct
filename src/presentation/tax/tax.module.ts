import { Module } from "@nestjs/common";
import { TaxController } from "./tax.controller.js";
import {
  PrismaTaxTypeRepository,
  PrismaTaxCodeRepository,
  PrismaTaxRateRepository,
  PrismaTaxAuthorityRepository,
  PrismaTaxRegionRepository,
  PrismaTaxRegistrationRepository,
  PrismaTaxReturnRepository,
  PrismaTaxExemptionRepository,
  PrismaTaxPaymentRepository,
  PrismaTaxDeterminationRuleRepository,
} from "../../infrastructure/tax/tax-prisma-repos.js";

@Module({
  controllers: [TaxController],
  providers: [
    PrismaTaxTypeRepository,
    PrismaTaxCodeRepository,
    PrismaTaxRateRepository,
    PrismaTaxAuthorityRepository,
    PrismaTaxRegionRepository,
    PrismaTaxRegistrationRepository,
    PrismaTaxReturnRepository,
    PrismaTaxExemptionRepository,
    PrismaTaxPaymentRepository,
    PrismaTaxDeterminationRuleRepository,
  ],
})
export class TaxModule {}
