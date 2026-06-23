import { DomainError } from "../../shared/domain-error.js";
import { TaxRegistration, TaxRegistrationId, TaxRegistrationStatus } from "../../domain/tax/tax-registration.js";
import { TaxRegistrationRepository } from "../../domain/tax/tax-repositories.js";

export class TaxRegistrationService {
  constructor(private readonly repo: TaxRegistrationRepository) {}

  async create(params: {
    taxpayerId: string; taxTypeId: string; taxAuthorityId: string; registrationNumber: string;
  }): Promise<TaxRegistration> {
    const existing = await this.repo.findByTaxpayerAndType(params.taxpayerId, params.taxTypeId);
    if (existing) throw new DomainError("Conflict", "Registration already exists for this taxpayer and tax type");

    const reg = TaxRegistration.create(params);
    await this.repo.save(reg);
    return reg;
  }

  async findById(id: string): Promise<TaxRegistration> {
    const reg = await this.repo.findById(new TaxRegistrationId(id));
    if (!reg) throw new DomainError("NotFound", "Tax registration not found");
    return reg;
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxRegistration[]> {
    return this.repo.findByTaxpayer(taxpayerId);
  }

  async register(id: string, certNumber: string): Promise<TaxRegistration> {
    const reg = await this.repo.findById(new TaxRegistrationId(id));
    if (!reg) throw new DomainError("NotFound", "Tax registration not found");
    reg.register(certNumber);
    await this.repo.save(reg);
    return reg;
  }

  async suspend(id: string, reason: string): Promise<TaxRegistration> {
    const reg = await this.repo.findById(new TaxRegistrationId(id));
    if (!reg) throw new DomainError("NotFound", "Tax registration not found");
    reg.suspend(reason);
    await this.repo.save(reg);
    return reg;
  }

  async findAll(): Promise<TaxRegistration[]> {
    return this.repo.findAll();
  }

  async revoke(id: string, reason: string): Promise<TaxRegistration> {
    const reg = await this.repo.findById(new TaxRegistrationId(id));
    if (!reg) throw new DomainError("NotFound", "Tax registration not found");
    reg.revoke(reason);
    await this.repo.save(reg);
    return reg;
  }
}
