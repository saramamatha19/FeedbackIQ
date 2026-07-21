import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-page)] px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-sm"
      >
        <div className="mb-8 text-center">
          <div className="mb-2 text-2xl font-semibold tracking-tight">
            Feedback<span className="text-blue-600">IQ</span>
          </div>
          <p className="text-sm text-[var(--color-ink-muted)]">AI-powered customer feedback intelligence</p>
        </div>
        <Outlet />
      </motion.div>
    </div>
  )
}
