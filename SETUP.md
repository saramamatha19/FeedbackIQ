# FeedbackIQ — Setup

## Prerequisites

- Python 3.12
- Node.js 20+ (tested on 24)
- PostgreSQL running locally (no Docker)
- An OpenAI API key

## 1. Database

```bash
# Create role + database (adjust superuser/password for your local install)
psql -U postgres -h localhost -c "CREATE ROLE feedbackiq LOGIN PASSWORD 'feedbackiq';"
psql -U postgres -h localhost -c "CREATE DATABASE feedbackiq OWNER feedbackiq;"
psql -U postgres -h localhost -d feedbackiq -c "CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS citext;"
```

## 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL, OPENAI_API_KEY, and a random JWT_SECRET
# (generate one with: python3 -c "import secrets; print(secrets.token_urlsafe(48))")

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Health check: `GET /health`.

### Promote a user to admin

Admin panel access is role-gated. After registering a user through the app:

```bash
psql -U feedbackiq -h localhost -d feedbackiq -c "UPDATE users SET role='admin' WHERE email='you@example.com';"
```

### Run the prompt evaluation

```bash
cd backend
source .venv/bin/activate
python3 eval/run_eval.py
```

Writes a timestamped JSON + Markdown report to `backend/eval/reports/`, one pair per run, so
you can diff accuracy across prompt versions. `backend/eval/eval_dataset.json` is the
hand-labeled gold set; `backend/eval/seed_feedback_dataset.csv` is the 135-row realistic
dataset for demoing the CSV upload path.

## 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # or create .env with VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 4. Try it out

1. Register an account at `/register`.
2. Go to **Upload** → **CSV Upload** → upload `backend/eval/seed_feedback_dataset.csv`.
3. Watch the 8-stage processing stepper, then view the **Dashboard**.
4. Filter **Recent Feedback** by category/sentiment/urgency/theme, then click a row to open the detail drawer.

## Known limitations (intentional, see README for rationale)

- Background jobs run in-process (FastAPI `BackgroundTasks`), not a distributed queue —
  progress is lost if the server restarts mid-job.
- Exports are CSV only.
- Contradiction detection is a heuristic baseline (same theme + opposite sentiment), not
  LLM-confirmed.
- Admin panel is read-only (stats + user list), no user management actions.
