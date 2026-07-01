export function fmtVND(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === '') return '—'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return '—'
  const abs = Math.abs(num)
  const formatted = abs.toLocaleString('vi-VN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
  return num < 0 ? `(${formatted})` : formatted
}

export function fmtDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    const day = String(d.getDate()).padStart(2, '0')
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const year = d.getFullYear()
    return `${day}/${month}/${year}`
  } catch { return dateStr }
}

export function fmtDateISO(dateStr: string): string {
  try {
    const [d, m, y] = dateStr.split('/')
    return `${y}-${m}-${d}`
  } catch { return dateStr }
}

export function fmtDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return `${fmtDate(dateStr)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch { return dateStr }
}

export function parseVNNumber(value: string): number {
  return parseFloat(value.replace(/\./g, '').replace(',', '.')) || 0
}

export function fmtPeriod(period: string): string {
  const year = period.slice(0, 4)
  const month = period.slice(4, 6)
  const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
  return `Tháng ${months[parseInt(month) - 1]}/${year}`
}
