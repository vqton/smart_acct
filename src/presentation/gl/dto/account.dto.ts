import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsBoolean, IsEnum, MinLength, MaxLength } from "class-validator";
import { AccountCategory, AccountNature } from "../../../domain/gl/account-category.js";

export class CreateAccountDto {
  @ApiProperty({ example: "1111" })
  @IsString() @MinLength(1) @MaxLength(7)
  code!: string;

  @ApiProperty({ example: "Tiền mặt VNĐ" })
  @IsString() @MinLength(1) @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: AccountCategory })
  @IsEnum(AccountCategory)
  category!: AccountCategory;

  @ApiProperty({ enum: AccountNature })
  @IsEnum(AccountNature)
  nature!: AccountNature;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  parentId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  currencyCode?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isControl?: boolean;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isPosting?: boolean;
}

export class UpdateAccountDto {
  @ApiPropertyOptional()
  @IsString() @IsOptional()
  name?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  nameEn?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  description?: string;

  @ApiPropertyOptional()
  @IsBoolean() @IsOptional()
  isActive?: boolean;
}
