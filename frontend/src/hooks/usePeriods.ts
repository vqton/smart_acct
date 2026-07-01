import { useMemo } from 'react'

const VIETNAMESE_MONTHS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

export function usePeriods() {
  const currentYear = new Date().getFullYear()
  const periods = useMemo(() => {
    const result: { value: string; label: string }[] = []
    for (let y = currentYear - 1; y <= currentYear + 1; y++) {
      for (let m = 1; m <= 12; m++) {
        const value = `${y}${String(m).padStart(2, '0')}`
        result.push({ value, label: `Tháng ${VIETNAMESE_MONTHS[m - 1]}/${y}` })
      }
    }
    return result.reverse()
  }, [currentYear])

  const currentPeriod = `${currentYear}${String(new Date().getMonth() + 1).padStart(2, '0')}`

  return { periods, currentPeriod }
}
