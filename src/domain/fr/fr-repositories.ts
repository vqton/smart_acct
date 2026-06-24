import type { ReportDefinition, ReportDefinitionState } from "./fr-report-definition.js";
import type { ReportInstance, ReportInstanceState } from "./fr-report-instance.js";
import type { Formula, FormulaState } from "./fr-formula.js";
import type { ConsolidationGroup, ConsolidationGroupState } from "./fr-consolidation.js";
import type { ConsolidationRun, ConsolidationRunState } from "./fr-consolidation.js";
import type { FrReportDefinitionId, FrReportInstanceId, FrFormulaId, FrConsolidationGroupId, FrConsolidationRunId, FrReportCategoryId } from "./fr-ids.js";

export interface ReportDefinitionRepository {
  save(def: ReportDefinition): Promise<void>;
  findById(id: FrReportDefinitionId): Promise<ReportDefinition | null>;
  findByCode(code: string): Promise<ReportDefinition | null>;
  findAll(): Promise<ReportDefinition[]>;
  findByCategory(categoryId: string): Promise<ReportDefinition[]>;
  findActive(): Promise<ReportDefinition[]>;
  delete(id: FrReportDefinitionId): Promise<void>;
}

export interface ReportInstanceRepository {
  save(instance: ReportInstance): Promise<void>;
  findById(id: FrReportInstanceId): Promise<ReportInstance | null>;
  findByReportDef(reportDefId: string): Promise<ReportInstance[]>;
  findByFiscalYear(fiscalYearId: string): Promise<ReportInstance[]>;
  findByPeriod(fiscalYearId: string, periodNumber: number): Promise<ReportInstance[]>;
  findAll(): Promise<ReportInstance[]>;
  findLatest(reportDefId: string): Promise<ReportInstance | null>;
  delete(id: FrReportInstanceId): Promise<void>;
}

export interface FormulaRepository {
  save(formula: Formula): Promise<void>;
  findById(id: FrFormulaId): Promise<Formula | null>;
  findByCode(code: string): Promise<Formula | null>;
  findAll(): Promise<Formula[]>;
  findActive(): Promise<Formula[]>;
  delete(id: FrFormulaId): Promise<void>;
}

export interface ConsolidationGroupRepository {
  save(group: ConsolidationGroup): Promise<void>;
  findById(id: FrConsolidationGroupId): Promise<ConsolidationGroup | null>;
  findByCode(code: string): Promise<ConsolidationGroup | null>;
  findAll(): Promise<ConsolidationGroup[]>;
  findActive(): Promise<ConsolidationGroup[]>;
  delete(id: FrConsolidationGroupId): Promise<void>;
}

export interface ConsolidationRunRepository {
  save(run: ConsolidationRun): Promise<void>;
  findById(id: FrConsolidationRunId): Promise<ConsolidationRun | null>;
  findByGroup(groupId: string): Promise<ConsolidationRun[]>;
  findByPeriod(groupId: string, fiscalYearId: string, periodNumber: number): Promise<ConsolidationRun | null>;
  findAll(): Promise<ConsolidationRun[]>;
  findLatestByGroup(groupId: string): Promise<ConsolidationRun | null>;
  delete(id: FrConsolidationRunId): Promise<void>;
}
