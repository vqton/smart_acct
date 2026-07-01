import { useQuery } from '@tanstack/react-query'
import { cashApi } from '@/api'
import { PageHeader, DataTable, StatusBadge, VNDisplay } from '@/components/ui'
import { fmtDate } from '@/utils/formatters'
import type { CashPayment } from '@/types/domain'

export default function CashPaymentListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['cash-payments'],
    queryFn: () => cashApi.listPayments(),
  })

  const payments = data?.payments || []

  return (
    <div>
      <PageHeader title="Phiếu chi" subtitle="Chi tiền mặt" onAdd={{ label: 'Thêm PC', onClick: () => {} }} />
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'voucher_number', label: 'Số CT', width: '120px', render: (r: CashPayment) => <span className="font-mono text-primary-600">{r.voucher_number}</span> },
            { key: 'voucher_date', label: 'Ngày', width: '90px', render: (r: CashPayment) => fmtDate(r.voucher_date) },
            { key: 'payee_name', label: 'Người nhận' },
            { key: 'amount', label: 'Số tiền', align: 'right', width: '130px', render: (r: CashPayment) => <VNDisplay amount={r.amount} /> },
            { key: 'description', label: 'Nội dung' },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: CashPayment) => <StatusBadge status={r.status} /> },
          ]}
          data={payments}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>
    </div>
  )
}
