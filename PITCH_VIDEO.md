# EcoSync AI 3-Minute Pitch Video Plan

Use this as the source of truth for the preliminary 3-minute video. The video should feel like a fast product demo with a few slide overlays, not a traditional slide presentation. Judges need to see the problem fit, the live product, the AI behavior, the human oversight, the evaluation evidence, and the Google deployment story.

Companion deck: [EcoSync_AI_3_Minute_Pitch.pptx](EcoSync_AI_3_Minute_Pitch.pptx).

## One-Line Story

EcoSync AI turns manual ecosystem coordination into explainable, human-approved, reusable relationship records across startups, mentors, partners, and programs.

## Best Live Video To Show

Show one continuous browser recording of the app, with only short slide/title overlays at the beginning and end. Do not use hackathon venue footage or the raw briefing recording in the final 3-minute video; it takes time away from the working demo and judging evidence.

Primary live demo flow:

1. Dashboard overview.
2. Matching screen.
3. Select `NasiNext Cloud Kitchen`.
4. Generate mentor recommendations.
5. Show the top recommendation card in detail.
6. Refresh one AI explanation.
7. Approve one recommendation and mark another for review.
8. Open Relationship Board.
9. Open Evaluation.
10. End with the deck slide that summarizes Google tech, SDGs, and scalability.

## Required Slides And Footage

| Time | Visual | Source | Purpose |
| --- | --- | --- | --- |
| 0:00-0:08 | Title slide: `EcoSync AI` + one-line story | Deck slide | Brand the idea immediately. |
| 0:08-0:22 | Problem slide: ecosystem relationships are fragmented across spreadsheets, chat, and coordinator memory | Deck slide | Hit problem-solution fit. |
| 0:22-0:38 | Dashboard live footage | App | Prove this is a working product. |
| 0:38-1:32 | Matching live footage for `NasiNext Cloud Kitchen` | App | Show the core AI-assisted workflow. |
| 1:32-1:58 | Recommendation card close-up | App | Show scoring, Gemini explanation, risks, gaps, ethics, and outcome metric. |
| 1:58-2:20 | Refresh, approve, and review actions | App | Show human oversight and control. |
| 2:20-2:38 | Relationship Board live footage | App | Show reusable lifecycle records. |
| 2:38-2:50 | Evaluation live footage | App | Show AI model performance evidence. |
| 2:50-3:00 | Closing slide: Google tech + SDG 8, 9, 17 + expansion path | Deck slide | Land rubric alignment and impact. |

## Slide Content

Keep slides minimal because the app is the hero.

### Slide 1: Title

Title: `EcoSync AI`

Subtitle: `AI-powered ecosystem linkage orchestration`

Footer text: `From one-off matching to reusable relationship records`

### Slide 2: Problem

Title: `Ecosystem linkage does not scale in spreadsheets`

Bullets:

- Program teams manually match startups, mentors, partners, and services.
- Relationship context is lost after each cohort.
- Support gaps, risks, follow-ups, and outcomes are hard to track.

### Slide 3: Closing

Title: `Built with Google AI for scalable ecosystem partnerships`

Bullets:

- Gemini explanations for rationale, risks, next action, ethics, and outcome metrics.
- Firestore-ready storage and Google Cloud Run deployment path.
- Expands from mentor matching to partners, funders, alumni, and cross-country programs.
- SDG 8, SDG 9, SDG 17.

## Exact Timeline, Screen Actions, And Script

### 0:00-0:08 | Title

Screen action: Show Slide 1.

Script:

> This is EcoSync AI, an AI-powered ecosystem linkage platform that turns startup support relationships into explainable, reusable records.

### 0:08-0:22 | Problem

Screen action: Show Slide 2.

Script:

> The problem is that innovation programs still coordinate startups, mentors, partners, and services through spreadsheets, chat, and personal memory. That may work for one small cohort, but it breaks when the ecosystem grows across programs, cities, and countries.

### 0:22-0:38 | Product Overview

Screen action: Switch to the live app Dashboard. Slowly move the cursor across ecosystem counts, recommendations, approved relationships, and review-needed relationships.

Script:

> EcoSync AI gives program managers one workspace to understand their ecosystem, generate relationship recommendations, approve decisions, and monitor the relationship lifecycle after the match is made.

### 0:38-1:02 | Generate Recommendations

Screen action:

1. Open `Matching`.
2. Select `NasiNext Cloud Kitchen`.
3. Click `Generate Relationships`.

Script:

> Here I select NasiNext Cloud Kitchen from the Kuala Lumpur SME Growth Cohort and generate mentor recommendations. The platform ranks mentors using deterministic scoring across domain expertise, business challenge overlap, stage fit, location, availability, and growth support.

### 1:02-1:32 | Explain The Top Match

Screen action: Pause on the top recommendation card. Zoom browser to 90-100% so score ring, score breakdown, AI rationale, risks, gaps, next action, ethics, and outcome metric are readable.

Script:

> The key AI layer is not just a number. Gemini-ready structured explanations turn the score into decision support: why this relationship fits, how confident the system is, what risks to consider, what support gaps remain, the recommended next action, the ethical guardrail, and a measurable outcome metric.

### 1:32-1:58 | Show AI Control

Screen action:

1. Click the refresh icon on the top recommendation.
2. Briefly point to the updated AI mode/cache/model/confidence area if visible.

Script:

> Each recommendation can refresh its AI explanation independently, and the backend validates structured AI output before showing it. If Gemini is unavailable, EcoSync falls back to deterministic explanations so the demo remains reliable, but the production path uses Gemini for richer reasoning.

### 1:58-2:20 | Human Oversight

Screen action:

1. Click `Approve` on the strongest recommendation.
2. Click `Review` on another recommendation.

Script:

> EcoSync does not make autonomous assignments. A human program manager stays accountable. They can approve, reject, or mark a recommendation for review when confidence, risks, or fairness concerns need more judgment.

### 2:20-2:38 | Relationship Lifecycle

Screen action: Open `Relationships` and show approved and review-needed items.

Script:

> Once a recommendation is approved, it becomes a relationship record. This is the important shift: the ecosystem now remembers who was connected, why the connection was made, what happens next, and what outcome should be measured.

### 2:38-2:50 | Model Performance Evidence

Screen action: Open `Evaluation`. Show benchmark cases, expected top mentor, actual top mentor, top-one accuracy, confidence, and AI mode counts.

Script:

> For model performance, EcoSync includes benchmark evaluation: expected top mentor, actual top mentor, top-one accuracy, average confidence, and AI mode counts. That gives judges evidence that the AI is measurable, not a black box.

### 2:50-3:00 | Closing Impact

Screen action: Show Slide 3.

Script:

> EcoSync AI uses Gemini, Firestore-ready persistence, and a Cloud Run deployment path to support SDG 8, SDG 9, and SDG 17. Starting with mentor matching, the same relationship model can scale to partners, funders, alumni, and regional ecosystem programs.

## Recording Checklist

- Run the app locally with `docker compose up --build`.
- Open the frontend at `http://localhost:5173`.
- Log in before recording.
- Preselect or prepare the seeded demo cohort.
- Use `NasiNext Cloud Kitchen` for the matching demo.
- Keep the browser at 90-100% zoom.
- Use 1080p screen recording.
- Hide bookmarks, notifications, terminal windows, and unrelated tabs.
- Keep cursor movements slow and intentional.
- Record the browser flow continuously, then add the title/problem/closing slide overlays in editing.

## Rubric Beats To Make Visible

| Rubric area | What the video must show |
| --- | --- |
| Google Technology Integration | Say `Gemini`, `Firestore-ready`, and `Cloud Run deployment path`. |
| AI Implementation Quality | Show deterministic score plus structured AI rationale, risks, gaps, ethics, next action, and outcome metric. |
| Working Demo and UI/UX | Show the actual dashboard, matching, relationships, and evaluation screens. |
| AI Model Performance | Show the Evaluation screen. |
| Originality and Creativity | Say `reusable relationship records`, not only `mentor matching`. |
| Problem-Solution Fit | Start from manual ecosystem linkage and fragmented coordination. |
| Scalability | Close with expansion to partners, funders, alumni, service providers, and cross-country programs. |
| Deployment Readiness | Mention Docker, Firestore-ready persistence, and Cloud Run path. |

## What Not To Show

- Do not spend video time on Docker logs, code, or environment files.
- Do not show the registration/admin flow unless the judge specifically asks later.
- Do not use the event briefing recording as main footage.
- Do not over-explain the full architecture; one sentence is enough.
- Do not demo every menu. The 3-minute video needs one strong story.

## Retake Checklist

Before exporting, confirm the video clearly proves:

- The product is functional, not a mockup.
- AI is essential to the recommendation workflow.
- Human approval is required before a relationship is created.
- The recommendation becomes a reusable lifecycle record.
- Model performance evidence is visible.
- Google technology and deployment readiness are stated.
- The impact ties to SDG 8, SDG 9, and SDG 17.
