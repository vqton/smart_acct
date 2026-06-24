import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsEnum, IsOptional, IsNumber, IsDateString, Min, MaxLength } from "class-validator";
import { TaxCategory, TaxNature, TaxBasis, TaxCalculationMethod, TaxPaymentMethod as TaxTypePaymentMethod, TaxFilingFrequency } from "../../../domain/tax/tax-type.js";
import { TaxRateType, TaxRateApplication } from "../../../domain/tax/tax-code.js";
import { JurisdictionLevel, TaxRegionType } from "../../../domain/tax/tax-jurisdiction.js";
import { IncentiveType, IncentiveApplicationLevel } from "../../../domain/tax/tax-incentive.js";
import { TaxReturnType } from "../../../domain/tax/tax-return.js";
import { TaxPaymentMethod } from "../../../domain/tax/tax-payment.js";

export class CreateTaxTypeDto {
  @ApiProperty({ example: "VAT" })
  @IsString() @MaxLength(50)
  code!: string;

  @ApiProperty({ example: "Thuế Giá trị gia tăng" })
  @IsString() @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: TaxCategory })
  @IsEnum(TaxCategory)
  category!: TaxCategory;

  @ApiProperty({ enum: TaxNature })
  @IsEnum(TaxNature)
  nature!: TaxNature;

  @ApiProperty({ enum: TaxBasis })
  @IsEnum(TaxBasis)
  basis!: TaxBasis;

  @ApiProperty({ enum: TaxCalculationMethod })
  @IsEnum(TaxCalculationMethod)
  calculationMethod!: TaxCalculationMethod;

  @ApiProperty({ enum: TaxTypePaymentMethod })
  @IsEnum(TaxTypePaymentMethod)
  paymentMethod!: TaxTypePaymentMethod;

  @ApiProperty({ enum: TaxFilingFrequency })
  @IsEnum(TaxFilingFrequency)
  filingFrequency!: TaxFilingFrequency;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  parentTaxTypeId?: string;
}

export class CreateTaxCodeDto {
  @ApiProperty({ example: "VAT10" })
  @IsString() @MaxLength(50)
  code!: string;

  @ApiProperty({ example: "VAT 10%" })
  @IsString() @MaxLength(255)
  name!: string;

  @ApiProperty()
  @IsString()
  taxTypeId!: string;

  @ApiProperty({ enum: TaxRateType })
  @IsEnum(TaxRateType)
  taxRateType!: TaxRateType;

  @ApiProperty({ enum: TaxRateApplication })
  @IsEnum(TaxRateApplication)
  application!: TaxRateApplication;

  @ApiPropertyOptional({ description: "Initial rate percentage" })
  @IsNumber() @IsOptional() @Min(0)
  rate?: number;

  @ApiPropertyOptional({ description: "Rate type for initial rate", enum: TaxRateType })
  @IsEnum(TaxRateType) @IsOptional()
  rateType?: TaxRateType;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  effectiveFrom?: string;
}

export class CreateTaxAuthorityDto {
  @ApiProperty({ example: "HCM_TAX" })
  @IsString() @MaxLength(50)
  code!: string;

  @ApiProperty({ example: "Cục Thuế TP Hồ Chí Minh" })
  @IsString() @MaxLength(255)
  name!: string;

  @ApiProperty({ example: "HCM01" })
  @IsString() @MaxLength(50)
  taxOfficeCode!: string;

  @ApiProperty({ enum: JurisdictionLevel })
  @IsEnum(JurisdictionLevel)
  jurisdictionLevel!: JurisdictionLevel;
}

export class CreateTaxRegionDto {
  @ApiProperty({ example: "HCM_IZ" })
  @IsString() @MaxLength(50)
  code!: string;

  @ApiProperty({ example: "Khu Công Nghệ Cao TP HCM" })
  @IsString() @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: TaxRegionType })
  @IsEnum(TaxRegionType)
  type!: TaxRegionType;

  @ApiPropertyOptional({ default: "VN" })
  @IsString() @IsOptional() @MaxLength(2)
  countryCode?: string;
}

export class CreateTaxRegistrationDto {
  @ApiProperty({ example: "REG-VAT-2024-001" })
  @IsString() @MaxLength(100)
  registrationNumber!: string;

  @ApiProperty()
  @IsString()
  taxpayerId!: string;

  @ApiProperty()
  @IsString()
  taxTypeId!: string;

  @ApiProperty()
  @IsString()
  taxAuthorityId!: string;
}

export class CreateTaxReturnDto {
  @ApiProperty({ example: "RET-VAT-Q1-2024" })
  @IsString() @MaxLength(100)
  returnNumber!: string;

  @ApiProperty({ enum: TaxReturnType })
  @IsEnum(TaxReturnType)
  returnType!: TaxReturnType;

  @ApiProperty()
  @IsString()
  taxTypeId!: string;

  @ApiProperty()
  @IsString()
  taxpayerId!: string;

  @ApiProperty()
  @IsString()
  taxAuthorityId!: string;

  @ApiProperty()
  @IsString()
  periodId!: string;

  @ApiProperty()
  @IsString()
  fiscalYearId!: string;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  filingDate?: string;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  dueDate?: string;

  @ApiPropertyOptional({ default: "system" })
  @IsString() @IsOptional()
  createdById?: string;
}

export class CreateTaxExemptionDto {
  @ApiProperty({ example: "EXEMPT-VAT-EDU" })
  @IsString() @MaxLength(50)
  code!: string;

  @ApiProperty({ example: "Miễn thuế giáo dục" })
  @IsString() @MaxLength(255)
  name!: string;

  @ApiProperty({ enum: IncentiveType })
  @IsEnum(IncentiveType)
  exemptionType!: IncentiveType;

  @ApiProperty()
  @IsString()
  taxTypeId!: string;

  @ApiProperty({ enum: IncentiveApplicationLevel })
  @IsEnum(IncentiveApplicationLevel)
  applicationLevel!: IncentiveApplicationLevel;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  validFrom?: string;
}

export class CreateTaxPaymentDto {
  @ApiProperty()
  @IsString()
  taxReturnId!: string;

  @ApiProperty()
  @IsString()
  taxpayerId!: string;

  @ApiProperty()
  @IsString()
  taxTypeId!: string;

  @ApiProperty({ example: 1000000 })
  @IsNumber() @Min(0)
  amount!: number;

  @ApiProperty({ enum: TaxPaymentMethod })
  @IsEnum(TaxPaymentMethod)
  paymentMethod!: TaxPaymentMethod;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  paymentDate?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  referenceNumber?: string;

  @ApiPropertyOptional({ default: "system" })
  @IsString() @IsOptional()
  paidById?: string;
}

export class CalculateTaxDto {
  @ApiProperty()
  @IsString()
  taxCodeId!: string;

  @ApiProperty({ example: 1000000 })
  @IsNumber() @Min(0)
  amount!: number;

  @ApiPropertyOptional()
  @IsDateString() @IsOptional()
  date?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  regionId?: string;

  @ApiPropertyOptional()
  @IsString() @IsOptional()
  taxpayerId?: string;
}
