import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsNumber, IsBoolean, IsDateString, IsOptional, MaxLength, Min, IsEnum } from "class-validator";
import {
  FaAssetType, FaAssetStatus, FaAcquisitionType, FaDepreciationMethod,
  FaDepreciationArea, FaDisposalType, FaRevaluationType, FaImpairmentType,
  FaLeaseType, FaLeasePaymentFrequency, FaMaintenanceType,
  FaVerificationMethod, FaVerificationStatus,
} from "../../../domain/fa/fa-enums.js";

// ─── Group ────────────────────────────────────────────────────────────────────────

export class CreateAssetGroupDto {
  @ApiProperty() @IsString() @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MaxLength(255) name!: string;
  @ApiProperty({ enum: FaAssetType }) @IsEnum(FaAssetType) assetType!: FaAssetType;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() parentId?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() usefulLifeMin?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() usefulLifeMax?: number;
  @ApiPropertyOptional({ enum: FaDepreciationMethod }) @IsEnum(FaDepreciationMethod) @IsOptional() depreciationMethod?: FaDepreciationMethod;
}

export class UpdateAssetGroupDto {
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isActive?: boolean;
}

// ─── Class ────────────────────────────────────────────────────────────────────────

export class CreateAssetClassDto {
  @ApiProperty() @IsString() @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MaxLength(255) name!: string;
  @ApiProperty({ enum: FaAssetType }) @IsEnum(FaAssetType) assetType!: FaAssetType;
  @ApiPropertyOptional() @IsString() @IsOptional() groupId?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() usefulLifeYears?: number;
  @ApiPropertyOptional({ enum: FaDepreciationMethod }) @IsEnum(FaDepreciationMethod) @IsOptional() depreciationMethod?: FaDepreciationMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() glAssetAccountId?: string;
}

// ─── Asset ────────────────────────────────────────────────────────────────────────

export class CreateAssetDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() @MaxLength(50) assetCode!: string;
  @ApiProperty() @IsString() @MaxLength(255) assetName!: string;
  @ApiProperty({ enum: FaAssetType }) @IsEnum(FaAssetType) assetType!: FaAssetType;
  @ApiProperty({ enum: FaDepreciationMethod }) @IsEnum(FaDepreciationMethod) depreciationMethod!: FaDepreciationMethod;
  @ApiProperty() @IsNumber() @Min(0) usefulLifeYears!: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() usefulLifeMonths?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() groupId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() classId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() serialNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() custodianId?: string;
}

export class AcquireAssetDto {
  @ApiProperty({ enum: FaAcquisitionType }) @IsEnum(FaAcquisitionType) acquisitionType!: FaAcquisitionType;
  @ApiProperty() @IsDateString() acquisitionDate!: string;
  @ApiProperty() @IsNumber() @Min(0) originalCost!: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() residualValue?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() supplierName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() poNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() invoiceNumber?: string;
}

export class TransferAssetDto {
  @ApiProperty() @IsString() transferNumber!: string;
  @ApiProperty() @IsDateString() transferDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toBranchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toCostCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toDepartmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toLocationId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toCustodianId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toCustodianName?: string;
}

export class DisposeAssetDto {
  @ApiProperty() @IsString() disposalNumber!: string;
  @ApiProperty({ enum: FaDisposalType }) @IsEnum(FaDisposalType) disposalType!: FaDisposalType;
  @ApiProperty() @IsDateString() disposalDate!: string;
  @ApiProperty() @IsNumber() @Min(0) proceeds!: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() costs?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() reason?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerName?: string;
}

export class RevalueAssetDto {
  @ApiProperty() @IsString() revaluationNumber!: string;
  @ApiProperty({ enum: FaRevaluationType }) @IsEnum(FaRevaluationType) revaluationType!: FaRevaluationType;
  @ApiProperty() @IsDateString() revaluationDate!: string;
  @ApiProperty() @IsNumber() newValue!: number;
}

export class ImpairAssetDto {
  @ApiProperty() @IsString() impairmentNumber!: string;
  @ApiProperty({ enum: FaImpairmentType }) @IsEnum(FaImpairmentType) impairmentType!: FaImpairmentType;
  @ApiProperty() @IsDateString() impairmentDate!: string;
  @ApiProperty() @IsNumber() @Min(0) carryingAmount!: number;
  @ApiProperty() @IsNumber() @Min(0) recoverableAmount!: number;
}

export class UpdateAssetDto {
  @ApiPropertyOptional() @IsString() @IsOptional() assetName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() custodianId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() locationId?: string;
}

// ─── CIP ──────────────────────────────────────────────────────────────────────────

export class CreateCipProjectDto {
  @ApiProperty() @IsString() @MaxLength(50) projectCode!: string;
  @ApiProperty() @IsString() @MaxLength(255) projectName!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsDateString() startDate!: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() totalBudget?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectType?: string;
}

export class AddCipCostDto {
  @ApiProperty() @IsDateString() costDate!: string;
  @ApiProperty() @IsNumber() @Min(0) amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costType?: string;
}

export class CapitalizeCipDto {
  @ApiProperty() @IsString() assetId!: string;
  @ApiProperty() @IsNumber() @Min(0) amount!: number;
}

// ─── Depreciation ─────────────────────────────────────────────────────────────────

export class RunDepreciationDto {
  @ApiProperty() @IsString() runNumber!: string;
  @ApiProperty({ enum: FaDepreciationArea }) @IsEnum(FaDepreciationArea) depreciationArea!: FaDepreciationArea;
  @ApiProperty() @IsString() periodId!: string;
  @ApiProperty() @IsString() fiscalYearId!: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isSimulation?: boolean;
}

// ─── Lease ────────────────────────────────────────────────────────────────────────

export class CreateLeaseDto {
  @ApiProperty() @IsString() @MaxLength(50) leaseNumber!: string;
  @ApiProperty({ enum: FaLeaseType }) @IsEnum(FaLeaseType) leaseType!: FaLeaseType;
  @ApiProperty() @IsDateString() startDate!: string;
  @ApiProperty() @IsDateString() endDate!: string;
  @ApiProperty() @IsNumber() @Min(0) paymentAmount!: number;
  @ApiProperty() @IsNumber() @Min(0) totalLeaseLiability!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() lessorName?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() interestRate?: number;
}

// ─── Maintenance ──────────────────────────────────────────────────────────────────

export class CreateMaintenanceRecordDto {
  @ApiProperty() @IsString() assetId!: string;
  @ApiProperty() @IsString() @MaxLength(50) recordNumber!: string;
  @ApiProperty({ enum: FaMaintenanceType }) @IsEnum(FaMaintenanceType) maintenanceType!: FaMaintenanceType;
  @ApiProperty() @IsDateString() maintenanceDate!: string;
  @ApiProperty() @IsNumber() @Min(0) cost!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() vendorName?: string;
}

// ─── Physical Verification ────────────────────────────────────────────────────────

export class CreateVerificationDto {
  @ApiProperty() @IsString() @MaxLength(50) verificationNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsDateString() verificationDate!: string;
  @ApiPropertyOptional({ enum: FaVerificationMethod }) @IsEnum(FaVerificationMethod) @IsOptional() verificationMethod?: FaVerificationMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() verifiedByName?: string;
}
