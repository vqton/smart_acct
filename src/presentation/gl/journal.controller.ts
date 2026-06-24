import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, ConflictException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaJournalBatchRepository, PrismaAccountRepository, PrismaPeriodRepository, PrismaFiscalYearRepository, PrismaVoucherTypeRepository, PrismaVoucherSeriesRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { JournalBatch, JournalBatchId, JournalEntryStatus } from "../../domain/gl/journal.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { Money } from "../../domain/shared/money.js";
import { PeriodId, FiscalYearId } from "../../domain/gl/period.js";
import { VoucherSeriesId } from "../../domain/gl/voucher.js";
import { CreateJournalBatchDto, ApproveBatchDto, PostBatchDto, ReverseBatchDto } from "./dto/journal.dto.js";

@ApiTags("GL Journals")
@Controller("api/gl/journals")
export class JournalController {
  constructor(
    private readonly batchRepo: PrismaJournalBatchRepository,
    private readonly accountRepo: PrismaAccountRepository,
    private readonly periodRepo: PrismaPeriodRepository,
    private readonly fiscalYearRepo: PrismaFiscalYearRepository,
    private readonly voucherTypeRepo: PrismaVoucherTypeRepository,
    private readonly voucherSeriesRepo: PrismaVoucherSeriesRepository,
  ) {}

  @Post()
  @ApiOperation({ summary: "Create journal batch with lines" })
  async create(@Body() dto: CreateJournalBatchDto) {
    const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(dto.fiscalYearId));
    if (!fiscalYear) throw new NotFoundException("Fiscal year not found");
    fiscalYear.canPost();

    const period = await this.periodRepo.findById(new PeriodId(dto.periodId));
    if (!period) throw new NotFoundException("Period not found");
    period.canPost();

    let batchNumber = "";
    if (dto.voucherSeriesId) {
      const series = await this.voucherSeriesRepo.findById(new VoucherSeriesId(dto.voucherSeriesId));
      if (!series) throw new NotFoundException("Voucher series not found");
      batchNumber = series.reserve();
      await this.voucherSeriesRepo.save(series);
    } else {
      batchNumber = `J${Date.now()}`;
    }

    // Validate all accounts exist
    for (const line of dto.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new NotFoundException(`Account ${line.accountId} not found`);
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

    for (const line of dto.lines) {
      batch.addLine({
        accountId: line.accountId,
        debitAmount: line.debitAmount,
        creditAmount: line.creditAmount,
        foreignDebitAmount: line.foreignDebitAmount ?? 0,
        foreignCreditAmount: line.foreignCreditAmount ?? 0,
        currencyCode: line.currencyCode ?? "VND",
        exchangeRate: line.exchangeRate ?? 1,
        description: line.description ?? null,
        costCenterId: line.costCenterId ?? null,
        departmentId: line.departmentId ?? null,
        projectId: line.projectId ?? null,
      });
    }

    batch.validateDebitCreditEqual();
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  @Get()
  @ApiOperation({ summary: "List journal batches" })
  async findAll(
    @Query("periodId") periodId?: string,
    @Query("status") status?: string,
    @Query("fromDate") fromDate?: string,
    @Query("toDate") toDate?: string,
  ) {
    if (periodId) return this.batchRepo.findByPeriod(periodId);
    if (status) return this.batchRepo.findByStatus(status as JournalEntryStatus);
    if (fromDate || toDate) {
      return this.batchRepo.findByDateRange(
        fromDate ? new Date(fromDate) : new Date(0),
        toDate ? new Date(toDate) : new Date("2100-01-01"),
      );
    }
    return this.batchRepo.findAll();
  }

  @Get(":id")
  @ApiOperation({ summary: "Get journal batch by ID" })
  async findById(@Param("id") id: string) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");
    return batch.toState();
  }

  @Put(":id/submit")
  @ApiOperation({ summary: "Submit batch for approval" })
  async submit(@Param("id") id: string) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");
    batch.submit();
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  @Put(":id/approve")
  @ApiOperation({ summary: "Approve batch" })
  async approve(@Param("id") id: string, @Body() dto: ApproveBatchDto) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");
    batch.approve(dto.userId);
    await this.batchRepo.save(batch);
    return batch.toState();
  }

  @Put(":id/post")
  @ApiOperation({ summary: "Post approved batch (update account balances)" })
  async post(@Param("id") id: string, @Body() dto: PostBatchDto) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");

    batch.post(dto.userId);

    // Update account balances
    for (const line of batch.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new NotFoundException(`Account ${line.accountId} not found`);
      account.canPost();
      account.updateBalance(Money.fromVnd(line.debitAmount), Money.fromVnd(line.creditAmount));
      await this.accountRepo.save(account);
    }

    await this.batchRepo.save(batch);
    return batch.toState();
  }

  @Put(":id/reverse")
  @ApiOperation({ summary: "Reverse a posted batch" })
  async reverse(@Param("id") id: string, @Body() dto: ReverseBatchDto) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");

    // Create reversal batch
    const reversal = JournalBatch.create({
      batchNumber: `R${Date.now()}`,
      journalType: batch.journalType,
      periodId: batch.periodId,
      fiscalYearId: batch.fiscalYearId,
      voucherDate: new Date(),
      postingDate: new Date(),
      description: `Đảo bút toán: ${dto.reason}`,
      createdById: dto.userId,
      reference: batch.batchNumber,
      source: dto.reason,
    });

    // Add inverted lines
    for (const line of batch.lines) {
      reversal.addLine({
        accountId: line.accountId,
        debitAmount: line.creditAmount,
        creditAmount: line.debitAmount,
        foreignDebitAmount: line.foreignCreditAmount,
        foreignCreditAmount: line.foreignDebitAmount,
        currencyCode: line.currencyCode,
        exchangeRate: line.exchangeRate,
        description: `Đảo: ${line.description ?? ""}`,
        costCenterId: line.costCenterId,
        departmentId: line.departmentId,
        projectId: line.projectId,
      });
    }

    reversal.validateDebitCreditEqual();
    reversal.post(dto.userId);

    // Update account balances (reverse)
    for (const line of reversal.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new NotFoundException(`Account ${line.accountId} not found`);
      account.canPost();
      account.updateBalance(Money.fromVnd(line.debitAmount), Money.fromVnd(line.creditAmount));
      await this.accountRepo.save(account);
    }

    batch.reverse(reversal.batchNumber);
    await this.batchRepo.save(reversal);
    await this.batchRepo.save(batch);

    return { reversed: batch.toState(), reversal: reversal.toState() };
  }

  @Put(":id/cancel")
  @ApiOperation({ summary: "Cancel a draft batch" })
  async cancel(@Param("id") id: string) {
    const batch = await this.batchRepo.findById(new JournalBatchId(id));
    if (!batch) throw new NotFoundException("Journal batch not found");
    batch.cancel();
    await this.batchRepo.save(batch);
    return batch.toState();
  }
}
