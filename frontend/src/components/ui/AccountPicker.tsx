import { Input } from './Input'
import type { Account } from '@/types/domain'
import { useState, useRef, useEffect } from 'react'

interface AccountPickerProps {
  value: string
  onChange: (code: string, account?: Account) => void
  accounts: Account[]
  label?: string
  error?: string
  disabled?: boolean
  placeholder?: string
}

export function AccountPicker({ value, onChange, accounts, label, error, disabled, placeholder }: AccountPickerProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = accounts.filter(
    (a) => !query || a.code.includes(query) || a.name.toLowerCase().includes(query.toLowerCase())
  ).slice(0, 20)

  const selected = accounts.find((a) => a.code === value)

  return (
    <div ref={ref} className="relative">
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <input
        value={open ? query : (selected ? `${selected.code} - ${selected.name}` : value)}
        onChange={(e) => { setQuery(e.target.value); setOpen(true); if (!e.target.value) onChange('') }}
        onFocus={() => { setOpen(true); setQuery('') }}
        placeholder={placeholder || 'Chọn tài khoản...'}
        disabled={disabled}
        className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:bg-gray-50"
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto scrollbar-thin">
          {filtered.map((acc) => (
            <button
              key={acc.code}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 flex items-center justify-between ${acc.code === value ? 'bg-blue-50' : ''}`}
              onClick={() => { onChange(acc.code, acc); setOpen(false); setQuery('') }}
            >
              <span><span className="font-mono text-primary-600">{acc.code}</span> - {acc.name}</span>
              <span className="text-xs text-gray-400">{acc.account_type}</span>
            </button>
          ))}
        </div>
      )}
      {error && <p className="text-xs text-danger-500 mt-1">{error}</p>}
    </div>
  )
}
