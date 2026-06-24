import { describe, it, expect } from "vitest";
import { ReportInstance } from "../fr-report-instance.js";
import { FrInstanceStatus } from "../fr-enums.js";

describe("ReportInstance", () => {
  it("creates with generating status", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-001",
      fiscalYearId: "fy-2026",
      periodNumber: 6,
      periodName: "Tháng 6",
      generatedById: "user-1",
    });
    expect(inst.status).toBe(FrInstanceStatus.Generating);
    expect(inst.instanceNumber).toBe("RPT-001");
  });

  it("completes with rows", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-002",
      fiscalYearId: "fy-2026",
      generatedById: "user-1",
    });
    inst.complete([
      { rowDefId: null, parentRowId: null, rowType: "header", rowCode: "A", label: "Assets", displayOrder: 1, indentLevel: 0, isBold: true, values: {} },
      { rowDefId: null, parentRowId: "A", rowType: "account", rowCode: "111", label: "Cash", displayOrder: 2, indentLevel: 1, isBold: false, values: { default: 1000000 } },
    ]);
    expect(inst.status).toBe(FrInstanceStatus.Completed);
    expect(inst.rows.length).toBe(2);
  });

  it("fails with error message", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-003",
      fiscalYearId: "fy-2026",
      generatedById: "user-1",
    });
    inst.fail("Account 999 not found");
    expect(inst.status).toBe(FrInstanceStatus.Failed);
    expect(inst.errorMessage).toBe("Account 999 not found");
  });

  it("approves completed instance", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-004",
      fiscalYearId: "fy-2026",
      generatedById: "user-1",
    });
    inst.complete([]);
    inst.approve("approver-1");
    expect(inst.status).toBe(FrInstanceStatus.Approved);
    expect(inst.approvedById).toBe("approver-1");
  });

  it("rejects approving non-completed instance", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-005",
      fiscalYearId: "fy-2026",
      generatedById: "user-1",
    });
    expect(() => inst.approve("approver-1"))
      .toThrow("Only completed instances can be approved");
  });

  it("locks approved instance", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-006",
      fiscalYearId: "fy-2026",
      generatedById: "user-1",
    });
    inst.complete([]);
    inst.approve("approver-1");
    inst.lock();
    expect(inst.status).toBe(FrInstanceStatus.Locked);
  });

  it("round-trips through toState and load", () => {
    const inst = ReportInstance.create({
      reportDefId: "rpt-1",
      instanceNumber: "RPT-007",
      fiscalYearId: "fy-2026",
      periodNumber: 12,
      periodName: "Tháng 12",
      asOfDate: "2026-12-31",
      legalEntityId: "entity-1",
      generatedById: "user-1",
    });
    inst.complete([]);
    inst.approve("user-2");

    const state = inst.toState();
    const loaded = ReportInstance.load(state);
    expect(loaded.instanceNumber).toBe("RPT-007");
    expect(loaded.status).toBe(FrInstanceStatus.Approved);
    expect(loaded.approvedById).toBe("user-2");
    expect(loaded.legalEntityId).toBe("entity-1");
  });
});
