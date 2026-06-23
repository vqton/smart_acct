import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, IsNumber, IsBoolean, IsDateString, Min, MaxLength, MinLength, ValidateNested, IsArray, ArrayMinSize } from "class-validator";
import { Type } from "class-transformer";
import {
  BankGroupType, CorrespondentType, BankAccountCategory, BankAccountStatus,
  TransactionNature, TransactionMethod, StatementSource, ReconciliationMatchType,
  TransactionStatus, PaymentPriority, ChargeBearer, PaymentBatchStatus,
  RecurringFrequency, SignatureRule, AccountLimitType,
} from "../../../domain/bank/bank-enums.js";

// ─── Bank Group ────────────────────────────────────────────────────────────────

export class CreateBankGroupDto {
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiProperty({ enum: BankGroupType }) @IsEnum(BankGroupType) groupType!: BankGroupType;
}

// ─── Bank ──────────────────────────────────────────────────────────────────────

export class CreateBankDto {
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiProperty() @IsString() @MaxLength(2) countryCode!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() shortName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() swiftCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() routingNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() bankCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() groupId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() website?: string;
}

export class UpdateBankDto {
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() swiftCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() routingNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() website?: string;
}

// ─── Bank Branch ────────────────────────────────────────────────────────────────

export class CreateBankBranchDto {
  @ApiProperty() @IsString() bankId!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() managerName?: string;
}

// ─── Correspondent Bank ─────────────────────────────────────────────────────────

export class CreateCorrespondentBankDto {
  @ApiProperty() @IsString() bankId!: string;
  @ApiProperty() @IsString() correspondentBankId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() accountNumber?: string;
  @ApiProperty({ enum: CorrespondentType }) @IsEnum(CorrespondentType) correspondentType!: CorrespondentType;
  @ApiProperty() @IsString() currencyCode!: string;
}

// ─── Bank Account ──────────────────────────────────────────────────────────────

export class CreateBankAccountDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() bankId!: string;
  @ApiProperty() @IsString() @MinLength(1) accountNumber!: string;
  @ApiProperty() @IsString() accountName!: string;
  @ApiPropertyOptional() @IsEnum(BankAccountCategory) @IsOptional() accountCategory?: BankAccountCategory;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() iban?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() swiftCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() glAccountId?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() openingDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class SuspendAccountDto {
  @ApiProperty() @IsString() reason!: string;
}

export class BlockAccountDto {
  @ApiProperty() @IsString() reason!: string;
}

export class CloseAccountDto {
  @ApiPropertyOptional() @IsBoolean() @IsOptional() force?: boolean;
}

// ─── Authorized Signer ─────────────────────────────────────────────────────────

export class AddSignerDto {
  @ApiProperty() @IsString() userId!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() title?: string;
  @ApiPropertyOptional() @IsEnum(SignatureRule) @IsOptional() signatureRule?: SignatureRule;
  @ApiPropertyOptional() @IsNumber() @IsOptional() signingLimit?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
}

// ─── Account Limit ──────────────────────────────────────────────────────────────

export class AddAccountLimitDto {
  @ApiProperty({ enum: AccountLimitType }) @IsEnum(AccountLimitType) limitType!: AccountLimitType;
  @ApiPropertyOptional() @IsNumber() @IsOptional() maxAmount?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() minAmount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isEnforced?: boolean;
}

// ─── Account Mapping ────────────────────────────────────────────────────────────

export class AddAccountMappingDto {
  @ApiProperty() @IsString() mappingType!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() glAccountId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectId?: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isDefault?: boolean;
}

// ─── Bank Transaction ───────────────────────────────────────────────────────────

export class CreateTransactionDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() transactionNumber!: string;
  @ApiProperty({ enum: TransactionNature }) @IsEnum(TransactionNature) nature!: TransactionNature;
  @ApiProperty({ enum: TransactionMethod }) @IsEnum(TransactionMethod) method!: TransactionMethod;
  @ApiProperty() @IsString() fromAccountId!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiProperty() @IsDateString() transactionDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() toAccountId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() beneficiaryName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() fees?: number;
}

// ─── Import Statement ───────────────────────────────────────────────────────────

export class ImportStatementLineDto {
  @ApiProperty() @IsDateString() lineDate!: string;
  @ApiProperty() @IsString() lineType!: string;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiProperty() @IsNumber() runningBalance!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
}

export class ImportStatementDto {
  @ApiProperty() @IsString() bankAccountId!: string;
  @ApiProperty() @IsString() statementNumber!: string;
  @ApiProperty() @IsDateString() periodStart!: string;
  @ApiProperty() @IsDateString() periodEnd!: string;
  @ApiProperty() @IsNumber() openingBalance!: number;
  @ApiProperty() @IsNumber() closingBalance!: number;
  @ApiPropertyOptional() @IsEnum(StatementSource) @IsOptional() source?: StatementSource;
  @ApiPropertyOptional() @IsString() @IsOptional() importedBy?: string;
  @ApiProperty({ type: [ImportStatementLineDto] })
  @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true })
  @Type(() => ImportStatementLineDto)
  lines!: ImportStatementLineDto[];
}

// ─── Reconciliation ─────────────────────────────────────────────────────────────

export class CreateReconciliationDto {
  @ApiProperty() @IsString() bankAccountId!: string;
  @ApiProperty() @IsString() bankStatementId!: string;
  @ApiProperty() @IsString() reconciliationNumber!: string;
  @ApiProperty() @IsDateString() reconciliationDate!: string;
  @ApiProperty() @IsNumber() statementBalance!: number;
  @ApiProperty() @IsNumber() bookBalance!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() preparedById?: string;
}

export class MatchReconciliationItemDto {
  @ApiPropertyOptional() @IsString() @IsOptional() statementLineId?: string;
  @ApiProperty() @IsString() sourceType!: string;
  @ApiProperty() @IsString() sourceId!: string;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiProperty({ enum: ReconciliationMatchType }) @IsEnum(ReconciliationMatchType) matchType!: ReconciliationMatchType;
}

// ─── Payment Request ────────────────────────────────────────────────────────────

export class CreatePaymentRequestDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() requestNumber!: string;
  @ApiProperty() @IsDateString() paymentDate!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiProperty() @IsString() fromAccountId!: string;
  @ApiProperty() @IsString() beneficiaryName!: string;
  @ApiPropertyOptional() @IsEnum(TransactionMethod) @IsOptional() method?: TransactionMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() reference?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiProperty() @IsString() requestedById!: string;
}

export class RejectPaymentRequestDto {
  @ApiProperty() @IsString() userId!: string;
  @ApiProperty() @IsString() reason!: string;
}

// ─── Payment Batch ──────────────────────────────────────────────────────────────

export class CreatePaymentBatchDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() batchNumber!: string;
  @ApiProperty() @IsDateString() paymentDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
}

// ─── Recurring Payment ──────────────────────────────────────────────────────────

export class CreateRecurringPaymentDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() fromAccountId!: string;
  @ApiProperty() @IsString() beneficiaryName!: string;
  @ApiProperty() @IsNumber() @Min(1) amount!: number;
  @ApiProperty({ enum: RecurringFrequency }) @IsEnum(RecurringFrequency) frequency!: RecurringFrequency;
  @ApiProperty() @IsDateString() startDate!: string;
  @ApiPropertyOptional() @IsEnum(TransactionMethod) @IsOptional() method?: TransactionMethod;
}

// ─── Cash Position ──────────────────────────────────────────────────────────────

export class CreateCashPositionDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsDateString() positionDate!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() openingBalance?: number;
}

// ─── FX Revaluation ─────────────────────────────────────────────────────────────

export class CreateFXRevaluationDto {
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsDateString() revaluationDate!: string;
  @ApiProperty() @IsString() currencyCode!: string;
  @ApiProperty() @IsNumber() exchangeRate!: number;
  @ApiProperty() @IsNumber() previousRate!: number;
  @ApiProperty() @IsString() accountId!: string;
  @ApiProperty() @IsNumber() accountBalance!: number;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isRealized?: boolean;
}

// ─── Common ─────────────────────────────────────────────────────────────────────

export class UserActionDto {
  @ApiProperty() @IsString() userId!: string;
}

export class ReasonDto {
  @ApiProperty() @IsString() reason!: string;
}
