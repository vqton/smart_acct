import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsNumber } from "class-validator";

export class GenerateReportDto {
  @ApiProperty()
  @IsString()
  reportDefId!: string;

  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  periodId?: string;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  periodNumber?: number;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  periodName?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  asOfDate?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  legalEntityId?: string;

  @ApiProperty()
  @IsString()
  generatedById!: string;
}

export class TrialBalanceQueryDto {
  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  periodNumber?: number;
}

export class RatioAnalysisQueryDto {
  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  periodNumber?: number;
}
