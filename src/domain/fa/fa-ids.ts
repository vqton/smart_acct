import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class FaAssetGroupId extends Identifier {
  static new(): FaAssetGroupId { return new FaAssetGroupId(IdGenerator.uuid()); }
  static from(id: string): FaAssetGroupId { return new FaAssetGroupId(id); }
}

export class FaAssetClassId extends Identifier {
  static new(): FaAssetClassId { return new FaAssetClassId(IdGenerator.uuid()); }
  static from(id: string): FaAssetClassId { return new FaAssetClassId(id); }
}

export class FaAssetCategoryId extends Identifier {
  static new(): FaAssetCategoryId { return new FaAssetCategoryId(IdGenerator.uuid()); }
  static from(id: string): FaAssetCategoryId { return new FaAssetCategoryId(id); }
}

export class FaAssetId extends Identifier {
  static new(): FaAssetId { return new FaAssetId(IdGenerator.uuid()); }
  static from(id: string): FaAssetId { return new FaAssetId(id); }
}

export class FaAssetDepreciationId extends Identifier {
  static new(): FaAssetDepreciationId { return new FaAssetDepreciationId(IdGenerator.uuid()); }
  static from(id: string): FaAssetDepreciationId { return new FaAssetDepreciationId(id); }
}

export class FaDepreciationRunId extends Identifier {
  static new(): FaDepreciationRunId { return new FaDepreciationRunId(IdGenerator.uuid()); }
  static from(id: string): FaDepreciationRunId { return new FaDepreciationRunId(id); }
}

export class FaDepreciationEntryId extends Identifier {
  static new(): FaDepreciationEntryId { return new FaDepreciationEntryId(IdGenerator.uuid()); }
  static from(id: string): FaDepreciationEntryId { return new FaDepreciationEntryId(id); }
}

export class FaRevaluationId extends Identifier {
  static new(): FaRevaluationId { return new FaRevaluationId(IdGenerator.uuid()); }
  static from(id: string): FaRevaluationId { return new FaRevaluationId(id); }
}

export class FaImpairmentId extends Identifier {
  static new(): FaImpairmentId { return new FaImpairmentId(IdGenerator.uuid()); }
  static from(id: string): FaImpairmentId { return new FaImpairmentId(id); }
}

export class FaDisposalId extends Identifier {
  static new(): FaDisposalId { return new FaDisposalId(IdGenerator.uuid()); }
  static from(id: string): FaDisposalId { return new FaDisposalId(id); }
}

export class FaTransferId extends Identifier {
  static new(): FaTransferId { return new FaTransferId(IdGenerator.uuid()); }
  static from(id: string): FaTransferId { return new FaTransferId(id); }
}

export class FaSplitMergeId extends Identifier {
  static new(): FaSplitMergeId { return new FaSplitMergeId(IdGenerator.uuid()); }
  static from(id: string): FaSplitMergeId { return new FaSplitMergeId(id); }
}

export class FaCipProjectId extends Identifier {
  static new(): FaCipProjectId { return new FaCipProjectId(IdGenerator.uuid()); }
  static from(id: string): FaCipProjectId { return new FaCipProjectId(id); }
}

export class FaCipCostId extends Identifier {
  static new(): FaCipCostId { return new FaCipCostId(IdGenerator.uuid()); }
  static from(id: string): FaCipCostId { return new FaCipCostId(id); }
}

export class FaCipMilestoneId extends Identifier {
  static new(): FaCipMilestoneId { return new FaCipMilestoneId(IdGenerator.uuid()); }
  static from(id: string): FaCipMilestoneId { return new FaCipMilestoneId(id); }
}

export class FaCipSettlementId extends Identifier {
  static new(): FaCipSettlementId { return new FaCipSettlementId(IdGenerator.uuid()); }
  static from(id: string): FaCipSettlementId { return new FaCipSettlementId(id); }
}

export class FaLeaseId extends Identifier {
  static new(): FaLeaseId { return new FaLeaseId(IdGenerator.uuid()); }
  static from(id: string): FaLeaseId { return new FaLeaseId(id); }
}

export class FaLeasePaymentId extends Identifier {
  static new(): FaLeasePaymentId { return new FaLeasePaymentId(IdGenerator.uuid()); }
  static from(id: string): FaLeasePaymentId { return new FaLeasePaymentId(id); }
}

export class FaMaintenancePlanId extends Identifier {
  static new(): FaMaintenancePlanId { return new FaMaintenancePlanId(IdGenerator.uuid()); }
  static from(id: string): FaMaintenancePlanId { return new FaMaintenancePlanId(id); }
}

export class FaMaintenanceScheduleId extends Identifier {
  static new(): FaMaintenanceScheduleId { return new FaMaintenanceScheduleId(IdGenerator.uuid()); }
  static from(id: string): FaMaintenanceScheduleId { return new FaMaintenanceScheduleId(id); }
}

export class FaMaintenanceRecordId extends Identifier {
  static new(): FaMaintenanceRecordId { return new FaMaintenanceRecordId(IdGenerator.uuid()); }
  static from(id: string): FaMaintenanceRecordId { return new FaMaintenanceRecordId(id); }
}

export class FaAssetTagId extends Identifier {
  static new(): FaAssetTagId { return new FaAssetTagId(IdGenerator.uuid()); }
  static from(id: string): FaAssetTagId { return new FaAssetTagId(id); }
}

export class FaPhysicalVerificationId extends Identifier {
  static new(): FaPhysicalVerificationId { return new FaPhysicalVerificationId(IdGenerator.uuid()); }
  static from(id: string): FaPhysicalVerificationId { return new FaPhysicalVerificationId(id); }
}

export class FaInsurancePolicyId extends Identifier {
  static new(): FaInsurancePolicyId { return new FaInsurancePolicyId(IdGenerator.uuid()); }
  static from(id: string): FaInsurancePolicyId { return new FaInsurancePolicyId(id); }
}

export class FaInsuranceClaimId extends Identifier {
  static new(): FaInsuranceClaimId { return new FaInsuranceClaimId(IdGenerator.uuid()); }
  static from(id: string): FaInsuranceClaimId { return new FaInsuranceClaimId(id); }
}

export class FaGlMappingId extends Identifier {
  static new(): FaGlMappingId { return new FaGlMappingId(IdGenerator.uuid()); }
  static from(id: string): FaGlMappingId { return new FaGlMappingId(id); }
}

export class FaAssetHistoryId extends Identifier {
  static new(): FaAssetHistoryId { return new FaAssetHistoryId(IdGenerator.uuid()); }
  static from(id: string): FaAssetHistoryId { return new FaAssetHistoryId(id); }
}

export class FaSnapshotId extends Identifier {
  static new(): FaSnapshotId { return new FaSnapshotId(IdGenerator.uuid()); }
  static from(id: string): FaSnapshotId { return new FaSnapshotId(id); }
}

export class FaApprovalId extends Identifier {
  static new(): FaApprovalId { return new FaApprovalId(IdGenerator.uuid()); }
  static from(id: string): FaApprovalId { return new FaApprovalId(id); }
}
