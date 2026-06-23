export interface BalanceEntry {
  accountId: string;
  periodId: string;
  fiscalYearId: string;
  debitAmount: number;
  creditAmount: number;
  foreignDebitAmount: number;
  foreignCreditAmount: number;
  runningBalance: number;
  runningForeignBalance: number;
  entryDate: Date;
}

export interface PeriodBalance {
  accountId: string;
  periodId: string;
  fiscalYearId: string;
  openingBalance: number;
  openingForeignBalance: number;
  periodDebit: number;
  periodCredit: number;
  periodForeignDebit: number;
  periodForeignCredit: number;
  closingBalance: number;
  closingForeignBalance: number;
}

export interface YearBalance {
  accountId: string;
  fiscalYearId: string;
  openingBalance: number;
  openingForeignBalance: number;
  yearDebit: number;
  yearCredit: number;
  yearForeignDebit: number;
  yearForeignCredit: number;
  closingBalance: number;
  closingForeignBalance: number;
}

export interface BalanceRepository {
  savePeriodBalance(balance: PeriodBalance): Promise<void>;
  getPeriodBalance(accountId: string, periodId: string): Promise<PeriodBalance | null>;
  saveYearBalance(balance: YearBalance): Promise<void>;
  getYearBalance(accountId: string, fiscalYearId: string): Promise<YearBalance | null>;
  saveBalanceEntry(entry: BalanceEntry): Promise<void>;
  getBalanceEntries(accountId: string, periodId: string): Promise<BalanceEntry[]>;
}

export class BalanceEngine {
  constructor(private balanceRepo: BalanceRepository) {}

  async updatePeriodBalance(
    accountId: string,
    periodId: string,
    fiscalYearId: string,
    debitAmount: number,
    creditAmount: number,
    foreignDebit: number,
    foreignCredit: number,
    isDebitNature: boolean,
  ): Promise<PeriodBalance> {
    let balance = await this.balanceRepo.getPeriodBalance(accountId, periodId);
    if (!balance) {
      balance = {
        accountId, periodId, fiscalYearId,
        openingBalance: 0, openingForeignBalance: 0,
        periodDebit: 0, periodCredit: 0,
        periodForeignDebit: 0, periodForeignCredit: 0,
        closingBalance: 0, closingForeignBalance: 0,
      };
    }

    balance.periodDebit += debitAmount;
    balance.periodCredit += creditAmount;
    balance.periodForeignDebit += foreignDebit;
    balance.periodForeignCredit += foreignCredit;

    const netChange = isDebitNature ? debitAmount - creditAmount : creditAmount - debitAmount;
    const foreignNetChange = isDebitNature ? foreignDebit - foreignCredit : foreignCredit - foreignDebit;

    balance.closingBalance = balance.openingBalance + (isDebitNature
      ? balance.periodDebit - balance.periodCredit
      : balance.periodCredit - balance.periodDebit);
    balance.closingForeignBalance = balance.openingForeignBalance + (isDebitNature
      ? balance.periodForeignDebit - balance.periodForeignCredit
      : balance.periodForeignCredit - balance.periodForeignDebit);

    await this.balanceRepo.savePeriodBalance(balance);
    return balance;
  }

  async updateYearBalance(
    accountId: string,
    fiscalYearId: string,
    debitAmount: number,
    creditAmount: number,
    foreignDebit: number,
    foreignCredit: number,
    isDebitNature: boolean,
  ): Promise<YearBalance> {
    let balance = await this.balanceRepo.getYearBalance(accountId, fiscalYearId);
    if (!balance) {
      balance = {
        accountId, fiscalYearId,
        openingBalance: 0, openingForeignBalance: 0,
        yearDebit: 0, yearCredit: 0,
        yearForeignDebit: 0, yearForeignCredit: 0,
        closingBalance: 0, closingForeignBalance: 0,
      };
    }

    balance.yearDebit += debitAmount;
    balance.yearCredit += creditAmount;
    balance.yearForeignDebit += foreignDebit;
    balance.yearForeignCredit += foreignCredit;

    balance.closingBalance = balance.openingBalance + (isDebitNature
      ? balance.yearDebit - balance.yearCredit
      : balance.yearCredit - balance.yearDebit);
    balance.closingForeignBalance = balance.openingForeignBalance + (isDebitNature
      ? balance.yearForeignDebit - balance.yearForeignCredit
      : balance.yearForeignCredit - balance.yearForeignDebit);

    await this.balanceRepo.saveYearBalance(balance);
    return balance;
  }

  async recordBalanceEntry(
    accountId: string,
    periodId: string,
    fiscalYearId: string,
    debitAmount: number,
    creditAmount: number,
    foreignDebit: number,
    foreignCredit: number,
    runningBalance: number,
    runningForeignBalance: number,
    entryDate: Date,
  ): Promise<void> {
    const entry: BalanceEntry = {
      accountId, periodId, fiscalYearId,
      debitAmount, creditAmount,
      foreignDebitAmount: foreignDebit,
      foreignCreditAmount: foreignCredit,
      runningBalance, runningForeignBalance,
      entryDate,
    };
    await this.balanceRepo.saveBalanceEntry(entry);
  }

  async getTrialBalance(
    periodId: string,
    fiscalYearId: string,
  ): Promise<PeriodBalance[]> {
    return [];
  }
}
