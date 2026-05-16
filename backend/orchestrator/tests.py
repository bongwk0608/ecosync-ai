from django.test import TestCase

from rest_framework.test import APIClient

from .ai.evaluation import evaluate_matching
from .matching import create_match_run, score_match
from .seed_data import MENTORS, STARTUPS


class MatchingServiceTests(TestCase):
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

    def test_match_run_includes_ai_evidence_fields(self):
        result = create_match_run(STARTUPS[0]["id"])
        recommendation = result["recommendations"][0]

        self.assertIn("confidence", recommendation)
        self.assertIn("recommended_next_action", recommendation)
        self.assertIn("outcome_metric", recommendation)
        self.assertEqual(recommendation["status"], "recommended")

    def test_evaluation_reports_accuracy(self):
        result = evaluate_matching()

        self.assertEqual(result["benchmark_cases"], 3)
        self.assertGreaterEqual(result["top_1_accuracy"], 0.67)


class EcosystemApiTests(TestCase):
    def setUp(self):
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
