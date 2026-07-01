import React from 'react'
import { Input } from './Input'
import { Select } from './Select'

interface SearchInputProps {
  value: string
  onChange: (v: string) => void
  placeholder?: string
}

export function SearchInput({ value, onChange, placeholder = 'Tìm kiếm...' }: SearchInputProps) {
  return (
    <Input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="max-w-xs"
      icon={
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      }
    />
  )
}

interface FilterBarProps {
  children: React.ReactNode
}

export function FilterBar({ children }: FilterBarProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      {children}
    </div>
  )
}

interface FilterSelectProps {
  value: string
  onChange: (v: string) => void
  label: string
  options: { value: string; label: string }[]
}

export function FilterSelect({ value, onChange, label, options }: FilterSelectProps) {
  return (
    <Select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={label}
      options={options}
      className="w-40"
    />
  )
}
