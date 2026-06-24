import { describe, it, expect } from "vitest";
import { ReportDefinition } from "../fr-report-definition.js";
import { ConsolidationRun } from "../fr-consolidation.js";
import { ConsolidationEliminationEntry } from "../fr-value-objects.js";
import { FrReportCategoryType, FrEliminationType } from "../fr-enums.js";
import {
  ActiveReportSpec,
  ReportHasRowsSpec,
  ConsolidationCanApproveSpec,
} from "../fr-specifications.js";

describe("ActiveReportSpec", () => {
  it("returns true for active report", () => {
    const spec = new ActiveReportSpec();
    const r = ReportDefinition.create({
      code: "BS", name: "BS",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    expect(spec.isSatisfiedBy(r)).toBe(false);
    r.activate();
    expect(spec.isSatisfiedBy(r)).toBe(true);
  });
});

describe("ReportHasRowsSpec", () => {
  it("returns false for empty report", () => {
    const spec = new ReportHasRowsSpec();
    const r = ReportDefinition.create({
      code: "BS", name: "BS",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    expect(spec.isSatisfiedBy(r)).toBe(false);
  });

  it("returns true for report with rows", () => {
    const spec = new ReportHasRowsSpec();
    const r = ReportDefinition.create({
      code: "BS", name: "BS",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    r.addRow({
      rowCode: "A", label: "Assets", rowType: "section",
      indentLevel: 0, displayOrder: 1, isBold: true, isVisible: true,
      showSubtotal: false, pageBreakBefore: false, parentRowCode: null,
      labelEn: null, cells: [],
    });
    expect(spec.isSatisfiedBy(r)).toBe(true);
  });
});

describe("ConsolidationCanApproveSpec", () => {
  it("returns false for non-verified run", () => {
    const spec = new ConsolidationCanApproveSpec();
    const r = ConsolidationRun.create({
      groupId: "g-1", runNumber: "C-1",
      fiscalYearId: "fy-2026", periodNumber: 1, periodName: "Jan",
      asOfDate: new Date(), preparedById: "u-1",
    });
    expect(spec.isSatisfiedBy(r)).toBe(false);
  });
});
