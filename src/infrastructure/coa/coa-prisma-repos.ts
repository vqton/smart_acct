import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { AccountClass, AccountClassState } from "../../domain/coa/account-class.js";
import { AccountType, AccountTypeState } from "../../domain/coa/account-type.js";
import { AccountMapping, AccountMappingState } from "../../domain/coa/account-mapping.js";
import { AccountExtension, AccountExtensionState } from "../../domain/coa/account-extension.js";
import { AccountClassId, AccountTypeId, AccountMappingId, AccountExtensionId } from "../../domain/coa/coa-ids.js";
import {
  AccountClassRepository, AccountTypeRepository,
  AccountMappingRepository, AccountExtensionRepository,
} from "../../domain/coa/coa-repositories.js";
import {
  AccountClassType, AccountTypeCategory, AccountSubType,
  AccountMappingStandard, AccountMappingType,
  AccountEffectiveStatus, AccountControlLevel, DimensionRequirement,
} from "../../domain/coa/coa-enums.js";
import { AccountNature } from "../../domain/gl/account-category.js";
import { DomainError } from "../../shared/domain-error.js";

function fromPrismaClass(row: Record<string, unknown>): AccountClass {
  return AccountClass.load({
    id: row.id as string,
    code: row.code as string,
    name: row.name as string,
    nameEn: (row.nameEn as string) ?? null,
    classType: row.classType as AccountClassType,
    description: (row.description as string) ?? null,
    displayOrder: row.displayOrder as number,
    isActive: row.isActive as boolean,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
  });
}

function fromPrismaType(row: Record<string, unknown>): AccountType {
  return AccountType.load({
    id: row.id as string,
    classId: row.classId as string,
    code: row.code as string,
    name: row.name as string,
    nameEn: (row.nameEn as string) ?? null,
    category: row.category as AccountTypeCategory,
    subType: (row.subType as AccountSubType) ?? null,
    nature: row.nature as AccountNature,
    description: (row.description as string) ?? null,
    parentTypeId: (row.parentTypeId as string) ?? null,
    isActive: row.isActive as boolean,
    displayOrder: row.displayOrder as number,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
  });
}

function fromPrismaMapping(row: Record<string, unknown>): AccountMapping {
  return AccountMapping.load({
    id: row.id as string,
    accountId: row.accountId as string,
    mappingStandard: row.mappingStandard as AccountMappingStandard,
    mappingType: row.mappingType as AccountMappingType,
    targetCode: row.targetCode as string,
    targetName: (row.targetName as string) ?? null,
    mappingRule: (row.mappingRule as string) ?? null,
    percentage: row.percentage ? Number(row.percentage) : null,
    effectiveFrom: row.effectiveFrom as Date,
    effectiveTo: (row.effectiveTo as Date) ?? null,
    isActive: row.isActive as boolean,
    description: (row.description as string) ?? null,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
  });
}

function fromPrismaExtension(row: Record<string, unknown>): AccountExtension {
  return AccountExtension.load({
    id: row.id as string,
    accountId: row.accountId as string,
    typeId: (row.typeId as string) ?? null,
    effectiveStatus: row.effectiveStatus as AccountEffectiveStatus,
    effectiveFrom: (row.effectiveFrom as Date) ?? null,
    effectiveTo: (row.effectiveTo as Date) ?? null,
    statusReason: (row.statusReason as string) ?? null,
    allowAutoPosting: row.allowAutoPosting as boolean,
    requireApproval: row.requireApproval as boolean,
    budgetControlLevel: row.budgetControlLevel as AccountControlLevel,
    budgetCheckMessage: (row.budgetCheckMessage as string) ?? null,
    defaultCostCenterId: (row.defaultCostCenterId as string) ?? null,
    defaultDepartmentId: (row.defaultDepartmentId as string) ?? null,
    defaultProjectId: (row.defaultProjectId as string) ?? null,
    defaultBranchId: (row.defaultBranchId as string) ?? null,
    costCenterRequired: row.costCenterRequired as DimensionRequirement,
    departmentRequired: row.departmentRequired as DimensionRequirement,
    projectRequired: row.projectRequired as DimensionRequirement,
    branchRequired: row.branchRequired as DimensionRequirement,
    profitCenterRequired: row.profitCenterRequired as DimensionRequirement,
    isCashAccount: row.isCashAccount as boolean,
    isBankAccount: row.isBankAccount as boolean,
    isTaxAccount: row.isTaxAccount as boolean,
    isInventoryAccount: row.isInventoryAccount as boolean,
    isReceivableAccount: row.isReceivableAccount as boolean,
    isPayableAccount: row.isPayableAccount as boolean,
    isIntercompanyAccount: row.isIntercompanyAccount as boolean,
    defaultTaxCodeId: (row.defaultTaxCodeId as string) ?? null,
    defaultTaxRateId: (row.defaultTaxRateId as string) ?? null,
    cashFlowCode: (row.cashFlowCode as string) ?? null,
    financialStatementCode: (row.financialStatementCode as string) ?? null,
    financialStatementNote: (row.financialStatementNote as string) ?? null,
    createdById: (row.createdById as string) ?? null,
    updatedById: (row.updatedById as string) ?? null,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
  });
}

// ─── AccountClass Repository ─────────────────────────────────────────────

@Injectable()
export class PrismaAccountClassRepository implements AccountClassRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(entity: AccountClass): Promise<void> {
    const s = entity.toState();
    await (this.prisma as any).accountClass.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: AccountClassId): Promise<AccountClass | null> {
    const row = await (this.prisma as any).accountClass.findUnique({ where: { id: id.value } });
    return row ? fromPrismaClass(row) : null;
  }

  async findByCode(code: string): Promise<AccountClass | null> {
    const row = await (this.prisma as any).accountClass.findUnique({ where: { code } });
    return row ? fromPrismaClass(row) : null;
  }

  async findAll(): Promise<AccountClass[]> {
    const rows = await (this.prisma as any).accountClass.findMany({ orderBy: { displayOrder: "asc" } });
    return rows.map((r: any) => fromPrismaClass(r));
  }

  async findActive(): Promise<AccountClass[]> {
    const rows = await (this.prisma as any).accountClass.findMany({
      where: { isActive: true },
      orderBy: { displayOrder: "asc" },
    });
    return rows.map((r: any) => fromPrismaClass(r));
  }
}

// ─── AccountType Repository ──────────────────────────────────────────────

@Injectable()
export class PrismaAccountTypeRepository implements AccountTypeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(entity: AccountType): Promise<void> {
    const s = entity.toState();
    await (this.prisma as any).accountType.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: AccountTypeId): Promise<AccountType | null> {
    const row = await (this.prisma as any).accountType.findUnique({ where: { id: id.value } });
    return row ? fromPrismaType(row) : null;
  }

  async findByCode(code: string): Promise<AccountType | null> {
    const row = await (this.prisma as any).accountType.findUnique({ where: { code } });
    return row ? fromPrismaType(row) : null;
  }

  async findByClass(classId: string): Promise<AccountType[]> {
    const rows = await (this.prisma as any).accountType.findMany({
      where: { classId },
      orderBy: { displayOrder: "asc" },
    });
    return rows.map((r: any) => fromPrismaType(r));
  }

  async findAll(): Promise<AccountType[]> {
    const rows = await (this.prisma as any).accountType.findMany({ orderBy: { displayOrder: "asc" } });
    return rows.map((r: any) => fromPrismaType(r));
  }

  async findActive(): Promise<AccountType[]> {
    const rows = await (this.prisma as any).accountType.findMany({
      where: { isActive: true },
      orderBy: { displayOrder: "asc" },
    });
    return rows.map((r: any) => fromPrismaType(r));
  }

  async findByCategory(category: string): Promise<AccountType[]> {
    const rows = await (this.prisma as any).accountType.findMany({
      where: { category },
      orderBy: { displayOrder: "asc" },
    });
    return rows.map((r: any) => fromPrismaType(r));
  }
}

// ─── AccountMapping Repository ───────────────────────────────────────────

@Injectable()
export class PrismaAccountMappingRepository implements AccountMappingRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(entity: AccountMapping): Promise<void> {
    const s = entity.toState();
    await (this.prisma as any).accountMapping.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findById(id: AccountMappingId): Promise<AccountMapping | null> {
    const row = await (this.prisma as any).accountMapping.findUnique({ where: { id: id.value } });
    return row ? fromPrismaMapping(row) : null;
  }

  async findByAccount(accountId: string): Promise<AccountMapping[]> {
    const rows = await (this.prisma as any).accountMapping.findMany({
      where: { accountId },
      orderBy: { createdAt: "desc" },
    });
    return rows.map((r: any) => fromPrismaMapping(r));
  }

  async findByStandard(standard: AccountMappingStandard): Promise<AccountMapping[]> {
    const rows = await (this.prisma as any).accountMapping.findMany({
      where: { mappingStandard: standard, isActive: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map((r: any) => fromPrismaMapping(r));
  }

  async findByAccountAndStandard(accountId: string, standard: AccountMappingStandard): Promise<AccountMapping | null> {
    const row = await (this.prisma as any).accountMapping.findFirst({
      where: { accountId, mappingStandard: standard, isActive: true },
    });
    return row ? fromPrismaMapping(row) : null;
  }

  async findActiveByAccount(accountId: string): Promise<AccountMapping[]> {
    const rows = await (this.prisma as any).accountMapping.findMany({
      where: { accountId, isActive: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map((r: any) => fromPrismaMapping(r));
  }

  async findAll(): Promise<AccountMapping[]> {
    const rows = await (this.prisma as any).accountMapping.findMany({ orderBy: { createdAt: "desc" } });
    return rows.map((r: any) => fromPrismaMapping(r));
  }

  async delete(id: AccountMappingId): Promise<void> {
    await (this.prisma as any).accountMapping.delete({ where: { id: id.value } });
  }
}

// ─── AccountExtension Repository ─────────────────────────────────────────

@Injectable()
export class PrismaAccountExtensionRepository implements AccountExtensionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(entity: AccountExtension): Promise<void> {
    const s = entity.toState();
    await (this.prisma as any).accountExtension.upsert({
      where: { id: s.id },
      create: s,
      update: s,
    });
  }

  async findByAccountId(accountId: string): Promise<AccountExtension | null> {
    const row = await (this.prisma as any).accountExtension.findUnique({ where: { accountId } });
    return row ? fromPrismaExtension(row) : null;
  }

  async findById(id: AccountExtensionId): Promise<AccountExtension | null> {
    const row = await (this.prisma as any).accountExtension.findUnique({ where: { id: id.value } });
    return row ? fromPrismaExtension(row) : null;
  }

  async findByType(typeId: string): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { typeId },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }

  async findByStatus(status: AccountEffectiveStatus): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { effectiveStatus: status },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }

  async findCashAccounts(): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { isCashAccount: true },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }

  async findBankAccounts(): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { isBankAccount: true },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }

  async findTaxAccounts(): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { isTaxAccount: true },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }

  async findInventoryAccounts(): Promise<AccountExtension[]> {
    const rows = await (this.prisma as any).accountExtension.findMany({
      where: { isInventoryAccount: true },
    });
    return rows.map((r: any) => fromPrismaExtension(r));
  }
}
