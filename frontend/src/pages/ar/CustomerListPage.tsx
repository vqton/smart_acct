import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { arApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, Select, StatusBadge, VNDisplay, FilterBar, FilterSelect } from '@/components/ui'
import toast from 'react-hot-toast'
import type { Customer } from '@/types/domain'
import { getErrorMessage } from '@/api/client'

const statusOptions = [
  { value: 'active', label: 'Hoạt động' },
  { value: 'inactive', label: 'Ngừng' },
  { value: 'blocked', label: 'Khóa' },
]

export default function CustomerListPage() {
  const [showForm, setShowForm] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['customers', statusFilter],
    queryFn: () => arApi.listCustomers({ status: statusFilter || undefined }),
  })

  const customers = data?.customers || []

  const createMutation = useMutation({
    mutationFn: (d: Partial<Customer>) => arApi.createCustomer(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['customers'] }); setShowForm(false); toast.success('Đã thêm khách hàng') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  return (
    <div>
      <PageHeader
        title="Khách hàng"
        subtitle="Danh sách khách hàng"
        onAdd={{ label: 'Thêm KH', onClick: () => setShowForm(true) }}
      />
      <FilterBar>
        <FilterSelect value={statusFilter} onChange={setStatusFilter} label="Trạng thái" options={statusOptions} />
      </FilterBar>
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'code', label: 'Mã KH', width: '100px', render: (r: Customer) => <span className="font-mono text-primary-600">{r.code}</span> },
            { key: 'name', label: 'Tên khách hàng' },
            { key: 'tax_code', label: 'MST', width: '110px', render: (r: Customer) => <span className="font-mono text-xs">{r.tax_code || '—'}</span> },
            { key: 'phone', label: 'Điện thoại', width: '120px' },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: Customer) => <StatusBadge status={r.status} /> },
          ]}
          data={customers}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Thêm khách hàng" size="lg">
        <CustomerForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>
    </div>
  )
}

function CustomerForm({ onSubmit, loading }: { onSubmit: (d: Partial<Customer>) => void; loading: boolean }) {
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [taxCode, setTaxCode] = useState('')
  const [phone, setPhone] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!code || !name) { toast.error('Nhập mã và tên khách hàng'); return }
    onSubmit({ code, name, tax_code: taxCode || null, phone: phone || null, customer_type: 'DOMESTIC', status: 'active' })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="Mã khách hàng" value={code} onChange={(e) => setCode(e.target.value)} required />
        <Input label="Mã số thuế" value={taxCode} onChange={(e) => setTaxCode(e.target.value)} />
      </div>
      <Input label="Tên khách hàng" value={name} onChange={(e) => setName(e.target.value)} required />
      <div className="grid grid-cols-2 gap-4">
        <Input label="Số điện thoại" value={phone} onChange={(e) => setPhone(e.target.value)} />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" loading={loading}>Tạo mới</Button>
      </div>
    </form>
  )
}
