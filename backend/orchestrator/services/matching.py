from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .gemini import explain_match
from .storage import store


WEIGHTS = {
    "domain_expertise": 25,
    "business_challenge": 20,
    "stage": 15,
    "location": 15,
    "availability": 15,
    "strategic_growth": 10,
}


def create_match_run(startup_id, mentor_ids=None):
    startup = store.get("startups", startup_id)
    if not startup:
        raise ValueError("Startup not found")

    mentors = store.list("mentors")
    if mentor_ids:
        wanted = set(mentor_ids)
        mentors = [mentor for mentor in mentors if mentor["id"] in wanted]

    match_run = store.create(
        "match_runs",
        {
            "startup_id": startup_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        },
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
                "relationship_type": ai["relationship_type"],
                "ai": ai,
                "status": "recommended",
            }
        )

    recommendations.sort(key=lambda item: item["total_score"], reverse=True)
    store.replace_many_for_match_run(match_run["id"], recommendations)
    match_run["recommendations"] = recommendations
    return match_run


def get_match_run(match_run_id):
    match_run = store.get("match_runs", match_run_id)
    if not match_run:
        return None
    match_run["recommendations"] = sorted(
        store.recommendations_for_run(match_run_id),
        key=lambda item: item["total_score"],
        reverse=True,
    )
    return match_run


def score_match(startup, mentor):
    startup_terms = terms_from_startup(startup)
    mentor_terms = terms_from_mentor(mentor)
    overlap = startup_terms.intersection(mentor_terms)

    domain_score = weighted_bool(
        startup.get("domain", "").lower() in lower_list(mentor.get("industries", [])),
        WEIGHTS["domain_expertise"],
        partial=ratio_overlap({startup.get("domain", "").lower()}, mentor_terms),
    )
    challenge_score = int(
        WEIGHTS["business_challenge"]
        * ratio_overlap(
            set(map(str.lower, startup.get("requested_support", []) + startup.get("pain_points", []))),
            mentor_terms,
        )
    )
    stage_score = weighted_bool(
        startup.get("stage", "").lower() in lower_list(mentor.get("preferred_stage", [])),
        WEIGHTS["stage"],
    )
    location_score = weighted_bool(
        "kuala lumpur" in startup.get("location", "").lower()
        and "kuala lumpur" in mentor.get("location", "").lower(),
        WEIGHTS["location"],
        partial=0.55 if mentor.get("location") else 0,
    )
    availability_score = availability_points(mentor.get("availability", ""))
    growth_score = int(WEIGHTS["strategic_growth"] * ratio_overlap(startup_terms, mentor_terms))

    breakdown = {
        "domain_expertise": domain_score,
        "business_challenge": challenge_score,
        "stage": stage_score,
        "location": location_score,
        "availability": availability_score,
        "strategic_growth": growth_score,
    }
    total = min(100, sum(breakdown.values()))

    missing_support = [
        need
        for need in startup.get("requested_support", [])
        if need.lower() not in mentor_terms
    ]
    risks = []
    if location_score < 10:
        risks.append("Mentor is not based directly in Kuala Lumpur.")
    if availability_score < 10:
        risks.append("Limited monthly availability may slow follow-through.")
    if challenge_score < 10:
        risks.append("Only partial coverage of the startup's stated support needs.")

    return {
        "total_score": total,
        "score_breakdown": breakdown,
        "matched_terms": sorted(overlap),
        "support_gaps": missing_support,
        "risks": risks,
    }


def terms_from_startup(startup):
    values = [
        startup.get("domain", ""),
        startup.get("stage", ""),
        startup.get("location", ""),
        startup.get("market", ""),
        *startup.get("pain_points", []),
        *startup.get("goals", []),
        *startup.get("requested_support", []),
    ]
    return normalize_terms(values)


def terms_from_mentor(mentor):
    values = [
        mentor.get("location", ""),
        mentor.get("mentoring_style", ""),
        *mentor.get("expertise", []),
        *mentor.get("industries", []),
        *mentor.get("past_roles", []),
        *mentor.get("preferred_stage", []),
    ]
    return normalize_terms(values)


def normalize_terms(values):
    terms = set()
    for value in values:
        lowered = str(value).lower()
        terms.add(lowered)
        for piece in lowered.replace("/", " ").replace("-", " ").split():
            if len(piece) > 2:
                terms.add(piece)
    return terms


def lower_list(values):
    return [str(value).lower() for value in values]


def ratio_overlap(source_terms, target_terms):
    clean_source = {term for term in source_terms if term}
    if not clean_source:
        return 0
    return min(1, len(clean_source.intersection(target_terms)) / len(clean_source))


def weighted_bool(condition, weight, partial=0):
    if condition:
        return weight
    return int(weight * partial)


def availability_points(value):
    digits = [int(char) for char in value if char.isdigit()]
    hours = digits[0] if digits else 1
    if hours >= 4:
        return WEIGHTS["availability"]
    if hours >= 2:
        return 10
    return 6
