import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { Money } from "../../domain/shared/money.js";
import { PrismaService } from "../../prisma/prisma.service.js";
import { PrismaJournalBatchRepository, PrismaAccountRepository, PrismaPeriodRepository, PrismaFiscalYearRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { PrismaItemRepository } from "../../infrastructure/inventory/inventory-prisma-repos.js";
import { ItemId } from "../../domain/inventory/inv-ids.js";
import { JournalBatch, JournalType } from "../../domain/gl/journal.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { PeriodId, FiscalYearId } from "../../domain/gl/period.js";
import { InventoryTransactionType } from "../../domain/inventory/inv-enums.js";
import type { InventoryTransaction } from "../../domain/inventory/inv-transaction.js";

@Injectable()
export class InventoryGlService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly batchRepo: PrismaJournalBatchRepository,
    private readonly accountRepo: PrismaAccountRepository,
    private readonly periodRepo: PrismaPeriodRepository,
    private readonly fiscalYearRepo: PrismaFiscalYearRepository,
    private readonly itemRepo: PrismaItemRepository,
  ) {}

  async postTransactionGl(
    tx: InventoryTransaction,
    userId: string,
  ): Promise<{ batchNumber: string }> {
    const s = tx.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const lines = tx.lines;
    if (lines.length === 0) throw new DomainError("Validation", "No lines to post to GL");

    const batch = JournalBatch.create({
      batchNumber: `INV-${s.transactionNumber}-${Date.now()}`,
      journalType: JournalType.Standard,
      periodId: period.id,
      fiscalYearId: fiscalYear.id,
      voucherDate: s.transactionDate,
      postingDate: new Date(),
      description: this.getDescription(s.transactionType, s.transactionNumber),
      createdById: userId,
      reference: s.transactionNumber,
      source: "inventory",
    });

    for (const line of lines) {
      const item = await this.itemRepo.findById(ItemId.from(line.itemId));
      if (!item) throw new DomainError("NotFound", `Item ${line.itemId} not found`);

      await this.addTransactionLines(batch, s.transactionType, line, item);
    }

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

  private async addTransactionLines(
    batch: JournalBatch,
    txType: string,
    line: { itemId: string; quantity: number; totalCost: number; warehouseId: string; description?: string | null },
    item: { glInventoryAccountId: string | null; glCogsAccountId: string | null; glExpenseAccountId: string | null; glPurchaseAccountId: string | null; glTransferAccountId: string | null },
  ): Promise<void> {
    const invAcct = item.glInventoryAccountId ?? await this.findFlaggedAccount("isInventoryAccount");
    const desc = line.description ?? `${txType} - ${line.itemId}`;
    const absCost = Math.abs(line.totalCost);
    if (absCost === 0) return;

    switch (txType) {
      case InventoryTransactionType.GoodsReceipt: {
        const grirAcct = await this.findAccountByCodePrefix("331", "GR/IR clearing account (331*)");
        batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `NK ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: grirAcct, debitAmount: 0, creditAmount: absCost, description: `Phải trả người bán ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.GoodsIssue: {
        const cogsAcct = item.glCogsAccountId ?? await this.findAccountByCodePrefix("632", "COGS account (632*)");
        batch.addLine({ accountId: cogsAcct, debitAmount: absCost, creditAmount: 0, description: `GVHB ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `XK ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.TransferOut: {
        const transferAcct = item.glTransferAccountId ?? await this.findAccountByCodePrefix("157", "Transfer account (157*)");
        batch.addLine({ accountId: transferAcct, debitAmount: absCost, creditAmount: 0, description: `CC kho ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `XK chuyển kho ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.TransferIn:
      case InventoryTransactionType.ProductionReceipt: {
        const srcAcct = txType === InventoryTransactionType.TransferIn
          ? await this.findAccountByCodePrefix("157", "Transfer account (157*)")
          : (item.glExpenseAccountId ?? await this.findAccountByCodePrefix("154", "WIP account (154*)"));
        batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `NK ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: srcAcct, debitAmount: 0, creditAmount: absCost, description: `Giảm ${txType === InventoryTransactionType.TransferIn ? "CC kho" : "SX"} ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.ProductionConsumption: {
        const wipAcct = item.glExpenseAccountId ?? await this.findAccountByCodePrefix("154", "WIP account (154*)");
        batch.addLine({ accountId: wipAcct, debitAmount: absCost, creditAmount: 0, description: `SX ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `XK SX ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.AdjustmentIncrease: {
        batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `Điều chỉnh tăng ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        const reserveAcct = await this.findAccountByCodePrefix("711", "Other income account (711*)");
        batch.addLine({ accountId: reserveAcct, debitAmount: 0, creditAmount: absCost, description: `DT khác ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.AdjustmentDecrease:
      case InventoryTransactionType.WriteOff: {
        const expenseAcct = item.glCogsAccountId ?? await this.findAccountByCodePrefix("632", "COGS account (632*)");
        batch.addLine({ accountId: expenseAcct, debitAmount: absCost, creditAmount: 0, description: `Xóa sổ ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `Giảm ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.WriteOn: {
        batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `Ghi tăng ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        const incomeAcct = await this.findAccountByCodePrefix("711", "Other income account (711*)");
        batch.addLine({ accountId: incomeAcct, debitAmount: 0, creditAmount: absCost, description: `TN khác ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.ReturnToVendor: {
        const grirAcct = await this.findAccountByCodePrefix("331", "GR/IR clearing account (331*)");
        batch.addLine({ accountId: grirAcct, debitAmount: absCost, creditAmount: 0, description: `Trả lại NCC ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `Giảm kho ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.CustomerReturn: {
        const cogsAcct = item.glCogsAccountId ?? await this.findAccountByCodePrefix("632", "COGS account (632*)");
        batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `KH trả lại ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        batch.addLine({ accountId: cogsAcct, debitAmount: 0, creditAmount: absCost, description: `Giảm GVHB ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        break;
      }
      case InventoryTransactionType.Revaluation: {
        if (line.totalCost >= 0) {
          batch.addLine({ accountId: invAcct, debitAmount: absCost, creditAmount: 0, description: `Đánh giá tăng ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
          const reserveAcct = await this.findAccountByCodePrefix("412", "Revaluation reserve (412*)");
          batch.addLine({ accountId: reserveAcct, debitAmount: 0, creditAmount: absCost, description: `Chênh lệch ĐG ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        } else {
          const reserveAcct = await this.findAccountByCodePrefix("412", "Revaluation reserve (412*)");
          batch.addLine({ accountId: reserveAcct, debitAmount: absCost, creditAmount: 0, description: `Giảm chênh lệch ĐG ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
          batch.addLine({ accountId: invAcct, debitAmount: 0, creditAmount: absCost, description: `Đánh giá giảm ${desc}`, costCenterId: null, departmentId: null, projectId: null, currencyCode: "VND", exchangeRate: 1, foreignDebitAmount: 0, foreignCreditAmount: 0 });
        }
        break;
      }
      default:
        throw new DomainError("Validation", `Unsupported transaction type for GL posting: ${txType}`);
    }
  }

  private async findAccountByCodePrefix(prefix: string, label: string): Promise<string> {
    const account = await (this.prisma as any).account.findFirst({
      where: { code: { startsWith: prefix }, isActive: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    if (!account) throw new DomainError("NotFound", `No account found for ${label}`);
    return account.id;
  }

  private async findFlaggedAccount(flag: string): Promise<string> {
    const ext = await (this.prisma as any).accountExtension.findFirst({
      where: { [flag]: true, account: { isActive: true, deletedAt: null } },
      include: { account: true },
      orderBy: { createdAt: "asc" },
    });
    if (ext) return ext.accountId;
    throw new DomainError("NotFound", `No account configured with ${flag}=true`);
  }

  private getDescription(txType: string, txNumber: string): string {
    const labels: Record<string, string> = {
      [InventoryTransactionType.GoodsReceipt]: `Hạch toán NK kho - ${txNumber}`,
      [InventoryTransactionType.GoodsIssue]: `Hạch toán XK kho - ${txNumber}`,
      [InventoryTransactionType.TransferOut]: `Hạch toán chuyển kho (đi) - ${txNumber}`,
      [InventoryTransactionType.TransferIn]: `Hạch toán chuyển kho (đến) - ${txNumber}`,
      [InventoryTransactionType.AdjustmentIncrease]: `Hạch toán điều chỉnh tăng - ${txNumber}`,
      [InventoryTransactionType.AdjustmentDecrease]: `Hạch toán điều chỉnh giảm - ${txNumber}`,
      [InventoryTransactionType.WriteOff]: `Hạch toán xóa sổ - ${txNumber}`,
      [InventoryTransactionType.WriteOn]: `Hạch toán ghi tăng - ${txNumber}`,
      [InventoryTransactionType.ReturnToVendor]: `Hạch toán trả lại NCC - ${txNumber}`,
      [InventoryTransactionType.CustomerReturn]: `Hạch toán khách trả lại - ${txNumber}`,
      [InventoryTransactionType.ProductionConsumption]: `Hạch toán SX tiêu hao - ${txNumber}`,
      [InventoryTransactionType.ProductionReceipt]: `Hạch toán nhập kho SX - ${txNumber}`,
      [InventoryTransactionType.Revaluation]: `Hạch toán đánh giá lại - ${txNumber}`,
    };
    return labels[txType] ?? `Hạch toán tồn kho - ${txNumber} (${txType})`;
  }

  private async resolvePeriodFiscalYear(): Promise<{ period: any; fiscalYear: any }> {
    const now = new Date();
    const period = await this.periodRepo.findOpenByDate(now);
    if (!period) throw new DomainError("NotFound", "No active period found for GL posting");
    const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(period.fiscalYearId));
    if (!fiscalYear) throw new DomainError("NotFound", "Fiscal year not found for period");
    return { period, fiscalYear };
  }
}
