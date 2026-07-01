import { api } from './client'
import type { Account, JournalEntry, TrialBalanceRow, DashboardData, Period, Vendor, Customer, ARInvoice, APInvoice, CashReceipt, CashPayment } from '@/types/domain'

// ── Auth ──
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
}

// ── COA ──
export const coaApi = {
  list: (params?: { regime?: string; status?: string; account_type?: string }) =>
    api.get<{ accounts: Account[]; total: number }>('/coa/accounts', { params }).then(r => r.data),
  get: (code: string) => api.get<Account>(`/coa/accounts/${code}`).then(r => r.data),
  create: (data: Partial<Account>) => api.post<Account>('/coa/accounts', data).then(r => r.data),
  update: (code: string, data: Partial<Account>) => api.put<Account>(`/coa/accounts/${code}`, data).then(r => r.data),
  delete: (code: string) => api.delete(`/coa/accounts/${code}`).then(r => r.data),
}

// ── GL ──
export const glApi = {
  listEntries: (params?: { period?: string; journal_type?: string; page?: number; page_size?: number }) =>
    api.get<{ entries: JournalEntry[]; total: number }>('/gl/entries', { params }).then(r => r.data),
  getEntry: (id: number) => api.get<JournalEntry>(`/gl/entries/${id}`).then(r => r.data),
  createEntry: (data: Partial<JournalEntry>) => api.post<JournalEntry>('/gl/entries', data).then(r => r.data),
  updateEntry: (id: number, data: Partial<JournalEntry>) => api.put<JournalEntry>(`/gl/entries/${id}`, data).then(r => r.data),
  postEntry: (id: number) => api.post(`/gl/entries/${id}/post`).then(r => r.data),
  deleteEntry: (id: number) => api.delete(`/gl/entries/${id}`).then(r => r.data),
  trialBalance: (period: string) => api.get<{ rows: TrialBalanceRow[] }>('/gl/reports/trial-balance', { params: { period } }).then(r => r.data),
  periods: {
    list: () => api.get<{ periods: Period[] }>('/periods').then(r => r.data),
    current: () => api.get<Period>('/periods/current').then(r => r.data),
    close: (period: string) => api.post(`/periods/${period}/close`).then(r => r.data),
  },
}

// ── AP ──
export const apApi = {
  listVendors: (params?: { status?: string }) =>
    api.get<{ vendors: Vendor[]; total: number }>('/ap/vendors', { params }).then(r => r.data),
  createVendor: (data: Partial<Vendor>) => api.post<Vendor>('/ap/vendors', data).then(r => r.data),
  listInvoices: (params?: { status?: string; vendor_id?: number }) =>
    api.get<{ invoices: APInvoice[]; total: number }>('/ap/invoices', { params }).then(r => r.data),
  createInvoice: (data: Partial<APInvoice>) => api.post('/ap/invoices', data).then(r => r.data),
}

// ── AR ──
export const arApi = {
  listCustomers: (params?: { status?: string }) =>
    api.get<{ customers: Customer[]; total: number }>('/ar/customers', { params }).then(r => r.data),
  createCustomer: (data: Partial<Customer>) => api.post<Customer>('/ar/customers', data).then(r => r.data),
  listInvoices: (params?: { status?: string; customer_id?: number }) =>
    api.get<{ invoices: ARInvoice[]; total: number }>('/ar/invoices', { params }).then(r => r.data),
  createInvoice: (data: Partial<ARInvoice>) => api.post('/ar/invoices', data).then(r => r.data),
}

// ── Cash ──
export const cashApi = {
  listReceipts: (params?: { status?: string }) =>
    api.get<{ receipts: CashReceipt[]; total: number }>('/cash/receipts', { params }).then(r => r.data),
  listPayments: (params?: { status?: string }) =>
    api.get<{ payments: CashPayment[]; total: number }>('/cash/payments', { params }).then(r => r.data),
  listBankAccounts: () => api.get('/cash/bank-accounts').then(r => r.data),
}

// ── Dashboard ──
export const dashboardApi = {
  get: () => api.get<DashboardData>('/dashboard').then(r => r.data),
}

// ── Reports ──
export const reportsApi = {
  trialBalance: (period: string) => api.get('/reports/trial-balance', { params: { period } }).then(r => r.data),
  balanceSheet: (period: string, format?: string) => api.get('/reports/balance-sheet', { params: { period, format } }).then(r => r.data),
  incomeStatement: (period: string) => api.get('/reports/income-statement', { params: { period } }).then(r => r.data),
}
