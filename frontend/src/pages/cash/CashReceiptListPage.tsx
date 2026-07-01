import { useQuery } from '@tanstack/react-query'
import { cashApi } from '@/api'
import { PageHeader, DataTable, StatusBadge, VNDisplay } from '@/components/ui'
import { fmtDate, fmtVND } from '@/utils/formatters'
import type { CashReceipt } from '@/types/domain'

export default function CashReceiptListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['cash-receipts'],
    queryFn: () => cashApi.listReceipts(),
  })

  const receipts = data?.receipts || []

  return (
    <div>
      <PageHeader title="Phiếu thu" subtitle="Thu tiền mặt" onAdd={{ label: 'Thêm PT', onClick: () => {} }} />
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'voucher_number', label: 'Số CT', width: '120px', render: (r: CashReceipt) => <span className="font-mono text-primary-600">{r.voucher_number}</span> },
            { key: 'voucher_date', label: 'Ngày', width: '90px', render: (r: CashReceipt) => fmtDate(r.voucher_date) },
            { key: 'payer_name', label: 'Người nộp' },
            { key: 'amount', label: 'Số tiền', align: 'right', width: '130px', render: (r: CashReceipt) => <VNDisplay amount={r.amount} /> },
            { key: 'description', label: 'Nội dung' },
            { key: 'status', label: 'Trạng thái', width: '100px', render: (r: CashReceipt) => <StatusBadge status={r.status} /> },
          ]}
          data={receipts}
          keyExtractor={(r) => r.id!}
          loading={isLoading}
        />
      </div>
    </div>
  )
}
