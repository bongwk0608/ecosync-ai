from statistics import mean

from ..matching.scoring import score_match
from ..services.storage import repository


BENCHMARK_CASES = [
    {
        "startup_id": "startup-nasi-next",
        "expected_top_mentor_id": "mentor-aisha",
        "reason": "Cloud kitchen operations and unit economics need an operator mentor.",
    },
    {
        "startup_id": "startup-halalbite",
        "expected_top_mentor_id": "mentor-farid",
        "reason": "Halal certification and supply chain needs require compliance depth.",
    },
    {
        "startup_id": "startup-batikdesk",
        "expected_top_mentor_id": "mentor-mei",
        "reason": "Pricing and planning needs should rank the finance mentor highly.",
    },
]

CONFIDENCE_POINTS = {"high": 1, "medium": 0.65, "low": 0.35}


def evaluate_matching():
    mentors = repository.list_mentors()
    cases = []
    correct = 0
    confidence_values = []
    mode_counts = {"gemini": 0, "demo-fallback": 0}

    for case in BENCHMARK_CASES:
        startup = repository.get_startup(case["startup_id"])
        ranked = sorted(
            (
                {
                    "mentor_id": mentor["id"],
                    "mentor_name": mentor["name"],
                    "score": score_match(startup, mentor)["total_score"],
                }
                for mentor in mentors
            ),
            key=lambda item: item["score"],
            reverse=True,
        )
        actual = ranked[0] if ranked else {}
        passed = actual.get("mentor_id") == case["expected_top_mentor_id"]
        correct += 1 if passed else 0
        confidence = "high" if actual.get("score", 0) >= 75 else "medium" if actual.get("score", 0) >= 55 else "low"
        confidence_values.append(CONFIDENCE_POINTS[confidence])
        mode_counts["demo-fallback"] += 1
        cases.append(
            {
                **case,
                "startup_name": startup["name"],
                "expected_top_mentor": repository.get_mentor(case["expected_top_mentor_id"])["name"],
                "actual_top_mentor_id": actual.get("mentor_id"),
                "actual_top_mentor": actual.get("mentor_name"),
                "actual_score": actual.get("score"),
                "confidence": confidence,
                "passed": passed,
            }
        )

    total = len(BENCHMARK_CASES)
    return {
        "benchmark_cases": total,
        "top_1_accuracy": round(correct / total, 2) if total else 0,
        "average_confidence": round(mean(confidence_values), 2) if confidence_values else 0,
        "mode_counts": mode_counts,
        "cases": cases,
    }
