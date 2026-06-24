import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { FaAsset } from "../../domain/fa/fa-asset.js";
import { FaCipProject } from "../../domain/fa/fa-cip.js";
import { FaRevaluation } from "../../domain/fa/fa-revaluation.js";
import { FaImpairment } from "../../domain/fa/fa-impairment.js";
import { FaDisposal } from "../../domain/fa/fa-disposal.js";
import { FaTransfer } from "../../domain/fa/fa-transfer.js";
import { FaDepreciationRun } from "../../domain/fa/fa-depreciation-run.js";
import { FaLease } from "../../domain/fa/fa-lease.js";
import { FaMaintenanceRecord } from "../../domain/fa/fa-maintenance.js";
import { FaPhysicalVerification } from "../../domain/fa/fa-physical.js";
import {
  FaAssetId, FaCipProjectId, FaRevaluationId, FaImpairmentId,
  FaDisposalId, FaTransferId, FaDepreciationRunId, FaLeaseId,
  FaMaintenanceRecordId, FaPhysicalVerificationId,
  FaAssetGroupId, FaAssetClassId, FaAssetCategoryId,
} from "../../domain/fa/fa-ids.js";
import {
  FaAssetType, FaAssetStatus, FaDepreciationMethod, FaDepreciationArea,
  FaDepreciationRunStatus, FaDisposalType, FaRevaluationType,
  FaImpairmentType, FaAcquisitionType, FaLeaseType,
  FaLeasePaymentFrequency, FaMaintenanceType,
  FaVerificationMethod, FaVerificationStatus,
} from "../../domain/fa/fa-enums.js";
import type {
  FaAssetGroupRepository, FaAssetClassRepository, FaAssetCategoryRepository,
  FaAssetRepository, FaCipProjectRepository, FaRevaluationRepository,
  FaImpairmentRepository, FaDisposalRepository, FaTransferRepository,
  FaDepreciationRunRepository, FaLeaseRepository,
  FaMaintenanceRecordRepository, FaPhysicalVerificationRepository,
} from "../../domain/fa/fa-repositories.js";
import { FaGlService } from "./fa-gl-service.js";

@Injectable()
export class FaService {
  constructor(
    private readonly groupRepo: FaAssetGroupRepository,
    private readonly classRepo: FaAssetClassRepository,
    private readonly categoryRepo: FaAssetCategoryRepository,
    private readonly assetRepo: FaAssetRepository,
    private readonly cipRepo: FaCipProjectRepository,
    private readonly revaluationRepo: FaRevaluationRepository,
    private readonly impairmentRepo: FaImpairmentRepository,
    private readonly disposalRepo: FaDisposalRepository,
    private readonly transferRepo: FaTransferRepository,
    private readonly depRunRepo: FaDepreciationRunRepository,
    private readonly leaseRepo: FaLeaseRepository,
    private readonly maintenanceRepo: FaMaintenanceRecordRepository,
    private readonly verificationRepo: FaPhysicalVerificationRepository,
    private readonly glService: FaGlService,
  ) {}

  // ─── Asset Group ────────────────────────────────────────────────────────────────

  async createGroup(p: {
    code: string; name: string; assetType: FaAssetType;
    parentId?: string; description?: string; category?: string;
    usefulLifeMin?: number; usefulLifeMax?: number;
    depreciationMethod?: FaDepreciationMethod;
  }): Promise<any> {
    const existing = await this.groupRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Group code ${p.code} exists`);
    const group = {
      id: FaAssetGroupId.new().value, code: p.code, name: p.name,
      assetType: p.assetType, description: p.description ?? null,
      parentId: p.parentId ?? null, usefulLifeMin: p.usefulLifeMin ?? null,
      usefulLifeMax: p.usefulLifeMax ?? null,
      depreciationMethod: p.depreciationMethod ?? null,
      isActive: true, version: 1, createdAt: new Date(), updatedAt: new Date(),
    };
    await this.groupRepo.save(group as any);
    return group;
  }

  async getGroup(id: string): Promise<any> {
    return this.groupRepo.findById(FaAssetGroupId.from(id));
  }

  async listGroups(): Promise<any[]> {
    return this.groupRepo.findActive();
  }

  async updateGroup(id: string, p: Record<string, unknown>): Promise<any> {
    const group = await this.groupRepo.findById(FaAssetGroupId.from(id));
    if (!group) throw new DomainError("NotFound", "Group not found");
    const updated = { ...group, ...p, updatedAt: new Date() };
    await this.groupRepo.save(updated as any);
    return updated;
  }

  // ─── Asset Class ────────────────────────────────────────────────────────────────

  async createClass(p: {
    code: string; name: string; assetType: FaAssetType;
    groupId?: string; description?: string;
    usefulLifeYears?: number; depreciationMethod?: FaDepreciationMethod;
    glAssetAccountId?: string; glDepreciationAccountId?: string;
    glAccumulatedDepreciationId?: string; glExpenseAccountId?: string;
  }): Promise<any> {
    const existing = await this.classRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Class code ${p.code} exists`);
    const cls = {
      id: FaAssetClassId.new().value, code: p.code, name: p.name,
      assetType: p.assetType, groupId: p.groupId ?? null,
      description: p.description ?? null,
      usefulLifeYears: p.usefulLifeYears ?? null,
      depreciationMethod: p.depreciationMethod ?? null,
      glAssetAccountId: p.glAssetAccountId ?? null,
      glDepreciationAccountId: p.glDepreciationAccountId ?? null,
      glAccumulatedDepreciationId: p.glAccumulatedDepreciationId ?? null,
      glExpenseAccountId: p.glExpenseAccountId ?? null,
      isActive: true, version: 1, createdAt: new Date(), updatedAt: new Date(),
    };
    await this.classRepo.save(cls as any);
    return cls;
  }

  async getClass(id: string): Promise<any> {
    return this.classRepo.findById(FaAssetClassId.from(id));
  }

  async listClasses(groupId?: string): Promise<any[]> {
    if (groupId) return this.classRepo.findByGroupId(groupId);
    return this.classRepo.findAll();
  }

  // ─── Asset Category ─────────────────────────────────────────────────────────────

  async createCategory(p: {
    code: string; name: string; classId?: string; description?: string;
  }): Promise<any> {
    const existing = await this.categoryRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Category code ${p.code} exists`);
    const cat = {
      id: FaAssetCategoryId.new().value, code: p.code, name: p.name,
      classId: p.classId ?? null, description: p.description ?? null,
      isActive: true, version: 1, createdAt: new Date(), updatedAt: new Date(),
    };
    await this.categoryRepo.save(cat as any);
    return cat;
  }

  async getCategory(id: string): Promise<any> {
    return this.categoryRepo.findById(FaAssetCategoryId.from(id));
  }

  async listCategories(classId?: string): Promise<any[]> {
    if (classId) return this.categoryRepo.findByClassId(classId);
    return this.categoryRepo.findAll();
  }

  // ─── Asset Master ───────────────────────────────────────────────────────────────

  async createAsset(p: {
    companyId: string; assetCode: string; assetName: string;
    assetType: FaAssetType; depreciationMethod: FaDepreciationMethod;
    usefulLifeYears: number; usefulLifeMonths?: number;
    branchId?: string; groupId?: string; classId?: string; categoryId?: string;
    description?: string; serialNumber?: string; modelNumber?: string;
    manufacturer?: string; costCenterId?: string; profitCenterId?: string;
    departmentId?: string; projectId?: string; custodianId?: string;
    custodianName?: string; locationId?: string;
  }): Promise<FaAsset> {
    const existing = await this.assetRepo.findByCode(p.assetCode);
    if (existing) throw new DomainError("Conflict", `Asset code ${p.assetCode} exists`);
    const asset = FaAsset.create({ ...p, usefulLifeMonths: p.usefulLifeMonths ?? 0 });
    await this.assetRepo.save(asset);
    return asset;
  }

  async getAsset(id: string): Promise<FaAsset | null> {
    return this.assetRepo.findById(FaAssetId.from(id));
  }

  async getAssetByCode(code: string): Promise<FaAsset | null> {
    return this.assetRepo.findByCode(code);
  }

  async listAssets(status?: FaAssetStatus, type?: FaAssetType): Promise<FaAsset[]> {
    if (status) return this.assetRepo.findByStatus(status);
    if (type) return this.assetRepo.findByType(type);
    return this.assetRepo.findActive();
  }

  async updateAsset(id: string, p: Record<string, unknown>): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.update(p as any);
    await this.assetRepo.save(asset);
    return asset;
  }

  // ─── Asset Lifecycle ────────────────────────────────────────────────────────────

  async acquireAsset(id: string, p: {
    acquisitionType: FaAcquisitionType; acquisitionDate: Date;
    originalCost: number; residualValue?: number;
    supplierId?: string; supplierName?: string; poNumber?: string;
    invoiceNumber?: string; contractNumber?: string; serialNumber?: string;
  }): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.acquire(p);
    await this.assetRepo.save(asset);
    return asset;
  }

  async capitalizeAsset(id: string, capitalizationDate: Date): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.capitalize(capitalizationDate);
    await this.assetRepo.save(asset);
    return asset;
  }

  async putAssetInUse(id: string, inUseDate: Date): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.putInUse(inUseDate);
    await this.assetRepo.save(asset);
    return asset;
  }

  async suspendAsset(id: string, from: Date, to?: Date): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.suspend(from, to);
    await this.assetRepo.save(asset);
    return asset;
  }

  async resumeAsset(id: string): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.resume();
    await this.assetRepo.save(asset);
    return asset;
  }

  async transferAsset(id: string, p: {
    toBranchId?: string; toCostCenterId?: string;
    toDepartmentId?: string; toLocationId?: string;
    toCustodianId?: string; toCustodianName?: string;
    transferDate: Date; transferNumber: string;
  }): Promise<FaTransfer> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.transfer(p);
    const transfer = FaTransfer.create({
      assetId: id, transferNumber: p.transferNumber, transferDate: p.transferDate,
      fromBranchId: asset.branchId ?? undefined, toBranchId: p.toBranchId,
      fromCostCenterId: asset.costCenterId ?? undefined, toCostCenterId: p.toCostCenterId,
      fromDepartmentId: asset.departmentId ?? undefined, toDepartmentId: p.toDepartmentId,
      fromLocationId: asset.locationId ?? undefined, toLocationId: p.toLocationId,
    });
    await this.assetRepo.save(asset);
    await this.transferRepo.save(transfer);
    return transfer;
  }

  // ─── Disposal ───────────────────────────────────────────────────────────────────

  async disposeAsset(id: string, p: {
    disposalType: FaDisposalType; disposalDate: Date;
    proceeds: number; costs?: number; reason?: string;
    customerId?: string; customerName?: string; invoiceNumber?: string;
    disposalNumber: string;
  }): Promise<FaDisposal> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");

    const disposal = FaDisposal.create({
      assetId: id, disposalNumber: p.disposalNumber,
      disposalType: p.disposalType, disposalDate: p.disposalDate,
      originalCost: asset.originalCost,
      accumulatedDepreciation: asset.accumulatedDepreciation,
      netBookValue: asset.netBookValue,
      disposalProceeds: p.proceeds, disposalCosts: p.costs ?? 0,
      customerId: p.customerId, customerName: p.customerName,
      invoiceNumber: p.invoiceNumber, reason: p.reason,
    });
    asset.dispose({ ...p, costs: p.costs ?? 0 });
    await this.assetRepo.save(asset);
    await this.disposalRepo.save(disposal);
    return disposal;
  }

  async writeOffAsset(id: string, reason: string): Promise<FaAsset> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");
    asset.writeOff(reason);
    await this.assetRepo.save(asset);
    return asset;
  }

  // ─── Revaluation ────────────────────────────────────────────────────────────────

  async revalueAsset(id: string, p: {
    revaluationType: FaRevaluationType; revaluationDate: Date;
    newValue: number; revaluationNumber: string;
    reserveAccountId?: string; documentNumber?: string; notes?: string;
  }): Promise<FaRevaluation> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");

    const reval = FaRevaluation.create({
      assetId: id, revaluationNumber: p.revaluationNumber,
      revaluationType: p.revaluationType, revaluationDate: p.revaluationDate,
      previousValue: asset.netBookValue, revaluedAmount: p.newValue - asset.netBookValue,
      newValue: p.newValue,
      accumulatedDepreciationBefore: asset.accumulatedDepreciation,
      accumulatedDepreciationAfter: asset.accumulatedDepreciation,
      revaluationReserve: Math.max(0, p.newValue - asset.netBookValue),
      reserveAccountId: p.reserveAccountId, documentNumber: p.documentNumber, notes: p.notes,
    });
    asset.revalue(p.revaluationType, p.newValue, p.revaluationDate);
    await this.assetRepo.save(asset);
    await this.revaluationRepo.save(reval);
    return reval;
  }

  // ─── Impairment ─────────────────────────────────────────────────────────────────

  async impairAsset(id: string, p: {
    impairmentType: FaImpairmentType; impairmentDate: Date;
    carryingAmount: number; recoverableAmount: number;
    impairmentNumber: string; fairValueLessCost?: number;
    valueInUse?: number; documentNumber?: string; notes?: string;
  }): Promise<FaImpairment> {
    const asset = await this.assetRepo.findById(FaAssetId.from(id));
    if (!asset) throw new DomainError("NotFound", "Asset not found");

    const loss = p.carryingAmount - p.recoverableAmount;
    const impairment = FaImpairment.create({
      assetId: id, ...p, impairmentLoss: Math.max(0, loss),
    });
    if (loss > 0) {
      asset.impair(p.impairmentType, loss, p.impairmentDate);
      await this.assetRepo.save(asset);
    }
    await this.impairmentRepo.save(impairment);
    return impairment;
  }

  // ─── Depreciation Engine ───────────────────────────────────────────────────────

  async runDepreciation(p: {
    runNumber: string; depreciationArea: FaDepreciationArea;
    periodId: string; fiscalYearId: string;
    isSimulation?: boolean; createdById?: string;
  }): Promise<{ run: FaDepreciationRun; totalDepreciation: number; entries: number }> {
    const run = FaDepreciationRun.create(p);
    await this.depRunRepo.save(run);
    run.start();

    const assets = await this.assetRepo.findForDepreciation(p.depreciationArea);
    run.setTotalAssets(assets.length);
    let totalDepr = 0;
    let entryCount = 0;

    for (const asset of assets) {
      try {
        const amount = asset.calculateMonthlyDepreciation();
        if (amount > 0) {
          asset.applyDepreciation(amount, new Date());
          await this.assetRepo.save(asset);
          totalDepr += amount;
          entryCount++;
        }
        run.incrementProcessed();
      } catch {
        run.incrementFailed();
      }
    }

    run.complete(totalDepr);
    await this.depRunRepo.save(run);
    return { run, totalDepreciation: totalDepr, entries: entryCount };
  }

  async getDepreciationRun(id: string): Promise<FaDepreciationRun | null> {
    return this.depRunRepo.findById(FaDepreciationRunId.from(id));
  }

  async listDepreciationRuns(periodId?: string): Promise<FaDepreciationRun[]> {
    if (periodId) return this.depRunRepo.findByPeriod(periodId);
    return this.depRunRepo.findAll();
  }

  // ─── CIP ────────────────────────────────────────────────────────────────────────

  async createCipProject(p: {
    projectCode: string; projectName: string; companyId: string;
    startDate: Date; totalBudget?: number; description?: string;
    projectType?: string; branchId?: string; departmentId?: string;
    projectManagerId?: string; expectedEndDate?: Date;
    contractNumber?: string; contractorId?: string; contractorName?: string;
  }): Promise<FaCipProject> {
    const existing = await this.cipRepo.findByCode(p.projectCode);
    if (existing) throw new DomainError("Conflict", `CIP project ${p.projectCode} exists`);
    const project = FaCipProject.create(p);
    await this.cipRepo.save(project);
    return project;
  }

  async getCipProject(id: string): Promise<FaCipProject | null> {
    return this.cipRepo.findById(FaCipProjectId.from(id));
  }

  async listCipProjects(status?: string): Promise<FaCipProject[]> {
    if (status === "active") return this.cipRepo.findActive();
    if (status === "completed") return this.cipRepo.findCompleted();
    return this.cipRepo.findAll();
  }

  async addCipCost(projectId: string, p: {
    costDate: Date; amount: number; description?: string;
    costType?: string; poNumber?: string; invoiceNumber?: string;
  }): Promise<void> {
    const project = await this.cipRepo.findById(FaCipProjectId.from(projectId));
    if (!project) throw new DomainError("NotFound", "CIP project not found");
    project.addCost(p.amount);
    await this.cipRepo.save(project);
  }

  async capitalizeCipProject(projectId: string, assetId: string, amount: number): Promise<void> {
    const project = await this.cipRepo.findById(FaCipProjectId.from(projectId));
    if (!project) throw new DomainError("NotFound", "CIP project not found");
    project.capitalize(amount, assetId);
    await this.cipRepo.save(project);
  }

  async completeCipProject(projectId: string, endDate: Date): Promise<void> {
    const project = await this.cipRepo.findById(FaCipProjectId.from(projectId));
    if (!project) throw new DomainError("NotFound", "CIP project not found");
    project.complete(endDate);
    await this.cipRepo.save(project);
  }

  // ─── Lease ──────────────────────────────────────────────────────────────────────

  async createLease(p: {
    leaseNumber: string; leaseType: FaLeaseType;
    startDate: Date; endDate: Date;
    paymentAmount: number; totalLeaseLiability: number;
    assetId?: string; lessorId?: string; lessorName?: string;
    leaseTermMonths?: number; paymentFrequency?: FaLeasePaymentFrequency;
    interestRate?: number; rightOfUseAsset?: number;
    reference?: string; notes?: string;
  }): Promise<FaLease> {
    const existing = await this.leaseRepo.findByNumber(p.leaseNumber);
    if (existing) throw new DomainError("Conflict", `Lease ${p.leaseNumber} exists`);
    const lease = FaLease.create(p);
    await this.leaseRepo.save(lease);
    return lease;
  }

  async getLease(id: string): Promise<FaLease | null> {
    return this.leaseRepo.findById(FaLeaseId.from(id));
  }

  async listLeases(): Promise<FaLease[]> {
    return this.leaseRepo.findActive();
  }

  // ─── Maintenance ────────────────────────────────────────────────────────────────

  async createMaintenanceRecord(p: {
    assetId: string; recordNumber: string;
    maintenanceType: FaMaintenanceType; maintenanceDate: Date;
    cost: number; description?: string; vendorId?: string;
    vendorName?: string; technicianId?: string; technicianName?: string;
  }): Promise<FaMaintenanceRecord> {
    const existing = await this.maintenanceRepo.findByRecordNumber(p.recordNumber);
    if (existing) throw new DomainError("Conflict", `Record ${p.recordNumber} exists`);
    const record = FaMaintenanceRecord.create(p);
    await this.maintenanceRepo.save(record);
    return record;
  }

  async getMaintenanceRecord(id: string): Promise<FaMaintenanceRecord | null> {
    return this.maintenanceRepo.findById(FaMaintenanceRecordId.from(id));
  }

  async listMaintenanceRecords(assetId?: string): Promise<FaMaintenanceRecord[]> {
    if (assetId) return this.maintenanceRepo.findByAssetId(assetId);
    return this.maintenanceRepo.findAll();
  }

  // ─── Physical Verification ──────────────────────────────────────────────────────

  async createVerification(p: {
    verificationNumber: string; companyId: string;
    verificationDate: Date; verificationMethod?: FaVerificationMethod;
    branchId?: string; verifiedById?: string; verifiedByName?: string;
  }): Promise<FaPhysicalVerification> {
    const existing = await this.verificationRepo.findByNumber(p.verificationNumber);
    if (existing) throw new DomainError("Conflict", `Verification ${p.verificationNumber} exists`);
    const verification = FaPhysicalVerification.create(p);
    await this.verificationRepo.save(verification);
    return verification;
  }

  async getVerification(id: string): Promise<FaPhysicalVerification | null> {
    return this.verificationRepo.findById(FaPhysicalVerificationId.from(id));
  }

  async listVerifications(status?: string): Promise<FaPhysicalVerification[]> {
    if (status) return this.verificationRepo.findByStatus(status);
    return this.verificationRepo.findAll();
  }

  async completeVerification(id: string): Promise<FaPhysicalVerification> {
    const verification = await this.verificationRepo.findById(FaPhysicalVerificationId.from(id));
    if (!verification) throw new DomainError("NotFound", "Verification not found");
    verification.complete();
    await this.verificationRepo.save(verification);
    return verification;
  }

  async approveVerification(id: string, userId: string): Promise<FaPhysicalVerification> {
    const verification = await this.verificationRepo.findById(FaPhysicalVerificationId.from(id));
    if (!verification) throw new DomainError("NotFound", "Verification not found");
    verification.approve(userId);
    await this.verificationRepo.save(verification);
    return verification;
  }
}
