# EcoSync AI

AI-powered ecosystem relationship orchestration platform for scalable program and cohort management.

EcoSync AI is a hackathon prototype for program managers who need to match SME startups with mentors across cohorts. It uses a React frontend, Django REST API, Firestore-ready storage, Gemini-ready AI explanations, and Docker deployment.

## What the Demo Shows

- A Kuala Lumpur SME cohort with seeded startups and mentors.
- Startup-to-mentor matching for food and beverage and small business domains.
- Deterministic analytics score breakdowns for domain fit, business challenge fit, stage, location, availability, and growth fit.
- Gemini-compatible explanation generation with a local fallback when no API key is configured.
- Relationship actions: approve, reject, or mark a recommendation for review.

## Run with Docker

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/api/health/

The default configuration uses in-memory seeded demo data. To use Firestore and Gemini, copy `.env.example` to `.env`, fill the credentials, and set `USE_FIRESTORE=1`.

Enabling Firestore (Docker)

1. Copy `.env.example` to `.env` and fill `FIREBASE_CLIENT_EMAIL` and `FIREBASE_PRIVATE_KEY` (escape newlines as `\n`).
2. Start with Docker Compose; the backend service will read these variables:

```bash
docker compose --env-file .env up --build
```

Notes:
- The app reads `USE_FIRESTORE=1` to switch to Firestore. Without it, the demo in-memory store is used.
- `FIREBASE_PRIVATE_KEY` in `.env` must contain `\n` for newline markers (the app replaces `\\n` with actual newlines at runtime).
- Alternatively, mount a service account JSON into the container and adapt `orchestrator.services.storage` to load it via `credentials.Certificate("/path/to/json")`.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Surface

- `GET /api/cohorts/`
- `GET /api/startups/`
- `POST /api/startups/`
- `GET /api/mentors/`
- `POST /api/mentors/`
- `POST /api/match-runs/`
- `GET /api/match-runs/{id}/`
- `POST /api/relationships/`

## Prototype Notes

- Authentication is intentionally deferred for demo speed.
- Firestore is abstracted behind `orchestrator.services.storage`.
- Matching logic is isolated in `orchestrator.services.matching`.
- Gemini output is validated and falls back to deterministic demo explanations when unavailable.
