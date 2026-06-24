import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { FaAsset, type FaAssetState } from "../../domain/fa/fa-asset.js";
import { FaCipProject, type FaCipProjectState } from "../../domain/fa/fa-cip.js";
import { FaRevaluation, type FaRevaluationState } from "../../domain/fa/fa-revaluation.js";
import { FaImpairment, type FaImpairmentState } from "../../domain/fa/fa-impairment.js";
import { FaDisposal, type FaDisposalState } from "../../domain/fa/fa-disposal.js";
import { FaTransfer, type FaTransferState } from "../../domain/fa/fa-transfer.js";
import { FaDepreciationRun, type FaDepreciationRunState } from "../../domain/fa/fa-depreciation-run.js";
import { FaLease, type FaLeaseState } from "../../domain/fa/fa-lease.js";
import { FaMaintenanceRecord, type FaMaintenanceRecordState } from "../../domain/fa/fa-maintenance.js";
import { FaPhysicalVerification, type FaPhysicalVerificationState } from "../../domain/fa/fa-physical.js";
import {
  FaAssetId, FaAssetGroupId, FaAssetClassId, FaAssetCategoryId,
  FaCipProjectId, FaRevaluationId, FaImpairmentId, FaDisposalId,
  FaTransferId, FaDepreciationRunId, FaLeaseId, FaMaintenanceRecordId,
  FaPhysicalVerificationId,
} from "../../domain/fa/fa-ids.js";
import { FaAssetStatus, FaAssetType, FaDepreciationArea, FaDepreciationRunStatus } from "../../domain/fa/fa-enums.js";
import type {
  FaAssetGroupRepository, FaAssetClassRepository, FaAssetCategoryRepository,
  FaAssetRepository, FaCipProjectRepository, FaRevaluationRepository,
  FaImpairmentRepository, FaDisposalRepository, FaTransferRepository,
  FaDepreciationRunRepository, FaLeaseRepository,
  FaMaintenanceRecordRepository, FaPhysicalVerificationRepository,
} from "../../domain/fa/fa-repositories.js";

function toNumber(v: unknown): number {
  if (v == null) return 0;
  if (typeof v === "number") return v;
  if (typeof v === "bigint") return Number(v);
  if (typeof v === "string") return Number(v);
  return Number(v as any);
}

// ─── Helpers ─────────────────────────────────────────────────────────────────────

function fromPrismaAsset(row: Record<string, unknown>): FaAsset {
  return FaAsset.load({
    id: row.id as string,
    companyId: row.companyId as string,
    branchId: (row.branchId as string) ?? null,
    assetCode: row.assetCode as string,
    assetName: row.assetName as string,
    assetNameEn: (row.assetNameEn as string) ?? null,
    description: (row.description as string) ?? null,
    assetType: row.assetType as FaAssetType,
    assetStatus: row.assetStatus as FaAssetStatus,
    groupId: (row.groupId as string) ?? null,
    classId: (row.classId as string) ?? null,
    categoryId: (row.categoryId as string) ?? null,
    parentId: (row.parentId as string) ?? null,
    rootAssetId: (row.rootAssetId as string) ?? null,
    isComponent: row.isComponent as boolean,
    isLeased: row.isLeased as boolean,
    isCip: row.isCip as boolean,
    isInvestmentProperty: row.isInvestmentProperty as boolean,
    acquisitionType: (row.acquisitionType as any) ?? null,
    acquisitionDate: (row.acquisitionDate as Date) ?? null,
    capitalizationDate: (row.capitalizationDate as Date) ?? null,
    inUseDate: (row.inUseDate as Date) ?? null,
    disposalDate: (row.disposalDate as Date) ?? null,
    retirementDate: (row.retirementDate as Date) ?? null,
    originalCost: toNumber(row.originalCost),
    accumulatedDepreciation: toNumber(row.accumulatedDepreciation),
    netBookValue: toNumber(row.netBookValue),
    residualValue: toNumber(row.residualValue),
    revaluationAmount: toNumber(row.revaluationAmount),
    impairmentAmount: toNumber(row.impairmentAmount),
    revaluationReserve: toNumber(row.revaluationReserve),
    currencyCode: (row.currencyCode as string) ?? "VND",
    exchangeRate: toNumber(row.exchangeRate),
    depreciationMethod: row.depreciationMethod as any,
    usefulLifeYears: row.usefulLifeYears as number,
    usefulLifeMonths: row.usefulLifeMonths as number,
    usefulLifeUnits: row.usefulLifeUnits ? Number(row.usefulLifeUnits) : null,
    unitsProduced: row.unitsProduced ? Number(row.unitsProduced) : null,
    depreciationRate: row.depreciationRate ? Number(row.depreciationRate) : null,
    depreciationStartDate: (row.depreciationStartDate as Date) ?? null,
    depreciationEndDate: (row.depreciationEndDate as Date) ?? null,
    isFullyDepreciated: row.isFullyDepreciated as boolean,
    isSuspended: row.isSuspended as boolean,
    suspensionStartDate: (row.suspensionStartDate as Date) ?? null,
    suspensionEndDate: (row.suspensionEndDate as Date) ?? null,
    costCenterId: (row.costCenterId as string) ?? null,
    profitCenterId: (row.profitCenterId as string) ?? null,
    departmentId: (row.departmentId as string) ?? null,
    projectId: (row.projectId as string) ?? null,
    businessUnitId: (row.businessUnitId as string) ?? null,
    locationId: (row.locationId as string) ?? null,
    custodianId: (row.custodianId as string) ?? null,
    custodianName: (row.custodianName as string) ?? null,
    ownerId: (row.ownerId as string) ?? null,
    serialNumber: (row.serialNumber as string) ?? null,
    modelNumber: (row.modelNumber as string) ?? null,
    manufacturer: (row.manufacturer as string) ?? null,
    manufacturerYear: (row.manufacturerYear as number) ?? null,
    manufactureCountry: (row.manufactureCountry as string) ?? null,
    supplierId: (row.supplierId as string) ?? null,
    supplierName: (row.supplierName as string) ?? null,
    warrantyExpiryDate: (row.warrantyExpiryDate as Date) ?? null,
    insurancePolicyNumber: (row.insurancePolicyNumber as string) ?? null,
    insuranceExpiryDate: (row.insuranceExpiryDate as Date) ?? null,
    insuredValue: row.insuredValue ? toNumber(row.insuredValue) : null,
    address: (row.address as string) ?? null,
    ward: (row.ward as string) ?? null,
    district: (row.district as string) ?? null,
    province: (row.province as string) ?? null,
    country: (row.country as string) ?? "VN",
    gpsCoordinates: (row.gpsCoordinates as string) ?? null,
    building: (row.building as string) ?? null,
    floor: (row.floor as string) ?? null,
    room: (row.room as string) ?? null,
    taxCode: (row.taxCode as string) ?? null,
    taxAuthority: (row.taxAuthority as string) ?? null,
    vatRate: row.vatRate ? Number(row.vatRate) : null,
    importDutyPaid: row.importDutyPaid ? toNumber(row.importDutyPaid) : null,
    nonRefundableTax: row.nonRefundableTax ? toNumber(row.nonRefundableTax) : null,
    cipProjectId: (row.cipProjectId as string) ?? null,
    poNumber: (row.poNumber as string) ?? null,
    invoiceNumber: (row.invoiceNumber as string) ?? null,
    contractNumber: (row.contractNumber as string) ?? null,
    approvalStatus: (row.approvalStatus as string) ?? null,
    approvedById: (row.approvedById as string) ?? null,
    approvedAt: (row.approvedAt as Date) ?? null,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
  });
}

function toPrismaAsset(s: FaAssetState): Record<string, unknown> {
  return {
    id: s.id, companyId: s.companyId, branchId: s.branchId,
    assetCode: s.assetCode, assetName: s.assetName, assetNameEn: s.assetNameEn,
    description: s.description, assetType: s.assetType, assetStatus: s.assetStatus,
    groupId: s.groupId, classId: s.classId, categoryId: s.categoryId,
    parentId: s.parentId, rootAssetId: s.rootAssetId,
    isComponent: s.isComponent, isLeased: s.isLeased, isCip: s.isCip,
    isInvestmentProperty: s.isInvestmentProperty,
    acquisitionType: s.acquisitionType, acquisitionDate: s.acquisitionDate,
    capitalizationDate: s.capitalizationDate, inUseDate: s.inUseDate,
    disposalDate: s.disposalDate, retirementDate: s.retirementDate,
    originalCost: BigInt(Math.round(s.originalCost)),
    accumulatedDepreciation: BigInt(Math.round(s.accumulatedDepreciation)),
    netBookValue: BigInt(Math.round(s.netBookValue)),
    residualValue: BigInt(Math.round(s.residualValue)),
    revaluationAmount: BigInt(Math.round(s.revaluationAmount)),
    impairmentAmount: BigInt(Math.round(s.impairmentAmount)),
    revaluationReserve: BigInt(Math.round(s.revaluationReserve)),
    currencyCode: s.currencyCode, exchangeRate: s.exchangeRate,
    depreciationMethod: s.depreciationMethod,
    usefulLifeYears: s.usefulLifeYears, usefulLifeMonths: s.usefulLifeMonths,
    usefulLifeUnits: s.usefulLifeUnits, unitsProduced: s.unitsProduced,
    depreciationRate: s.depreciationRate,
    depreciationStartDate: s.depreciationStartDate,
    depreciationEndDate: s.depreciationEndDate,
    isFullyDepreciated: s.isFullyDepreciated, isSuspended: s.isSuspended,
    suspensionStartDate: s.suspensionStartDate,
    suspensionEndDate: s.suspensionEndDate,
    costCenterId: s.costCenterId, profitCenterId: s.profitCenterId,
    departmentId: s.departmentId, projectId: s.projectId,
    businessUnitId: s.businessUnitId, locationId: s.locationId,
    custodianId: s.custodianId, custodianName: s.custodianName,
    ownerId: s.ownerId,
    serialNumber: s.serialNumber, modelNumber: s.modelNumber,
    manufacturer: s.manufacturer, manufacturerYear: s.manufacturerYear,
    manufactureCountry: s.manufactureCountry,
    supplierId: s.supplierId, supplierName: s.supplierName,
    warrantyExpiryDate: s.warrantyExpiryDate,
    insurancePolicyNumber: s.insurancePolicyNumber,
    insuranceExpiryDate: s.insuranceExpiryDate,
    insuredValue: s.insuredValue ? BigInt(Math.round(s.insuredValue)) : null,
    address: s.address, ward: s.ward, district: s.district,
    province: s.province, country: s.country,
    gpsCoordinates: s.gpsCoordinates, building: s.building,
    floor: s.floor, room: s.room,
    taxCode: s.taxCode, taxAuthority: s.taxAuthority, vatRate: s.vatRate,
    importDutyPaid: s.importDutyPaid ? BigInt(Math.round(s.importDutyPaid)) : null,
    nonRefundableTax: s.nonRefundableTax ? BigInt(Math.round(s.nonRefundableTax)) : null,
    cipProjectId: s.cipProjectId, poNumber: s.poNumber,
    invoiceNumber: s.invoiceNumber, contractNumber: s.contractNumber,
    approvalStatus: s.approvalStatus, approvedById: s.approvedById,
    approvedAt: s.approvedAt,
    version: s.version, createdAt: s.createdAt, updatedAt: s.updatedAt,
  };
}

// ─── Group ────────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaAssetGroupRepository implements FaAssetGroupRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(group: any): Promise<void> {
    await (this.prisma as any).faAssetGroup.upsert({
      where: { id: group.id }, create: group, update: group,
    });
  }

  async findById(id: FaAssetGroupId): Promise<any | null> {
    return (this.prisma as any).faAssetGroup.findUnique({ where: { id: id.value } });
  }

  async findByCode(code: string): Promise<any | null> {
    return (this.prisma as any).faAssetGroup.findUnique({ where: { code } });
  }

  async findAll(): Promise<any[]> {
    return (this.prisma as any).faAssetGroup.findMany({ where: { deletedAt: null } });
  }

  async findActive(): Promise<any[]> {
    return (this.prisma as any).faAssetGroup.findMany({ where: { isActive: true, deletedAt: null } });
  }
}

// ─── Class ────────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaAssetClassRepository implements FaAssetClassRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(cls: any): Promise<void> {
    await (this.prisma as any).faAssetClass.upsert({
      where: { id: cls.id }, create: cls, update: cls,
    });
  }

  async findById(id: FaAssetClassId): Promise<any | null> {
    return (this.prisma as any).faAssetClass.findUnique({ where: { id: id.value } });
  }

  async findByCode(code: string): Promise<any | null> {
    return (this.prisma as any).faAssetClass.findUnique({ where: { code } });
  }

  async findAll(): Promise<any[]> {
    return (this.prisma as any).faAssetClass.findMany({ where: { deletedAt: null } });
  }

  async findByGroupId(groupId: string): Promise<any[]> {
    return (this.prisma as any).faAssetClass.findMany({ where: { groupId, deletedAt: null } });
  }
}

// ─── Category ─────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaAssetCategoryRepository implements FaAssetCategoryRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(cat: any): Promise<void> {
    await (this.prisma as any).faAssetCategory.upsert({
      where: { id: cat.id }, create: cat, update: cat,
    });
  }

  async findById(id: FaAssetCategoryId): Promise<any | null> {
    return (this.prisma as any).faAssetCategory.findUnique({ where: { id: id.value } });
  }

  async findByCode(code: string): Promise<any | null> {
    return (this.prisma as any).faAssetCategory.findUnique({ where: { code } });
  }

  async findAll(): Promise<any[]> {
    return (this.prisma as any).faAssetCategory.findMany({ where: { deletedAt: null } });
  }

  async findByClassId(classId: string): Promise<any[]> {
    return (this.prisma as any).faAssetCategory.findMany({ where: { classId, deletedAt: null } });
  }
}

// ─── Asset ────────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaAssetRepository implements FaAssetRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(asset: FaAsset): Promise<void> {
    const s = asset.toState();
    const data = toPrismaAsset(s);
    await (this.prisma as any).faAsset.upsert({
      where: { id: data.id as string },
      create: data,
      update: data,
    });
  }

  async findById(id: FaAssetId): Promise<FaAsset | null> {
    const row = await (this.prisma as any).faAsset.findUnique({ where: { id: id.value } });
    return row ? fromPrismaAsset(row) : null;
  }

  async findByCode(code: string): Promise<FaAsset | null> {
    const row = await (this.prisma as any).faAsset.findUnique({ where: { assetCode: code } });
    return row ? fromPrismaAsset(row) : null;
  }

  async findBySerialNumber(serial: string): Promise<FaAsset | null> {
    const row = await (this.prisma as any).faAsset.findUnique({ where: { serialNumber: serial } });
    return row ? fromPrismaAsset(row) : null;
  }

  async findAll(): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({ where: { deletedAt: null } });
    return rows.map(fromPrismaAsset);
  }

  async findActive(): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { deletedAt: null, assetStatus: { in: [FaAssetStatus.Capitalized, FaAssetStatus.InUse] } },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByStatus(status: FaAssetStatus): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { assetStatus: status, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByType(assetType: FaAssetType): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { assetType, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByGroupId(groupId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { groupId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByClassId(classId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { classId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByCategoryId(categoryId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { categoryId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByCostCenterId(costCenterId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { costCenterId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByCustodianId(custodianId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { custodianId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findByCipProjectId(projectId: string): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { cipProjectId: projectId, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findFullyDepreciated(): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { isFullyDepreciated: true, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }

  async findForDepreciation(area: FaDepreciationArea): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: {
        assetStatus: FaAssetStatus.InUse,
        isFullyDepreciated: false,
        isSuspended: false,
        deletedAt: null,
        depreciationStartDate: { not: null },
      },
    });
    return rows.map(fromPrismaAsset);
  }

  async findSuspended(): Promise<FaAsset[]> {
    const rows = await (this.prisma as any).faAsset.findMany({
      where: { isSuspended: true, deletedAt: null },
    });
    return rows.map(fromPrismaAsset);
  }
}

// ─── CIP ──────────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaCipProjectRepository implements FaCipProjectRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(project: FaCipProject): Promise<void> {
    const s = project.toState();
    await (this.prisma as any).faCipProject.upsert({
      where: { id: s.id },
      create: {
        id: s.id, projectCode: s.projectCode, projectName: s.projectName,
        companyId: s.companyId, startDate: s.startDate,
        totalBudget: BigInt(Math.round(s.totalBudget)),
        totalCost: BigInt(Math.round(s.totalCost)),
        capitalizedAmount: BigInt(Math.round(s.capitalizedAmount)),
        remainingBudget: BigInt(Math.round(s.remainingBudget)),
        projectType: s.projectType, status: s.status,
        branchId: s.branchId, departmentId: s.departmentId,
        projectManagerId: s.projectManagerId,
        expectedEndDate: s.expectedEndDate, actualEndDate: s.actualEndDate,
        currencyCode: s.currencyCode, description: s.description,
        contractNumber: s.contractNumber, contractorId: s.contractorId,
        contractorName: s.contractorName, isExternal: s.isExternal,
        approvalStatus: s.approvalStatus, approvedById: s.approvedById,
        approvedAt: s.approvedAt, version: s.version,
        createdAt: s.createdAt, updatedAt: s.updatedAt,
      },
      update: {
        totalCost: BigInt(Math.round(s.totalCost)),
        capitalizedAmount: BigInt(Math.round(s.capitalizedAmount)),
        remainingBudget: BigInt(Math.round(s.remainingBudget)),
        status: s.status, actualEndDate: s.actualEndDate,
        updatedAt: s.updatedAt,
      },
    });
  }

  async findById(id: FaCipProjectId): Promise<FaCipProject | null> {
    const row = await (this.prisma as any).faCipProject.findUnique({ where: { id: id.value } });
    return row ? FaCipProject.load(row as FaCipProjectState) : null;
  }

  async findByCode(code: string): Promise<FaCipProject | null> {
    const row = await (this.prisma as any).faCipProject.findUnique({ where: { projectCode: code } });
    return row ? FaCipProject.load(row as FaCipProjectState) : null;
  }

  async findAll(): Promise<FaCipProject[]> {
    const rows = await (this.prisma as any).faCipProject.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaCipProject.load(r as FaCipProjectState));
  }

  async findActive(): Promise<FaCipProject[]> {
    const rows = await (this.prisma as any).faCipProject.findMany({ where: { status: "active", deletedAt: null } });
    return rows.map((r: any) => FaCipProject.load(r as FaCipProjectState));
  }

  async findCompleted(): Promise<FaCipProject[]> {
    const rows = await (this.prisma as any).faCipProject.findMany({ where: { status: "completed", deletedAt: null } });
    return rows.map((r: any) => FaCipProject.load(r as FaCipProjectState));
  }
}

// ─── Revaluation ──────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaRevaluationRepository implements FaRevaluationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(revaluation: FaRevaluation): Promise<void> {
    const s = revaluation.toState();
    await (this.prisma as any).faRevaluation.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaRevaluationId): Promise<FaRevaluation | null> {
    const row = await (this.prisma as any).faRevaluation.findUnique({ where: { id: id.value } });
    return row ? FaRevaluation.load(row as FaRevaluationState) : null;
  }

  async findByNumber(number: string): Promise<FaRevaluation | null> {
    const row = await (this.prisma as any).faRevaluation.findUnique({ where: { revaluationNumber: number } });
    return row ? FaRevaluation.load(row as FaRevaluationState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaRevaluation[]> {
    const rows = await (this.prisma as any).faRevaluation.findMany({ where: { assetId, deletedAt: null } });
    return rows.map((r: any) => FaRevaluation.load(r as FaRevaluationState));
  }

  async findAll(): Promise<FaRevaluation[]> {
    const rows = await (this.prisma as any).faRevaluation.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaRevaluation.load(r as FaRevaluationState));
  }
}

// ─── Impairment ───────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaImpairmentRepository implements FaImpairmentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(impairment: FaImpairment): Promise<void> {
    const s = impairment.toState();
    await (this.prisma as any).faImpairment.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaImpairmentId): Promise<FaImpairment | null> {
    const row = await (this.prisma as any).faImpairment.findUnique({ where: { id: id.value } });
    return row ? FaImpairment.load(row as FaImpairmentState) : null;
  }

  async findByNumber(number: string): Promise<FaImpairment | null> {
    const row = await (this.prisma as any).faImpairment.findUnique({ where: { impairmentNumber: number } });
    return row ? FaImpairment.load(row as FaImpairmentState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaImpairment[]> {
    const rows = await (this.prisma as any).faImpairment.findMany({ where: { assetId, deletedAt: null } });
    return rows.map((r: any) => FaImpairment.load(r as FaImpairmentState));
  }

  async findAll(): Promise<FaImpairment[]> {
    const rows = await (this.prisma as any).faImpairment.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaImpairment.load(r as FaImpairmentState));
  }
}

// ─── Disposal ─────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaDisposalRepository implements FaDisposalRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(disposal: FaDisposal): Promise<void> {
    const s = disposal.toState();
    await (this.prisma as any).faDisposal.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaDisposalId): Promise<FaDisposal | null> {
    const row = await (this.prisma as any).faDisposal.findUnique({ where: { id: id.value } });
    return row ? FaDisposal.load(row as FaDisposalState) : null;
  }

  async findByNumber(number: string): Promise<FaDisposal | null> {
    const row = await (this.prisma as any).faDisposal.findUnique({ where: { disposalNumber: number } });
    return row ? FaDisposal.load(row as FaDisposalState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaDisposal[]> {
    const rows = await (this.prisma as any).faDisposal.findMany({ where: { assetId, deletedAt: null } });
    return rows.map((r: any) => FaDisposal.load(r as FaDisposalState));
  }

  async findAll(): Promise<FaDisposal[]> {
    const rows = await (this.prisma as any).faDisposal.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaDisposal.load(r as FaDisposalState));
  }
}

// ─── Transfer ─────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaTransferRepository implements FaTransferRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transfer: FaTransfer): Promise<void> {
    const s = transfer.toState();
    await (this.prisma as any).faTransfer.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaTransferId): Promise<FaTransfer | null> {
    const row = await (this.prisma as any).faTransfer.findUnique({ where: { id: id.value } });
    return row ? FaTransfer.load(row as FaTransferState) : null;
  }

  async findByNumber(number: string): Promise<FaTransfer | null> {
    const row = await (this.prisma as any).faTransfer.findUnique({ where: { transferNumber: number } });
    return row ? FaTransfer.load(row as FaTransferState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaTransfer[]> {
    const rows = await (this.prisma as any).faTransfer.findMany({ where: { assetId, deletedAt: null } });
    return rows.map((r: any) => FaTransfer.load(r as FaTransferState));
  }

  async findAll(): Promise<FaTransfer[]> {
    const rows = await (this.prisma as any).faTransfer.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaTransfer.load(r as FaTransferState));
  }
}

// ─── Depreciation Run ─────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaDepreciationRunRepository implements FaDepreciationRunRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(run: FaDepreciationRun): Promise<void> {
    const s = run.toState();
    await (this.prisma as any).faDepreciationRun.upsert({
      where: { id: s.id },
      create: {
        ...s,
        totalDepreciation: BigInt(Math.round(s.totalDepreciation)),
      },
      update: {
        ...s,
        totalDepreciation: BigInt(Math.round(s.totalDepreciation)),
      },
    });
  }

  async findById(id: FaDepreciationRunId): Promise<FaDepreciationRun | null> {
    const row = await (this.prisma as any).faDepreciationRun.findUnique({ where: { id: id.value } });
    return row ? FaDepreciationRun.load(row as FaDepreciationRunState) : null;
  }

  async findByRunNumber(number: string): Promise<FaDepreciationRun | null> {
    const row = await (this.prisma as any).faDepreciationRun.findUnique({ where: { runNumber: number } });
    return row ? FaDepreciationRun.load(row as FaDepreciationRunState) : null;
  }

  async findAll(): Promise<FaDepreciationRun[]> {
    const rows = await (this.prisma as any).faDepreciationRun.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaDepreciationRun.load(r as FaDepreciationRunState));
  }

  async findByPeriod(periodId: string): Promise<FaDepreciationRun[]> {
    const rows = await (this.prisma as any).faDepreciationRun.findMany({
      where: { periodId, deletedAt: null },
    });
    return rows.map((r: any) => FaDepreciationRun.load(r as FaDepreciationRunState));
  }

  async findByStatus(status: string): Promise<FaDepreciationRun[]> {
    const rows = await (this.prisma as any).faDepreciationRun.findMany({
      where: { status, deletedAt: null },
    });
    return rows.map((r: any) => FaDepreciationRun.load(r as FaDepreciationRunState));
  }
}

// ─── Lease ────────────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaLeaseRepository implements FaLeaseRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(lease: FaLease): Promise<void> {
    const s = lease.toState();
    await (this.prisma as any).faLease.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaLeaseId): Promise<FaLease | null> {
    const row = await (this.prisma as any).faLease.findUnique({ where: { id: id.value } });
    return row ? FaLease.load(row as FaLeaseState) : null;
  }

  async findByNumber(number: string): Promise<FaLease | null> {
    const row = await (this.prisma as any).faLease.findUnique({ where: { leaseNumber: number } });
    return row ? FaLease.load(row as FaLeaseState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaLease | null> {
    const row = await (this.prisma as any).faLease.findFirst({
      where: { assetId, deletedAt: null },
    });
    return row ? FaLease.load(row as FaLeaseState) : null;
  }

  async findAll(): Promise<FaLease[]> {
    const rows = await (this.prisma as any).faLease.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaLease.load(r as FaLeaseState));
  }

  async findActive(): Promise<FaLease[]> {
    const rows = await (this.prisma as any).faLease.findMany({
      where: { status: "active", deletedAt: null },
    });
    return rows.map((r: any) => FaLease.load(r as FaLeaseState));
  }
}

// ─── Maintenance ──────────────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaMaintenanceRecordRepository implements FaMaintenanceRecordRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(record: FaMaintenanceRecord): Promise<void> {
    const s = record.toState();
    await (this.prisma as any).faMaintenanceRecord.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaMaintenanceRecordId): Promise<FaMaintenanceRecord | null> {
    const row = await (this.prisma as any).faMaintenanceRecord.findUnique({ where: { id: id.value } });
    return row ? FaMaintenanceRecord.load(row as FaMaintenanceRecordState) : null;
  }

  async findByRecordNumber(number: string): Promise<FaMaintenanceRecord | null> {
    const row = await (this.prisma as any).faMaintenanceRecord.findUnique({ where: { recordNumber: number } });
    return row ? FaMaintenanceRecord.load(row as FaMaintenanceRecordState) : null;
  }

  async findByAssetId(assetId: string): Promise<FaMaintenanceRecord[]> {
    const rows = await (this.prisma as any).faMaintenanceRecord.findMany({ where: { assetId, deletedAt: null } });
    return rows.map((r: any) => FaMaintenanceRecord.load(r as FaMaintenanceRecordState));
  }

  async findAll(): Promise<FaMaintenanceRecord[]> {
    const rows = await (this.prisma as any).faMaintenanceRecord.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaMaintenanceRecord.load(r as FaMaintenanceRecordState));
  }
}

// ─── Physical Verification ────────────────────────────────────────────────────────

@Injectable()
export class PrismaFaPhysicalVerificationRepository implements FaPhysicalVerificationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(verification: FaPhysicalVerification): Promise<void> {
    const s = verification.toState();
    await (this.prisma as any).faPhysicalVerification.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: FaPhysicalVerificationId): Promise<FaPhysicalVerification | null> {
    const row = await (this.prisma as any).faPhysicalVerification.findUnique({ where: { id: id.value } });
    return row ? FaPhysicalVerification.load(row as FaPhysicalVerificationState) : null;
  }

  async findByNumber(number: string): Promise<FaPhysicalVerification | null> {
    const row = await (this.prisma as any).faPhysicalVerification.findUnique({ where: { verificationNumber: number } });
    return row ? FaPhysicalVerification.load(row as FaPhysicalVerificationState) : null;
  }

  async findAll(): Promise<FaPhysicalVerification[]> {
    const rows = await (this.prisma as any).faPhysicalVerification.findMany({ where: { deletedAt: null } });
    return rows.map((r: any) => FaPhysicalVerification.load(r as FaPhysicalVerificationState));
  }

  async findByStatus(status: string): Promise<FaPhysicalVerification[]> {
    const rows = await (this.prisma as any).faPhysicalVerification.findMany({
      where: { status, deletedAt: null },
    });
    return rows.map((r: any) => FaPhysicalVerification.load(r as FaPhysicalVerificationState));
  }
}
