export interface CashCountReport {
  denomination: string | null;
  quantity: number;
  unitValue: number;
  totalValue: number;
}

export interface ReceiptSummary {
  receiptCount: number;
  totalAmount: number;
  currencyCode: string;
}

export interface PaymentSummary {
  paymentCount: number;
  totalAmount: number;
  currencyCode: string;
}

export interface BankBalance {
  accountId: string;
  currentBalance: number;
  availableBalance: number;
  blockedBalance: number;
  currencyCode: string;
}

export interface CashPositionSummary {
  cashBoxId: string;
  cashBoxCode: string;
  currentBalance: number;
  currencyCode: string;
  asOfDate: Date;
}

export interface BankReconciliationSummary {
  statementBalance: number;
  bookBalance: number;
  difference: number;
  matchedCount: number;
  unmatchedCount: number;
  outstandingItems: number;
}
