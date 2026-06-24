import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  BgtBudgetPlanId, BgtBudgetVersionId, BgtBudgetDetailId,
  BgtScenarioId, BgtForecastHeaderId, BgtAllocationRuleId,
  BgtAllocationResultId, BgtBudgetControlId, BgtReservationId,
  BgtTransferId, BgtApprovalRequestId, BgtSnapshotId,
} from "../../domain/budget/bgt-ids.js";
import { BgtBudgetPlan, type BgtBudgetPlanState } from "../../domain/budget/bgt-budget-plan.js";
import { BgtBudgetVersion, type BgtBudgetVersionState } from "../../domain/budget/bgt-budget-version.js";
import { BgtBudgetDetail, type BgtBudgetDetailState } from "../../domain/budget/bgt-budget-detail.js";
import { BgtBudgetScenario, type BgtBudgetScenarioState } from "../../domain/budget/bgt-budget-scenario.js";
import { BgtForecastHeader, type BgtForecastHeaderState } from "../../domain/budget/bgt-forecast.js";
import { BgtAllocationRule, type BgtAllocationRuleState } from "../../domain/budget/bgt-allocation.js";
import { BgtAllocationResult, type BgtAllocationResultState } from "../../domain/budget/bgt-allocation.js";
import { BgtBudgetControl, type BgtBudgetControlState } from "../../domain/budget/bgt-budget-control.js";
import { BgtBudgetReservation, type BgtBudgetReservationState } from "../../domain/budget/bgt-reservation.js";
import { BgtBudgetTransfer, type BgtBudgetTransferState } from "../../domain/budget/bgt-transfer.js";
import { BgtApprovalRequest, type BgtApprovalRequestState } from "../../domain/budget/bgt-approval.js";
import { BgtBudgetSnapshot, type BgtBudgetSnapshotState } from "../../domain/budget/bgt-snapshot.js";
import type {
  BgtBudgetPlanRepository, BgtBudgetVersionRepository, BgtBudgetDetailRepository,
  BgtScenarioRepository, BgtForecastRepository, BgtAllocationRuleRepository,
  BgtAllocationResultRepository, BgtBudgetControlRepository, BgtReservationRepository,
  BgtTransferRepository, BgtApprovalRepository, BgtSnapshotRepository,
} from "../../domain/budget/bgt-repositories.js";

function toNumber(val: unknown, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  if (typeof val === "number") return val;
  if (typeof val === "object" && "toString" in (val as object)) return parseFloat((val as any).toString());
  return fallback;
}

// ─── Budget Plan Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaBgtBudgetPlanRepository implements BgtBudgetPlanRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(plan: BgtBudgetPlan): Promise<void> {
    const s = plan.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    data.totalPlannedAmount = toNumber(data.totalPlannedAmount);
    data.totalApprovedAmount = toNumber(data.totalApprovedAmount);
    data.totalRemainingAmount = toNumber(data.totalRemainingAmount);
    data.totalReservedAmount = toNumber(data.totalReservedAmount);
    data.totalConsumedAmount = toNumber(data.totalConsumedAmount);
    await this.prisma.bgtBudgetPlan.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: BgtBudgetPlanId): Promise<BgtBudgetPlan | null> {
    const row = await this.prisma.bgtBudgetPlan.findUnique({ where: { id: id.value } });
    return row ? BgtBudgetPlan.load(row as any) : null;
  }

  async findByCode(code: string): Promise<BgtBudgetPlan | null> {
    const row = await this.prisma.bgtBudgetPlan.findUnique({ where: { code } });
    return row ? BgtBudgetPlan.load(row as any) : null;
  }

  async findAll(): Promise<BgtBudgetPlan[]> {
    return (await this.prisma.bgtBudgetPlan.findMany({ orderBy: { code: "asc" } })).map(r => BgtBudgetPlan.load(r as any));
  }

  async findByFiscalYear(fiscalYearId: string): Promise<BgtBudgetPlan[]> {
    return (await this.prisma.bgtBudgetPlan.findMany({ where: { fiscalYearId }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetPlan.load(r as any));
  }

  async findByStatus(status: string): Promise<BgtBudgetPlan[]> {
    return (await this.prisma.bgtBudgetPlan.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetPlan.load(r as any));
  }

  async findByType(budgetType: string): Promise<BgtBudgetPlan[]> {
    return (await this.prisma.bgtBudgetPlan.findMany({ where: { budgetType: budgetType as any }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetPlan.load(r as any));
  }

  async delete(id: BgtBudgetPlanId): Promise<void> {
    await this.prisma.bgtBudgetPlan.delete({ where: { id: id.value } }).catch(() => {});
  }
}

// ─── Budget Version Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaBgtBudgetVersionRepository implements BgtBudgetVersionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(version: BgtBudgetVersion): Promise<void> {
    const s = version.toState();
    const data: any = { ...s };
    delete data.createdAt;
    data.totalAmount = toNumber(data.totalAmount);
    await this.prisma.bgtBudgetVersion.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtBudgetVersion | null> {
    const row = await this.prisma.bgtBudgetVersion.findUnique({ where: { id } });
    return row ? BgtBudgetVersion.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion[]> {
    return (await this.prisma.bgtBudgetVersion.findMany({ where: { budgetPlanId }, orderBy: { versionNumber: "desc" } })).map(r => BgtBudgetVersion.load(r as any));
  }

  async findCurrentByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion | null> {
    const row = await this.prisma.bgtBudgetVersion.findFirst({ where: { budgetPlanId, isCurrent: true } });
    return row ? BgtBudgetVersion.load(row as any) : null;
  }

  async findApprovedByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion | null> {
    const row = await this.prisma.bgtBudgetVersion.findFirst({ where: { budgetPlanId, isApproved: true }, orderBy: { versionNumber: "desc" } });
    return row ? BgtBudgetVersion.load(row as any) : null;
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetVersion.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Budget Detail Repository ─────────────────────────────────────────────────

@Injectable()
export class PrismaBgtBudgetDetailRepository implements BgtBudgetDetailRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(detail: BgtBudgetDetail): Promise<void> {
    const s = detail.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    for (const key of ["originalAmount", "currentAmount", "approvedAmount", "reservedAmount",
      "consumedAmount", "remainingAmount", "committedAmount", "encumberedAmount", "availableAmount",
      "period1", "period2", "period3", "period4", "period5", "period6", "period7", "period8",
      "period9", "period10", "period11", "period12", "period13", "period14", "period15", "period16",
      "period17", "period18", "period19", "period20", "period21", "period22", "period23", "period24",
      "customPeriod1", "customPeriod2", "customPeriod3", "customPeriod4", "customPeriod5", "customPeriod6"]) {
      (data as any)[key] = toNumber((data as any)[key]);
    }
    await this.prisma.bgtBudgetDetail.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async saveMany(details: BgtBudgetDetail[]): Promise<void> {
    for (const d of details) await this.save(d);
  }

  async findById(id: string): Promise<BgtBudgetDetail | null> {
    const row = await this.prisma.bgtBudgetDetail.findUnique({ where: { id } });
    return row ? BgtBudgetDetail.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetDetail[]> {
    return (await this.prisma.bgtBudgetDetail.findMany({ where: { budgetPlanId, isActive: true }, orderBy: { lineNumber: "asc" } })).map(r => BgtBudgetDetail.load(r as any));
  }

  async findByBudgetPlanAndAccount(budgetPlanId: string, glAccountId: string): Promise<BgtBudgetDetail[]> {
    return (await this.prisma.bgtBudgetDetail.findMany({ where: { budgetPlanId, glAccountId, isActive: true } })).map(r => BgtBudgetDetail.load(r as any));
  }

  async findByBudgetPlanAndCostCenter(budgetPlanId: string, costCenterId: string): Promise<BgtBudgetDetail[]> {
    return (await this.prisma.bgtBudgetDetail.findMany({ where: { budgetPlanId, costCenterId, isActive: true } })).map(r => BgtBudgetDetail.load(r as any));
  }

  async findByBudgetPlanAndProject(budgetPlanId: string, projectId: string): Promise<BgtBudgetDetail[]> {
    return (await this.prisma.bgtBudgetDetail.findMany({ where: { budgetPlanId, projectId, isActive: true } })).map(r => BgtBudgetDetail.load(r as any));
  }

  async findByBudgetPlanAndDepartment(budgetPlanId: string, departmentId: string): Promise<BgtBudgetDetail[]> {
    return (await this.prisma.bgtBudgetDetail.findMany({ where: { budgetPlanId, departmentId, isActive: true } })).map(r => BgtBudgetDetail.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetDetail.delete({ where: { id } }).catch(() => {});
  }

  async updateAmounts(id: string, state: Partial<BgtBudgetDetailState>): Promise<void> {
    const data: any = { ...state };
    delete data.id;
    await this.prisma.bgtBudgetDetail.update({ where: { id }, data }).catch(() => {});
  }
}

// ─── Scenario Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBgtScenarioRepository implements BgtScenarioRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(scenario: BgtBudgetScenario): Promise<void> {
    const s = scenario.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    await this.prisma.bgtBudgetScenario.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtBudgetScenario | null> {
    const row = await this.prisma.bgtBudgetScenario.findUnique({ where: { id } });
    return row ? BgtBudgetScenario.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetScenario[]> {
    return (await this.prisma.bgtBudgetScenario.findMany({ where: { budgetPlanId } })).map(r => BgtBudgetScenario.load(r as any));
  }

  async findBaseByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetScenario | null> {
    const row = await this.prisma.bgtBudgetScenario.findFirst({ where: { budgetPlanId, isBase: true } });
    return row ? BgtBudgetScenario.load(row as any) : null;
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetScenario.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Forecast Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBgtForecastRepository implements BgtForecastRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(forecast: BgtForecastHeader): Promise<void> {
    const s = forecast.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    data.totalForecastAmount = toNumber(data.totalForecastAmount);
    await this.prisma.bgtForecastHeader.upsert({ where: { id: data.id }, create: data, update: data });
    for (const line of forecast.lines) {
      const ls = line.toState();
      const ld: any = { ...ls };
      ld.forecastAmount = toNumber(ld.forecastAmount);
      ld.actualAmount = toNumber(ld.actualAmount);
      ld.varianceAmount = toNumber(ld.varianceAmount);
      await this.prisma.bgtForecastLine.upsert({ where: { id: ld.id }, create: ld, update: ld });
    }
  }

  async findById(id: string): Promise<BgtForecastHeader | null> {
    const row = await this.prisma.bgtForecastHeader.findUnique({
      where: { id },
      include: { forecastLines: true },
    });
    if (!row) return null;
    const header = BgtForecastHeader.load(row as any);
    return header;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtForecastHeader[]> {
    return (await this.prisma.bgtForecastHeader.findMany({ where: { budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtForecastHeader.load(r as any));
  }

  async findByNumber(forecastNumber: string): Promise<BgtForecastHeader | null> {
    const row = await this.prisma.bgtForecastHeader.findUnique({ where: { forecastNumber } });
    return row ? BgtForecastHeader.load(row as any) : null;
  }

  async findByStatus(status: string): Promise<BgtForecastHeader[]> {
    return (await this.prisma.bgtForecastHeader.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtForecastHeader.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtForecastHeader.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Allocation Rule Repository ───────────────────────────────────────────────

@Injectable()
export class PrismaBgtAllocationRuleRepository implements BgtAllocationRuleRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rule: BgtAllocationRule): Promise<void> {
    const s = rule.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    data.totalAmount = toNumber(data.totalAmount);
    data.allocatedAmount = toNumber(data.allocatedAmount);
    data.remainingAmount = toNumber(data.remainingAmount);
    await this.prisma.bgtAllocationRule.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtAllocationRule | null> {
    const row = await this.prisma.bgtAllocationRule.findUnique({ where: { id } });
    return row ? BgtAllocationRule.load(row as any) : null;
  }

  async findByCode(code: string): Promise<BgtAllocationRule | null> {
    const row = await this.prisma.bgtAllocationRule.findUnique({ where: { code } });
    return row ? BgtAllocationRule.load(row as any) : null;
  }

  async findAll(): Promise<BgtAllocationRule[]> {
    return (await this.prisma.bgtAllocationRule.findMany({ orderBy: { code: "asc" } })).map(r => BgtAllocationRule.load(r as any));
  }

  async findByStatus(status: string): Promise<BgtAllocationRule[]> {
    return (await this.prisma.bgtAllocationRule.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtAllocationRule.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtAllocationRule.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Allocation Result Repository ─────────────────────────────────────────────

@Injectable()
export class PrismaBgtAllocationResultRepository implements BgtAllocationResultRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(result: BgtAllocationResult): Promise<void> {
    const s = result.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    data.sourceAmount = toNumber(data.sourceAmount);
    data.allocatedAmount = toNumber(data.allocatedAmount);
    await this.prisma.bgtAllocationResult.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtAllocationResult | null> {
    const row = await this.prisma.bgtAllocationResult.findUnique({ where: { id } });
    return row ? BgtAllocationResult.load(row as any) : null;
  }

  async findByRule(ruleId: string): Promise<BgtAllocationResult[]> {
    return (await this.prisma.bgtAllocationResult.findMany({ where: { ruleId }, orderBy: { createdAt: "desc" } })).map(r => BgtAllocationResult.load(r as any));
  }

  async findByRunNumber(runNumber: string): Promise<BgtAllocationResult[]> {
    return (await this.prisma.bgtAllocationResult.findMany({ where: { runNumber } })).map(r => BgtAllocationResult.load(r as any));
  }
}

// ─── Budget Control Repository ────────────────────────────────────────────────

@Injectable()
export class PrismaBgtBudgetControlRepository implements BgtBudgetControlRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(control: BgtBudgetControl): Promise<void> {
    const s = control.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    await this.prisma.bgtBudgetControl.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtBudgetControl | null> {
    const row = await this.prisma.bgtBudgetControl.findUnique({ where: { id } });
    return row ? BgtBudgetControl.load(row as any) : null;
  }

  async findByBudgetDetail(budgetDetailId: string): Promise<BgtBudgetControl[]> {
    return (await this.prisma.bgtBudgetControl.findMany({ where: { budgetDetailId } })).map(r => BgtBudgetControl.load(r as any));
  }

  async findActiveByBudgetDetail(budgetDetailId: string): Promise<BgtBudgetControl[]> {
    return (await this.prisma.bgtBudgetControl.findMany({ where: { budgetDetailId, isActive: true } })).map(r => BgtBudgetControl.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetControl.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Reservation Repository ───────────────────────────────────────────────────

@Injectable()
export class PrismaBgtReservationRepository implements BgtReservationRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(reservation: BgtBudgetReservation): Promise<void> {
    const s = reservation.toState();
    const data: any = { ...s };
    data.totalAmount = toNumber(data.totalAmount);
    data.consumedAmount = toNumber(data.consumedAmount);
    data.releasedAmount = toNumber(data.releasedAmount);
    data.remainingAmount = toNumber(data.remainingAmount);
    await this.prisma.bgtBudgetReservation.upsert({ where: { id: data.id }, create: data, update: data });
    for (const line of reservation.lines) {
      const ls = line.toState();
      const ld: any = { ...ls };
      ld.amount = toNumber(ld.amount);
      ld.consumedAmount = toNumber(ld.consumedAmount);
      ld.releasedAmount = toNumber(ld.releasedAmount);
      ld.remainingAmount = toNumber(ld.remainingAmount);
      await this.prisma.bgtBudgetReservationLine.upsert({ where: { id: ld.id }, create: ld, update: ld });
    }
  }

  async findById(id: string): Promise<BgtBudgetReservation | null> {
    const row = await this.prisma.bgtBudgetReservation.findUnique({ where: { id } });
    return row ? BgtBudgetReservation.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetReservation[]> {
    return (await this.prisma.bgtBudgetReservation.findMany({ where: { budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetReservation.load(r as any));
  }

  async findByNumber(reservationNumber: string): Promise<BgtBudgetReservation | null> {
    const row = await this.prisma.bgtBudgetReservation.findUnique({ where: { reservationNumber } });
    return row ? BgtBudgetReservation.load(row as any) : null;
  }

  async findByStatus(status: string): Promise<BgtBudgetReservation[]> {
    return (await this.prisma.bgtBudgetReservation.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetReservation.load(r as any));
  }

  async findBySourceDocument(sourceDocumentType: string, sourceDocumentId: string): Promise<BgtBudgetReservation[]> {
    return (await this.prisma.bgtBudgetReservation.findMany({ where: { sourceDocumentType, sourceDocumentId } })).map(r => BgtBudgetReservation.load(r as any));
  }

  async findActive(): Promise<BgtBudgetReservation[]> {
    return (await this.prisma.bgtBudgetReservation.findMany({ where: { status: { in: ["active", "partially_consumed"] } } })).map(r => BgtBudgetReservation.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetReservation.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Transfer Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBgtTransferRepository implements BgtTransferRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(transfer: BgtBudgetTransfer): Promise<void> {
    const s = transfer.toState();
    const data: any = { ...s };
    data.totalAmount = toNumber(data.totalAmount);
    await this.prisma.bgtBudgetTransfer.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtBudgetTransfer | null> {
    const row = await this.prisma.bgtBudgetTransfer.findUnique({ where: { id } });
    return row ? BgtBudgetTransfer.load(row as any) : null;
  }

  async findByNumber(transferNumber: string): Promise<BgtBudgetTransfer | null> {
    const row = await this.prisma.bgtBudgetTransfer.findUnique({ where: { transferNumber } });
    return row ? BgtBudgetTransfer.load(row as any) : null;
  }

  async findBySourceBudgetPlan(budgetPlanId: string): Promise<BgtBudgetTransfer[]> {
    return (await this.prisma.bgtBudgetTransfer.findMany({ where: { sourceBudgetPlanId: budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetTransfer.load(r as any));
  }

  async findByTargetBudgetPlan(budgetPlanId: string): Promise<BgtBudgetTransfer[]> {
    return (await this.prisma.bgtBudgetTransfer.findMany({ where: { targetBudgetPlanId: budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetTransfer.load(r as any));
  }

  async findByStatus(status: string): Promise<BgtBudgetTransfer[]> {
    return (await this.prisma.bgtBudgetTransfer.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetTransfer.load(r as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetTransfer.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Approval Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBgtApprovalRepository implements BgtApprovalRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(request: BgtApprovalRequest): Promise<void> {
    const s = request.toState();
    const data: any = { ...s };
    data.totalAmount = toNumber(data.totalAmount);
    await this.prisma.bgtApprovalRequest.upsert({ where: { id: data.id }, create: data, update: data });
    for (const step of request.steps) {
      const ss = step.toState();
      const sd: any = { ...ss };
      await this.prisma.bgtApprovalStep.upsert({ where: { id: sd.id }, create: sd, update: sd });
    }
  }

  async findById(id: string): Promise<BgtApprovalRequest | null> {
    const row = await this.prisma.bgtApprovalRequest.findUnique({ where: { id } });
    return row ? BgtApprovalRequest.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtApprovalRequest[]> {
    return (await this.prisma.bgtApprovalRequest.findMany({ where: { budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtApprovalRequest.load(r as any));
  }

  async findByNumber(requestNumber: string): Promise<BgtApprovalRequest | null> {
    const row = await this.prisma.bgtApprovalRequest.findUnique({ where: { requestNumber } });
    return row ? BgtApprovalRequest.load(row as any) : null;
  }

  async findByStatus(status: string): Promise<BgtApprovalRequest[]> {
    return (await this.prisma.bgtApprovalRequest.findMany({ where: { status: status as any }, orderBy: { createdAt: "desc" } })).map(r => BgtApprovalRequest.load(r as any));
  }

  async findByApprover(approverId: string): Promise<BgtApprovalRequest[]> {
    return (await this.prisma.bgtApprovalStep.findMany({
      where: { approverId, status: "pending" },
      include: { approvalRequest: true },
      orderBy: { createdAt: "desc" },
    })).map(r => BgtApprovalRequest.load(r.approvalRequest as any));
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtApprovalRequest.delete({ where: { id } }).catch(() => {});
  }
}

// ─── Snapshot Repository ──────────────────────────────────────────────────────

@Injectable()
export class PrismaBgtSnapshotRepository implements BgtSnapshotRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(snapshot: BgtBudgetSnapshot): Promise<void> {
    const s = snapshot.toState();
    const data: any = { ...s };
    delete data.createdAt; delete data.updatedAt;
    data.totalAmount = toNumber(data.totalAmount);
    await this.prisma.bgtBudgetSnapshot.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: string): Promise<BgtBudgetSnapshot | null> {
    const row = await this.prisma.bgtBudgetSnapshot.findUnique({ where: { id } });
    return row ? BgtBudgetSnapshot.load(row as any) : null;
  }

  async findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetSnapshot[]> {
    return (await this.prisma.bgtBudgetSnapshot.findMany({ where: { budgetPlanId }, orderBy: { createdAt: "desc" } })).map(r => BgtBudgetSnapshot.load(r as any));
  }

  async findByNumber(snapshotNumber: string): Promise<BgtBudgetSnapshot | null> {
    const row = await this.prisma.bgtBudgetSnapshot.findUnique({ where: { snapshotNumber } });
    return row ? BgtBudgetSnapshot.load(row as any) : null;
  }

  async delete(id: string): Promise<void> {
    await this.prisma.bgtBudgetSnapshot.delete({ where: { id } }).catch(() => {});
  }
}
