import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { CostingEngineService } from "../../application/costing/costing-engine-service.js";
import { AllocationEngineService } from "../../application/costing/allocation-engine-service.js";
import { PeriodCloseService } from "../../application/costing/period-close-service.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateCostVersionDto, CreateWorkCenterDto,
  CreateBomDto, AddBomLineDto, AddBomRoutingDto,
  CreateProductionOrderDto, IssueComponentDto, CompleteOperationDto,
  CreateCostPoolDto, CreateAllocationRuleDto, CreateOverheadRateDto,
  CreateCostSnapshotDto,
} from "./dto/costing.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) {
    if (e.kind === "NotFound") throw new NotFoundException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}

@ApiTags("Costing")
@Controller("api/costing")
export class CostingController {
  constructor(
    private readonly costingEngine: CostingEngineService,
    private readonly allocationEngine: AllocationEngineService,
    private readonly periodClose: PeriodCloseService,
  ) {}

  // ─── Cost Versions ─────────────────────────────────────────────────────────

  @Post("cost-versions")
  @ApiOperation({ summary: "Create cost version" })
  async createCostVersion(@Body() dto: CreateCostVersionDto) {
    try { return await this.costingEngine.createCostVersion(dto); }
    catch (e) { handleError(e); }
  }

  @Post("cost-versions/:id/lock")
  @ApiOperation({ summary: "Lock cost version" })
  async lockCostVersion(@Param("id") id: string) {
    try { return await this.costingEngine.lockCostVersion(id); }
    catch (e) { handleError(e); }
  }

  // ─── Work Centers ──────────────────────────────────────────────────────────

  @Post("work-centers")
  @ApiOperation({ summary: "Create work center" })
  async createWorkCenter(@Body() dto: CreateWorkCenterDto) {
    try { return await this.costingEngine.createWorkCenter(dto); }
    catch (e) { handleError(e); }
  }

  // ─── BOM ───────────────────────────────────────────────────────────────────

  @Post("boms")
  @ApiOperation({ summary: "Create BOM" })
  async createBom(@Body() dto: CreateBomDto) {
    try { return await this.costingEngine.createBom(dto); }
    catch (e) { handleError(e); }
  }

  @Post("boms/:id/lines")
  @ApiOperation({ summary: "Add BOM line" })
  async addBomLine(@Param("id") id: string, @Body() dto: AddBomLineDto) {
    try { return await this.costingEngine.addBomLine(id, dto); }
    catch (e) { handleError(e); }
  }

  @Post("boms/:id/routings")
  @ApiOperation({ summary: "Add BOM routing operation" })
  async addBomRouting(@Param("id") id: string, @Body() dto: AddBomRoutingDto) {
    try { return await this.costingEngine.addBomRouting(id, dto); }
    catch (e) { handleError(e); }
  }

  @Get("boms/:id/cost")
  @ApiOperation({ summary: "Calculate BOM cost" })
  async calculateBomCost(@Param("id") id: string) {
    try { return await this.costingEngine.calculateBomCost(id); }
    catch (e) { handleError(e); }
  }

  @Post("boms/:id/rollup")
  @ApiOperation({ summary: "Roll up BOM cost from components" })
  async rollUpCost(@Param("id") id: string) {
    try { return await this.costingEngine.rollUpCost(id); }
    catch (e) { handleError(e); }
  }

  // ─── Production Orders ─────────────────────────────────────────────────────

  @Post("production-orders")
  @ApiOperation({ summary: "Create production order" })
  async createProductionOrder(@Body() dto: CreateProductionOrderDto) {
    try { return await this.costingEngine.createProductionOrder(dto); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/load-bom/:bomId")
  @ApiOperation({ summary: "Load BOM into production order" })
  async loadBomToOrder(@Param("id") id: string, @Param("bomId") bomId: string) {
    try { return await this.costingEngine.loadBomToOrder(id, bomId); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/release")
  @ApiOperation({ summary: "Release production order" })
  async releaseOrder(@Param("id") id: string) {
    try { return await this.costingEngine.releaseProductionOrder(id, "system"); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/issue-component")
  @ApiOperation({ summary: "Issue component to production" })
  async issueComponent(@Param("id") id: string, @Body() dto: IssueComponentDto) {
    try { return await this.costingEngine.issueComponent(id, dto.componentId, dto.quantity, dto.unitCost); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/complete-operation")
  @ApiOperation({ summary: "Complete production operation" })
  async completeOperation(@Param("id") id: string, @Body() dto: CompleteOperationDto) {
    try { return await this.costingEngine.completeOperation(id, dto.operationId, dto.actualSetupTime, dto.actualRunTime); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/complete")
  @ApiOperation({ summary: "Complete production order" })
  async completeOrder(@Param("id") id: string) {
    try { return await this.costingEngine.completeProductionOrder(id, "system"); }
    catch (e) { handleError(e); }
  }

  @Post("production-orders/:id/close")
  @ApiOperation({ summary: "Close production order" })
  async closeOrder(@Param("id") id: string) {
    try { return await this.costingEngine.closeProductionOrder(id, "system"); }
    catch (e) { handleError(e); }
  }

  // ─── Cost Pools ────────────────────────────────────────────────────────────

  @Post("cost-pools")
  @ApiOperation({ summary: "Create cost pool" })
  async createCostPool(@Body() dto: CreateCostPoolDto) {
    try { return await this.allocationEngine.createCostPool(dto); }
    catch (e) { handleError(e); }
  }

  // ─── Allocation Rules ──────────────────────────────────────────────────────

  @Post("allocation-rules")
  @ApiOperation({ summary: "Create allocation rule" })
  async createAllocationRule(@Body() dto: CreateAllocationRuleDto) {
    try { return await this.allocationEngine.createAllocationRule(dto); }
    catch (e) { handleError(e); }
  }

  @Post("allocation-rules/execute/:periodId")
  @ApiOperation({ summary: "Execute cost allocations for period" })
  async executeAllocation(@Param("periodId") periodId: string) {
    try { return await this.allocationEngine.executeAllocation(periodId); }
    catch (e) { handleError(e); }
  }

  // ─── Overhead Rates ────────────────────────────────────────────────────────

  @Post("overhead-rates")
  @ApiOperation({ summary: "Create overhead rate" })
  async createOverheadRate(@Body() dto: CreateOverheadRateDto) {
    try { return await this.allocationEngine.createOverheadRate(dto); }
    catch (e) { handleError(e); }
  }

  // ─── Cost Snapshots ────────────────────────────────────────────────────────

  @Post("cost-snapshots")
  @ApiOperation({ summary: "Create cost snapshot" })
  async createCostSnapshot(@Body() dto: CreateCostSnapshotDto) {
    try { return await this.allocationEngine.createCostSnapshot(dto); }
    catch (e) { handleError(e); }
  }

  @Post("cost-snapshots/:id/freeze")
  @ApiOperation({ summary: "Freeze cost snapshot" })
  async freezeSnapshot(@Param("id") id: string) {
    try { return await this.allocationEngine.freezeSnapshot(id, "system"); }
    catch (e) { handleError(e); }
  }

  // ─── Period Close ──────────────────────────────────────────────────────────

  @Post("period-close")
  @ApiOperation({ summary: "Execute period close" })
  async executePeriodClose(
    @Body() p: { periodId: string; fiscalYearId: string; closeType?: string },
  ) {
    try { return await this.periodClose.executePeriodClose(p.periodId, p.fiscalYearId, p.closeType); }
    catch (e) { handleError(e); }
  }

  // ─── Query ─────────────────────────────────────────────────────────────────

  @Get("overhead-absorption/:orderId")
  @ApiOperation({ summary: "Calculate overhead absorption" })
  async calculateOverhead(@Param("orderId") orderId: string) {
    try { return await this.allocationEngine.calculateOverheadAbsorption(orderId); }
    catch (e) { handleError(e); }
  }
}
