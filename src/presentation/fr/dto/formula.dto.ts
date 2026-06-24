import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, MinLength, MaxLength } from "class-validator";
import { FrFormulaType } from "../../../domain/fr/fr-enums.js";

export class CreateFormulaDto {
  @ApiProperty({ example: "GROSS_PROFIT" })
  @IsString() @MinLength(1) @MaxLength(20)
  code!: string;

  @ApiProperty({ example: "Gross Profit" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: FrFormulaType, default: FrFormulaType.Simple })
  @IsEnum(FrFormulaType) @IsOptional()
  formulaType?: FrFormulaType;

  @ApiProperty({ example: "SUM(ACCOUNT(511), ACCOUNT(512)) - ACCOUNT(632)" })
  @IsString()
  expression!: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiProperty()
  @IsString()
  createdById!: string;
}

export class UpdateFormulaDto {
  @ApiPropertyOptional()
  @IsString() @IsOptional()
  expression?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;
}
