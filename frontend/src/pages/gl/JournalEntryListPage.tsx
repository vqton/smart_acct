import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { glApi } from '@/api'
import { PageHeader, DataTable, Button, Modal, Input, Select, StatusBadge, VNDisplay, FilterBar, FilterSelect } from '@/components/ui'
import { Card } from '@/components/ui/Card'
import toast from 'react-hot-toast'
import type { JournalEntry, JournalLine } from '@/types/domain'
import { fmtDate, fmtDateTime } from '@/utils/formatters'
import { getErrorMessage } from '@/api/client'
import { fmtVND } from '@/utils/formatters'

const journalTypeOptions = [
  { value: 'GENERAL', label: 'Nhật ký chung' },
  { value: 'CASH_RECEIPT', label: 'Thu tiền' },
  { value: 'CASH_PAYMENT', label: 'Chi tiền' },
  { value: 'SALES', label: 'Bán hàng' },
  { value: 'PURCHASE', label: 'Mua hàng' },
  { value: 'PAYROLL', label: 'Tiền lương' },
]

export default function JournalEntryListPage() {
  const [showForm, setShowForm] = useState(false)
  const [periodFilter, setPeriodFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['gl-entries', periodFilter, typeFilter],
    queryFn: () => glApi.listEntries({ period: periodFilter || undefined, journal_type: typeFilter || undefined }),
  })

  const entries = data?.entries || []

  const postMutation = useMutation({
    mutationFn: (id: number) => glApi.postEntry(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['gl-entries'] }); toast.success('Đã ghi sổ') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  return (
    <div>
      <PageHeader
        title="Nhật ký chung"
        subtitle="Chứng từ ghi sổ kế toán"
        onAdd={{ label: 'Thêm chứng từ', onClick: () => setShowForm(true) }}
      />

      <FilterBar>
        <Input placeholder="Kỳ (VD: 202601)" value={periodFilter} onChange={(e) => setPeriodFilter(e.target.value)} className="w-32" />
        <FilterSelect value={typeFilter} onChange={setTypeFilter} label="Loại" options={journalTypeOptions} />
      </FilterBar>

      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'journal_number', label: 'Số CT', width: '130px', render: (r: JournalEntry) => <span className="font-mono text-primary-600">{r.journal_number}</span> },
            { key: 'transaction_date', label: 'Ngày', width: '100px', render: (r: JournalEntry) => fmtDate(r.transaction_date) },
            { key: 'description', label: 'Diễn giải' },
            { key: 'journal_type', label: 'Loại', width: '100px', render: (r: JournalEntry) => <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{r.journal_type}</span> },
            { key: 'is_posted', label: 'Trạng thái', width: '100px', render: (r: JournalEntry) => <StatusBadge status={r.is_posted ? 'posted' : 'draft'} /> },
            { key: 'created_at', label: 'Ngày tạo', width: '140px', render: (r: JournalEntry) => fmtDateTime(r.created_at) },
          ]}
          data={entries}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>

      <JournalEntryFormModal
        open={showForm}
        onClose={() => setShowForm(false)}
      />
    </div>
  )
}

function JournalEntryFormModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [description, setDescription] = useState('')
  const [journalType, setJournalType] = useState('GENERAL')
  const [lines, setLines] = useState<JournalLine[]>([
    { account_id: '', debit: '0', credit: '0', description: '', is_taxable: false, vat_rate: null, tax_code: null, line_type: null, entity_id: null, entity_name: null },
    { account_id: '', debit: '0', credit: '0', description: '', is_taxable: false, vat_rate: null, tax_code: null, line_type: null, entity_id: null, entity_name: null },
  ])
  const qc = useQueryClient()

  const createMutation = useMutation({
    mutationFn: () => glApi.createEntry({
      transaction_date: date,
      description,
      journal_type: journalType as any,
      lines: lines.filter((l) => l.account_id),
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['gl-entries'] }); onClose(); toast.success('Đã tạo chứng từ') },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const updateLine = (i: number, field: keyof JournalLine, value: string | boolean | null) => {
    setLines((prev) => {
      const next = [...prev]
      next[i] = { ...next[i], [field]: value }
      return next
    })
  }

  const addLine = () => {
    setLines((prev) => [...prev, { account_id: '', debit: '0', credit: '0', description: '', is_taxable: false, vat_rate: null, tax_code: null, line_type: null, entity_id: null, entity_name: null }])
  }

  const totalDebit = lines.reduce((s, l) => s + (parseFloat(l.debit) || 0), 0)
  const totalCredit = lines.reduce((s, l) => s + (parseFloat(l.credit) || 0), 0)
  const balanced = Math.abs(totalDebit - totalCredit) < 0.001

  return (
    <Modal open={open} onClose={onClose} title="Thêm chứng từ ghi sổ" size="xl"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Hủy</Button>
          <Button onClick={() => createMutation.mutate()} loading={createMutation.isPending} disabled={!balanced || !description}>
            Ghi sổ
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <Input label="Ngày" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          <Select label="Loại chứng từ" value={journalType} onChange={(e) => setJournalType(e.target.value)} options={journalTypeOptions} />
        </div>
        <Input label="Diễn giải" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Nội dung hạch toán" />

        <Card title="Định khoản" subtitle="Nhập các dòng Nợ/Có">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 text-xs font-medium text-gray-500">TK Nợ</th>
                  <th className="text-left py-2 px-2 text-xs font-medium text-gray-500">TK Có</th>
                  <th className="text-right py-2 px-2 text-xs font-medium text-gray-500">Số tiền</th>
                  <th className="text-left py-2 px-2 text-xs font-medium text-gray-500">Diễn giải</th>
                  <th className="w-10" />
                </tr>
              </thead>
              <tbody>
                {lines.map((line, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="py-1 px-1">
                      <input
                        className="w-20 border border-gray-200 rounded px-2 py-1 text-xs font-mono focus:border-primary-500 focus:outline-none"
                        placeholder="TK Nợ"
                        value={line.debit !== '0' ? line.account_id : ''}
                        onChange={(e) => {
                          updateLine(i, 'account_id', e.target.value)
                          if (e.target.value && line.credit === '0') updateLine(i, 'credit', '0')
                        }}
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        className="w-20 border border-gray-200 rounded px-2 py-1 text-xs font-mono focus:border-primary-500 focus:outline-none"
                        placeholder="TK Có"
                        value={line.credit !== '0' ? line.account_id : ''}
                        onChange={(e) => {
                          updateLine(i, 'account_id', e.target.value)
                          if (e.target.value && line.debit === '0') updateLine(i, 'debit', '0')
                        }}
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        className="w-28 border border-gray-200 rounded px-2 py-1 text-xs font-mono text-right focus:border-primary-500 focus:outline-none"
                        placeholder="0"
                        value={parseFloat(line.debit) > 0 ? line.debit : (parseFloat(line.credit) > 0 ? line.credit : '')}
                        onChange={(e) => {
                          const val = e.target.value
                          const isDebit = line.debit !== '0' || !line.account_id
                          // Simple: put on debit if no account, otherwise on current side
                          if (line.debit !== '0' || (!line.account_id && line.credit === '0')) {
                            updateLine(i, 'debit', val || '0')
                          } else {
                            updateLine(i, 'credit', val || '0')
                          }
                        }}
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:border-primary-500 focus:outline-none"
                        placeholder="Diễn giải"
                        value={line.description || ''}
                        onChange={(e) => updateLine(i, 'description', e.target.value)}
                      />
                    </td>
                    <td className="py-1 px-1">
                      {lines.length > 2 && (
                        <button onClick={() => setLines((prev) => prev.filter((_, j) => j !== i))} className="text-danger-400 hover:text-danger-600 text-xs">
                          ✕
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-3">
            <button onClick={addLine} className="text-xs text-primary-600 hover:text-primary-800 font-medium">
              + Thêm dòng
            </button>
            <div className="text-sm">
              <span className={`font-mono font-medium ${balanced ? 'text-success-500' : 'text-danger-500'}`}>
                Nợ: {fmtVND(totalDebit)} | Có: {fmtVND(totalCredit)}
                {!balanced && ' (Mất cân đối!)'}
              </span>
            </div>
          </div>
        </Card>
      </div>
    </Modal>
  )
}
