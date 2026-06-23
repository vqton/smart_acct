import { DomainError } from "../../shared/domain-error.js";
import { TaxType, TaxTypeId, TaxCategory, TaxNature, TaxBasis, TaxCalculationMethod, TaxPaymentMethod, TaxFilingFrequency } from "../../domain/tax/tax-type.js";
import { TaxTypeRepository } from "../../domain/tax/tax-repositories.js";

export class TaxTypeService {
  constructor(private readonly repo: TaxTypeRepository) {}

  async create(params: {
    code: string; name: string; category: TaxCategory; nature: TaxNature;
    basis: TaxBasis; calculationMethod: TaxCalculationMethod;
    paymentMethod: TaxPaymentMethod; filingFrequency: TaxFilingFrequency;
    parentTaxTypeId?: string;
  }): Promise<TaxType> {
    const existing = await this.repo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Tax type code ${params.code} already exists`);

    const tt = new TaxType(params);
    await this.repo.save(tt);
    return tt;
  }

  async findById(id: string): Promise<TaxType> {
    const tt = await this.repo.findById(new TaxTypeId(id));
    if (!tt) throw new DomainError("NotFound", "Tax type not found");
    return tt;
  }

  async findByCode(code: string): Promise<TaxType | null> {
    return this.repo.findByCode(code);
  }

  async findAll(): Promise<TaxType[]> {
    return this.repo.findAll();
  }

  async findActive(): Promise<TaxType[]> {
    return this.repo.findActive();
  }

  async deactivate(id: string): Promise<void> {
    const tt = await this.repo.findById(new TaxTypeId(id));
    if (!tt) throw new DomainError("NotFound", "Tax type not found");
    tt.deactivate();
    await this.repo.save(tt);
  }
}
