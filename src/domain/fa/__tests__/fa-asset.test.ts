import { describe, it, expect } from "vitest";
import { FaAsset } from "../fa-asset.js";
import { FaCipProject } from "../fa-cip.js";
import { FaRevaluation } from "../fa-revaluation.js";
import { FaImpairment } from "../fa-impairment.js";
import { FaDisposal } from "../fa-disposal.js";
import { FaTransfer } from "../fa-transfer.js";
import { FaDepreciationRun } from "../fa-depreciation-run.js";
import { FaLease } from "../fa-lease.js";
import { FaMaintenanceRecord } from "../fa-maintenance.js";
import { FaPhysicalVerification } from "../fa-physical.js";
import {
  FaAssetType, FaAssetStatus, FaAcquisitionType, FaDepreciationMethod,
  FaDepreciationArea, FaDepreciationRunStatus, FaDisposalType,
  FaRevaluationType, FaImpairmentType, FaLeaseType,
  FaLeasePaymentFrequency, FaMaintenanceType,
  FaVerificationMethod, FaVerificationStatus,
} from "../fa-enums.js";

describe("FaAsset", () => {
  it("creates asset", () => {
    const asset = FaAsset.create({
      companyId: "comp1", assetCode: "TS001", assetName: "Test Asset",
      assetType: FaAssetType.Tangible,
      depreciationMethod: FaDepreciationMethod.StraightLine,
      usefulLifeYears: 10, usefulLifeMonths: 0,
    });
    expect(asset.assetCode).toBe("TS001");
    expect(asset.assetStatus).toBe(FaAssetStatus.Draft);
    expect(asset.assetType).toBe(FaAssetType.Tangible);
    expect(asset.originalCost).toBe(0);
  });

  it("serializes to state and loads back", () => {
    const asset = FaAsset.create({
      companyId: "comp1", assetCode: "TS001", assetName: "Test Asset",
      assetType: FaAssetType.Tangible,
      depreciationMethod: FaDepreciationMethod.StraightLine,
      usefulLifeYears: 10, usefulLifeMonths: 0,
      serialNumber: "SN12345", costCenterId: "cc1",
    });
    const state = asset.toState();
    const loaded = FaAsset.load(state);
    expect(loaded.assetCode).toBe("TS001");
    expect(loaded.serialNumber).toBe("SN12345");
    expect(loaded.costCenterId).toBe("cc1");
  });

  it("acquires asset", () => {
    const asset = FaAsset.create({
      companyId: "comp1", assetCode: "TS001", assetName: "Test Asset",
      assetType: FaAssetType.Tangible,
      depreciationMethod: FaDepreciationMethod.StraightLine,
      usefulLifeYears: 10, usefulLifeMonths: 0,
    });
    asset.acquire({
      acquisitionType: FaAcquisitionType.Purchase,
      acquisitionDate: new Date("2025-01-01"),
      originalCost: 100000000,
      supplierName: "ABC Corp",
    });
    expect(asset.assetStatus).toBe(FaAssetStatus.Acquired);
    expect(asset.originalCost).toBe(100000000);
    expect(asset.netBookValue).toBe(100000000);
  });

  it("capitalizes asset", () => {
    const asset = buildAcquiredAsset();
    asset.capitalize(new Date("2025-01-15"));
    expect(asset.assetStatus).toBe(FaAssetStatus.Capitalized);
    expect(asset.capitalizationDate).toBeTruthy();
  });

  it("puts asset in use", () => {
    const asset = buildCapitalizedAsset();
    asset.putInUse(new Date("2025-02-01"));
    expect(asset.assetStatus).toBe(FaAssetStatus.InUse);
    expect(asset.depreciationStartDate).toBeTruthy();
  });

  it("calculates straight-line depreciation", () => {
    const asset = buildInUseAsset();
    const depr = asset.calculateMonthlyDepreciation();
    // 100M / 120 months = ~833,333
    expect(depr).toBeGreaterThan(0);
    expect(depr).toBeLessThan(1000000);
  });

  it("applies depreciation", () => {
    const asset = buildInUseAsset();
    const beforeNbv = asset.netBookValue;
    asset.applyDepreciation(asset.calculateMonthlyDepreciation(), new Date());
    expect(asset.netBookValue).toBeLessThan(beforeNbv);
    expect(asset.accumulatedDepreciation).toBeGreaterThan(0);
  });

  it("marks fully depreciated", () => {
    const asset = buildInUseAsset();
    asset.markFullyDepreciated();
    expect(asset.isFullyDepreciated).toBe(true);
    expect(asset.assetStatus).toBe(FaAssetStatus.FullyDepreciated);
  });

  it("revalues asset upward", () => {
    const asset = buildInUseAsset();
    const oldNbv = asset.netBookValue;
    const newValue = oldNbv + 50000000;
    asset.revalue(FaRevaluationType.Upward, newValue, new Date("2025-06-01"));
    expect(asset.netBookValue).toBe(newValue);
    expect(asset.revaluationAmount).toBeGreaterThan(0);
    expect(asset.revaluationReserve).toBeGreaterThan(0);
  });

  it("records impairment", () => {
    const asset = buildInUseAsset();
    const impairmentLoss = 20000000;
    asset.impair(FaImpairmentType.External, impairmentLoss, new Date("2025-06-01"));
    expect(asset.impairmentAmount).toBe(impairmentLoss);
    expect(asset.netBookValue).toBe(100000000 - 20000000);
  });

  it("disposes asset", () => {
    const asset = buildInUseAsset();
    asset.dispose({
      disposalType: FaDisposalType.Sale, disposalDate: new Date("2025-12-01"),
      proceeds: 80000000, costs: 2000000,
    });
    expect(asset.assetStatus).toBe(FaAssetStatus.Sold);
    expect(asset.disposalDate).toBeTruthy();
  });

  it("transfers asset", () => {
    const asset = buildInUseAsset();
    asset.transfer({
      toBranchId: "branch2", toCostCenterId: "cc2", transferDate: new Date("2025-06-01"),
    });
    expect(asset.branchId).toBe("branch2");
    expect(asset.costCenterId).toBe("cc2");
  });

  it("writes off asset", () => {
    const asset = buildInUseAsset();
    asset.writeOff("Obsolete");
    expect(asset.assetStatus).toBe(FaAssetStatus.WrittenOff);
  });

  it("suspends and resumes asset", () => {
    const asset = buildInUseAsset();
    asset.suspend(new Date("2025-06-01"), new Date("2025-07-01"));
    expect(asset.assetStatus).toBe(FaAssetStatus.Suspended);
    expect(asset.isSuspended).toBe(true);
    asset.resume();
    expect(asset.assetStatus).toBe(FaAssetStatus.InUse);
    expect(asset.isSuspended).toBe(false);
  });

  it("reopens disposed asset", () => {
    const asset = buildInUseAsset();
    asset.writeOff("Obsolete");
    asset.reopen();
    expect(asset.assetStatus).toBe(FaAssetStatus.InUse);
    expect(asset.isFullyDepreciated).toBe(false);
  });

  it("rejects disposal before acquisition", () => {
    const asset = buildDraftAsset();
    expect(() => asset.dispose({
      disposalType: FaDisposalType.Sale, disposalDate: new Date("2025-01-01"),
      proceeds: 0, costs: 0,
    })).toThrow("Asset must be capitalized or in use");
  });

  it("rejects capitalization without acquisition", () => {
    const asset = buildDraftAsset();
    expect(() => asset.capitalize(new Date("2025-01-15"))).toThrow();
  });

  it("creates events on lifecycle", () => {
    const asset = buildAcquiredAsset();
    expect(asset.clearEvents().length).toBeGreaterThan(0);
  });
});

describe("FaCipProject", () => {
  it("creates CIP project", () => {
    const proj = FaCipProject.create({
      projectCode: "CIP001", projectName: "Factory Construction",
      companyId: "comp1", startDate: new Date("2025-01-01"),
      totalBudget: 1000000000,
    });
    expect(proj.projectCode).toBe("CIP001");
    expect(proj.totalBudget).toBe(1000000000);
  });

  it("adds cost and capitalizes", () => {
    const proj = FaCipProject.create({
      projectCode: "CIP001", projectName: "Test", companyId: "comp1",
      startDate: new Date("2025-01-01"), totalBudget: 500000000,
    });
    proj.addCost(200000000);
    expect(proj.totalCost).toBe(200000000);
    proj.capitalize(200000000, "asset123");
    expect(proj.capitalizedAmount).toBe(200000000);
  });

  it("serializes state", () => {
    const proj = FaCipProject.create({
      projectCode: "CIP001", projectName: "Test", companyId: "comp1",
      startDate: new Date("2025-01-01"),
    });
    const state = proj.toState();
    const loaded = FaCipProject.load(state);
    expect(loaded.projectCode).toBe("CIP001");
  });
});

describe("FaDisposal", () => {
  it("creates disposal with gain", () => {
    const d = FaDisposal.create({
      assetId: "asset1", disposalNumber: "TH001",
      disposalType: FaDisposalType.Sale, disposalDate: new Date("2025-12-01"),
      originalCost: 100000000, accumulatedDepreciation: 20000000,
      netBookValue: 80000000, disposalProceeds: 90000000, disposalCosts: 1000000,
    });
    expect(d.gainOnDisposal).toBe(9000000);
    expect(d.lossOnDisposal).toBe(0);
  });

  it("creates disposal with loss", () => {
    const d = FaDisposal.create({
      assetId: "asset1", disposalNumber: "TH002",
      disposalType: FaDisposalType.Scrap, disposalDate: new Date("2025-12-01"),
      originalCost: 100000000, accumulatedDepreciation: 20000000,
      netBookValue: 80000000, disposalProceeds: 50000000,
    });
    expect(d.lossOnDisposal).toBe(30000000);
    expect(d.gainOnDisposal).toBe(0);
  });

  it("serializes state", () => {
    const d = FaDisposal.create({
      assetId: "asset1", disposalNumber: "TH001",
      disposalType: FaDisposalType.Sale, disposalDate: new Date(),
      originalCost: 100000000, accumulatedDepreciation: 20000000,
      netBookValue: 80000000, disposalProceeds: 90000000,
    });
    const state = d.toState();
    const loaded = FaDisposal.load(state);
    expect(loaded.disposalNumber).toBe("TH001");
  });
});

describe("FaTransfer", () => {
  it("creates transfer", () => {
    const t = FaTransfer.create({
      assetId: "asset1", transferNumber: "DC001",
      transferDate: new Date("2025-06-01"),
      fromBranchId: "branch1", toBranchId: "branch2",
    });
    expect(t.transferNumber).toBe("DC001");
    expect(t.toBranchId).toBe("branch2");
  });

  it("serializes state", () => {
    const t = FaTransfer.create({
      assetId: "asset1", transferNumber: "DC001",
      transferDate: new Date("2025-06-01"),
    });
    const state = t.toState();
    const loaded = FaTransfer.load(state);
    expect(loaded.transferNumber).toBe("DC001");
  });
});

describe("FaDepreciationRun", () => {
  it("creates and processes depreciation run", () => {
    const run = FaDepreciationRun.create({
      runNumber: "KH01202506", depreciationArea: FaDepreciationArea.Book,
      periodId: "period1", fiscalYearId: "fy2025",
    });
    expect(run.status).toBe(FaDepreciationRunStatus.Pending);
    run.start();
    expect(run.status).toBe(FaDepreciationRunStatus.InProgress);
    run.setTotalAssets(10);
    run.complete(50000000);
    expect(run.status).toBe(FaDepreciationRunStatus.Completed);
    expect(run.totalDepreciation).toBe(50000000);
  });

  it("serializes state", () => {
    const run = FaDepreciationRun.create({
      runNumber: "KH001", depreciationArea: FaDepreciationArea.Tax,
      periodId: "p1", fiscalYearId: "fy1",
    });
    const state = run.toState();
    const loaded = FaDepreciationRun.load(state);
    expect(loaded.runNumber).toBe("KH001");
  });
});

describe("FaRevaluation", () => {
  it("creates revaluation record", () => {
    const r = FaRevaluation.create({
      assetId: "asset1", revaluationNumber: "DG001",
      revaluationType: FaRevaluationType.Upward,
      revaluationDate: new Date("2025-06-01"),
      previousValue: 80000000, revaluedAmount: 20000000, newValue: 100000000,
      accumulatedDepreciationBefore: 20000000,
      accumulatedDepreciationAfter: 20000000,
      revaluationReserve: 20000000,
    });
    expect(r.revaluationNumber).toBe("DG001");
    expect(r.revaluedAmount).toBe(20000000);
  });
});

describe("FaImpairment", () => {
  it("creates impairment record", () => {
    const i = FaImpairment.create({
      assetId: "asset1", impairmentNumber: "STT001",
      impairmentType: FaImpairmentType.External,
      impairmentDate: new Date("2025-06-01"),
      carryingAmount: 100000000, recoverableAmount: 70000000,
      impairmentLoss: 30000000,
    });
    expect(i.impairmentLoss).toBe(30000000);
  });
});

describe("FaLease", () => {
  it("creates finance lease", () => {
    const l = FaLease.create({
      leaseNumber: "LS001", leaseType: FaLeaseType.Finance,
      startDate: new Date("2025-01-01"), endDate: new Date("2027-12-31"),
      paymentAmount: 10000000, totalLeaseLiability: 300000000,
      interestRate: 8.5, lessorName: "Leasing Corp",
    });
    expect(l.leaseNumber).toBe("LS001");
    expect(l.totalLeaseLiability).toBe(300000000);
  });

  it("records payment", () => {
    const l = FaLease.create({
      leaseNumber: "LS001", leaseType: FaLeaseType.Finance,
      startDate: new Date("2025-01-01"), endDate: new Date("2027-12-31"),
      paymentAmount: 10000000, totalLeaseLiability: 300000000,
    });
    l.recordPayment(10000000, 2000000);
    expect(l.totalLeaseLiability).toBeLessThan(300000000);
  });

  it("rejects lease with end before start", () => {
    expect(() => FaLease.create({
      leaseNumber: "LS002", leaseType: FaLeaseType.Finance,
      startDate: new Date("2025-12-31"), endDate: new Date("2025-01-01"),
      paymentAmount: 10000000, totalLeaseLiability: 0,
    })).toThrow("Lease end must be after start");
  });
});

describe("FaMaintenanceRecord", () => {
  it("creates maintenance record", () => {
    const r = FaMaintenanceRecord.create({
      assetId: "asset1", recordNumber: "BT001",
      maintenanceType: FaMaintenanceType.Preventive,
      maintenanceDate: new Date("2025-03-15"),
      cost: 5000000,
    });
    expect(r.recordNumber).toBe("BT001");
    expect(r.cost).toBe(5000000);
  });

  it("completes maintenance", () => {
    const r = FaMaintenanceRecord.create({
      assetId: "asset1", recordNumber: "BT001",
      maintenanceType: FaMaintenanceType.Corrective,
      maintenanceDate: new Date("2025-03-15"),
      cost: 5000000,
    });
    r.complete(new Date("2025-03-16"), "Found worn part", "Replaced");
    expect(r.recordNumber).toBe("BT001");
  });
});

describe("FaPhysicalVerification", () => {
  it("creates verification", () => {
    const v = FaPhysicalVerification.create({
      verificationNumber: "KK001", companyId: "comp1",
      verificationDate: new Date("2025-06-30"),
      verificationMethod: FaVerificationMethod.Barcode,
    });
    expect(v.verificationNumber).toBe("KK001");
    expect(v.status).toBe(FaVerificationStatus.Planned);
  });

  it("completes verification", () => {
    const v = FaPhysicalVerification.create({
      verificationNumber: "KK001", companyId: "comp1",
      verificationDate: new Date("2025-06-30"),
    });
    v.setTotalAssets(10);
    v.recordVerification(true);
    v.recordVerification(false);
    v.recordMissing();
    v.complete();
    expect(v.status).toBe(FaVerificationStatus.Completed);
    expect(v.matchedAssets).toBe(1);
    expect(v.discrepancyAssets).toBe(1);
    expect(v.missingAssets).toBe(1);
  });

  it("approves verification", () => {
    const v = FaPhysicalVerification.create({
      verificationNumber: "KK001", companyId: "comp1",
      verificationDate: new Date("2025-06-30"),
    });
    v.approve("user1");
    expect(v.status).toBe(FaVerificationStatus.Approved);
  });
});

// ─── Helpers ───────────────────────────────────────────────────────────────────────

function buildDraftAsset(): FaAsset {
  return FaAsset.create({
    companyId: "comp1", assetCode: "TS001", assetName: "Test Asset",
    assetType: FaAssetType.Tangible,
    depreciationMethod: FaDepreciationMethod.StraightLine,
    usefulLifeYears: 10, usefulLifeMonths: 0,
  });
}

function buildAcquiredAsset(): FaAsset {
  const asset = buildDraftAsset();
  asset.acquire({
    acquisitionType: FaAcquisitionType.Purchase,
    acquisitionDate: new Date("2025-01-01"),
    originalCost: 100000000,
  });
  return asset;
}

function buildCapitalizedAsset(): FaAsset {
  const asset = buildAcquiredAsset();
  asset.capitalize(new Date("2025-01-15"));
  return asset;
}

function buildInUseAsset(): FaAsset {
  const asset = buildCapitalizedAsset();
  asset.putInUse(new Date("2025-02-01"));
  return asset;
}
