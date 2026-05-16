from .storage import repository


def dashboard_summary():
    relationships = repository.list_relationships()
    recommendations = repository.list_recommendations()
    active_statuses = {"approved", "active", "completed"}
    review_statuses = {"review", "needs_review"}

    return {
        "cohorts": len(repository.list_cohorts()),
        "entities": {
            "startups": len(repository.list_startups()),
            "mentors": len(repository.list_mentors()),
            "partners": len(repository.list_partners()),
            "programs": len(repository.list_programs()),
        },
        "recommendations": len(recommendations),
        "relationships": {
            "total": len(relationships),
            "approved": count_by_status(relationships, {"approved"}),
            "active": count_by_status(relationships, active_statuses),
            "review_needed": count_by_status(relationships, review_statuses),
            "rejected": count_by_status(relationships, {"rejected"}),
        },
        "problem_fit": {
            "manual_coordination_reduced": "Ranked AI recommendations replace spreadsheet triage.",
            "relationships_first_class": "Recommendations become trackable relationship records.",
            "reuse_signal": "Profiles and decisions can be reused across cohorts and programs.",
        },
    }


def count_by_status(items, statuses):
    return sum(1 for item in items if item.get("status") in statuses)
