// ── Enums ──
export type AccountType = 'ASSET' | 'LIABILITY' | 'EQUITY' | 'REVENUE' | 'EXPENSE' | 'CASH' | 'INVENTORY'
export type DCRDirection = 'debit' | 'credit'
export type AccountingRegime = 'tt99_2025' | 'tt133_2016' | 'tt200_2014'
export type AccountStatus = 'active' | 'inactive' | 'frozen'
export type JournalType = 'GENERAL' | 'SALES' | 'PURCHASE' | 'CASH_RECEIPT' | 'CASH_PAYMENT' | 'PAYROLL' | 'INVENTORY' | 'FIXED_ASSET' | 'ADJUSTMENT' | 'OPENING' | 'CLOSING'
export type DocumentStatus = 'draft' | 'pending' | 'approved' | 'posted' | 'cancelled'
export type PaymentMethod = 'CASH' | 'BANK_TRANSFER' | 'CHEQUE' | 'CREDIT_CARD' | 'OTHER'
export type SubsidiaryType = 'AR' | 'AP' | 'INVENTORY' | 'FA' | 'COST' | 'PREPAID' | 'LOAN'

// ── Core Entities ──
export interface Account {
  code: string
  name: string
  account_type: AccountType
  regime: AccountingRegime
  vas_compliant: boolean
  drcr_direction: DCRDirection
  level: number
  status: AccountStatus
  currency: string
  unit: string
  parent_code: string | null
  description: string | null
  created_at: string | null
  updated_at: string | null
}

export interface JournalLine {
  id?: number
  account_id: string
  debit: string
  credit: string
  description: string | null
  vat_rate: string | null
  line_type: string | null
  is_taxable: boolean
  tax_code: string | null
  entity_id: string | null
  entity_name: string | null
}

export interface JournalEntry {
  id?: number
  journal_number: string
  journal_type: JournalType
  transaction_date: string
  description: string
  period: string
  is_posted: boolean
  posted_date: string | null
  source_module: string | null
  created_by: string | null
  approved_by: string | null
  is_approved: boolean
  approval_date: string | null
  correction_method: string | null
  ref_journal_number: string | null
  created_at: string | null
  updated_at: string | null
  lines: JournalLine[]
}

export interface Vendor {
  id?: number
  code: string
  name: string
  tax_code: string | null
  address: string | null
  phone: string | null
  email: string | null
  vendor_type: string
  vendor_group: string | null
  status: string
  credit_limit: string | null
  payment_terms: string | null
  bank_account: string | null
  bank_name: string | null
  notes: string | null
}

export interface Customer {
  id?: number
  code: string
  name: string
  tax_code: string | null
  address: string | null
  phone: string | null
  email: string | null
  customer_type: string
  customer_group: string | null
  status: string
  credit_limit: string | null
  payment_terms: string | null
  notes: string | null
}

export interface ARInvoice {
  id?: number
  invoice_number: string
  invoice_date: string
  customer_id: number
  customer_name: string
  invoice_type: string
  status: string
  total_amount: string
  vat_amount: string
  grand_total: string
  paid_amount: string
  due_date: string
  notes: string | null
}

export interface APInvoice {
  id?: number
  invoice_number: string
  invoice_date: string
  vendor_id: number
  vendor_name: string
  invoice_type: string
  status: string
  total_amount: string
  vat_amount: string
  grand_total: string
  paid_amount: string
  due_date: string
  notes: string | null
}

// ── GL Reporting ──
export interface TrialBalanceRow {
  account_code: string
  account_name: string
  opening_debit: string
  opening_credit: string
  period_debit: string
  period_credit: string
  closing_debit: string
  closing_credit: string
}

export interface BalanceSheetRow {
  account_code: string
  account_name: string
  current_year: string
  prior_year: string | null
}

export interface IncomeStatementRow {
  account_code: string
  account_name: string
  current_period: string
  accumulated: string
}

export interface CashFlowRow {
  description: string
  amount: string
}

// ── Cash ──
export interface CashReceipt {
  id?: number
  voucher_number: string
  voucher_date: string
  receipt_type: string
  amount: string
  payer_name: string
  description: string
  status: string
}

export interface CashPayment {
  id?: number
  voucher_number: string
  voucher_date: string
  payment_type: string
  amount: string
  payee_name: string
  description: string
  status: string
}

// ── Dashboard ──
export interface DashboardData {
  cash_balance: string
  bank_balance: string
  ar_aging: { current: string; overdue_30: string; overdue_60: string; overdue_90: string }
  ap_aging: { current: string; overdue_30: string; overdue_60: string; overdue_90: string }
  revenue_current_month: string
  expense_current_month: string
  unposted_count: number
  pending_approval_count: number
  period_status: string
  revenue_trend: { month: string; revenue: string; expense: string }[]
  ar_ap_trend: { month: string; receivable: string; payable: string }[]
}

// ── Period ──
export interface Period {
  period: string
  start_date: string
  end_date: string
  is_closed: boolean
  is_current: boolean
  period_type: string
}

// ── Pagination ──
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ── API Response ──
export interface ApiError {
  error: string
}

export type ApiResult<T> = { success: true; data: T } | { success: false; error: string }
