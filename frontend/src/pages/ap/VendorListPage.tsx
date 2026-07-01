import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { apApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, Select, StatusBadge, VNDisplay, FilterBar, FilterSelect } from '@/components/ui'
import toast from 'react-hot-toast'
import type { Vendor } from '@/types/domain'
import { getErrorMessage } from '@/api'

const statusOptions = [
  { value: 'active', label: 'Hoạt động' },
  { value: 'inactive', label: 'Ngừng' },
  { value: 'blocked', label: 'Khóa' },
]

export default function VendorListPage() {
  const [showForm, setShowForm] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['vendors', statusFilter],
    queryFn: () => apApi.listVendors({ status: statusFilter || undefined }),
  })

  const vendors = data?.vendors || []

  const createMutation = useMutation({
    mutationFn: (d: Partial<Vendor>) => apApi.createVendor(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['vendors'] }); setShowForm(false); toast.success('Đã thêm nhà cung cấp') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  return (
    <div>
      <PageHeader
        title="Nhà cung cấp"
        subtitle="Danh sách nhà cung cấp"
        onAdd={{ label: 'Thêm NCC', onClick: () => setShowForm(true) }}
      />
      <FilterBar>
        <FilterSelect value={statusFilter} onChange={setStatusFilter} label="Trạng thái" options={statusOptions} />
      </FilterBar>
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'code', label: 'Mã NCC', width: '100px', render: (r: Vendor) => <span className="font-mono text-primary-600">{r.code}</span> },
            { key: 'name', label: 'Tên nhà cung cấp' },
            { key: 'tax_code', label: 'MST', width: '110px', render: (r: Vendor) => <span className="font-mono text-xs">{r.tax_code || '—'}</span> },
            { key: 'phone', label: 'Điện thoại', width: '120px' },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: Vendor) => <StatusBadge status={r.status} /> },
          ]}
          data={vendors}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Thêm nhà cung cấp" size="lg">
        <VendorForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>
    </div>
  )
}

function VendorForm({ onSubmit, loading }: { onSubmit: (d: Partial<Vendor>) => void; loading: boolean }) {
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [taxCode, setTaxCode] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!code || !name) { toast.error('Nhập mã và tên nhà cung cấp'); return }
    onSubmit({ code, name, tax_code: taxCode || null, phone: phone || null, address: address || null, vendor_type: 'DOMESTIC', status: 'active' })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="Mã nhà cung cấp" value={code} onChange={(e) => setCode(e.target.value)} required />
        <Input label="Mã số thuế" value={taxCode} onChange={(e) => setTaxCode(e.target.value)} />
      </div>
      <Input label="Tên nhà cung cấp" value={name} onChange={(e) => setName(e.target.value)} required />
      <div className="grid grid-cols-2 gap-4">
        <Input label="Số điện thoại" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <Input label="Địa chỉ" value={address} onChange={(e) => setAddress(e.target.value)} />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" loading={loading}>Tạo mới</Button>
      </div>
    </form>
  )
}
