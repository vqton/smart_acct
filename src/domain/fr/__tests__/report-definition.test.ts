import { describe, it, expect } from "vitest";
import { ReportDefinition } from "../fr-report-definition.js";
import { FrReportCategoryType, FrReportStatus, FrRowType } from "../fr-enums.js";

describe("ReportDefinition", () => {
  it("creates with valid params", () => {
    const d = ReportDefinition.create({
      code: "BS_01",
      name: "Bảng cân đối kế toán",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    expect(d.code).toBe("BS_01");
    expect(d.name).toBe("Bảng cân đối kế toán");
    expect(d.category).toBe(FrReportCategoryType.BalanceSheet);
    expect(d.status).toBe(FrReportStatus.Draft);
    expect(d.isComparative).toBe(false);
  });

  it("activates report", () => {
    const d = ReportDefinition.create({
      code: "PL_01",
      name: "Báo cáo kết quả KD",
      category: FrReportCategoryType.IncomeStatement,
      createdById: "user-1",
    });
    d.activate();
    expect(d.status).toBe(FrReportStatus.Active);
  });

  it("deactivates active report", () => {
    const d = ReportDefinition.create({
      code: "CF_01",
      name: "Báo cáo lưu chuyển tiền tệ",
      category: FrReportCategoryType.CashFlow,
      createdById: "user-1",
    });
    d.activate();
    d.deactivate();
    expect(d.status).toBe(FrReportStatus.Inactive);
  });

  it("rejects deactivating draft report", () => {
    const d = ReportDefinition.create({
      code: "TB_01", name: "Trial Balance",
      category: FrReportCategoryType.TrialBalance,
      createdById: "user-1",
    });
    expect(() => d.deactivate()).toThrow("Only active reports can be deactivated");
  });

  it("adds row to report", () => {
    const d = ReportDefinition.create({
      code: "BS_02", name: "Balance Sheet",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    d.addRow({
      rowCode: "A", label: "Tài sản", rowType: "section",
      indentLevel: 0, displayOrder: 1, isBold: true, isVisible: true,
      showSubtotal: false, pageBreakBefore: false, parentRowCode: null,
      labelEn: null, cells: [],
    });
    expect(d.rows.length).toBe(1);
    expect(d.rows[0].rowCode).toBe("A");
  });

  it("rejects row with missing parent", () => {
    const d = ReportDefinition.create({
      code: "BS_03", name: "BS",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    expect(() => d.addRow({
      rowCode: "A1", label: "Sub", rowType: "account",
      indentLevel: 1, displayOrder: 1, isBold: false, isVisible: true,
      showSubtotal: false, pageBreakBefore: false, parentRowCode: "NONEXISTENT",
      labelEn: null, cells: [],
    })).toThrow("Parent row NONEXISTENT not found");
  });

  it("round-trips through toState and load", () => {
    const d = ReportDefinition.create({
      code: "BS_04", name: "BS",
      category: FrReportCategoryType.BalanceSheet,
      createdById: "user-1",
    });
    d.activate();
    d.addRow({
      rowCode: "A", label: "Assets", rowType: "section",
      indentLevel: 0, displayOrder: 1, isBold: true, isVisible: true,
      showSubtotal: false, pageBreakBefore: false, parentRowCode: null,
      labelEn: "Assets", cells: [],
    });

    const state = d.toState();
    const loaded = ReportDefinition.load(state);
    expect(loaded.code).toBe(d.code);
    expect(loaded.name).toBe(d.name);
    expect(loaded.status).toBe(d.status);
    expect(loaded.rows.length).toBe(1);
    expect(loaded.rows[0].labelEn).toBe("Assets");
  });
});
