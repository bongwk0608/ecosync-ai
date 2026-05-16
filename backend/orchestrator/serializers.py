from rest_framework import serializers


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
    match_run_id = serializers.CharField()
    startup_id = serializers.CharField()
    mentor_id = serializers.CharField()
    relationship_type = serializers.ChoiceField(
        choices=["primary mentor", "specialist mentor", "advisor", "not recommended"]
    )
    status = serializers.ChoiceField(choices=["approved", "rejected", "review"])
    notes = serializers.CharField(required=False, allow_blank=True)
