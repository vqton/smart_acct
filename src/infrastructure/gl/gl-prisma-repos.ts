import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import type {
  AccountRepository, AccountSearchCriteria,
  JournalBatchRepository,
  FiscalYearRepository,
  PeriodRepository,
  VoucherTypeRepository,
  VoucherSeriesRepository,
  ExchangeRateRepository,
  CostCenterRepository,
  DepartmentRepository,
  BudgetRepository,
  UnitOfWork,
} from "../../domain/gl/repositories.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { Account, type AccountState } from "../../domain/gl/account.js";
import { AccountCategory, AccountNature } from "../../domain/gl/account-category.js";
import { JournalBatch, JournalBatchId, type JournalBatchState, JournalEntryStatus, type JournalEntryLine, JournalType } from "../../domain/gl/journal.js";
import { FiscalYear, FiscalYearId, type FiscalYearState } from "../../domain/gl/period.js";
import { Period, PeriodId, type PeriodState } from "../../domain/gl/period.js";
import { VoucherType, VoucherTypeId, type VoucherTypeState } from "../../domain/gl/voucher.js";
import { VoucherSeries, VoucherSeriesId, type VoucherSeriesState } from "../../domain/gl/voucher.js";
import { ExchangeRate, ExchangeRateId, type ExchangeRateState } from "../../domain/gl/exchange-rate.js";
import { CostCenter, CostCenterId, type CostCenterState } from "../../domain/gl/dimension.js";
import { Department, DepartmentId, type DepartmentState } from "../../domain/gl/dimension.js";
import { Budget, BudgetId, type BudgetState } from "../../domain/gl/budget.js";

@Injectable()
export class PrismaUnitOfWork implements UnitOfWork {
  private _active = false;

  constructor(private readonly prisma: PrismaService) {}

  async begin(): Promise<void> {
    await this.prisma.$transaction(async () => {
      this._active = true;
    });
    this._active = false;
  }

  async commit(): Promise<void> {
    this._active = false;
  }

  async rollback(): Promise<void> {
    this._active = false;
  }

  isActive(): boolean {
    return this._active;
  }
}

function fromPrismaAccount(row: Record<string, unknown>): Account {
  return Account.load({
    id: row.id as string,
    code: row.code as string,
    name: row.name as string,
    nameEn: (row.nameEn as string) ?? null,
    category: row.category as AccountCategory,
    nature: row.nature as AccountNature,
    parentId: (row.parentId as string) ?? null,
    isActive: row.isActive as boolean,
    isControl: row.isControl as boolean,
    isPosting: row.isPosting as boolean,
    allowManualEntry: row.allowManualEntry as boolean,
    balance: Number(row.balance as bigint),
    foreignBalance: Number(row.foreignBalance as bigint),
    currencyCode: (row.currencyCode as string) ?? null,
    description: (row.description as string) ?? null,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
    version: row.version as number,
    deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaAccount(account: Account): Record<string, unknown> {
  const s = account.toState();
  return {
    id: s.id,
    code: s.code,
    name: s.name,
    nameEn: s.nameEn,
    category: s.category,
    nature: s.nature,
    parentId: s.parentId,
    isActive: s.isActive,
    isControl: s.isControl,
    isPosting: s.isPosting,
    allowManualEntry: s.allowManualEntry,
    balance: BigInt(Math.round(s.balance)),
    foreignBalance: BigInt(Math.round(s.foreignBalance)),
    currencyCode: s.currencyCode,
    description: s.description,
    version: s.version,
    deletedAt: s.deletedAt,
    createdAt: s.createdAt,
    updatedAt: s.updatedAt,
  };
}

@Injectable()
export class PrismaAccountRepository implements AccountRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(account: Account): Promise<void> {
    const data = toPrismaAccount(account);
    await this.prisma.account.upsert({
      where: { id: data.id as string },
      create: data as any,
      update: data as any,
    });
  }

  async findById(id: AccountId): Promise<Account | null> {
    const row = await this.prisma.account.findUnique({ where: { id: id.value } });
    return row ? fromPrismaAccount(row as any) : null;
  }

  async findByCode(code: string): Promise<Account | null> {
    const row = await this.prisma.account.findUnique({ where: { code } });
    return row ? fromPrismaAccount(row as any) : null;
  }

  async findAll(): Promise<Account[]> {
    const rows = await this.prisma.account.findMany({ orderBy: { code: "asc" } });
    return rows.map(r => fromPrismaAccount(r as any));
  }

  async findActive(): Promise<Account[]> {
    const rows = await this.prisma.account.findMany({
      where: { isActive: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    return rows.map(r => fromPrismaAccount(r as any));
  }

  async findPostingAccounts(): Promise<Account[]> {
    const rows = await this.prisma.account.findMany({
      where: { isActive: true, isPosting: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    return rows.map(r => fromPrismaAccount(r as any));
  }

  async findChildren(parentId: string): Promise<Account[]> {
    const rows = await this.prisma.account.findMany({
      where: { parentId },
      orderBy: { code: "asc" },
    });
    return rows.map(r => fromPrismaAccount(r as any));
  }

  async search(criteria: AccountSearchCriteria): Promise<Account[]> {
    const where: Record<string, unknown> = {};
    if (criteria.keyword) {
      where.OR = [
        { code: { contains: criteria.keyword } },
        { name: { contains: criteria.keyword } },
      ];
    }
    if (criteria.category) where.category = criteria.category;
    if (criteria.isActive !== undefined) where.isActive = criteria.isActive;
    if (criteria.isControl !== undefined) where.isControl = criteria.isControl;
    if (criteria.parentId !== undefined) where.parentId = criteria.parentId;
    const rows = await (this.prisma.account as any).findMany({ where, orderBy: { code: "asc" } });
    return rows.map((r: any) => fromPrismaAccount(r));
  }

  async delete(id: AccountId): Promise<void> {
    await this.prisma.account.delete({ where: { id: id.value } });
  }
}

function fromPrismaJournalBatch(row: any, lines?: any[]): JournalBatch {
  const state: JournalBatchState = {
    id: row.id,
    batchNumber: row.batchNumber,
    journalType: row.journalType as JournalType,
    status: row.status as JournalEntryStatus,
    periodId: row.periodId,
    fiscalYearId: row.fiscalYearId,
    voucherTypeId: row.voucherTypeId ?? null,
    voucherSeriesId: row.voucherSeriesId ?? null,
    voucherNumber: row.voucherNumber ?? null,
    voucherDate: row.voucherDate,
    postingDate: row.postingDate,
    description: row.description,
    reference: row.reference ?? null,
    source: row.source ?? null,
    totalDebit: Number(row.totalDebit as bigint),
    totalCredit: Number(row.totalCredit as bigint),
    foreignTotalDebit: Number(row.foreignTotalDebit as bigint),
    foreignTotalCredit: Number(row.foreignTotalCredit as bigint),
    currencyCode: row.currencyCode,
    exchangeRate: Number(row.exchangeRate),
    isForeignCurrency: row.isForeignCurrency,
    approvedById: row.approvedById ?? null,
    approvedAt: row.approvedAt ?? null,
    postedById: row.postedById ?? null,
    postedAt: row.postedAt ?? null,
    reversedBatchId: row.reversedBatchId ?? null,
    recurringTemplateId: row.recurringTemplateId ?? null,
    attachmentCount: row.attachmentCount,
    commentCount: row.commentCount,
    lines: lines?.map(l => ({
      id: l.id,
      accountId: l.accountId,
      debitAmount: Number(l.debitAmount as bigint),
      creditAmount: Number(l.creditAmount as bigint),
      foreignDebitAmount: Number(l.foreignDebitAmount as bigint),
      foreignCreditAmount: Number(l.foreignCreditAmount as bigint),
      currencyCode: l.currencyCode,
      exchangeRate: Number(l.exchangeRate),
      description: l.description ?? null,
      costCenterId: l.costCenterId ?? null,
      departmentId: l.departmentId ?? null,
      projectId: l.projectId ?? null,
      lineOrder: l.lineOrder,
    })) ?? [],
    createdById: row.createdById,
    createdAt: row.createdAt,
    updatedAt: row.updatedAt,
    version: row.version,
    deletedAt: row.deletedAt ?? null,
  };
  return JournalBatch.load(state);
}

@Injectable()
export class PrismaJournalBatchRepository implements JournalBatchRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(batch: JournalBatch): Promise<void> {
    const s = batch.toState();
    const data: Record<string, unknown> = {
      id: s.id,
      batchNumber: s.batchNumber,
      journalType: s.journalType,
      status: s.status,
      periodId: s.periodId,
      fiscalYearId: s.fiscalYearId,
      voucherTypeId: s.voucherTypeId,
      voucherSeriesId: s.voucherSeriesId,
      voucherNumber: s.voucherNumber,
      voucherDate: s.voucherDate,
      postingDate: s.postingDate,
      description: s.description,
      reference: s.reference,
      source: s.source,
      totalDebit: BigInt(Math.round(s.totalDebit)),
      totalCredit: BigInt(Math.round(s.totalCredit)),
      foreignTotalDebit: BigInt(Math.round(s.foreignTotalDebit)),
      foreignTotalCredit: BigInt(Math.round(s.foreignTotalCredit)),
      currencyCode: s.currencyCode,
      exchangeRate: s.exchangeRate,
      isForeignCurrency: s.isForeignCurrency,
      approvedById: s.approvedById,
      approvedAt: s.approvedAt,
      postedById: s.postedById,
      postedAt: s.postedAt,
      reversedBatchId: s.reversedBatchId,
      recurringTemplateId: s.recurringTemplateId,
      attachmentCount: s.attachmentCount,
      commentCount: s.commentCount,
      createdById: s.createdById,
      version: s.version,
      deletedAt: s.deletedAt,
    };
    await this.prisma.journalBatch.upsert({
      where: { id: s.id },
      create: data as any,
      update: data as any,
    });

    // replace lines
    await this.prisma.journalEntryLine.deleteMany({ where: { batchId: s.id } });
    if (s.lines.length > 0) {
      await this.prisma.journalEntryLine.createMany({
        data: s.lines.map(l => ({
          id: l.id,
          batchId: s.id,
          accountId: l.accountId,
          debitAmount: BigInt(Math.round(l.debitAmount)),
          creditAmount: BigInt(Math.round(l.creditAmount)),
          foreignDebitAmount: BigInt(Math.round(l.foreignDebitAmount)),
          foreignCreditAmount: BigInt(Math.round(l.foreignCreditAmount)),
          currencyCode: l.currencyCode,
          exchangeRate: l.exchangeRate,
          description: l.description,
          costCenterId: l.costCenterId,
          departmentId: l.departmentId,
          projectId: l.projectId,
          lineOrder: l.lineOrder,
        })),
      });
    }
  }

  async findById(id: JournalBatchId): Promise<JournalBatch | null> {
    const row = await this.prisma.journalBatch.findUnique({
      where: { id: id.value },
      include: { lines: true },
    });
    return row ? fromPrismaJournalBatch(row, (row as any).lines) : null;
  }

  async findByBatchNumber(batchNumber: string): Promise<JournalBatch | null> {
    const row = await this.prisma.journalBatch.findUnique({
      where: { batchNumber },
      include: { lines: true },
    });
    return row ? fromPrismaJournalBatch(row, (row as any).lines) : null;
  }

  async findByPeriod(periodId: string): Promise<JournalBatch[]> {
    const rows = await this.prisma.journalBatch.findMany({
      where: { periodId },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => fromPrismaJournalBatch(r, (r as any).lines));
  }

  async findByStatus(status: JournalEntryStatus): Promise<JournalBatch[]> {
    const rows = await this.prisma.journalBatch.findMany({
      where: { status },
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => fromPrismaJournalBatch(r, (r as any).lines));
  }

  async findByDateRange(from: Date, to: Date): Promise<JournalBatch[]> {
    const rows = await this.prisma.journalBatch.findMany({
      where: { postingDate: { gte: from, lte: to } },
      include: { lines: true },
      orderBy: { postingDate: "asc" },
    });
    return rows.map(r => fromPrismaJournalBatch(r, (r as any).lines));
  }

  async findByAccountId(accountId: string, from?: Date, to?: Date): Promise<JournalBatch[]> {
    const where: Record<string, unknown> = {
      lines: { some: { accountId } },
    };
    if (from || to) {
      where.postingDate = {};
      if (from) (where.postingDate as Record<string, unknown>).gte = from;
      if (to) (where.postingDate as Record<string, unknown>).lte = to;
    }
    const rows = await (this.prisma.journalBatch as any).findMany({
      where,
      include: { lines: true },
      orderBy: { postingDate: "asc" },
    });
    return rows.map((r: any) => fromPrismaJournalBatch(r, r.lines));
  }

  async findAll(): Promise<JournalBatch[]> {
    const rows = await this.prisma.journalBatch.findMany({
      include: { lines: true },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(r => fromPrismaJournalBatch(r, (r as any).lines));
  }

  async delete(id: JournalBatchId): Promise<void> {
    await this.prisma.journalEntryLine.deleteMany({ where: { batchId: id.value } });
    await this.prisma.journalBatch.delete({ where: { id: id.value } });
  }
}

@Injectable()
export class PrismaFiscalYearRepository implements FiscalYearRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(fy: FiscalYear): Promise<void> {
    const s = fy.toState();
    await this.prisma.fiscalYear.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: FiscalYearId): Promise<FiscalYear | null> {
    const row = await this.prisma.fiscalYear.findUnique({ where: { id: id.value } });
    return row ? FiscalYear.load(row as FiscalYearState) : null;
  }

  async findByCode(code: string): Promise<FiscalYear | null> {
    const row = await this.prisma.fiscalYear.findUnique({ where: { code } });
    return row ? FiscalYear.load(row as FiscalYearState) : null;
  }

  async findActive(): Promise<FiscalYear | null> {
    const row = await this.prisma.fiscalYear.findFirst({
      where: { isActive: true, isClosed: false },
    });
    return row ? FiscalYear.load(row as FiscalYearState) : null;
  }

  async findAll(): Promise<FiscalYear[]> {
    const rows = await this.prisma.fiscalYear.findMany({ orderBy: { startDate: "desc" } });
    return rows.map(r => FiscalYear.load(r as FiscalYearState));
  }

  async delete(id: FiscalYearId): Promise<void> {
    await this.prisma.fiscalYear.delete({ where: { id: id.value } });
  }
}

@Injectable()
export class PrismaPeriodRepository implements PeriodRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(period: Period): Promise<void> {
    const s = period.toState();
    await this.prisma.period.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: PeriodId): Promise<Period | null> {
    const row = await this.prisma.period.findUnique({ where: { id: id.value } });
    return row ? Period.load(row as PeriodState) : null;
  }

  async findByFiscalYear(fiscalYearId: string): Promise<Period[]> {
    const rows = await this.prisma.period.findMany({
      where: { fiscalYearId },
      orderBy: { periodNumber: "asc" },
    });
    return rows.map(r => Period.load(r as PeriodState));
  }

  async findOpenByDate(date: Date): Promise<Period | null> {
    const row = await this.prisma.period.findFirst({
      where: {
        startDate: { lte: date },
        endDate: { gte: date },
        status: "open",
      },
    });
    return row ? Period.load(row as PeriodState) : null;
  }

  async findOpen(): Promise<Period[]> {
    const rows = await this.prisma.period.findMany({
      where: { status: "open" },
      orderBy: { periodNumber: "asc" },
    });
    return rows.map(r => Period.load(r as PeriodState));
  }
}

@Injectable()
export class PrismaVoucherTypeRepository implements VoucherTypeRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(vt: VoucherType): Promise<void> {
    const s = vt.toState();
    await this.prisma.voucherType.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: VoucherTypeId): Promise<VoucherType | null> {
    const row = await this.prisma.voucherType.findUnique({ where: { id: id.value } });
    return row ? VoucherType.load(row as VoucherTypeState) : null;
  }

  async findByCode(code: string): Promise<VoucherType | null> {
    const row = await this.prisma.voucherType.findUnique({ where: { code } });
    return row ? VoucherType.load(row as VoucherTypeState) : null;
  }

  async findAll(): Promise<VoucherType[]> {
    const rows = await this.prisma.voucherType.findMany({ orderBy: { code: "asc" } });
    return rows.map(r => VoucherType.load(r as VoucherTypeState));
  }

  async findActive(): Promise<VoucherType[]> {
    const rows = await this.prisma.voucherType.findMany({
      where: { isActive: true },
      orderBy: { code: "asc" },
    });
    return rows.map(r => VoucherType.load(r as VoucherTypeState));
  }
}

@Injectable()
export class PrismaVoucherSeriesRepository implements VoucherSeriesRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(vs: VoucherSeries): Promise<void> {
    const s = vs.toState();
    await this.prisma.voucherSeries.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: VoucherSeriesId): Promise<VoucherSeries | null> {
    const row = await this.prisma.voucherSeries.findUnique({ where: { id: id.value } });
    return row ? VoucherSeries.load(row as VoucherSeriesState) : null;
  }

  async findByCode(code: string): Promise<VoucherSeries | null> {
    const row = await this.prisma.voucherSeries.findUnique({ where: { code } });
    return row ? VoucherSeries.load(row as VoucherSeriesState) : null;
  }

  async findByVoucherType(voucherTypeId: string): Promise<VoucherSeries[]> {
    const rows = await this.prisma.voucherSeries.findMany({
      where: { voucherTypeId },
      orderBy: { code: "asc" },
    });
    return rows.map(r => VoucherSeries.load(r as VoucherSeriesState));
  }

  async findActive(): Promise<VoucherSeries[]> {
    const rows = await this.prisma.voucherSeries.findMany({
      where: { isActive: true },
      orderBy: { code: "asc" },
    });
    return rows.map(r => VoucherSeries.load(r as VoucherSeriesState));
  }

  async findNextSequence(voucherTypeId: string, fiscalYearId?: string): Promise<VoucherSeries | null> {
    const where: Record<string, unknown> = { voucherTypeId, isActive: true };
    if (fiscalYearId) where.fiscalYearId = fiscalYearId;
    return (await this.prisma.voucherSeries.findFirst({
      where: where as any,
      orderBy: { nextNumber: "asc" },
    })) as any;
  }
}

@Injectable()
export class PrismaExchangeRateRepository implements ExchangeRateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rate: ExchangeRate): Promise<void> {
    const s = rate.toState();
    await this.prisma.exchangeRate.upsert({
      where: { id: s.id },
      create: { ...s, rate: s.rate } as any,
      update: { ...s, rate: s.rate } as any,
    });
  }

  private toDomain(row: Record<string, unknown>): ExchangeRate {
    return ExchangeRate.load({
      ...row,
      rate: Number(row.rate),
    } as unknown as ExchangeRateState);
  }

  async findById(id: ExchangeRateId): Promise<ExchangeRate | null> {
    const row = await this.prisma.exchangeRate.findUnique({ where: { id: id.value } });
    return row ? this.toDomain(row as any) : null;
  }

  async findRate(fromCurrency: string, toCurrency: string, date: Date): Promise<ExchangeRate | null> {
    const row = await this.prisma.exchangeRate.findFirst({
      where: {
        fromCurrency,
        toCurrency,
        validFrom: { lte: date },
        validTo: { gte: date },
        isActive: true,
      },
      orderBy: { validFrom: "desc" },
    });
    return row ? this.toDomain(row as any) : null;
  }

  async findRatesByDate(date: Date): Promise<ExchangeRate[]> {
    const rows = await this.prisma.exchangeRate.findMany({
      where: {
        validFrom: { lte: date },
        validTo: { gte: date },
        isActive: true,
      },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findAll(): Promise<ExchangeRate[]> {
    const rows = await this.prisma.exchangeRate.findMany({ orderBy: { validFrom: "desc" } });
    return rows.map(r => this.toDomain(r as any));
  }
}

@Injectable()
export class PrismaCostCenterRepository implements CostCenterRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(cc: CostCenter): Promise<void> {
    const s = cc.toState();
    await this.prisma.costCenter.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: CostCenterId): Promise<CostCenter | null> {
    const row = await this.prisma.costCenter.findUnique({ where: { id: id.value } });
    return row ? CostCenter.load(row as CostCenterState) : null;
  }

  async findByCode(code: string): Promise<CostCenter | null> {
    const row = await this.prisma.costCenter.findUnique({ where: { code } });
    return row ? CostCenter.load(row as CostCenterState) : null;
  }

  async findAll(): Promise<CostCenter[]> {
    const rows = await this.prisma.costCenter.findMany({ orderBy: { code: "asc" } });
    return rows.map(r => CostCenter.load(r as CostCenterState));
  }

  async findActive(): Promise<CostCenter[]> {
    const rows = await this.prisma.costCenter.findMany({
      where: { status: "active" },
      orderBy: { code: "asc" },
    });
    return rows.map(r => CostCenter.load(r as CostCenterState));
  }
}

@Injectable()
export class PrismaDepartmentRepository implements DepartmentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(dept: Department): Promise<void> {
    const s = dept.toState();
    await this.prisma.department.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: DepartmentId): Promise<Department | null> {
    const row = await this.prisma.department.findUnique({ where: { id: id.value } });
    return row ? Department.load(row as DepartmentState) : null;
  }

  async findByCode(code: string): Promise<Department | null> {
    const row = await this.prisma.department.findUnique({ where: { code } });
    return row ? Department.load(row as DepartmentState) : null;
  }

  async findAll(): Promise<Department[]> {
    const rows = await this.prisma.department.findMany({ orderBy: { code: "asc" } });
    return rows.map(r => Department.load(r as DepartmentState));
  }

  async findActive(): Promise<Department[]> {
    const rows = await this.prisma.department.findMany({
      where: { status: "active" },
      orderBy: { code: "asc" },
    });
    return rows.map(r => Department.load(r as DepartmentState));
  }
}

@Injectable()
export class PrismaBudgetRepository implements BudgetRepository {
  constructor(private readonly prisma: PrismaService) {}

  private toDomain(row: Record<string, unknown>): Budget {
    const state = {
      ...row,
      totalOriginalAmount: Number(row.totalOriginalAmount),
      totalCurrentAmount: Number(row.totalCurrentAmount),
      totalUsedAmount: Number(row.totalUsedAmount),
      totalRemainingAmount: Number(row.totalRemainingAmount),
      lines: (row as any).lines ?? [],
    } as unknown as BudgetState;
    return Budget.load(state);
  }

  async save(budget: Budget): Promise<void> {
    const s = budget.toState();
    await this.prisma.budget.upsert({
      where: { id: s.id },
      create: { ...s } as any,
      update: { ...s } as any,
    });
  }

  async findById(id: BudgetId): Promise<Budget | null> {
    const row = await this.prisma.budget.findUnique({
      where: { id: id.value },
      include: { lines: true },
    });
    return row ? this.toDomain(row as any) : null;
  }

  async findByFiscalYear(fiscalYearId: string): Promise<Budget[]> {
    const rows = await this.prisma.budget.findMany({
      where: { fiscalYearId },
      orderBy: { code: "asc" },
      include: { lines: true },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByCostCenter(costCenterId: string): Promise<Budget[]> {
    const rows = await this.prisma.budget.findMany({
      where: { costCenterId },
      orderBy: { code: "asc" },
      include: { lines: true },
    });
    return rows.map(r => this.toDomain(r as any));
  }

  async findByAccountAndPeriod(accountId: string, fiscalYearId: string): Promise<Budget | null> {
    const row = await this.prisma.budgetLine.findFirst({
      where: { accountId },
      include: { budget: { include: { lines: true } } },
    });
    if (!row || (row as any).budget.fiscalYearId !== fiscalYearId) return null;
    return (row as any).budget ? this.toDomain((row as any).budget) : null;
  }

  async findAll(): Promise<Budget[]> {
    const rows = await this.prisma.budget.findMany({
      orderBy: { code: "asc" },
      include: { lines: true },
    });
    return rows.map(r => this.toDomain(r as any));
  }
}
