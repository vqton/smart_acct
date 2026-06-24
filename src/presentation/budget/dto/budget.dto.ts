import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsNumber, IsBoolean, IsDateString, Min, Max, IsEnum } from "class-validator";

// ─── Budget Plan DTOs ─────────────────────────────────────────────────────────

export class CreateBudgetPlanDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() budgetType!: string;
  @ApiProperty() @IsString() fiscalYearId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() currencyCode?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() startDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() endDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() isTemplate?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsString() parentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

export class UpdateBudgetPlanDto {
  @ApiPropertyOptional() @IsOptional() @IsString() name?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() startDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() endDate?: string;
}

export class AdjustBudgetAmountDto {
  @ApiProperty() @IsNumber() amount!: number;
}

// ─── Budget Version DTOs ──────────────────────────────────────────────────────

export class CreateBudgetVersionDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsNumber() versionNumber!: number;
  @ApiProperty() @IsString() label!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() totalAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
}

export class CloneVersionDto {
  @ApiProperty() @IsNumber() newVersionNumber!: number;
  @ApiProperty() @IsString() label!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

// ─── Budget Detail DTOs ───────────────────────────────────────────────────────

export class CreateBudgetDetailDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() glAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() departmentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() projectId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() productId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() customerId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() supplierId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() originalAmount?: number;
}

export class UpdateDetailAmountDto {
  @ApiProperty() @IsNumber() amount!: number;
}

export class SetDetailPeriodDto {
  @ApiProperty() @IsNumber() period!: number;
  @ApiProperty() @IsNumber() amount!: number;
}

// ─── Scenario DTOs ────────────────────────────────────────────────────────────

export class CreateScenarioDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() scenarioType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() assumptions?: string;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() isBase?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsNumber() confidencePct?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() weightPct?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

// ─── Forecast DTOs ────────────────────────────────────────────────────────────

export class CreateForecastDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsString() forecastNumber!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() forecastMethod?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() scenarioId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() forecastPeriods?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() periodType?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() startDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() endDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() totalForecastAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() confidencePct?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

export class AddForecastLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() glAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() departmentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() projectId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() forecastAmount?: number;
}

export class AddForecastDriverDto {
  @ApiProperty() @IsString() driverName!: string;
  @ApiProperty() @IsString() driverType!: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() baseValue?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() growthRate?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() seasonalFactor?: number;
}

export class RollingForecastDto {
  @ApiProperty() @IsString() newForecastNumber!: string;
  @ApiProperty() @IsNumber() additionalPeriods!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

// ─── Allocation DTOs ──────────────────────────────────────────────────────────

export class CreateAllocationRuleDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() allocationMethod?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceBudgetPlanId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() targetBudgetPlanId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() totalAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() fiscalYearId?: string;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() isRecurring?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

export class AddAllocationLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceGlAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() targetGlAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceCostCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() targetCostCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() allocationPct?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() allocationAmount?: number;
}

export class ExecuteAllocationDto {
  @ApiPropertyOptional() @IsOptional() @IsString() periodId?: string;
}

// ─── Control DTOs ─────────────────────────────────────────────────────────────

export class CreateBudgetControlDto {
  @ApiProperty() @IsString() budgetDetailId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() controlLevel?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() controlAction?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() toleranceAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() tolerancePct?: number;
  @ApiPropertyOptional() @IsOptional() @IsDateString() effectiveFrom?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() effectiveTo?: string;
}

export class CheckBudgetDto {
  @ApiProperty() @IsString() budgetDetailId!: string;
  @ApiProperty() @IsNumber() requestedAmount!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() checkedById?: string;
}

// ─── Reservation DTOs ─────────────────────────────────────────────────────────

export class CreateReservationDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsString() reservationNumber!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() commitmentType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceDocumentType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceDocumentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiProperty() @IsNumber() totalAmount!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() currencyCode?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() expiresAt?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

export class ConsumeReservationDto {
  @ApiProperty() @IsNumber() amount!: number;
}

export class ReleaseReservationDto {
  @ApiProperty() @IsNumber() amount!: number;
}

export class CancelReservationDto {
  @ApiProperty() @IsString() reason!: string;
}

export class AddReservationLineDto {
  @ApiProperty() @IsString() budgetDetailId!: string;
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() glAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() departmentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() projectId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() periodNumber?: number;
}

// ─── Transfer DTOs ───────────────────────────────────────────────────────────

export class CreateTransferDto {
  @ApiProperty() @IsString() transferNumber!: string;
  @ApiProperty() @IsString() sourceBudgetPlanId!: string;
  @ApiProperty() @IsString() targetBudgetPlanId!: string;
  @ApiProperty() @IsNumber() totalAmount!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() effectiveDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

// ─── Approval DTOs ────────────────────────────────────────────────────────────

export class CreateApprovalRequestDto {
  @ApiProperty() @IsString() budgetPlanId!: string;
  @ApiProperty() @IsString() requestNumber!: string;
  @ApiProperty() @IsNumber() totalAmount!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() requestedById?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
}

export class AddApprovalStepDto {
  @ApiProperty() @IsNumber() stepOrder!: number;
  @ApiProperty() @IsString() approverId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() delegateId?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() slaDeadline?: string;
}

export class AddApprovalStepsBulkDto {
  @ApiProperty({ type: [AddApprovalStepDto] }) steps!: AddApprovalStepDto[];
}

export class ProcessStepDto {
  @ApiProperty() @IsString() decision!: string;
  @ApiProperty() @IsString() approverId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() comments?: string;
}
