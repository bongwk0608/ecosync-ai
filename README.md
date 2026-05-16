# EcoSync AI

AI-powered ecosystem linkage orchestration for scalable program and cohort management.

EcoSync AI is a Build with AI MyHack prototype for program managers who need to form, approve, monitor, and reuse ecosystem relationships across cohorts. Instead of treating mentor, partner, startup, and program connections as one-off spreadsheet assignments, EcoSync turns them into trackable relationship records with AI rationale, human approval, lifecycle status, next actions, and measurable outcomes.

## What The Demo Shows

- A Kuala Lumpur SME cohort with seeded startups, mentors, partners, and program data.
- Startup-to-mentor ecosystem matching with deterministic score breakdowns.
- Gemini-compatible AI explanations with risks, support gaps, confidence, next actions, ethical guardrails, and outcome metrics.
- Per-recommendation AI refresh and optional LLM response caching.
- Human decisions: approve, reject, or mark a recommendation as needing review.
- Relationship board for approved/reviewed/rejected relationship actions.
- Dashboard and evaluation views for rubric evidence.
- Registration, login, admin approval, role access, and optional Gmail status notifications.
- Firestore-ready persistence with a demo fallback store for reliable local judging.

For the preliminary 3-minute recording, use the timestamped run-of-show in [PITCH_VIDEO.md](PITCH_VIDEO.md).

## Tech Stack

- Backend: Django 5, Django REST Framework, DRF token auth
- Frontend: React 18, Vite, lucide-react
- AI: Google Gemini API through `google-generativeai`
- Storage: in-memory demo store or Firebase/Firestore
- Email: Gmail SMTP for account approval/decline/pending notifications
- Local deployment: Docker Compose

## Prerequisites

Install these before running the project:

- Docker Desktop
- Python 3.12 recommended for local backend development
- Node.js 20 recommended for local frontend development
- A Google AI Studio Gemini API key, optional but recommended
- A Firebase project and service account JSON, optional for Firestore mode
- A Gmail account with an App Password, optional for real approval emails

## Environment Setup

Copy the example env file:

```powershell
copy .env.example .env
```

Minimum local demo configuration:

```env
USE_FIRESTORE=0
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
REMEMBER_LLM_RESPONSES=1
```

Recommended full demo configuration:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-3.1-flash-lite
REMEMBER_LLM_RESPONSES=1

USE_FIRESTORE=1
FIRESTORE_TRANSPORT=rest
FIREBASE_CREDENTIALS_FILE=d:\Hackathon 2026\ecosync-ai\your-firebase-adminsdk.json

EMAIL_BACKEND=orchestrator.services.gmail_backend.CertifiEmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_ALLOW_INSECURE_TLS=0
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_gmail_app_password
DEFAULT_FROM_EMAIL=EcoSync AI <your_gmail@gmail.com>
```

Important:

- Do not commit `.env` or Firebase service account JSON.
- `EMAIL_HOST_PASSWORD` must be a Gmail App Password, not your normal Gmail password.
- If local antivirus/proxy software intercepts TLS and causes certificate errors, set `EMAIL_ALLOW_INSECURE_TLS=1` for local demo only.
- `REMEMBER_LLM_RESPONSES=1` caches AI explanations when startup, mentor, score, prompt version, and model are unchanged.
- `REMEMBER_LLM_RESPONSES=0` calls Gemini/fallback fresh on every match run.

## Run With Docker

From the repo root:

```powershell
docker compose up --build
```

Docker automatically runs Django migrations before starting the backend.

Open:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/api/health/
- Django Admin: http://localhost:8000/admin/

Stop the app:

```powershell
docker compose down
```

## First Admin User

Create a Django superuser before approving registrations:

```powershell
cd backend
.\.venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser
```

Then open:

```text
http://localhost:8000/admin/
```

Approve users from:

```text
Orchestrator > User profiles
```

Changing a profile status sends a status email when Gmail SMTP is configured.

## User Registration Flow

1. A visitor opens the React app.
2. They register with all required fields:
   - username
   - email
   - password
   - full name
   - organization
   - role
3. The account is created as inactive with `approval_status=pending`.
4. Admin reviews the user in Django Admin.
5. Admin changes status to `approved`, `declined`, or back to `pending`.
6. The system emails the user whenever the account status changes.
7. Only approved users can log in and access ecosystem APIs.

Role behavior:

- Pending or declined users cannot access the app.
- Approved normal users can view data, run matching, refresh AI, create relationship decisions, and add startup/mentor datasets.
- Normal users cannot delete datasets.
- Staff/admin users can update and delete startup/mentor datasets and use Django Admin.
- `admin_operator` users become staff when approved.

## Local Development Without Docker

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend reads:

```env
VITE_API_URL=http://localhost:8000/api
```

from `frontend/.env`, or defaults to the same URL if not set.

## Firestore Setup

To use Firestore instead of in-memory demo data:

1. Create a Firebase project.
2. Create a Cloud Firestore database.
3. Download a Firebase Admin SDK service account JSON.
4. Place the JSON in the repo root.
5. Set:

```env
USE_FIRESTORE=1
FIRESTORE_TRANSPORT=rest
FIREBASE_CREDENTIALS_FILE=d:\Hackathon 2026\ecosync-ai\your-firebase-adminsdk.json
```

For Docker, `docker-compose.yml` maps the repo to `/workspace`, so the default Docker credential path can be:

```env
FIREBASE_CREDENTIALS_FILE_DOCKER=/workspace/your-firebase-adminsdk.json
```

Seed Firestore with demo data:

```powershell
cd backend
.\.venv\Scripts\activate
python manage.py seed_firestore
```

## Gemini Setup

1. Create an API key in Google AI Studio.
2. Add it to `.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

If `GEMINI_API_KEY` is empty or Gemini fails, the app still works with deterministic fallback explanations.

AI response fields include:

- `ai_mode`
- `model`
- `relationship_type`
- `confidence`
- `rationale`
- `risks`
- `support_gaps`
- `recommended_next_action`
- `outcome_metric`
- `ethical_consideration`
- `explanation_quality_checks`
- `ai_cache_status`

Cache statuses:

- `hit`: reused a valid cached explanation.
- `miss`: generated a new explanation because cache was empty or stale.
- `refresh`: manually refreshed one recommendation card.
- `disabled`: cache is off because `REMEMBER_LLM_RESPONSES=0`.

## Gmail Email Setup

For real account-status notification emails:

1. Log in to the Gmail account used by `EMAIL_HOST_USER`.
2. Enable 2-Step Verification.
3. Create a Gmail App Password for Mail.
4. Put the 16-character app password in `.env`.

Example:

```env
EMAIL_BACKEND=orchestrator.services.gmail_backend.CertifiEmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
DEFAULT_FROM_EMAIL=EcoSync AI <your_gmail@gmail.com>
```

Send a test email:

```powershell
backend\.venv\Scripts\python.exe backend\manage.py shell -c "from django.core.mail import send_mail; print(send_mail('EcoSync AI test email','This is a test email from EcoSync AI.','EcoSync AI <your_gmail@gmail.com>',['recipient@example.com'],fail_silently=False))"
```

If it prints `1`, Gmail accepted the email.

## API Surface

Public:

- `GET /api/health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`

Authenticated and approved:

- `GET /api/auth/me/`
- `POST /api/auth/logout/`
- `GET /api/dashboard/`
- `GET /api/evaluation/`
- `GET /api/cohorts/`
- `GET /api/programs/`
- `GET /api/partners/`
- `GET /api/startups/`
- `POST /api/startups/`
- `GET /api/mentors/`
- `POST /api/mentors/`
- `POST /api/match-runs/`
- `GET /api/match-runs/{id}/`
- `POST /api/recommendations/{id}/refresh-ai/`
- `GET /api/relationships/`
- `POST /api/relationships/`

Staff/admin only:

- `PATCH /api/startups/{id}/`
- `DELETE /api/startups/{id}/`
- `PATCH /api/mentors/{id}/`
- `DELETE /api/mentors/{id}/`

All protected API calls require:

```http
Authorization: Token <token>
```

## Test And Verification

Backend:

```powershell
backend\.venv\Scripts\python.exe backend\manage.py check
backend\.venv\Scripts\python.exe backend\manage.py test orchestrator
```

Frontend:

```powershell
cd frontend
npm run build
```

Current expected result:

- Django system check passes.
- Backend test suite passes.
- Frontend production build passes.

## Troubleshooting

Gmail error `535 Username and Password not accepted`:

- The app reached Gmail, but Gmail rejected the credential.
- Use a Gmail App Password, not the normal Gmail password.
- Make sure the app password belongs to the same account as `EMAIL_HOST_USER`.

Gmail certificate error:

- Local antivirus/proxy software may intercept TLS.
- For local demo only, set:

```env
EMAIL_ALLOW_INSECURE_TLS=1
```

Gemini appears to use fallback:

- Check that `.env` has no hidden BOM at the first line.
- Confirm `GEMINI_API_KEY` is set.
- Restart backend or Docker after editing `.env`.

Firestore connection fails:

- Confirm `FIREBASE_CREDENTIALS_FILE` points to the correct JSON file.
- Confirm Firestore database exists in Firebase Console.
- For Docker, prefer a `/workspace/...` credential path.

Frontend cannot call backend:

- Confirm backend is running on http://localhost:8000.
- Confirm `VITE_API_URL=http://localhost:8000/api`.
- Confirm CORS allows http://localhost:5173.

User cannot log in:

- Confirm the user has a `UserProfile`.
- Confirm `approval_status=approved`.
- Confirm `user.is_active=True`.
- Admin can fix this in Django Admin under User profiles.

## Rubric Alignment

- Google Technology Integration: Gemini explanations, Firestore-ready persistence, Firebase service account support, and Google Cloud Run deployment path.
- AI Implementation Quality: deterministic ranking plus Gemini JSON explanations, validation, fallback, risks, gaps, confidence, ethics, and response caching.
- Working Demo & UI/UX: dashboard, matching workspace, directories, relationship board, evaluation view, auth, and admin approval flow.
- AI Model Performance: benchmark cases expose expected vs actual top mentor, top-1 accuracy, average confidence, and AI mode counts.
- Problem-Solution Fit: replaces manual ecosystem coordination with reusable relationship records and human-approved recommendations.
- Scalability: modular backend, repository-style storage abstraction, role-based access, and reusable cohort/profile/relationship data.
- Deployment Readiness: Docker Compose for local demo, environment-based integrations, and documented Cloud Run path.

## Deployment Readiness

Local demo:

```powershell
docker compose up --build
```

Recommended cloud path:

1. Build backend and frontend containers.
2. Deploy backend to Google Cloud Run.
3. Set production env vars for Django, Gemini, Firestore, Gmail, allowed hosts, and CORS origins.
4. Deploy frontend to Cloud Run, Firebase Hosting, or another static host.
5. Set frontend `VITE_API_URL` to the deployed backend API URL.
6. Use Firestore for persistent storage.

## Prototype Notes

- Firestore is abstracted behind repository-style storage helpers.
- Matching logic is split across `orchestrator.matching`.
- AI prompting, validation, fallback, caching, and evaluation are split across `orchestrator.ai`.
- Registration approval uses Django Admin, DRF token auth, and Gmail SMTP notification hooks.
- Organization-level data isolation and audit-log reporting are production next steps.

See `SUBMISSION.md` for the short pitch, business model, SDG framing, and production next steps.
