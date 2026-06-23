import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsDateString, MinLength, MaxLength, IsInt, Min } from "class-validator";

export class CreateFiscalYearDto {
  @ApiProperty({ example: "FY2026" })
  @IsString() @MinLength(1) @MaxLength(20)
  code!: string;

  @ApiProperty({ example: "Năm tài chính 2026" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiProperty()
  @IsDateString()
  startDate!: string;

  @ApiProperty()
  @IsDateString()
  endDate!: string;
}

export class CreatePeriodDto {
  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiProperty()
  @IsInt() @Min(1)
  periodNumber!: number;

  @ApiProperty()
  @IsString()
  name!: string;

  @ApiProperty()
  @IsDateString()
  startDate!: string;

  @ApiProperty()
  @IsDateString()
  endDate!: string;
}
