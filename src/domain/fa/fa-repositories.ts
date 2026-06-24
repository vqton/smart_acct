import type { FaAsset } from "./fa-asset.js";
import type { FaCipProject } from "./fa-cip.js";
import type { FaRevaluation } from "./fa-revaluation.js";
import type { FaImpairment } from "./fa-impairment.js";
import type { FaDisposal } from "./fa-disposal.js";
import type { FaTransfer } from "./fa-transfer.js";
import type { FaDepreciationRun } from "./fa-depreciation-run.js";
import type { FaLease } from "./fa-lease.js";
import type { FaMaintenanceRecord } from "./fa-maintenance.js";
import type { FaPhysicalVerification } from "./fa-physical.js";
import {
  FaAssetId, FaCipProjectId, FaRevaluationId, FaImpairmentId,
  FaDisposalId, FaTransferId, FaDepreciationRunId, FaLeaseId,
  FaMaintenanceRecordId, FaPhysicalVerificationId, FaAssetGroupId,
  FaAssetClassId, FaAssetCategoryId,
} from "./fa-ids.js";
import { FaAssetStatus, FaAssetType, FaDepreciationArea } from "./fa-enums.js";

// ─── Group ───────────────────────────────────────────────────────────────────────

export interface FaAssetGroupRepository {
  save(group: any): Promise<void>;
  findById(id: FaAssetGroupId): Promise<any | null>;
  findByCode(code: string): Promise<any | null>;
  findAll(): Promise<any[]>;
  findActive(): Promise<any[]>;
}

// ─── Class ───────────────────────────────────────────────────────────────────────

export interface FaAssetClassRepository {
  save(cls: any): Promise<void>;
  findById(id: FaAssetClassId): Promise<any | null>;
  findByCode(code: string): Promise<any | null>;
  findAll(): Promise<any[]>;
  findByGroupId(groupId: string): Promise<any[]>;
}

// ─── Category ────────────────────────────────────────────────────────────────────

export interface FaAssetCategoryRepository {
  save(cat: any): Promise<void>;
  findById(id: FaAssetCategoryId): Promise<any | null>;
  findByCode(code: string): Promise<any | null>;
  findAll(): Promise<any[]>;
  findByClassId(classId: string): Promise<any[]>;
}

// ─── Asset ────────────────────────────────────────────────────────────────────────

export interface FaAssetRepository {
  save(asset: FaAsset): Promise<void>;
  findById(id: FaAssetId): Promise<FaAsset | null>;
  findByCode(code: string): Promise<FaAsset | null>;
  findBySerialNumber(serial: string): Promise<FaAsset | null>;
  findAll(): Promise<FaAsset[]>;
  findActive(): Promise<FaAsset[]>;
  findByStatus(status: FaAssetStatus): Promise<FaAsset[]>;
  findByType(assetType: FaAssetType): Promise<FaAsset[]>;
  findByGroupId(groupId: string): Promise<FaAsset[]>;
  findByClassId(classId: string): Promise<FaAsset[]>;
  findByCategoryId(categoryId: string): Promise<FaAsset[]>;
  findByCostCenterId(costCenterId: string): Promise<FaAsset[]>;
  findByCustodianId(custodianId: string): Promise<FaAsset[]>;
  findByCipProjectId(projectId: string): Promise<FaAsset[]>;
  findFullyDepreciated(): Promise<FaAsset[]>;
  findForDepreciation(area: FaDepreciationArea): Promise<FaAsset[]>;
  findSuspended(): Promise<FaAsset[]>;
}

// ─── CIP ─────────────────────────────────────────────────────────────────────────

export interface FaCipProjectRepository {
  save(project: FaCipProject): Promise<void>;
  findById(id: FaCipProjectId): Promise<FaCipProject | null>;
  findByCode(code: string): Promise<FaCipProject | null>;
  findAll(): Promise<FaCipProject[]>;
  findActive(): Promise<FaCipProject[]>;
  findCompleted(): Promise<FaCipProject[]>;
}

// ─── Revaluation ──────────────────────────────────────────────────────────────────

export interface FaRevaluationRepository {
  save(revaluation: FaRevaluation): Promise<void>;
  findById(id: FaRevaluationId): Promise<FaRevaluation | null>;
  findByNumber(number: string): Promise<FaRevaluation | null>;
  findByAssetId(assetId: string): Promise<FaRevaluation[]>;
  findAll(): Promise<FaRevaluation[]>;
}

// ─── Impairment ───────────────────────────────────────────────────────────────────

export interface FaImpairmentRepository {
  save(impairment: FaImpairment): Promise<void>;
  findById(id: FaImpairmentId): Promise<FaImpairment | null>;
  findByNumber(number: string): Promise<FaImpairment | null>;
  findByAssetId(assetId: string): Promise<FaImpairment[]>;
  findAll(): Promise<FaImpairment[]>;
}

// ─── Disposal ─────────────────────────────────────────────────────────────────────

export interface FaDisposalRepository {
  save(disposal: FaDisposal): Promise<void>;
  findById(id: FaDisposalId): Promise<FaDisposal | null>;
  findByNumber(number: string): Promise<FaDisposal | null>;
  findByAssetId(assetId: string): Promise<FaDisposal[]>;
  findAll(): Promise<FaDisposal[]>;
}

// ─── Transfer ─────────────────────────────────────────────────────────────────────

export interface FaTransferRepository {
  save(transfer: FaTransfer): Promise<void>;
  findById(id: FaTransferId): Promise<FaTransfer | null>;
  findByNumber(number: string): Promise<FaTransfer | null>;
  findByAssetId(assetId: string): Promise<FaTransfer[]>;
  findAll(): Promise<FaTransfer[]>;
}

// ─── Depreciation Run ─────────────────────────────────────────────────────────────

export interface FaDepreciationRunRepository {
  save(run: FaDepreciationRun): Promise<void>;
  findById(id: FaDepreciationRunId): Promise<FaDepreciationRun | null>;
  findByRunNumber(number: string): Promise<FaDepreciationRun | null>;
  findAll(): Promise<FaDepreciationRun[]>;
  findByPeriod(periodId: string): Promise<FaDepreciationRun[]>;
  findByStatus(status: string): Promise<FaDepreciationRun[]>;
}

// ─── Lease ────────────────────────────────────────────────────────────────────────

export interface FaLeaseRepository {
  save(lease: FaLease): Promise<void>;
  findById(id: FaLeaseId): Promise<FaLease | null>;
  findByNumber(number: string): Promise<FaLease | null>;
  findByAssetId(assetId: string): Promise<FaLease | null>;
  findAll(): Promise<FaLease[]>;
  findActive(): Promise<FaLease[]>;
}

// ─── Maintenance ──────────────────────────────────────────────────────────────────

export interface FaMaintenanceRecordRepository {
  save(record: FaMaintenanceRecord): Promise<void>;
  findById(id: FaMaintenanceRecordId): Promise<FaMaintenanceRecord | null>;
  findByRecordNumber(number: string): Promise<FaMaintenanceRecord | null>;
  findByAssetId(assetId: string): Promise<FaMaintenanceRecord[]>;
  findAll(): Promise<FaMaintenanceRecord[]>;
}

// ─── Physical Verification ───────────────────────────────────────────────────────

export interface FaPhysicalVerificationRepository {
  save(verification: FaPhysicalVerification): Promise<void>;
  findById(id: FaPhysicalVerificationId): Promise<FaPhysicalVerification | null>;
  findByNumber(number: string): Promise<FaPhysicalVerification | null>;
  findAll(): Promise<FaPhysicalVerification[]>;
  findByStatus(status: string): Promise<FaPhysicalVerification[]>;
}
