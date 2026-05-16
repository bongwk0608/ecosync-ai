from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    MatchRunRequestSerializer,
    MentorSerializer,
    RelationshipSerializer,
    StartupSerializer,
)
from .ai.evaluation import evaluate_matching
from .matching import create_match_run, get_match_run, refresh_recommendation_ai
from .permissions import IsApprovedUser
from .services.dashboard import dashboard_summary
from .services.storage import repository


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    return Response({"status": "ok", "service": "ecosync-api"})


class CohortListView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_cohorts())


class DashboardView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(dashboard_summary())


class EvaluationView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(evaluate_matching())


class ProgramListView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_programs())


class PartnerListView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_partners())


class StartupListCreateView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_startups())

    def post(self, request):
        serializer = StartupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = add_audit_fields(serializer.validated_data, request.user)
        return Response(
            repository.create_startup(payload),
            status=status.HTTP_201_CREATED,
        )


class StartupDetailView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request, startup_id):
        startup = repository.get_startup(startup_id)
        if not startup:
            return Response({"detail": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(startup)

    def patch(self, request, startup_id):
        return self._save(request, startup_id, partial=True)

    def put(self, request, startup_id):
        return self._save(request, startup_id, partial=False)

    def delete(self, request, startup_id):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete datasets."}, status=status.HTTP_403_FORBIDDEN)
        deleted = repository.delete_startup(startup_id)
        if not deleted:
            return Response({"detail": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _save(self, request, startup_id, partial):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can update datasets."}, status=status.HTTP_403_FORBIDDEN)
        existing = repository.get_startup(startup_id)
        if not existing:
            return Response({"detail": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StartupSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        payload = {**existing, **serializer.validated_data}
        payload = update_audit_fields(payload, request.user)
        return Response(repository.update_startup(startup_id, payload))


class MentorListCreateView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_mentors())

    def post(self, request):
        serializer = MentorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = add_audit_fields(serializer.validated_data, request.user)
        return Response(
            repository.create_mentor(payload),
            status=status.HTTP_201_CREATED,
        )


class MentorDetailView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request, mentor_id):
        mentor = repository.get_mentor(mentor_id)
        if not mentor:
            return Response({"detail": "Mentor not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(mentor)

    def patch(self, request, mentor_id):
        return self._save(request, mentor_id, partial=True)

    def put(self, request, mentor_id):
        return self._save(request, mentor_id, partial=False)

    def delete(self, request, mentor_id):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete datasets."}, status=status.HTTP_403_FORBIDDEN)
        deleted = repository.delete_mentor(mentor_id)
        if not deleted:
            return Response({"detail": "Mentor not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _save(self, request, mentor_id, partial):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can update datasets."}, status=status.HTTP_403_FORBIDDEN)
        existing = repository.get_mentor(mentor_id)
        if not existing:
            return Response({"detail": "Mentor not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MentorSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        payload = {**existing, **serializer.validated_data}
        payload = update_audit_fields(payload, request.user)
        return Response(repository.update_mentor(mentor_id, payload))


class MatchRunCreateView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request):
        serializer = MatchRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match_run = create_match_run(
                **serializer.validated_data,
                created_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(match_run, status=status.HTTP_201_CREATED)


class MatchRunDetailView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request, match_run_id):
        match_run = get_match_run(match_run_id)
        if not match_run:
            return Response({"detail": "Match run not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(match_run)


class RecommendationRefreshAiView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, _request, recommendation_id):
        try:
            recommendation = refresh_recommendation_ai(recommendation_id)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        if not recommendation:
            return Response(
                {"detail": "Recommendation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(recommendation)


class RelationshipCreateView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, _request):
        return Response(repository.list_relationships())

    def post(self, request):
        serializer = RelationshipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = add_audit_fields(serializer.validated_data, request.user)
        payload.setdefault("lifecycle_status", payload.get("status", "recommended"))
        relationship = repository.create_relationship(payload)
        return Response(relationship, status=status.HTTP_201_CREATED)


def add_audit_fields(payload, user):
    audited = dict(payload)
    audited["created_by_user_id"] = user.id
    audited["created_by_username"] = user.username
    audited["updated_by_user_id"] = user.id
    return audited


def update_audit_fields(payload, user):
    audited = dict(payload)
    audited["updated_by_user_id"] = user.id
    return audited
