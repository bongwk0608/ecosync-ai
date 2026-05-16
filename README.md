# EcoSync AI

AI-powered ecosystem linkage orchestration for scalable program and cohort management.

EcoSync AI is a Build with AI MyHack prototype for program managers who need to form, approve, monitor, and reuse ecosystem relationships across cohorts. The official problem highlights that mentor, company, partner, and program linkages are often created manually as one-off assignments. EcoSync treats those relationships as first-class entities with AI recommendations, human approval, lifecycle status, and measurable next actions.

## What the Demo Shows

- A Kuala Lumpur SME cohort with seeded startups and mentors.
- Startup-to-mentor ecosystem matching for food and beverage and small business domains.
- Partner and program data to show reusable ecosystem context beyond one cohort.
- Deterministic analytics score breakdowns for domain fit, business challenge fit, stage, location, availability, and growth fit.
- Gemini-compatible explanation generation with model/fallback visibility.
- Relationship actions: approve, reject, or mark a recommendation as needing review.
- Relationship lifecycle tracking with next actions, risk notes, and outcome metrics.
- Dashboard and evaluation screens for rubric evidence.

## Run with Docker

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/api/health/

The default configuration uses in-memory seeded demo data. To use Firestore and Gemini, copy `.env.example` to `.env`, fill the credentials, and set `USE_FIRESTORE=1`.

Set `REMEMBER_LLM_RESPONSES=1` to cache Gemini/fallback explanations per startup-mentor pair. Set it to `0` to call Gemini or fallback fresh for every recommendation.

User access is protected by admin approval. Run migrations, create a superuser, then approve or decline registrations in Django Admin:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

Configure Gmail SMTP with a Gmail App Password if you want approval/decline emails to send from a real Gmail inbox. Without SMTP settings, local development uses console email output.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Surface

- `GET /api/health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`
- `GET /api/dashboard/`
- `GET /api/evaluation/`
- `GET /api/cohorts/`
- `GET /api/programs/`
- `GET /api/partners/`
- `GET /api/startups/`
- `POST /api/startups/`
- `GET /api/startups/{id}/`
- `PATCH /api/startups/{id}/` staff only
- `DELETE /api/startups/{id}/` staff only
- `GET /api/mentors/`
- `POST /api/mentors/`
- `GET /api/mentors/{id}/`
- `PATCH /api/mentors/{id}/` staff only
- `DELETE /api/mentors/{id}/` staff only
- `POST /api/match-runs/`
- `GET /api/match-runs/{id}/`
- `POST /api/recommendations/{id}/refresh-ai/`
- `GET /api/relationships/`
- `POST /api/relationships/`

All ecosystem APIs require `Authorization: Token <token>` after login. New registrations remain inactive until an admin approves them in Django Admin.
Approved users can add startup and mentor datasets. Only staff/admin users can update or delete those datasets.

Recommendation responses include `ai_cache_status`:

- `hit`: reused a valid cached explanation.
- `miss`: generated a new explanation because cache was empty or stale.
- `refresh`: refreshed one recommendation card manually.
- `disabled`: cache is off because `REMEMBER_LLM_RESPONSES=0`.

## Rubric Alignment

- Google Technology Integration: Gemini explanations and Firestore-ready persistence, with a Google Cloud Run deployment path.
- AI Implementation Quality: deterministic ranking plus Gemini JSON explanations, fallback validation, risks, gaps, confidence, and ethical guardrails.
- Working Demo & UI/UX: dashboard, matching workspace, directories, relationship board, and evaluation view.
- AI Model Performance: benchmark cases expose expected vs actual top mentor, top-1 accuracy, average confidence, and AI mode counts.
- Problem-Solution Fit: replaces manual ecosystem coordination with reusable relationship records and human-approved recommendations.
- Scalability: profile and relationship data can be reused across cohorts, programs, and regions.
- Deployment Readiness: Docker Compose for local demo; Firestore/Gemini env vars for cloud-backed runs.

## Deployment Readiness

Local demo:

```bash
docker compose up --build
```

Cloud deployment path:

1. Build backend and frontend containers.
2. Deploy backend to Google Cloud Run with `GEMINI_API_KEY`, `GEMINI_MODEL`, `REMEMBER_LLM_RESPONSES`, Gmail SMTP settings, Firestore credentials, allowed hosts, and CORS origins.
3. Deploy frontend to Cloud Run, Firebase Hosting, or another static host with `VITE_API_URL` pointed at the backend.
4. Set `USE_FIRESTORE=1` when Firestore persistence is ready; keep `USE_FIRESTORE=0` for deterministic judging demos.

## Prototype Notes

- Registration approval uses Django Admin, DRF token auth, and optional Gmail SMTP result emails.
- Firestore is abstracted behind repository-style storage helpers.
- Matching logic is split across `orchestrator.matching`.
- AI prompting, validation, fallback, and evaluation are split across `orchestrator.ai`.
- Gemini output is validated and falls back to deterministic demo explanations when unavailable.

See `SUBMISSION.md` for the short pitch, business model, SDG framing, and production next steps.
