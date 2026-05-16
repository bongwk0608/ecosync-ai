from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.core import mail
from django.test import RequestFactory
from django.test import TestCase, override_settings

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .ai.evaluation import evaluate_matching
from .matching import create_match_run, score_match
from .models import UserProfile
from .admin import UserProfileAdmin
from .seed_data import MENTORS, STARTUPS
from .services.storage import DemoStore, repository


def reset_demo_store():
    repository.store = DemoStore()


def create_approved_user(username="demo-user", is_staff=False):
    user = get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="StrongPass123!",
        is_active=True,
        is_staff=is_staff,
    )
    UserProfile.objects.create(
        user=user,
        full_name="Demo User",
        organization="EcoSync",
        role="admin_operator" if is_staff else "program_manager",
        approval_status="approved",
    )
    token, _created = Token.objects.get_or_create(user=user)
    return user, token


def create_profile(username, status="pending", is_staff=False):
    user = get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="StrongPass123!",
        is_active=status == "approved",
        is_staff=is_staff,
    )
    profile = UserProfile.objects.create(
        user=user,
        full_name=f"{username.title()} User",
        organization="EcoSync",
        role="admin_operator" if is_staff else "program_manager",
        approval_status=status,
    )
    return user, profile


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
        self.user, self.token = create_approved_user()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

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

    def test_unauthenticated_user_cannot_access_dashboard(self):
        self.client.credentials()
        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 401)

    def test_approved_user_can_add_startup_dataset(self):
        payload = {
            "name": "Demo Retail Lab",
            "domain": "retail SME",
            "location": "Kuala Lumpur",
            "stage": "validation",
            "pain_points": ["conversion"],
            "goals": ["increase sales"],
            "requested_support": ["digital marketing"],
            "founder_notes": "Needs practical help.",
        }
        response = self.client.post("/api/startups/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by_username"], self.user.username)

    def test_approved_user_cannot_delete_dataset(self):
        response = self.client.delete(f"/api/startups/{STARTUPS[0]['id']}/")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_and_delete_dataset(self):
        admin_user, admin_token = create_approved_user("admin-user", is_staff=True)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        updated = self.client.patch(
            f"/api/startups/{STARTUPS[0]['id']}/",
            {"name": "Updated Startup"},
            format="json",
        )
        deleted = self.client.delete(f"/api/startups/{STARTUPS[0]['id']}/")

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["name"], "Updated Startup")
        self.assertEqual(updated.data["updated_by_user_id"], admin_user.id)
        self.assertEqual(deleted.status_code, 204)


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_requires_compulsory_fields(self):
        response = self.client.post("/api/auth/register/", {"username": "missing"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_registration_creates_inactive_pending_user(self):
        payload = {
            "username": "pending-user",
            "email": "pending@example.com",
            "password": "StrongPass123!",
            "full_name": "Pending User",
            "organization": "Pending Org",
            "role": "program_manager",
        }
        response = self.client.post("/api/auth/register/", payload, format="json")
        user = get_user_model().objects.get(username="pending-user")

        self.assertEqual(response.status_code, 201)
        self.assertFalse(user.is_active)
        self.assertEqual(user.ecosync_profile.approval_status, "pending")

    def test_pending_user_cannot_login(self):
        user = get_user_model().objects.create_user(
            username="pending",
            email="pending@example.com",
            password="StrongPass123!",
            is_active=False,
        )
        UserProfile.objects.create(
            user=user,
            full_name="Pending User",
            organization="EcoSync",
            role="program_manager",
            approval_status="pending",
        )

        response = self.client.post(
            "/api/auth/login/",
            {"username": "pending", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["approval_status"], "pending")

    def test_approved_user_can_login_and_get_token(self):
        create_approved_user("approved")

        response = self.client.post(
            "/api/auth/login/",
            {"username": "approved", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["approval_status"], "approved")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_registration_result_email_can_be_sent(self):
        user, _token = create_approved_user("email-user")
        profile = user.ecosync_profile

        from .services.email import send_registration_result_email

        sent = send_registration_result_email(profile)

        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_status_change_email_covers_approved_declined_and_pending(self):
        _user, profile = create_profile("status-user", status="pending")

        from .services.email import send_account_status_change_email

        profile.approval_status = "approved"
        approved_sent = send_account_status_change_email(profile, previous_status="pending")
        profile.approval_status = "declined"
        declined_sent = send_account_status_change_email(profile, previous_status="approved")
        profile.approval_status = "pending"
        pending_sent = send_account_status_change_email(profile, previous_status="declined")

        self.assertTrue(approved_sent)
        self.assertTrue(declined_sent)
        self.assertTrue(pending_sent)
        self.assertEqual(len(mail.outbox), 3)
        self.assertIn("account approved", mail.outbox[0].subject)
        self.assertIn("account declined", mail.outbox[1].subject)
        self.assertIn("pending review", mail.outbox[2].subject)
        self.assertIn("declined to pending", mail.outbox[2].body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_admin_bulk_action_skips_unchanged_statuses(self):
        admin_user, _admin_profile = create_profile("bulk-admin", status="approved", is_staff=True)
        _changed_user, changed_profile = create_profile("bulk-changed", status="pending")
        _skipped_user, skipped_profile = create_profile("bulk-skipped", status="approved")
        request = RequestFactory().post("/")
        request.user = admin_user
        request._messages = []
        model_admin = UserProfileAdmin(UserProfile, AdminSite())
        model_admin.message_user = lambda *args, **kwargs: None

        model_admin.approve_applications(
            request,
            UserProfile.objects.filter(id__in=[changed_profile.id, skipped_profile.id]),
        )

        changed_profile.refresh_from_db()
        skipped_profile.refresh_from_db()
        self.assertEqual(changed_profile.approval_status, "approved")
        self.assertEqual(skipped_profile.approval_status, "approved")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("pending to approved", mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_resend_action_sends_current_status_email(self):
        admin_user, _admin_profile = create_profile("resend-admin", status="approved", is_staff=True)
        _user, profile = create_profile("resend-user", status="declined")
        request = RequestFactory().post("/")
        request.user = admin_user
        request._messages = []
        model_admin = UserProfileAdmin(UserProfile, AdminSite())
        model_admin.message_user = lambda *args, **kwargs: None

        model_admin.resend_result_email(request, UserProfile.objects.filter(id=profile.id))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("account declined", mail.outbox[0].subject)
