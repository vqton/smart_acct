import { AccountRepository } from "../../domain/gl/repositories.js";
import { TaxReturnRepository, TaxPaymentRepository } from "../../domain/tax/tax-repositories.js";
import { AccountId } from "../../domain/gl/account-id.js";

export interface TaxReconciliationEntry {
  accountCode: string;
  accountName: string;
  taxTypeCode: string;
  glBalance: number;
  declaredAmount: number;
  paidAmount: number;
  refundAmount: number;
  netDue: number;
  varianceGLvsDeclared: number;
  varianceDeclaredvsPaid: number;
}

export interface TaxReconciliationResult {
  periodId: string;
  fiscalYearId: string;
  reconciledAt: Date;
  entries: TaxReconciliationEntry[];
  summary: {
    totalGLBalance: number;
    totalDeclared: number;
    totalPaid: number;
    totalVarianceGLvsDeclared: number;
    totalVarianceDeclaredvsPaid: number;
  };
}

const TAX_ACCOUNT_MAP = [
  { accountCode: "3331", taxTypeCode: "VAT" },
  { accountCode: "1331", taxTypeCode: "VAT" },
  { accountCode: "3334", taxTypeCode: "CIT" },
  { accountCode: "3335", taxTypeCode: "PIT" },
];

export class TaxReconciliationService {
  constructor(
    private readonly accountRepo: AccountRepository,
    private readonly taxReturnRepo: TaxReturnRepository,
    private readonly taxPaymentRepo: TaxPaymentRepository,
  ) {}

  async reconcile(params: {
    periodId: string;
    fiscalYearId: string;
  }): Promise<TaxReconciliationResult> {
    const entries: TaxReconciliationEntry[] = [];
    let totalGLBalance = 0;
    let totalDeclared = 0;
    let totalPaid = 0;

    const returns = await this.taxReturnRepo.findByPeriod(params.periodId);

    for (const mapping of TAX_ACCOUNT_MAP) {
      const account = await this.accountRepo.findByCode(mapping.accountCode);
      if (!account) continue;

      const glBalance = account.balance.toNumber();
      const taxReturns = returns.filter(r => r.taxTypeId.includes(mapping.taxTypeCode) || r.toState().taxTypeId.includes(mapping.taxTypeCode));
      const declaredAmount = taxReturns.reduce((sum, tr) => {
        const s = tr.toState();
        return mapping.accountCode === "1331"
          ? sum + s.totalRecoverableAmount
          : mapping.accountCode === "3331"
            ? sum + s.totalTaxAmount
            : sum + s.netPayableAmount;
      }, 0);

      const payments = await this.taxPaymentRepo.findByTaxReturn(
        mapping.accountCode === "3331" || mapping.accountCode === "1331" ? "VAT" : mapping.taxTypeCode,
      );

      const matchingPayments = taxReturns.length > 0
        ? (await Promise.all(taxReturns.map(tr => this.taxPaymentRepo.findByTaxReturn(tr.id.value)))).flat()
        : [];

      const paidAmount = matchingPayments.reduce((sum, p) => {
        const s = p.toState();
        return s.status === "completed" || s.status === "partially_refunded" ? sum + s.amount : sum;
      }, 0);
      const refundAmount = matchingPayments.reduce((sum, p) => sum + p.refundAmount, 0);
      const netDue = paidAmount - refundAmount;

      totalGLBalance += glBalance;
      totalDeclared += declaredAmount;
      totalPaid += netDue;

      entries.push({
        accountCode: mapping.accountCode,
        accountName: account.name,
        taxTypeCode: mapping.taxTypeCode,
        glBalance,
        declaredAmount,
        paidAmount,
        refundAmount,
        netDue,
        varianceGLvsDeclared: glBalance - declaredAmount,
        varianceDeclaredvsPaid: declaredAmount - netDue,
      });
    }

    return {
      periodId: params.periodId,
      fiscalYearId: params.fiscalYearId,
      reconciledAt: new Date(),
      entries,
      summary: {
        totalGLBalance,
        totalDeclared,
        totalPaid,
        totalVarianceGLvsDeclared: totalGLBalance - totalDeclared,
        totalVarianceDeclaredvsPaid: totalDeclared - totalPaid,
      },
    };
  }
}
