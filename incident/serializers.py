"""
Serializers for incident APIs
"""
from rest_framework import serializers

from core.models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer for incidents."""

    class Meta:
        model = Incident
        fields = ['id', 'title', 'time_completion_hr', 'price', 'link']
        read_only_fields = ['id']

class IncidentDetailsSerializer(IncidentSerializer):
    """serializer for incident detail view """

    class Meta(IncidentSerializer.Meta):
        fields = IncidentSerializer.Meta.fields + ['description']



      