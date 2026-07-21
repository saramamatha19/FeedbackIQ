export const CATEGORY_COLORS: Record<string, string> = {
  Bug: 'var(--cat-1)',
  'Feature Request': 'var(--cat-2)',
  Complaint: 'var(--cat-3)',
  Praise: 'var(--cat-5)',
  Question: 'var(--cat-4)',
  Other: 'var(--cat-other)',
}

export const CATEGORY_ICONS: Record<string, string> = {
  Bug: '🐛',
  'Feature Request': '✨',
  Complaint: '😠',
  Praise: '💚',
  Question: '❓',
  Other: '📋',
}

export const SENTIMENT_COLORS: Record<string, string> = {
  Positive: 'var(--color-positive)',
  Negative: 'var(--color-negative)',
  Neutral: 'var(--color-neutral)',
  Mixed: 'var(--color-watch)',
}

export const URGENCY_STYLES: Record<string, { color: string; label: string }> = {
  Low: { color: 'var(--color-info)', label: 'Low' },
  Medium: { color: 'var(--color-watch)', label: 'Medium' },
  High: { color: '#ea580c', label: 'High' },
  Critical: { color: 'var(--color-urgent)', label: 'Critical' },
}

export const SEVERITY_ORDER = ['Minor', 'Moderate', 'Major', 'Blocker']

export const SEVERITY_FILL: Record<string, number> = {
  Minor: 0.25,
  Moderate: 0.5,
  Major: 0.75,
  Blocker: 1,
}

export const BUSINESS_IMPACT_FILL: Record<string, number> = {
  None: 0.1,
  Low: 0.35,
  Medium: 0.65,
  High: 1,
}

export const EMOTION_EMOJI: Record<string, string> = {
  Frustration: '😤',
  Anger: '😡',
  Confusion: '😕',
  Satisfaction: '🙂',
  Delight: '😍',
  Disappointment: '😞',
  Neutral: '😐',
}

export const CANONICAL_THEMES = [
  'Login & Authentication',
  'Performance & Speed',
  'UI/UX & Design',
  'Pricing & Billing',
  'Customer Support',
  'Onboarding',
  'Mobile App',
  'Notifications',
  'Search & Discovery',
  'Data Export/Import',
  'Integrations & API',
  'Reliability & Bugs',
  'Security & Privacy',
  'Feature Request',
  'Documentation & Help',
  'Account Management',
  'Collaboration & Sharing',
  'Reporting & Analytics',
  'Accessibility',
  'Other',
]
