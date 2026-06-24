import { Injectable, Inject } from "@nestjs/common";
import type {
  ReportDefinitionRepository,
  ReportInstanceRepository,
} from "../../domain/fr/fr-repositories.js";
import { ReportInstance, type ReportInstanceState, type ReportInstanceRowValue } from "../../domain/fr/fr-report-instance.js";
import type { ReportCellDefinition } from "../../domain/fr/fr-value-objects.js";
import { FrRowType, FrCellType } from "../../domain/fr/fr-enums.js";
import { FormulaEngine, type FormulaContext } from "./formula-engine.js";
import { GlBalanceProvider } from "./gl-balance-provider.js";

export type AccountBalanceProvider = GlBalanceProvider;

export interface ReportGenerateParams {
  reportDefId: string;
  fiscalYearId: string;
  periodId?: string;
  periodNumber?: number;
  periodName?: string;
  asOfDate?: string;
  legalEntityId?: string;
  consolidationRunId?: string;
  generatedById: string;
}

@Injectable()
export class ReportEngine {
  constructor(
    private readonly reportDefRepo: ReportDefinitionRepository,
    private readonly instanceRepo: ReportInstanceRepository,
    private readonly formulaEngine: FormulaEngine,
    private readonly balanceProvider: GlBalanceProvider,
  ) {}

  async generate(params: ReportGenerateParams): Promise<any> {
    const reportDef = await this.reportDefRepo.findById(params.reportDefId as any);
    if (!reportDef) throw new Error("Report definition not found");

    const instance = ReportInstance.create({
      ...params,
      reportDefId: params.reportDefId,
      instanceNumber: `RPT-${params.reportDefId}-${Date.now()}`,
      reportingCurrency: reportDef.displayCurrency,
    });

    try {
      const periodBalances = await this.balanceProvider.getPeriodBalances(
        params.fiscalYearId,
        params.periodNumber,
      );

      const rows = await this.buildRows(reportDef, periodBalances, params);
      instance.complete(rows);
    } catch (err) {
      instance.fail((err as Error).message);
      await this.instanceRepo.save(instance);
      throw err;
    }

    await this.instanceRepo.save(instance);
    return instance.toState();
  }

  private async buildRows(
    reportDef: any,
    periodBalances: Record<string, number>,
    params: ReportGenerateParams,
  ): Promise<ReportInstanceRowValue[]> {
    const rows: ReportInstanceRowValue[] = [];
    const context: FormulaContext = {
      variables: {},
      accountBalances: periodBalances,
      periodValues: {},
      reportValues: {},
    };

    for (const rowDef of reportDef.rows) {
      if (!rowDef.isVisible) continue;

      let values: Record<string, number> = {};

      if (rowDef.rowType === FrRowType.Account) {
        const balance = periodBalances[rowDef.cells?.[0]?.accountCode ?? ""] ?? 0;
        values = { "default": balance };
      } else if (rowDef.rowType === FrRowType.Formula && rowDef.cells?.length > 0) {
        values = await this.evaluateRowCells(rowDef.cells, context, params);
      }

      rows.push({
        rowDefId: rowDef.rowCode ?? null,
        parentRowId: rowDef.parentRowCode ?? null,
        rowType: rowDef.rowType,
        rowCode: rowDef.rowCode ?? null,
        label: rowDef.label,
        displayOrder: rowDef.displayOrder,
        indentLevel: rowDef.indentLevel,
        isBold: rowDef.isBold,
        values,
      });
    }

    return rows;
  }

  private async evaluateRowCells(
    cells: ReportCellDefinition[],
    context: FormulaContext,
    params: ReportGenerateParams,
  ): Promise<Record<string, number>> {
    const values: Record<string, number> = {};

    for (const cell of cells) {
      const colKey = cell.columnId ?? "default";

      switch (cell.cellType as FrCellType) {
        case FrCellType.AccountBalance:
          if (cell.accountCode) {
            const balance = await this.balanceProvider.getAccountBalance(
              cell.accountCode,
              params.fiscalYearId,
              params.periodNumber,
            );
            values[colKey] = balance;
          }
          break;

        case FrCellType.Formula:
          if (cell.formulaId) {
            values[colKey] = await this.formulaEngine.evaluateNested(cell.formulaId, context);
          } else if (cell.formulaText) {
            values[colKey] = await this.formulaEngine.evaluate(cell.formulaText, context);
          }
          break;

        case FrCellType.Calculated:
          if (cell.formulaText) {
            values[colKey] = await this.formulaEngine.evaluate(cell.formulaText, context);
          }
          break;

        case FrCellType.Aggregated:
          if (cell.aggregationFunction) {
            balancesList = await this.getAggregatedBalances(cell, params);
            values[colKey] = this.applyAggregation(cell.aggregationFunction, balancesList);
          }
          break;

        case FrCellType.Variance:
          if (cell.formulaText) {
            const current = await this.formulaEngine.evaluate(cell.formulaText, context);
            const previous = await this.getComparativeBalance(cell, params);
            values[colKey] = current - previous;
          }
          break;

        case FrCellType.Percentage:
          if (cell.formulaText) {
            const numerator = await this.formulaEngine.evaluate(cell.formulaText, context);
            const denominator = await this.getComparativeBalance(cell, params);
            values[colKey] = denominator !== 0 ? (numerator / denominator) * 100 : 0;
          }
          break;

        default:
          if (cell.staticValue !== null) {
            values[colKey] = Number(cell.staticValue) || 0;
          }
          break;
      }
    }

    return values;
  }

  private async getAggregatedBalances(
    cell: ReportCellDefinition,
    params: ReportGenerateParams,
  ): Promise<number[]> {
    const balances: number[] = [];
    const count = cell.periodCount || 1;
    const offset = cell.periodOffset || 0;

    for (let i = 0; i < count; i++) {
      const periodNum = (params.periodNumber ?? 1) - offset - i;
      const balance = await this.balanceProvider.getAccountBalance(
        cell.accountCode ?? "",
        params.fiscalYearId,
        periodNum,
      );
      balances.push(balance);
    }

    return balances;
  }

  private async getComparativeBalance(
    cell: ReportCellDefinition,
    params: ReportGenerateParams,
  ): Promise<number> {
    return this.balanceProvider.getAccountBalance(
      cell.accountCode ?? "",
      params.fiscalYearId,
      (params.periodNumber ?? 1) - 1,
    );
  }

  private applyAggregation(fn: string, values: number[]): number {
    switch (fn.toUpperCase()) {
      case "SUM": return values.reduce((a, b) => a + b, 0);
      case "AVG": return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
      case "MIN": return Math.min(...values);
      case "MAX": return Math.max(...values);
      case "COUNT": return values.filter(v => v !== 0).length;
      default: return values[values.length - 1] ?? 0;
    }
  }
}

// Workaround for TS hoisting
let balancesList: number[];
