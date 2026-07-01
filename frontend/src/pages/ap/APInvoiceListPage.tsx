import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { apApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, Select, StatusBadge, VNDisplay } from '@/components/ui'
import toast from 'react-hot-toast'
import type { APInvoice } from '@/types/domain'
import { fmtDate } from '@/utils/formatters'
import { getErrorMessage } from '@/api/client'

export default function APInvoiceListPage() {
  const [showForm, setShowForm] = useState(false)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['ap-invoices'],
    queryFn: () => apApi.listInvoices(),
  })

  const invoices = data?.invoices || []

  const createMutation = useMutation({
    mutationFn: (d: Partial<APInvoice>) => apApi.createInvoice(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['ap-invoices'] }); setShowForm(false); toast.success('Đã thêm hóa đơn') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  return (
    <div>
      <PageHeader
        title="Hóa đơn mua hàng"
        subtitle="Công nợ phải trả nhà cung cấp"
        onAdd={{ label: 'Thêm hóa đơn', onClick: () => setShowForm(true) }}
      />
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Số HĐ', width: '120px', render: (r: APInvoice) => <span className="font-mono text-primary-600">{r.invoice_number}</span> },
            { key: 'invoice_date', label: 'Ngày', width: '90px', render: (r: APInvoice) => fmtDate(r.invoice_date) },
            { key: 'vendor_name', label: 'Nhà cung cấp' },
            { key: 'grand_total', label: 'Tổng tiền', align: 'right', width: '130px', render: (r: APInvoice) => <VNDisplay amount={r.grand_total} /> },
            { key: 'due_date', label: 'Hạn TT', width: '90px', render: (r: APInvoice) => fmtDate(r.due_date) },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: APInvoice) => <StatusBadge status={r.status} /> },
          ]}
          data={invoices}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Thêm hóa đơn mua hàng" size="lg">
        <APInvoiceForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>
    </div>
  )
}

function APInvoiceForm({ onSubmit, loading }: { onSubmit: (d: Partial<APInvoice>) => void; loading: boolean }) {
  const [invNum, setInvNum] = useState('')
  const [vendorName, setVendorName] = useState('')
  const [total, setTotal] = useState('')
  const [vat, setVat] = useState('')
  const [dueDate, setDueDate] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!invNum || !vendorName || !total) { toast.error('Nhập đầy đủ thông tin'); return }
    onSubmit({
      invoice_number: invNum, vendor_name: vendorName, vendor_id: 0,
      total_amount: total, vat_amount: vat || '0', grand_total: String(parseFloat(total) + parseFloat(vat || '0')),
      due_date: dueDate, status: 'draft', invoice_type: 'PURCHASE',
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="Số hóa đơn" value={invNum} onChange={(e) => setInvNum(e.target.value)} required />
        <Input label="Ngày hóa đơn" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </div>
      <Input label="Nhà cung cấp" value={vendorName} onChange={(e) => setVendorName(e.target.value)} required />
      <div className="grid grid-cols-2 gap-4">
        <Input label="Tổng tiền" type="number" value={total} onChange={(e) => setTotal(e.target.value)} required />
        <Input label="Tiền VAT" type="number" value={vat} onChange={(e) => setVat(e.target.value)} />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" loading={loading}>Tạo mới</Button>
      </div>
    </form>
  )
}
