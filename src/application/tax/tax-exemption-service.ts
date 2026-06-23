import { DomainError } from "../../shared/domain-error.js";
import { TaxExemption, TaxExemptionId, IncentiveType, IncentiveApplicationLevel } from "../../domain/tax/tax-incentive.js";
import { TaxExemptionRepository } from "../../domain/tax/tax-repositories.js";

export class TaxExemptionService {
  constructor(private readonly repo: TaxExemptionRepository) {}

  async create(params: {
    code: string; name: string; incentiveType: IncentiveType;
    taxTypeId: string; applicationLevel: IncentiveApplicationLevel; effectiveFrom: Date;
    taxCodeId?: string; taxpayerId?: string; regionId?: string;
    reductionPercent?: number; reductionAmount?: number; maxAmount?: number;
    legalReference?: string;
  }): Promise<TaxExemption> {
    const existing = await this.repo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Exemption code ${params.code} already exists`);

    const exemption = new TaxExemption(params.code, params.name, params.incentiveType, params.taxTypeId, params.applicationLevel, params.effectiveFrom);
    await this.repo.save(exemption);
    return exemption;
  }

  async findById(id: string): Promise<TaxExemption> {
    const ex = await this.repo.findById(new TaxExemptionId(id));
    if (!ex) throw new DomainError("NotFound", "Tax exemption not found");
    return ex;
  }

  async findByCode(code: string): Promise<TaxExemption | null> {
    return this.repo.findByCode(code);
  }

  async findAll(): Promise<TaxExemption[]> {
    return this.repo.findAll();
  }

  async findActive(): Promise<TaxExemption[]> {
    return this.repo.findActive();
  }

  async deactivate(id: string): Promise<void> {
    const ex = await this.repo.findById(new TaxExemptionId(id));
    if (!ex) throw new DomainError("NotFound", "Tax exemption not found");
    ex.deactivate();
    await this.repo.save(ex);
  }
}
