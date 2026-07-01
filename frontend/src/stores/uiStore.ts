import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean
  sidebarCollapsed: boolean
  currentLang: 'vi' | 'en'
  currentPeriod: string
  darkMode: boolean
  toggleSidebar: () => void
  toggleSidebarCollapse: () => void
  setLang: (lang: 'vi' | 'en') => void
  setPeriod: (period: string) => void
  toggleDarkMode: () => void
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  sidebarCollapsed: false,
  currentLang: 'vi',
  currentPeriod: '',
  darkMode: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleSidebarCollapse: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setLang: (lang) => set({ currentLang: lang }),
  setPeriod: (period) => set({ currentPeriod: period }),
  toggleDarkMode: () => set((s) => ({ darkMode: !s.darkMode })),
}))
