export enum BankGroupType {
  Domestic = "domestic",
  Foreign = "foreign",
  JointVenture = "joint_venture",
  Government = "government",
  Central = "central",
  Investment = "investment",
  Commercial = "commercial",
  Cooperative = "cooperative",
}

export enum CorrespondentType {
  Nostro = "nostro",
  Vostro = "vostro",
  Intermediary = "intermediary",
  Beneficiary = "beneficiary",
}

export enum BankAccountCategory {
  Current = "current",
  Savings = "savings",
  Deposit = "deposit",
  Loan = "loan",
  Treasury = "treasury",
  Investment = "investment",
  Escrow = "escrow",
  Suspense = "suspense",
  Payroll = "payroll",
  Tax = "tax",
  Intercompany = "intercompany",
  Virtual = "virtual",
  Corporate = "corporate",
  Margin = "margin",
  Collateral = "collateral",
  Trust = "trust",
}

export enum BankAccountStatus {
  Pending = "pending",
  Active = "active",
  Suspended = "suspended",
  Blocked = "blocked",
  Dormant = "dormant",
  Closed = "closed",
  Archived = "archived",
}

export enum SignatureRule {
  Single = "single",
  Dual = "dual",
  Triple = "triple",
  Threshold = "threshold",
  Collective = "collective",
}

export enum TransactionNature {
  Incoming = "incoming",
  Outgoing = "outgoing",
  Internal = "internal",
  Intercompany = "intercompany",
  External = "external",
}

export enum TransactionStatus {
  Draft = "draft",
  Pending = "pending",
  Submitted = "submitted",
  Authorized = "authorized",
  Approved = "approved",
  Executed = "executed",
  Sent = "sent",
  Completed = "completed",
  Failed = "failed",
  Reversed = "reversed",
  Cancelled = "cancelled",
  Returned = "returned",
  ChargedBack = "charged_back",
}

export enum TransactionMethod {
  Wire = "wire",
  Ach = "ach",
  Swift = "swift",
  Sepa = "sepa",
  Domestic = "domestic",
  InternalTransfer = "internal_transfer",
  Cheque = "cheque",
  Cash = "cash",
  Card = "card",
  DirectDebit = "direct_debit",
  DirectCredit = "direct_credit",
  StandingOrder = "standing_order",
  BulkPayment = "bulk_payment",
  EWallet = "e_wallet",
}

export enum PaymentPriority {
  Low = "low",
  Normal = "normal",
  High = "high",
  Urgent = "urgent",
  Emergency = "emergency",
}

export enum PaymentChannel {
  Branch = "branch",
  Internet = "internet",
  Mobile = "mobile",
  Api = "api",
  File = "file",
  Electronic = "electronic",
  Atm = "atm",
  Pos = "pos",
}

export enum ChargeBearer {
  Sender = "sender",
  Beneficiary = "beneficiary",
  Shared = "shared",
  AllCharges = "all_charges",
}

export enum SettlementMethod {
  Netting = "netting",
  Gross = "gross",
  RealTime = "real_time",
  Deferred = "deferred",
  Direct = "direct",
}

export enum StatementSource {
  Manual = "manual",
  Mt940 = "mt940",
  Mt942 = "mt942",
  Camt052 = "camt_052",
  Camt053 = "camt_053",
  Camt054 = "camt_054",
  Csv = "csv",
  Excel = "excel",
  Api = "api",
  Pdf = "pdf",
  Print = "print",
}

export enum ReconciliationMatchType {
  Auto = "auto",
  Manual = "manual",
  Rule = "rule",
  Tolerance = "tolerance",
  Partial = "partial",
  Split = "split",
  Merge = "merge",
}

export enum ReconciliationStatus {
  Open = "open",
  InProgress = "in_progress",
  Matched = "matched",
  DifferenceFound = "difference_found",
  Resolved = "resolved",
  Approved = "approved",
  Closed = "closed",
  Reversed = "reversed",
}

export enum PaymentBatchStatus {
  Draft = "draft",
  Validated = "validated",
  Authorized = "authorized",
  Approved = "approved",
  Released = "released",
  Processing = "processing",
  Completed = "completed",
  PartiallyCompleted = "partially_completed",
  Failed = "failed",
  Cancelled = "cancelled",
}

export enum ApprovalStatus {
  Pending = "pending",
  Approved = "approved",
  Rejected = "rejected",
  Returned = "returned",
  Escalated = "escalated",
  Delegated = "delegated",
}

export enum ApprovalMode {
  Sequential = "sequential",
  Parallel = "parallel",
  Any = "any",
}

export enum InterestCalculationMethod {
  Simple = "simple",
  Compound = "compound",
  Daily = "daily",
  Monthly = "monthly",
  Quarterly = "quarterly",
  Annual = "annual",
}

export enum InterestBasis {
  Actual360 = "actual_360",
  Actual365 = "actual_365",
  ActualActual = "actual_actual",
  Thirty360 = "thirty_360",
  ThirtyE360 = "thirty_e_360",
}

export enum FXRateType {
  Spot = "spot",
  Forward = "forward",
  Swap = "swap",
  Historical = "historical",
  Budget = "budget",
  Reference = "reference",
  Buy = "buy",
  Sell = "sell",
  Transfer = "transfer",
}

export enum GLPostingStatus {
  Pending = "pending",
  Posted = "posted",
  Failed = "failed",
  Reversed = "reversed",
}

export enum RecurringFrequency {
  Daily = "daily",
  Weekly = "weekly",
  BiWeekly = "bi_weekly",
  Monthly = "monthly",
  BiMonthly = "bi_monthly",
  Quarterly = "quarterly",
  SemiAnnual = "semi_annual",
  Annual = "annual",
}

export enum CashPositionStatus {
  Draft = "draft",
  Confirmed = "confirmed",
  Approved = "approved",
  Locked = "locked",
}

export enum AccountLimitType {
  Single = "single",
  Daily = "daily",
  Weekly = "weekly",
  Monthly = "monthly",
  PerTransaction = "per_transaction",
}

export enum BankChargeType {
  Transaction = "transaction",
  Monthly = "monthly",
  Annual = "annual",
  Maintenance = "maintenance",
  Overdraft = "overdraft",
  Wire = "wire",
  CurrencyConversion = "currency_conversion",
  Late = "late",
  EarlyRepayment = "early_repayment",
  Service = "service",
  Penalty = "penalty",
  Commission = "commission",
}
