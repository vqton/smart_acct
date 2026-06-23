import { TaxCalculationEngine, TaxCalculationRequest, TaxCalculationResult } from "../../domain/tax/tax-calculation.js";
import { TaxCodeRepository } from "../../domain/tax/tax-repositories.js";
import { TaxExemptionRepository } from "../../domain/tax/tax-repositories.js";
import { TaxCodeId } from "../../domain/tax/tax-code.js";

export class TaxCalculationService {
  private engine: TaxCalculationEngine;

  constructor(
    taxCodeRepo: TaxCodeRepository,
    exemptionRepo: TaxExemptionRepository,
  ) {
    this.engine = new TaxCalculationEngine(
      async (id) => taxCodeRepo.findById(TaxCodeId.from(id)),
      async (taxCodeId, taxpayerId, date) => exemptionRepo.findApplicable(taxCodeId, taxpayerId, date),
    );
  }

  async calculate(req: TaxCalculationRequest): Promise<TaxCalculationResult> {
    return this.engine.calculate(req);
  }
}
