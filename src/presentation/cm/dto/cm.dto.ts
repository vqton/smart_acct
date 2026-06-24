import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, IsNumber, IsBoolean, IsDateString, Min, MaxLength, MinLength, ValidateNested, IsArray, ArrayMinSize } from "class-validator";
import { Type } from "class-transformer";
import { CashBoxType, CashBoxStatus, PaymentMethod, BankAccountType, BankTransferType, StatementLineType } from "../../../domain/cm/cm-enums.js";

// ─── Cash Box ──────────────────────────────────────────────────────────────────

export class CreateCashBoxDto {
  @ApiProperty() @IsString() locationId!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiProperty({ enum: CashBoxType }) @IsEnum(CashBoxType) boxType!: CashBoxType;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() minBalance?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() maxBalance?: number;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() allowNegative?: boolean;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
}

export class UpdateCashBoxDto {
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsEnum(CashBoxStatus) @IsOptional() status?: CashBoxStatus;
  @ApiPropertyOptional() @IsNumber() @IsOptional() minBalance?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() maxBalance?: number;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() allowNegative?: boolean;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
}

// ─── Cash Session ──────────────────────────────────────────────────────────────

export class OpenSessionDto {
  @ApiProperty() @IsString() cashBoxId!: string;
  @ApiProperty() @IsString() cashierId!: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() openedBalance?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
}

export class CloseSessionDto {
  @ApiProperty() @IsNumber() countedBalance!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CashCountDto {
  @ApiProperty() @IsString() denomination!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsNumber() unitValue!: number;
}

// ─── Cash Receipt ──────────────────────────────────────────────────────────────

export class CreateReceiptDto {
  @ApiProperty() @IsString() @MinLength(1) receiptNumber!: string;
  @ApiProperty() @IsDateString() receiptDate!: string;
  @ApiProperty() @IsString() cashBoxId!: string;
  @ApiProperty() @IsString() cashierId!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsEnum(PaymentMethod) @IsOptional() paymentMethod?: PaymentMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() sessionId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paidBy?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
}

// ─── Cash Payment ──────────────────────────────────────────────────────────────

export class CreatePaymentDto {
  @ApiProperty() @IsString() @MinLength(1) paymentNumber!: string;
  @ApiProperty() @IsDateString() paymentDate!: string;
  @ApiProperty() @IsString() cashBoxId!: string;
  @ApiProperty() @IsString() cashierId!: string;
  @ApiProperty() @IsString() @MinLength(1) payeeName!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsEnum(PaymentMethod) @IsOptional() paymentMethod?: PaymentMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() sessionId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
}

// ─── Bank ──────────────────────────────────────────────────────────────────────

export class CmCreateBankDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() swiftCode?: string;
}

export class CmCreateBankAccountDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() bankId!: string;
  @ApiProperty() @IsString() @MinLength(1) accountNumber!: string;
  @ApiProperty() @IsString() @MinLength(1) accountName!: string;
  @ApiPropertyOptional() @IsEnum(BankAccountType) @IsOptional() accountType?: BankAccountType;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiProperty() @IsDateString() openingDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() glAccountId?: string;
}

// ─── Bank Transfer ─────────────────────────────────────────────────────────────

export class CreateBankTransferDto {
  @ApiProperty() @IsString() transferNumber!: string;
  @ApiProperty({ enum: BankTransferType }) @IsEnum(BankTransferType) transferType!: BankTransferType;
  @ApiProperty() @IsString() fromAccountId!: string;
  @ApiProperty() @IsString() toAccountId!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiProperty() @IsDateString() transferDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() beneficiaryName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() beneficiaryBank?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() beneficiaryAccount?: string;
}

// ─── Bank Statement ────────────────────────────────────────────────────────────

export class ImportStatementLineDto {
  @ApiProperty() @IsDateString() lineDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() chequeNumber?: string;
  @ApiProperty({ enum: StatementLineType }) @IsEnum(StatementLineType) lineType!: StatementLineType;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiProperty() @IsNumber() runningBalance!: number;
}

export class CmImportStatementDto {
  @ApiProperty() @IsString() bankAccountId!: string;
  @ApiProperty() @IsString() statementNumber!: string;
  @ApiProperty() @IsDateString() periodStart!: string;
  @ApiProperty() @IsDateString() periodEnd!: string;
  @ApiProperty() @IsNumber() openingBalance!: number;
  @ApiProperty() @IsNumber() closingBalance!: number;
  @ApiProperty({ type: [ImportStatementLineDto] })
  @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true })
  @Type(() => ImportStatementLineDto)
  lines!: ImportStatementLineDto[];
}

// ─── Cash Advance ──────────────────────────────────────────────────────────────

export class CreateCashAdvanceDto {
  @ApiProperty() @IsString() advanceNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() employeeId!: string;
  @ApiProperty() @IsString() employeeName!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiProperty() @IsDateString() advanceDate!: string;
  @ApiProperty() @IsString() purpose!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() expectedSettleDate?: string;
}

// ─── Cash Transfer ─────────────────────────────────────────────────────────────

export class CreateCashTransferDto {
  @ApiProperty() @IsString() transferNumber!: string;
  @ApiProperty() @IsString() fromLocationId!: string;
  @ApiProperty() @IsString() toLocationId!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiProperty() @IsDateString() transferDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
}

// ─── Petty Cash ────────────────────────────────────────────────────────────────

export class CreatePettyCashDto {
  @ApiProperty() @IsString() locationId!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) fundCode!: string;
  @ApiProperty() @IsString() fundName!: string;
  @ApiProperty() @IsNumber() @Min(1) maximumBalance!: number;
  @ApiProperty() @IsNumber() @Min(0) minimumBalance!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() holderId?: string;
}

// ─── Approval ──────────────────────────────────────────────────────────────────

export class ApproveDto {
  @ApiProperty() @IsString() userId!: string;
}

export class RejectDto {
  @ApiProperty() @IsString() userId!: string;
  @ApiProperty() @IsString() reason!: string;
}

export class ReverseDto {
  @ApiProperty() @IsString() userId!: string;
  @ApiProperty() @IsString() reason!: string;
}

// ─── Cash Forecast ─────────────────────────────────────────────────────────────

export class CreateCashForecastDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() forecastNumber!: string;
  @ApiProperty() @IsString() forecastName!: string;
  @ApiProperty() @IsString() periodType!: string;
  @ApiProperty() @IsDateString() periodStart!: string;
  @ApiProperty() @IsDateString() periodEnd!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() openingBalance?: number;
}

export class AddForecastLineDto {
  @ApiProperty() @IsDateString() lineDate!: string;
  @ApiProperty() @IsString() description!: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() inflowAmount?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() outflowAmount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() category?: string;
}
