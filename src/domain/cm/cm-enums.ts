export enum CashBoxType {
  CashRegister = "cash_register",
  CashDrawer = "cash_drawer",
  SafeDeposit = "safe_deposit",
  PettyCash = "petty_cash",
  Teller = "teller",
  Atm = "atm",
  PosTerminal = "pos_terminal",
  Vault = "vault",
  CashOffice = "cash_office",
  Other = "other",
}

export enum CashBoxStatus {
  Active = "active",
  Inactive = "inactive",
  Suspended = "suspended",
  Closed = "closed",
  Archived = "archived",
}

export enum CashSessionStatus {
  Pending = "pending",
  Open = "open",
  Counting = "counting",
  Closed = "closed",
  Reconciled = "reconciled",
  Disputed = "disputed",
}

export enum CashDirection {
  In = "in",
  Out = "out",
}

export enum CashDifferenceType {
  Shortage = "shortage",
  Overage = "overage",
  Counterfeit = "counterfeit",
  Dispute = "dispute",
  Adjustment = "adjustment",
}

export enum CashDifferenceStatus {
  Pending = "pending",
  Investigated = "investigated",
  Approved = "approved",
  Rejected = "rejected",
  Resolved = "resolved",
  WrittenOff = "written_off",
}

export enum ReceiptStatus {
  Draft = "draft",
  Issued = "issued",
  Approved = "approved",
  Posted = "posted",
  Cancelled = "cancelled",
  Reversed = "reversed",
}

export enum PaymentStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Paid = "paid",
  Posted = "posted",
  Cancelled = "cancelled",
  Rejected = "rejected",
  Reversed = "reversed",
}

export enum PaymentMethod {
  Cash = "cash",
  Cheque = "cheque",
  BankTransfer = "bank_transfer",
  WireTransfer = "wire_transfer",
  IntercompanyTransfer = "intercompany_transfer",
  Card = "card",
  EWallet = "e_wallet",
  Offset = "offset",
  Other = "other",
}

export enum ChequeType {
  Personal = "personal",
  Corporate = "corporate",
  Cashier = "cashier",
  Certified = "certified",
  Travellers = "travellers",
  Government = "government",
}

export enum ChequeStatus {
  Unissued = "unissued",
  Issued = "issued",
  Deposited = "deposited",
  Cleared = "cleared",
  Returned = "returned",
  Cancelled = "cancelled",
  Stopped = "stopped",
  Voided = "voided",
  Reconciled = "reconciled",
}

export enum BankAccountType {
  Current = "current",
  Savings = "savings",
  Deposit = "deposit",
  Loan = "loan",
  Treasury = "treasury",
  Suspense = "suspense",
  Payroll = "payroll",
  Tax = "tax",
  Intercompany = "intercompany",
  Virtual = "virtual",
}

export enum BankAccountStatus {
  Active = "active",
  Inactive = "inactive",
  Suspended = "suspended",
  Closed = "closed",
  Blocked = "blocked",
}

export enum BankTransferType {
  Internal = "internal",
  Intercompany = "intercompany",
  Domestic = "domestic",
  International = "international",
  Swift = "swift",
  Wire = "wire",
  Ach = "ach",
  Sepa = "sepa",
}

export enum BankTransferStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Sent = "sent",
  Completed = "completed",
  Failed = "failed",
  Reversed = "reversed",
  Cancelled = "cancelled",
}

export enum CashAdvanceStatus {
  Draft = "draft",
  Approved = "approved",
  Disbursed = "disbursed",
  Settled = "settled",
  PartiallySettled = "partially_settled",
  Overdue = "overdue",
  WrittenOff = "written_off",
  Cancelled = "cancelled",
}

export enum CashTransferStatus {
  Draft = "draft",
  Approved = "approved",
  InTransit = "in_transit",
  Completed = "completed",
  Cancelled = "cancelled",
  Disputed = "disputed",
}

export enum CashForecastStatus {
  Draft = "draft",
  Confirmed = "confirmed",
  Locked = "locked",
  Archived = "archived",
}

export enum PettyCashStatus {
  Active = "active",
  Suspended = "suspended",
  Replenishing = "replenishing",
  Closed = "closed",
  Audited = "audited",
}

export enum ChequeBookStatus {
  Active = "active",
  Used = "used",
  FullUsed = "full_used",
  Cancelled = "cancelled",
  Lost = "lost",
}

export enum BankReconciliationStatus {
  Open = "open",
  InProgress = "in_progress",
  Matched = "matched",
  DifferenceFound = "difference_found",
  Resolved = "resolved",
  Closed = "closed",
}

export enum StatementLineType {
  Debit = "debit",
  Credit = "credit",
  Fee = "fee",
  Interest = "interest",
  Chargeback = "chargeback",
  Reversal = "reversal",
  Other = "other",
}
