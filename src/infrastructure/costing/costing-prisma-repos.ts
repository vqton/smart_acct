import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  CostVersion, type CostVersionState,
  CostVersionId, WorkCenter, type WorkCenterState,
  WorkCenterId, Bom, type BomState, BomLine, BomRouting,
  BomId, ProductionOrder, type ProductionOrderState,
  ProductionOrderComponent, ProductionOrderOperation,
  ProductionOrderId, CostPool, type CostPoolState,
  CostPoolId, AllocationRule, type AllocationRuleState,
  AllocationRuleId, OverheadRate, type OverheadRateState,
  OverheadRateId, CostSnapshot, type CostSnapshotState,
  CostSnapshotLine, CostSnapshotId,
  ProductionVariance, type ProductionVarianceState,
  ProductionVarianceId,
} from "../../domain/costing/index.js";
import type {
  CostVersionRepository, WorkCenterRepository,
  BomRepository, ProductionOrderRepository,
  CostPoolRepository, AllocationRuleRepository,
  OverheadRateRepository, CostSnapshotRepository,
  ProductionVarianceRepository,
} from "../../domain/costing/cst-repositories.js";

function toNumber(val: unknown, fallback: number = 0): number {
  if (val == null) return fallback;
  if (typeof val === "bigint") return Number(val);
  if (typeof val === "string") return parseFloat(val);
  if (typeof val === "number") return val;
  if (typeof val === "object" && "toString" in (val as object)) return parseFloat((val as any).toString());
  return fallback;
}

@Injectable()
export class PrismaCostVersionRepository implements CostVersionRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(version: CostVersion): Promise<void> {
    const s = version.toState();
    const data: any = { ...s };
    await this.prisma.cstCostVersion.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: CostVersionId): Promise<CostVersion | null> {
    const row = await this.prisma.cstCostVersion.findUnique({ where: { id: id.value } });
    return row ? CostVersion.load(row as any) : null;
  }

  async findByCode(code: string): Promise<CostVersion | null> {
    const row = await this.prisma.cstCostVersion.findUnique({ where: { code } });
    return row ? CostVersion.load(row as any) : null;
  }

  async findActive(): Promise<CostVersion[]> {
    return (await this.prisma.cstCostVersion.findMany({ where: { isActive: true, deletedAt: null }, orderBy: { createdAt: "desc" } })).map(r => CostVersion.load(r as any));
  }

  async findByFiscalYear(fiscalYearId: string): Promise<CostVersion[]> {
    return (await this.prisma.cstCostVersion.findMany({ where: { fiscalYearId }, orderBy: { createdAt: "desc" } })).map(r => CostVersion.load(r as any));
  }
}

@Injectable()
export class PrismaWorkCenterRepository implements WorkCenterRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(center: WorkCenter): Promise<void> {
    const s = center.toState();
    const data: any = { ...s };
    await this.prisma.cstWorkCenter.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: WorkCenterId): Promise<WorkCenter | null> {
    const row = await this.prisma.cstWorkCenter.findUnique({ where: { id: id.value } });
    return row ? WorkCenter.load(row as any) : null;
  }

  async findByCode(code: string): Promise<WorkCenter | null> {
    const row = await this.prisma.cstWorkCenter.findUnique({ where: { code } });
    return row ? WorkCenter.load(row as any) : null;
  }

  async findAll(): Promise<WorkCenter[]> {
    return (await this.prisma.cstWorkCenter.findMany({ orderBy: { code: "asc" } })).map(r => WorkCenter.load(r as any));
  }

  async findByCostCenter(costCenterId: string): Promise<WorkCenter[]> {
    return (await this.prisma.cstWorkCenter.findMany({ where: { costCenterId }, orderBy: { code: "asc" } })).map(r => WorkCenter.load(r as any));
  }
}

@Injectable()
export class PrismaBomRepository implements BomRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(bom: Bom): Promise<void> {
    const s = bom.toState();
    const { lines, routings, ...header } = s;
    const data: any = { ...header };
    await this.prisma.cstBom.upsert({ where: { id: data.id }, create: data, update: data });

    for (const line of lines) {
      const lineData: any = { ...line };
      await this.prisma.cstBomLine.upsert({ where: { id: lineData.id }, create: lineData, update: lineData });
    }
    for (const routing of routings) {
      const routingData: any = { ...routing };
      await this.prisma.cstBomRouting.upsert({ where: { id: routingData.id }, create: routingData, update: routingData });
    }
  }

  async findById(id: BomId): Promise<Bom | null> {
    const row = await this.prisma.cstBom.findUnique({ where: { id: id.value }, include: { lines: true, routings: true } });
    if (!row) return null;
    return Bom.load({ ...row, lines: (row as any).lines ?? [], routings: (row as any).routings ?? [] } as any);
  }

  async findByCode(code: string): Promise<Bom | null> {
    const row = await this.prisma.cstBom.findUnique({ where: { code }, include: { lines: true, routings: true } });
    if (!row) return null;
    return Bom.load({ ...row, lines: (row as any).lines ?? [], routings: (row as any).routings ?? [] } as any);
  }

  async findByItem(itemId: string): Promise<Bom[]> {
    const rows = await this.prisma.cstBom.findMany({ where: { itemId }, include: { lines: true, routings: true }, orderBy: { createdAt: "desc" } });
    return rows.map(r => Bom.load({ ...r, lines: (r as any).lines ?? [], routings: (r as any).routings ?? [] } as any));
  }

  async findDefaultByItem(itemId: string): Promise<Bom | null> {
    const row = await this.prisma.cstBom.findFirst({ where: { itemId, isDefault: true, isActive: true, deletedAt: null }, include: { lines: true, routings: true } });
    if (!row) return null;
    return Bom.load({ ...row, lines: (row as any).lines ?? [], routings: (row as any).routings ?? [] } as any);
  }

  async findActive(): Promise<Bom[]> {
    const rows = await this.prisma.cstBom.findMany({ where: { isActive: true, deletedAt: null }, include: { lines: true, routings: true }, orderBy: { code: "asc" } });
    return rows.map(r => Bom.load({ ...r, lines: (r as any).lines ?? [], routings: (r as any).routings ?? [] } as any));
  }
}

@Injectable()
export class PrismaProductionOrderRepository implements ProductionOrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(order: ProductionOrder): Promise<void> {
    const s = order.toState();
    const { components, operations, ...header } = s;
    const data: any = { ...header };
    await this.prisma.cstProductionOrder.upsert({ where: { id: data.id }, create: data, update: data });

    for (const comp of components) {
      const compData: any = { ...comp };
      await this.prisma.cstProductionOrderComponent.upsert({ where: { id: compData.id }, create: compData, update: compData });
    }
    for (const op of operations) {
      const opData: any = { ...op };
      await this.prisma.cstProductionOrderOperation.upsert({ where: { id: opData.id }, create: opData, update: opData });
    }
  }

  async findById(id: ProductionOrderId): Promise<ProductionOrder | null> {
    const row = await this.prisma.cstProductionOrder.findUnique({ where: { id: id.value }, include: { components: true, operations: true } });
    if (!row) return null;
    return ProductionOrder.load({ ...row, components: (row as any).components ?? [], operations: (row as any).operations ?? [] } as any);
  }

  async findByOrderNumber(orderNumber: string): Promise<ProductionOrder | null> {
    const row = await this.prisma.cstProductionOrder.findUnique({ where: { orderNumber }, include: { components: true, operations: true } });
    if (!row) return null;
    return ProductionOrder.load({ ...row, components: (row as any).components ?? [], operations: (row as any).operations ?? [] } as any);
  }

  async findByItem(itemId: string): Promise<ProductionOrder[]> {
    const rows = await this.prisma.cstProductionOrder.findMany({ where: { itemId }, include: { components: true, operations: true }, orderBy: { createdAt: "desc" } });
    return rows.map(r => ProductionOrder.load({ ...r, components: (r as any).components ?? [], operations: (r as any).operations ?? [] } as any));
  }

  async findByStatus(status: string): Promise<ProductionOrder[]> {
    const rows = await this.prisma.cstProductionOrder.findMany({ where: { status: status as any }, include: { components: true, operations: true }, orderBy: { createdAt: "desc" } });
    return rows.map(r => ProductionOrder.load({ ...r, components: (r as any).components ?? [], operations: (r as any).operations ?? [] } as any));
  }

  async findByCompany(companyId: string): Promise<ProductionOrder[]> {
    const rows = await this.prisma.cstProductionOrder.findMany({ where: { companyId }, include: { components: true, operations: true }, orderBy: { createdAt: "desc" } });
    return rows.map(r => ProductionOrder.load({ ...r, components: (r as any).components ?? [], operations: (r as any).operations ?? [] } as any));
  }
}

@Injectable()
export class PrismaCostPoolRepository implements CostPoolRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(pool: CostPool): Promise<void> {
    const s = pool.toState();
    const data: any = { ...s };
    await this.prisma.cstCostPool.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: CostPoolId): Promise<CostPool | null> {
    const row = await this.prisma.cstCostPool.findUnique({ where: { id: id.value } });
    return row ? CostPool.load(row as any) : null;
  }

  async findByCode(code: string): Promise<CostPool | null> {
    const row = await this.prisma.cstCostPool.findUnique({ where: { code } });
    return row ? CostPool.load(row as any) : null;
  }

  async findByType(poolType: string): Promise<CostPool[]> {
    return (await this.prisma.cstCostPool.findMany({ where: { poolType: poolType as any }, orderBy: { code: "asc" } })).map(r => CostPool.load(r as any));
  }

  async findByCostCenter(costCenterId: string): Promise<CostPool[]> {
    return (await this.prisma.cstCostPool.findMany({ where: { costCenterId }, orderBy: { code: "asc" } })).map(r => CostPool.load(r as any));
  }

  async findByPeriod(periodId: string): Promise<CostPool[]> {
    return (await this.prisma.cstCostPool.findMany({ where: { periodId }, orderBy: { code: "asc" } })).map(r => CostPool.load(r as any));
  }
}

@Injectable()
export class PrismaAllocationRuleRepository implements AllocationRuleRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rule: AllocationRule): Promise<void> {
    const s = rule.toState();
    const data: any = { ...s };
    await this.prisma.cstCostAllocationRule.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: AllocationRuleId): Promise<AllocationRule | null> {
    const row = await this.prisma.cstCostAllocationRule.findUnique({ where: { id: id.value } });
    return row ? AllocationRule.load(row as any) : null;
  }

  async findByCode(code: string): Promise<AllocationRule | null> {
    const row = await this.prisma.cstCostAllocationRule.findUnique({ where: { code } });
    return row ? AllocationRule.load(row as any) : null;
  }

  async findByPool(poolId: string): Promise<AllocationRule[]> {
    return (await this.prisma.cstCostAllocationRule.findMany({ where: { poolId }, orderBy: { priority: "asc" } })).map(r => AllocationRule.load(r as any));
  }

  async findBySourceCostCenter(costCenterId: string): Promise<AllocationRule[]> {
    return (await this.prisma.cstCostAllocationRule.findMany({ where: { sourceCostCenterId: costCenterId }, orderBy: { priority: "asc" } })).map(r => AllocationRule.load(r as any));
  }

  async findActive(): Promise<AllocationRule[]> {
    return (await this.prisma.cstCostAllocationRule.findMany({ where: { isActive: true, deletedAt: null }, orderBy: { priority: "asc" } })).map(r => AllocationRule.load(r as any));
  }
}

@Injectable()
export class PrismaOverheadRateRepository implements OverheadRateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rate: OverheadRate): Promise<void> {
    const s = rate.toState();
    const data: any = { ...s };
    await this.prisma.cstOverheadRate.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: OverheadRateId): Promise<OverheadRate | null> {
    const row = await this.prisma.cstOverheadRate.findUnique({ where: { id: id.value } });
    return row ? OverheadRate.load(row as any) : null;
  }

  async findByCode(code: string): Promise<OverheadRate | null> {
    const row = await this.prisma.cstOverheadRate.findUnique({ where: { code } });
    return row ? OverheadRate.load(row as any) : null;
  }

  async findByWorkCenter(workCenterId: string): Promise<OverheadRate[]> {
    return (await this.prisma.cstOverheadRate.findMany({ where: { workCenterId }, orderBy: { code: "asc" } })).map(r => OverheadRate.load(r as any));
  }

  async findByCostCenter(costCenterId: string): Promise<OverheadRate[]> {
    return (await this.prisma.cstOverheadRate.findMany({ where: { costCenterId }, orderBy: { code: "asc" } })).map(r => OverheadRate.load(r as any));
  }

  async findActive(): Promise<OverheadRate[]> {
    return (await this.prisma.cstOverheadRate.findMany({ where: { isActive: true, deletedAt: null }, orderBy: { code: "asc" } })).map(r => OverheadRate.load(r as any));
  }
}

@Injectable()
export class PrismaCostSnapshotRepository implements CostSnapshotRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(snapshot: CostSnapshot): Promise<void> {
    const s = snapshot.toState();
    const { lines, ...header } = s;
    const data: any = { ...header };
    await this.prisma.cstCostSnapshot.upsert({ where: { id: data.id }, create: data, update: data });

    for (const line of lines) {
      const lineData: any = { ...line };
      await this.prisma.cstCostSnapshotLine.upsert({ where: { id: lineData.id }, create: lineData, update: lineData });
    }
  }

  async findById(id: CostSnapshotId): Promise<CostSnapshot | null> {
    const row = await this.prisma.cstCostSnapshot.findUnique({ where: { id: id.value }, include: { lines: true } });
    if (!row) return null;
    return CostSnapshot.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findBySnapshotNumber(snapshotNumber: string): Promise<CostSnapshot | null> {
    const row = await this.prisma.cstCostSnapshot.findUnique({ where: { snapshotNumber }, include: { lines: true } });
    if (!row) return null;
    return CostSnapshot.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }

  async findByPeriod(periodId: string): Promise<CostSnapshot[]> {
    const rows = await this.prisma.cstCostSnapshot.findMany({ where: { periodId }, include: { lines: true }, orderBy: { snapshotDate: "desc" } });
    return rows.map(r => CostSnapshot.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findByType(snapshotType: string): Promise<CostSnapshot[]> {
    const rows = await this.prisma.cstCostSnapshot.findMany({ where: { snapshotType: snapshotType as any }, include: { lines: true }, orderBy: { snapshotDate: "desc" } });
    return rows.map(r => CostSnapshot.load({ ...r, lines: (r as any).lines ?? [] } as any));
  }

  async findLatestByPeriod(periodId: string): Promise<CostSnapshot | null> {
    const row = await this.prisma.cstCostSnapshot.findFirst({ where: { periodId }, include: { lines: true }, orderBy: { snapshotDate: "desc" } });
    if (!row) return null;
    return CostSnapshot.load({ ...row, lines: (row as any).lines ?? [] } as any);
  }
}

@Injectable()
export class PrismaProductionVarianceRepository implements ProductionVarianceRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(variance: ProductionVariance): Promise<void> {
    const s = variance.toState();
    const data: any = { ...s };
    await this.prisma.cstProductionVariance.upsert({ where: { id: data.id }, create: data, update: data });
  }

  async findById(id: ProductionVarianceId): Promise<ProductionVariance | null> {
    const row = await this.prisma.cstProductionVariance.findUnique({ where: { id: id.value } });
    return row ? ProductionVariance.load(row as any) : null;
  }

  async findByOrder(orderId: string): Promise<ProductionVariance[]> {
    return (await this.prisma.cstProductionVariance.findMany({ where: { orderId }, orderBy: { createdAt: "desc" } })).map(r => ProductionVariance.load(r as any));
  }

  async findByPeriod(periodId: string): Promise<ProductionVariance[]> {
    return (await this.prisma.cstProductionVariance.findMany({ where: { periodId }, orderBy: { createdAt: "desc" } })).map(r => ProductionVariance.load(r as any));
  }

  async findByVarianceType(varianceType: string): Promise<ProductionVariance[]> {
    return (await this.prisma.cstProductionVariance.findMany({ where: { varianceType: varianceType as any }, orderBy: { createdAt: "desc" } })).map(r => ProductionVariance.load(r as any));
  }
}

// ─── Allocation Entry Repository (simplified, not aggregate-root) ─────────

export interface AllocationEntryRecord {
  id?: string;
  ruleId: string;
  productionOrderId: string | null;
  batchId: string | null;
  periodId: string | null;
  sourceCostCenterId: string | null;
  targetCostCenterId: string | null;
  sourceAmount: number;
  allocatedAmount: number;
  basisValue: number;
  allocationDate: Date;
  currencyCode: string;
  exchangeRate: number;
  glBatchId: string | null;
  postedToGL: boolean;
  createdById: string | null;
}

@Injectable()
export class PrismaAllocationEntryRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(entry: AllocationEntryRecord): Promise<void> {
    const data: any = { ...entry };
    await this.prisma.cstCostAllocationEntry.upsert({ where: { id: data.id ?? crypto.randomUUID() }, create: data, update: data });
  }

  async findByPeriod(periodId: string): Promise<AllocationEntryRecord[]> {
    return (await this.prisma.cstCostAllocationEntry.findMany({ where: { periodId }, orderBy: { allocationDate: "desc" } })) as any;
  }

  async findByRule(ruleId: string): Promise<AllocationEntryRecord[]> {
    return (await this.prisma.cstCostAllocationEntry.findMany({ where: { ruleId }, orderBy: { allocationDate: "desc" } })) as any;
  }
}
