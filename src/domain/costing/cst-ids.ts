import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class CostVersionId extends Identifier {
  static new(): CostVersionId { return new CostVersionId(IdGenerator.uuid()); }
}

export class WorkCenterId extends Identifier {
  static new(): WorkCenterId { return new WorkCenterId(IdGenerator.uuid()); }
}

export class BomId extends Identifier {
  static new(): BomId { return new BomId(IdGenerator.uuid()); }
}

export class BomLineId extends Identifier {
  static new(): BomLineId { return new BomLineId(IdGenerator.uuid()); }
}

export class BomRoutingId extends Identifier {
  static new(): BomRoutingId { return new BomRoutingId(IdGenerator.uuid()); }
}

export class ProductionOrderId extends Identifier {
  static new(): ProductionOrderId { return new ProductionOrderId(IdGenerator.uuid()); }
}

export class ProductionOrderComponentId extends Identifier {
  static new(): ProductionOrderComponentId { return new ProductionOrderComponentId(IdGenerator.uuid()); }
}

export class ProductionOrderOperationId extends Identifier {
  static new(): ProductionOrderOperationId { return new ProductionOrderOperationId(IdGenerator.uuid()); }
}

export class CostPoolId extends Identifier {
  static new(): CostPoolId { return new CostPoolId(IdGenerator.uuid()); }
}

export class AllocationRuleId extends Identifier {
  static new(): AllocationRuleId { return new AllocationRuleId(IdGenerator.uuid()); }
}

export class AllocationEntryId extends Identifier {
  static new(): AllocationEntryId { return new AllocationEntryId(IdGenerator.uuid()); }
}

export class OverheadRateId extends Identifier {
  static new(): OverheadRateId { return new OverheadRateId(IdGenerator.uuid()); }
}

export class CostSnapshotId extends Identifier {
  static new(): CostSnapshotId { return new CostSnapshotId(IdGenerator.uuid()); }
}

export class CostRollupId extends Identifier {
  static new(): CostRollupId { return new CostRollupId(IdGenerator.uuid()); }
}

export class ProductionVarianceId extends Identifier {
  static new(): ProductionVarianceId { return new ProductionVarianceId(IdGenerator.uuid()); }
}

export class PeriodCloseId extends Identifier {
  static new(): PeriodCloseId { return new PeriodCloseId(IdGenerator.uuid()); }
}
