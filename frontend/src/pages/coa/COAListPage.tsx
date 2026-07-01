import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { coaApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, Select, StatusBadge, FilterBar, FilterSelect } from '@/components/ui'
import { AccountPicker } from '@/components/ui/AccountPicker'
import { Card } from '@/components/ui/Card'
import { VNDisplay } from '@/components/ui'
import toast from 'react-hot-toast'
import type { Account, AccountType, DCRDirection } from '@/types/domain'
import { ACCOUNT_TYPE_MAP } from '@/utils/constants'
import { getErrorMessage } from '@/api/client'

const accountTypeOptions = Object.entries(ACCOUNT_TYPE_MAP).map(([value, label]) => ({ value, label }))
const statusOptions = [
  { value: 'active', label: 'Đang sử dụng' },
  { value: 'inactive', label: 'Ngừng sử dụng' },
  { value: 'frozen', label: 'Đóng băng' },
]

export default function COAListPage() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editAccount, setEditAccount] = useState<Account | null>(null)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['coa', typeFilter, statusFilter],
    queryFn: () => coaApi.list({ account_type: typeFilter || undefined, status: statusFilter || undefined }),
  })

  const accounts = data?.accounts || []

  const filtered = accounts.filter((a) =>
    !search || a.code.includes(search) || a.name.toLowerCase().includes(search.toLowerCase())
  )

  const createMutation = useMutation({
    mutationFn: (d: Partial<Account>) => editAccount ? coaApi.update(editAccount.code, d) : coaApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['coa'] }); setShowForm(false); setEditAccount(null); toast.success(editAccount ? 'Đã cập nhật tài khoản' : 'Đã tạo tài khoản') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  return (
    <div>
      <PageHeader
        title="Hệ thống tài khoản kế toán"
        subtitle="Danh mục tài khoản theo TT 99/2025"
        onAdd={{ label: 'Thêm tài khoản', onClick: () => { setEditAccount(null); setShowForm(true) } }}
      />

      <FilterBar>
        <FilterSelect value={typeFilter} onChange={setTypeFilter} label="Loại TK" options={accountTypeOptions} />
        <FilterSelect value={statusFilter} onChange={setStatusFilter} label="Trạng thái" options={statusOptions} />
      </FilterBar>

      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'code', label: 'Số hiệu', width: '100px', render: (r: Account) => <span className="font-mono text-primary-600 font-medium">{r.code}</span> },
            { key: 'name', label: 'Tên tài khoản' },
            { key: 'account_type', label: 'Loại', width: '120px', render: (r: Account) => <span className="text-xs">{ACCOUNT_TYPE_MAP[r.account_type] || r.account_type}</span> },
            { key: 'drcr_direction', label: 'Hướng', width: '80px', render: (r: Account) => <span className="text-xs font-mono">{r.drcr_direction === 'debit' ? 'Nợ' : 'Có'}</span> },
            { key: 'level', label: 'Cấp', width: '60px', align: 'center' },
            { key: 'status', label: 'Trạng thái', width: '110px', render: (r: Account) => <StatusBadge status={r.status} /> },
          ]}
          data={filtered}
          keyExtractor={(r) => r.code}
          loading={isLoading}
          onRowClick={(r) => { setEditAccount(r); setShowForm(true) }}
        />
      </div>

      <Modal
        open={showForm}
        onClose={() => { setShowForm(false); setEditAccount(null) }}
        title={editAccount ? 'Sửa tài khoản' : 'Thêm tài khoản mới'}
        size="lg"
      >
        <AccountForm
          account={editAccount}
          onSubmit={(data) => createMutation.mutate(data)}
          loading={createMutation.isPending}
        />
      </Modal>
    </div>
  )
}

function AccountForm({ account, onSubmit, loading }: { account: Account | null; onSubmit: (d: Partial<Account>) => void; loading: boolean }) {
  const [code, setCode] = useState(account?.code || '')
  const [name, setName] = useState(account?.name || '')
  const [accountType, setAccountType] = useState<string>(account?.account_type || 'ASSET')
  const [direction, setDirection] = useState<string>(account?.drcr_direction || 'debit')
  const [parentCode, setParentCode] = useState(account?.parent_code || '')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!code || !name) { toast.error('Vui lòng nhập số hiệu và tên tài khoản'); return }
    onSubmit({ code, name, account_type: accountType as AccountType, drcr_direction: direction as DCRDirection, parent_code: parentCode || undefined })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="Số hiệu tài khoản" value={code} onChange={(e) => setCode(e.target.value)} required placeholder="VD: 1111" />
        <Select label="Loại tài khoản" value={accountType} onChange={(e) => setAccountType(e.target.value)} options={accountTypeOptions} />
      </div>
      <Input label="Tên tài khoản" value={name} onChange={(e) => setName(e.target.value)} required />
      <div className="grid grid-cols-2 gap-4">
        <Select label="Hướng DCR" value={direction} onChange={(e) => setDirection(e.target.value)} options={[{ value: 'debit', label: 'Nợ (Dư Nợ)' }, { value: 'credit', label: 'Có (Dư Có)' }]} />
        <Input label="Tài khoản cha" value={parentCode} onChange={(e) => setParentCode(e.target.value)} placeholder="Để trống nếu là cấp 1" />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="secondary" onClick={() => {}}>Hủy</Button>
        <Button type="submit" loading={loading}>{account ? 'Cập nhật' : 'Tạo mới'}</Button>
      </div>
    </form>
  )
}
