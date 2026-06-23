import { TaxType, TaxTypeId, TaxTypeState } from "./tax-type.js";
import { TaxCode, TaxCodeId, TaxCodeState, TaxRate, TaxRateState } from "./tax-code.js";
import { TaxAuthority, TaxAuthorityId, TaxAuthorityState } from "./tax-jurisdiction.js";
import { TaxRegion, TaxRegionId, TaxRegionState } from "./tax-jurisdiction.js";
import { TaxRegistration, TaxRegistrationId, TaxRegistrationState } from "./tax-registration.js";
import { TaxReturn, TaxReturnId, TaxReturnState, TaxReturnStatus, TaxReturnType, TaxLineItem } from "./tax-return.js";
import { TaxExemption, TaxExemptionId, TaxExemptionState } from "./tax-incentive.js";
import { TaxPayment, TaxPaymentId, TaxPaymentStatus } from "./tax-payment.js";
import { TaxDeterminationRule } from "./tax-calculation.js";

export interface TaxTypeRepository {
  save(t: TaxType): Promise<void>;
  findById(id: TaxTypeId): Promise<TaxType | null>;
  findByCode(code: string): Promise<TaxType | null>;
  findByCategory(category: string): Promise<TaxType[]>;
  findAll(): Promise<TaxType[]>;
  findActive(): Promise<TaxType[]>;
}

export interface TaxCodeRepository {
  save(tc: TaxCode): Promise<void>;
  findById(id: TaxCodeId): Promise<TaxCode | null>;
  findByCode(code: string): Promise<TaxCode | null>;
  findByTaxType(taxTypeId: string): Promise<TaxCode[]>;
  findActive(): Promise<TaxCode[]>;
  findAll(): Promise<TaxCode[]>;
}

export interface TaxRateRepository {
  save(r: TaxRate): Promise<void>;
  findById(id: string): Promise<TaxRate | null>;
  findByTaxCode(taxCodeId: string): Promise<TaxRate[]>;
  findEffective(taxCodeId: string, date: Date): Promise<TaxRate | null>;
}

export interface TaxAuthorityRepository {
  save(a: TaxAuthority): Promise<void>;
  findById(id: TaxAuthorityId): Promise<TaxAuthority | null>;
  findByCode(code: string): Promise<TaxAuthority | null>;
  findByLevel(level: string): Promise<TaxAuthority[]>;
  findAll(): Promise<TaxAuthority[]>;
}

export interface TaxRegionRepository {
  save(r: TaxRegion): Promise<void>;
  findById(id: TaxRegionId): Promise<TaxRegion | null>;
  findByCode(code: string): Promise<TaxRegion | null>;
  findByType(type: string): Promise<TaxRegion[]>;
  findByLocation(provinceCode?: string, districtCode?: string): Promise<TaxRegion[]>;
  findAll(): Promise<TaxRegion[]>;
}

export interface TaxRegistrationRepository {
  save(r: TaxRegistration): Promise<void>;
  findById(id: TaxRegistrationId): Promise<TaxRegistration | null>;
  findByTaxpayer(taxpayerId: string): Promise<TaxRegistration[]>;
  findByTaxType(taxTypeId: string): Promise<TaxRegistration[]>;
  findByTaxpayerAndType(taxpayerId: string, taxTypeId: string): Promise<TaxRegistration | null>;
  findActiveByTaxpayer(taxpayerId: string): Promise<TaxRegistration[]>;
  findAll(): Promise<TaxRegistration[]>;
}

export interface TaxReturnRepository {
  save(tr: TaxReturn): Promise<void>;
  findById(id: TaxReturnId): Promise<TaxReturn | null>;
  findByReturnNumber(returnNumber: string): Promise<TaxReturn | null>;
  findByTaxpayer(taxpayerId: string): Promise<TaxReturn[]>;
  findByPeriod(periodId: string): Promise<TaxReturn[]>;
  findByStatus(status: TaxReturnStatus): Promise<TaxReturn[]>;
  findByTaxType(taxTypeId: string): Promise<TaxReturn[]>;
  findPending(): Promise<TaxReturn[]>;
  findAll(): Promise<TaxReturn[]>;
}

export interface TaxExemptionRepository {
  save(e: TaxExemption): Promise<void>;
  findById(id: TaxExemptionId): Promise<TaxExemption | null>;
  findByCode(code: string): Promise<TaxExemption | null>;
  findByTaxType(taxTypeId: string): Promise<TaxExemption[]>;
  findByTaxpayer(taxpayerId: string): Promise<TaxExemption[]>;
  findActive(): Promise<TaxExemption[]>;
  findApplicable(taxCodeId: string, taxpayerId: string, date: Date): Promise<TaxExemption[]>;
  findAll(): Promise<TaxExemption[]>;
}

export interface TaxPaymentRepository {
  save(p: TaxPayment): Promise<void>;
  findById(id: TaxPaymentId): Promise<TaxPayment | null>;
  findByTaxReturn(taxReturnId: string): Promise<TaxPayment[]>;
  findByTaxpayer(taxpayerId: string): Promise<TaxPayment[]>;
  findByStatus(status: TaxPaymentStatus): Promise<TaxPayment[]>;
  findAll(): Promise<TaxPayment[]>;
}

export interface TaxDeterminationRuleRepository {
  save(rule: TaxDeterminationRule): Promise<void>;
  findAll(): Promise<TaxDeterminationRule[]>;
  findByProductCategory(category: string): Promise<TaxDeterminationRule[]>;
  findByHsCode(hsCode: string): Promise<TaxDeterminationRule[]>;
  findEffective(date: Date): Promise<TaxDeterminationRule[]>;
}
