import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import type {
  TaxTypeRepository,
  TaxCodeRepository,
  TaxRateRepository,
  TaxAuthorityRepository,
  TaxRegionRepository,
  TaxRegistrationRepository,
  TaxReturnRepository,
  TaxExemptionRepository,
  TaxPaymentRepository,
  TaxDeterminationRuleRepository,
} from "../../domain/tax/tax-repositories.js";
import { TaxType, TaxTypeId, type TaxTypeState } from "../../domain/tax/tax-type.js";
import { TaxCode, TaxCodeId, type TaxCodeState, TaxRate, type TaxRateState } from "../../domain/tax/tax-code.js";
import { TaxAuthority, TaxAuthorityId, type TaxAuthorityState, TaxRegion, TaxRegionId, type TaxRegionState } from "../../domain/tax/tax-jurisdiction.js";
import { TaxRegistration, TaxRegistrationId, type TaxRegistrationState } from "../../domain/tax/tax-registration.js";
import { TaxReturn, TaxReturnId, type TaxReturnState, TaxReturnStatus, TaxReturnType, type TaxLineItem } from "../../domain/tax/tax-return.js";
import { TaxExemption, TaxExemptionId, type TaxExemptionState } from "../../domain/tax/tax-incentive.js";
import { TaxPayment, TaxPaymentId, TaxPaymentStatus } from "../../domain/tax/tax-payment.js";
import { TaxDeterminationRule } from "../../domain/tax/tax-calculation.js";

@Injectable()
export class PrismaTaxTypeRepository implements TaxTypeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(t: TaxType): Promise<void> {
    const s = t.toState();
    await (this.prisma as any).taxType.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxTypeId): Promise<TaxType | null> {
    const row = await (this.prisma as any).taxType.findUnique({ where: { id: id.value } });
    return row ? TaxType.load(row as TaxTypeState) : null;
  }

  async findByCode(code: string): Promise<TaxType | null> {
    const row = await (this.prisma as any).taxType.findUnique({ where: { code } });
    return row ? TaxType.load(row as TaxTypeState) : null;
  }

  async findByCategory(category: string): Promise<TaxType[]> {
    const rows = await (this.prisma as any).taxType.findMany({ where: { category } });
    return rows.map((r: any) => TaxType.load(r as TaxTypeState));
  }

  async findAll(): Promise<TaxType[]> {
    const rows = await (this.prisma as any).taxType.findMany();
    return rows.map((r: any) => TaxType.load(r as TaxTypeState));
  }

  async findActive(): Promise<TaxType[]> {
    const rows = await (this.prisma as any).taxType.findMany({ where: { isActive: true } });
    return rows.map((r: any) => TaxType.load(r as TaxTypeState));
  }
}

@Injectable()
export class PrismaTaxCodeRepository implements TaxCodeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(tc: TaxCode): Promise<void> {
    const s = tc.toState();
    const { rates: _rates, ...scalars } = s;
    await (this.prisma as any).taxCode.upsert({
      where: { id: s.id },
      create: scalars,
      update: scalars,
    });
  }

  async findById(id: TaxCodeId): Promise<TaxCode | null> {
    const row = await (this.prisma as any).taxCode.findUnique({ where: { id: id.value }, include: { rates: true } });
    return row ? TaxCode.load(row as TaxCodeState) : null;
  }

  async findByCode(code: string): Promise<TaxCode | null> {
    const row = await (this.prisma as any).taxCode.findUnique({ where: { code }, include: { rates: true } });
    return row ? TaxCode.load(row as TaxCodeState) : null;
  }

  async findByTaxType(taxTypeId: string): Promise<TaxCode[]> {
    const rows = await (this.prisma as any).taxCode.findMany({ where: { taxTypeId }, include: { rates: true } });
    return rows.map((r: any) => TaxCode.load(r as TaxCodeState));
  }

  async findActive(): Promise<TaxCode[]> {
    const rows = await (this.prisma as any).taxCode.findMany({ where: { isActive: true }, include: { rates: true } });
    return rows.map((r: any) => TaxCode.load(r as TaxCodeState));
  }

  async findAll(): Promise<TaxCode[]> {
    const rows = await (this.prisma as any).taxCode.findMany({ include: { rates: true } });
    return rows.map((r: any) => TaxCode.load(r as TaxCodeState));
  }
}

@Injectable()
export class PrismaTaxRateRepository implements TaxRateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(r: TaxRate): Promise<void> {
    const s = r.toState();
    await (this.prisma as any).taxRate.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: string): Promise<TaxRate | null> {
    const row = await (this.prisma as any).taxRate.findUnique({ where: { id } });
    return row ? TaxRate.load(row as TaxRateState) : null;
  }

  async findByTaxCode(taxCodeId: string): Promise<TaxRate[]> {
    const rows = await (this.prisma as any).taxRate.findMany({ where: { taxCodeId } });
    return rows.map((r: any) => TaxRate.load(r as TaxRateState));
  }

  async findEffective(taxCodeId: string, date: Date): Promise<TaxRate | null> {
    const row = await (this.prisma as any).taxRate.findFirst({
      where: {
        taxCodeId,
        effectiveFrom: { lte: date },
        effectiveTo: { gte: date },
        isActive: true,
      },
      orderBy: { priority: "desc" },
    });
    return row ? TaxRate.load(row as TaxRateState) : null;
  }
}

@Injectable()
export class PrismaTaxAuthorityRepository implements TaxAuthorityRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(a: TaxAuthority): Promise<void> {
    const s = a.toState();
    await (this.prisma as any).taxAuthority.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxAuthorityId): Promise<TaxAuthority | null> {
    const row = await (this.prisma as any).taxAuthority.findUnique({ where: { id: id.value } });
    return row ? TaxAuthority.load(row as TaxAuthorityState) : null;
  }

  async findByCode(code: string): Promise<TaxAuthority | null> {
    const row = await (this.prisma as any).taxAuthority.findUnique({ where: { code } });
    return row ? TaxAuthority.load(row as TaxAuthorityState) : null;
  }

  async findByLevel(level: string): Promise<TaxAuthority[]> {
    const rows = await (this.prisma as any).taxAuthority.findMany({ where: { jurisdictionLevel: level } });
    return rows.map((r: any) => TaxAuthority.load(r as TaxAuthorityState));
  }

  async findAll(): Promise<TaxAuthority[]> {
    const rows = await (this.prisma as any).taxAuthority.findMany();
    return rows.map((r: any) => TaxAuthority.load(r as TaxAuthorityState));
  }
}

@Injectable()
export class PrismaTaxRegionRepository implements TaxRegionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(r: TaxRegion): Promise<void> {
    const s = r.toState();
    await (this.prisma as any).taxRegion.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxRegionId): Promise<TaxRegion | null> {
    const row = await (this.prisma as any).taxRegion.findUnique({ where: { id: id.value } });
    return row ? TaxRegion.load(row as TaxRegionState) : null;
  }

  async findByCode(code: string): Promise<TaxRegion | null> {
    const row = await (this.prisma as any).taxRegion.findUnique({ where: { code } });
    return row ? TaxRegion.load(row as TaxRegionState) : null;
  }

  async findByType(type: string): Promise<TaxRegion[]> {
    const rows = await (this.prisma as any).taxRegion.findMany({ where: { type } });
    return rows.map((r: any) => TaxRegion.load(r as TaxRegionState));
  }

  async findByLocation(provinceCode?: string, districtCode?: string): Promise<TaxRegion[]> {
    const where: Record<string, unknown> = {};
    if (provinceCode) where.provinceCode = provinceCode;
    if (districtCode) where.districtCode = districtCode;
    const rows = await (this.prisma as any).taxRegion.findMany({ where });
    return rows.map((r: any) => TaxRegion.load(r as TaxRegionState));
  }

  async findAll(): Promise<TaxRegion[]> {
    const rows = await (this.prisma as any).taxRegion.findMany();
    return rows.map((r: any) => TaxRegion.load(r as TaxRegionState));
  }
}

@Injectable()
export class PrismaTaxRegistrationRepository implements TaxRegistrationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(r: TaxRegistration): Promise<void> {
    const s = r.toState();
    await (this.prisma as any).taxRegistration.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxRegistrationId): Promise<TaxRegistration | null> {
    const row = await (this.prisma as any).taxRegistration.findUnique({ where: { id: id.value } });
    return row ? TaxRegistration.load(row as TaxRegistrationState) : null;
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxRegistration[]> {
    const rows = await (this.prisma as any).taxRegistration.findMany({ where: { taxpayerId } });
    return rows.map((r: any) => TaxRegistration.load(r as TaxRegistrationState));
  }

  async findByTaxType(taxTypeId: string): Promise<TaxRegistration[]> {
    const rows = await (this.prisma as any).taxRegistration.findMany({ where: { taxTypeId } });
    return rows.map((r: any) => TaxRegistration.load(r as TaxRegistrationState));
  }

  async findByTaxpayerAndType(taxpayerId: string, taxTypeId: string): Promise<TaxRegistration | null> {
    const row = await (this.prisma as any).taxRegistration.findFirst({
      where: { taxpayerId, taxTypeId },
    });
    return row ? TaxRegistration.load(row as TaxRegistrationState) : null;
  }

  async findActiveByTaxpayer(taxpayerId: string): Promise<TaxRegistration[]> {
    const rows = await (this.prisma as any).taxRegistration.findMany({
      where: { taxpayerId, status: "active" },
    });
    return rows.map((r: any) => TaxRegistration.load(r as TaxRegistrationState));
  }

  async findAll(): Promise<TaxRegistration[]> {
    const rows = await (this.prisma as any).taxRegistration.findMany();
    return rows.map((r: any) => TaxRegistration.load(r as TaxRegistrationState));
  }
}

@Injectable()
export class PrismaTaxReturnRepository implements TaxReturnRepository {
  constructor(private readonly prisma: PrismaService) {}

  private toDomain(row: Record<string, unknown>): TaxReturn {
    return TaxReturn.load({
      ...row,
      lines: (row as any).lines ?? [],
      attachments: (row as any).attachments ?? [],
    } as unknown as TaxReturnState);
  }

  async save(tr: TaxReturn): Promise<void> {
    const s = tr.toState();
    const { lines: _lines, attachments: _attachments, ...scalars } = s;
    await (this.prisma as any).taxReturn.upsert({
      where: { id: s.id },
      create: scalars,
      update: scalars,
    });
  }

  async findById(id: TaxReturnId): Promise<TaxReturn | null> {
    const row = await (this.prisma as any).taxReturn.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByReturnNumber(returnNumber: string): Promise<TaxReturn | null> {
    const row = await (this.prisma as any).taxReturn.findUnique({ where: { returnNumber } });
    return row ? this.toDomain(row as any) : null;
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany({ where: { taxpayerId } });
    return rows.map((r: any) => this.toDomain(r));
  }

  async findByPeriod(periodId: string): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany({ where: { periodId } });
    return rows.map((r: any) => this.toDomain(r));
  }

  async findByStatus(status: TaxReturnStatus): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany({ where: { status } });
    return rows.map((r: any) => this.toDomain(r));
  }

  async findByTaxType(taxTypeId: string): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany({ where: { taxTypeId } });
    return rows.map((r: any) => this.toDomain(r));
  }

  async findPending(): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany({
      where: { status: { in: ["draft", "prepared", "submitted"] } },
    });
    return rows.map((r: any) => this.toDomain(r));
  }

  async findAll(): Promise<TaxReturn[]> {
    const rows = await (this.prisma as any).taxReturn.findMany();
    return rows.map((r: any) => this.toDomain(r));
  }
}

@Injectable()
export class PrismaTaxExemptionRepository implements TaxExemptionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(e: TaxExemption): Promise<void> {
    const s = e.toState();
    await (this.prisma as any).taxExemption.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxExemptionId): Promise<TaxExemption | null> {
    const row = await (this.prisma as any).taxExemption.findUnique({ where: { id: id.value } });
    return row ? TaxExemption.load(row as TaxExemptionState) : null;
  }

  async findByCode(code: string): Promise<TaxExemption | null> {
    const row = await (this.prisma as any).taxExemption.findUnique({ where: { code } });
    return row ? TaxExemption.load(row as TaxExemptionState) : null;
  }

  async findByTaxType(taxTypeId: string): Promise<TaxExemption[]> {
    const rows = await (this.prisma as any).taxExemption.findMany({ where: { taxTypeId } });
    return rows.map((r: any) => TaxExemption.load(r as TaxExemptionState));
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxExemption[]> {
    const rows = await (this.prisma as any).taxExemption.findMany({ where: { taxpayerId } });
    return rows.map((r: any) => TaxExemption.load(r as TaxExemptionState));
  }

  async findActive(): Promise<TaxExemption[]> {
    const rows = await (this.prisma as any).taxExemption.findMany({
      where: { status: "active" },
    });
    return rows.map((r: any) => TaxExemption.load(r as TaxExemptionState));
  }

  async findApplicable(taxCodeId: string, taxpayerId: string, date: Date): Promise<TaxExemption[]> {
    const rows = await (this.prisma as any).taxExemption.findMany({
      where: {
        taxCodeId,
        taxpayerId,
        status: "active",
        validFrom: { lte: date },
        validTo: { gte: date },
      },
    });
    return rows.map((r: any) => TaxExemption.load(r as TaxExemptionState));
  }

  async findAll(): Promise<TaxExemption[]> {
    const rows = await (this.prisma as any).taxExemption.findMany();
    return rows.map((r: any) => TaxExemption.load(r as TaxExemptionState));
  }
}

@Injectable()
export class PrismaTaxPaymentRepository implements TaxPaymentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(p: TaxPayment): Promise<void> {
    const s = p.toState();
    await (this.prisma as any).taxPayment.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: TaxPaymentId): Promise<TaxPayment | null> {
    const row = await (this.prisma as any).taxPayment.findUnique({ where: { id: id.value } });
    return row ? TaxPayment.load(row as any) : null;
  }

  async findByTaxReturn(taxReturnId: string): Promise<TaxPayment[]> {
    const rows = await (this.prisma as any).taxPayment.findMany({ where: { taxReturnId } });
    return rows.map((r: any) => TaxPayment.load(r as any));
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxPayment[]> {
    const rows = await (this.prisma as any).taxPayment.findMany({ where: { taxpayerId } });
    return rows.map((r: any) => TaxPayment.load(r as any));
  }

  async findByStatus(status: TaxPaymentStatus): Promise<TaxPayment[]> {
    const rows = await (this.prisma as any).taxPayment.findMany({ where: { status } });
    return rows.map((r: any) => TaxPayment.load(r as any));
  }

  async findAll(): Promise<TaxPayment[]> {
    const rows = await (this.prisma as any).taxPayment.findMany();
    return rows.map((r: any) => TaxPayment.load(r as any));
  }
}

@Injectable()
export class PrismaTaxDeterminationRuleRepository implements TaxDeterminationRuleRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rule: TaxDeterminationRule): Promise<void> {
    await (this.prisma as any).taxDeterminationRule.upsert({
      where: { id: rule.id },
      create: rule as any,
      update: rule as any,
    });
  }

  async findAll(): Promise<TaxDeterminationRule[]> {
    const rows = await (this.prisma as any).taxDeterminationRule.findMany({
      orderBy: { ruleOrder: "asc" },
    });
    return rows as any;
  }

  async findByProductCategory(category: string): Promise<TaxDeterminationRule[]> {
    const rows = await (this.prisma as any).taxDeterminationRule.findMany({
      where: { conditionValue: category },
      orderBy: { ruleOrder: "asc" },
    });
    return rows as any;
  }

  async findByHsCode(hsCode: string): Promise<TaxDeterminationRule[]> {
    const rows = await (this.prisma as any).taxDeterminationRule.findMany({
      where: { conditionValue: hsCode },
      orderBy: { ruleOrder: "asc" },
    });
    return rows as any;
  }

  async findEffective(date: Date): Promise<TaxDeterminationRule[]> {
    const rows = await (this.prisma as any).taxDeterminationRule.findMany({
      where: {
        isActive: true,
        effectiveFrom: { lte: date },
        effectiveTo: { gte: date },
      },
      orderBy: { ruleOrder: "asc" },
    });
    return rows as any;
  }
}
