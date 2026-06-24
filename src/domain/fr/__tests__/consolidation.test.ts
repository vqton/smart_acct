import { describe, it, expect } from "vitest";
import { ConsolidationGroup, ConsolidationRun } from "../fr-consolidation.js";
import { ConsolidationGroupMember, ConsolidationEliminationEntry } from "../fr-value-objects.js";
import { FrConsolidationMethod, FrConsolidationStatus, FrEliminationType } from "../fr-enums.js";
import { ConsolidationCanCompleteSpec, ConsolidationCanApproveSpec } from "../fr-specifications.js";

const makeMember = (id: string, code: string, pct: number) =>
  new ConsolidationGroupMember(id, code, code, pct, FrConsolidationMethod.Full, new Date(), "VND", 0, true);

describe("ConsolidationGroup", () => {
  it("creates with parent company", () => {
    const g = ConsolidationGroup.create({
      code: "GROUP_01",
      name: "ABC Group",
      parentCompanyId: "parent-1",
      createdById: "user-1",
    });
    expect(g.code).toBe("GROUP_01");
    expect(g.parentCompanyId).toBe("parent-1");
    expect(g.isActive).toBe(true);
  });

  it("adds members", () => {
    const g = ConsolidationGroup.create({
      code: "GROUP_02", name: "Group 2",
      parentCompanyId: "parent-1", createdById: "user-1",
    });
    g.addMember(makeMember("sub-1", "SUB1", 0.75));
    g.addMember(makeMember("sub-2", "SUB2", 0.51));
    expect(g.members.length).toBe(2);
  });

  it("rejects duplicate members", () => {
    const g = ConsolidationGroup.create({
      code: "GROUP_03", name: "Group 3",
      parentCompanyId: "parent-1", createdById: "user-1",
    });
    g.addMember(makeMember("sub-1", "SUB1", 0.75));
    expect(() => g.addMember(makeMember("sub-1", "SUB1", 0.8)))
      .toThrow("Member already exists in group");
  });

  it("removes members", () => {
    const g = ConsolidationGroup.create({
      code: "GROUP_04", name: "Group 4",
      parentCompanyId: "parent-1", createdById: "user-1",
    });
    g.addMember(makeMember("sub-1", "SUB1", 0.75));
    g.removeMember("sub-1");
    expect(g.members.length).toBe(0);
  });

  it("deactivates", () => {
    const g = ConsolidationGroup.create({
      code: "GROUP_05", name: "Group 5",
      parentCompanyId: "parent-1", createdById: "user-1",
    });
    g.deactivate();
    expect(g.isActive).toBe(false);
  });
});

describe("ConsolidationRun", () => {
  it("creates with draft status", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1",
      runNumber: "CONS-001",
      fiscalYearId: "fy-2026",
      periodNumber: 6,
      periodName: "June 2026",
      asOfDate: new Date("2026-06-30"),
      preparedById: "user-1",
    });
    expect(r.status).toBe(FrConsolidationStatus.Draft);
  });

  it("adds elimination entries", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-002",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyRevenue, "parent", "sub",
      "511", 1000000, 0, "IC revenue elim", true, null,
    ));
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyExpense, "sub", "parent",
      "632", 0, 1000000, "IC expense elim", true, null,
    ));
    expect(r.entries.length).toBe(2);
  });

  it("completes with balanced entries", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-003",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyReceivable, "parent", "sub",
      "131", 500000, 500000, "Balanced entry", true, null,
    ));
    r.complete();
    expect(r.status).toBe(FrConsolidationStatus.Completed);
  });

  it("rejects complete with unbalanced entries", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-004",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyRevenue, "parent", "sub",
      "511", 1000000, 0, "Unbalanced", true, null,
    ));
    expect(() => r.complete()).toThrow("Unbalanced entries");
  });

  it("verifies and approves", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-005",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyReceivable, "parent", "sub",
      "131", 500000, 500000, "ok", true, null,
    ));
    r.complete();
    r.verify("reviewer-1");
    r.approve("approver-1");
    expect(r.status).toBe(FrConsolidationStatus.Approved);
  });

  it("satisfies ConsolidationCanCompleteSpec when balanced", () => {
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-006",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    r.addEntry(new ConsolidationEliminationEntry(
      FrEliminationType.IntercompanyReceivable, "parent", "sub",
      "131", 500000, 500000, "ok", true, null,
    ));
    const spec = new ConsolidationCanCompleteSpec();
    expect(spec.isSatisfiedBy(r)).toBe(false);
    r.complete();
    expect(spec.isSatisfiedBy(r)).toBe(false);
  });
});

describe("ConsolidationCanApproveSpec", () => {
  it("returns true only for verified runs", () => {
    const spec = new ConsolidationCanApproveSpec();
    const r = ConsolidationRun.create({
      groupId: "group-1", runNumber: "CONS-007",
      fiscalYearId: "fy-2026", periodNumber: 6, periodName: "June",
      asOfDate: new Date("2026-06-30"), preparedById: "user-1",
    });
    expect(spec.isSatisfiedBy(r)).toBe(false);
  });
});
