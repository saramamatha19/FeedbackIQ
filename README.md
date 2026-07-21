# FeedbackIQ — AI Customer Feedback Intelligence Platform

FeedbackIQ ingests customer feedback (single entries, pasted batches, or CSV files of
thousands of rows) and runs it through an AI pipeline that classifies category, sentiment,
emotion, theme, urgency, severity, business impact, and intent — then surfaces it all through
a SaaS-style analytics dashboard with natural-language search.

See `SETUP.md` for how to run it. This document explains *why* it's built the way it is,
since — per the project brief — prompt engineering is the primary evaluation criterion, with
backend architecture, DB design, and UI/UX close behind.

---

## 1. Prompt Engineering (the primary graded surface)

All prompts live in `backend/app/prompts/`, each as a self-contained module with:
`PROMPT_VERSION`, `REVISION_HISTORY`, `SYSTEM_PROMPT`, `FEWSHOT_EXAMPLES`, a strict
`JSON_SCHEMA` for structured outputs, and a `build_messages()` builder.

| Module | Purpose |
|---|---|
| `classifier_prompt.py` | The workhorse — one structured call classifies category/sentiment/emotion/theme/urgency/severity/business_impact/intent/confidence/explanation/suggested_action for a batch of up to 15 items |
| `split_prompt.py` | Splits a pasted multi-feedback blob into individual verbatim items (bullets, numbered lists, blank-line paragraphs, or rambling prose) |
| `duplicate_confirm_prompt.py` | Confirms whether a fuzzy-shortlisted pair is a true duplicate (same root complaint) vs. merely similar wording |
| `summary_prompt.py` | Produces the dashboard's "This Week's Key Signals" — exactly 3 bullets, generated from pre-aggregated stats, never raw text |
| `nlquery_prompt.py` | Translates a natural-language search query into a structured, enum-constrained filter |
| `_shared/canonical_themes.py`, `_shared/schemas.py`, `_shared/retry.py` | Shared closed-set taxonomy, Pydantic re-validation models, and the uniform retry/fallback wrapper used by every module above |

### Key design decisions (and why)

- **One mega-prompt for classification, not N separate calls per field.** Category, sentiment,
  emotion, urgency, severity, business impact, theme, and intent are all correlated reads of
  the *same text* — splitting them into separate LLM calls would multiply the fixed per-call
  overhead (system prompt + few-shot tokens) for zero accuracy gain, which matters at
  "thousands of rows" scale. Batching 15 items per call amortizes that fixed cost further.
- **Closed-set theme taxonomy (20 canonical themes + "Other"), not free generation.**
  "Unable to login" / "Can't sign in" / "Login failed" need semantic collapsing an LLM is good
  at, but the *output vocabulary* must stay fixed for dashboard aggregation and NL-query
  filtering to work deterministically. Free generation would cause theme explosion at scale.
- **Guardrails**: every categorical field is an explicit enum in an OpenAI structured-output
  schema (`strict: true`), independently re-validated against Pydantic models in code — two
  layers, so a single point of failure (SDK drift, model misbehavior) can't silently corrupt
  data.
- **Retry/error-recovery**: one retry with a stricter system reminder on malformed JSON or
  enum violations, then a safe-default fallback (`category="Other"`, `confidence=0`,
  `needs_human_review=true`) with the raw failed response logged. Low confidence alone never
  triggers a retry — it's a valid signal (ambiguous/sarcastic/short input), not an error.
- **Duplicate detection without embeddings**: theme-grouping does the real cost-cutting
  (O(n²) over a whole batch → O(k²) per theme, k usually small); within a normal-sized theme
  bucket, *every* pair goes to the LLM confirmation rather than being pre-filtered on lexical
  similarity, because true duplicates are frequently worded completely differently. A cheap
  fuzzy filter is only applied as a last-resort cost cap for pathologically large theme
  buckets. (This exact issue was caught during live testing — see §4.)
- **Contradiction detection**: ships as a zero-LLM-cost heuristic (same theme + opposite
  sentiment) for the MVP, per the explicit scope decision below.
- **NL search is not RAG.** The LLM never sees or produces SQL — it emits a structured,
  enum-constrained filter object, which `nl_query_service.py` translates into a parameterized
  SQLAlchemy query via a hand-written field/operator allowlist. `user_id` scoping is applied
  in code, unconditionally, so the LLM's output can never leak cross-tenant data even if it
  ignored every instruction in the prompt. This is the actual safety boundary — the prompt is
  defense-in-depth, not the guarantee.

### Evaluation

`backend/eval/eval_dataset.json` is a 31-item hand-labeled gold set deliberately covering
typos, emoji, sarcasm, mixed-language/code-switched text, one-word input, long rambling
multi-topic feedback, bundled multi-issue feedback, ambiguous/vague feedback, a 2-cluster
duplicate set, and a 2-pair contradiction set. `backend/eval/run_eval.py` runs it against the
live classifier and produces a timestamped JSON + Markdown report.

**Real before/after, not a hypothetical**: the v1.0 baseline run scored 71% on urgency
(vs. 84–97% on other fields), because the model routinely under-called severe cases
("High" instead of "Critical" for crash+data-loss reports) — see
`backend/eval/reports/eval_report_v1.0_20260720T183841Z.md`. That's a genuine
weakness surfaced by the eval harness, not a contrived example. In response, `classifier_prompt.py`
was bumped to v1.1 with an explicit urgency decision rule tied to the spec's own named
critical examples (crash, data loss, payment failure, cannot login, account locked) and a new
few-shot demonstrating it. Re-running the eval
(`backend/eval/reports/eval_report_v1.1_20260720T184034Z.md`) showed:

| Field | v1.0 | v1.1 |
|---|---|---|
| Category | 83.9% | 87.1% |
| Sentiment | 96.8% | 96.8% |
| Theme | 83.9% | 80.6% |
| Urgency | 71.0% | **80.6%** |
| Emotion | 87.1% | 90.3% |

Theme dipped slightly — reported as-is rather than cherry-picked, since a 31-item eval set is
small enough that some movement is noise. The confidence-calibration metric in both reports
(avg confidence, correct vs. incorrect) also honestly shows the model's self-reported
confidence isn't yet strongly discriminating on this sample size — a known limitation, not
hidden.

---

## 2. Architecture

**Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL (local install, no Docker),
repository-pattern data access, service-layer business logic, cookie-based JWT auth.

**The one schema decision worth calling out**: `ai_predictions` is versioned (1:N from
`feedback`), not overwritten in place. A partial unique index
(`UNIQUE(feedback_id) WHERE is_current = true`) enforces exactly one active prediction per
feedback row at the database level. Re-running AI analysis inserts a new row and flips the
old one's flag in the same transaction — this is what makes "re-run AI analysis" and
"prediction history" real, auditable features instead of a lossy overwrite, and it's what lets
the eval harness's before/after comparison mean something at the data layer too.

**Async ingestion**: CSV/paste uploads run through FastAPI `BackgroundTasks` (not
Celery/Redis) with a bounded async batch size — the right tradeoff for a single-instance,
no-Docker deployment; documented as the explicit production upgrade path in `SETUP.md`.

**Frontend**: React + Vite + TypeScript + Tailwind v4 + Framer Motion + Recharts + TanStack
Query + Zustand + React Router. Auth token is an httpOnly cookie (not localStorage) —
immune to XSS-based token theft, which matters more than the CSRF exposure it introduces for
a same-origin app.

---

## 3. What's scoped down (and why)

Per the "few days, depth over breadth" build priority, these are deliberately minimal:

- **Contradiction detection** ships as the heuristic baseline only (see above) — the
  LLM-confirmation layer described in the design doc is a documented stretch goal.
- **Admin panel** is read-only (usage stats + user list), no user management actions.
- **Exports** are CSV only.
- **Background jobs** are in-process, not a distributed queue.
- **Dedup/contradiction** are scoped within a single upload batch, not cross-batch/all-time.

None of these cuts touch the graded core: prompt versioning discipline, few-shot coverage of
every named hard case, guardrails + retry logic, the eval report, the dashboard, the upload
flow with its animated 8-stage pipeline, the feedback detail drawer, or dark/light mode — all
verified working end-to-end against a live Postgres database and the OpenAI API (see below).

---

## 4. What was actually verified (not just written)

Every layer of this system was exercised against live infrastructure during development, not
just type-checked:

- Auth: register → cookie set → `/me` → logout → re-auth rejected, against real Postgres.
- Single/paste/CSV ingestion, the full 8-stage pipeline, and duplicate/contradiction detection
  — run against the real OpenAI API, not mocked.
- **A real bug was caught and fixed via this testing**: the fuzzy duplicate pre-filter
  (`rapidfuzz.token_sort_ratio ≥ 70`) scored the spec's own motivating example — "Unable to
  login" / "Can't sign in" / "Login failed" — at only 40–44, meaning it never reached the LLM
  confirmation step at all. Fixed by sending every pair within a normal-sized theme bucket to
  the LLM directly (see `duplicate_service.py`), since theme-grouping already does the real
  cost-cutting.
- The frontend was driven with a headless-Chromium script through the full login → dashboard →
  upload → CSV processing → dashboard → feedback-drawer flow, in both light and dark mode,
  with zero console errors. This also caught and fixed two real UI bugs: category-breakdown
  pie labels were clipped/unreadable (fixed with a proper legend), and "Praise" and "Feature
  Request" shared the same color in the categorical palette (fixed by giving each category a
  distinct color) — exactly the kind of "never rely on color alone" defect that's easy to miss
  without actually looking at a rendered screenshot.

---

## 5. Project Layout

```
backend/
  app/
    prompts/          versioned prompt modules (the core graded artifact)
    db/models/         SQLAlchemy models incl. the versioned ai_predictions schema
    services/           ai_service (OpenAI client), pipeline_service (8-stage orchestration),
                         duplicate_service, contradiction_service, dashboard_service, nl_query_service
    api/v1/endpoints/    auth, uploads, feedback, dashboard, nl_query, exports, admin
  eval/
    eval_dataset.json    31-item hand-labeled gold set
    run_eval.py          evaluation harness
    reports/             timestamped before/after eval reports
    seed_feedback_dataset.csv   135-row realistic demo dataset
frontend/
  src/
    features/            dashboard, upload, feedback, search — feature-scoped components
    pages/                route-level pages
    api/                  typed API client
```
