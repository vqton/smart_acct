import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  PrismaBgtBudgetPlanRepository,
  PrismaBgtBudgetVersionRepository,
  PrismaBgtBudgetDetailRepository,
  PrismaBgtAllocationRuleRepository,
  PrismaBgtBudgetControlRepository,
  PrismaBgtReservationRepository,
  PrismaBgtTransferRepository,
  PrismaBgtApprovalRepository,
  PrismaBgtSnapshotRepository,
} from "../../infrastructure/budget/budget-prisma-repos.js";
import { BgtBudgetPlan, type BgtBudgetPlanState } from "../../domain/budget/bgt-budget-plan.js";
import { BgtBudgetVersion, type BgtBudgetVersionState } from "../../domain/budget/bgt-budget-version.js";
import { BgtBudgetDetail, type BgtBudgetDetailState } from "../../domain/budget/bgt-budget-detail.js";
import { BgtBudgetPlanId, BgtBudgetDetailId } from "../../domain/budget/bgt-ids.js";
import { BgtBudgetStatus } from "../../domain/budget/bgt-enums.js";

export interface CreateBudgetPlanInput {
  code: string; name: string; budgetType: string; fiscalYearId: string;
  description?: string; currencyCode?: string; startDate?: Date; endDate?: Date;
  notes?: string; isTemplate?: boolean; parentId?: string; createdById?: string;
}

export interface CreateBudgetDetailInput {
  budgetPlanId: string; lineNumber: number; glAccountId?: string;
  costCenterId?: string; departmentId?: string; projectId?: string;
  productId?: string; customerId?: string; supplierId?: string;
  employeeId?: string; assetId?: string; locationId?: string;
  description?: string; originalAmount?: number;
}

export interface CreateBudgetVersionInput {
  budgetPlanId: string; versionNumber: number; label: string;
  description?: string; totalAmount?: number; createdById?: string;
  sourceVersionId?: string; notes?: string;
}

@Injectable()
export class BudgetEngineService {
  constructor(
    private readonly planRepo: PrismaBgtBudgetPlanRepository,
    private readonly versionRepo: PrismaBgtBudgetVersionRepository,
    private readonly detailRepo: PrismaBgtBudgetDetailRepository,
  ) {}

  // ─── Budget Plan ───────────────────────────────────────────────────────────

  async createPlan(p: CreateBudgetPlanInput): Promise<BgtBudgetPlan> {
    const existing = await this.planRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Budget code ${p.code} already exists`);
    const plan = BgtBudgetPlan.create(p);
    await this.planRepo.save(plan);
    return plan;
  }

  async getPlan(id: string): Promise<BgtBudgetPlan | null> {
    return this.planRepo.findById(BgtBudgetPlanId.from(id));
  }

  async listPlans(fiscalYearId?: string, status?: string, type?: string): Promise<BgtBudgetPlan[]> {
    if (fiscalYearId) return this.planRepo.findByFiscalYear(fiscalYearId);
    if (status) return this.planRepo.findByStatus(status);
    if (type) return this.planRepo.findByType(type);
    return this.planRepo.findAll();
  }

  async submitPlan(id: string, userId: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.submit(userId);
    await this.planRepo.save(plan);
    return plan;
  }

  async approvePlan(id: string, userId: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.approve(userId);
    await this.planRepo.save(plan);
    return plan;
  }

  async rejectPlan(id: string, userId: string, reason: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.reject(userId, reason);
    await this.planRepo.save(plan);
    return plan;
  }

  async reviewPlan(id: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.review();
    await this.planRepo.save(plan);
    return plan;
  }

  async revisePlan(id: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.revise();
    await this.planRepo.save(plan);
    return plan;
  }

  async publishPlan(id: string, userId: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.publish(userId);
    await this.planRepo.save(plan);
    return plan;
  }

  async activatePlan(id: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.activate();
    await this.planRepo.save(plan);
    return plan;
  }

  async freezePlan(id: string, userId: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.freeze(userId);
    await this.planRepo.save(plan);
    return plan;
  }

  async closePlan(id: string, userId: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.close(userId);
    await this.planRepo.save(plan);
    return plan;
  }

  async reopenPlan(id: string): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.reopen();
    await this.planRepo.save(plan);
    return plan;
  }

  async updatePlan(id: string, p: Partial<CreateBudgetPlanInput>): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.update(p);
    await this.planRepo.save(plan);
    return plan;
  }

  async adjustPlanAmount(id: string, amount: number): Promise<BgtBudgetPlan> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(id));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.adjustTotalPlanned(amount);
    await this.planRepo.save(plan);
    return plan;
  }

  // ─── Budget Version ───────────────────────────────────────────────────────

  async createVersion(p: CreateBudgetVersionInput): Promise<BgtBudgetVersion> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(p.budgetPlanId));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    const version = BgtBudgetVersion.create(p);
    await this.versionRepo.save(version);
    return version;
  }

  async approveVersion(id: string, userId: string): Promise<BgtBudgetVersion> {
    const version = await this.versionRepo.findById(id);
    if (!version) throw new DomainError("NotFound", "Budget version not found");
    version.approve(userId);
    await this.versionRepo.save(version);
    return version;
  }

  async freezeVersion(id: string): Promise<BgtBudgetVersion> {
    const version = await this.versionRepo.findById(id);
    if (!version) throw new DomainError("NotFound", "Budget version not found");
    version.freeze();
    await this.versionRepo.save(version);
    return version;
  }

  async getVersions(budgetPlanId: string): Promise<BgtBudgetVersion[]> {
    return this.versionRepo.findByBudgetPlan(budgetPlanId);
  }

  async cloneVersion(id: string, newVersionNumber: number, label: string, createdById?: string): Promise<BgtBudgetVersion> {
    const version = await this.versionRepo.findById(id);
    if (!version) throw new DomainError("NotFound", "Budget version not found");
    const cloned = version.clone(newVersionNumber, label, createdById);
    await this.versionRepo.save(cloned);
    const details = await this.detailRepo.findByBudgetPlan(version.budgetPlanId);
    for (const d of details) {
      const newDetail = BgtBudgetDetail.create({
        budgetPlanId: d.budgetPlanId, versionId: cloned.id.value,
        lineNumber: d.lineNumber, glAccountId: d.glAccountId ?? undefined,
        costCenterId: d.costCenterId ?? undefined,
        departmentId: d.departmentId ?? undefined,
        projectId: d.projectId ?? undefined,
        originalAmount: d.originalAmount, currentAmount: d.currentAmount,
        description: d.description ?? undefined,
      });
      await this.detailRepo.save(newDetail);
    }
    return cloned;
  }

  // ─── Budget Detail ────────────────────────────────────────────────────────

  async createDetail(p: CreateBudgetDetailInput): Promise<BgtBudgetDetail> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(p.budgetPlanId));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    const detail = BgtBudgetDetail.create(p);
    const total = detail.totalPeriodAmount > 0 ? detail.totalPeriodAmount : (p.originalAmount ?? 0);
    if (total > 0) {
      plan.adjustTotalPlanned(plan.totalPlannedAmount + total);
      await this.planRepo.save(plan);
    }
    await this.detailRepo.save(detail);
    return detail;
  }

  async getDetail(id: string): Promise<BgtBudgetDetail | null> {
    return this.detailRepo.findById(id);
  }

  async getDetails(budgetPlanId: string): Promise<BgtBudgetDetail[]> {
    return this.detailRepo.findByBudgetPlan(budgetPlanId);
  }

  async updateDetailAmount(id: string, amount: number): Promise<BgtBudgetDetail> {
    const detail = await this.detailRepo.findById(id);
    if (!detail) throw new DomainError("NotFound", "Budget detail not found");
    const oldTotal = detail.currentAmount;
    detail.updateAmount(amount);
    await this.detailRepo.save(detail);
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(detail.budgetPlanId));
    if (plan) {
      plan.adjustTotalPlanned(plan.totalPlannedAmount + (amount - oldTotal));
      await this.planRepo.save(plan);
    }
    return detail;
  }

  async setDetailPeriod(id: string, period: number, amount: number): Promise<BgtBudgetDetail> {
    const detail = await this.detailRepo.findById(id);
    if (!detail) throw new DomainError("NotFound", "Budget detail not found");
    const oldTotal = detail.currentAmount;
    detail.setPeriodAmount(period, amount);
    await this.detailRepo.save(detail);
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(detail.budgetPlanId));
    if (plan) {
      plan.adjustTotalPlanned(plan.totalPlannedAmount + (detail.currentAmount - oldTotal));
      await this.planRepo.save(plan);
    }
    return detail;
  }

  async deleteDetail(id: string): Promise<void> {
    const detail = await this.detailRepo.findById(id);
    if (!detail) throw new DomainError("NotFound", "Budget detail not found");
    await this.detailRepo.delete(id);
  }

  async recordConsumption(budgetPlanId: string, glAccountId: string, amount: number, periodNumber?: number): Promise<void> {
    const plan = await this.planRepo.findById(BgtBudgetPlanId.from(budgetPlanId));
    if (!plan) throw new DomainError("NotFound", "Budget plan not found");
    plan.recordConsumption(amount);
    await this.planRepo.save(plan);
    const details = await this.detailRepo.findByBudgetPlanAndAccount(budgetPlanId, glAccountId);
    for (const detail of details) {
      detail.recordConsumption(amount, periodNumber);
      await this.detailRepo.save(detail);
    }
  }
}
