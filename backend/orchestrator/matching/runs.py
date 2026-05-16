from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..ai.gemini import explain_match
from ..services.storage import repository
from .scoring import score_match


def create_match_run(startup_id, mentor_ids=None):
    startup = repository.get_startup(startup_id)
    if not startup:
        raise ValueError("Startup not found")

    mentors = repository.list_mentors()
    if mentor_ids:
        wanted = set(mentor_ids)
        mentors = [mentor for mentor in mentors if mentor["id"] in wanted]

    match_run = repository.create_match_run(
        {
            "startup_id": startup_id,
            "cohort_id": startup.get("cohort_id"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
            "relationship_scope": "mentor-startup",
        }
    )

    recommendations = []
    for mentor in mentors:
        deterministic = score_match(startup, mentor)
        ai = explain_match(startup, mentor, deterministic)
        recommendations.append(
            {
                "id": f"recommendation-{uuid.uuid4().hex[:8]}",
                "match_run_id": match_run["id"],
                "startup_id": startup["id"],
                "mentor_id": mentor["id"],
                "mentor": mentor,
                "total_score": deterministic["total_score"],
                "score_breakdown": deterministic["score_breakdown"],
                "matched_terms": deterministic["matched_terms"],
                "support_gaps": deterministic["support_gaps"],
                "risks": deterministic["risks"],
                "relationship_type": ai["relationship_type"],
                "confidence": ai["confidence"],
                "recommended_next_action": ai["recommended_next_action"],
                "outcome_metric": ai["outcome_metric"],
                "ethical_consideration": ai["ethical_consideration"],
                "ai": ai,
                "status": "recommended",
                "lifecycle_status": "recommended",
            }
        )

    recommendations.sort(key=lambda item: item["total_score"], reverse=True)
    repository.replace_recommendations_for_run(match_run["id"], recommendations)
    match_run["recommendations"] = recommendations
    return match_run


def get_match_run(match_run_id):
    match_run = repository.get_match_run(match_run_id)
    if not match_run:
        return None
    match_run["recommendations"] = sorted(
        repository.recommendations_for_run(match_run_id),
        key=lambda item: item["total_score"],
        reverse=True,
    )
    return match_run
