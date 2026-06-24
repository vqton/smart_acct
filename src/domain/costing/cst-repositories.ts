import { CostVersion, CostVersionState } from "./cst-cost-version.js";
import { CostVersionId } from "./cst-ids.js";
import { WorkCenter, WorkCenterState } from "./cst-work-center.js";
import { WorkCenterId } from "./cst-ids.js";
import { Bom, BomState } from "./cst-bom.js";
import { BomId } from "./cst-ids.js";
import { ProductionOrder, ProductionOrderState } from "./cst-production-order.js";
import { ProductionOrderId } from "./cst-ids.js";
import { CostPool, CostPoolState } from "./cst-cost-pool.js";
import { CostPoolId } from "./cst-ids.js";
import { AllocationRule, AllocationRuleState } from "./cst-allocation-rule.js";
import { AllocationRuleId } from "./cst-ids.js";
import { OverheadRate, OverheadRateState } from "./cst-overhead-rate.js";
import { OverheadRateId } from "./cst-ids.js";
import { CostSnapshot, CostSnapshotState } from "./cst-cost-snapshot.js";
import { CostSnapshotId } from "./cst-ids.js";
import { ProductionVariance, ProductionVarianceState } from "./cst-prod-variance.js";
import { ProductionVarianceId } from "./cst-ids.js";

export interface CostVersionRepository {
  save(version: CostVersion): Promise<void>;
  findById(id: CostVersionId): Promise<CostVersion | null>;
  findByCode(code: string): Promise<CostVersion | null>;
  findActive(): Promise<CostVersion[]>;
  findByFiscalYear(fiscalYearId: string): Promise<CostVersion[]>;
}

export interface WorkCenterRepository {
  save(center: WorkCenter): Promise<void>;
  findById(id: WorkCenterId): Promise<WorkCenter | null>;
  findByCode(code: string): Promise<WorkCenter | null>;
  findAll(): Promise<WorkCenter[]>;
  findByCostCenter(costCenterId: string): Promise<WorkCenter[]>;
}

export interface BomRepository {
  save(bom: Bom): Promise<void>;
  findById(id: BomId): Promise<Bom | null>;
  findByCode(code: string): Promise<Bom | null>;
  findByItem(itemId: string): Promise<Bom[]>;
  findDefaultByItem(itemId: string): Promise<Bom | null>;
  findActive(): Promise<Bom[]>;
}

export interface ProductionOrderRepository {
  save(order: ProductionOrder): Promise<void>;
  findById(id: ProductionOrderId): Promise<ProductionOrder | null>;
  findByOrderNumber(orderNumber: string): Promise<ProductionOrder | null>;
  findByItem(itemId: string): Promise<ProductionOrder[]>;
  findByStatus(status: string): Promise<ProductionOrder[]>;
  findByCompany(companyId: string): Promise<ProductionOrder[]>;
}

export interface CostPoolRepository {
  save(pool: CostPool): Promise<void>;
  findById(id: CostPoolId): Promise<CostPool | null>;
  findByCode(code: string): Promise<CostPool | null>;
  findByType(poolType: string): Promise<CostPool[]>;
  findByCostCenter(costCenterId: string): Promise<CostPool[]>;
  findByPeriod(periodId: string): Promise<CostPool[]>;
}

export interface AllocationRuleRepository {
  save(rule: AllocationRule): Promise<void>;
  findById(id: AllocationRuleId): Promise<AllocationRule | null>;
  findByCode(code: string): Promise<AllocationRule | null>;
  findByPool(poolId: string): Promise<AllocationRule[]>;
  findBySourceCostCenter(costCenterId: string): Promise<AllocationRule[]>;
  findActive(): Promise<AllocationRule[]>;
}

export interface OverheadRateRepository {
  save(rate: OverheadRate): Promise<void>;
  findById(id: OverheadRateId): Promise<OverheadRate | null>;
  findByCode(code: string): Promise<OverheadRate | null>;
  findByWorkCenter(workCenterId: string): Promise<OverheadRate[]>;
  findByCostCenter(costCenterId: string): Promise<OverheadRate[]>;
  findActive(): Promise<OverheadRate[]>;
}

export interface CostSnapshotRepository {
  save(snapshot: CostSnapshot): Promise<void>;
  findById(id: CostSnapshotId): Promise<CostSnapshot | null>;
  findBySnapshotNumber(snapshotNumber: string): Promise<CostSnapshot | null>;
  findByPeriod(periodId: string): Promise<CostSnapshot[]>;
  findByType(snapshotType: string): Promise<CostSnapshot[]>;
  findLatestByPeriod(periodId: string): Promise<CostSnapshot | null>;
}

export interface ProductionVarianceRepository {
  save(variance: ProductionVariance): Promise<void>;
  findById(id: ProductionVarianceId): Promise<ProductionVariance | null>;
  findByOrder(orderId: string): Promise<ProductionVariance[]>;
  findByPeriod(periodId: string): Promise<ProductionVariance[]>;
  findByVarianceType(varianceType: string): Promise<ProductionVariance[]>;
}
