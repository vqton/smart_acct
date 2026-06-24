import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsBoolean, IsEnum, MinLength, MaxLength, IsArray, ValidateNested } from "class-validator";
import { Type } from "class-transformer";
import { FrReportCategoryType } from "../../../domain/fr/fr-enums.js";

export class CreateReportDefinitionDto {
  @ApiProperty({ example: "BS_01" })
  @IsString() @MinLength(1) @MaxLength(20)
  code!: string;

  @ApiProperty({ example: "Bảng cân đối kế toán" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiPropertyOptional({ example: "Balance Sheet" })
  @IsString() @IsOptional()
  nameEn?: string;

  @ApiProperty({ enum: FrReportCategoryType })
  @IsEnum(FrReportCategoryType)
  category!: FrReportCategoryType;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiPropertyOptional({ default: "VND" })
  @IsString() @IsOptional()
  displayCurrency?: string;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isComparative?: boolean;

  @ApiPropertyOptional()
  @IsString()
  createdById!: string;
}

export class UpdateReportDefinitionDto {
  @ApiPropertyOptional()
  @IsString() @IsOptional()
  name?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  nameEn?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;
}

export class AddReportRowDto {
  @ApiProperty()
  @IsString()
  rowCode!: string;

  @ApiProperty({ example: "A. Tài sản ngắn hạn" })
  @IsString()
  label!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  labelEn?: string;

  @ApiProperty()
  @IsString()
  rowType!: string;

  @ApiPropertyOptional({ default: 0 })
  indentLevel?: number;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isBold?: boolean;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  parentRowCode?: string;
}
