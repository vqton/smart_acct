import { Controller, Get, Post, Param, Body, NotFoundException, ConflictException, Query } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaTaxTypeRepository, PrismaTaxCodeRepository, PrismaTaxRateRepository, PrismaTaxAuthorityRepository, PrismaTaxRegionRepository, PrismaTaxRegistrationRepository, PrismaTaxReturnRepository, PrismaTaxExemptionRepository, PrismaTaxPaymentRepository } from "../../infrastructure/tax/tax-prisma-repos.js";
import { TaxType, TaxTypeId } from "../../domain/tax/tax-type.js";
import { TaxCode, TaxCodeId, TaxRate, TaxRateType } from "../../domain/tax/tax-code.js";
import { TaxAuthority, TaxAuthorityId, TaxRegion, TaxRegionId } from "../../domain/tax/tax-jurisdiction.js";
import { TaxRegistration, TaxRegistrationId } from "../../domain/tax/tax-registration.js";
import { TaxReturn, TaxReturnId } from "../../domain/tax/tax-return.js";
import { TaxExemption, TaxExemptionId } from "../../domain/tax/tax-incentive.js";
import { TaxPayment, TaxPaymentId } from "../../domain/tax/tax-payment.js";
import { CreateTaxTypeDto, CreateTaxCodeDto, CreateTaxAuthorityDto, CreateTaxRegionDto, CreateTaxRegistrationDto, CreateTaxReturnDto, CreateTaxExemptionDto, CreateTaxPaymentDto, CalculateTaxDto } from "./dto/tax.dto.js";

@ApiTags("Tax")
@Controller("api/tax")
export class TaxController {
  constructor(
    private readonly taxTypeRepo: PrismaTaxTypeRepository,
    private readonly taxCodeRepo: PrismaTaxCodeRepository,
    private readonly taxRateRepo: PrismaTaxRateRepository,
    private readonly taxAuthorityRepo: PrismaTaxAuthorityRepository,
    private readonly taxRegionRepo: PrismaTaxRegionRepository,
    private readonly taxRegistrationRepo: PrismaTaxRegistrationRepository,
    private readonly taxReturnRepo: PrismaTaxReturnRepository,
    private readonly taxExemptionRepo: PrismaTaxExemptionRepository,
    private readonly taxPaymentRepo: PrismaTaxPaymentRepository,
  ) {}

  // --- Tax Types ---
  @Post("types")
  @ApiOperation({ summary: "Create a tax type" })
  async createTaxType(@Body() dto: CreateTaxTypeDto) {
    const c = await this.taxTypeRepo.findByCode(dto.code);
    if (c) throw new ConflictException(`Tax type ${dto.code} already exists`);
    const e = new TaxType(dto);
    await this.taxTypeRepo.save(e);
    return e.toState();
  }

  @Get("types")
  @ApiOperation({ summary: "List tax types" })
  async listTaxTypes() { return this.taxTypeRepo.findAll(); }

  @Get("types/:id")
  @ApiOperation({ summary: "Get tax type by ID" })
  async getTaxType(@Param("id") id: string) {
    const e = await this.taxTypeRepo.findById(new TaxTypeId(id));
    if (!e) throw new NotFoundException("Tax type not found");
    return e.toState();
  }

  // --- Tax Codes ---
  @Post("codes")
  @ApiOperation({ summary: "Create a tax code" })
  async createTaxCode(@Body() dto: CreateTaxCodeDto) {
    const c = await this.taxCodeRepo.findByCode(dto.code);
    if (c) throw new ConflictException(`Tax code ${dto.code} already exists`);
    const e = new TaxCode(dto.code, dto.name, dto.taxTypeId, dto.taxRateType, dto.application, new Date(dto.effectiveFrom ?? new Date()));
    if (dto.rate !== undefined) {
      const r = TaxRate.create(dto.taxTypeId ?? "", dto.rate, dto.rateType ?? TaxRateType.Percentage, new Date(dto.effectiveFrom ?? new Date()));
      (e as any).addRate(r);
    }
    await this.taxCodeRepo.save(e);
    return e.toState();
  }

  @Get("codes")
  @ApiOperation({ summary: "List tax codes" })
  async listTaxCodes(@Query("taxTypeId") taxTypeId?: string) {
    if (taxTypeId) return this.taxCodeRepo.findByTaxType(taxTypeId);
    return this.taxCodeRepo.findAll();
  }

  @Get("codes/:id")
  @ApiOperation({ summary: "Get tax code by ID" })
  async getTaxCode(@Param("id") id: string) {
    const e = await this.taxCodeRepo.findById(new TaxCodeId(id));
    if (!e) throw new NotFoundException("Tax code not found");
    return e.toState();
  }

  // --- Authorities ---
  @Post("authorities")
  @ApiOperation({ summary: "Create a tax authority" })
  async createTaxAuthority(@Body() dto: CreateTaxAuthorityDto) {
    const c = await this.taxAuthorityRepo.findByCode(dto.code);
    if (c) throw new ConflictException(`Authority ${dto.code} already exists`);
    const e = new TaxAuthority(dto.code, dto.name, dto.taxOfficeCode, dto.jurisdictionLevel);
    await this.taxAuthorityRepo.save(e);
    return e.toState();
  }

  @Get("authorities")
  @ApiOperation({ summary: "List authorities" })
  async listAuthorities(@Query("level") level?: string) {
    if (level) return this.taxAuthorityRepo.findByLevel(level);
    return this.taxAuthorityRepo.findAll();
  }

  @Get("authorities/:id")
  @ApiOperation({ summary: "Get authority by ID" })
  async getAuthority(@Param("id") id: string) {
    const e = await this.taxAuthorityRepo.findById(new TaxAuthorityId(id));
    if (!e) throw new NotFoundException("Authority not found");
    return e.toState();
  }

  // --- Regions ---
  @Post("regions")
  @ApiOperation({ summary: "Create a tax region" })
  async createRegion(@Body() dto: CreateTaxRegionDto) {
    const c = await this.taxRegionRepo.findByCode(dto.code);
    if (c) throw new ConflictException(`Region ${dto.code} already exists`);
    const e = new TaxRegion(dto.code, dto.name, dto.type, dto.countryCode ?? "VN");
    await this.taxRegionRepo.save(e);
    return e.toState();
  }

  @Get("regions")
  @ApiOperation({ summary: "List regions" })
  async listRegions() { return this.taxRegionRepo.findAll(); }

  @Get("regions/:id")
  @ApiOperation({ summary: "Get region by ID" })
  async getRegion(@Param("id") id: string) {
    const e = await this.taxRegionRepo.findById(new TaxRegionId(id));
    if (!e) throw new NotFoundException("Region not found");
    return e.toState();
  }

  // --- Registrations ---
  @Post("registrations")
  @ApiOperation({ summary: "Create a tax registration" })
  async createRegistration(@Body() dto: CreateTaxRegistrationDto) {
    const c = await this.taxRegistrationRepo.findByTaxpayerAndType(dto.taxpayerId, dto.taxTypeId);
    if (c) throw new ConflictException("Registration already exists");
    const e = TaxRegistration.create({ registrationNumber: dto.registrationNumber, taxpayerId: dto.taxpayerId, taxTypeId: dto.taxTypeId, taxAuthorityId: dto.taxAuthorityId });
    await this.taxRegistrationRepo.save(e);
    return e.toState();
  }

  @Get("registrations")
  @ApiOperation({ summary: "List registrations" })
  async listRegistrations(@Query("taxpayerId") id?: string) {
    if (id) return this.taxRegistrationRepo.findByTaxpayer(id);
    return this.taxRegistrationRepo.findAll();
  }

  @Get("registrations/:id")
  @ApiOperation({ summary: "Get registration by ID" })
  async getRegistration(@Param("id") id: string) {
    const e = await this.taxRegistrationRepo.findById(new TaxRegistrationId(id));
    if (!e) throw new NotFoundException("Registration not found");
    return e.toState();
  }

  // --- Returns ---
  @Post("returns")
  @ApiOperation({ summary: "Create a tax return" })
  async createReturn(@Body() dto: CreateTaxReturnDto) {
    const e = TaxReturn.create({ returnNumber: dto.returnNumber, returnType: dto.returnType, taxTypeId: dto.taxTypeId, taxpayerId: dto.taxpayerId, taxAuthorityId: dto.taxAuthorityId, periodId: dto.periodId, fiscalYearId: dto.fiscalYearId, filingDate: new Date(dto.filingDate ?? new Date()), dueDate: new Date(dto.dueDate ?? new Date()), createdById: dto.createdById ?? "system" });
    await this.taxReturnRepo.save(e);
    return e.toState();
  }

  @Get("returns")
  @ApiOperation({ summary: "List returns" })
  async listReturns(@Query("taxpayerId") id?: string, @Query("status") s?: string) {
    if (id) return this.taxReturnRepo.findByTaxpayer(id);
    if (s) return this.taxReturnRepo.findByStatus(s as any);
    return this.taxReturnRepo.findAll();
  }

  @Get("returns/:id")
  @ApiOperation({ summary: "Get return by ID" })
  async getReturn(@Param("id") id: string) {
    const e = await this.taxReturnRepo.findById(new TaxReturnId(id));
    if (!e) throw new NotFoundException("Return not found");
    return e.toState();
  }

  // --- Exemptions ---
  @Post("exemptions")
  @ApiOperation({ summary: "Create a tax exemption" })
  async createExemption(@Body() dto: CreateTaxExemptionDto) {
    const c = await this.taxExemptionRepo.findByCode(dto.code);
    if (c) throw new ConflictException(`Exemption ${dto.code} already exists`);
    const e = new TaxExemption(dto.code, dto.name, dto.exemptionType, dto.taxTypeId, dto.applicationLevel, new Date(dto.validFrom ?? new Date()));
    await this.taxExemptionRepo.save(e);
    return e.toState();
  }

  @Get("exemptions")
  @ApiOperation({ summary: "List exemptions" })
  async listExemptions() { return this.taxExemptionRepo.findAll(); }

  @Get("exemptions/:id")
  @ApiOperation({ summary: "Get exemption by ID" })
  async getExemption(@Param("id") id: string) {
    const e = await this.taxExemptionRepo.findById(new TaxExemptionId(id));
    if (!e) throw new NotFoundException("Exemption not found");
    return e.toState();
  }

  // --- Payments ---
  @Post("payments")
  @ApiOperation({ summary: "Create a tax payment" })
  async createPayment(@Body() dto: CreateTaxPaymentDto) {
    const e = TaxPayment.create({ taxReturnId: dto.taxReturnId, taxpayerId: dto.taxpayerId, taxTypeId: dto.taxTypeId, amount: dto.amount, paymentMethod: dto.paymentMethod, paymentDate: new Date(dto.paymentDate ?? new Date()), referenceNumber: dto.referenceNumber ?? "", paidById: dto.paidById ?? "system" });
    await this.taxPaymentRepo.save(e);
    return e.toState();
  }

  @Get("payments")
  @ApiOperation({ summary: "List payments" })
  async listPayments(@Query("taxpayerId") id?: string, @Query("status") s?: string) {
    if (id) return this.taxPaymentRepo.findByTaxpayer(id);
    if (s) return this.taxPaymentRepo.findByStatus(s as any);
    return this.taxPaymentRepo.findAll();
  }

  @Get("payments/:id")
  @ApiOperation({ summary: "Get payment by ID" })
  async getPayment(@Param("id") id: string) {
    const e = await this.taxPaymentRepo.findById(new TaxPaymentId(id));
    if (!e) throw new NotFoundException("Payment not found");
    return e.toState();
  }

  // --- Calculation ---
  @Post("calculation/calculate")
  @ApiOperation({ summary: "Calculate tax" })
  async calculate(@Body() dto: CalculateTaxDto) {
    const tc = await this.taxCodeRepo.findById(new TaxCodeId(dto.taxCodeId));
    if (!tc) throw new NotFoundException("Tax code not found");
    const rate = await this.taxRateRepo.findEffective(dto.taxCodeId, new Date(dto.date ?? new Date()));
    if (!rate) throw new NotFoundException("No effective rate found");
    const taxAmount = (dto.amount * Number(rate.rate)) / 100;
    return { grossAmount: dto.amount, taxRate: Number(rate.rate), taxAmount, netAmount: dto.amount + taxAmount };
  }
}
