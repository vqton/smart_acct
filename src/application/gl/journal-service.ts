import { DomainError } from "../../shared/domain-error.js";
import {
  JournalBatch, JournalBatchId, JournalBatchState, JournalEntryLine,
  JournalType, JournalEntryStatus,
} from "../../domain/gl/journal.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { PeriodId, FiscalYearId } from "../../domain/gl/period.js";
import { VoucherSeriesId, SequenceMethod } from "../../domain/gl/voucher.js";
import {
  JournalBatchRepository, AccountRepository, PeriodRepository,
  FiscalYearRepository, VoucherTypeRepository, VoucherSeriesRepository,
  UnitOfWork,
} from "../../domain/gl/repositories.js";

export interface CreateJournalLineDTO {
  accountId: string;
  debitAmount: number;
  creditAmount: number;
  currencyCode?: string;
  exchangeRate?: number;
  description?: string;
  costCenterId?: string;
  departmentId?: string;
  projectId?: string;
}

export interface CreateJournalBatchDTO {
  journalType: JournalType;
  periodId: string;
  fiscalYearId: string;
  voucherDate: string;
  postingDate: string;
  description: string;
  voucherTypeId?: string;
  voucherSeriesId?: string;
  reference?: string;
  source?: string;
  createdById: string;
  lines: CreateJournalLineDTO[];
}

export interface JournalSearchCriteria {
  fromDate?: string;
  toDate?: string;
  status?: JournalEntryStatus;
  journalType?: JournalType;
  accountId?: string;
  periodId?: string;
  keyword?: string;
}

export class JournalService {
  constructor(
    private readonly batchRepo: JournalBatchRepository,
    private readonly accountRepo: AccountRepository,
    private readonly periodRepo: PeriodRepository,
    private readonly fiscalYearRepo: FiscalYearRepository,
    private readonly voucherTypeRepo: VoucherTypeRepository,
    private readonly voucherSeriesRepo: VoucherSeriesRepository,
    private readonly uow: UnitOfWork,
  ) {}

  async create(dto: CreateJournalBatchDTO): Promise<JournalBatchState> {
    const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(dto.fiscalYearId));
    if (!fiscalYear) throw new DomainError("NotFound", "Fiscal year not found");
    fiscalYear.canPost();

    const period = await this.periodRepo.findById(new PeriodId(dto.periodId));
    if (!period) throw new DomainError("NotFound", "Period not found");
    period.canPost();

    let batchNumber = "";
    if (dto.voucherSeriesId) {
      const series = await this.voucherSeriesRepo.findById(new VoucherSeriesId(dto.voucherSeriesId));
      if (!series) throw new DomainError("NotFound", "Voucher series not found");
      batchNumber = series.reserve();
      await this.voucherSeriesRepo.save(series);
    } else {
      batchNumber = `J${Date.now()}`;
    }

    const batch = JournalBatch.create({
      batchNumber,
      journalType: dto.journalType,
      periodId: dto.periodId,
      fiscalYearId: dto.fiscalYearId,
      voucherDate: new Date(dto.voucherDate),
      postingDate: new Date(dto.postingDate),
      description: dto.description,
      createdById: dto.createdById,
      voucherTypeId: dto.voucherTypeId,
      voucherSeriesId: dto.voucherSeriesId,
      reference: dto.reference,
      source: dto.source,
    });

    for (const lineDto of dto.lines) {
      const account = await this.accountRepo.findById(new AccountId(lineDto.accountId));
      if (!account) throw new DomainError("NotFound", `Account ${lineDto.accountId} not found`);
      account.canPost();

      batch.addLine({
        accountId: lineDto.accountId,
        debitAmount: lineDto.debitAmount,
        creditAmount: lineDto.creditAmount,
        foreignDebitAmount: 0,
        foreignCreditAmount: 0,
        currencyCode: lineDto.currencyCode ?? "VND",
        exchangeRate: lineDto.exchangeRate ?? 1,
        description: lineDto.description ?? null,
        costCenterId: lineDto.costCenterId ?? null,
        departmentId: lineDto.departmentId ?? null,
        projectId: lineDto.projectId ?? null,
      });
    }

    batch.validateDebitCreditEqual();
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  async submit(id: string): Promise<JournalBatchState> {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new DomainError("NotFound", "Batch not found");
    batch.submit();
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  async approve(id: string, userId: string): Promise<JournalBatchState> {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new DomainError("NotFound", "Batch not found");
    batch.approve(userId);
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  async findById(id: string): Promise<JournalBatchState> {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new DomainError("NotFound", "Batch not found");
    return batch.toState();
  }

  async findByPeriod(periodId: string): Promise<JournalBatchState[]> {
    const batches = await this.batchRepo.findByPeriod(periodId);
    return batches.map(b => b.toState());
  }

  async findByDateRange(from: string, to: string): Promise<JournalBatchState[]> {
    const batches = await this.batchRepo.findByDateRange(new Date(from), new Date(to));
    return batches.map(b => b.toState());
  }

  async search(criteria: JournalSearchCriteria): Promise<JournalBatchState[]> {
    if (criteria.accountId) {
      const batches = await this.batchRepo.findByAccountId(
        criteria.accountId,
        criteria.fromDate ? new Date(criteria.fromDate) : undefined,
        criteria.toDate ? new Date(criteria.toDate) : undefined,
      );
      return batches.map(b => b.toState());
    }
    if (criteria.periodId) {
      return this.findByPeriod(criteria.periodId);
    }
    if (criteria.fromDate && criteria.toDate) {
      return this.findByDateRange(criteria.fromDate, criteria.toDate);
    }
    const all = await this.batchRepo.findAll();
    return all.map(b => b.toState());
  }

  async cancel(id: string): Promise<void> {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new DomainError("NotFound", "Batch not found");
    batch.cancel();
    await this.batchRepo.save(batch);
  }

  async delete(id: string): Promise<void> {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new DomainError("NotFound", "Batch not found");
    batch.markDeleted();
    await this.batchRepo.save(batch);
  }
}
