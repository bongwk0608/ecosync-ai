from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    MatchRunRequestSerializer,
    MentorSerializer,
    RelationshipSerializer,
    StartupSerializer,
)
from .services.matching import create_match_run, get_match_run
from .services.storage import store


@api_view(["GET"])
def health(_request):
    return Response({"status": "ok", "service": "ecosync-api"})


class CohortListView(APIView):
    def get(self, _request):
        return Response(store.list("cohorts"))


class StartupListCreateView(APIView):
    def get(self, _request):
        return Response(store.list("startups"))

    def post(self, request):
        serializer = StartupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            store.create("startups", serializer.validated_data),
            status=status.HTTP_201_CREATED,
        )


class MentorListCreateView(APIView):
    def get(self, _request):
        return Response(store.list("mentors"))

    def post(self, request):
        serializer = MentorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            store.create("mentors", serializer.validated_data),
            status=status.HTTP_201_CREATED,
        )


class MatchRunCreateView(APIView):
    def post(self, request):
        serializer = MatchRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match_run = create_match_run(**serializer.validated_data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(match_run, status=status.HTTP_201_CREATED)


class MatchRunDetailView(APIView):
    def get(self, _request, match_run_id):
        match_run = get_match_run(match_run_id)
        if not match_run:
            return Response({"detail": "Match run not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(match_run)


class RelationshipCreateView(APIView):
    def post(self, request):
        serializer = RelationshipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        relationship = store.create("relationships", serializer.validated_data)
        return Response(relationship, status=status.HTTP_201_CREATED)
