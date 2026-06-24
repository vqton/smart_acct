import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { PayrollRunState, PayrollLineState } from "../../domain/prl/index.js";

export interface PayrollJournalEntry {
  description: string;
  journalDate: Date;
  currencyCode: string;
  lines: PayrollJournalLine[];
}

export interface PayrollJournalLine {
  lineNumber: number;
  accountCode: string;
  accountName: string;
  debitAmount: bigint;
  creditAmount: bigint;
  description: string;
  costCenterId?: string;
  departmentId?: string;
  branchId?: string;
  employeeId?: string;
  lineType: string;
}

/**
 * Generates GL journal entries from a posted/completed payroll run.
 *
 * Vietnamese accounting standards (Thông tư 200/2014/TT-BTC):
 * - Nợ TK 642 (hoặc 622, 627, 641 tùy bộ phận): Tổng lương + BHXH/BHYT/BHTN người SDLĐ
 * - Có TK 334: Lương thực lĩnh (net pay)
 * - Có TK 3382: Kinh phí công đoàn
 * - Có TK 3383: BHXH (phần người SDLĐ)
 * - Có TK 3384: BHYT (phần người SDLĐ)
 * - Có TK 3386: BHTN (phần người SDLĐ)
 * - Có TK 3335: Thuế TNCN (PIT)
 */
@Injectable()
export class PayrollGLPostingService {
  private readonly DEFAULT_ACCOUNTS = {
    salaryExpense: "6421",
    salaryPayable: "334",
    siPayable: "3383",
    hiPayable: "3384",
    uiPayable: "3386",
    unionPayable: "3382",
    pitPayable: "3335",
    insuranceExpense: "6421",
  };

  generatePosting(run: PayrollRunState, accountMapping?: Partial<typeof this.DEFAULT_ACCOUNTS>): PayrollJournalEntry {
    const accts = { ...this.DEFAULT_ACCOUNTS, ...accountMapping };

    const journalLines: PayrollJournalLine[] = [];
    let lineNo = 0;

    for (const line of run.lines) {
      if (line.isExcluded) continue;

      const dept = line.departmentId;
      const cc = line.costCenterId;
      const branch = line.branchId;
      const empId = line.employeeId;

      lineNo++;
      journalLines.push({
        lineNumber: lineNo,
        accountCode: accts.salaryExpense,
        accountName: "Chi phí lương",
        debitAmount: line.grossPay + line.employerCost,
        creditAmount: 0n,
        description: `Lương ${line.employeeCode} - ${line.employeeName}`,
        costCenterId: cc ?? undefined,
        departmentId: dept ?? undefined,
        branchId: branch ?? undefined,
        employeeId: empId,
        lineType: "salary_expense",
      });

      lineNo++;
      journalLines.push({
        lineNumber: lineNo,
        accountCode: accts.salaryPayable,
        accountName: "Phải trả người lao động",
        debitAmount: 0n,
        creditAmount: line.netPay,
        description: `Lương thực lĩnh ${line.employeeCode}`,
        costCenterId: cc ?? undefined,
        departmentId: dept ?? undefined,
        employeeId: empId,
        lineType: "net_pay",
      });

      lineNo++;
      journalLines.push({
        lineNumber: lineNo,
        accountCode: accts.pitPayable,
        accountName: "Thuế TNCN phải nộp",
        debitAmount: 0n,
        creditAmount: line.totalPIT,
        description: `Thuế TNCN ${line.employeeCode}`,
        employeeId: empId,
        lineType: "pit_payable",
      });

      if (line.totalInsurance > 0n) {
        lineNo++;
        journalLines.push({
          lineNumber: lineNo,
          accountCode: accts.siPayable,
          accountName: "BHXH phải nộp",
          debitAmount: 0n,
          creditAmount: line.totalInsurance,
          description: `BHXH/BHYT/BHTN ${line.employeeCode}`,
          employeeId: empId,
          lineType: "insurance_payable",
        });
      }

      if (line.employerCost > 0n) {
        lineNo++;
        journalLines.push({
          lineNumber: lineNo,
          accountCode: accts.siPayable,
          accountName: "BHXH phải nộp (phần SDLĐ)",
          debitAmount: 0n,
          creditAmount: line.employerCost,
          description: `BHXH/BHYT/BHTN người SDLĐ ${line.employeeCode}`,
          employeeId: empId,
          lineType: "employer_insurance",
        });
      }
    }

    const totalDebit = journalLines.reduce((s, l) => s + l.debitAmount, 0n);
    const totalCredit = journalLines.reduce((s, l) => s + l.creditAmount, 0n);

    return {
      description: `Bút toán lương ${run.name} - ${run.runNumber}`,
      journalDate: run.postedDate ?? new Date(),
      currencyCode: run.currencyCode,
      lines: journalLines,
    };
  }
}
