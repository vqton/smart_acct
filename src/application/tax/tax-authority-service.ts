import { DomainError } from "../../shared/domain-error.js";
import { TaxAuthority, TaxAuthorityId, TaxRegion, TaxRegionId, JurisdictionLevel, TaxRegionType } from "../../domain/tax/tax-jurisdiction.js";
import { TaxAuthorityRepository, TaxRegionRepository } from "../../domain/tax/tax-repositories.js";

export class TaxAuthorityService {
  constructor(
    private readonly authRepo: TaxAuthorityRepository,
    private readonly regionRepo: TaxRegionRepository,
  ) {}

  async createAuthority(params: {
    code: string; name: string; taxOfficeCode: string; jurisdictionLevel: JurisdictionLevel;
    parentId?: string; address?: string; phone?: string; email?: string; website?: string;
  }): Promise<TaxAuthority> {
    const existing = await this.authRepo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Tax authority code ${params.code} already exists`);

    const auth = new TaxAuthority(params.code, params.name, params.taxOfficeCode, params.jurisdictionLevel);
    await this.authRepo.save(auth);
    return auth;
  }

  async findAuthorityById(id: string): Promise<TaxAuthority> {
    const auth = await this.authRepo.findById(new TaxAuthorityId(id));
    if (!auth) throw new DomainError("NotFound", "Tax authority not found");
    return auth;
  }

  async findAllAuthorities(): Promise<TaxAuthority[]> {
    return this.authRepo.findAll();
  }

  async createRegion(params: {
    code: string; name: string; regionType: TaxRegionType; countryCode: string;
    provinceCode?: string; districtCode?: string; communeCode?: string;
  }): Promise<TaxRegion> {
    const existing = await this.regionRepo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Tax region code ${params.code} already exists`);

    const region = new TaxRegion(params.code, params.name, params.regionType, params.countryCode);
    await this.regionRepo.save(region);
    return region;
  }

  async findRegionById(id: string): Promise<TaxRegion> {
    const region = await this.regionRepo.findById(new TaxRegionId(id));
    if (!region) throw new DomainError("NotFound", "Tax region not found");
    return region;
  }

  async findAllRegions(): Promise<TaxRegion[]> {
    return this.regionRepo.findAll();
  }
}
