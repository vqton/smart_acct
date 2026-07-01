export const API_BASE = '/api/v1'

export const NAV_ITEMS = [
  {
    label: 'Tổng quan', labelEn: 'Dashboard', icon: '📊', path: '/dashboard',
  },
  {
    label: 'Hệ thống TK', labelEn: 'Chart of Accounts', icon: '📒', path: '/coa',
  },
  {
    label: 'Kế toán tổng hợp', labelEn: 'General Ledger', icon: '📔', path: '/gl',
    children: [
      { label: 'Nhật ký chung', labelEn: 'General Journal', icon: '', path: '/gl/journal' },
      { label: 'Sổ cái', labelEn: 'General Ledger', icon: '', path: '/gl/ledger' },
      { label: 'CĐ số phát sinh', labelEn: 'Trial Balance', icon: '', path: '/gl/trial-balance' },
    ],
  },
  {
    label: 'Công nợ phải thu', labelEn: 'Accounts Receivable', icon: '💰', path: '/ar',
    children: [
      { label: 'Khách hàng', labelEn: 'Customers', icon: '', path: '/ar/customers' },
      { label: 'Hóa đơn bán hàng', labelEn: 'Sales Invoices', icon: '', path: '/ar/invoices' },
      { label: 'Báo cáo công nợ', labelEn: 'Aging Report', icon: '', path: '/ar/aging' },
    ],
  },
  {
    label: 'Công nợ phải trả', labelEn: 'Accounts Payable', icon: '💳', path: '/ap',
    children: [
      { label: 'Nhà cung cấp', labelEn: 'Vendors', icon: '', path: '/ap/vendors' },
      { label: 'Hóa đơn mua hàng', labelEn: 'Purchase Invoices', icon: '', path: '/ap/invoices' },
      { label: 'Báo cáo công nợ', labelEn: 'Aging Report', icon: '', path: '/ap/aging' },
    ],
  },
  {
    label: 'Tiền mặt & Ngân hàng', labelEn: 'Cash & Bank', icon: '🏦', path: '/cash',
    children: [
      { label: 'Phiếu thu', labelEn: 'Cash Receipts', icon: '', path: '/cash/receipts' },
      { label: 'Phiếu chi', labelEn: 'Cash Payments', icon: '', path: '/cash/payments' },
      { label: 'Ngân hàng', labelEn: 'Bank', icon: '', path: '/cash/bank' },
      { label: 'Quỹ tạm ứng', labelEn: 'Petty Cash', icon: '', path: '/cash/petty' },
    ],
  },
  {
    label: 'Thuế', labelEn: 'Tax', icon: '🧾', path: '/tax',
    children: [
      { label: 'Khai thuế GTGT', labelEn: 'VAT Declaration', icon: '', path: '/tax/vat' },
      { label: 'Hóa đơn điện tử', labelEn: 'E-Invoice', icon: '', path: '/tax/einvoice' },
    ],
  },
  {
    label: 'Tài sản cố định', labelEn: 'Fixed Assets', icon: '🏭', path: '/fa',
    children: [
      { label: 'Danh mục TSCĐ', labelEn: 'Asset List', icon: '', path: '/fa/assets' },
      { label: 'Khấu hao', labelEn: 'Depreciation', icon: '', path: '/fa/depreciation' },
    ],
  },
  {
    label: 'Hàng tồn kho', labelEn: 'Inventory', icon: '📦', path: '/inventory',
    children: [
      { label: 'Danh mục vật tư', labelEn: 'Items', icon: '', path: '/inv/items' },
      { label: 'Nhập kho', labelEn: 'Receipts', icon: '', path: '/inv/receipts' },
      { label: 'Xuất kho', labelEn: 'Issues', icon: '', path: '/inv/issues' },
    ],
  },
  {
    label: 'Tiền lương', labelEn: 'Payroll', icon: '👥', path: '/payroll',
    children: [
      { label: 'Nhân viên', labelEn: 'Employees', icon: '', path: '/payroll/employees' },
      { label: 'Bảng lương', labelEn: 'Payroll', icon: '', path: '/payroll/runs' },
    ],
  },
  {
    label: 'Giá thành', labelEn: 'Costing', icon: '📐', path: '/costing',
  },
  {
    label: 'Ngân sách', labelEn: 'Budget', icon: '📋', path: '/budget',
  },
  {
    label: 'Khoản mục đầu tư', labelEn: 'Treasury', icon: '💹', path: '/treasury',
  },
  {
    label: 'Báo cáo tài chính', labelEn: 'Financial Reports', icon: '📑', path: '/reports',
  },
  {
    label: 'Công cụ dụng cụ', labelEn: 'Tools & Equipment', icon: '🔧', path: '/ccdc',
  },
  {
    label: 'Kiểm toán', labelEn: 'Audit', icon: '🔍', path: '/audit',
  },
]

export const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  draft:    { label: 'Nháp', color: 'text-gray-600', bg: 'bg-gray-100' },
  pending:  { label: 'Chờ duyệt', color: 'text-yellow-700', bg: 'bg-yellow-100' },
  approved: { label: 'Đã duyệt', color: 'text-blue-700', bg: 'bg-blue-100' },
  posted:   { label: 'Đã ghi sổ', color: 'text-green-700', bg: 'bg-green-100' },
  cancelled:{ label: 'Hủy', color: 'text-red-700', bg: 'bg-red-100' },
}

export const ACCOUNT_TYPE_MAP: Record<string, string> = {
  ASSET: 'Tài sản', LIABILITY: 'Nợ phải trả', EQUITY: 'Vốn chủ sở hữu',
  REVENUE: 'Doanh thu', EXPENSE: 'Chi phí', CASH: 'Tiền mặt', INVENTORY: 'Hàng tồn kho',
}
