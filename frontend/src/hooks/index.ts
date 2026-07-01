import { useState, useEffect } from 'react'

type ShortcutHandler = (e: KeyboardEvent) => void

export function useShortcuts(handlers: Record<string, ShortcutHandler>) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
      for (const [key, fn] of Object.entries(handlers)) {
        const parts = key.split('+')
        const ctrl = parts.includes('ctrl')
        const shift = parts.includes('shift')
        const alt = parts.includes('alt')
        const k = parts[parts.length - 1].toLowerCase()
        if (e.key.toLowerCase() === k && e.ctrlKey === ctrl && e.shiftKey === shift && e.altKey === alt) {
          e.preventDefault()
          fn(e)
          return
        }
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [handlers])
}

export function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}
