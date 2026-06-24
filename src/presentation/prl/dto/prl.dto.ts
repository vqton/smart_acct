import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import {
  IsString, IsOptional, IsBoolean, IsEnum, IsNumber, IsDateString, MinLength, MaxLength, Min, IsInt, IsArray, ArrayMinSize,
} from "class-validator";

// ─── Payroll Group ──────────────────────────────────────────────────────────

export class CreatePayrollGroupDto {
  @ApiProperty({ example: "PG-MONTHLY" }) @IsString() @MinLength(1) @MaxLength(20)
  code!: string;
  @ApiProperty({ example: "Monthly Payroll - HCMC" }) @IsString() @MinLength(1) @MaxLength(255)
  name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  description?: string;
  @ApiProperty() @IsString()
  companyId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  branchId?: string;
  @ApiPropertyOptional({ default: "monthly" }) @IsString() @IsOptional()
  payFrequency?: string;
  @ApiPropertyOptional({ default: "VND" }) @IsString() @IsOptional()
  currencyCode?: string;
}

export class UpdatePayrollGroupDto {
  @ApiPropertyOptional() @IsString() @IsOptional()
  name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  payFrequency?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  currencyCode?: string;
}

// ─── Salary Component ───────────────────────────────────────────────────────

export class CreateSalaryComponentDto {
  @ApiProperty({ example: "BASIC" }) @IsString() @MinLength(1) @MaxLength(20)
  code!: string;
  @ApiProperty({ example: "Lương cơ bản" }) @IsString() @MinLength(1) @MaxLength(255)
  name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  nameEn?: string;
  @ApiProperty({ example: "base_salary" }) @IsString()
  elementType!: string;
  @ApiProperty({ example: "earning" }) @IsString()
  category!: string;
  @ApiPropertyOptional({ default: true }) @IsBoolean() @IsOptional()
  isTaxable?: boolean;
  @ApiPropertyOptional({ default: false }) @IsBoolean() @IsOptional()
  isInsurable?: boolean;
  @ApiPropertyOptional({ default: true }) @IsBoolean() @IsOptional()
  isPITable?: boolean;
  @ApiPropertyOptional({ default: 0 }) @IsInt() @IsOptional()
  priority?: number;
  @ApiPropertyOptional() @IsString() @IsOptional()
  formula?: string;
}

// ─── Employee Payroll ───────────────────────────────────────────────────────

export class CreateEmployeePayrollDto {
  @ApiProperty({ example: "EMP001" }) @IsString() @MinLength(1) @MaxLength(50)
  employeeCode!: string;
  @ApiProperty({ example: "Nguyen Van A" }) @IsString() @MinLength(1) @MaxLength(255)
  employeeName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  fullName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  gender?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  taxCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  socialInsuranceNo?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  healthInsuranceNo?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  email?: string;
  @ApiProperty() @IsString()
  companyId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  positionId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  costCenterId?: string;
  @ApiProperty() @IsString()
  groupId!: string;
  @ApiProperty() @IsDateString()
  hireDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  paymentMethod?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  employmentType?: string;
  @ApiPropertyOptional({ default: false }) @IsBoolean() @IsOptional()
  isPITRegistered?: boolean;
  @ApiPropertyOptional({ default: 0 }) @IsInt() @IsOptional()
  dependentCount?: number;
}

export class UpdateEmployeePayrollDto {
  @ApiPropertyOptional() @IsString() @IsOptional()
  employeeName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  fullName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  taxCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  socialInsuranceNo?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  positionId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  groupId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  paymentMethod?: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  employmentType?: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional()
  isPITRegistered?: boolean;
  @ApiPropertyOptional() @IsInt() @IsOptional()
  dependentCount?: number;
}

export class TerminateEmployeeDto {
  @ApiProperty() @IsDateString()
  terminationDate!: string;
}

// ─── Payroll Period ─────────────────────────────────────────────────────────

export class CreatePayrollPeriodDto {
  @ApiProperty() @IsString()
  calendarId!: string;
  @ApiProperty() @IsInt()
  periodNumber!: number;
  @ApiProperty({ example: "Tháng 06/2026" }) @IsString()
  name!: string;
  @ApiProperty() @IsDateString()
  startDate!: string;
  @ApiProperty() @IsDateString()
  endDate!: string;
  @ApiProperty() @IsInt()
  year!: number;
  @ApiProperty() @IsInt()
  month!: number;
  @ApiPropertyOptional() @IsDateString() @IsOptional()
  paymentDate?: string;
}

// ─── Payroll Run ────────────────────────────────────────────────────────────

export class CreatePayrollRunDto {
  @ApiProperty({ example: "PR-2026-06-HCMC" }) @IsString()
  runNumber!: string;
  @ApiProperty() @IsString()
  groupId!: string;
  @ApiProperty() @IsString()
  periodId!: string;
  @ApiProperty() @IsString()
  calendarId!: string;
  @ApiProperty({ example: "Payroll June 2026 - HCMC" }) @IsString()
  name!: string;
  @ApiProperty() @IsString()
  companyId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional()
  branchId?: string;
}

export class AddEmployeesToRunDto {
  @ApiProperty({ type: [String] }) @IsArray() @ArrayMinSize(1)
  employeeIds!: string[];
}

export class ApproveRunDto {
  @ApiProperty() @IsString()
  approvedById!: string;
}

export class PostRunDto {
  @ApiProperty() @IsString()
  postedById!: string;
}

export class ReverseRunDto {
  @ApiProperty() @IsString()
  reversedById!: string;
}

// ─── Insurance Rate ─────────────────────────────────────────────────────────

export class CreateInsuranceRateDto {
  @ApiProperty({ example: "social_insurance" }) @IsString()
  insuranceType!: string;
  @ApiProperty({ example: "BHXH 2026" }) @IsString()
  name!: string;
  @ApiProperty() @IsDateString()
  effectiveFrom!: string;
  @ApiProperty({ example: 0.08 }) @IsNumber()
  eeRate!: number;
  @ApiProperty({ example: 0.175 }) @IsNumber()
  erRate!: number;
  @ApiPropertyOptional() @IsInt() @IsOptional()
  ceilingAmount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional()
  regulationRef?: string;
}

// ─── Tax Bracket ────────────────────────────────────────────────────────────

export class CreateTaxBracketDto {
  @ApiProperty({ example: "Bậc 1" }) @IsString()
  name!: string;
  @ApiProperty() @IsDateString()
  effectiveFrom!: string;
  @ApiProperty() @IsInt()
  bracketOrder!: number;
  @ApiProperty({ example: 0 }) @IsInt()
  fromAmount!: number;
  @ApiPropertyOptional() @IsInt() @IsOptional()
  toAmount?: number;
  @ApiProperty({ example: 0.05 }) @IsNumber()
  rate!: number;
  @ApiProperty({ example: 0 }) @IsInt()
  deductAmount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional()
  regulationRef?: string;
}
