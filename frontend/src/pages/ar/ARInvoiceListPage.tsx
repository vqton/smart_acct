import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { arApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, StatusBadge, VNDisplay } from '@/components/ui'
import toast from 'react-hot-toast'
import type { ARInvoice } from '@/types/domain'
import { fmtDate } from '@/utils/formatters'
import { getErrorMessage } from '@/api'

export default function ARInvoiceListPage() {
  const [showForm, setShowForm] = useState(false)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['ar-invoices'],
    queryFn: () => arApi.listInvoices(),
  })

  const invoices = data?.invoices || []

  return (
    <div>
      <PageHeader
        title="Hóa đơn bán hàng"
        subtitle="Công nợ phải thu khách hàng"
        onAdd={{ label: 'Thêm HĐ', onClick: () => setShowForm(true) }}
      />
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Số HĐ', width: '120px', render: (r: ARInvoice) => <span className="font-mono text-primary-600">{r.invoice_number}</span> },
            { key: 'invoice_date', label: 'Ngày', width: '90px', render: (r: ARInvoice) => fmtDate(r.invoice_date) },
            { key: 'customer_name', label: 'Khách hàng' },
            { key: 'grand_total', label: 'Tổng tiền', align: 'right', width: '130px', render: (r: ARInvoice) => <VNDisplay amount={r.grand_total} /> },
            { key: 'due_date', label: 'Hạn TT', width: '90px', render: (r: ARInvoice) => fmtDate(r.due_date) },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: ARInvoice) => <StatusBadge status={r.status} /> },
          ]}
          data={invoices}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>
    </div>
  )
}
