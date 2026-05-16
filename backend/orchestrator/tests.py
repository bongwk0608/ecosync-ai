from django.test import TestCase

from .seed_data import MENTORS, STARTUPS
from .services.matching import score_match


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
