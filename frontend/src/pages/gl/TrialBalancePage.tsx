import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { glApi } from '@/api'
import { PageHeader, DataTable, Button, Input, VNDisplay } from '@/components/ui'
import { Card } from '@/components/ui/Card'
import type { TrialBalanceRow } from '@/types/domain'

export default function TrialBalancePage() {
  const [period, setPeriod] = useState('')
  const [queryPeriod, setQueryPeriod] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['trial-balance', queryPeriod],
    queryFn: () => glApi.trialBalance(queryPeriod),
    enabled: !!queryPeriod,
  })

  const rows = data?.rows || []

  const totalOD = rows.reduce((s, r) => s + parseFloat(r.opening_debit || '0'), 0)
  const totalOC = rows.reduce((s, r) => s + parseFloat(r.opening_credit || '0'), 0)
  const totalPD = rows.reduce((s, r) => s + parseFloat(r.period_debit || '0'), 0)
  const totalPC = rows.reduce((s, r) => s + parseFloat(r.period_credit || '0'), 0)
  const totalCD = rows.reduce((s, r) => s + parseFloat(r.closing_debit || '0'), 0)
  const totalCC = rows.reduce((s, r) => s + parseFloat(r.closing_credit || '0'), 0)

  return (
    <div>
      <PageHeader title="Bảng cân đối số phát sinh" subtitle="Bảng CĐSPS theo kỳ" />

      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Input
            placeholder="Kỳ (VD: 202601)"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="w-40"
          />
          <Button onClick={() => setQueryPeriod(period)} disabled={!period}>
            Xem
          </Button>
        </div>

        <DataTable
          columns={[
            { key: 'account_code', label: 'TK', width: '90px', render: (r: TrialBalanceRow) => <span className="font-mono text-primary-600">{r.account_code}</span> },
            { key: 'account_name', label: 'Tên tài khoản' },
            { key: 'opening_debit', label: 'SD ĐK Nợ', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.opening_debit} /> },
            { key: 'opening_credit', label: 'SD ĐK Có', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.opening_credit} /> },
            { key: 'period_debit', label: 'PS Nợ', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.period_debit} /> },
            { key: 'period_credit', label: 'PS Có', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.period_credit} /> },
            { key: 'closing_debit', label: 'SD CK Nợ', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.closing_debit} /> },
            { key: 'closing_credit', label: 'SD CK Có', align: 'right', width: '130px', render: (r: TrialBalanceRow) => <VNDisplay amount={r.closing_credit} /> },
          ]}
          data={rows}
          keyExtractor={(r) => r.account_code}
          loading={isLoading}
          emptyMessage={queryPeriod ? 'Không có dữ liệu cho kỳ này' : 'Nhập kỳ và nhấn Xem'}
        />

        {rows.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div className="text-right">
                <span className="text-gray-500">Tổng SD ĐK: </span>
                <span className="font-mono font-medium"><VNDisplay amount={totalOD} /> / <VNDisplay amount={totalOC} /></span>
              </div>
              <div className="text-right">
                <span className="text-gray-500">Tổng PS: </span>
                <span className="font-mono font-medium"><VNDisplay amount={totalPD} /> / <VNDisplay amount={totalPC} /></span>
              </div>
              <div className="text-right">
                <span className="text-gray-500">Tổng SD CK: </span>
                <span className="font-mono font-medium"><VNDisplay amount={totalCD} /> / <VNDisplay amount={totalCC} /></span>
              </div>
              <div className={`text-right font-medium ${Math.abs(totalOD - totalOC) < 0.01 && Math.abs(totalCD - totalCC) < 0.01 ? 'text-success-500' : 'text-danger-500'}`}>
                {Math.abs(totalOD - totalOC) < 0.01 && Math.abs(totalCD - totalCC) < 0.01 ? '✓ Cân đối' : '✗ Mất cân đối'}
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
