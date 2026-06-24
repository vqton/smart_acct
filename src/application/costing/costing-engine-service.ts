import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  CostVersion, CostVersionState, CostVersionId,
  WorkCenter, WorkCenterState, WorkCenterId,
  Bom, BomState, BomLine, BomRouting, BomId,
  ProductionOrder, ProductionOrderState, ProductionOrderId,
  ProductionOrderComponent, ProductionOrderOperation,
  OverheadRate, OverheadRateId,
  ProductionVariance, ProductionVarianceId,
  CstCostMethod, CstCostElementType, CstProductionOrderStatus,
  CstAllocationBasis, CstCostPoolType, CstVarianceType,
} from "../../domain/costing/index.js";
import { ItemId } from "../../domain/inventory/inv-ids.js";
import {
  PrismaCostVersionRepository,
  PrismaWorkCenterRepository,
  PrismaBomRepository,
  PrismaProductionOrderRepository,
  PrismaOverheadRateRepository,
  PrismaProductionVarianceRepository,
} from "../../infrastructure/costing/costing-prisma-repos.js";
import { PrismaItemRepository } from "../../infrastructure/inventory/inventory-prisma-repos.js";

@Injectable()
export class CostingEngineService {
  constructor(
    private readonly costVersionRepo: PrismaCostVersionRepository,
    private readonly workCenterRepo: PrismaWorkCenterRepository,
    private readonly bomRepo: PrismaBomRepository,
    private readonly prodOrderRepo: PrismaProductionOrderRepository,
    private readonly overheadRateRepo: PrismaOverheadRateRepository,
    private readonly varianceRepo: PrismaProductionVarianceRepository,
    private readonly itemRepo: PrismaItemRepository,
  ) {}

  // ─── Cost Version ──────────────────────────────────────────────────────────

  async createCostVersion(p: {
    code: string; name: string; costMethod: string; fiscalYearId: string;
    effectiveFrom: string; effectiveTo?: string; description?: string;
  }): Promise<CostVersionState> {
    const cv = CostVersion.create({
      code: p.code, name: p.name,
      costMethod: p.costMethod as CstCostMethod,
      fiscalYearId: p.fiscalYearId,
      effectiveFrom: new Date(p.effectiveFrom),
      effectiveTo: p.effectiveTo ? new Date(p.effectiveTo) : null,
      description: p.description,
    });
    await this.costVersionRepo.save(cv);
    return cv.toState();
  }

  async lockCostVersion(id: string): Promise<CostVersionState> {
    const cv = await this.costVersionRepo.findById(new CostVersionId(id));
    if (!cv) throw new DomainError("NotFound", "Cost version not found");
    cv.lock();
    await this.costVersionRepo.save(cv);
    return cv.toState();
  }

  // ─── Work Center ───────────────────────────────────────────────────────────

  async createWorkCenter(p: {
    code: string; name: string; workCenterType?: string;
    costCenterId?: string; departmentId?: string;
    hourlyRate?: number; machineRate?: number; overheadRate?: number;
  }): Promise<WorkCenterState> {
    const wc = WorkCenter.create({
      code: p.code, name: p.name, workCenterType: p.workCenterType,
      costCenterId: p.costCenterId, departmentId: p.departmentId,
      hourlyRate: p.hourlyRate, machineRate: p.machineRate, overheadRate: p.overheadRate,
    });
    await this.workCenterRepo.save(wc);
    return wc.toState();
  }

  // ─── BOM ───────────────────────────────────────────────────────────────────

  async createBom(p: {
    code: string; name: string; itemId: string; itemCode: string; itemName: string;
    quantity?: number; uom?: string; effectiveFrom?: string; description?: string;
  }): Promise<BomState> {
    const bom = Bom.create({
      code: p.code, name: p.name, itemId: p.itemId, itemCode: p.itemCode, itemName: p.itemName,
      quantity: p.quantity, uom: p.uom,
      effectiveFrom: p.effectiveFrom ? new Date(p.effectiveFrom) : new Date(),
      description: p.description,
    });
    await this.bomRepo.save(bom);
    return bom.toState();
  }

  async addBomLine(bomId: string, p: {
    lineNumber: number; componentItemId: string; componentCode: string;
    componentName: string; quantity: number; uom?: string;
    costElement?: string; unitCost?: number;
  }): Promise<BomState> {
    const bom = await this.bomRepo.findById(new BomId(bomId));
    if (!bom) throw new DomainError("NotFound", "BOM not found");
    const line = BomLine.create({
      bomId, lineNumber: p.lineNumber, componentItemId: p.componentItemId,
      componentCode: p.componentCode, componentName: p.componentName,
      quantity: p.quantity, uom: p.uom,
      costElement: p.costElement as CstCostElementType, unitCost: p.unitCost,
    });
    bom.addLine(line);
    await this.bomRepo.save(bom);
    return bom.toState();
  }

  async addBomRouting(bomId: string, p: {
    operationSeq: number; operationDescription: string;
    workCenterId?: string; setupTime?: number; runTime?: number;
    laborRate?: number; machineRate?: number; overheadRate?: number;
  }): Promise<BomState> {
    const bom = await this.bomRepo.findById(new BomId(bomId));
    if (!bom) throw new DomainError("NotFound", "BOM not found");
    const routing = BomRouting.create({
      bomId, operationSeq: p.operationSeq,
      operationDescription: p.operationDescription,
      workCenterId: p.workCenterId, setupTime: p.setupTime, runTime: p.runTime,
      laborRate: p.laborRate, machineRate: p.machineRate, overheadRate: p.overheadRate,
    });
    bom.addRouting(routing);
    await this.bomRepo.save(bom);
    return bom.toState();
  }

  async calculateBomCost(bomId: string): Promise<{ materialCost: number; routingCost: number; totalCost: number }> {
    const bom = await this.bomRepo.findById(new BomId(bomId));
    if (!bom) throw new DomainError("NotFound", "BOM not found");
    return {
      materialCost: bom.totalMaterialCost(),
      routingCost: bom.totalRoutingCost(),
      totalCost: bom.totalCost(),
    };
  }

  async rollUpCost(bomId: string): Promise<BomState> {
    const bom = await this.bomRepo.findById(new BomId(bomId));
    if (!bom) throw new DomainError("NotFound", "BOM not found");
    for (const line of bom.lines) {
      const ls = line.toState();
      const childBom = await this.bomRepo.findDefaultByItem(ls.componentItemId);
      if (childBom) {
        line.updateCost(childBom.totalCost());
      } else {
        const item = await this.itemRepo.findById(new ItemId(ls.componentItemId));
        if (item) {
          line.updateCost(item.standardCost ?? 0);
        }
      }
    }
    bom.revise();
    await this.bomRepo.save(bom);
    return bom.toState();
  }

  // ─── Production Orders ─────────────────────────────────────────────────────

  async createProductionOrder(p: {
    orderNumber: string; itemId: string; itemCode: string; itemName: string;
    quantity: number; plannedStartDate: string; companyId: string;
    bomId?: string; workCenterId?: string; warehouseId?: string;
    estimatedMaterialCost?: number; estimatedLaborCost?: number;
    estimatedMachineCost?: number; estimatedOverheadCost?: number;
  }): Promise<ProductionOrderState> {
    const po = ProductionOrder.create({
      orderNumber: p.orderNumber, itemId: p.itemId, itemCode: p.itemCode,
      itemName: p.itemName, quantity: p.quantity,
      plannedStartDate: new Date(p.plannedStartDate), companyId: p.companyId,
      bomId: p.bomId, workCenterId: p.workCenterId, warehouseId: p.warehouseId,
      estimatedMaterialCost: p.estimatedMaterialCost,
      estimatedLaborCost: p.estimatedLaborCost,
      estimatedMachineCost: p.estimatedMachineCost,
      estimatedOverheadCost: p.estimatedOverheadCost,
    });
    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async loadBomToOrder(orderId: string, bomId: string): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(orderId));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    const bom = await this.bomRepo.findById(new BomId(bomId));
    if (!bom) throw new DomainError("NotFound", "BOM not found");

    let lineNum = 0;
    for (const bl of bom.lines) {
      const bls = bl.toState();
      po.addComponent(ProductionOrderComponent.create({
        orderId: po.id.value, lineNumber: ++lineNum,
        componentItemId: bls.componentItemId, componentCode: bls.componentCode,
        componentName: bls.componentName, requiredQty: bls.quantity * po.quantity,
        unitCost: bls.unitCost, costElement: bls.costElement as CstCostElementType,
        bomLineId: bls.id,
      }));
    }

    for (const br of bom.routings) {
      const brs = br.toState();
      po.addOperation(ProductionOrderOperation.create({
        orderId: po.id.value, operationSeq: brs.operationSeq,
        operationName: brs.operationDescription,
        workCenterId: brs.workCenterId,
        setupTime: brs.setupTime, runTime: brs.runTime,
        laborRate: brs.laborRate, machineRate: brs.machineRate,
        overheadRate: brs.overheadRate,
      }));
    }

    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async releaseProductionOrder(id: string, userId: string): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(id));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    po.release(userId);
    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async issueComponent(orderId: string, componentId: string, quantity: number, unitCost: number): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(orderId));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    po.issueComponent(componentId, quantity, unitCost);
    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async completeOperation(orderId: string, operationId: string, actualSetupTime: number, actualRunTime: number): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(orderId));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    po.completeOperation(operationId, actualSetupTime, actualRunTime);
    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async completeProductionOrder(id: string, userId: string): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(id));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    po.complete(userId);

    const ps = po.toState();
    const variances = [
      { type: CstVarianceType.MaterialPrice, element: CstCostElementType.Material, standard: ps.estimatedMaterialCost, actual: ps.actualMaterialCost },
      { type: CstVarianceType.LaborRate, element: CstCostElementType.Labor, standard: ps.estimatedLaborCost, actual: ps.actualLaborCost },
      { type: CstVarianceType.MachineRate, element: CstCostElementType.Machine, standard: ps.estimatedMachineCost, actual: ps.actualMachineCost },
      { type: CstVarianceType.OverheadSpending, element: CstCostElementType.Overhead, standard: ps.estimatedOverheadCost, actual: ps.actualOverheadCost },
    ];

    for (const v of variances) {
      const diff = v.actual - v.standard;
      if (Math.abs(diff) > 0.001) {
        const pv = ProductionVariance.create({
          orderId: po.id.value, varianceType: v.type, costElement: v.element,
          standardAmount: v.standard, actualAmount: v.actual,
        });
        await this.varianceRepo.save(pv);
      }
    }

    await this.prodOrderRepo.save(po);
    return po.toState();
  }

  async closeProductionOrder(id: string, userId: string): Promise<ProductionOrderState> {
    const po = await this.prodOrderRepo.findById(new ProductionOrderId(id));
    if (!po) throw new DomainError("NotFound", "Production order not found");
    po.close(userId);
    await this.prodOrderRepo.save(po);
    return po.toState();
  }
}
