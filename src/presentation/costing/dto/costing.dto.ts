import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsNumber, IsBoolean, IsDateString, Min, Max, IsEnum } from "class-validator";

// ─── Cost Version ───────────────────────────────────────────────────────────

export class CreateCostVersionDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() costMethod!: string;
  @ApiProperty() @IsString() fiscalYearId!: string;
  @ApiProperty() @IsDateString() effectiveFrom!: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() effectiveTo?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
}

// ─── Work Center ────────────────────────────────────────────────────────────

export class CreateWorkCenterDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() workCenterType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() departmentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() hourlyRate?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() machineRate?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() overheadRate?: number;
}

// ─── BOM ────────────────────────────────────────────────────────────────────

export class CreateBomDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() quantity?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() uom?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() effectiveFrom?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
}

export class AddBomLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() componentItemId!: string;
  @ApiProperty() @IsString() componentCode!: string;
  @ApiProperty() @IsString() componentName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() uom?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costElement?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() unitCost?: number;
}

export class AddBomRoutingDto {
  @ApiProperty() @IsNumber() operationSeq!: number;
  @ApiProperty() @IsString() operationDescription!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() workCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() setupTime?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() runTime?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() laborRate?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() machineRate?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() overheadRate?: number;
}

// ─── Production Orders ──────────────────────────────────────────────────────

export class CreateProductionOrderDto {
  @ApiProperty() @IsString() orderNumber!: string;
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsDateString() plannedStartDate!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() bomId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() workCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() warehouseId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() estimatedMaterialCost?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() estimatedLaborCost?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() estimatedMachineCost?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() estimatedOverheadCost?: number;
}

export class IssueComponentDto {
  @ApiProperty() @IsString() componentId!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsNumber() unitCost!: number;
}

export class CompleteOperationDto {
  @ApiProperty() @IsString() operationId!: string;
  @ApiProperty() @IsNumber() actualSetupTime!: number;
  @ApiProperty() @IsNumber() actualRunTime!: number;
}

// ─── Cost Pools ─────────────────────────────────────────────────────────────

export class CreateCostPoolDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() poolType!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() totalAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() fiscalYearId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() periodId?: string;
}

// ─── Allocation Rules ───────────────────────────────────────────────────────

export class CreateAllocationRuleDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() poolId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() sourceCostCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() targetCostCenterId?: string;
  @ApiProperty() @IsString() allocationMethod!: string;
  @ApiProperty() @IsString() allocationBasis!: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() basisValue?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() percentage?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() fixedAmount?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() priority?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() fiscalYearId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() periodId?: string;
}

// ─── Overhead Rates ─────────────────────────────────────────────────────────

export class CreateOverheadRateDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() costPoolType!: string;
  @ApiProperty() @IsString() allocationBasis!: string;
  @ApiProperty() @IsNumber() rate!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() rateType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() workCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costCenterId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() fiscalYearId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() costVersionId?: string;
}

// ─── Cost Snapshots ─────────────────────────────────────────────────────────

export class CreateCostSnapshotDto {
  @ApiProperty() @IsString() snapshotNumber!: string;
  @ApiProperty() @IsString() snapshotType!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() periodId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() fiscalYearId?: string;
}
