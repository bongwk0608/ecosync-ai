# EcoSync AI Submission Notes

## Elevator Pitch

EcoSync AI helps ecosystem program managers automate and monitor high-value relationships between startups, mentors, partners, cohorts, and programs. Instead of manually coordinating linkages in spreadsheets or chat groups, the platform recommends relationships, explains the fit with Gemini-ready AI, requires human approval, and tracks relationship status, risks, next actions, and outcome metrics.

The core idea is simple: ecosystem relationships should not be one-off assignments. They should be reusable, explainable, reviewable records that improve from cohort to cohort.

## Problem Statement Alignment

The MyHack problem focuses on ecosystem linkage at scale. Program teams often manage startups, mentors, partners, funders, and service providers using fragmented data and manual follow-up. That creates several problems:

- Matching is slow and dependent on individual coordinator knowledge.
- Startup and mentor information is duplicated across programs.
- Relationships are created once, then rarely monitored.
- Program managers cannot easily see support gaps, risks, or next actions.
- Successful relationships are difficult to reuse across cohorts, locations, or countries.

EcoSync AI addresses this by making relationship recommendations and relationship lifecycle records first-class parts of the workflow. The app demonstrates startup-to-mentor matching today, but the architecture is designed to expand to partners, funders, service providers, alumni, and cross-program referrals.

## What The Prototype Demonstrates

- Secure registration and login with admin approval.
- Program dashboard showing ecosystem entities, recommendations, and relationship metrics.
- Directory views for startups, mentors, partners, cohorts, and programs.
- AI-assisted matching workspace for generating ranked mentor-startup recommendations.
- Deterministic score breakdowns for domain fit, business challenge fit, stage, location, availability, and strategic growth.
- Gemini-compatible AI explanation for each recommendation.
- Per-recommendation AI refresh and optional LLM response memory/cache.
- Human actions to approve, reject, or mark recommendations for review.
- Relationship board showing decisions and next actions.
- Evaluation screen showing benchmark matching accuracy evidence.
- Firestore-ready persistence and Docker-based local demo deployment.

## Google Technologies Used

- **Gemini API** via `google-generativeai` for structured recommendation explanations.
- **Firebase / Firestore** support for persistent ecosystem data storage.
- **Firebase Admin SDK** and Firestore REST transport support.
- **Google Cloud Run deployment path** for backend and frontend containers.
- **Gmail SMTP** support for registration approval, decline, and pending-status notifications.

Gemini is used where it matters most: not just producing a score, but explaining relationship quality in language a program manager can act on. The AI output includes rationale, risks, support gaps, recommended next action, confidence, outcome metric, and ethical consideration.

## AI Implementation

EcoSync AI combines deterministic scoring with Gemini-generated explanation.

Deterministic scoring ranks mentor fit using:

- domain expertise
- business challenge overlap
- startup stage fit
- location proximity
- mentor availability
- strategic growth support

Gemini then turns the ranked match into a structured decision-support explanation. The prompt asks for strict JSON and the backend validates the response before returning it to the frontend.

Each recommendation includes:

- relationship type
- confidence
- rationale
- risks
- support gaps
- next action
- measurable outcome metric
- ethical consideration
- explanation quality checks
- AI mode and model
- cache status

If Gemini is unavailable, EcoSync falls back to deterministic demo explanations so the demo remains reliable.

## AI Response Memory

The project includes an environment-controlled AI explanation cache:

- `REMEMBER_LLM_RESPONSES=1`: reuse previous AI/fallback explanations when startup data, mentor data, deterministic score, prompt version, and model are unchanged.
- `REMEMBER_LLM_RESPONSES=0`: generate a fresh explanation every match run.
- Each recommendation has a refresh button to regenerate only that card’s AI explanation.

This lowers Gemini cost, improves demo consistency, and still gives users control when they want a fresh explanation.

## Model Performance Evidence

The app includes an evaluation endpoint and frontend evaluation view. It reports:

- benchmark case count
- expected top mentor
- actual top mentor
- top-1 accuracy
- average confidence
- AI mode counts

This is lightweight evidence suitable for the preliminary round. The next improvement would be expanding benchmark cases to cover more industries, more relationship types, partner referrals, and weaker/ambiguous matches.

## Ethics And Human Oversight

EcoSync AI is designed as decision support, not autonomous assignment.

Ethical safeguards:

- Human approval is required before a recommendation becomes a relationship.
- AI confidence is visible.
- Risks and support gaps are shown beside the recommendation.
- The system includes an ethical consideration field per recommendation.
- Users can reject or mark recommendations as needing review.
- Admin approval is required before new users can access the platform.

This reduces the risk of blindly accepting AI output and keeps program managers accountable for final relationship decisions.

## Security And User Management

The project includes a practical security layer for the demo:

- User registration requires admin approval.
- Pending and declined users cannot access app data.
- Approved users receive token-based API access.
- Admins review registration applications in Django Admin.
- Users receive email notifications when account status changes.
- Normal users can add datasets but cannot delete them.
- Staff/admin users can update and delete startup and mentor datasets.

Roles:

- `program_manager`: approved user workspace access.
- `ecosystem_partner`: approved user workspace access.
- `admin_operator`: staff/admin access when approved.

## Business Model

Target customers:

- startup accelerators
- government grant agencies
- university innovation teams
- chambers of commerce
- NGO entrepreneurship programs
- corporate innovation programs

Possible business model:

- SaaS subscription per organization.
- Tiered pricing by number of cohorts, users, and ecosystem entities.
- Paid modules for AI evaluation, Firestore persistence, cross-program analytics, and reporting.
- Enterprise tier for custom integrations with CRM, grant systems, or national startup databases.

Value proposition:

- reduce manual coordination time
- improve match quality
- make support gaps visible
- standardize relationship follow-up
- preserve ecosystem knowledge across cohorts

## Scalability

Technical scalability:

- Backend logic is split into domain, matching, AI, storage, and API layers.
- Storage abstraction supports demo store and Firestore-backed persistence.
- Frontend is split into API client, reusable components, and views.
- Docker Compose provides repeatable local setup.
- Google Cloud Run path is documented.

Operational scalability:

- Profiles can be reused across cohorts.
- Relationship history can inform future recommendations.
- Relationship status and outcome metrics create longitudinal program evidence.
- Matching can expand beyond mentors to partners, funders, service providers, alumni, and regional ecosystem actors.

## Deployment Approach

Local demo:

- Run with Docker Compose.
- Backend runs migrations automatically.
- Frontend runs on Vite.
- Demo can use seeded in-memory data or Firestore.

Production path:

1. Deploy Django backend container to Google Cloud Run.
2. Configure Gemini, Firestore, Gmail SMTP, allowed hosts, and CORS through environment variables.
3. Deploy React frontend to Cloud Run, Firebase Hosting, or another static host.
4. Point `VITE_API_URL` to the deployed backend API.
5. Use Firestore for persistent ecosystem data.

## Demo Script

Use [PITCH_VIDEO.md](PITCH_VIDEO.md) as the source of truth for the preliminary 3-minute recording. The video should be a continuous app demo:

1. Open Dashboard and show ecosystem counts, recommendations, and relationship metrics.
2. Open Matching and select `NasiNext Cloud Kitchen`.
3. Generate relationships.
4. Explain the score breakdown, Gemini-ready rationale, risks, support gaps, next action, ethical guardrail, and outcome metric.
5. Refresh one AI explanation to show per-card AI control.
6. Approve one recommendation and mark another for review.
7. Open Relationship Board to show lifecycle tracking.
8. Open Evaluation to show benchmark matching evidence.
9. Close with scalability: the same relationship model can support mentors, partners, funders, alumni, and future cohorts.

## UN SDG Impact

EcoSync AI supports:

- **SDG 8: Decent Work and Economic Growth** by helping SMEs access better mentorship, market access, and program support.
- **SDG 9: Industry, Innovation and Infrastructure** by improving innovation ecosystem infrastructure and reducing repeated manual coordination.
- **SDG 17: Partnerships for the Goals** by making cross-organization ecosystem relationships easier to form, monitor, and reuse.

## Current Limitations

- Benchmark evaluation set is still small.
- Firestore is integrated through a repository abstraction, but deeper production data modeling is a future step.
- Organization-level data isolation is not fully implemented yet.
- Matching currently focuses on startup-to-mentor recommendations, though the architecture supports expansion.
- Cloud Run deployment path is documented, but the final deployed URL should be prepared before presentation if required.

## Production Next Steps

- Expand benchmarks and model evaluation cases.
- Add organization-level tenancy and audit reports.
- Add full CRUD admin screens for all ecosystem entity types.
- Add partner, funder, service provider, and alumni matching.
- Add outcome tracking over multiple months.
- Add CRM/import integrations.
- Add richer analytics for program managers and funders.
- Deploy backend and frontend to Google Cloud Run or Firebase Hosting.

## Why EcoSync AI Should Score Well

EcoSync AI is not only a mentor matching demo. It is a relationship orchestration platform aligned with the hackathon problem: automating ecosystem linkage at scale. It uses Google AI where explanation matters, keeps humans in control, records lifecycle decisions, and provides a practical path from prototype to deployable ecosystem infrastructure.
