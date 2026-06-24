import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import type {
  ReportDefinitionRepository,
  ReportInstanceRepository,
  FormulaRepository,
  ConsolidationGroupRepository,
  ConsolidationRunRepository,
} from "../../domain/fr/fr-repositories.js";
import { FrReportDefinitionId, FrReportInstanceId, FrFormulaId, FrConsolidationGroupId, FrConsolidationRunId } from "../../domain/fr/fr-ids.js";
import { ReportDefinition, type ReportDefinitionState } from "../../domain/fr/fr-report-definition.js";
import { ReportInstance, type ReportInstanceState } from "../../domain/fr/fr-report-instance.js";
import { Formula, type FormulaState } from "../../domain/fr/fr-formula.js";
import { ConsolidationGroup, type ConsolidationGroupState } from "../../domain/fr/fr-consolidation.js";
import { ConsolidationRun, type ConsolidationRunState } from "../../domain/fr/fr-consolidation.js";
import { FrReportStatus, FrConsolidationStatus, FrReportCategoryType, FrFormulaType } from "../../domain/fr/fr-enums.js";

@Injectable()
export class PrismaReportDefinitionRepository implements ReportDefinitionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(def: ReportDefinition): Promise<void> {
    const s = def.toState();
    const data = {
      id: s.id,
      code: s.code,
      name: s.name,
      nameEn: s.nameEn,
      status: s.status,
      description: s.description,
      displayCurrency: s.displayCurrency,
      displayScale: s.displayScale,
      displayDecimals: s.displayDecimals,
      isComparative: s.isComparative,
      comparativePeriods: s.comparativePeriods,
      isConsolidated: s.isConsolidated,
      createdById: s.createdById,
      version: s.version,
      deletedAt: s.deletedAt,
    };

    await this.prisma.frReportDefinition.upsert({
      where: { id: s.id },
      create: data as any,
      update: data as any,
    });
  }

  async findById(id: FrReportDefinitionId): Promise<ReportDefinition | null> {
    const row = await this.prisma.frReportDefinition.findUnique({ where: { id: id.value } });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findByCode(code: string): Promise<ReportDefinition | null> {
    const row = await this.prisma.frReportDefinition.findUnique({ where: { code } });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findAll(): Promise<ReportDefinition[]> {
    const rows = await this.prisma.frReportDefinition.findMany({ orderBy: { createdAt: "desc" } });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findByCategory(categoryId: string): Promise<ReportDefinition[]> {
    const rows = await this.prisma.frReportDefinition.findMany({
      where: { categoryId },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findActive(): Promise<ReportDefinition[]> {
    const rows = await this.prisma.frReportDefinition.findMany({
      where: { status: FrReportStatus.Active, deletedAt: null },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async delete(id: FrReportDefinitionId): Promise<void> {
    await this.prisma.frReportDefinition.update({
      where: { id: id.value },
      data: { deletedAt: new Date() },
    });
  }

  private fromPrisma(row: any): ReportDefinition {
    return ReportDefinition.load({
      id: row.id,
      code: row.code,
      name: row.name,
      nameEn: row.nameEn ?? null,
      category: FrReportCategoryType.BalanceSheet,
      status: row.status,
      description: row.description ?? null,
      displayCurrency: row.displayCurrency,
      displayScale: row.displayScale,
      displayDecimals: row.displayDecimals,
      isComparative: row.isComparative,
      comparativePeriods: row.comparativePeriods,
      isConsolidated: row.isConsolidated,
      defaultFiscalYearId: null,
      createdById: row.createdById,
      rows: [],
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      version: row.version,
      deletedAt: row.deletedAt,
    });
  }
}

@Injectable()
export class PrismaReportInstanceRepository implements ReportInstanceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(instance: ReportInstance): Promise<void> {
    const s = instance.toState();
    await this.prisma.frReportInstance.upsert({
      where: { id: s.id },
      create: {
        id: s.id,
        reportId: s.reportDefId,
        instanceNumber: s.instanceNumber,
        status: s.status,
        fiscalYearId: s.fiscalYearId,
        periodId: s.periodId,
        periodNumber: s.periodNumber,
        periodName: s.periodName,
        asOfDate: s.asOfDate ? new Date(s.asOfDate) : null,
        legalEntityId: s.legalEntityId,
        consolidationRunId: s.consolidationRunId,
        reportingCurrency: s.reportingCurrency,
        generatedById: s.generatedById,
        generatedAt: s.generatedAt,
        approvedById: s.approvedById,
        approvedAt: s.approvedAt,
        errorMessage: s.errorMessage,
        deletedAt: s.deletedAt,
      } as any,
      update: {
        status: s.status,
        approvedById: s.approvedById,
        approvedAt: s.approvedAt,
        errorMessage: s.errorMessage,
        deletedAt: s.deletedAt,
      } as any,
    });
  }

  async findById(id: FrReportInstanceId): Promise<ReportInstance | null> {
    const row = await this.prisma.frReportInstance.findUnique({ where: { id: id.value } });
    if (!row) return null;
    return ReportInstance.load(this.rowToState(row as any));
  }

  async findByReportDef(reportDefId: string): Promise<ReportInstance[]> {
    const rows = await this.prisma.frReportInstance.findMany({
      where: { reportId: reportDefId },
      orderBy: { generatedAt: "desc" },
    });
    return rows.map(r => ReportInstance.load(this.rowToState(r as any)));
  }

  async findByFiscalYear(fiscalYearId: string): Promise<ReportInstance[]> {
    const rows = await this.prisma.frReportInstance.findMany({
      where: { fiscalYearId },
      orderBy: { generatedAt: "desc" },
    });
    return rows.map(r => ReportInstance.load(this.rowToState(r as any)));
  }

  async findByPeriod(fiscalYearId: string, periodNumber: number): Promise<ReportInstance[]> {
    const rows = await this.prisma.frReportInstance.findMany({
      where: { fiscalYearId, periodNumber },
      orderBy: { generatedAt: "desc" },
    });
    return rows.map(r => ReportInstance.load(this.rowToState(r as any)));
  }

  async findAll(): Promise<ReportInstance[]> {
    const rows = await this.prisma.frReportInstance.findMany({
      orderBy: { generatedAt: "desc" },
    });
    return rows.map(r => ReportInstance.load(this.rowToState(r as any)));
  }

  async findLatest(reportDefId: string): Promise<ReportInstance | null> {
    const row = await this.prisma.frReportInstance.findFirst({
      where: { reportId: reportDefId },
      orderBy: { generatedAt: "desc" },
    });
    if (!row) return null;
    return ReportInstance.load(this.rowToState(row as any));
  }

  async delete(id: FrReportInstanceId): Promise<void> {
    await this.prisma.frReportInstance.update({
      where: { id: id.value },
      data: { deletedAt: new Date() },
    });
  }

  private rowToState(row: any): ReportInstanceState {
    return {
      id: row.id,
      reportDefId: row.reportId,
      instanceNumber: row.instanceNumber,
      status: row.status,
      fiscalYearId: row.fiscalYearId,
      periodId: row.periodId ?? null,
      periodNumber: row.periodNumber ?? null,
      periodName: row.periodName ?? null,
      asOfDate: row.asOfDate?.toISOString() ?? null,
      legalEntityId: row.legalEntityId ?? null,
      consolidationRunId: row.consolidationRunId ?? null,
      reportingCurrency: row.reportingCurrency,
      exchangeRate: Number(row.exchangeRate ?? 1),
      rows: [],
      generatedById: row.generatedById,
      generatedAt: row.generatedAt,
      approvedById: row.approvedById ?? null,
      approvedAt: row.approvedAt ?? null,
      errorMessage: row.errorMessage ?? null,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    };
  }
}

@Injectable()
export class PrismaFormulaRepository implements FormulaRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(formula: Formula): Promise<void> {
    const s = formula.toState();
    await this.prisma.frFormula.upsert({
      where: { id: s.id },
      create: {
        id: s.id,
        code: s.code,
        name: s.name,
        formulaType: s.formulaType,
        expression: s.expression,
        description: s.description,
        returnType: s.returnType,
        isActive: s.isActive,
        createdById: s.createdById,
        deletedAt: s.deletedAt,
      } as any,
      update: {
        expression: s.expression,
        description: s.description,
        isActive: s.isActive,
        deletedAt: s.deletedAt,
        version: { increment: 1 },
      } as any,
    });
  }

  async findById(id: FrFormulaId): Promise<Formula | null> {
    const row = await this.prisma.frFormula.findUnique({ where: { id: id.value } });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findByCode(code: string): Promise<Formula | null> {
    const row = await this.prisma.frFormula.findUnique({ where: { code } });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findAll(): Promise<Formula[]> {
    const rows = await this.prisma.frFormula.findMany({ orderBy: { createdAt: "desc" } });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findActive(): Promise<Formula[]> {
    const rows = await this.prisma.frFormula.findMany({
      where: { isActive: true, deletedAt: null },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async delete(id: FrFormulaId): Promise<void> {
    await this.prisma.frFormula.update({
      where: { id: id.value },
      data: { deletedAt: new Date() },
    });
  }

  private fromPrisma(row: any): Formula {
    return Formula.load({
      id: row.id,
      code: row.code,
      name: row.name,
      formulaType: row.formulaType as FrFormulaType,
      expression: row.expression,
      description: row.description ?? null,
      returnType: row.returnType,
      minValue: row.minValue ? Number(row.minValue) : null,
      maxValue: row.maxValue ? Number(row.maxValue) : null,
      validationRule: row.validationRule ?? null,
      isActive: row.isActive,
      version: row.version,
      createdById: row.createdById,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    });
  }
}

@Injectable()
export class PrismaConsolidationGroupRepository implements ConsolidationGroupRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(group: ConsolidationGroup): Promise<void> {
    const s = group.toState();
    await this.prisma.frConsolidationGroup.upsert({
      where: { id: s.id },
      create: {
        id: s.id,
        code: s.code,
        name: s.name,
        description: s.description,
        parentCompanyId: s.parentCompanyId,
        currencyCode: s.currencyCode,
        isActive: s.isActive,
        createdById: s.createdById,
        deletedAt: s.deletedAt,
      } as any,
      update: {
        name: s.name,
        description: s.description,
        isActive: s.isActive,
        deletedAt: s.deletedAt,
      } as any,
    });

    for (const member of s.members) {
      await this.prisma.frConsolidationGroupMember.upsert({
        where: { groupId_legalEntityId: { groupId: s.id, legalEntityId: member.legalEntityId } },
        create: {
          groupId: s.id,
          legalEntityId: member.legalEntityId,
          legalEntityCode: member.legalEntityCode,
          legalEntityName: member.legalEntityName,
          ownershipPercentage: member.ownershipPercentage,
          consolidationMethod: member.consolidationMethod,
          consolidationDate: member.consolidationDate,
          functionalCurrency: member.functionalCurrency,
          goodwillAmount: BigInt(Math.round(member.goodwillAmount)),
          isActive: member.isActive,
        } as any,
        update: {
          ownershipPercentage: member.ownershipPercentage,
          isActive: member.isActive,
        } as any,
      });
    }
  }

  async findById(id: FrConsolidationGroupId): Promise<ConsolidationGroup | null> {
    const row = await this.prisma.frConsolidationGroup.findUnique({
      where: { id: id.value },
      include: { members: true },
    });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findByCode(code: string): Promise<ConsolidationGroup | null> {
    const row = await this.prisma.frConsolidationGroup.findUnique({
      where: { code },
      include: { members: true },
    });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findAll(): Promise<ConsolidationGroup[]> {
    const rows = await this.prisma.frConsolidationGroup.findMany({
      include: { members: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findActive(): Promise<ConsolidationGroup[]> {
    const rows = await this.prisma.frConsolidationGroup.findMany({
      where: { isActive: true, deletedAt: null },
      include: { members: true },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async delete(id: FrConsolidationGroupId): Promise<void> {
    await this.prisma.frConsolidationGroup.update({
      where: { id: id.value },
      data: { deletedAt: new Date() },
    });
  }

  private fromPrisma(row: any): ConsolidationGroup {
    return ConsolidationGroup.load({
      id: row.id,
      code: row.code,
      name: row.name,
      description: row.description ?? null,
      parentCompanyId: row.parentCompanyId,
      currencyCode: row.currencyCode,
      members: (row.members ?? []).map((m: any) => ({
        legalEntityId: m.legalEntityId,
        legalEntityCode: m.legalEntityCode,
        legalEntityName: m.legalEntityName,
        ownershipPercentage: Number(m.ownershipPercentage),
        consolidationMethod: m.consolidationMethod,
        consolidationDate: m.consolidationDate,
        functionalCurrency: m.functionalCurrency,
        goodwillAmount: Number(m.goodwillAmount),
        isActive: m.isActive,
      })),
      isActive: row.isActive,
      version: row.version,
      createdById: row.createdById,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    });
  }
}

@Injectable()
export class PrismaConsolidationRunRepository implements ConsolidationRunRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(run: ConsolidationRun): Promise<void> {
    const s = run.toState();
    await this.prisma.frConsolidationRun.upsert({
      where: { id: s.id },
      create: {
        id: s.id,
        groupId: s.groupId,
        runNumber: s.runNumber,
        status: s.status,
        fiscalYearId: s.fiscalYearId,
        periodId: s.periodId,
        periodNumber: s.periodNumber,
        periodName: s.periodName,
        asOfDate: s.asOfDate,
        reportingCurrency: s.reportingCurrency,
        preparedById: s.preparedById,
        reviewedById: s.reviewedById,
        approvedById: s.approvedById,
        errorMessage: s.errorMessage,
        notes: s.notes,
        deletedAt: s.deletedAt,
      } as any,
      update: {
        status: s.status,
        reviewedById: s.reviewedById,
        approvedById: s.approvedById,
        errorMessage: s.errorMessage,
        notes: s.notes,
        deletedAt: s.deletedAt,
      } as any,
    });
  }

  async findById(id: FrConsolidationRunId): Promise<ConsolidationRun | null> {
    const row = await this.prisma.frConsolidationRun.findUnique({
      where: { id: id.value },
      include: { entries: true },
    });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findAll(): Promise<ConsolidationRun[]> {
    const rows = await this.prisma.frConsolidationRun.findMany({
      include: { entries: true },
      orderBy: { periodNumber: "desc" },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findByGroup(groupId: string): Promise<ConsolidationRun[]> {
    const rows = await this.prisma.frConsolidationRun.findMany({
      where: { groupId },
      include: { entries: true },
      orderBy: { periodNumber: "desc" },
    });
    return rows.map(r => this.fromPrisma(r as any));
  }

  async findByPeriod(groupId: string, fiscalYearId: string, periodNumber: number): Promise<ConsolidationRun | null> {
    const row = await this.prisma.frConsolidationRun.findFirst({
      where: { groupId, fiscalYearId, periodNumber },
      include: { entries: true },
    });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async findLatestByGroup(groupId: string): Promise<ConsolidationRun | null> {
    const row = await this.prisma.frConsolidationRun.findFirst({
      where: { groupId },
      orderBy: { periodNumber: "desc" },
      include: { entries: true },
    });
    if (!row) return null;
    return this.fromPrisma(row as any);
  }

  async delete(id: FrConsolidationRunId): Promise<void> {
    await this.prisma.frConsolidationRun.update({
      where: { id: id.value },
      data: { deletedAt: new Date() },
    });
  }

  private fromPrisma(row: any): ConsolidationRun {
    return ConsolidationRun.load({
      id: row.id,
      groupId: row.groupId,
      runNumber: row.runNumber,
      status: row.status as FrConsolidationStatus,
      fiscalYearId: row.fiscalYearId,
      periodId: row.periodId ?? null,
      periodNumber: row.periodNumber,
      periodName: row.periodName,
      asOfDate: row.asOfDate,
      reportingCurrency: row.reportingCurrency,
      entries: (row.entries ?? []).map((e: any) => ({
        eliminationType: e.eliminationType,
        fromEntityId: e.fromEntityId ?? null,
        toEntityId: e.toEntityId ?? null,
        accountCode: e.accountCode,
        debitAmount: Number(e.debitAmount),
        creditAmount: Number(e.creditAmount),
        description: e.description ?? null,
        isAutoDetected: e.isAutoDetected ?? false,
        sourceBatchId: e.sourceBatchId ?? null,
      })),
      preparedById: row.preparedById,
      reviewedById: row.reviewedById ?? null,
      approvedById: row.approvedById ?? null,
      errorMessage: row.errorMessage ?? null,
      notes: row.notes ?? null,
      version: row.version,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    });
  }
}
