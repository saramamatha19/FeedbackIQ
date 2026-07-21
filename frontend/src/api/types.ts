export interface User {
  id: string
  email: string
  full_name: string | null
  role: string
  created_at: string
}

export interface Prediction {
  id: string
  category: string
  sentiment: string
  emotion: string
  theme: string
  urgency: string
  severity: string
  business_impact: string
  customer_intent: string
  confidence_score: number
  ai_explanation: string
  suggested_action: string
  needs_human_review: boolean
  processing_time_ms: number | null
  prompt_version: string
  model_name: string
  created_at: string
}

export interface Feedback {
  id: string
  upload_id: string
  raw_text: string
  created_at: string
  prediction: Prediction | null
}

export interface Upload {
  id: string
  source_type: 'single' | 'paste' | 'csv'
  original_filename: string | null
  display_name: string | null
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial'
  current_stage: string | null
  total_rows: number
  processed_rows: number
  failed_rows: number
  created_at: string
  completed_at: string | null
}

export interface UploadStatus {
  id: string
  status: Upload['status']
  current_stage: string | null
  total_rows: number
  processed_rows: number
  failed_rows: number
  error_message: string | null
}

export interface KeySignal {
  headline: string
  detail: string
  supporting_theme: string
  severity_hint: 'info' | 'watch' | 'urgent'
}

export interface DashboardData {
  overview: {
    total_feedback: number
    positive: number
    neutral: number
    negative: number
    urgent: number
    avg_confidence: number
    avg_severity: number
    duplicate_groups: number
    contradictions: number
  }
  category_breakdown: { category: string; count: number }[]
  sentiment_distribution: { sentiment: string; count: number }[]
  emotion_distribution: { emotion: string; count: number }[]
  top_themes: { theme: string; count: number }[]
  feature_request_ranking: { theme: string; votes: number }[]
  bug_leaderboard: {
    theme: string
    occurrences: number
    max_severity: number
    urgent_count: number
    latest_occurrence: string | null
  }[]
  key_signals: KeySignal[]
}

export interface DashboardResponse {
  upload_id: string | null
  generated_at: string
  data: DashboardData
}

export interface NLQueryResponse {
  filters_applied: Record<string, unknown>
  result_count: number
  results: Feedback[]
}
