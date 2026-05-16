from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health),
    path("dashboard/", views.DashboardView.as_view()),
    path("evaluation/", views.EvaluationView.as_view()),
    path("cohorts/", views.CohortListView.as_view()),
    path("programs/", views.ProgramListView.as_view()),
    path("partners/", views.PartnerListView.as_view()),
    path("startups/", views.StartupListCreateView.as_view()),
    path("mentors/", views.MentorListCreateView.as_view()),
    path("match-runs/", views.MatchRunCreateView.as_view()),
    path("match-runs/<str:match_run_id>/", views.MatchRunDetailView.as_view()),
    path(
        "recommendations/<str:recommendation_id>/refresh-ai/",
        views.RecommendationRefreshAiView.as_view(),
    ),
    path("relationships/", views.RelationshipCreateView.as_view()),
]
