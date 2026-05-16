from __future__ import annotations

import json

from django.conf import settings


def explain_match(startup, mentor, deterministic_result):
    if not settings.GEMINI_API_KEY:
        return demo_explanation(startup, mentor, deterministic_result)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(build_prompt(startup, mentor, deterministic_result))
        text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(text)
        explanation = validate_explanation(parsed, startup, mentor, deterministic_result)
        explanation["ai_mode"] = "gemini"
        explanation["model"] = settings.GEMINI_MODEL
        return explanation
    except Exception:
        return demo_explanation(startup, mentor, deterministic_result)


def build_prompt(startup, mentor, deterministic_result):
    return json.dumps(
        {
            "instruction": (
                "Return strict JSON only. Recommend whether this mentor-startup ecosystem "
                "relationship should be formed. Include startup_summary, mentor_summary, "
                "rationale, risks, support_gaps, recommended_next_action, relationship_type, "
                "confidence, outcome_metric, ethical_consideration, and explanation_quality_checks."
            ),
            "startup": startup,
            "mentor": mentor,
            "deterministic_score": deterministic_result,
            "relationship_type_choices": [
                "primary mentor",
                "specialist mentor",
                "advisor",
                "partner referral",
                "not recommended",
            ],
            "confidence_choices": ["high", "medium", "low"],
        }
    )


def validate_explanation(parsed, startup, mentor, deterministic_result):
    fallback = demo_explanation(startup, mentor, deterministic_result)
    allowed_types = {
        "primary mentor",
        "specialist mentor",
        "advisor",
        "partner referral",
        "not recommended",
    }
    allowed_confidence = {"high", "medium", "low"}
    return {
        "startup_summary": parsed.get("startup_summary") or fallback["startup_summary"],
        "mentor_summary": parsed.get("mentor_summary") or fallback["mentor_summary"],
        "rationale": parsed.get("rationale") or fallback["rationale"],
        "risks": parsed.get("risks") if isinstance(parsed.get("risks"), list) else fallback["risks"],
        "support_gaps": parsed.get("support_gaps")
        if isinstance(parsed.get("support_gaps"), list)
        else fallback["support_gaps"],
        "recommended_next_action": parsed.get("recommended_next_action")
        or fallback["recommended_next_action"],
        "relationship_type": parsed.get("relationship_type")
        if parsed.get("relationship_type") in allowed_types
        else fallback["relationship_type"],
        "confidence": parsed.get("confidence")
        if parsed.get("confidence") in allowed_confidence
        else fallback["confidence"],
        "outcome_metric": parsed.get("outcome_metric") or fallback["outcome_metric"],
        "ethical_consideration": parsed.get("ethical_consideration")
        or fallback["ethical_consideration"],
        "explanation_quality_checks": parsed.get("explanation_quality_checks")
        if isinstance(parsed.get("explanation_quality_checks"), list)
        else fallback["explanation_quality_checks"],
        "ai_mode": "demo-fallback",
        "model": "deterministic-fallback",
    }


def demo_explanation(startup, mentor, deterministic_result):
    total = deterministic_result["total_score"]
    if total >= 78:
        relationship_type = "primary mentor"
    elif total >= 62:
        relationship_type = "specialist mentor"
    elif total >= 45:
        relationship_type = "advisor"
    else:
        relationship_type = "not recommended"

    matched_needs = sorted(
        set(startup.get("requested_support", []))
        .union(startup.get("pain_points", []))
        .intersection(set(mentor.get("expertise", [])))
    )
    if not matched_needs:
        matched_needs = deterministic_result.get("matched_terms", [])[:3]

    return {
        "startup_summary": (
            f"{startup['name']} is a {startup['stage']} {startup['domain']} SME in "
            f"{startup['location']} serving {startup.get('market', 'its target market')}."
        ),
        "mentor_summary": (
            f"{mentor['name']} brings {', '.join(mentor.get('expertise', [])[:3])} "
            f"experience with a {mentor.get('mentoring_style', 'practical')} style."
        ),
        "rationale": (
            f"The fit is strongest around {', '.join(matched_needs) or startup['domain']}. "
            f"The deterministic score is {total}/100 with useful overlap in domain, "
            "business needs, stage context, and ecosystem follow-through."
        ),
        "risks": deterministic_result.get("risks", []),
        "support_gaps": deterministic_result.get("support_gaps", []),
        "recommended_next_action": (
            "Schedule a 45-minute diagnostic session and agree on two measurable actions "
            "for the next month."
        ),
        "relationship_type": relationship_type,
        "confidence": "high" if total >= 75 else "medium" if total >= 55 else "low",
        "outcome_metric": "Two completed mentor actions and one tracked business KPI within 30 days.",
        "ethical_consideration": (
            "Keep the program manager in the loop and allow humans to override AI recommendations."
        ),
        "explanation_quality_checks": [
            "uses deterministic score",
            "names relationship risks",
            "keeps human approval required",
        ],
        "ai_mode": "demo-fallback",
        "model": "deterministic-fallback",
    }
