from ..domain import SCORE_WEIGHTS
from .terms import lower_list, ratio_overlap, terms_from_mentor, terms_from_startup


def score_match(startup, mentor):
    startup_terms = terms_from_startup(startup)
    mentor_terms = terms_from_mentor(mentor)
    overlap = startup_terms.intersection(mentor_terms)

    domain_score = weighted_bool(
        startup.get("domain", "").lower() in lower_list(mentor.get("industries", [])),
        SCORE_WEIGHTS["domain_expertise"],
        partial=ratio_overlap({startup.get("domain", "").lower()}, mentor_terms),
    )
    challenge_score = int(
        SCORE_WEIGHTS["business_challenge"]
        * ratio_overlap(
            set(map(str.lower, startup.get("requested_support", []) + startup.get("pain_points", []))),
            mentor_terms,
        )
    )
    stage_score = weighted_bool(
        startup.get("stage", "").lower() in lower_list(mentor.get("preferred_stage", [])),
        SCORE_WEIGHTS["stage"],
    )
    location_score = weighted_bool(
        "kuala lumpur" in startup.get("location", "").lower()
        and "kuala lumpur" in mentor.get("location", "").lower(),
        SCORE_WEIGHTS["location"],
        partial=0.55 if mentor.get("location") else 0,
    )
    availability_score = availability_points(mentor.get("availability", ""))
    growth_score = int(SCORE_WEIGHTS["strategic_growth"] * ratio_overlap(startup_terms, mentor_terms))

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


def weighted_bool(condition, weight, partial=0):
    if condition:
        return weight
    return int(weight * partial)


def availability_points(value):
    digits = [int(char) for char in value if char.isdigit()]
    hours = digits[0] if digits else 1
    if hours >= 4:
        return SCORE_WEIGHTS["availability"]
    if hours >= 2:
        return 10
    return 6
