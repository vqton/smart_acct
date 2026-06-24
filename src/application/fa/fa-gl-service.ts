import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { JournalBatch, JournalType } from "../../domain/gl/journal.js";
import { PrismaJournalBatchRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaAccountRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaPeriodRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaFiscalYearRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { PeriodId, FiscalYearId } from "../../domain/gl/period.js";
import { Money } from "../../domain/shared/money.js";
import { FaAsset, FaAssetState } from "../../domain/fa/fa-asset.js";
import { FaDisposal } from "../../domain/fa/fa-disposal.js";
import { FaAcquisitionType, FaDisposalType } from "../../domain/fa/fa-enums.js";
import { PrismaService } from "../../prisma/prisma.service.js";

@Injectable()
export class FaGlService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly batchRepo: PrismaJournalBatchRepository,
    private readonly accountRepo: PrismaAccountRepository,
    private readonly periodRepo: PrismaPeriodRepository,
    private readonly fiscalYearRepo: PrismaFiscalYearRepository,
  ) {}

  async postAcquisition(asset: FaAsset, userId: string): Promise<{ batchNumber: string }> {
    const s = asset.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const batch = this.createBatch(`FA-MUA-${s.assetCode}-${Date.now()}`, JournalType.Standard, period, fiscalYear, `Mua TSCĐ ${s.assetCode} - ${s.assetName}`, userId, s.assetCode);

    // Nợ 211 - Nguyên giá TSCĐ / Có 331 - Phải trả người bán
    const assetAcct = await this.findAccountByCode("211", "Tài khoản TSCĐ hữu hình (211)");
    const payableAcct = await this.findAccountByCode("331", "Phải trả người bán (331)");
    const totalCost = s.originalCost + (s.importDutyPaid ?? 0) + (s.nonRefundableTax ?? 0);

    batch.addLine({ accountId: assetAcct, debitAmount: totalCost, creditAmount: 0, description: `Nguyên giá TSCĐ ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    batch.addLine({ accountId: payableAcct, debitAmount: 0, creditAmount: totalCost, description: `Phải trả người bán ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });

    return this.postBatch(batch, userId);
  }

  async postCapitalization(asset: FaAsset, userId: string): Promise<{ batchNumber: string }> {
    const s = asset.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const batch = this.createBatch(`FA-TBH-${s.assetCode}-${Date.now()}`, JournalType.Standard, period, fiscalYear, `Tăng TSCĐ ${s.assetCode}`, userId, s.assetCode);

    // Nợ 211 - TSCĐ / Có 241 - XDCB (nếu CIP) hoặc Có 111/112/331
    if (s.cipProjectId) {
      const assetAcct = await this.findAccountByCode("211", "TSCĐ hữu hình (211)");
      const cipAcct = await this.findAccountByCode("241", "XDCB dở dang (241)");
      batch.addLine({ accountId: assetAcct, debitAmount: s.originalCost, creditAmount: 0, description: `Kết chuyển TBH ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
      batch.addLine({ accountId: cipAcct, debitAmount: 0, creditAmount: s.originalCost, description: `Giảm XDCB ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    }

    return this.postBatch(batch, userId);
  }

  async postDepreciation(p: {
    assetCode: string; assetName: string; amount: number;
    glDepreciationAccountId?: string; glExpenseAccountId?: string;
    periodId: string; fiscalYearId: string; batchNumber: string;
    userId: string;
  }): Promise<{ batchNumber: string }> {
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const batch = this.createBatch(p.batchNumber, JournalType.Standard, period, fiscalYear, `Khấu hao TSCĐ ${p.assetCode} - ${p.assetName}`, p.userId, p.assetCode);

    // Nợ 627/641/642 / Có 214 - Hao mòn TSCĐ
    const expenseAcct = p.glExpenseAccountId ?? await this.findAccountByCode("627", "Chi phí SXC (627)");
    const deprAcct = p.glDepreciationAccountId ?? await this.findAccountByCode("2141", "Hao mòn TSCĐ hữu hình (2141)");

    batch.addLine({ accountId: expenseAcct, debitAmount: p.amount, creditAmount: 0, description: `KH TSCĐ ${p.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    batch.addLine({ accountId: deprAcct, debitAmount: 0, creditAmount: p.amount, description: `KH TSCĐ ${p.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });

    return this.postBatch(batch, p.userId);
  }

  async postDisposal(asset: FaAsset, disposal: FaDisposal, userId: string): Promise<{ batchNumber: string }> {
    const s = asset.toState();
    const d = disposal.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const batch = this.createBatch(`FA-THANHLY-${s.assetCode}-${Date.now()}`, JournalType.Standard, period, fiscalYear, `Thanh lý TSCĐ ${s.assetCode}`, userId, s.assetCode);

    const deprAcct = await this.findAccountByCode("2141", "Hao mòn TSCĐ (2141)");
    const assetAcct = await this.findAccountByCode("211", "TSCĐ hữu hình (211)");

    // Ghi giảm TSCĐ: Nợ 214 / Có 211
    batch.addLine({ accountId: deprAcct, debitAmount: d.accumulatedDepreciation, creditAmount: 0, description: `Giảm hao mòn ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    batch.addLine({ accountId: assetAcct, debitAmount: 0, creditAmount: d.originalCost, description: `Giảm nguyên giá ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });

    // Xử lý lãi/lỗ
    if (d.gainOnDisposal > 0) {
      const gainAcct = await this.findAccountByCode("711", "Thu nhập khác (711)");
      batch.addLine({ accountId: new AccountId(s.id).value, debitAmount: 0, creditAmount: d.gainOnDisposal, description: `Lãi thanh lý ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
      batch.addLine({ accountId: gainAcct, debitAmount: 0, creditAmount: d.gainOnDisposal, description: `Lãi thanh lý ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    }
    if (d.lossOnDisposal > 0) {
      const lossAcct = await this.findAccountByCode("811", "Chi phí khác (811)");
      batch.addLine({ accountId: lossAcct, debitAmount: d.lossOnDisposal, creditAmount: 0, description: `Lỗ thanh lý ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
      batch.addLine({ accountId: new AccountId(s.id).value, debitAmount: 0, creditAmount: d.lossOnDisposal, description: `Lỗ thanh lý ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    }

    return this.postBatch(batch, userId);
  }

  async postRevaluation(asset: FaAsset, userId: string): Promise<{ batchNumber: string }> {
    const s = asset.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();

    const revalAmount = s.revaluationAmount;
    if (revalAmount === 0) throw new DomainError("Validation", "No revaluation to post");

    const batch = this.createBatch(`FA-DG-${s.assetCode}-${Date.now()}`, JournalType.Standard, period, fiscalYear, `Đánh giá lại TSCĐ ${s.assetCode}`, userId, s.assetCode);

    const assetAcct = await this.findAccountByCode("211", "TSCĐ hữu hình (211)");
    if (revalAmount > 0) {
      const reserveAcct = await this.findAccountByCode("412", "Chênh lệch đánh giá lại (412)");
      batch.addLine({ accountId: assetAcct, debitAmount: revalAmount, creditAmount: 0, description: `Đánh giá tăng ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
      batch.addLine({ accountId: reserveAcct, debitAmount: 0, creditAmount: revalAmount, description: `Dự phòng ĐG ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    } else {
      const absReval = Math.abs(revalAmount);
      const reserveAcct = await this.findAccountByCode("412", "Chênh lệch đánh giá lại (412)");
      batch.addLine({ accountId: reserveAcct, debitAmount: absReval, creditAmount: 0, description: `Giảm dự phòng ĐG ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
      batch.addLine({ accountId: assetAcct, debitAmount: 0, creditAmount: absReval, description: `Đánh giá giảm ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    }

    return this.postBatch(batch, userId);
  }

  async postImpairment(asset: FaAsset, userId: string, impairmentLoss: number): Promise<{ batchNumber: string }> {
    const s = asset.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const batch = this.createBatch(`FA-STT-${s.assetCode}-${Date.now()}`, JournalType.Standard, period, fiscalYear, `Suy giảm TSCĐ ${s.assetCode}`, userId, s.assetCode);

    // Nợ 627/641/642 / Có 229 - Dự phòng giảm giá
    const expenseAcct = await this.findAccountByCode("627", "Chi phí SXC (627)");
    const impairAcct = await this.findAccountByCode("229", "Dự phòng giảm giá TSCĐ (229)");

    batch.addLine({ accountId: expenseAcct, debitAmount: impairmentLoss, creditAmount: 0, description: `Suy giảm ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
    batch.addLine({ accountId: impairAcct, debitAmount: 0, creditAmount: impairmentLoss, description: `DP giảm giá ${s.assetCode}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });

    return this.postBatch(batch, userId);
  }

  private createBatch(
    batchNumber: string, journalType: JournalType,
    period: any, fiscalYear: any,
    description: string, userId: string, reference: string,
  ): JournalBatch {
    return JournalBatch.create({
      batchNumber, journalType,
      periodId: period.id, fiscalYearId: fiscalYear.id,
      voucherDate: new Date(), postingDate: new Date(),
      description, createdById: userId,
      reference, source: "fixed_asset",
    });
  }

  private async postBatch(batch: JournalBatch, userId: string): Promise<{ batchNumber: string }> {
    batch.submit();
    batch.approve(userId);
    batch.post(userId);

    for (const bl of batch.lines) {
      const acct = await this.accountRepo.findById(new AccountId(bl.accountId));
      if (!acct) throw new DomainError("NotFound", `Account ${bl.accountId} not found`);
      acct.canPost();
      acct.updateBalance(Money.fromVnd(bl.debitAmount), Money.fromVnd(bl.creditAmount));
      await this.accountRepo.save(acct);
    }

    await this.batchRepo.save(batch);
    return { batchNumber: batch.batchNumber };
  }

  private async findAccountByCode(code: string, label: string): Promise<string> {
    const account = await (this.prisma as any).account.findFirst({
      where: { code, isActive: true, deletedAt: null },
    });
    if (!account) throw new DomainError("NotFound", `No account found for ${label}`);
    return account.id;
  }

  private async resolvePeriodFiscalYear(): Promise<{ period: any; fiscalYear: any }> {
    const now = new Date();
    const period = await this.periodRepo.findOpenByDate(now);
    if (!period) throw new DomainError("NotFound", "No active period found for GL posting");
    const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(period.fiscalYearId));
    if (!fiscalYear) throw new DomainError("NotFound", "Fiscal year not found");
    return { period, fiscalYear };
  }
}
