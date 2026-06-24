import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  PrismaBgtAllocationRuleRepository,
  PrismaBgtAllocationResultRepository,
} from "../../infrastructure/budget/budget-prisma-repos.js";
import { BgtAllocationRule, BgtAllocationRuleLine, BgtAllocationResult } from "../../domain/budget/bgt-allocation.js";

export interface CreateAllocationRuleInput {
  code: string; name: string; allocationMethod?: string;
  description?: string; sourceBudgetPlanId?: string;
  targetBudgetPlanId?: string; sourceDimensionType?: string;
  sourceDimensionId?: string; targetDimensionType?: string;
  targetDimensionId?: string; totalAmount?: number;
  fiscalYearId?: string; periodType?: string; isRecurring?: boolean;
  recurrenceInterval?: string; notes?: string; createdById?: string;
}

export interface CreateAllocationRuleLineInput {
  ruleId: string; lineNumber: number;
  sourceGlAccountId?: string; targetGlAccountId?: string;
  sourceCostCenterId?: string; targetCostCenterId?: string;
  sourceDepartmentId?: string; targetDepartmentId?: string;
  sourceProjectId?: string; targetProjectId?: string;
  allocationPct?: number; allocationAmount?: number;
  driverId?: string; driverValue?: number; description?: string;
}

@Injectable()
export class AllocationEngineService {
  constructor(
    private readonly ruleRepo: PrismaBgtAllocationRuleRepository,
    private readonly resultRepo: PrismaBgtAllocationResultRepository,
  ) {}

  async createRule(p: CreateAllocationRuleInput): Promise<BgtAllocationRule> {
    const existing = await this.ruleRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Allocation rule ${p.code} already exists`);
    const rule = BgtAllocationRule.create(p);
    await this.ruleRepo.save(rule);
    return rule;
  }

  async getRule(id: string): Promise<BgtAllocationRule | null> {
    return this.ruleRepo.findById(id);
  }

  async listRules(status?: string): Promise<BgtAllocationRule[]> {
    if (status) return this.ruleRepo.findByStatus(status);
    return this.ruleRepo.findAll();
  }

  async addRuleLine(ruleId: string, p: CreateAllocationRuleLineInput): Promise<BgtAllocationRule> {
    const rule = await this.ruleRepo.findById(ruleId);
    if (!rule) throw new DomainError("NotFound", "Allocation rule not found");
    const line = BgtAllocationRuleLine.create({ ...p, ruleId });
    rule.addLine(line);
    await this.ruleRepo.save(rule);
    return rule;
  }

  async executeRule(ruleId: string, periodId?: string): Promise<BgtAllocationResult> {
    const rule = await this.ruleRepo.findById(ruleId);
    if (!rule) throw new DomainError("NotFound", "Allocation rule not found");
    const result = rule.execute(periodId);
    await this.ruleRepo.save(rule);
    await this.resultRepo.save(result);
    return result;
  }

  async getResults(ruleId: string): Promise<BgtAllocationResult[]> {
    return this.resultRepo.findByRule(ruleId);
  }

  async markResultPosted(resultId: string, glBatchId: string): Promise<void> {
    const result = await this.resultRepo.findById(resultId);
    if (!result) throw new DomainError("NotFound", "Allocation result not found");
    result.markPosted(glBatchId);
    await this.resultRepo.save(result);
  }
}
