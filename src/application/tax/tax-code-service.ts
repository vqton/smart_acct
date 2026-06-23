import { DomainError } from "../../shared/domain-error.js";
import { TaxCode, TaxCodeId, TaxRate, TaxRateType, TaxRateApplication, RoundingMethod } from "../../domain/tax/tax-code.js";
import { TaxCodeRepository, TaxRateRepository } from "../../domain/tax/tax-repositories.js";

export class TaxCodeService {
  constructor(
    private readonly codeRepo: TaxCodeRepository,
    private readonly rateRepo: TaxRateRepository,
  ) {}

  async create(params: {
    code: string; name: string; taxTypeId: string;
    taxRateType: TaxRateType; application: TaxRateApplication; effectiveFrom: Date;
    roundingMethod?: RoundingMethod; precision?: number;
    isRecoverable?: boolean; isRefundable?: boolean; isDeductible?: boolean;
    glTaxAccountId?: string; glRecoverableAccountId?: string; glExpenseAccountId?: string;
    description?: string;
  }): Promise<TaxCode> {
    const existing = await this.codeRepo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Tax code ${params.code} already exists`);

    const tc = new TaxCode(params.code, params.name, params.taxTypeId, params.taxRateType, params.application, params.effectiveFrom);
    await this.codeRepo.save(tc);
    return tc;
  }

  async findById(id: string): Promise<TaxCode> {
    const tc = await this.codeRepo.findById(new TaxCodeId(id));
    if (!tc) throw new DomainError("NotFound", "Tax code not found");
    return tc;
  }

  async findByCode(code: string): Promise<TaxCode | null> {
    return this.codeRepo.findByCode(code);
  }

  async findAll(): Promise<TaxCode[]> {
    return this.codeRepo.findAll();
  }

  async findActive(): Promise<TaxCode[]> {
    return this.codeRepo.findActive();
  }

  async addRate(taxCodeId: string, params: {
    rate: number; rateType: TaxRateType; effectiveFrom: Date;
  }): Promise<TaxRate> {
    const tc = await this.codeRepo.findById(new TaxCodeId(taxCodeId));
    if (!tc) throw new DomainError("NotFound", "Tax code not found");

    const rate = TaxRate.create(taxCodeId, params.rate, params.rateType, params.effectiveFrom);
    tc.addRate(rate);
    await this.codeRepo.save(tc);
    return rate;
  }

  async findEffectiveRate(taxCodeId: string, date: Date): Promise<TaxRate | null> {
    return this.rateRepo.findEffective(taxCodeId, date);
  }

  async deactivate(id: string): Promise<void> {
    const tc = await this.codeRepo.findById(new TaxCodeId(id));
    if (!tc) throw new DomainError("NotFound", "Tax code not found");
    tc.deactivate();
    await this.codeRepo.save(tc);
  }
}
