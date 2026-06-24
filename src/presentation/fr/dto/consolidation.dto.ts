import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsNumber, IsEnum, Min, Max, IsArray, ValidateNested, MinLength, MaxLength } from "class-validator";
import { Type } from "class-transformer";
import { FrConsolidationMethod } from "../../../domain/fr/fr-enums.js";

export class CreateConsolidationGroupDto {
  @ApiProperty({ example: "GROUP_01" })
  @IsString() @MinLength(1) @MaxLength(20)
  code!: string;

  @ApiProperty({ example: "Tập đoàn ABC" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiProperty()
  @IsString()
  parentCompanyId!: string;

  @ApiPropertyOptional({ default: "VND" })
  @IsString() @IsOptional()
  currencyCode?: string;

  @ApiProperty()
  @IsString()
  createdById!: string;
}

export class AddGroupMemberDto {
  @ApiProperty()
  @IsString()
  legalEntityId!: string;

  @ApiProperty()
  @IsString()
  legalEntityCode!: string;

  @ApiProperty()
  @IsString()
  legalEntityName!: string;

  @ApiProperty({ example: 0.75 })
  @IsNumber() @Min(0) @Max(1)
  ownershipPercentage!: number;

  @ApiProperty({ enum: FrConsolidationMethod })
  @IsEnum(FrConsolidationMethod)
  consolidationMethod!: FrConsolidationMethod;
}

export class CreateConsolidationRunDto {
  @ApiProperty()
  @IsString()
  groupId!: string;

  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  periodId?: string;

  @ApiProperty()
  @IsNumber()
  periodNumber!: number;

  @ApiProperty()
  @IsString()
  periodName!: string;

  @ApiProperty()
  @IsString()
  asOfDate!: string;

  @ApiProperty()
  @IsString()
  preparedById!: string;
}
