from django.test import TestCase, override_settings

from rest_framework.test import APIClient

from .ai.evaluation import evaluate_matching
from .matching import create_match_run, score_match
from .seed_data import MENTORS, STARTUPS
from .services.storage import DemoStore, repository


def reset_demo_store():
    repository.store = DemoStore()


class MatchingServiceTests(TestCase):
    def setUp(self):
        reset_demo_store()

    def test_food_operator_scores_higher_than_finance_for_cloud_kitchen(self):
        startup = STARTUPS[0]
        operator = MENTORS[0]
        finance = MENTORS[3]

        operator_score = score_match(startup, operator)["total_score"]
        finance_score = score_match(startup, finance)["total_score"]

        self.assertGreater(operator_score, finance_score)
        self.assertGreaterEqual(operator_score, 70)

    def test_score_breakdown_uses_expected_categories(self):
        result = score_match(STARTUPS[1], MENTORS[2])

        self.assertEqual(
            set(result["score_breakdown"].keys()),
            {
                "domain_expertise",
                "business_challenge",
                "stage",
                "location",
                "availability",
                "strategic_growth",
            },
        )
        self.assertLessEqual(result["total_score"], 100)

    @override_settings(GEMINI_API_KEY="")
    def test_match_run_includes_ai_evidence_fields(self):
        result = create_match_run(STARTUPS[0]["id"])
        recommendation = result["recommendations"][0]

        self.assertIn("confidence", recommendation)
        self.assertIn("recommended_next_action", recommendation)
        self.assertIn("outcome_metric", recommendation)
        self.assertIn("ai_cache_status", recommendation)
        self.assertEqual(recommendation["status"], "recommended")

    def test_evaluation_reports_accuracy(self):
        result = evaluate_matching()

        self.assertEqual(result["benchmark_cases"], 3)
        self.assertGreaterEqual(result["top_1_accuracy"], 0.67)

    @override_settings(GEMINI_API_KEY="", REMEMBER_LLM_RESPONSES=True)
    def test_llm_cache_misses_then_hits_for_same_inputs(self):
        first = create_match_run(STARTUPS[0]["id"])
        second = create_match_run(STARTUPS[0]["id"])

        self.assertEqual(first["recommendations"][0]["ai_cache_status"], "miss")
        self.assertEqual(second["recommendations"][0]["ai_cache_status"], "hit")
        self.assertGreaterEqual(len(repository.store.list("llm_explanations")), 1)

    @override_settings(GEMINI_API_KEY="", REMEMBER_LLM_RESPONSES=True)
    def test_llm_cache_misses_when_profile_changes(self):
        first = create_match_run(STARTUPS[0]["id"])
        startup = repository.store.get("startups", STARTUPS[0]["id"])
        startup["domain"] = f"{startup['domain']} export"
        second = create_match_run(STARTUPS[0]["id"])

        self.assertEqual(first["recommendations"][0]["ai_cache_status"], "miss")
        self.assertEqual(second["recommendations"][0]["ai_cache_status"], "miss")

    @override_settings(GEMINI_API_KEY="", REMEMBER_LLM_RESPONSES=True, GEMINI_MODEL="model-a")
    def test_llm_cache_misses_when_model_changes(self):
        first = create_match_run(STARTUPS[0]["id"])
        with override_settings(GEMINI_MODEL="model-b"):
            second = create_match_run(STARTUPS[0]["id"])

        self.assertEqual(first["recommendations"][0]["ai_cache_status"], "miss")
        self.assertEqual(second["recommendations"][0]["ai_cache_status"], "miss")

    @override_settings(GEMINI_API_KEY="", REMEMBER_LLM_RESPONSES=False)
    def test_llm_cache_disabled_does_not_write_cache(self):
        first = create_match_run(STARTUPS[0]["id"])
        second = create_match_run(STARTUPS[0]["id"])

        self.assertEqual(first["recommendations"][0]["ai_cache_status"], "disabled")
        self.assertEqual(second["recommendations"][0]["ai_cache_status"], "disabled")
        self.assertEqual(repository.store.list("llm_explanations"), [])


class EcosystemApiTests(TestCase):
    def setUp(self):
        reset_demo_store()
        self.client = APIClient()

    def test_dashboard_endpoint_returns_rubric_metrics(self):
        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("entities", response.data)
        self.assertIn("problem_fit", response.data)

    def test_relationship_create_and_list_preserves_lifecycle_fields(self):
        payload = {
            "match_run_id": "demo-run",
            "startup_id": STARTUPS[0]["id"],
            "mentor_id": MENTORS[0]["id"],
            "relationship_type": "primary mentor",
            "status": "approved",
            "notes": "Approved during demo.",
            "next_action": "Book diagnostic call.",
            "review_reason": "",
            "outcome_metric": "Two mentor actions in 30 days.",
        }
        created = self.client.post("/api/relationships/", payload, format="json")
        listed = self.client.get("/api/relationships/")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["next_action"], payload["next_action"])
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)

    @override_settings(GEMINI_API_KEY="", REMEMBER_LLM_RESPONSES=True)
    def test_refresh_recommendation_updates_one_ai_result(self):
        match_run = create_match_run(STARTUPS[0]["id"])
        recommendation = match_run["recommendations"][0]

        response = self.client.post(
            f"/api/recommendations/{recommendation['id']}/refresh-ai/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], recommendation["id"])
        self.assertEqual(response.data["ai_cache_status"], "refresh")
        self.assertIn("ai", response.data)
