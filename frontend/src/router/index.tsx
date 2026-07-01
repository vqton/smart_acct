import { createBrowserRouter, Navigate } from 'react-router-dom'
import { MainLayout } from '@/components/layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import COAListPage from '@/pages/coa/COAListPage'
import JournalEntryListPage from '@/pages/gl/JournalEntryListPage'
import TrialBalancePage from '@/pages/gl/TrialBalancePage'
import VendorListPage from '@/pages/ap/VendorListPage'
import APInvoiceListPage from '@/pages/ap/APInvoiceListPage'
import CustomerListPage from '@/pages/ar/CustomerListPage'
import ARInvoiceListPage from '@/pages/ar/ARInvoiceListPage'
import CashReceiptListPage from '@/pages/cash/CashReceiptListPage'
import CashPaymentListPage from '@/pages/cash/CashPaymentListPage'
import GenericListPage from '@/pages/GenericListPage'
import PagePlaceholder from '@/pages/PagePlaceholder'

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },

      // COA
      { path: 'coa', element: <COAListPage /> },

      // GL
      { path: 'gl/journal', element: <JournalEntryListPage /> },
      { path: 'gl/ledger', element: <GenericListPage title="Sổ cái" module="GL" /> },
      { path: 'gl/trial-balance', element: <TrialBalancePage /> },

      // AR
      { path: 'ar/customers', element: <CustomerListPage /> },
      { path: 'ar/invoices', element: <ARInvoiceListPage /> },
      { path: 'ar/aging', element: <GenericListPage title="Báo cáo công nợ phải thu" module="AR" /> },

      // AP
      { path: 'ap/vendors', element: <VendorListPage /> },
      { path: 'ap/invoices', element: <APInvoiceListPage /> },
      { path: 'ap/aging', element: <GenericListPage title="Báo cáo công nợ phải trả" module="AP" /> },

      // Cash
      { path: 'cash/receipts', element: <CashReceiptListPage /> },
      { path: 'cash/payments', element: <CashPaymentListPage /> },
      { path: 'cash/bank', element: <GenericListPage title="Ngân hàng" module="CASH" /> },
      { path: 'cash/petty', element: <GenericListPage title="Quỹ tạm ứng" module="CASH" /> },

      // Other modules
      { path: 'tax/vat', element: <GenericListPage title="Khai thuế GTGT" module="TAX" /> },
      { path: 'tax/einvoice', element: <GenericListPage title="Hóa đơn điện tử" module="TAX" /> },
      { path: 'fa/assets', element: <GenericListPage title="Danh mục TSCĐ" module="FA" /> },
      { path: 'fa/depreciation', element: <GenericListPage title="Khấu hao TSCĐ" module="FA" /> },
      { path: 'inv/items', element: <GenericListPage title="Danh mục vật tư" module="INVENTORY" /> },
      { path: 'inv/receipts', element: <GenericListPage title="Nhập kho" module="INVENTORY" /> },
      { path: 'inv/issues', element: <GenericListPage title="Xuất kho" module="INVENTORY" /> },
      { path: 'payroll/employees', element: <GenericListPage title="Nhân viên" module="PAYROLL" /> },
      { path: 'payroll/runs', element: <GenericListPage title="Bảng lương" module="PAYROLL" /> },
      { path: 'costing', element: <GenericListPage title="Giá thành" module="COSTING" /> },
      { path: 'budget', element: <GenericListPage title="Ngân sách" module="BUDGET" /> },
      { path: 'treasury', element: <GenericListPage title="Khoản mục đầu tư" module="TREASURY" /> },
      { path: 'reports', element: <GenericListPage title="Báo cáo tài chính" module="REPORTS" /> },
      { path: 'ccdc', element: <GenericListPage title="Công cụ dụng cụ" module="CCDC" /> },
      { path: 'audit', element: <GenericListPage title="Kiểm toán" module="AUDIT" /> },

      // Period Management
      { path: 'periods', element: <GenericListPage title="Quản lý kỳ kế toán" module="GL" /> },
    ],
  },
])
