import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { BudgetEngineService } from "../../application/budget/budget-engine-service.js";
import { ForecastEngineService } from "../../application/budget/forecast-engine-service.js";
import { AllocationEngineService } from "../../application/budget/allocation-engine-service.js";
import { ControlEngineService } from "../../application/budget/control-engine-service.js";
import { ApprovalEngineService } from "../../application/budget/approval-engine-service.js";
import { PrismaBgtBudgetPlanRepository, PrismaBgtTransferRepository } from "../../infrastructure/budget/budget-prisma-repos.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateBudgetPlanDto, UpdateBudgetPlanDto, AdjustBudgetAmountDto,
  CreateBudgetVersionDto, CloneVersionDto,
  CreateBudgetDetailDto, UpdateDetailAmountDto, SetDetailPeriodDto,
  CreateScenarioDto,
  CreateForecastDto, AddForecastLineDto, AddForecastDriverDto, RollingForecastDto,
  CreateAllocationRuleDto, AddAllocationLineDto, ExecuteAllocationDto,
  CreateBudgetControlDto, CheckBudgetDto,
  CreateReservationDto, ConsumeReservationDto, ReleaseReservationDto,
  CancelReservationDto, AddReservationLineDto,
  CreateTransferDto,
  CreateApprovalRequestDto, AddApprovalStepDto, AddApprovalStepsBulkDto, ProcessStepDto,
} from "./dto/budget.dto.js";
import { BgtBudgetPlanId } from "../../domain/budget/bgt-ids.js";
import { BgtBudgetTransfer } from "../../domain/budget/bgt-transfer.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) {
    if (e.kind === "NotFound") throw new NotFoundException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}

@ApiTags("Budget")
@Controller("api/budget")
export class BudgetController {
  constructor(
    private readonly budgetEngine: BudgetEngineService,
    private readonly forecastEngine: ForecastEngineService,
    private readonly allocationEngine: AllocationEngineService,
    private readonly controlEngine: ControlEngineService,
    private readonly approvalEngine: ApprovalEngineService,
    private readonly planRepo: PrismaBgtBudgetPlanRepository,
    private readonly transferRepo: PrismaBgtTransferRepository,
  ) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET PLANS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("plans")
  @ApiOperation({ summary: "Create budget plan" })
  async createPlan(@Body() dto: CreateBudgetPlanDto) {
    try { return (await this.budgetEngine.createPlan({ ...dto, startDate: dto.startDate ? new Date(dto.startDate) : undefined, endDate: dto.endDate ? new Date(dto.endDate) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("plans")
  @ApiOperation({ summary: "List budget plans" })
  async listPlans(
    @Query("fiscalYearId") fiscalYearId?: string,
    @Query("status") status?: string,
    @Query("type") type?: string,
  ) {
    return (await this.budgetEngine.listPlans(fiscalYearId, status, type)).map(p => p.toState());
  }

  @Get("plans/:id")
  @ApiOperation({ summary: "Get budget plan" })
  async getPlan(@Param("id") id: string) {
    const plan = await this.budgetEngine.getPlan(id);
    if (!plan) throw new NotFoundException("Budget plan not found");
    return plan.toState();
  }

  @Put("plans/:id")
  @ApiOperation({ summary: "Update budget plan" })
  async updatePlan(@Param("id") id: string, @Body() dto: UpdateBudgetPlanDto) {
    try { return (await this.budgetEngine.updatePlan(id, { ...dto, startDate: dto.startDate ? new Date(dto.startDate) : undefined, endDate: dto.endDate ? new Date(dto.endDate) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Workflow ────────────────────────────────────────────────────────────

  @Post("plans/:id/submit")
  @ApiOperation({ summary: "Submit budget plan for approval" })
  async submitPlan(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.submitPlan(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/review")
  @ApiOperation({ summary: "Move to review" })
  async reviewPlan(@Param("id") id: string) {
    try { return (await this.budgetEngine.reviewPlan(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/approve")
  @ApiOperation({ summary: "Approve budget plan" })
  async approvePlan(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.approvePlan(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/reject")
  @ApiOperation({ summary: "Reject budget plan" })
  async rejectPlan(@Param("id") id: string, @Body("userId") userId: string, @Body("reason") reason: string) {
    try { return (await this.budgetEngine.rejectPlan(id, userId || "system", reason || "Rejected")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/revise")
  @ApiOperation({ summary: "Send back for revision" })
  async revisePlan(@Param("id") id: string) {
    try { return (await this.budgetEngine.revisePlan(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/publish")
  @ApiOperation({ summary: "Publish budget plan" })
  async publishPlan(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.publishPlan(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/activate")
  @ApiOperation({ summary: "Activate budget plan" })
  async activatePlan(@Param("id") id: string) {
    try { return (await this.budgetEngine.activatePlan(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/freeze")
  @ApiOperation({ summary: "Freeze budget plan" })
  async freezePlan(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.freezePlan(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/close")
  @ApiOperation({ summary: "Close budget plan" })
  async closePlan(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.closePlan(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/reopen")
  @ApiOperation({ summary: "Reopen budget plan" })
  async reopenPlan(@Param("id") id: string) {
    try { return (await this.budgetEngine.reopenPlan(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("plans/:id/adjust")
  @ApiOperation({ summary: "Adjust total planned amount" })
  async adjustPlan(@Param("id") id: string, @Body() dto: AdjustBudgetAmountDto) {
    try { return (await this.budgetEngine.adjustPlanAmount(id, dto.amount)).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET VERSIONS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("versions")
  @ApiOperation({ summary: "Create budget version" })
  async createVersion(@Body() dto: CreateBudgetVersionDto) {
    try { return (await this.budgetEngine.createVersion(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("plans/:planId/versions")
  @ApiOperation({ summary: "List versions for budget plan" })
  async getVersions(@Param("planId") planId: string) {
    return (await this.budgetEngine.getVersions(planId)).map(v => v.toState());
  }

  @Post("versions/:id/approve")
  @ApiOperation({ summary: "Approve version" })
  async approveVersion(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.budgetEngine.approveVersion(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("versions/:id/freeze")
  @ApiOperation({ summary: "Freeze version" })
  async freezeVersion(@Param("id") id: string) {
    try { return (await this.budgetEngine.freezeVersion(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("versions/:id/clone")
  @ApiOperation({ summary: "Clone version" })
  async cloneVersion(@Param("id") id: string, @Body() dto: CloneVersionDto) {
    try { return (await this.budgetEngine.cloneVersion(id, dto.newVersionNumber, dto.label, dto.createdById)).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET DETAILS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("details")
  @ApiOperation({ summary: "Create budget detail line" })
  async createDetail(@Body() dto: CreateBudgetDetailDto) {
    try { return (await this.budgetEngine.createDetail(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("plans/:planId/details")
  @ApiOperation({ summary: "List details for budget plan" })
  async getDetails(@Param("planId") planId: string) {
    return (await this.budgetEngine.getDetails(planId)).map(d => d.toState());
  }

  @Get("details/:id")
  @ApiOperation({ summary: "Get budget detail" })
  async getDetail(@Param("id") id: string) {
    const detail = await this.budgetEngine.getDetail(id);
    if (!detail) throw new NotFoundException("Budget detail not found");
    return detail.toState();
  }

  @Put("details/:id/amount")
  @ApiOperation({ summary: "Update detail amount" })
  async updateDetailAmount(@Param("id") id: string, @Body() dto: UpdateDetailAmountDto) {
    try { return (await this.budgetEngine.updateDetailAmount(id, dto.amount)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("details/:id/period")
  @ApiOperation({ summary: "Set period amount" })
  async setDetailPeriod(@Param("id") id: string, @Body() dto: SetDetailPeriodDto) {
    try { return (await this.budgetEngine.setDetailPeriod(id, dto.period, dto.amount)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("details/:id/delete")
  @ApiOperation({ summary: "Delete budget detail" })
  async deleteDetail(@Param("id") id: string) {
    try { await this.budgetEngine.deleteDetail(id); return { deleted: true }; }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET SCENARIOS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("scenarios")
  @ApiOperation({ summary: "Create budget scenario" })
  async createScenario(@Body() dto: CreateScenarioDto) {
    try { return (await this.forecastEngine.createScenario(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("plans/:planId/scenarios")
  @ApiOperation({ summary: "List scenarios for budget plan" })
  async getScenarios(@Param("planId") planId: string) {
    return (await this.forecastEngine.getScenarios(planId)).map(s => s.toState());
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // FORECASTS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("forecasts")
  @ApiOperation({ summary: "Create forecast" })
  async createForecast(@Body() dto: CreateForecastDto) {
    try { return (await this.forecastEngine.createForecast({ ...dto, startDate: dto.startDate ? new Date(dto.startDate) : undefined, endDate: dto.endDate ? new Date(dto.endDate) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("forecasts")
  @ApiOperation({ summary: "List forecasts" })
  async listForecasts(
    @Query("budgetPlanId") budgetPlanId?: string,
    @Query("status") status?: string,
  ) {
    return (await this.forecastEngine.listForecasts(budgetPlanId, status)).map(f => f.toState());
  }

  @Get("forecasts/:id")
  @ApiOperation({ summary: "Get forecast" })
  async getForecast(@Param("id") id: string) {
    const forecast = await this.forecastEngine.getForecast(id);
    if (!forecast) throw new NotFoundException("Forecast not found");
    return forecast.toState();
  }

  @Post("forecasts/:id/submit")
  @ApiOperation({ summary: "Submit forecast" })
  async submitForecast(@Param("id") id: string) {
    try { return (await this.forecastEngine.submitForecast(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("forecasts/:id/approve")
  @ApiOperation({ summary: "Approve forecast" })
  async approveForecast(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.forecastEngine.approveForecast(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("forecasts/:id/publish")
  @ApiOperation({ summary: "Publish forecast" })
  async publishForecast(@Param("id") id: string) {
    try { return (await this.forecastEngine.publishForecast(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("forecasts/:id/lines")
  @ApiOperation({ summary: "Add forecast line" })
  async addForecastLine(@Param("id") id: string, @Body() dto: AddForecastLineDto) {
    try { return (await this.forecastEngine.addForecastLine(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("forecasts/:id/drivers")
  @ApiOperation({ summary: "Add forecast driver" })
  async addForecastDriver(@Param("id") id: string, @Body() dto: AddForecastDriverDto) {
    try { return (await this.forecastEngine.addForecastDriver(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("forecasts/:id/rolling")
  @ApiOperation({ summary: "Generate rolling forecast" })
  async generateRolling(@Param("id") id: string, @Body() dto: RollingForecastDto) {
    try { return (await this.forecastEngine.generateRollingForecast(id, dto.newForecastNumber, dto.additionalPeriods, dto.createdById)).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // ALLOCATION RULES
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("allocations")
  @ApiOperation({ summary: "Create allocation rule" })
  async createAllocation(@Body() dto: CreateAllocationRuleDto) {
    try { return (await this.allocationEngine.createRule(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("allocations")
  @ApiOperation({ summary: "List allocation rules" })
  async listAllocations(@Query("status") status?: string) {
    return (await this.allocationEngine.listRules(status)).map(r => r.toState());
  }

  @Get("allocations/:id")
  @ApiOperation({ summary: "Get allocation rule" })
  async getAllocation(@Param("id") id: string) {
    const rule = await this.allocationEngine.getRule(id);
    if (!rule) throw new NotFoundException("Allocation rule not found");
    return rule.toState();
  }

  @Post("allocations/:id/lines")
  @ApiOperation({ summary: "Add allocation rule line" })
  async addAllocationLine(@Param("id") id: string, @Body() dto: AddAllocationLineDto) {
    try { return (await this.allocationEngine.addRuleLine(id, { ...dto, ruleId: id })).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("allocations/:id/execute")
  @ApiOperation({ summary: "Execute allocation rule" })
  async executeAllocation(@Param("id") id: string, @Body() dto: ExecuteAllocationDto) {
    try { return (await this.allocationEngine.executeRule(id, dto.periodId)).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET CONTROL
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("controls")
  @ApiOperation({ summary: "Create budget control" })
  async createControl(@Body() dto: CreateBudgetControlDto) {
    try { return (await this.controlEngine.createControl({ ...dto, effectiveFrom: dto.effectiveFrom ? new Date(dto.effectiveFrom) : undefined, effectiveTo: dto.effectiveTo ? new Date(dto.effectiveTo) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("controls/check")
  @ApiOperation({ summary: "Check budget availability" })
  async checkBudget(@Body() dto: CheckBudgetDto) {
    try { return await this.controlEngine.checkBudget(dto.budgetDetailId, dto.requestedAmount, dto.checkedById); }
    catch (e) { handleError(e); }
  }

  @Put("controls/:id")
  @ApiOperation({ summary: "Update budget control" })
  async updateControl(@Param("id") id: string, @Body() dto: CreateBudgetControlDto) {
    try { return (await this.controlEngine.updateControl(id, { ...dto, effectiveFrom: dto.effectiveFrom ? new Date(dto.effectiveFrom) : undefined, effectiveTo: dto.effectiveTo ? new Date(dto.effectiveTo) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // RESERVATIONS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("reservations")
  @ApiOperation({ summary: "Create budget reservation" })
  async createReservation(@Body() dto: CreateReservationDto) {
    try { return (await this.controlEngine.createReservation({ ...dto, expiresAt: dto.expiresAt ? new Date(dto.expiresAt) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("reservations")
  @ApiOperation({ summary: "List reservations" })
  async listReservations(
    @Query("budgetPlanId") budgetPlanId?: string,
    @Query("status") status?: string,
  ) {
    return (await this.controlEngine.listReservations(budgetPlanId, status)).map(r => r.toState());
  }

  @Get("reservations/:id")
  @ApiOperation({ summary: "Get reservation" })
  async getReservation(@Param("id") id: string) {
    const resv = await this.controlEngine.getReservation(id);
    if (!resv) throw new NotFoundException("Reservation not found");
    return resv.toState();
  }

  @Post("reservations/:id/activate")
  @ApiOperation({ summary: "Activate reservation" })
  async activateReservation(@Param("id") id: string) {
    try { return (await this.controlEngine.activateReservation(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("reservations/:id/consume")
  @ApiOperation({ summary: "Consume reservation" })
  async consumeReservation(@Param("id") id: string, @Body() dto: ConsumeReservationDto) {
    try { return (await this.controlEngine.consumeReservation(id, dto.amount)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("reservations/:id/release")
  @ApiOperation({ summary: "Release reservation" })
  async releaseReservation(@Param("id") id: string, @Body() dto: ReleaseReservationDto) {
    try { return (await this.controlEngine.releaseReservation(id, dto.amount)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("reservations/:id/cancel")
  @ApiOperation({ summary: "Cancel reservation" })
  async cancelReservation(@Param("id") id: string, @Body() dto: CancelReservationDto) {
    try { await this.controlEngine.cancelReservation(id, dto.reason); return { cancelled: true }; }
    catch (e) { handleError(e); }
  }

  @Post("reservations/:id/lines")
  @ApiOperation({ summary: "Add reservation line" })
  async addReservationLine(@Param("id") id: string, @Body() dto: AddReservationLineDto) {
    try { return (await this.controlEngine.addReservationLine(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUDGET TRANSFERS
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("transfers")
  @ApiOperation({ summary: "Create budget transfer" })
  async createTransfer(@Body() dto: CreateTransferDto) {
    try {
      const srcPlan = await this.planRepo.findById(BgtBudgetPlanId.from(dto.sourceBudgetPlanId));
      if (!srcPlan) throw new BadRequestException("Source budget plan not found");
      const tgtPlan = await this.planRepo.findById(BgtBudgetPlanId.from(dto.targetBudgetPlanId));
      if (!tgtPlan) throw new BadRequestException("Target budget plan not found");
      const transfer = BgtBudgetTransfer.create({
        ...dto, effectiveDate: dto.effectiveDate ? new Date(dto.effectiveDate) : undefined,
      });
      await this.transferRepo.save(transfer);
      return transfer.toState();
    } catch (e) { handleError(e); }
  }

  @Post("transfers/:id/submit")
  @ApiOperation({ summary: "Submit budget transfer" })
  async submitTransfer(@Param("id") id: string) {
    try {
      const transfer = await this.transferRepo.findById(id);
      if (!transfer) throw new NotFoundException("Transfer not found");
      transfer.submit();
      await this.transferRepo.save(transfer);
      return transfer.toState();
    } catch (e) { handleError(e); }
  }

  @Post("transfers/:id/approve")
  @ApiOperation({ summary: "Approve budget transfer" })
  async approveTransfer(@Param("id") id: string, @Body("userId") userId: string) {
    try {
      const transfer = await this.transferRepo.findById(id);
      if (!transfer) throw new NotFoundException("Transfer not found");
      transfer.approve(userId || "system");
      await this.transferRepo.save(transfer);
      return transfer.toState();
    } catch (e) { handleError(e); }
  }

  @Post("transfers/:id/complete")
  @ApiOperation({ summary: "Complete budget transfer" })
  async completeTransfer(@Param("id") id: string) {
    try {
      const transfer = await this.transferRepo.findById(id);
      if (!transfer) throw new NotFoundException("Transfer not found");
      transfer.complete();
      await this.transferRepo.save(transfer);
      return transfer.toState();
    } catch (e) { handleError(e); }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // APPROVAL WORKFLOW
  // ═══════════════════════════════════════════════════════════════════════════

  @Post("approvals")
  @ApiOperation({ summary: "Create approval request" })
  async createApproval(@Body() dto: CreateApprovalRequestDto) {
    try { return (await this.approvalEngine.createRequest(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("approvals")
  @ApiOperation({ summary: "List approval requests" })
  async listApprovals(
    @Query("budgetPlanId") budgetPlanId?: string,
    @Query("status") status?: string,
  ) {
    return (await this.approvalEngine.listRequests(budgetPlanId, status)).map(r => r.toState());
  }

  @Get("approvals/:id")
  @ApiOperation({ summary: "Get approval request" })
  async getApproval(@Param("id") id: string) {
    const req = await this.approvalEngine.getRequest(id);
    if (!req) throw new NotFoundException("Approval request not found");
    return req.toState();
  }

  @Get("approvals/pending/:approverId")
  @ApiOperation({ summary: "Get pending approvals for approver" })
  async getPendingApprovals(@Param("approverId") approverId: string) {
    return (await this.approvalEngine.getPendingForApprover(approverId)).map(r => r.toState());
  }

  @Post("approvals/:id/steps")
  @ApiOperation({ summary: "Add approval step" })
  async addApprovalStep(@Param("id") id: string, @Body() dto: AddApprovalStepDto) {
    try { return (await this.approvalEngine.addStep(id, { ...dto, approvalRequestId: id, slaDeadline: dto.slaDeadline ? new Date(dto.slaDeadline) : undefined })).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("approvals/:id/steps/bulk")
  @ApiOperation({ summary: "Add multiple approval steps" })
  async addApprovalStepsBulk(@Param("id") id: string, @Body() dto: AddApprovalStepsBulkDto) {
    try {
      const steps = dto.steps.map(s => ({ ...s, approvalRequestId: id, slaDeadline: s.slaDeadline ? new Date(s.slaDeadline) : undefined }));
      return (await this.approvalEngine.addStepsBulk(id, steps)).toState();
    } catch (e) { handleError(e); }
  }

  @Post("approvals/:id/process")
  @ApiOperation({ summary: "Process approval step" })
  async processStep(@Param("id") id: string, @Body() dto: ProcessStepDto) {
    try { return (await this.approvalEngine.processStep(id, 0, dto.decision, dto.approverId, dto.comments)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("approvals/:id/process/:stepOrder")
  @ApiOperation({ summary: "Process specific approval step" })
  async processStepAt(@Param("id") id: string, @Param("stepOrder") stepOrder: string, @Body() dto: ProcessStepDto) {
    try { return (await this.approvalEngine.processStep(id, parseInt(stepOrder), dto.decision, dto.approverId, dto.comments)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("approvals/:id/resubmit")
  @ApiOperation({ summary: "Resubmit approval request" })
  async resubmitApproval(@Param("id") id: string) {
    try { return (await this.approvalEngine.resubmitRequest(id)).toState(); }
    catch (e) { handleError(e); }
  }
}
