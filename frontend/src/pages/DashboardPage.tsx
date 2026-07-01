import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api'
import { PageHeader } from '@/components/ui'
import { Card, StatCard } from '@/components/ui/Card'
import { VNDisplay } from '@/components/ui'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, Legend,
} from 'recharts'
import type { DashboardData } from '@/types/domain'

export default function DashboardPage() {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  })

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Tổng quan" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
              <div className="h-3 bg-gray-200 rounded w-24 mb-3" />
              <div className="h-7 bg-gray-200 rounded w-32 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader title="Tổng quan" subtitle="Bảng điều khiển tài chính" />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Tiền mặt"
          value={data ? new Intl.NumberFormat('vi-VN').format(parseFloat(data.cash_balance)) + ' đ' : '—'}
          icon="💰"
        />
        <StatCard
          label="Tiền gửi ngân hàng"
          value={data ? new Intl.NumberFormat('vi-VN').format(parseFloat(data.bank_balance)) + ' đ' : '—'}
          icon="🏦"
        />
        <StatCard
          label="Doanh thu tháng này"
          value={data ? new Intl.NumberFormat('vi-VN').format(parseFloat(data.revenue_current_month)) + ' đ' : '—'}
          icon="📈"
        />
        <StatCard
          label="Chi phí tháng này"
          value={data ? new Intl.NumberFormat('vi-VN').format(parseFloat(data.expense_current_month)) + ' đ' : '—'}
          icon="📉"
        />
        <StatCard
          label="CT chưa ghi sổ"
          value={data ? String(data.unposted_count) : '—'}
          icon="⏳"
        />
        <StatCard
          label="CT chờ duyệt"
          value={data ? String(data.pending_approval_count) : '—'}
          icon="📋"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Revenue Trend Chart */}
        <Card title="Doanh thu & Chi phí" subtitle="Theo tháng">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.revenue_trend || []}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1565C0" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#1565C0" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F44336" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#F44336" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => (v / 1000000).toFixed(0) + 'tr'} />
                <Tooltip formatter={(v: number) => new Intl.NumberFormat('vi-VN').format(v) + ' đ'} />
                <Area type="monotone" dataKey="revenue" stroke="#1565C0" fill="url(#revGrad)" name="Doanh thu" strokeWidth={2} />
                <Area type="monotone" dataKey="expense" stroke="#F44336" fill="url(#expGrad)" name="Chi phí" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* AR/AP Chart */}
        <Card title="Công nợ" subtitle="Phải thu / Phải trả theo tháng">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.ar_ap_trend || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => (v / 1000000).toFixed(0) + 'tr'} />
                <Tooltip formatter={(v: number) => new Intl.NumberFormat('vi-VN').format(v) + ' đ'} />
                <Legend />
                <Bar dataKey="receivable" fill="#1565C0" name="Phải thu" radius={[4, 4, 0, 0]} />
                <Bar dataKey="payable" fill="#FF9800" name="Phải trả" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Aging */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Công nợ phải thu quá hạn" subtitle="Phân tích theo kỳ hạn">
          <div className="space-y-3">
            {data && [
              { label: 'Trong hạn', value: data.ar_aging.current, pct: 40 },
              { label: '30-60 ngày', value: data.ar_aging.overdue_30, pct: 25 },
              { label: '60-90 ngày', value: data.ar_aging.overdue_60, pct: 15 },
              { label: 'Trên 90 ngày', value: data.ar_aging.overdue_90, pct: 20 },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-24">{item.label}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${item.pct}%` }} />
                </div>
                <span className="text-sm font-mono font-medium">
                  <VNDisplay amount={item.value} />
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Công nợ phải trả quá hạn" subtitle="Phân tích theo kỳ hạn">
          <div className="space-y-3">
            {data && [
              { label: 'Trong hạn', value: data.ap_aging.current, pct: 45 },
              { label: '30-60 ngày', value: data.ap_aging.overdue_30, pct: 30 },
              { label: '60-90 ngày', value: data.ap_aging.overdue_60, pct: 15 },
              { label: 'Trên 90 ngày', value: data.ap_aging.overdue_90, pct: 10 },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-24">{item.label}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div className="bg-warning-500 h-2 rounded-full" style={{ width: `${item.pct}%` }} />
                </div>
                <span className="text-sm font-mono font-medium">
                  <VNDisplay amount={item.value} />
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
