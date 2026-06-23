import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, IsArray, MinLength, MaxLength, IsNumber, Min, ValidateNested, IsDateString, ArrayMinSize } from "class-validator";
import { Type } from "class-transformer";
import { JournalType, JournalEntryStatus } from "../../../domain/gl/journal.js";

export class JournalLineDto {
  @ApiProperty()
  @IsString()
  accountId!: string;

  @ApiProperty()
  @IsNumber() @Min(0)
  debitAmount!: number;

  @ApiProperty()
  @IsNumber() @Min(0)
  creditAmount!: number;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  foreignDebitAmount?: number;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  foreignCreditAmount?: number;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  currencyCode?: string;

  @ApiPropertyOptional()
  @IsNumber() @IsOptional()
  exchangeRate?: number;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  costCenterId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  departmentId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  projectId?: string;
}

export class CreateJournalBatchDto {
  @ApiProperty({ enum: JournalType })
  @IsEnum(JournalType)
  journalType!: JournalType;

  @ApiProperty()
  @IsString()
  periodId!: string;

  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiProperty()
  @IsDateString()
  voucherDate!: string;

  @ApiProperty()
  @IsDateString()
  postingDate!: string;

  @ApiProperty()
  @IsString() @MinLength(1)
  description!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  voucherTypeId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  voucherSeriesId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  reference?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  source?: string;

  @ApiProperty()
  @IsString()
  createdById!: string;

  @ApiProperty({ type: [JournalLineDto] })
  @IsArray() @ArrayMinSize(2)
  @ValidateNested({ each: true })
  @Type(() => JournalLineDto)
  lines!: JournalLineDto[];
}

export class ApproveBatchDto {
  @ApiProperty()
  @IsString()
  userId!: string;
}

export class PostBatchDto {
  @ApiProperty()
  @IsString()
  userId!: string;
}

export class ReverseBatchDto {
  @ApiProperty()
  @IsString()
  userId!: string;

  @ApiProperty()
  @IsString()
  reason!: string;
}
