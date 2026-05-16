from django.urls import path

from . import auth_views
from . import views

urlpatterns = [
    path("health/", views.health),
    path("auth/register/", auth_views.RegisterView.as_view()),
    path("auth/login/", auth_views.LoginView.as_view()),
    path("auth/me/", auth_views.MeView.as_view()),
    path("auth/logout/", auth_views.LogoutView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("evaluation/", views.EvaluationView.as_view()),
    path("cohorts/", views.CohortListView.as_view()),
    path("programs/", views.ProgramListView.as_view()),
    path("partners/", views.PartnerListView.as_view()),
    path("startups/", views.StartupListCreateView.as_view()),
    path("startups/<str:startup_id>/", views.StartupDetailView.as_view()),
    path("mentors/", views.MentorListCreateView.as_view()),
    path("mentors/<str:mentor_id>/", views.MentorDetailView.as_view()),
    path("match-runs/", views.MatchRunCreateView.as_view()),
    path("match-runs/<str:match_run_id>/", views.MatchRunDetailView.as_view()),
    path(
        "recommendations/<str:recommendation_id>/refresh-ai/",
        views.RecommendationRefreshAiView.as_view(),
    ),
    path("relationships/", views.RelationshipCreateView.as_view()),
]
