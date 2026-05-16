from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health),
    path("cohorts/", views.CohortListView.as_view()),
    path("startups/", views.StartupListCreateView.as_view()),
    path("mentors/", views.MentorListCreateView.as_view()),
    path("match-runs/", views.MatchRunCreateView.as_view()),
    path("match-runs/<str:match_run_id>/", views.MatchRunDetailView.as_view()),
    path("relationships/", views.RelationshipCreateView.as_view()),
]
