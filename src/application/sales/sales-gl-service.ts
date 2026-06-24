import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PrismaService } from "../../prisma/prisma.service.js";
import { PrismaJournalBatchRepository, PrismaAccountRepository, PrismaPeriodRepository, PrismaFiscalYearRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { JournalBatch, JournalType } from "../../domain/gl/journal.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { PeriodId, FiscalYearId } from "../../domain/gl/period.js";
import type { SalesInvoice } from "../../domain/sales/sales-invoice.js";
import type { CustomerReceipt } from "../../domain/sales/sales-payment.js";

@Injectable()
export class SalesGlService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly batchRepo: PrismaJournalBatchRepository,
    private readonly accountRepo: PrismaAccountRepository,
    private readonly periodRepo: PrismaPeriodRepository,
    private readonly fiscalYearRepo: PrismaFiscalYearRepository,
  ) {}

  async postInvoiceGl(invoice: SalesInvoice, postedById: string): Promise<{ batchNumber: string }> {
    const s = invoice.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const [arAccountId, revenueAccountId, vatAccountId] = await Promise.all([
      this.findAccountByFlag("isReceivableAccount"),
      this.findRevenueAccount(),
      this.findVatOutputAccount(),
    ]);

    const batch = JournalBatch.create({
      batchNumber: `SI-${s.invoiceNumber}-${Date.now()}`,
      journalType: JournalType.Standard,
      periodId: period.id,
      fiscalYearId: fiscalYear.id,
      voucherDate: s.invoiceDate,
      postingDate: new Date(),
      description: `Hạch toán doanh thu - HĐ ${s.invoiceNumber}`,
      createdById: postedById,
      reference: s.invoiceNumber,
      source: "sales_invoice",
    });

    batch.addLine({
      accountId: arAccountId,
      debitAmount: s.grandTotal,
      creditAmount: 0,
      description: `Phải thu khách hàng - ${s.invoiceNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    batch.addLine({
      accountId: revenueAccountId,
      debitAmount: 0,
      creditAmount: s.subtotal,
      description: `Doanh thu bán hàng - ${s.invoiceNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    if (s.taxAmount > 0) {
      batch.addLine({
        accountId: vatAccountId,
        debitAmount: 0,
        creditAmount: s.taxAmount,
        description: `Thuế GTGT đầu ra - ${s.invoiceNumber}`,
        costCenterId: null, departmentId: null, projectId: null,
        currencyCode: "VND", exchangeRate: 1,
        foreignDebitAmount: 0, foreignCreditAmount: 0,
      });
    }

    batch.submit();
    batch.approve(postedById);
    batch.post(postedById);

    for (const line of batch.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new DomainError("NotFound", `Account ${line.accountId} not found`);
      account.canPost();
      account.updateBalance(line.debitAmount, line.creditAmount);
      await this.accountRepo.save(account);
    }

    await this.batchRepo.save(batch);
    return { batchNumber: batch.batchNumber };
  }

  async postReceiptGl(receipt: CustomerReceipt, approvedBy: string): Promise<{ batchNumber: string }> {
    const s = receipt.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const [cashAccountId, arAccountId] = await Promise.all([
      this.findCashOrBankAccount(),
      this.findAccountByFlag("isReceivableAccount"),
    ]);

    const batch = JournalBatch.create({
      batchNumber: `SR-${s.receiptNumber}-${Date.now()}`,
      journalType: JournalType.Standard,
      periodId: period.id,
      fiscalYearId: fiscalYear.id,
      voucherDate: s.paymentDate,
      postingDate: new Date(),
      description: `Thu tiền khách hàng - PN ${s.receiptNumber}`,
      createdById: approvedBy,
      reference: s.receiptNumber,
      source: "sales_receipt",
    });

    batch.addLine({
      accountId: cashAccountId,
      debitAmount: s.amount,
      creditAmount: 0,
      description: `Tiền thu từ khách hàng - ${s.receiptNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    batch.addLine({
      accountId: arAccountId,
      debitAmount: 0,
      creditAmount: s.amount,
      description: `Bù trừ công nợ phải thu - ${s.receiptNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    batch.submit();
    batch.approve(approvedBy);
    batch.post(approvedBy);

    for (const line of batch.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new DomainError("NotFound", `Account ${line.accountId} not found`);
      account.canPost();
      account.updateBalance(line.debitAmount, line.creditAmount);
      await this.accountRepo.save(account);
    }

    await this.batchRepo.save(batch);
    return { batchNumber: batch.batchNumber };
  }

  async postCreditNoteGl(creditNote: SalesInvoice, postedById: string): Promise<{ batchNumber: string }> {
    const s = creditNote.toState();
    const { period, fiscalYear } = await this.resolvePeriodFiscalYear();
    const [arAccountId, revenueAccountId, vatAccountId] = await Promise.all([
      this.findAccountByFlag("isReceivableAccount"),
      this.findRevenueAccount(),
      this.findVatOutputAccount(),
    ]);

    const batch = JournalBatch.create({
      batchNumber: `SCN-${s.invoiceNumber}-${Date.now()}`,
      journalType: JournalType.Standard,
      periodId: period.id,
      fiscalYearId: fiscalYear.id,
      voucherDate: s.invoiceDate,
      postingDate: new Date(),
      description: `Giảm trừ doanh thu - HĐĐC ${s.invoiceNumber}`,
      createdById: postedById,
      reference: s.invoiceNumber,
      source: "sales_credit_note",
    });

    batch.addLine({
      accountId: arAccountId,
      debitAmount: 0,
      creditAmount: s.grandTotal,
      description: `Giảm công nợ phải thu - ${s.invoiceNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    batch.addLine({
      accountId: revenueAccountId,
      debitAmount: s.subtotal,
      creditAmount: 0,
      description: `Giảm doanh thu - ${s.invoiceNumber}`,
      costCenterId: null, departmentId: null, projectId: null,
      currencyCode: "VND", exchangeRate: 1,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
    });

    if (s.taxAmount > 0) {
      batch.addLine({
        accountId: vatAccountId,
        debitAmount: s.taxAmount,
        creditAmount: 0,
        description: `Giảm thuế GTGT - ${s.invoiceNumber}`,
        costCenterId: null, departmentId: null, projectId: null,
        currencyCode: "VND", exchangeRate: 1,
        foreignDebitAmount: 0, foreignCreditAmount: 0,
      });
    }

    batch.submit();
    batch.approve(postedById);
    batch.post(postedById);

    for (const line of batch.lines) {
      const account = await this.accountRepo.findById(new AccountId(line.accountId));
      if (!account) throw new DomainError("NotFound", `Account ${line.accountId} not found`);
      account.canPost();
      account.updateBalance(line.debitAmount, line.creditAmount);
      await this.accountRepo.save(account);
    }

    await this.batchRepo.save(batch);
    return { batchNumber: batch.batchNumber };
  }

  private async resolvePeriodFiscalYear(): Promise<{ period: any; fiscalYear: any }> {
    const now = new Date();
    const period = await this.periodRepo.findOpenByDate(now);
    if (!period) throw new DomainError("NotFound", "No active period found for GL posting");

    const fiscalYear = await this.fiscalYearRepo.findById(new FiscalYearId(period.fiscalYearId));
    if (!fiscalYear) throw new DomainError("NotFound", "Fiscal year not found for period");

    return { period, fiscalYear };
  }

  private async findAccountByFlag(flag: string): Promise<string> {
    const ext = await (this.prisma as any).accountExtension.findFirst({
      where: { [flag]: true, account: { isActive: true, deletedAt: null } },
      include: { account: true },
      orderBy: { createdAt: "asc" },
    });
    if (ext) return ext.accountId;
    throw new DomainError("NotFound", `No account configured with ${flag}=true`);
  }

  private async findRevenueAccount(): Promise<string> {
    const ext = await (this.prisma as any).accountExtension.findFirst({
      where: { account: { code: { startsWith: "511" }, isActive: true, deletedAt: null } },
      include: { account: true },
      orderBy: { createdAt: "asc" },
    });
    if (ext) return ext.accountId;
    const account = await (this.prisma as any).account.findFirst({
      where: { code: { startsWith: "511" }, isActive: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    if (account) return account.id;
    throw new DomainError("NotFound", "No revenue account (511*) configured");
  }

  private async findVatOutputAccount(): Promise<string> {
    const ext = await (this.prisma as any).accountExtension.findFirst({
      where: { isTaxAccount: true, account: { code: { startsWith: "3331" }, isActive: true, deletedAt: null } },
      include: { account: true },
      orderBy: { createdAt: "asc" },
    });
    if (ext) return ext.accountId;
    const account = await (this.prisma as any).account.findFirst({
      where: { code: { startsWith: "3331" }, isActive: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    if (account) return account.id;
    throw new DomainError("NotFound", "No VAT output account (3331*) configured");
  }

  private async findCashOrBankAccount(): Promise<string> {
    const ext = await (this.prisma as any).accountExtension.findFirst({
      where: { OR: [{ isCashAccount: true }, { isBankAccount: true }], account: { isActive: true, deletedAt: null } },
      include: { account: true },
      orderBy: { createdAt: "asc" },
    });
    if (ext) return ext.accountId;
    const account = await (this.prisma as any).account.findFirst({
      where: { code: { startsWith: "111" }, isActive: true, deletedAt: null },
      orderBy: { code: "asc" },
    });
    if (account) return account.id;
    throw new DomainError("NotFound", "No cash/bank account (111*) configured");
  }
}
