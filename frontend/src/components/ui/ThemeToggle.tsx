import { useUiStore } from '@/store/uiStore'

export function ThemeToggle() {
  const { theme, toggleTheme } = useUiStore()
  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-border)] text-base hover:bg-black/5 dark:hover:bg-white/10"
    >
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  )
}
