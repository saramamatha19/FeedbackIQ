import { create } from 'zustand'

type Theme = 'light' | 'dark'

type FeedbackScope = 'own' | 'admin'

interface UiState {
  theme: Theme
  selectedFeedbackId: string | null
  selectedFeedbackScope: FeedbackScope
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
  openFeedbackDrawer: (id: string, scope?: FeedbackScope) => void
  closeFeedbackDrawer: () => void
}

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('fiq-theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
  localStorage.setItem('fiq-theme', theme)
}

const initialTheme = getInitialTheme()
applyTheme(initialTheme)

export const useUiStore = create<UiState>((set, get) => ({
  theme: initialTheme,
  selectedFeedbackId: null,
  selectedFeedbackScope: 'own',
  setTheme: (theme) => {
    applyTheme(theme)
    set({ theme })
  },
  toggleTheme: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark'
    applyTheme(next)
    set({ theme: next })
  },
  openFeedbackDrawer: (id, scope = 'own') => set({ selectedFeedbackId: id, selectedFeedbackScope: scope }),
  closeFeedbackDrawer: () => set({ selectedFeedbackId: null }),
}))
