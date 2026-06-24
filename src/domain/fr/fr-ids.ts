import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class FrReportDefinitionId extends Identifier {
  static new(): FrReportDefinitionId { return new FrReportDefinitionId(IdGenerator.uuid()); }
}

export class FrReportInstanceId extends Identifier {
  static new(): FrReportInstanceId { return new FrReportInstanceId(IdGenerator.uuid()); }
}

export class FrFormulaId extends Identifier {
  static new(): FrFormulaId { return new FrFormulaId(IdGenerator.uuid()); }
}

export class FrConsolidationGroupId extends Identifier {
  static new(): FrConsolidationGroupId { return new FrConsolidationGroupId(IdGenerator.uuid()); }
}

export class FrConsolidationRunId extends Identifier {
  static new(): FrConsolidationRunId { return new FrConsolidationRunId(IdGenerator.uuid()); }
}

export class FrConsolidationEntryId extends Identifier {
  static new(): FrConsolidationEntryId { return new FrConsolidationEntryId(IdGenerator.uuid()); }
}

export class FrReportCategoryId extends Identifier {
  static new(): FrReportCategoryId { return new FrReportCategoryId(IdGenerator.uuid()); }
}

export class FrReportingDimensionId extends Identifier {
  static new(): FrReportingDimensionId { return new FrReportingDimensionId(IdGenerator.uuid()); }
}

export class FrFinancialRatioId extends Identifier {
  static new(): FrFinancialRatioId { return new FrFinancialRatioId(IdGenerator.uuid()); }
}
