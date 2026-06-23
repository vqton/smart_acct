import { DomainError } from "../../shared/domain-error.js";
import { AccountRepository } from "../../domain/gl/repositories.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { JournalService, CreateJournalLineDTO } from "../gl/journal-service.js";
import { PostingEngine, PostingResult, PostingOptions } from "../gl/posting-engine.js";
import { TaxCalculationResult } from "../../domain/tax/tax-calculation.js";
import { TaxCodeRepository } from "../../domain/tax/tax-repositories.js";
import { TaxCode, TaxRateApplication } from "../../domain/tax/tax-code.js";
import { TransactionSide } from "../../domain/tax/tax-calculation.js";

export type TaxPostingTransactionType = "purchase" | "sales" | "expense" | "cit_accrual";

export interface TaxGlPostingRequest {
  calculationResult: TaxCalculationResult;
  transactionType: TaxPostingTransactionType;
  transactionDate: string;
  postingDate: string;
  description: string;
  periodId: string;
  fiscalYearId: string;
  createdById: string;
  counterpartyAccountId?: string;
  primaryAccountId?: string;
  voucherTypeId?: string;
  voucherSeriesId?: string;
  reference?: string;
  source?: string;
  idempotencyKey?: string;
}

export class TaxGlPostingService {
  constructor(
    private readonly journalService: JournalService,
    private readonly postingEngine: PostingEngine,
    private readonly accountRepo: AccountRepository,
    private readonly taxCodeRepo: TaxCodeRepository,
  ) {}

  async postTaxJournal(request: TaxGlPostingRequest): Promise<PostingResult> {
    const lines = await this.buildJournalLines(request);

    const batch = await this.journalService.create({
      journalType: "standard" as any,
      periodId: request.periodId,
      fiscalYearId: request.fiscalYearId,
      voucherDate: request.transactionDate,
      postingDate: request.postingDate,
      description: request.description,
      createdById: request.createdById,
      voucherTypeId: request.voucherTypeId,
      voucherSeriesId: request.voucherSeriesId,
      reference: request.reference,
      source: request.source ?? "tax-engine",
      lines,
    });

    const submitted = await this.journalService.submit(batch.id);
    await this.journalService.approve(submitted.id, request.createdById);

    const options: PostingOptions = {};
    if (request.idempotencyKey) options.idempotencyKey = request.idempotencyKey;

    return this.postingEngine.post(batch.id, request.createdById, options);
  }

  private async buildJournalLines(request: TaxGlPostingRequest): Promise<CreateJournalLineDTO[]> {
    const calc = request.calculationResult;

    switch (request.transactionType) {
      case "purchase": return this.buildPurchaseLines(calc, request);
      case "sales": return this.buildSalesLines(calc, request);
      case "expense": return this.buildExpenseLines(calc, request);
      case "cit_accrual": return this.buildCitLines(calc, request);
      default: throw new DomainError("Validation", `Unsupported transaction type: ${request.transactionType}`);
    }
  }

  private async buildPurchaseLines(calc: TaxCalculationResult, req: TaxGlPostingRequest): Promise<CreateJournalLineDTO[]> {
    const lines: CreateJournalLineDTO[] = [];
    let totalTax = 0;
    let totalNet = 0;

    for (const line of calc.lines) {
      const taxCode = line.taxCode ? await this.taxCodeRepo.findByCode(line.taxCode) : null;
      const expenseAccount = req.primaryAccountId ?? taxCode?.glExpenseAccountId ?? null;
      const recoverableAccount = taxCode?.glRecoverableAccountId ?? null;

      if (!expenseAccount) {
        throw new DomainError("Validation", `No GL expense account for tax code ${line.taxCode}. Set primaryAccountId or configure glExpenseAccountId on tax code.`);
      }

      totalNet += line.taxableAmount;
      totalTax += line.taxAmount;

      lines.push({
        accountId: expenseAccount,
        debitAmount: line.taxableAmount,
        creditAmount: 0,
        description: `Purchase: ${line.taxCode}`,
      });

      if (recoverableAccount && line.recoverableAmount > 0 && !line.isExempt && !line.isZeroRated) {
        lines.push({
          accountId: recoverableAccount,
          debitAmount: line.recoverableAmount,
          creditAmount: 0,
          description: `VAT recoverable: ${line.taxCode}`,
        });
      }
    }

    const apAccount = req.counterpartyAccountId;
    if (apAccount) {
      const total = totalNet + totalTax;
      lines.push({
        accountId: apAccount,
        debitAmount: 0,
        creditAmount: total,
        description: "AP - purchase with tax",
      });
    }

    return lines;
  }

  private async buildSalesLines(calc: TaxCalculationResult, req: TaxGlPostingRequest): Promise<CreateJournalLineDTO[]> {
    const lines: CreateJournalLineDTO[] = [];
    let totalNet = 0;
    let totalTax = 0;

    const revenueAccount = req.primaryAccountId ?? null;
    if (!revenueAccount) {
      throw new DomainError("Validation", "primaryAccountId (revenue account) required for sales posting");
    }

    let taxPayableAccount: string | null = null;

    for (const line of calc.lines) {
      const taxCode = line.taxCode ? await this.taxCodeRepo.findByCode(line.taxCode) : null;
      if (taxCode?.glTaxAccountId) {
        taxPayableAccount = taxCode.glTaxAccountId;
      }

      totalNet += line.taxableAmount;
      totalTax += line.taxAmount;

      lines.push({
        accountId: revenueAccount,
        debitAmount: 0,
        creditAmount: line.taxableAmount,
        description: `Revenue: ${line.taxCode}`,
      });
    }

    if (totalTax > 0 && taxPayableAccount) {
      lines.push({
        accountId: taxPayableAccount,
        debitAmount: 0,
        creditAmount: totalTax,
        description: "VAT payable",
      });
    }

    const arAccount = req.counterpartyAccountId;
    if (arAccount) {
      const total = totalNet + totalTax;
      lines.push({
        accountId: arAccount,
        debitAmount: total,
        creditAmount: 0,
        description: "AR - sales with tax",
      });
    }

    return lines;
  }

  private async buildExpenseLines(calc: TaxCalculationResult, req: TaxGlPostingRequest): Promise<CreateJournalLineDTO[]> {
    const lines = await this.buildPurchaseLines(calc, req);
    return lines;
  }

  private async buildCitLines(calc: TaxCalculationResult, req: TaxGlPostingRequest): Promise<CreateJournalLineDTO[]> {
    const expenseAccount = req.primaryAccountId ?? "821";
    const expense = await this.accountRepo.findById(new AccountId(expenseAccount));
    if (!expense) throw new DomainError("NotFound", `CIT expense account ${expenseAccount} not found`);

    const totalTax = calc.totalTaxAmount;

    let payableAccountId = req.counterpartyAccountId ?? "";
    if (!payableAccountId) {
      const payable = await this.accountRepo.findById(new AccountId("3334"));
      if (!payable) throw new DomainError("NotFound", "CIT payable account 3334 not found");
      payableAccountId = payable.id.value;
    }

    return [
      {
        accountId: expenseAccount,
        debitAmount: totalTax,
        creditAmount: 0,
        description: "CIT expense",
      },
      {
        accountId: payableAccountId,
        debitAmount: 0,
        creditAmount: totalTax,
        description: "CIT payable",
      },
    ];
  }

  async generateLinesOnly(calc: TaxCalculationResult, transactionType: TaxPostingTransactionType, context: {
    primaryAccountId?: string;
    counterpartyAccountId?: string;
    taxCodeOverrides?: Record<string, { glExpenseAccountId?: string; glRecoverableAccountId?: string; glTaxAccountId?: string }>;
  }): Promise<CreateJournalLineDTO[]> {
    return this.buildJournalLines({
      calculationResult: calc,
      transactionType,
      transactionDate: new Date().toISOString(),
      postingDate: new Date().toISOString(),
      description: "Preview only",
      periodId: "",
      fiscalYearId: "",
      createdById: "system",
      primaryAccountId: context.primaryAccountId,
      counterpartyAccountId: context.counterpartyAccountId,
    });
  }
}
