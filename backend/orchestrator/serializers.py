from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .domain import RELATIONSHIP_STATUSES, RELATIONSHIP_TYPES
from .models import UserProfile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    full_name = serializers.CharField(max_length=150)
    organization = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=[choice[0] for choice in UserProfile.ROLE_CHOICES])

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already registered.")
        return value

    def validate_email(self, value):
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class StartupSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(max_length=120)
    domain = serializers.CharField(max_length=80)
    location = serializers.CharField(max_length=120)
    stage = serializers.CharField(max_length=60)
    pain_points = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    goals = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    revenue_range = serializers.CharField(max_length=80, required=False, allow_blank=True)
    team_size = serializers.IntegerField(min_value=1, required=False)
    market = serializers.CharField(max_length=120, required=False, allow_blank=True)
    requested_support = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    founder_notes = serializers.CharField(required=False, allow_blank=True)


class MentorSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(max_length=120)
    expertise = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    industries = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    location = serializers.CharField(max_length=120)
    languages = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    availability = serializers.CharField(max_length=80)
    past_roles = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    mentoring_style = serializers.CharField(max_length=120)
    preferred_stage = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class MatchRunRequestSerializer(serializers.Serializer):
    startup_id = serializers.CharField()
    mentor_ids = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )


class RelationshipSerializer(serializers.Serializer):
    match_run_id = serializers.CharField(required=False, allow_blank=True)
    startup_id = serializers.CharField()
    mentor_id = serializers.CharField()
    relationship_type = serializers.ChoiceField(choices=RELATIONSHIP_TYPES)
    status = serializers.ChoiceField(choices=RELATIONSHIP_STATUSES)
    notes = serializers.CharField(required=False, allow_blank=True)
    next_action = serializers.CharField(required=False, allow_blank=True)
    review_reason = serializers.CharField(required=False, allow_blank=True)
    outcome_metric = serializers.CharField(required=False, allow_blank=True)
    lifecycle_status = serializers.ChoiceField(
        choices=RELATIONSHIP_STATUSES, required=False
    )
