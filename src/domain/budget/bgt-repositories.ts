import type { BgtBudgetPlan } from "./bgt-budget-plan.js";
import type { BgtBudgetPlanId } from "./bgt-ids.js";
import type { BgtBudgetVersion } from "./bgt-budget-version.js";
import type { BgtBudgetDetail, BgtBudgetDetailState } from "./bgt-budget-detail.js";
import type { BgtBudgetScenario } from "./bgt-budget-scenario.js";
import type { BgtForecastHeader } from "./bgt-forecast.js";
import type { BgtAllocationRule } from "./bgt-allocation.js";
import type { BgtAllocationResult } from "./bgt-allocation.js";
import type { BgtBudgetControl } from "./bgt-budget-control.js";
import type { BgtBudgetReservation } from "./bgt-reservation.js";
import type { BgtBudgetTransfer } from "./bgt-transfer.js";
import type { BgtApprovalRequest } from "./bgt-approval.js";
import type { BgtBudgetSnapshot } from "./bgt-snapshot.js";

// ─── Budget Plan Repository ───────────────────────────────────────────────────

export interface BgtBudgetPlanRepository {
  findById(id: BgtBudgetPlanId): Promise<BgtBudgetPlan | null>;
  findByCode(code: string): Promise<BgtBudgetPlan | null>;
  findAll(): Promise<BgtBudgetPlan[]>;
  findByFiscalYear(fiscalYearId: string): Promise<BgtBudgetPlan[]>;
  findByStatus(status: string): Promise<BgtBudgetPlan[]>;
  findByType(budgetType: string): Promise<BgtBudgetPlan[]>;
  save(plan: BgtBudgetPlan): Promise<void>;
  delete(id: BgtBudgetPlanId): Promise<void>;
}

// ─── Budget Version Repository ────────────────────────────────────────────────

export interface BgtBudgetVersionRepository {
  findById(id: string): Promise<BgtBudgetVersion | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion[]>;
  findCurrentByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion | null>;
  findApprovedByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetVersion | null>;
  save(version: BgtBudgetVersion): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Budget Detail Repository ─────────────────────────────────────────────────

export interface BgtBudgetDetailRepository {
  findById(id: string): Promise<BgtBudgetDetail | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetDetail[]>;
  findByBudgetPlanAndAccount(budgetPlanId: string, glAccountId: string): Promise<BgtBudgetDetail[]>;
  findByBudgetPlanAndCostCenter(budgetPlanId: string, costCenterId: string): Promise<BgtBudgetDetail[]>;
  findByBudgetPlanAndProject(budgetPlanId: string, projectId: string): Promise<BgtBudgetDetail[]>;
  findByBudgetPlanAndDepartment(budgetPlanId: string, departmentId: string): Promise<BgtBudgetDetail[]>;
  save(detail: BgtBudgetDetail): Promise<void>;
  saveMany(details: BgtBudgetDetail[]): Promise<void>;
  delete(id: string): Promise<void>;
  updateAmounts(id: string, state: Partial<BgtBudgetDetailState>): Promise<void>;
}

// ─── Scenario Repository ──────────────────────────────────────────────────────

export interface BgtScenarioRepository {
  findById(id: string): Promise<BgtBudgetScenario | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetScenario[]>;
  findBaseByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetScenario | null>;
  save(scenario: BgtBudgetScenario): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Forecast Repository ──────────────────────────────────────────────────────

export interface BgtForecastRepository {
  findById(id: string): Promise<BgtForecastHeader | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtForecastHeader[]>;
  findByNumber(forecastNumber: string): Promise<BgtForecastHeader | null>;
  findByStatus(status: string): Promise<BgtForecastHeader[]>;
  save(forecast: BgtForecastHeader): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Allocation Repository ────────────────────────────────────────────────────

export interface BgtAllocationRuleRepository {
  findById(id: string): Promise<BgtAllocationRule | null>;
  findByCode(code: string): Promise<BgtAllocationRule | null>;
  findAll(): Promise<BgtAllocationRule[]>;
  findByStatus(status: string): Promise<BgtAllocationRule[]>;
  save(rule: BgtAllocationRule): Promise<void>;
  delete(id: string): Promise<void>;
}

export interface BgtAllocationResultRepository {
  findById(id: string): Promise<BgtAllocationResult | null>;
  findByRule(ruleId: string): Promise<BgtAllocationResult[]>;
  findByRunNumber(runNumber: string): Promise<BgtAllocationResult[]>;
  save(result: BgtAllocationResult): Promise<void>;
}

// ─── Budget Control Repository ────────────────────────────────────────────────

export interface BgtBudgetControlRepository {
  findById(id: string): Promise<BgtBudgetControl | null>;
  findByBudgetDetail(budgetDetailId: string): Promise<BgtBudgetControl[]>;
  findActiveByBudgetDetail(budgetDetailId: string): Promise<BgtBudgetControl[]>;
  save(control: BgtBudgetControl): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Reservation Repository ───────────────────────────────────────────────────

export interface BgtReservationRepository {
  findById(id: string): Promise<BgtBudgetReservation | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetReservation[]>;
  findByNumber(reservationNumber: string): Promise<BgtBudgetReservation | null>;
  findByStatus(status: string): Promise<BgtBudgetReservation[]>;
  findBySourceDocument(sourceDocumentType: string, sourceDocumentId: string): Promise<BgtBudgetReservation[]>;
  findActive(): Promise<BgtBudgetReservation[]>;
  save(reservation: BgtBudgetReservation): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Transfer Repository ──────────────────────────────────────────────────────

export interface BgtTransferRepository {
  findById(id: string): Promise<BgtBudgetTransfer | null>;
  findByNumber(transferNumber: string): Promise<BgtBudgetTransfer | null>;
  findBySourceBudgetPlan(budgetPlanId: string): Promise<BgtBudgetTransfer[]>;
  findByTargetBudgetPlan(budgetPlanId: string): Promise<BgtBudgetTransfer[]>;
  findByStatus(status: string): Promise<BgtBudgetTransfer[]>;
  save(transfer: BgtBudgetTransfer): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Approval Repository ──────────────────────────────────────────────────────

export interface BgtApprovalRepository {
  findById(id: string): Promise<BgtApprovalRequest | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtApprovalRequest[]>;
  findByNumber(requestNumber: string): Promise<BgtApprovalRequest | null>;
  findByStatus(status: string): Promise<BgtApprovalRequest[]>;
  findByApprover(approverId: string): Promise<BgtApprovalRequest[]>;
  save(request: BgtApprovalRequest): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Snapshot Repository ──────────────────────────────────────────────────────

export interface BgtSnapshotRepository {
  findById(id: string): Promise<BgtBudgetSnapshot | null>;
  findByBudgetPlan(budgetPlanId: string): Promise<BgtBudgetSnapshot[]>;
  findByNumber(snapshotNumber: string): Promise<BgtBudgetSnapshot | null>;
  save(snapshot: BgtBudgetSnapshot): Promise<void>;
  delete(id: string): Promise<void>;
}

// ─── Composite Repository ─────────────────────────────────────────────────────

export interface BgtUnitOfWork {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
}

export interface BgtRepositoryProvider {
  plans: BgtBudgetPlanRepository;
  versions: BgtBudgetVersionRepository;
  details: BgtBudgetDetailRepository;
  scenarios: BgtScenarioRepository;
  forecasts: BgtForecastRepository;
  allocationRules: BgtAllocationRuleRepository;
  allocationResults: BgtAllocationResultRepository;
  controls: BgtBudgetControlRepository;
  reservations: BgtReservationRepository;
  transfers: BgtTransferRepository;
  approvals: BgtApprovalRepository;
  snapshots: BgtSnapshotRepository;
  uow: BgtUnitOfWork;
}
