import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  PrismaBgtApprovalRepository,
  PrismaBgtBudgetPlanRepository,
  PrismaBgtBudgetDetailRepository,
} from "../../infrastructure/budget/budget-prisma-repos.js";
import { BgtApprovalRequest, BgtApprovalStep } from "../../domain/budget/bgt-approval.js";

export interface CreateApprovalRequestInput {
  budgetPlanId: string; requestNumber: string; totalAmount: number;
  description?: string; requestedById?: string; notes?: string;
}

export interface CreateApprovalStepInput {
  approvalRequestId: string; stepOrder: number; approverId: string;
  delegateId?: string; slaDeadline?: Date; escalationAt?: Date;
}

@Injectable()
export class ApprovalEngineService {
  constructor(
    private readonly approvalRepo: PrismaBgtApprovalRepository,
    private readonly planRepo: PrismaBgtBudgetPlanRepository,
  ) {}

  async createRequest(p: CreateApprovalRequestInput): Promise<BgtApprovalRequest> {
    const existing = await this.approvalRepo.findByNumber(p.requestNumber);
    if (existing) throw new DomainError("Conflict", `Approval request ${p.requestNumber} already exists`);
    const request = BgtApprovalRequest.create(p);
    await this.approvalRepo.save(request);
    return request;
  }

  async getRequest(id: string): Promise<BgtApprovalRequest | null> {
    return this.approvalRepo.findById(id);
  }

  async listRequests(budgetPlanId?: string, status?: string): Promise<BgtApprovalRequest[]> {
    if (status) return this.approvalRepo.findByStatus(status);
    if (budgetPlanId) return this.approvalRepo.findByBudgetPlan(budgetPlanId);
    return this.approvalRepo.findByStatus("pending");
  }

  async getPendingForApprover(approverId: string): Promise<BgtApprovalRequest[]> {
    return this.approvalRepo.findByApprover(approverId);
  }

  async addStep(requestId: string, p: CreateApprovalStepInput): Promise<BgtApprovalRequest> {
    const request = await this.approvalRepo.findById(requestId);
    if (!request) throw new DomainError("NotFound", "Approval request not found");
    const step = BgtApprovalStep.create({ ...p, approvalRequestId: requestId });
    request.addStep(step);
    await this.approvalRepo.save(request);
    return request;
  }

  async processStep(requestId: string, stepOrder: number, decision: string, approverId: string, comments?: string): Promise<BgtApprovalRequest> {
    const request = await this.approvalRepo.findById(requestId);
    if (!request) throw new DomainError("NotFound", "Approval request not found");
    request.processStep(stepOrder, decision, approverId, comments);
    await this.approvalRepo.save(request);

    if (request.status === "approved") {
      const plan = await this.planRepo.findById(request.budgetPlanId as any);
      if (plan) {
        plan.approve(approverId);
        await this.planRepo.save(plan);
      }
    }
    return request;
  }

  async resubmitRequest(requestId: string): Promise<BgtApprovalRequest> {
    const request = await this.approvalRepo.findById(requestId);
    if (!request) throw new DomainError("NotFound", "Approval request not found");
    request.resubmit();
    await this.approvalRepo.save(request);
    return request;
  }

  async addStepsBulk(requestId: string, steps: CreateApprovalStepInput[]): Promise<BgtApprovalRequest> {
    const request = await this.approvalRepo.findById(requestId);
    if (!request) throw new DomainError("NotFound", "Approval request not found");
    for (const p of steps) {
      const step = BgtApprovalStep.create({ ...p, approvalRequestId: requestId });
      request.addStep(step);
    }
    await this.approvalRepo.save(request);
    return request;
  }
}
