-- CreateTable
CREATE TABLE `Account` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `category` ENUM('short_term_asset', 'long_term_asset', 'short_term_liability', 'long_term_liability', 'equity', 'revenue', 'operating_expense', 'other_expense', 'other_income', 'cost_of_goods_sold', 'manufacturing_cost') NOT NULL,
    `nature` ENUM('debit', 'credit') NOT NULL,
    `parentId` VARCHAR(191) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `isControl` BOOLEAN NOT NULL DEFAULT false,
    `isPosting` BOOLEAN NOT NULL DEFAULT true,
    `allowManualEntry` BOOLEAN NOT NULL DEFAULT true,
    `balance` BIGINT NOT NULL DEFAULT 0,
    `foreignBalance` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NULL,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `Account_code_key`(`code`),
    INDEX `Account_code_idx`(`code`),
    INDEX `Account_parentId_idx`(`parentId`),
    INDEX `Account_category_idx`(`category`),
    INDEX `Account_isActive_idx`(`isActive`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `FiscalYear` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `startDate` DATETIME(3) NOT NULL,
    `endDate` DATETIME(3) NOT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `isClosed` BOOLEAN NOT NULL DEFAULT false,
    `closedAt` DATETIME(3) NULL,
    `closedById` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `FiscalYear_code_key`(`code`),
    INDEX `FiscalYear_code_idx`(`code`),
    INDEX `FiscalYear_isActive_idx`(`isActive`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Period` (
    `id` VARCHAR(191) NOT NULL,
    `fiscalYearId` VARCHAR(191) NOT NULL,
    `periodNumber` INTEGER NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `startDate` DATETIME(3) NOT NULL,
    `endDate` DATETIME(3) NOT NULL,
    `status` ENUM('open', 'closed', 'locked') NOT NULL DEFAULT 'open',
    `openedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `closedAt` DATETIME(3) NULL,
    `closedById` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `Period_fiscalYearId_idx`(`fiscalYearId`),
    INDEX `Period_status_idx`(`status`),
    INDEX `Period_startDate_endDate_idx`(`startDate`, `endDate`),
    UNIQUE INDEX `Period_fiscalYearId_periodNumber_key`(`fiscalYearId`, `periodNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `VoucherType` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `category` ENUM('payment', 'receipt', 'journal', 'sales', 'purchase', 'payroll', 'inventory', 'fixed_asset', 'tax', 'other') NOT NULL,
    `description` TEXT NULL,
    `requiresApproval` BOOLEAN NOT NULL DEFAULT true,
    `requiresAttachment` BOOLEAN NOT NULL DEFAULT false,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,

    UNIQUE INDEX `VoucherType_code_key`(`code`),
    INDEX `VoucherType_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `VoucherSeries` (
    `id` VARCHAR(191) NOT NULL,
    `voucherTypeId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `prefix` VARCHAR(10) NOT NULL,
    `suffix` VARCHAR(10) NULL,
    `currentNumber` INTEGER NOT NULL DEFAULT 0,
    `nextNumber` INTEGER NOT NULL DEFAULT 1,
    `minDigits` INTEGER NOT NULL DEFAULT 4,
    `sequenceMethod` ENUM('annual', 'monthly', 'continuous') NOT NULL DEFAULT 'annual',
    `fiscalYearId` VARCHAR(191) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,

    UNIQUE INDEX `VoucherSeries_code_key`(`code`),
    INDEX `VoucherSeries_voucherTypeId_idx`(`voucherTypeId`),
    INDEX `VoucherSeries_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `JournalBatch` (
    `id` VARCHAR(191) NOT NULL,
    `batchNumber` VARCHAR(50) NOT NULL,
    `journalType` ENUM('standard', 'recurring', 'reversing', 'accrual', 'allocation', 'adjustment', 'closing', 'opening') NOT NULL DEFAULT 'standard',
    `status` ENUM('draft', 'submitted', 'approved', 'posted', 'reversed', 'cancelled') NOT NULL DEFAULT 'draft',
    `periodId` VARCHAR(191) NOT NULL,
    `fiscalYearId` VARCHAR(191) NOT NULL,
    `voucherTypeId` VARCHAR(191) NULL,
    `voucherSeriesId` VARCHAR(191) NULL,
    `voucherNumber` VARCHAR(50) NULL,
    `voucherDate` DATETIME(3) NOT NULL,
    `postingDate` DATETIME(3) NOT NULL,
    `description` TEXT NOT NULL,
    `reference` VARCHAR(100) NULL,
    `source` VARCHAR(50) NULL,
    `totalDebit` BIGINT NOT NULL DEFAULT 0,
    `totalCredit` BIGINT NOT NULL DEFAULT 0,
    `foreignTotalDebit` BIGINT NOT NULL DEFAULT 0,
    `foreignTotalCredit` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `isForeignCurrency` BOOLEAN NOT NULL DEFAULT false,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `postedById` VARCHAR(191) NULL,
    `postedAt` DATETIME(3) NULL,
    `reversedBatchId` VARCHAR(191) NULL,
    `recurringTemplateId` VARCHAR(191) NULL,
    `attachmentCount` INTEGER NOT NULL DEFAULT 0,
    `commentCount` INTEGER NOT NULL DEFAULT 0,
    `createdById` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `JournalBatch_batchNumber_key`(`batchNumber`),
    INDEX `JournalBatch_batchNumber_idx`(`batchNumber`),
    INDEX `JournalBatch_periodId_idx`(`periodId`),
    INDEX `JournalBatch_fiscalYearId_idx`(`fiscalYearId`),
    INDEX `JournalBatch_status_idx`(`status`),
    INDEX `JournalBatch_postingDate_idx`(`postingDate`),
    INDEX `JournalBatch_voucherDate_idx`(`voucherDate`),
    INDEX `JournalBatch_createdById_idx`(`createdById`),
    INDEX `JournalBatch_voucherTypeId_idx`(`voucherTypeId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `JournalEntryLine` (
    `id` VARCHAR(191) NOT NULL,
    `batchId` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `debitAmount` BIGINT NOT NULL DEFAULT 0,
    `creditAmount` BIGINT NOT NULL DEFAULT 0,
    `foreignDebitAmount` BIGINT NOT NULL DEFAULT 0,
    `foreignCreditAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `description` TEXT NULL,
    `costCenterId` VARCHAR(191) NULL,
    `departmentId` VARCHAR(191) NULL,
    `projectId` VARCHAR(191) NULL,
    `lineOrder` INTEGER NOT NULL,

    INDEX `JournalEntryLine_batchId_idx`(`batchId`),
    INDEX `JournalEntryLine_accountId_idx`(`accountId`),
    INDEX `JournalEntryLine_costCenterId_idx`(`costCenterId`),
    INDEX `JournalEntryLine_departmentId_idx`(`departmentId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `ExchangeRate` (
    `id` VARCHAR(191) NOT NULL,
    `fromCurrency` VARCHAR(3) NOT NULL,
    `toCurrency` VARCHAR(3) NOT NULL,
    `rate` DECIMAL(19, 6) NOT NULL,
    `rateType` ENUM('buy', 'sell', 'transfer', 'reference') NOT NULL DEFAULT 'reference',
    `validFrom` DATETIME(3) NOT NULL,
    `validTo` DATETIME(3) NOT NULL,
    `source` VARCHAR(100) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,

    INDEX `ExchangeRate_fromCurrency_toCurrency_idx`(`fromCurrency`, `toCurrency`),
    INDEX `ExchangeRate_validFrom_validTo_idx`(`validFrom`, `validTo`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `CostCenter` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `parentId` VARCHAR(191) NULL,
    `managerId` VARCHAR(191) NULL,
    `budgetHolderId` VARCHAR(191) NULL,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    `description` TEXT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `CostCenter_code_key`(`code`),
    INDEX `CostCenter_code_idx`(`code`),
    INDEX `CostCenter_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Department` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `parentId` VARCHAR(191) NULL,
    `headId` VARCHAR(191) NULL,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    `description` TEXT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `Department_code_key`(`code`),
    INDEX `Department_code_idx`(`code`),
    INDEX `Department_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Budget` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `type` ENUM('operational', 'capital', 'project', 'department') NOT NULL DEFAULT 'operational',
    `status` ENUM('draft', 'submitted', 'approved', 'rejected', 'closed') NOT NULL DEFAULT 'draft',
    `fiscalYearId` VARCHAR(191) NOT NULL,
    `costCenterId` VARCHAR(191) NULL,
    `departmentId` VARCHAR(191) NULL,
    `projectId` VARCHAR(191) NULL,
    `totalOriginalAmount` BIGINT NOT NULL DEFAULT 0,
    `totalCurrentAmount` BIGINT NOT NULL DEFAULT 0,
    `totalUsedAmount` BIGINT NOT NULL DEFAULT 0,
    `totalRemainingAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `description` TEXT NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `createdById` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `Budget_code_key`(`code`),
    INDEX `Budget_fiscalYearId_idx`(`fiscalYearId`),
    INDEX `Budget_costCenterId_idx`(`costCenterId`),
    INDEX `Budget_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `BudgetLine` (
    `id` VARCHAR(191) NOT NULL,
    `budgetId` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `originalAmount` BIGINT NOT NULL DEFAULT 0,
    `currentAmount` BIGINT NOT NULL DEFAULT 0,
    `usedAmount` BIGINT NOT NULL DEFAULT 0,
    `remainingAmount` BIGINT NOT NULL DEFAULT 0,
    `period1` BIGINT NOT NULL DEFAULT 0,
    `period2` BIGINT NOT NULL DEFAULT 0,
    `period3` BIGINT NOT NULL DEFAULT 0,
    `period4` BIGINT NOT NULL DEFAULT 0,
    `period5` BIGINT NOT NULL DEFAULT 0,
    `period6` BIGINT NOT NULL DEFAULT 0,
    `period7` BIGINT NOT NULL DEFAULT 0,
    `period8` BIGINT NOT NULL DEFAULT 0,
    `period9` BIGINT NOT NULL DEFAULT 0,
    `period10` BIGINT NOT NULL DEFAULT 0,
    `period11` BIGINT NOT NULL DEFAULT 0,
    `period12` BIGINT NOT NULL DEFAULT 0,

    INDEX `BudgetLine_budgetId_idx`(`budgetId`),
    INDEX `BudgetLine_accountId_idx`(`accountId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `AuditLog` (
    `id` VARCHAR(191) NOT NULL,
    `entityType` VARCHAR(50) NOT NULL,
    `entityId` VARCHAR(36) NOT NULL,
    `action` VARCHAR(50) NOT NULL,
    `changes` JSON NULL,
    `performedById` VARCHAR(191) NOT NULL,
    `performedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `ipAddress` VARCHAR(45) NULL,
    `userAgent` VARCHAR(255) NULL,
    `batchId` VARCHAR(191) NULL,

    INDEX `AuditLog_entityType_entityId_idx`(`entityType`, `entityId`),
    INDEX `AuditLog_performedById_idx`(`performedById`),
    INDEX `AuditLog_performedAt_idx`(`performedAt`),
    INDEX `AuditLog_batchId_idx`(`batchId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_types` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `category` ENUM('value_added_tax', 'corporate_income_tax', 'personal_income_tax', 'special_consumption_tax', 'natural_resource_tax', 'environmental_tax', 'customs_duty', 'land_tax', 'license_tax', 'other') NOT NULL,
    `nature` VARCHAR(20) NOT NULL,
    `basis` ENUM('revenue', 'profit', 'salary', 'consumption', 'resource_volume', 'land_area', 'customs_value', 'other') NOT NULL,
    `calculation_method` ENUM('direct', 'deduction', 'withholding', 'presumptive', 'hybrid') NOT NULL,
    `payment_method` ENUM('monthly', 'quarterly', 'annual', 'per_transaction', 'withholding') NOT NULL,
    `filing_frequency` ENUM('monthly', 'quarterly', 'annual', 'per_transaction') NOT NULL,
    `description` TEXT NULL,
    `legalReference` VARCHAR(255) NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT true,
    `requiresRegistration` BOOLEAN NOT NULL DEFAULT true,
    `requiresDeclaration` BOOLEAN NOT NULL DEFAULT true,
    `requiresPayment` BOOLEAN NOT NULL DEFAULT true,
    `hasWithholding` BOOLEAN NOT NULL DEFAULT false,
    `hasExemption` BOOLEAN NOT NULL DEFAULT false,
    `hasIncentive` BOOLEAN NOT NULL DEFAULT false,
    `priority` INTEGER NOT NULL DEFAULT 0,
    `parent_tax_type_id` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_types_code_key`(`code`),
    INDEX `tax_types_category_idx`(`category`),
    INDEX `tax_types_is_active_idx`(`is_active`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_codes` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `taxTypeId` VARCHAR(191) NOT NULL,
    `tax_rate_type` ENUM('percentage', 'fixed_amount', 'mixed') NOT NULL,
    `application` ENUM('sales', 'purchases', 'imports', 'exports', 'both') NOT NULL,
    `roundingMethod` VARCHAR(191) NOT NULL DEFAULT 'round',
    `precision` INTEGER NOT NULL DEFAULT 0,
    `description` TEXT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `isRecoverable` BOOLEAN NOT NULL DEFAULT true,
    `isRefundable` BOOLEAN NOT NULL DEFAULT false,
    `isDeductible` BOOLEAN NOT NULL DEFAULT true,
    `gl_tax_account_id` VARCHAR(191) NULL,
    `gl_recoverable_account_id` VARCHAR(191) NULL,
    `gl_expense_account_id` VARCHAR(191) NULL,
    `effectiveFrom` DATETIME(3) NOT NULL,
    `effectiveTo` DATETIME(3) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_codes_code_key`(`code`),
    INDEX `tax_codes_taxTypeId_idx`(`taxTypeId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_rates` (
    `id` VARCHAR(191) NOT NULL,
    `taxCodeId` VARCHAR(191) NOT NULL,
    `rate` DECIMAL(19, 6) NOT NULL,
    `rateType` ENUM('percentage', 'fixed_amount', 'mixed') NOT NULL DEFAULT 'percentage',
    `minimumAmount` BIGINT NULL,
    `maximumAmount` BIGINT NULL,
    `effectiveFrom` DATETIME(3) NOT NULL,
    `effectiveTo` DATETIME(3) NULL,
    `priority` INTEGER NOT NULL DEFAULT 0,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `tax_rates_taxCodeId_idx`(`taxCodeId`),
    INDEX `tax_rates_taxCodeId_effectiveFrom_effectiveTo_idx`(`taxCodeId`, `effectiveFrom`, `effectiveTo`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_authorities` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `taxOfficeCode` VARCHAR(20) NOT NULL,
    `jurisdictionLevel` VARCHAR(20) NOT NULL,
    `parentId` VARCHAR(191) NULL,
    `address` TEXT NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(255) NULL,
    `website` VARCHAR(255) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_authorities_code_key`(`code`),
    INDEX `tax_authorities_jurisdictionLevel_idx`(`jurisdictionLevel`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_regions` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `type` VARCHAR(30) NOT NULL,
    `provinceCode` VARCHAR(10) NULL,
    `districtCode` VARCHAR(10) NULL,
    `wardCode` VARCHAR(10) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_regions_code_key`(`code`),
    INDEX `tax_regions_type_idx`(`type`),
    INDEX `tax_regions_provinceCode_idx`(`provinceCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_registrations` (
    `id` VARCHAR(191) NOT NULL,
    `registrationNumber` VARCHAR(50) NOT NULL,
    `taxpayerId` VARCHAR(36) NOT NULL,
    `taxpayerName` VARCHAR(255) NOT NULL,
    `taxTypeId` VARCHAR(191) NOT NULL,
    `taxAuthorityId` VARCHAR(191) NULL,
    `status` ENUM('draft', 'submitted', 'active', 'suspended', 'cancelled', 'closed') NOT NULL DEFAULT 'draft',
    `registrationDate` DATETIME(3) NULL,
    `deregistrationDate` DATETIME(3) NULL,
    `suspensionDate` DATETIME(3) NULL,
    `reason` TEXT NULL,
    `submittedById` VARCHAR(191) NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_registrations_registrationNumber_key`(`registrationNumber`),
    INDEX `tax_registrations_taxpayerId_idx`(`taxpayerId`),
    INDEX `tax_registrations_taxTypeId_idx`(`taxTypeId`),
    INDEX `tax_registrations_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_exemptions` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(50) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `exemptionType` ENUM('full_exemption', 'partial_exemption', 'reduced_rate', 'tax_holiday', 'investment_incentive', 'export_incentive', 'special_economic_zone') NOT NULL,
    `status` ENUM('active', 'used', 'expired', 'revoked') NOT NULL DEFAULT 'active',
    `taxTypeId` VARCHAR(191) NOT NULL,
    `taxCodeId` VARCHAR(191) NULL,
    `taxpayerId` VARCHAR(36) NULL,
    `exemptPercentage` DECIMAL(5, 2) NULL,
    `exemptAmount` BIGINT NULL,
    `maxAmount` BIGINT NULL,
    `validFrom` DATETIME(3) NOT NULL,
    `validTo` DATETIME(3) NULL,
    `issuingAuthority` VARCHAR(255) NULL,
    `referenceNumber` VARCHAR(100) NULL,
    `reason` TEXT NULL,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_exemptions_code_key`(`code`),
    INDEX `tax_exemptions_taxTypeId_idx`(`taxTypeId`),
    INDEX `tax_exemptions_taxpayerId_idx`(`taxpayerId`),
    INDEX `tax_exemptions_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_returns` (
    `id` VARCHAR(191) NOT NULL,
    `returnNumber` VARCHAR(50) NOT NULL,
    `returnType` ENUM('original', 'amended', 'supplementary', 'final') NOT NULL DEFAULT 'original',
    `status` ENUM('draft', 'prepared', 'submitted', 'accepted', 'rejected', 'amended', 'closed') NOT NULL DEFAULT 'draft',
    `taxTypeId` VARCHAR(191) NOT NULL,
    `taxpayerId` VARCHAR(36) NOT NULL,
    `taxpayerName` VARCHAR(255) NOT NULL,
    `periodId` VARCHAR(36) NOT NULL,
    `periodName` VARCHAR(100) NOT NULL,
    `fiscalYearId` VARCHAR(191) NOT NULL,
    `totalTaxAmount` BIGINT NOT NULL DEFAULT 0,
    `totalPaidAmount` BIGINT NOT NULL DEFAULT 0,
    `totalDueAmount` BIGINT NOT NULL DEFAULT 0,
    `totalCreditAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `originalReturnId` VARCHAR(191) NULL,
    `submittedById` VARCHAR(191) NULL,
    `submittedAt` DATETIME(3) NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_returns_returnNumber_key`(`returnNumber`),
    INDEX `tax_returns_taxpayerId_idx`(`taxpayerId`),
    INDEX `tax_returns_taxTypeId_idx`(`taxTypeId`),
    INDEX `tax_returns_status_idx`(`status`),
    INDEX `tax_returns_periodId_idx`(`periodId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_payments` (
    `id` VARCHAR(191) NOT NULL,
    `paymentNumber` VARCHAR(50) NOT NULL,
    `taxReturnId` VARCHAR(191) NULL,
    `taxTypeId` VARCHAR(191) NOT NULL,
    `taxpayerId` VARCHAR(36) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `paidAmount` BIGINT NOT NULL DEFAULT 0,
    `refundAmount` BIGINT NOT NULL DEFAULT 0,
    `status` ENUM('pending', 'due', 'paid', 'overdue', 'partially_paid', 'refunded', 'cancelled', 'fully_refunded', 'failed') NOT NULL DEFAULT 'pending',
    `paymentDate` DATETIME(3) NULL,
    `dueDate` DATETIME(3) NULL,
    `paymentMethod` VARCHAR(50) NULL,
    `reference` VARCHAR(100) NULL,
    `bankAccount` VARCHAR(50) NULL,
    `glBatchId` VARCHAR(191) NULL,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `tax_payments_paymentNumber_key`(`paymentNumber`),
    INDEX `tax_payments_taxReturnId_idx`(`taxReturnId`),
    INDEX `tax_payments_taxpayerId_idx`(`taxpayerId`),
    INDEX `tax_payments_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `tax_determination_rules` (
    `id` VARCHAR(191) NOT NULL,
    `taxTypeId` VARCHAR(191) NOT NULL,
    `ruleOrder` INTEGER NOT NULL,
    `conditionField` VARCHAR(50) NOT NULL,
    `conditionOperator` VARCHAR(20) NOT NULL,
    `conditionValue` VARCHAR(255) NOT NULL,
    `resultTaxCodeId` VARCHAR(36) NULL,
    `resultRate` DECIMAL(19, 6) NULL,
    `effectiveFrom` DATETIME(3) NOT NULL,
    `effectiveTo` DATETIME(3) NULL,
    `description` TEXT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `tax_determination_rules_taxTypeId_idx`(`taxTypeId`),
    INDEX `tax_determination_rules_effectiveFrom_effectiveTo_idx`(`effectiveFrom`, `effectiveTo`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_account_classes` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(1) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `classType` ENUM('asset', 'liability', 'equity', 'revenue', 'expense', 'cost_of_goods_sold', 'other_income', 'other_expense', 'manufacturing') NOT NULL,
    `description` TEXT NULL,
    `displayOrder` INTEGER NOT NULL DEFAULT 0,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `coa_account_classes_code_key`(`code`),
    INDEX `coa_account_classes_code_idx`(`code`),
    INDEX `coa_account_classes_classType_idx`(`classType`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_account_types` (
    `id` VARCHAR(191) NOT NULL,
    `classId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(10) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `category` ENUM('current_asset', 'non_current_asset', 'current_liability', 'non_current_liability', 'equity', 'revenue', 'operating_expense', 'manufacturing_cost', 'cost_of_goods_sold', 'other_income', 'other_expense', 'off_balance_sheet') NOT NULL,
    `subType` ENUM('cash', 'bank', 'receivable', 'inventory', 'fixed_asset', 'intangible_asset', 'investment', 'payable', 'tax_payable', 'loan', 'equity_capital', 'retained_earnings', 'revenue', 'cost_of_sales', 'salary', 'depreciation', 'tax_expense', 'other') NULL,
    `nature` ENUM('debit', 'credit') NOT NULL,
    `description` TEXT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `displayOrder` INTEGER NOT NULL DEFAULT 0,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `parentTypeId` VARCHAR(191) NULL,

    UNIQUE INDEX `coa_account_types_code_key`(`code`),
    INDEX `coa_account_types_classId_idx`(`classId`),
    INDEX `coa_account_types_code_idx`(`code`),
    INDEX `coa_account_types_category_idx`(`category`),
    INDEX `coa_account_types_subType_idx`(`subType`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_account_extensions` (
    `id` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `typeId` VARCHAR(191) NULL,
    `effectiveStatus` ENUM('draft', 'active', 'suspended', 'closed', 'archived') NOT NULL DEFAULT 'active',
    `effectiveFrom` DATETIME(3) NULL,
    `effectiveTo` DATETIME(3) NULL,
    `statusReason` TEXT NULL,
    `allowAutoPosting` BOOLEAN NOT NULL DEFAULT true,
    `requireApproval` BOOLEAN NOT NULL DEFAULT false,
    `budgetControlLevel` ENUM('none', 'warning', 'strict') NOT NULL DEFAULT 'none',
    `budgetCheckMessage` TEXT NULL,
    `defaultCostCenterId` VARCHAR(191) NULL,
    `defaultDepartmentId` VARCHAR(191) NULL,
    `defaultProjectId` VARCHAR(191) NULL,
    `defaultBranchId` VARCHAR(191) NULL,
    `costCenterRequired` ENUM('optional', 'recommended', 'required', 'prohibited') NOT NULL DEFAULT 'optional',
    `departmentRequired` ENUM('optional', 'recommended', 'required', 'prohibited') NOT NULL DEFAULT 'optional',
    `projectRequired` ENUM('optional', 'recommended', 'required', 'prohibited') NOT NULL DEFAULT 'optional',
    `branchRequired` ENUM('optional', 'recommended', 'required', 'prohibited') NOT NULL DEFAULT 'optional',
    `profitCenterRequired` ENUM('optional', 'recommended', 'required', 'prohibited') NOT NULL DEFAULT 'optional',
    `isCashAccount` BOOLEAN NOT NULL DEFAULT false,
    `isBankAccount` BOOLEAN NOT NULL DEFAULT false,
    `isTaxAccount` BOOLEAN NOT NULL DEFAULT false,
    `isInventoryAccount` BOOLEAN NOT NULL DEFAULT false,
    `isReceivableAccount` BOOLEAN NOT NULL DEFAULT false,
    `isPayableAccount` BOOLEAN NOT NULL DEFAULT false,
    `isIntercompanyAccount` BOOLEAN NOT NULL DEFAULT false,
    `defaultTaxCodeId` VARCHAR(36) NULL,
    `defaultTaxRateId` VARCHAR(36) NULL,
    `cashFlowCode` VARCHAR(10) NULL,
    `financialStatementCode` VARCHAR(20) NULL,
    `financialStatementNote` TEXT NULL,
    `createdById` VARCHAR(191) NULL,
    `updatedById` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `coa_account_extensions_accountId_key`(`accountId`),
    INDEX `coa_account_extensions_typeId_idx`(`typeId`),
    INDEX `coa_account_extensions_effectiveStatus_idx`(`effectiveStatus`),
    INDEX `coa_account_extensions_isCashAccount_idx`(`isCashAccount`),
    INDEX `coa_account_extensions_isBankAccount_idx`(`isBankAccount`),
    INDEX `coa_account_extensions_isTaxAccount_idx`(`isTaxAccount`),
    INDEX `coa_account_extensions_isInventoryAccount_idx`(`isInventoryAccount`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_account_mappings` (
    `id` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `mappingStandard` ENUM('ifrs', 'vas', 'cash_flow', 'tax', 'statutory', 'management') NOT NULL,
    `mappingType` ENUM('direct', 'aggregation', 'percentage', 'formula', 'manual') NOT NULL,
    `targetCode` VARCHAR(50) NOT NULL,
    `targetName` VARCHAR(255) NULL,
    `mappingRule` TEXT NULL,
    `percentage` DECIMAL(7, 4) NULL,
    `effectiveFrom` DATETIME(3) NOT NULL,
    `effectiveTo` DATETIME(3) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `coa_account_mappings_accountId_idx`(`accountId`),
    INDEX `coa_account_mappings_mappingStandard_idx`(`mappingStandard`),
    INDEX `coa_account_mappings_targetCode_idx`(`targetCode`),
    UNIQUE INDEX `coa_account_mappings_accountId_mappingStandard_targetCode_key`(`accountId`, `mappingStandard`, `targetCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_hierarchy_changes` (
    `id` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `oldParentId` VARCHAR(191) NULL,
    `newParentId` VARCHAR(191) NULL,
    `changedById` VARCHAR(191) NOT NULL,
    `changedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `reason` TEXT NULL,

    INDEX `coa_hierarchy_changes_accountId_idx`(`accountId`),
    INDEX `coa_hierarchy_changes_changedAt_idx`(`changedAt`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_code_changes` (
    `id` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `oldCode` VARCHAR(20) NOT NULL,
    `newCode` VARCHAR(20) NOT NULL,
    `changedById` VARCHAR(191) NOT NULL,
    `changedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `reason` TEXT NULL,

    INDEX `coa_code_changes_accountId_idx`(`accountId`),
    INDEX `coa_code_changes_changedAt_idx`(`changedAt`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `coa_status_changes` (
    `id` VARCHAR(191) NOT NULL,
    `accountId` VARCHAR(191) NOT NULL,
    `oldStatus` ENUM('draft', 'active', 'suspended', 'closed', 'archived') NOT NULL,
    `newStatus` ENUM('draft', 'active', 'suspended', 'closed', 'archived') NOT NULL,
    `changedById` VARCHAR(191) NOT NULL,
    `changedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `reason` TEXT NULL,

    INDEX `coa_status_changes_accountId_idx`(`accountId`),
    INDEX `coa_status_changes_changedAt_idx`(`changedAt`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_companies` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `taxCode` VARCHAR(20) NULL,
    `address` TEXT NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(255) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_companies_code_key`(`code`),
    INDEX `cm_companies_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_locations` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `address` TEXT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_locations_code_key`(`code`),
    INDEX `cm_cash_locations_companyId_idx`(`companyId`),
    INDEX `cm_cash_locations_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_boxes` (
    `id` VARCHAR(191) NOT NULL,
    `locationId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `boxType` ENUM('cash_register', 'cash_drawer', 'safe_deposit', 'petty_cash', 'teller', 'atm', 'pos_terminal', 'vault', 'cash_office', 'other') NOT NULL,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `minBalance` BIGINT NOT NULL DEFAULT 0,
    `maxBalance` BIGINT NULL DEFAULT 0,
    `currentBalance` BIGINT NOT NULL DEFAULT 0,
    `allowNegative` BOOLEAN NOT NULL DEFAULT false,
    `status` ENUM('active', 'inactive', 'suspended', 'closed', 'archived') NOT NULL DEFAULT 'active',
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_boxes_code_key`(`code`),
    INDEX `cm_cash_boxes_locationId_idx`(`locationId`),
    INDEX `cm_cash_boxes_code_idx`(`code`),
    INDEX `cm_cash_boxes_boxType_idx`(`boxType`),
    INDEX `cm_cash_boxes_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_registers` (
    `id` VARCHAR(191) NOT NULL,
    `cashBoxId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `serialNumber` VARCHAR(100) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_registers_code_key`(`code`),
    INDEX `cm_cash_registers_cashBoxId_idx`(`cashBoxId`),
    INDEX `cm_cash_registers_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cashiers` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `employeeId` VARCHAR(36) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `effectiveFrom` DATETIME(3) NOT NULL,
    `effectiveTo` DATETIME(3) NULL,
    `maxCashAmount` BIGINT NOT NULL DEFAULT 0,
    `maxDailyAmount` BIGINT NOT NULL DEFAULT 0,
    `requireSupervisor` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cashiers_code_key`(`code`),
    INDEX `cm_cashiers_companyId_idx`(`companyId`),
    INDEX `cm_cashiers_employeeId_idx`(`employeeId`),
    INDEX `cm_cashiers_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_sessions` (
    `id` VARCHAR(191) NOT NULL,
    `sessionNumber` VARCHAR(50) NOT NULL,
    `cashBoxId` VARCHAR(191) NOT NULL,
    `cashRegisterId` VARCHAR(191) NULL,
    `cashierId` VARCHAR(191) NOT NULL,
    `status` ENUM('pending', 'open', 'counting', 'closed', 'reconciled', 'disputed') NOT NULL DEFAULT 'pending',
    `openedAt` DATETIME(3) NOT NULL,
    `closedAt` DATETIME(3) NULL,
    `openedBalance` BIGINT NOT NULL DEFAULT 0,
    `expectedBalance` BIGINT NOT NULL DEFAULT 0,
    `countedBalance` BIGINT NOT NULL DEFAULT 0,
    `difference` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_sessions_sessionNumber_key`(`sessionNumber`),
    INDEX `cm_cash_sessions_cashBoxId_idx`(`cashBoxId`),
    INDEX `cm_cash_sessions_cashRegisterId_idx`(`cashRegisterId`),
    INDEX `cm_cash_sessions_cashierId_idx`(`cashierId`),
    INDEX `cm_cash_sessions_sessionNumber_idx`(`sessionNumber`),
    INDEX `cm_cash_sessions_status_idx`(`status`),
    INDEX `cm_cash_sessions_openedAt_closedAt_idx`(`openedAt`, `closedAt`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_counts` (
    `id` VARCHAR(191) NOT NULL,
    `sessionId` VARCHAR(191) NOT NULL,
    `cashBoxId` VARCHAR(191) NOT NULL,
    `countMethod` ENUM('manual', 'scanner', 'scale', 'hybrid') NOT NULL DEFAULT 'manual',
    `countType` ENUM('in', 'out') NOT NULL DEFAULT 'in',
    `denomination` VARCHAR(50) NULL,
    `quantity` INTEGER NOT NULL DEFAULT 0,
    `unitValue` BIGINT NOT NULL DEFAULT 0,
    `totalValue` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `countedById` VARCHAR(191) NOT NULL,
    `countedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `verifiedById` VARCHAR(191) NULL,
    `verifiedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `cm_cash_counts_sessionId_idx`(`sessionId`),
    INDEX `cm_cash_counts_cashBoxId_idx`(`cashBoxId`),
    INDEX `cm_cash_counts_countedById_idx`(`countedById`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_differences` (
    `id` VARCHAR(191) NOT NULL,
    `sessionId` VARCHAR(191) NOT NULL,
    `diffType` ENUM('shortage', 'overage', 'counterfeit', 'dispute', 'adjustment') NOT NULL,
    `expectedAmount` BIGINT NOT NULL DEFAULT 0,
    `actualAmount` BIGINT NOT NULL DEFAULT 0,
    `differenceAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `status` ENUM('pending', 'investigated', 'approved', 'rejected', 'resolved', 'written_off') NOT NULL DEFAULT 'pending',
    `reason` TEXT NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `resolvedById` VARCHAR(191) NULL,
    `resolvedAt` DATETIME(3) NULL,
    `resolution` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `cm_cash_differences_sessionId_idx`(`sessionId`),
    INDEX `cm_cash_differences_status_idx`(`status`),
    INDEX `cm_cash_differences_diffType_idx`(`diffType`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_petty_cash_funds` (
    `id` VARCHAR(191) NOT NULL,
    `locationId` VARCHAR(191) NOT NULL,
    `fundCode` VARCHAR(20) NOT NULL,
    `fundName` VARCHAR(255) NOT NULL,
    `fundBalance` BIGINT NOT NULL DEFAULT 0,
    `maximumBalance` BIGINT NOT NULL DEFAULT 0,
    `minimumBalance` BIGINT NOT NULL DEFAULT 0,
    `replenishThreshold` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `holderId` VARCHAR(36) NULL,
    `status` ENUM('active', 'suspended', 'replenishing', 'closed', 'audited') NOT NULL DEFAULT 'active',
    `description` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_petty_cash_funds_fundCode_key`(`fundCode`),
    INDEX `cm_petty_cash_funds_locationId_idx`(`locationId`),
    INDEX `cm_petty_cash_funds_fundCode_idx`(`fundCode`),
    INDEX `cm_petty_cash_funds_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_petty_cash_replenishments` (
    `id` VARCHAR(191) NOT NULL,
    `fundId` VARCHAR(191) NOT NULL,
    `replenishNumber` VARCHAR(50) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `replenishDate` DATETIME(3) NOT NULL,
    `receivedById` VARCHAR(36) NULL,
    `reference` VARCHAR(100) NULL,
    `notes` TEXT NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_petty_cash_replenishments_replenishNumber_key`(`replenishNumber`),
    INDEX `cm_petty_cash_replenishments_fundId_idx`(`fundId`),
    INDEX `cm_petty_cash_replenishments_replenishNumber_idx`(`replenishNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_advances` (
    `id` VARCHAR(191) NOT NULL,
    `advanceNumber` VARCHAR(50) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `employeeId` VARCHAR(36) NOT NULL,
    `employeeName` VARCHAR(255) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `settledAmount` BIGINT NOT NULL DEFAULT 0,
    `outstandingAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `advanceDate` DATETIME(3) NOT NULL,
    `expectedSettleDate` DATETIME(3) NULL,
    `purpose` TEXT NOT NULL,
    `status` ENUM('draft', 'approved', 'disbursed', 'settled', 'partially_settled', 'overdue', 'written_off', 'cancelled') NOT NULL DEFAULT 'draft',
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `disbursedById` VARCHAR(191) NULL,
    `disbursedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_advances_advanceNumber_key`(`advanceNumber`),
    INDEX `cm_cash_advances_companyId_idx`(`companyId`),
    INDEX `cm_cash_advances_employeeId_idx`(`employeeId`),
    INDEX `cm_cash_advances_status_idx`(`status`),
    INDEX `cm_cash_advances_advanceDate_idx`(`advanceDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_advance_settlements` (
    `id` VARCHAR(191) NOT NULL,
    `advanceId` VARCHAR(191) NOT NULL,
    `settlementNumber` VARCHAR(50) NOT NULL,
    `settlementDate` DATETIME(3) NOT NULL,
    `totalAmount` BIGINT NOT NULL DEFAULT 0,
    `returnAmount` BIGINT NOT NULL DEFAULT 0,
    `expenseAmount` BIGINT NOT NULL DEFAULT 0,
    `additionalAdvance` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `receiptCount` INTEGER NOT NULL DEFAULT 0,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_advance_settlements_settlementNumber_key`(`settlementNumber`),
    INDEX `cm_advance_settlements_advanceId_idx`(`advanceId`),
    INDEX `cm_advance_settlements_settlementNumber_idx`(`settlementNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_transfers` (
    `id` VARCHAR(191) NOT NULL,
    `transferNumber` VARCHAR(50) NOT NULL,
    `fromLocationId` VARCHAR(191) NOT NULL,
    `toLocationId` VARCHAR(191) NOT NULL,
    `fromCashBoxId` VARCHAR(191) NULL,
    `toCashBoxId` VARCHAR(191) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `transferDate` DATETIME(3) NOT NULL,
    `expectedArrivalDate` DATETIME(3) NULL,
    `actualArrivalDate` DATETIME(3) NULL,
    `status` ENUM('draft', 'approved', 'in_transit', 'completed', 'cancelled', 'disputed') NOT NULL DEFAULT 'draft',
    `sentById` VARCHAR(191) NULL,
    `receivedById` VARCHAR(191) NULL,
    `reference` VARCHAR(100) NULL,
    `notes` TEXT NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_transfers_transferNumber_key`(`transferNumber`),
    INDEX `cm_cash_transfers_fromLocationId_idx`(`fromLocationId`),
    INDEX `cm_cash_transfers_toLocationId_idx`(`toLocationId`),
    INDEX `cm_cash_transfers_transferNumber_idx`(`transferNumber`),
    INDEX `cm_cash_transfers_status_idx`(`status`),
    INDEX `cm_cash_transfers_transferDate_idx`(`transferDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_receipts` (
    `id` VARCHAR(191) NOT NULL,
    `receiptNumber` VARCHAR(50) NOT NULL,
    `receiptDate` DATETIME(3) NOT NULL,
    `cashBoxId` VARCHAR(191) NOT NULL,
    `sessionId` VARCHAR(191) NULL,
    `cashierId` VARCHAR(191) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `vndAmount` BIGINT NOT NULL DEFAULT 0,
    `paidBy` VARCHAR(255) NULL,
    `paidById` VARCHAR(36) NULL,
    `paymentMethod` ENUM('cash', 'cheque', 'bank_transfer', 'wire_transfer', 'intercompany_transfer', 'card', 'e_wallet', 'offset', 'other') NOT NULL DEFAULT 'cash',
    `reference` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `status` ENUM('draft', 'issued', 'approved', 'posted', 'cancelled', 'reversed') NOT NULL DEFAULT 'draft',
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `postedById` VARCHAR(191) NULL,
    `postedAt` DATETIME(3) NULL,
    `reversedById` VARCHAR(191) NULL,
    `reversedAt` DATETIME(3) NULL,
    `reversalReason` TEXT NULL,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_receipts_receiptNumber_key`(`receiptNumber`),
    INDEX `cm_cash_receipts_cashBoxId_idx`(`cashBoxId`),
    INDEX `cm_cash_receipts_sessionId_idx`(`sessionId`),
    INDEX `cm_cash_receipts_cashierId_idx`(`cashierId`),
    INDEX `cm_cash_receipts_receiptNumber_idx`(`receiptNumber`),
    INDEX `cm_cash_receipts_receiptDate_idx`(`receiptDate`),
    INDEX `cm_cash_receipts_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_receipt_attachments` (
    `id` VARCHAR(191) NOT NULL,
    `receiptId` VARCHAR(191) NOT NULL,
    `fileName` VARCHAR(255) NOT NULL,
    `filePath` VARCHAR(500) NOT NULL,
    `fileSize` INTEGER NOT NULL DEFAULT 0,
    `mimeType` VARCHAR(100) NULL,
    `attachmentType` ENUM('receipt', 'invoice', 'contract', 'supporting_document', 'image', 'pdf', 'other') NOT NULL DEFAULT 'other',
    `uploadedById` VARCHAR(191) NOT NULL,
    `uploadedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `description` TEXT NULL,

    INDEX `cm_receipt_attachments_receiptId_idx`(`receiptId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_payments` (
    `id` VARCHAR(191) NOT NULL,
    `paymentNumber` VARCHAR(50) NOT NULL,
    `paymentDate` DATETIME(3) NOT NULL,
    `cashBoxId` VARCHAR(191) NOT NULL,
    `sessionId` VARCHAR(191) NULL,
    `cashierId` VARCHAR(191) NOT NULL,
    `payeeName` VARCHAR(255) NOT NULL,
    `payeeId` VARCHAR(36) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `vndAmount` BIGINT NOT NULL DEFAULT 0,
    `paymentMethod` ENUM('cash', 'cheque', 'bank_transfer', 'wire_transfer', 'intercompany_transfer', 'card', 'e_wallet', 'offset', 'other') NOT NULL DEFAULT 'cash',
    `reference` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `status` ENUM('draft', 'submitted', 'approved', 'paid', 'posted', 'cancelled', 'rejected', 'reversed') NOT NULL DEFAULT 'draft',
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `paidById` VARCHAR(191) NULL,
    `paidAt` DATETIME(3) NULL,
    `postedById` VARCHAR(191) NULL,
    `postedAt` DATETIME(3) NULL,
    `reversedById` VARCHAR(191) NULL,
    `reversedAt` DATETIME(3) NULL,
    `reversalReason` TEXT NULL,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_payments_paymentNumber_key`(`paymentNumber`),
    INDEX `cm_cash_payments_cashBoxId_idx`(`cashBoxId`),
    INDEX `cm_cash_payments_sessionId_idx`(`sessionId`),
    INDEX `cm_cash_payments_cashierId_idx`(`cashierId`),
    INDEX `cm_cash_payments_paymentNumber_idx`(`paymentNumber`),
    INDEX `cm_cash_payments_paymentDate_idx`(`paymentDate`),
    INDEX `cm_cash_payments_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_payment_attachments` (
    `id` VARCHAR(191) NOT NULL,
    `paymentId` VARCHAR(191) NOT NULL,
    `fileName` VARCHAR(255) NOT NULL,
    `filePath` VARCHAR(500) NOT NULL,
    `fileSize` INTEGER NOT NULL DEFAULT 0,
    `mimeType` VARCHAR(100) NULL,
    `attachmentType` ENUM('receipt', 'invoice', 'contract', 'supporting_document', 'image', 'pdf', 'other') NOT NULL DEFAULT 'other',
    `uploadedById` VARCHAR(191) NOT NULL,
    `uploadedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `description` TEXT NULL,

    INDEX `cm_payment_attachments_paymentId_idx`(`paymentId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_banks` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `swiftCode` VARCHAR(11) NULL,
    `routingNumber` VARCHAR(20) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_banks_code_key`(`code`),
    INDEX `cm_banks_companyId_idx`(`companyId`),
    INDEX `cm_banks_code_idx`(`code`),
    INDEX `cm_banks_swiftCode_idx`(`swiftCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_branches` (
    `id` VARCHAR(191) NOT NULL,
    `bankId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `address` TEXT NULL,
    `phone` VARCHAR(20) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_bank_branches_code_key`(`code`),
    INDEX `cm_bank_branches_bankId_idx`(`bankId`),
    INDEX `cm_bank_branches_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_accounts` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `bankId` VARCHAR(191) NOT NULL,
    `branchId` VARCHAR(191) NULL,
    `accountNumber` VARCHAR(50) NOT NULL,
    `accountName` VARCHAR(255) NOT NULL,
    `accountType` ENUM('current', 'savings', 'deposit', 'loan', 'treasury', 'suspense', 'payroll', 'tax', 'intercompany', 'virtual') NOT NULL DEFAULT 'current',
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `status` ENUM('active', 'inactive', 'suspended', 'closed', 'blocked') NOT NULL DEFAULT 'active',
    `currentBalance` BIGINT NOT NULL DEFAULT 0,
    `availableBalance` BIGINT NOT NULL DEFAULT 0,
    `blockedBalance` BIGINT NOT NULL DEFAULT 0,
    `glAccountId` VARCHAR(191) NULL,
    `isVirtual` BOOLEAN NOT NULL DEFAULT false,
    `parentAccountId` VARCHAR(191) NULL,
    `openingDate` DATETIME(3) NOT NULL,
    `closingDate` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `cm_bank_accounts_companyId_idx`(`companyId`),
    INDEX `cm_bank_accounts_bankId_idx`(`bankId`),
    INDEX `cm_bank_accounts_accountNumber_idx`(`accountNumber`),
    INDEX `cm_bank_accounts_status_idx`(`status`),
    INDEX `cm_bank_accounts_currencyCode_idx`(`currencyCode`),
    UNIQUE INDEX `cm_bank_accounts_bankId_accountNumber_key`(`bankId`, `accountNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cheque_books` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `chequeBookNumber` VARCHAR(50) NOT NULL,
    `startNumber` INTEGER NOT NULL DEFAULT 1,
    `endNumber` INTEGER NOT NULL DEFAULT 100,
    `currentNumber` INTEGER NOT NULL DEFAULT 1,
    `status` ENUM('active', 'used', 'full_used', 'cancelled', 'lost') NOT NULL DEFAULT 'active',
    `issuedDate` DATETIME(3) NOT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cheque_books_chequeBookNumber_key`(`chequeBookNumber`),
    INDEX `cm_cheque_books_bankAccountId_idx`(`bankAccountId`),
    INDEX `cm_cheque_books_chequeBookNumber_idx`(`chequeBookNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cheques` (
    `id` VARCHAR(191) NOT NULL,
    `chequeBookId` VARCHAR(191) NOT NULL,
    `chequeNumber` INTEGER NOT NULL,
    `chequeType` ENUM('personal', 'corporate', 'cashier', 'certified', 'travellers', 'government') NOT NULL DEFAULT 'corporate',
    `payeeName` VARCHAR(255) NULL,
    `payeeId` VARCHAR(36) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `issueDate` DATETIME(3) NULL,
    `depositDate` DATETIME(3) NULL,
    `clearingDate` DATETIME(3) NULL,
    `returnedDate` DATETIME(3) NULL,
    `voidDate` DATETIME(3) NULL,
    `status` ENUM('unissued', 'issued', 'deposited', 'cleared', 'returned', 'cancelled', 'stopped', 'voided', 'reconciled') NOT NULL DEFAULT 'unissued',
    `reference` VARCHAR(100) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `cm_cheques_chequeBookId_idx`(`chequeBookId`),
    INDEX `cm_cheques_chequeNumber_idx`(`chequeNumber`),
    INDEX `cm_cheques_status_idx`(`status`),
    UNIQUE INDEX `cm_cheques_chequeBookId_chequeNumber_key`(`chequeBookId`, `chequeNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_transfers` (
    `id` VARCHAR(191) NOT NULL,
    `transferNumber` VARCHAR(50) NOT NULL,
    `transferType` ENUM('internal', 'intercompany', 'domestic', 'international', 'swift', 'wire', 'ach', 'sepa') NOT NULL,
    `fromAccountId` VARCHAR(191) NOT NULL,
    `toAccountId` VARCHAR(191) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `vndAmount` BIGINT NOT NULL DEFAULT 0,
    `transferDate` DATETIME(3) NOT NULL,
    `valueDate` DATETIME(3) NULL,
    `reference` VARCHAR(100) NULL,
    `swiftMessage` TEXT NULL,
    `beneficiaryName` VARCHAR(255) NULL,
    `beneficiaryBank` VARCHAR(255) NULL,
    `beneficiaryAccount` VARCHAR(50) NULL,
    `intermediaryBank` VARCHAR(255) NULL,
    `fees` BIGINT NOT NULL DEFAULT 0,
    `status` ENUM('draft', 'submitted', 'approved', 'sent', 'completed', 'failed', 'reversed', 'cancelled') NOT NULL DEFAULT 'draft',
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `executedById` VARCHAR(191) NULL,
    `executedAt` DATETIME(3) NULL,
    `completedAt` DATETIME(3) NULL,
    `failureReason` TEXT NULL,
    `notes` TEXT NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_bank_transfers_transferNumber_key`(`transferNumber`),
    INDEX `cm_bank_transfers_fromAccountId_idx`(`fromAccountId`),
    INDEX `cm_bank_transfers_toAccountId_idx`(`toAccountId`),
    INDEX `cm_bank_transfers_transferNumber_idx`(`transferNumber`),
    INDEX `cm_bank_transfers_status_idx`(`status`),
    INDEX `cm_bank_transfers_transferDate_idx`(`transferDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_statements` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `statementNumber` VARCHAR(50) NOT NULL,
    `periodStart` DATETIME(3) NOT NULL,
    `periodEnd` DATETIME(3) NOT NULL,
    `openingBalance` BIGINT NOT NULL DEFAULT 0,
    `closingBalance` BIGINT NOT NULL DEFAULT 0,
    `totalDebit` BIGINT NOT NULL DEFAULT 0,
    `totalCredit` BIGINT NOT NULL DEFAULT 0,
    `importedAt` DATETIME(3) NULL,
    `importedBy` VARCHAR(191) NULL,
    `source` VARCHAR(50) NULL,
    `isReconciled` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `cm_bank_statements_bankAccountId_idx`(`bankAccountId`),
    INDEX `cm_bank_statements_periodStart_periodEnd_idx`(`periodStart`, `periodEnd`),
    UNIQUE INDEX `cm_bank_statements_bankAccountId_statementNumber_key`(`bankAccountId`, `statementNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_statement_lines` (
    `id` VARCHAR(191) NOT NULL,
    `statementId` VARCHAR(191) NOT NULL,
    `lineDate` DATETIME(3) NOT NULL,
    `valueDate` DATETIME(3) NULL,
    `description` TEXT NULL,
    `reference` VARCHAR(100) NULL,
    `chequeNumber` VARCHAR(50) NULL,
    `lineType` ENUM('debit', 'credit', 'fee', 'interest', 'chargeback', 'reversal', 'other') NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `runningBalance` BIGINT NOT NULL DEFAULT 0,
    `isMatched` BOOLEAN NOT NULL DEFAULT false,
    `matchedToId` VARCHAR(36) NULL,
    `matchedToType` VARCHAR(50) NULL,
    `matchedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `cm_bank_statement_lines_statementId_idx`(`statementId`),
    INDEX `cm_bank_statement_lines_lineDate_idx`(`lineDate`),
    INDEX `cm_bank_statement_lines_isMatched_idx`(`isMatched`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_reconciliations` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `bankStatementId` VARCHAR(191) NOT NULL,
    `reconciliationNumber` VARCHAR(50) NOT NULL,
    `reconciliationDate` DATETIME(3) NOT NULL,
    `statementBalance` BIGINT NOT NULL DEFAULT 0,
    `bookBalance` BIGINT NOT NULL DEFAULT 0,
    `difference` BIGINT NOT NULL DEFAULT 0,
    `status` ENUM('open', 'in_progress', 'matched', 'difference_found', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    `matchedCount` INTEGER NOT NULL DEFAULT 0,
    `unmatchedCount` INTEGER NOT NULL DEFAULT 0,
    `preparedById` VARCHAR(191) NULL,
    `reviewedById` VARCHAR(191) NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_bank_reconciliations_reconciliationNumber_key`(`reconciliationNumber`),
    INDEX `cm_bank_reconciliations_bankAccountId_idx`(`bankAccountId`),
    INDEX `cm_bank_reconciliations_bankStatementId_idx`(`bankStatementId`),
    INDEX `cm_bank_reconciliations_reconciliationNumber_idx`(`reconciliationNumber`),
    INDEX `cm_bank_reconciliations_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_bank_reconciliation_items` (
    `id` VARCHAR(191) NOT NULL,
    `reconciliationId` VARCHAR(191) NOT NULL,
    `statementLineId` VARCHAR(191) NULL,
    `sourceType` VARCHAR(50) NOT NULL,
    `sourceId` VARCHAR(36) NOT NULL,
    `sourceReference` VARCHAR(100) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `matchType` VARCHAR(20) NOT NULL,
    `matchDate` DATETIME(3) NOT NULL,
    `isClearItem` BOOLEAN NOT NULL DEFAULT true,
    `notes` TEXT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `cm_bank_reconciliation_items_reconciliationId_idx`(`reconciliationId`),
    INDEX `cm_bank_reconciliation_items_statementLineId_idx`(`statementLineId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_forecasts` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `forecastNumber` VARCHAR(50) NOT NULL,
    `forecastName` VARCHAR(255) NOT NULL,
    `periodType` ENUM('daily', 'weekly', 'monthly', 'quarterly', 'custom') NOT NULL DEFAULT 'daily',
    `periodStart` DATETIME(3) NOT NULL,
    `periodEnd` DATETIME(3) NOT NULL,
    `status` ENUM('draft', 'confirmed', 'locked', 'archived') NOT NULL DEFAULT 'draft',
    `totalInflow` BIGINT NOT NULL DEFAULT 0,
    `totalOutflow` BIGINT NOT NULL DEFAULT 0,
    `netFlow` BIGINT NOT NULL DEFAULT 0,
    `openingBalance` BIGINT NOT NULL DEFAULT 0,
    `closingBalance` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `preparedById` VARCHAR(191) NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_cash_forecasts_forecastNumber_key`(`forecastNumber`),
    INDEX `cm_cash_forecasts_companyId_idx`(`companyId`),
    INDEX `cm_cash_forecasts_forecastNumber_idx`(`forecastNumber`),
    INDEX `cm_cash_forecasts_periodStart_periodEnd_idx`(`periodStart`, `periodEnd`),
    INDEX `cm_cash_forecasts_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_cash_forecast_lines` (
    `id` VARCHAR(191) NOT NULL,
    `forecastId` VARCHAR(191) NOT NULL,
    `lineDate` DATETIME(3) NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `inflowAmount` BIGINT NOT NULL DEFAULT 0,
    `outflowAmount` BIGINT NOT NULL DEFAULT 0,
    `netAmount` BIGINT NOT NULL DEFAULT 0,
    `category` VARCHAR(50) NULL,
    `confidence` DECIMAL(5, 2) NULL,
    `source` VARCHAR(100) NULL,
    `bankAccountId` VARCHAR(191) NULL,
    `cashBoxId` VARCHAR(191) NULL,

    INDEX `cm_cash_forecast_lines_forecastId_idx`(`forecastId`),
    INDEX `cm_cash_forecast_lines_lineDate_idx`(`lineDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_liquidity_forecasts` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `forecastNumber` VARCHAR(50) NOT NULL,
    `forecastName` VARCHAR(255) NOT NULL,
    `forecastDate` DATETIME(3) NOT NULL,
    `periodDays` INTEGER NOT NULL DEFAULT 30,
    `totalInflow` BIGINT NOT NULL DEFAULT 0,
    `totalOutflow` BIGINT NOT NULL DEFAULT 0,
    `netLiquidity` BIGINT NOT NULL DEFAULT 0,
    `currentCash` BIGINT NOT NULL DEFAULT 0,
    `projectedCash` BIGINT NOT NULL DEFAULT 0,
    `minimumRequired` BIGINT NOT NULL DEFAULT 0,
    `surplusDeficit` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `status` ENUM('draft', 'confirmed', 'locked', 'archived') NOT NULL DEFAULT 'draft',
    `preparedById` VARCHAR(191) NULL,
    `approvedById` VARCHAR(191) NULL,
    `approvedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `cm_liquidity_forecasts_forecastNumber_key`(`forecastNumber`),
    INDEX `cm_liquidity_forecasts_companyId_idx`(`companyId`),
    INDEX `cm_liquidity_forecasts_forecastNumber_idx`(`forecastNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_liquidity_forecast_lines` (
    `id` VARCHAR(191) NOT NULL,
    `forecastId` VARCHAR(191) NOT NULL,
    `dayOffset` INTEGER NOT NULL DEFAULT 0,
    `forecastDate` DATETIME(3) NOT NULL,
    `inflowAmount` BIGINT NOT NULL DEFAULT 0,
    `outflowAmount` BIGINT NOT NULL DEFAULT 0,
    `netAmount` BIGINT NOT NULL DEFAULT 0,
    `cumulativeBalance` BIGINT NOT NULL DEFAULT 0,
    `category` VARCHAR(50) NULL,
    `confidence` DECIMAL(5, 2) NULL,

    INDEX `cm_liquidity_forecast_lines_forecastId_idx`(`forecastId`),
    INDEX `cm_liquidity_forecast_lines_forecastDate_idx`(`forecastDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_approval_requests` (
    `id` VARCHAR(191) NOT NULL,
    `entityType` VARCHAR(50) NOT NULL,
    `entityId` VARCHAR(36) NOT NULL,
    `requestNumber` VARCHAR(50) NOT NULL,
    `currentLevel` INTEGER NOT NULL DEFAULT 1,
    `maxLevel` INTEGER NOT NULL DEFAULT 1,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `requestedById` VARCHAR(191) NOT NULL,
    `requestedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `completedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `cm_approval_requests_requestNumber_key`(`requestNumber`),
    INDEX `cm_approval_requests_entityType_entityId_idx`(`entityType`, `entityId`),
    INDEX `cm_approval_requests_status_idx`(`status`),
    INDEX `cm_approval_requests_requestedById_idx`(`requestedById`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_approval_steps` (
    `id` VARCHAR(191) NOT NULL,
    `approvalId` VARCHAR(191) NOT NULL,
    `level` INTEGER NOT NULL DEFAULT 1,
    `approverId` VARCHAR(36) NOT NULL,
    `approverName` VARCHAR(255) NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `actionAt` DATETIME(3) NULL,
    `comment` TEXT NULL,
    `escalatedAt` DATETIME(3) NULL,
    `delegatedTo` VARCHAR(36) NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    INDEX `cm_approval_steps_approvalId_idx`(`approvalId`),
    INDEX `cm_approval_steps_approverId_idx`(`approverId`),
    INDEX `cm_approval_steps_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_attachments` (
    `id` VARCHAR(191) NOT NULL,
    `entityType` VARCHAR(50) NOT NULL,
    `entityId` VARCHAR(36) NOT NULL,
    `fileName` VARCHAR(255) NOT NULL,
    `filePath` VARCHAR(500) NOT NULL,
    `fileSize` INTEGER NOT NULL DEFAULT 0,
    `mimeType` VARCHAR(100) NULL,
    `attachmentType` ENUM('receipt', 'invoice', 'contract', 'supporting_document', 'image', 'pdf', 'other') NOT NULL DEFAULT 'other',
    `uploadedById` VARCHAR(191) NOT NULL,
    `uploadedAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `description` TEXT NULL,
    `ocrData` TEXT NULL,

    INDEX `cm_attachments_entityType_entityId_idx`(`entityType`, `entityId`),
    INDEX `cm_attachments_uploadedById_idx`(`uploadedById`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_currencies` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(3) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `nameEn` VARCHAR(100) NULL,
    `symbol` VARCHAR(10) NULL,
    `decimalPlaces` INTEGER NOT NULL DEFAULT 2,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `isFunctional` BOOLEAN NOT NULL DEFAULT false,
    `isForeign` BOOLEAN NOT NULL DEFAULT false,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `cm_currencies_code_key`(`code`),
    INDEX `cm_currencies_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `cm_holiday_calendars` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `date` DATETIME(3) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `isRecurring` BOOLEAN NOT NULL DEFAULT false,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `cm_holiday_calendars_companyId_idx`(`companyId`),
    INDEX `cm_holiday_calendars_date_idx`(`date`),
    UNIQUE INDEX `cm_holiday_calendars_companyId_date_key`(`companyId`, `date`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_groups` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `groupType` ENUM('domestic', 'foreign', 'joint_venture', 'government', 'central', 'investment', 'commercial', 'cooperative') NOT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_groups_code_key`(`code`),
    INDEX `bnk_groups_code_idx`(`code`),
    INDEX `bnk_groups_groupType_idx`(`groupType`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_correspondents` (
    `id` VARCHAR(191) NOT NULL,
    `bankId` VARCHAR(191) NOT NULL,
    `correspondentBankId` VARCHAR(191) NOT NULL,
    `accountNumber` VARCHAR(50) NULL,
    `correspondentType` ENUM('nostro', 'vostro', 'intermediary', 'beneficiary') NOT NULL,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `bnk_correspondents_bankId_idx`(`bankId`),
    INDEX `bnk_correspondents_currencyCode_idx`(`currencyCode`),
    UNIQUE INDEX `bnk_correspondents_bankId_correspondentBankId_currencyCode_key`(`bankId`, `correspondentBankId`, `currencyCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_banks` (
    `id` VARCHAR(191) NOT NULL,
    `groupId` VARCHAR(191) NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `shortName` VARCHAR(50) NULL,
    `swiftCode` VARCHAR(11) NULL,
    `routingNumber` VARCHAR(20) NULL,
    `bankCode` VARCHAR(20) NULL,
    `countryCode` VARCHAR(2) NOT NULL DEFAULT 'VN',
    `address` TEXT NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(255) NULL,
    `website` VARCHAR(255) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `isCorrespondent` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_banks_code_key`(`code`),
    INDEX `bnk_banks_code_idx`(`code`),
    INDEX `bnk_banks_swiftCode_idx`(`swiftCode`),
    INDEX `bnk_banks_countryCode_idx`(`countryCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_branches` (
    `id` VARCHAR(191) NOT NULL,
    `bankId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `nameEn` VARCHAR(255) NULL,
    `address` TEXT NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(255) NULL,
    `managerName` VARCHAR(255) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_branches_code_key`(`code`),
    INDEX `bnk_branches_bankId_idx`(`bankId`),
    INDEX `bnk_branches_code_idx`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_accounts` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `bankId` VARCHAR(191) NOT NULL,
    `branchId` VARCHAR(191) NULL,
    `accountNumber` VARCHAR(50) NOT NULL,
    `accountName` VARCHAR(255) NOT NULL,
    `accountNameEn` VARCHAR(255) NULL,
    `accountCategory` ENUM('current', 'savings', 'deposit', 'loan', 'treasury', 'investment', 'escrow', 'suspense', 'payroll', 'tax', 'intercompany', 'virtual', 'corporate', 'margin', 'collateral', 'trust') NOT NULL DEFAULT 'current',
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `countryCode` VARCHAR(2) NOT NULL DEFAULT 'VN',
    `iban` VARCHAR(34) NULL,
    `swiftCode` VARCHAR(11) NULL,
    `routingNumber` VARCHAR(20) NULL,
    `status` ENUM('pending', 'active', 'suspended', 'blocked', 'dormant', 'closed', 'archived') NOT NULL DEFAULT 'pending',
    `currentBalance` BIGINT NOT NULL DEFAULT 0,
    `availableBalance` BIGINT NOT NULL DEFAULT 0,
    `blockedBalance` BIGINT NOT NULL DEFAULT 0,
    `creditLimit` BIGINT NOT NULL DEFAULT 0,
    `minimumBalance` BIGINT NOT NULL DEFAULT 0,
    `maximumBalance` BIGINT NOT NULL DEFAULT 0,
    `overdraftLimit` BIGINT NOT NULL DEFAULT 0,
    `interestRate` DECIMAL(7, 4) NOT NULL DEFAULT 0,
    `glAccountId` VARCHAR(191) NULL,
    `glBankChargeAccountId` VARCHAR(191) NULL,
    `glInterestAccountId` VARCHAR(191) NULL,
    `glFXAccountId` VARCHAR(191) NULL,
    `isVirtual` BOOLEAN NOT NULL DEFAULT false,
    `parentAccountId` VARCHAR(191) NULL,
    `classification` VARCHAR(50) NULL,
    `openingDate` DATETIME(3) NOT NULL,
    `closingDate` DATETIME(3) NULL,
    `lastActivityDate` DATETIME(3) NULL,
    `lastReconciliationDate` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `bnk_accounts_companyId_idx`(`companyId`),
    INDEX `bnk_accounts_accountNumber_idx`(`accountNumber`),
    INDEX `bnk_accounts_status_idx`(`status`),
    INDEX `bnk_accounts_currencyCode_idx`(`currencyCode`),
    UNIQUE INDEX `bnk_accounts_bankId_accountNumber_key`(`bankId`, `accountNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_authorized_signers` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NULL,
    `signatureRule` ENUM('single', 'dual', 'triple', 'threshold', 'collective') NOT NULL DEFAULT 'single',
    `signingLimit` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `startDate` DATETIME(3) NOT NULL,
    `endDate` DATETIME(3) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_authorized_signers_bankAccountId_idx`(`bankAccountId`),
    INDEX `bnk_authorized_signers_userId_idx`(`userId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_account_limits` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `limitType` ENUM('single', 'daily', 'weekly', 'monthly', 'per_transaction') NOT NULL,
    `maxAmount` BIGINT NOT NULL DEFAULT 0,
    `minAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `isEnforced` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_account_limits_bankAccountId_idx`(`bankAccountId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_account_mappings` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `mappingType` VARCHAR(50) NOT NULL,
    `glAccountId` VARCHAR(191) NULL,
    `branchId` VARCHAR(191) NULL,
    `costCenterId` VARCHAR(191) NULL,
    `departmentId` VARCHAR(191) NULL,
    `projectId` VARCHAR(191) NULL,
    `isDefault` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_account_mappings_bankAccountId_idx`(`bankAccountId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_transactions` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `transactionNumber` VARCHAR(50) NOT NULL,
    `nature` ENUM('incoming', 'outgoing', 'internal', 'intercompany', 'external') NOT NULL,
    `method` ENUM('wire', 'ach', 'swift', 'sepa', 'domestic', 'internal_transfer', 'cheque', 'cash', 'card', 'direct_debit', 'direct_credit', 'standing_order', 'bulk_payment', 'e_wallet') NOT NULL,
    `status` ENUM('draft', 'pending', 'submitted', 'authorized', 'approved', 'executed', 'sent', 'completed', 'failed', 'reversed', 'cancelled', 'returned', 'charged_back') NOT NULL DEFAULT 'draft',
    `fromAccountId` VARCHAR(191) NOT NULL,
    `fromAccountNumber` VARCHAR(50) NULL,
    `toAccountId` VARCHAR(191) NULL,
    `toAccountNumber` VARCHAR(50) NULL,
    `toBankId` VARCHAR(36) NULL,
    `toBankName` VARCHAR(255) NULL,
    `toBankSwift` VARCHAR(11) NULL,
    `toBankRouting` VARCHAR(20) NULL,
    `beneficiaryName` VARCHAR(255) NULL,
    `beneficiaryAccount` VARCHAR(50) NULL,
    `beneficiaryAddress` TEXT NULL,
    `beneficiaryBank` VARCHAR(255) NULL,
    `intermediaryBankId` VARCHAR(36) NULL,
    `intermediaryBankSwift` VARCHAR(11) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `vndAmount` BIGINT NOT NULL DEFAULT 0,
    `chargeBearer` ENUM('sender', 'beneficiary', 'shared', 'all_charges') NOT NULL DEFAULT 'sender',
    `paymentPriority` ENUM('low', 'normal', 'high', 'urgent', 'emergency') NOT NULL DEFAULT 'normal',
    `settlementMethod` VARCHAR(50) NULL,
    `paymentChannel` VARCHAR(50) NULL,
    `reference` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `fees` BIGINT NOT NULL DEFAULT 0,
    `feeCurrencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `valueDate` DATETIME(3) NULL,
    `transactionDate` DATETIME(3) NOT NULL,
    `swiftMessage` TEXT NULL,
    `endToEndId` VARCHAR(50) NULL,
    `transactionId` VARCHAR(50) NULL,
    `clearingSystemRef` VARCHAR(50) NULL,
    `approvalLevel` INTEGER NOT NULL DEFAULT 0,
    `requiredApprovals` INTEGER NOT NULL DEFAULT 0,
    `approvedById` VARCHAR(36) NULL,
    `approvedAt` DATETIME(3) NULL,
    `executedById` VARCHAR(36) NULL,
    `executedAt` DATETIME(3) NULL,
    `completedAt` DATETIME(3) NULL,
    `failureReason` TEXT NULL,
    `reversalReason` TEXT NULL,
    `reversedAt` DATETIME(3) NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_transactions_transactionNumber_key`(`transactionNumber`),
    INDEX `bnk_transactions_companyId_idx`(`companyId`),
    INDEX `bnk_transactions_fromAccountId_idx`(`fromAccountId`),
    INDEX `bnk_transactions_toAccountId_idx`(`toAccountId`),
    INDEX `bnk_transactions_transactionNumber_idx`(`transactionNumber`),
    INDEX `bnk_transactions_status_idx`(`status`),
    INDEX `bnk_transactions_reference_idx`(`reference`),
    INDEX `bnk_transactions_transactionDate_idx`(`transactionDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_statements` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `statementNumber` VARCHAR(50) NOT NULL,
    `periodStart` DATETIME(3) NOT NULL,
    `periodEnd` DATETIME(3) NOT NULL,
    `openingBalance` BIGINT NOT NULL DEFAULT 0,
    `closingBalance` BIGINT NOT NULL DEFAULT 0,
    `totalDebit` BIGINT NOT NULL DEFAULT 0,
    `totalCredit` BIGINT NOT NULL DEFAULT 0,
    `transactionCount` INTEGER NOT NULL DEFAULT 0,
    `source` ENUM('manual', 'mt940', 'mt942', 'camt_052', 'camt_053', 'camt_054', 'csv', 'excel', 'api', 'pdf', 'print') NOT NULL DEFAULT 'manual',
    `importedAt` DATETIME(3) NULL,
    `importedBy` VARCHAR(36) NULL,
    `hash` VARCHAR(64) NULL,
    `isReconciled` BOOLEAN NOT NULL DEFAULT false,
    `isLocked` BOOLEAN NOT NULL DEFAULT false,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `bnk_statements_bankAccountId_idx`(`bankAccountId`),
    INDEX `bnk_statements_periodStart_periodEnd_idx`(`periodStart`, `periodEnd`),
    UNIQUE INDEX `bnk_statements_bankAccountId_statementNumber_key`(`bankAccountId`, `statementNumber`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_statement_lines` (
    `id` VARCHAR(191) NOT NULL,
    `statementId` VARCHAR(191) NOT NULL,
    `lineDate` DATETIME(3) NOT NULL,
    `valueDate` DATETIME(3) NULL,
    `description` TEXT NULL,
    `reference` VARCHAR(100) NULL,
    `chequeNumber` VARCHAR(50) NULL,
    `lineType` VARCHAR(20) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `exchangeRate` DECIMAL(19, 6) NOT NULL DEFAULT 1.0,
    `runningBalance` BIGINT NOT NULL DEFAULT 0,
    `isMatched` BOOLEAN NOT NULL DEFAULT false,
    `matchedToId` VARCHAR(36) NULL,
    `matchedToType` VARCHAR(50) NULL,
    `matchedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_statement_lines_statementId_idx`(`statementId`),
    INDEX `bnk_statement_lines_lineDate_idx`(`lineDate`),
    INDEX `bnk_statement_lines_isMatched_idx`(`isMatched`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_reconciliations` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `bankStatementId` VARCHAR(191) NOT NULL,
    `reconciliationNumber` VARCHAR(50) NOT NULL,
    `reconciliationDate` DATETIME(3) NOT NULL,
    `statementBalance` BIGINT NOT NULL DEFAULT 0,
    `bookBalance` BIGINT NOT NULL DEFAULT 0,
    `clearedAmount` BIGINT NOT NULL DEFAULT 0,
    `outstandingAmount` BIGINT NOT NULL DEFAULT 0,
    `difference` BIGINT NOT NULL DEFAULT 0,
    `status` ENUM('open', 'in_progress', 'matched', 'difference_found', 'resolved', 'approved', 'closed', 'reversed') NOT NULL DEFAULT 'open',
    `matchedCount` INTEGER NOT NULL DEFAULT 0,
    `unmatchedCount` INTEGER NOT NULL DEFAULT 0,
    `autoMatchedCount` INTEGER NOT NULL DEFAULT 0,
    `manualMatchedCount` INTEGER NOT NULL DEFAULT 0,
    `preparedById` VARCHAR(36) NULL,
    `reviewedById` VARCHAR(36) NULL,
    `approvedById` VARCHAR(36) NULL,
    `approvedAt` DATETIME(3) NULL,
    `reversedById` VARCHAR(36) NULL,
    `reversedAt` DATETIME(3) NULL,
    `reversalReason` TEXT NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_reconciliations_reconciliationNumber_key`(`reconciliationNumber`),
    INDEX `bnk_reconciliations_bankAccountId_idx`(`bankAccountId`),
    INDEX `bnk_reconciliations_bankStatementId_idx`(`bankStatementId`),
    INDEX `bnk_reconciliations_reconciliationNumber_idx`(`reconciliationNumber`),
    INDEX `bnk_reconciliations_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_reconciliation_items` (
    `id` VARCHAR(191) NOT NULL,
    `reconciliationId` VARCHAR(191) NOT NULL,
    `statementLineId` VARCHAR(191) NULL,
    `sourceType` VARCHAR(50) NOT NULL,
    `sourceId` VARCHAR(36) NOT NULL,
    `sourceReference` VARCHAR(100) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `matchType` ENUM('auto', 'manual', 'rule', 'tolerance', 'partial', 'split', 'merge') NOT NULL,
    `matchDate` DATETIME(3) NOT NULL,
    `isClearItem` BOOLEAN NOT NULL DEFAULT true,
    `notes` TEXT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_reconciliation_items_reconciliationId_idx`(`reconciliationId`),
    INDEX `bnk_reconciliation_items_statementLineId_idx`(`statementLineId`),
    INDEX `bnk_reconciliation_items_sourceType_sourceId_idx`(`sourceType`, `sourceId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_payment_requests` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `requestNumber` VARCHAR(50) NOT NULL,
    `paymentDate` DATETIME(3) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `fromAccountId` VARCHAR(191) NOT NULL,
    `toAccountId` VARCHAR(36) NULL,
    `beneficiaryName` VARCHAR(255) NOT NULL,
    `beneficiaryAccount` VARCHAR(50) NULL,
    `beneficiaryBank` VARCHAR(255) NULL,
    `beneficiaryBankSwift` VARCHAR(11) NULL,
    `method` ENUM('wire', 'ach', 'swift', 'sepa', 'domestic', 'internal_transfer', 'cheque', 'cash', 'card', 'direct_debit', 'direct_credit', 'standing_order', 'bulk_payment', 'e_wallet') NOT NULL DEFAULT 'wire',
    `priority` ENUM('low', 'normal', 'high', 'urgent', 'emergency') NOT NULL DEFAULT 'normal',
    `chargeBearer` ENUM('sender', 'beneficiary', 'shared', 'all_charges') NOT NULL DEFAULT 'sender',
    `reference` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `approvalStatus` ENUM('pending', 'approved', 'rejected', 'returned', 'escalated', 'delegated') NOT NULL DEFAULT 'pending',
    `approvalLevel` INTEGER NOT NULL DEFAULT 0,
    `requiredApprovals` INTEGER NOT NULL DEFAULT 1,
    `requestedById` VARCHAR(191) NOT NULL,
    `requestedAt` DATETIME(3) NOT NULL,
    `approvedById` VARCHAR(36) NULL,
    `approvedAt` DATETIME(3) NULL,
    `rejectedById` VARCHAR(36) NULL,
    `rejectedAt` DATETIME(3) NULL,
    `rejectionReason` TEXT NULL,
    `batchId` VARCHAR(191) NULL,
    `transactionId` VARCHAR(36) NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_payment_requests_requestNumber_key`(`requestNumber`),
    INDEX `bnk_payment_requests_companyId_idx`(`companyId`),
    INDEX `bnk_payment_requests_fromAccountId_idx`(`fromAccountId`),
    INDEX `bnk_payment_requests_requestNumber_idx`(`requestNumber`),
    INDEX `bnk_payment_requests_approvalStatus_idx`(`approvalStatus`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_payment_batches` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `batchNumber` VARCHAR(50) NOT NULL,
    `status` ENUM('draft', 'validated', 'authorized', 'approved', 'released', 'processing', 'completed', 'partially_completed', 'failed', 'cancelled') NOT NULL DEFAULT 'draft',
    `paymentCount` INTEGER NOT NULL DEFAULT 0,
    `totalAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `paymentDate` DATETIME(3) NOT NULL,
    `valueDate` DATETIME(3) NULL,
    `approvedById` VARCHAR(36) NULL,
    `approvedAt` DATETIME(3) NULL,
    `releasedById` VARCHAR(36) NULL,
    `releasedAt` DATETIME(3) NULL,
    `completedAt` DATETIME(3) NULL,
    `failureCount` INTEGER NOT NULL DEFAULT 0,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_payment_batches_batchNumber_key`(`batchNumber`),
    INDEX `bnk_payment_batches_companyId_idx`(`companyId`),
    INDEX `bnk_payment_batches_batchNumber_idx`(`batchNumber`),
    INDEX `bnk_payment_batches_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_recurring_payments` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `fromAccountId` VARCHAR(191) NOT NULL,
    `toAccountId` VARCHAR(36) NULL,
    `beneficiaryName` VARCHAR(255) NOT NULL,
    `beneficiaryAccount` VARCHAR(50) NULL,
    `beneficiaryBank` VARCHAR(255) NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `frequency` ENUM('daily', 'weekly', 'bi_weekly', 'monthly', 'bi_monthly', 'quarterly', 'semi_annual', 'annual') NOT NULL,
    `interval` INTEGER NOT NULL DEFAULT 1,
    `startDate` DATETIME(3) NOT NULL,
    `endDate` DATETIME(3) NULL,
    `nextExecutionDate` DATETIME(3) NOT NULL,
    `lastExecutionDate` DATETIME(3) NULL,
    `executionCount` INTEGER NOT NULL DEFAULT 0,
    `maxExecutions` INTEGER NULL,
    `method` ENUM('wire', 'ach', 'swift', 'sepa', 'domestic', 'internal_transfer', 'cheque', 'cash', 'card', 'direct_debit', 'direct_credit', 'standing_order', 'bulk_payment', 'e_wallet') NOT NULL DEFAULT 'wire',
    `reference` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `bnk_recurring_payments_companyId_idx`(`companyId`),
    INDEX `bnk_recurring_payments_fromAccountId_idx`(`fromAccountId`),
    INDEX `bnk_recurring_payments_nextExecutionDate_idx`(`nextExecutionDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_cash_positions` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `positionDate` DATETIME(3) NOT NULL,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `openingBalance` BIGINT NOT NULL DEFAULT 0,
    `totalInflows` BIGINT NOT NULL DEFAULT 0,
    `totalOutflows` BIGINT NOT NULL DEFAULT 0,
    `netFlow` BIGINT NOT NULL DEFAULT 0,
    `closingBalance` BIGINT NOT NULL DEFAULT 0,
    `availableBalance` BIGINT NOT NULL DEFAULT 0,
    `blockedBalance` BIGINT NOT NULL DEFAULT 0,
    `pendingInflows` BIGINT NOT NULL DEFAULT 0,
    `pendingOutflows` BIGINT NOT NULL DEFAULT 0,
    `projectedBalance` BIGINT NOT NULL DEFAULT 0,
    `minimumBalance` BIGINT NOT NULL DEFAULT 0,
    `maximumBalance` BIGINT NOT NULL DEFAULT 0,
    `status` ENUM('draft', 'confirmed', 'approved', 'locked') NOT NULL DEFAULT 'draft',
    `isReconciled` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    INDEX `bnk_cash_positions_companyId_idx`(`companyId`),
    INDEX `bnk_cash_positions_positionDate_idx`(`positionDate`),
    UNIQUE INDEX `bnk_cash_positions_companyId_positionDate_currencyCode_key`(`companyId`, `positionDate`, `currencyCode`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_cash_forecasts` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `forecastNumber` VARCHAR(50) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `periodStart` DATETIME(3) NOT NULL,
    `periodEnd` DATETIME(3) NOT NULL,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `openingBalance` BIGINT NOT NULL DEFAULT 0,
    `projectedInflows` BIGINT NOT NULL DEFAULT 0,
    `projectedOutflows` BIGINT NOT NULL DEFAULT 0,
    `netProjected` BIGINT NOT NULL DEFAULT 0,
    `closingBalance` BIGINT NOT NULL DEFAULT 0,
    `minimumRequired` BIGINT NOT NULL DEFAULT 0,
    `surplusDeficit` BIGINT NOT NULL DEFAULT 0,
    `confidenceLevel` DECIMAL(5, 2) NOT NULL DEFAULT 0,
    `status` ENUM('draft', 'confirmed', 'approved', 'locked') NOT NULL DEFAULT 'draft',
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,
    `deletedAt` DATETIME(3) NULL,

    UNIQUE INDEX `bnk_cash_forecasts_forecastNumber_key`(`forecastNumber`),
    INDEX `bnk_cash_forecasts_companyId_idx`(`companyId`),
    INDEX `bnk_cash_forecasts_periodStart_periodEnd_idx`(`periodStart`, `periodEnd`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_fx_rates` (
    `id` VARCHAR(191) NOT NULL,
    `fromCurrency` VARCHAR(3) NOT NULL,
    `toCurrency` VARCHAR(3) NOT NULL,
    `rate` DECIMAL(19, 6) NOT NULL,
    `rateType` ENUM('spot', 'forward', 'swap', 'historical', 'budget', 'reference', 'buy', 'sell', 'transfer') NOT NULL DEFAULT 'reference',
    `validFrom` DATETIME(3) NOT NULL,
    `validTo` DATETIME(3) NOT NULL,
    `source` VARCHAR(100) NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_fx_rates_fromCurrency_toCurrency_idx`(`fromCurrency`, `toCurrency`),
    INDEX `bnk_fx_rates_validFrom_validTo_idx`(`validFrom`, `validTo`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_fx_revaluations` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `revaluationDate` DATETIME(3) NOT NULL,
    `currencyCode` VARCHAR(3) NOT NULL,
    `exchangeRate` DECIMAL(19, 6) NOT NULL,
    `previousRate` DECIMAL(19, 6) NOT NULL,
    `accountId` VARCHAR(36) NOT NULL,
    `accountBalance` BIGINT NOT NULL DEFAULT 0,
    `fxGainLoss` BIGINT NOT NULL DEFAULT 0,
    `gainLossType` VARCHAR(4) NOT NULL,
    `isRealized` BOOLEAN NOT NULL DEFAULT false,
    `sourceTransactionId` VARCHAR(36) NULL,
    `glBatchId` VARCHAR(191) NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_fx_revaluations_companyId_idx`(`companyId`),
    INDEX `bnk_fx_revaluations_accountId_idx`(`accountId`),
    INDEX `bnk_fx_revaluations_revaluationDate_idx`(`revaluationDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_approval_matrices` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `entityType` VARCHAR(50) NOT NULL,
    `minAmount` BIGINT NOT NULL DEFAULT 0,
    `maxAmount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `approvalMode` ENUM('sequential', 'parallel', 'any') NOT NULL DEFAULT 'sequential',
    `levels` INTEGER NOT NULL DEFAULT 1,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_approval_matrices_companyId_idx`(`companyId`),
    INDEX `bnk_approval_matrices_entityType_idx`(`entityType`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_approval_matrix_levels` (
    `id` VARCHAR(191) NOT NULL,
    `matrixId` VARCHAR(191) NOT NULL,
    `level` INTEGER NOT NULL,
    `approverId` VARCHAR(36) NOT NULL,
    `approverName` VARCHAR(255) NULL,
    `minAmount` BIGINT NOT NULL DEFAULT 0,
    `maxAmount` BIGINT NOT NULL DEFAULT 0,
    `isRequired` BOOLEAN NOT NULL DEFAULT true,

    INDEX `bnk_approval_matrix_levels_matrixId_idx`(`matrixId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_approval_requests` (
    `id` VARCHAR(191) NOT NULL,
    `requestNumber` VARCHAR(50) NOT NULL,
    `entityType` VARCHAR(50) NOT NULL,
    `entityId` VARCHAR(36) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `status` ENUM('pending', 'approved', 'rejected', 'returned', 'escalated', 'delegated') NOT NULL DEFAULT 'pending',
    `currentLevel` INTEGER NOT NULL DEFAULT 1,
    `maxLevel` INTEGER NOT NULL DEFAULT 1,
    `approvalMode` ENUM('sequential', 'parallel', 'any') NOT NULL DEFAULT 'sequential',
    `requestedById` VARCHAR(36) NOT NULL,
    `requestedAt` DATETIME(3) NOT NULL,
    `completedAt` DATETIME(3) NULL,
    `notes` TEXT NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `bnk_approval_requests_requestNumber_key`(`requestNumber`),
    INDEX `bnk_approval_requests_entityType_entityId_idx`(`entityType`, `entityId`),
    INDEX `bnk_approval_requests_status_idx`(`status`),
    INDEX `bnk_approval_requests_requestedById_idx`(`requestedById`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_approval_steps` (
    `id` VARCHAR(191) NOT NULL,
    `approvalId` VARCHAR(191) NOT NULL,
    `level` INTEGER NOT NULL,
    `approverId` VARCHAR(36) NOT NULL,
    `approverName` VARCHAR(255) NULL,
    `status` ENUM('pending', 'approved', 'rejected', 'returned', 'escalated', 'delegated') NOT NULL DEFAULT 'pending',
    `actionAt` DATETIME(3) NULL,
    `comment` TEXT NULL,
    `escalatedAt` DATETIME(3) NULL,
    `delegatedTo` VARCHAR(36) NULL,

    INDEX `bnk_approval_steps_approvalId_idx`(`approvalId`),
    INDEX `bnk_approval_steps_approverId_idx`(`approverId`),
    INDEX `bnk_approval_steps_status_idx`(`status`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_charges` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `chargeType` ENUM('transaction', 'monthly', 'annual', 'maintenance', 'overdraft', 'wire', 'currency_conversion', 'late', 'early_repayment', 'service', 'penalty', 'commission') NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `chargeDate` DATETIME(3) NOT NULL,
    `description` TEXT NULL,
    `reference` VARCHAR(100) NULL,
    `transactionId` VARCHAR(36) NULL,
    `glBatchId` VARCHAR(191) NULL,
    `postedToGL` BOOLEAN NOT NULL DEFAULT false,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_charges_bankAccountId_idx`(`bankAccountId`),
    INDEX `bnk_charges_chargeDate_idx`(`chargeDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_interest_calculations` (
    `id` VARCHAR(191) NOT NULL,
    `bankAccountId` VARCHAR(191) NOT NULL,
    `calculationDate` DATETIME(3) NOT NULL,
    `amount` BIGINT NOT NULL DEFAULT 0,
    `currencyCode` VARCHAR(3) NOT NULL DEFAULT 'VND',
    `interestRate` DECIMAL(7, 4) NOT NULL,
    `calculationMethod` ENUM('simple', 'compound', 'daily', 'monthly', 'quarterly', 'annual') NOT NULL DEFAULT 'simple',
    `interestBasis` ENUM('actual_360', 'actual_365', 'actual_actual', 'thirty_360', 'thirty_e_360') NOT NULL DEFAULT 'actual_365',
    `daysInPeriod` INTEGER NOT NULL DEFAULT 0,
    `interestAmount` BIGINT NOT NULL DEFAULT 0,
    `isCalculated` BOOLEAN NOT NULL DEFAULT false,
    `isPosted` BOOLEAN NOT NULL DEFAULT false,
    `glBatchId` VARCHAR(191) NULL,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    INDEX `bnk_interest_calculations_bankAccountId_idx`(`bankAccountId`),
    INDEX `bnk_interest_calculations_calculationDate_idx`(`calculationDate`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_business_calendars` (
    `id` VARCHAR(191) NOT NULL,
    `companyId` VARCHAR(191) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `year` INTEGER NOT NULL,
    `isActive` BOOLEAN NOT NULL DEFAULT true,
    `version` INTEGER NOT NULL DEFAULT 1,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `bnk_business_calendars_code_key`(`code`),
    INDEX `bnk_business_calendars_companyId_idx`(`companyId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bnk_calendar_holidays` (
    `id` VARCHAR(191) NOT NULL,
    `calendarId` VARCHAR(191) NOT NULL,
    `date` DATETIME(3) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `isRecurring` BOOLEAN NOT NULL DEFAULT false,
    `isActive` BOOLEAN NOT NULL DEFAULT true,

    INDEX `bnk_calendar_holidays_date_idx`(`date`),
    UNIQUE INDEX `bnk_calendar_holidays_calendarId_date_key`(`calendarId`, `date`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Account` ADD CONSTRAINT `Account_parentId_fkey` FOREIGN KEY (`parentId`) REFERENCES `Account`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Period` ADD CONSTRAINT `Period_fiscalYearId_fkey` FOREIGN KEY (`fiscalYearId`) REFERENCES `FiscalYear`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `VoucherSeries` ADD CONSTRAINT `VoucherSeries_voucherTypeId_fkey` FOREIGN KEY (`voucherTypeId`) REFERENCES `VoucherType`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `VoucherSeries` ADD CONSTRAINT `VoucherSeries_fiscalYearId_fkey` FOREIGN KEY (`fiscalYearId`) REFERENCES `FiscalYear`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalBatch` ADD CONSTRAINT `JournalBatch_periodId_fkey` FOREIGN KEY (`periodId`) REFERENCES `Period`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalBatch` ADD CONSTRAINT `JournalBatch_fiscalYearId_fkey` FOREIGN KEY (`fiscalYearId`) REFERENCES `FiscalYear`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalBatch` ADD CONSTRAINT `JournalBatch_voucherTypeId_fkey` FOREIGN KEY (`voucherTypeId`) REFERENCES `VoucherType`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalBatch` ADD CONSTRAINT `JournalBatch_voucherSeriesId_fkey` FOREIGN KEY (`voucherSeriesId`) REFERENCES `VoucherSeries`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalEntryLine` ADD CONSTRAINT `JournalEntryLine_batchId_fkey` FOREIGN KEY (`batchId`) REFERENCES `JournalBatch`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `JournalEntryLine` ADD CONSTRAINT `JournalEntryLine_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Budget` ADD CONSTRAINT `Budget_fiscalYearId_fkey` FOREIGN KEY (`fiscalYearId`) REFERENCES `FiscalYear`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `BudgetLine` ADD CONSTRAINT `BudgetLine_budgetId_fkey` FOREIGN KEY (`budgetId`) REFERENCES `Budget`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `BudgetLine` ADD CONSTRAINT `BudgetLine_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_codes` ADD CONSTRAINT `tax_codes_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_rates` ADD CONSTRAINT `tax_rates_taxCodeId_fkey` FOREIGN KEY (`taxCodeId`) REFERENCES `tax_codes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_authorities` ADD CONSTRAINT `tax_authorities_parentId_fkey` FOREIGN KEY (`parentId`) REFERENCES `tax_authorities`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_registrations` ADD CONSTRAINT `tax_registrations_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_exemptions` ADD CONSTRAINT `tax_exemptions_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_exemptions` ADD CONSTRAINT `tax_exemptions_taxCodeId_fkey` FOREIGN KEY (`taxCodeId`) REFERENCES `tax_codes`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_returns` ADD CONSTRAINT `tax_returns_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_payments` ADD CONSTRAINT `tax_payments_taxReturnId_fkey` FOREIGN KEY (`taxReturnId`) REFERENCES `tax_returns`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_payments` ADD CONSTRAINT `tax_payments_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `tax_determination_rules` ADD CONSTRAINT `tax_determination_rules_taxTypeId_fkey` FOREIGN KEY (`taxTypeId`) REFERENCES `tax_types`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_account_types` ADD CONSTRAINT `coa_account_types_classId_fkey` FOREIGN KEY (`classId`) REFERENCES `coa_account_classes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_account_types` ADD CONSTRAINT `coa_account_types_parentTypeId_fkey` FOREIGN KEY (`parentTypeId`) REFERENCES `coa_account_types`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_account_extensions` ADD CONSTRAINT `coa_account_extensions_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_account_extensions` ADD CONSTRAINT `coa_account_extensions_typeId_fkey` FOREIGN KEY (`typeId`) REFERENCES `coa_account_types`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_account_mappings` ADD CONSTRAINT `coa_account_mappings_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_hierarchy_changes` ADD CONSTRAINT `coa_hierarchy_changes_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_code_changes` ADD CONSTRAINT `coa_code_changes_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `coa_status_changes` ADD CONSTRAINT `coa_status_changes_accountId_fkey` FOREIGN KEY (`accountId`) REFERENCES `Account`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_locations` ADD CONSTRAINT `cm_cash_locations_companyId_fkey` FOREIGN KEY (`companyId`) REFERENCES `cm_companies`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_boxes` ADD CONSTRAINT `cm_cash_boxes_locationId_fkey` FOREIGN KEY (`locationId`) REFERENCES `cm_cash_locations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_registers` ADD CONSTRAINT `cm_cash_registers_cashBoxId_fkey` FOREIGN KEY (`cashBoxId`) REFERENCES `cm_cash_boxes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_sessions` ADD CONSTRAINT `cm_cash_sessions_cashBoxId_fkey` FOREIGN KEY (`cashBoxId`) REFERENCES `cm_cash_boxes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_sessions` ADD CONSTRAINT `cm_cash_sessions_cashRegisterId_fkey` FOREIGN KEY (`cashRegisterId`) REFERENCES `cm_cash_registers`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_sessions` ADD CONSTRAINT `cm_cash_sessions_cashierId_fkey` FOREIGN KEY (`cashierId`) REFERENCES `cm_cashiers`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_counts` ADD CONSTRAINT `cm_cash_counts_sessionId_fkey` FOREIGN KEY (`sessionId`) REFERENCES `cm_cash_sessions`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_counts` ADD CONSTRAINT `cm_cash_counts_cashBoxId_fkey` FOREIGN KEY (`cashBoxId`) REFERENCES `cm_cash_boxes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_differences` ADD CONSTRAINT `cm_cash_differences_sessionId_fkey` FOREIGN KEY (`sessionId`) REFERENCES `cm_cash_sessions`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_petty_cash_funds` ADD CONSTRAINT `cm_petty_cash_funds_locationId_fkey` FOREIGN KEY (`locationId`) REFERENCES `cm_cash_locations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_petty_cash_replenishments` ADD CONSTRAINT `cm_petty_cash_replenishments_fundId_fkey` FOREIGN KEY (`fundId`) REFERENCES `cm_petty_cash_funds`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_advance_settlements` ADD CONSTRAINT `cm_advance_settlements_advanceId_fkey` FOREIGN KEY (`advanceId`) REFERENCES `cm_cash_advances`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_transfers` ADD CONSTRAINT `cm_cash_transfers_fromLocationId_fkey` FOREIGN KEY (`fromLocationId`) REFERENCES `cm_cash_locations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_transfers` ADD CONSTRAINT `cm_cash_transfers_toLocationId_fkey` FOREIGN KEY (`toLocationId`) REFERENCES `cm_cash_locations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_receipts` ADD CONSTRAINT `cm_cash_receipts_cashBoxId_fkey` FOREIGN KEY (`cashBoxId`) REFERENCES `cm_cash_boxes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_receipts` ADD CONSTRAINT `cm_cash_receipts_sessionId_fkey` FOREIGN KEY (`sessionId`) REFERENCES `cm_cash_sessions`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_receipts` ADD CONSTRAINT `cm_cash_receipts_cashierId_fkey` FOREIGN KEY (`cashierId`) REFERENCES `cm_cashiers`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_receipt_attachments` ADD CONSTRAINT `cm_receipt_attachments_receiptId_fkey` FOREIGN KEY (`receiptId`) REFERENCES `cm_cash_receipts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_payments` ADD CONSTRAINT `cm_cash_payments_cashBoxId_fkey` FOREIGN KEY (`cashBoxId`) REFERENCES `cm_cash_boxes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_payments` ADD CONSTRAINT `cm_cash_payments_sessionId_fkey` FOREIGN KEY (`sessionId`) REFERENCES `cm_cash_sessions`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_payments` ADD CONSTRAINT `cm_cash_payments_cashierId_fkey` FOREIGN KEY (`cashierId`) REFERENCES `cm_cashiers`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_payment_attachments` ADD CONSTRAINT `cm_payment_attachments_paymentId_fkey` FOREIGN KEY (`paymentId`) REFERENCES `cm_cash_payments`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_banks` ADD CONSTRAINT `cm_banks_companyId_fkey` FOREIGN KEY (`companyId`) REFERENCES `cm_companies`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_branches` ADD CONSTRAINT `cm_bank_branches_bankId_fkey` FOREIGN KEY (`bankId`) REFERENCES `cm_banks`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_accounts` ADD CONSTRAINT `cm_bank_accounts_companyId_fkey` FOREIGN KEY (`companyId`) REFERENCES `cm_companies`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_accounts` ADD CONSTRAINT `cm_bank_accounts_bankId_fkey` FOREIGN KEY (`bankId`) REFERENCES `cm_banks`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_accounts` ADD CONSTRAINT `cm_bank_accounts_branchId_fkey` FOREIGN KEY (`branchId`) REFERENCES `cm_bank_branches`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cheque_books` ADD CONSTRAINT `cm_cheque_books_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `cm_bank_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cheques` ADD CONSTRAINT `cm_cheques_chequeBookId_fkey` FOREIGN KEY (`chequeBookId`) REFERENCES `cm_cheque_books`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_transfers` ADD CONSTRAINT `cm_bank_transfers_fromAccountId_fkey` FOREIGN KEY (`fromAccountId`) REFERENCES `cm_bank_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_transfers` ADD CONSTRAINT `cm_bank_transfers_toAccountId_fkey` FOREIGN KEY (`toAccountId`) REFERENCES `cm_bank_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_statements` ADD CONSTRAINT `cm_bank_statements_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `cm_bank_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_statement_lines` ADD CONSTRAINT `cm_bank_statement_lines_statementId_fkey` FOREIGN KEY (`statementId`) REFERENCES `cm_bank_statements`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_reconciliations` ADD CONSTRAINT `cm_bank_reconciliations_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `cm_bank_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_reconciliations` ADD CONSTRAINT `cm_bank_reconciliations_bankStatementId_fkey` FOREIGN KEY (`bankStatementId`) REFERENCES `cm_bank_statements`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_bank_reconciliation_items` ADD CONSTRAINT `cm_bank_reconciliation_items_reconciliationId_fkey` FOREIGN KEY (`reconciliationId`) REFERENCES `cm_bank_reconciliations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_forecasts` ADD CONSTRAINT `cm_cash_forecasts_companyId_fkey` FOREIGN KEY (`companyId`) REFERENCES `cm_companies`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_cash_forecast_lines` ADD CONSTRAINT `cm_cash_forecast_lines_forecastId_fkey` FOREIGN KEY (`forecastId`) REFERENCES `cm_cash_forecasts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_liquidity_forecast_lines` ADD CONSTRAINT `cm_liquidity_forecast_lines_forecastId_fkey` FOREIGN KEY (`forecastId`) REFERENCES `cm_liquidity_forecasts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cm_approval_steps` ADD CONSTRAINT `cm_approval_steps_approvalId_fkey` FOREIGN KEY (`approvalId`) REFERENCES `cm_approval_requests`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_branches` ADD CONSTRAINT `bnk_branches_bankId_fkey` FOREIGN KEY (`bankId`) REFERENCES `bnk_banks`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_accounts` ADD CONSTRAINT `bnk_accounts_branchId_fkey` FOREIGN KEY (`branchId`) REFERENCES `bnk_branches`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_authorized_signers` ADD CONSTRAINT `bnk_authorized_signers_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_account_limits` ADD CONSTRAINT `bnk_account_limits_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_account_mappings` ADD CONSTRAINT `bnk_account_mappings_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_transactions` ADD CONSTRAINT `bnk_transactions_fromAccountId_fkey` FOREIGN KEY (`fromAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_transactions` ADD CONSTRAINT `bnk_transactions_toAccountId_fkey` FOREIGN KEY (`toAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_statements` ADD CONSTRAINT `bnk_statements_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_statement_lines` ADD CONSTRAINT `bnk_statement_lines_statementId_fkey` FOREIGN KEY (`statementId`) REFERENCES `bnk_statements`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_reconciliations` ADD CONSTRAINT `bnk_reconciliations_bankAccountId_fkey` FOREIGN KEY (`bankAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_reconciliations` ADD CONSTRAINT `bnk_reconciliations_bankStatementId_fkey` FOREIGN KEY (`bankStatementId`) REFERENCES `bnk_statements`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_reconciliation_items` ADD CONSTRAINT `bnk_reconciliation_items_reconciliationId_fkey` FOREIGN KEY (`reconciliationId`) REFERENCES `bnk_reconciliations`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_payment_requests` ADD CONSTRAINT `bnk_payment_requests_fromAccountId_fkey` FOREIGN KEY (`fromAccountId`) REFERENCES `bnk_accounts`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_approval_matrix_levels` ADD CONSTRAINT `bnk_approval_matrix_levels_matrixId_fkey` FOREIGN KEY (`matrixId`) REFERENCES `bnk_approval_matrices`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_approval_steps` ADD CONSTRAINT `bnk_approval_steps_approvalId_fkey` FOREIGN KEY (`approvalId`) REFERENCES `bnk_approval_requests`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `bnk_calendar_holidays` ADD CONSTRAINT `bnk_calendar_holidays_calendarId_fkey` FOREIGN KEY (`calendarId`) REFERENCES `bnk_business_calendars`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;
