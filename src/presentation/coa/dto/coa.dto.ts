import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsBoolean, IsEnum, IsNumber, IsDateString, MinLength, MaxLength } from "class-validator";
import { AccountClassType } from "../../../domain/coa/coa-enums.js";
import { AccountTypeCategory, AccountSubType } from "../../../domain/coa/coa-enums.js";
import { AccountMappingStandard, AccountMappingType } from "../../../domain/coa/coa-enums.js";
import { AccountEffectiveStatus, AccountControlLevel, DimensionRequirement } from "../../../domain/coa/coa-enums.js";
import { AccountNature } from "../../../domain/gl/account-category.js";

// ─── Account Class ───────────────────────────────────────────────────────

export class CreateAccountClassDto {
  @ApiProperty({ example: "1", description: "Single digit class code (1-9)" })
  @IsString() @MinLength(1) @MaxLength(1)
  code!: string;

  @ApiProperty({ example: "Tài sản" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: AccountClassType })
  @IsEnum(AccountClassType)
  classType!: AccountClassType;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  displayOrder?: number;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;
}

// ─── Account Type ────────────────────────────────────────────────────────

export class CreateAccountTypeDto {
  @ApiProperty()
  @IsString()
  classId!: string;

  @ApiProperty({ example: "111" })
  @IsString() @MinLength(1) @MaxLength(10)
  code!: string;

  @ApiProperty({ example: "Tiền mặt" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: AccountTypeCategory })
  @IsEnum(AccountTypeCategory)
  category!: AccountTypeCategory;

  @ApiProperty({ enum: AccountNature })
  @IsEnum(AccountNature)
  nature!: AccountNature;

  @ApiPropertyOptional({ enum: AccountSubType })
  @IsEnum(AccountSubType) @IsOptional()
  subType?: AccountSubType;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  parentTypeId?: string;
}

// ─── Account Mapping ─────────────────────────────────────────────────────

export class CreateAccountMappingDto {
  @ApiProperty()
  @IsString()
  accountId!: string;

  @ApiProperty({ enum: AccountMappingStandard })
  @IsEnum(AccountMappingStandard)
  mappingStandard!: AccountMappingStandard;

  @ApiProperty({ enum: AccountMappingType })
  @IsEnum(AccountMappingType)
  mappingType!: AccountMappingType;

  @ApiProperty()
  @IsString()
  targetCode!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  targetName?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  mappingRule?: string;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  percentage?: number;

  @ApiProperty()
  @IsDateString()
  effectiveFrom!: string;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  effectiveTo?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;
}

// ─── Account Extension ───────────────────────────────────────────────────

export class UpdateAccountExtensionDto {
  @ApiPropertyOptional()
  @IsString() @IsOptional()
  typeId?: string;

  @ApiPropertyOptional({ enum: AccountEffectiveStatus })
  @IsEnum(AccountEffectiveStatus) @IsOptional()
  effectiveStatus?: AccountEffectiveStatus;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  effectiveFrom?: string;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  effectiveTo?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  statusReason?: string;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  allowAutoPosting?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  requireApproval?: boolean;

  @ApiPropertyOptional({ enum: AccountControlLevel })
  @IsEnum(AccountControlLevel) @IsOptional()
  budgetControlLevel?: AccountControlLevel;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  budgetCheckMessage?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultCostCenterId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultDepartmentId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultProjectId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultBranchId?: string;

  @ApiPropertyOptional({ enum: DimensionRequirement })
  @IsEnum(DimensionRequirement) @IsOptional()
  costCenterRequired?: DimensionRequirement;

  @ApiPropertyOptional({ enum: DimensionRequirement })
  @IsEnum(DimensionRequirement) @IsOptional()
  departmentRequired?: DimensionRequirement;

  @ApiPropertyOptional({ enum: DimensionRequirement })
  @IsEnum(DimensionRequirement) @IsOptional()
  projectRequired?: DimensionRequirement;

  @ApiPropertyOptional({ enum: DimensionRequirement })
  @IsEnum(DimensionRequirement) @IsOptional()
  branchRequired?: DimensionRequirement;

  @ApiPropertyOptional({ enum: DimensionRequirement })
  @IsEnum(DimensionRequirement) @IsOptional()
  profitCenterRequired?: DimensionRequirement;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isCashAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isBankAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isTaxAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isInventoryAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isReceivableAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isPayableAccount?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isIntercompanyAccount?: boolean;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultTaxCodeId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  defaultTaxRateId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  cashFlowCode?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  financialStatementCode?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  financialStatementNote?: string;
}
