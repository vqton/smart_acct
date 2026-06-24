import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  CostPool, CostPoolState, CostPoolId,
  AllocationRule, AllocationRuleState, AllocationRuleId,
  OverheadRate, OverheadRateState, OverheadRateId,
  CostSnapshot, CostSnapshotState, CostSnapshotId, CostSnapshotLine,
  CstCostPoolType, CstAllocationMethod, CstAllocationBasis,
  CstCostSnapshotType, CstCostMethod,
} from "../../domain/costing/index.js";
import {
  PrismaCostPoolRepository,
  PrismaAllocationRuleRepository,
  PrismaOverheadRateRepository,
  PrismaCostSnapshotRepository,
  PrismaAllocationEntryRepository,
} from "../../infrastructure/costing/costing-prisma-repos.js";

@Injectable()
export class AllocationEngineService {
  constructor(
    private readonly poolRepo: PrismaCostPoolRepository,
    private readonly ruleRepo: PrismaAllocationRuleRepository,
    private readonly overheadRepo: PrismaOverheadRateRepository,
    private readonly snapshotRepo: PrismaCostSnapshotRepository,
    private readonly entryRepo: PrismaAllocationEntryRepository,
  ) {}

  // ─── Cost Pools ────────────────────────────────────────────────────────────

  async createCostPool(p: {
    code: string; name: string; poolType: string;
    costCenterId?: string; totalAmount?: number;
    fiscalYearId?: string; periodId?: string;
  }): Promise<CostPoolState> {
    const pool = CostPool.create({
      code: p.code, name: p.name,
      poolType: p.poolType as CstCostPoolType,
      costCenterId: p.costCenterId, totalAmount: p.totalAmount,
      fiscalYearId: p.fiscalYearId, periodId: p.periodId,
    });
    await this.poolRepo.save(pool);
    return pool.toState();
  }

  // ─── Allocation Rules ──────────────────────────────────────────────────────

  async createAllocationRule(p: {
    code: string; name: string; poolId?: string;
    sourceCostCenterId?: string; targetCostCenterId?: string;
    allocationMethod: string; allocationBasis: string;
    basisValue?: number; percentage?: number; fixedAmount?: number;
    priority?: number; fiscalYearId?: string; periodId?: string;
  }): Promise<AllocationRuleState> {
    const rule = AllocationRule.create({
      code: p.code, name: p.name, poolId: p.poolId,
      sourceCostCenterId: p.sourceCostCenterId,
      targetCostCenterId: p.targetCostCenterId,
      allocationMethod: p.allocationMethod as CstAllocationMethod,
      allocationBasis: p.allocationBasis as CstAllocationBasis,
      basisValue: p.basisValue, percentage: p.percentage,
      fixedAmount: p.fixedAmount, priority: p.priority,
      fiscalYearId: p.fiscalYearId, periodId: p.periodId,
    });
    await this.ruleRepo.save(rule);
    return rule.toState();
  }

  // ─── Overhead Rates ────────────────────────────────────────────────────────

  async createOverheadRate(p: {
    code: string; name: string; costPoolType: string;
    allocationBasis: string; rate: number; rateType?: string;
    workCenterId?: string; costCenterId?: string;
    fiscalYearId?: string; costVersionId?: string;
  }): Promise<OverheadRateState> {
    const oh = OverheadRate.create({
      code: p.code, name: p.name,
      costPoolType: p.costPoolType as CstCostPoolType,
      allocationBasis: p.allocationBasis as CstAllocationBasis,
      rate: p.rate, rateType: p.rateType,
      workCenterId: p.workCenterId, costCenterId: p.costCenterId,
      fiscalYearId: p.fiscalYearId, costVersionId: p.costVersionId,
    });
    await this.overheadRepo.save(oh);
    return oh.toState();
  }

  // ─── Execute Allocation ────────────────────────────────────────────────────

  async executeAllocation(periodId: string): Promise<{
    poolsProcessed: number; totalAllocated: number; entriesCreated: number;
  }> {
    const pools = await this.poolRepo.findByPeriod(periodId);
    let totalAllocated = 0;
    let entriesCreated = 0;

    for (const pool of pools) {
      const ps = pool.toState();
      if (ps.unallocatedAmount <= 0) continue;

      const rules = await this.ruleRepo.findByPool(pool.id.value);
      let poolAllocated = 0;

      for (const rule of rules) {
        const rs = rule.toState();
        const amount = rule.calculateAllocation(ps.unallocatedAmount);
        if (amount <= 0) continue;

        pool.allocate(amount);
        await this.entryRepo.save({
          ruleId: rs.id, productionOrderId: null, batchId: null,
          periodId, sourceCostCenterId: rs.sourceCostCenterId,
          targetCostCenterId: rs.targetCostCenterId,
          sourceAmount: ps.totalAmount, allocatedAmount: amount,
          basisValue: rs.basisValue, allocationDate: new Date(),
          currencyCode: "VND", exchangeRate: 1, glBatchId: null,
          postedToGL: false, createdById: null,
        });
        poolAllocated += amount;
        entriesCreated++;
      }

      await this.poolRepo.save(pool);
      totalAllocated += poolAllocated;
    }

    return { poolsProcessed: pools.length, totalAllocated, entriesCreated };
  }

  // ─── Cost Snapshot ─────────────────────────────────────────────────────────

  async createCostSnapshot(p: {
    snapshotNumber: string; snapshotType: string;
    periodId?: string; fiscalYearId?: string;
  }): Promise<CostSnapshotState> {
    const snap = CostSnapshot.create({
      snapshotNumber: p.snapshotNumber,
      snapshotType: p.snapshotType as CstCostSnapshotType,
      periodId: p.periodId, fiscalYearId: p.fiscalYearId,
    });
    await this.snapshotRepo.save(snap);
    return snap.toState();
  }

  async freezeSnapshot(id: string, userId: string): Promise<CostSnapshotState> {
    const snap = await this.snapshotRepo.findById(new CostSnapshotId(id));
    if (!snap) throw new DomainError("NotFound", "Cost snapshot not found");
    snap.freeze(userId);
    await this.snapshotRepo.save(snap);
    return snap.toState();
  }

  // ─── Overhead Absorption ───────────────────────────────────────────────────

  async calculateOverheadAbsorption(productionOrderId: string): Promise<{
    laborOverhead: number; machineOverhead: number; totalOverhead: number;
  }> {
    const rates = await this.overheadRepo.findActive();
    let laborOverhead = 0;
    let machineOverhead = 0;

    for (const rate of rates) {
      const rs = rate.toState();
      if (rs.rateType === "percentage") {
        if (rs.costPoolType === CstCostPoolType.LaborOverhead) {
          laborOverhead += rs.rate;
        } else if (rs.costPoolType === CstCostPoolType.MachineOverhead) {
          machineOverhead += rs.rate;
        }
      }
    }

    return {
      laborOverhead,
      machineOverhead,
      totalOverhead: laborOverhead + machineOverhead,
    };
  }
}
