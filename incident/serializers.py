"""
Serializers for incident APIs
"""
from rest_framework import serializers

from core.models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer for incidents."""

    class Meta:
        model = Incident
        fields = ['Report_name', 'priority', 'date_time', 'status']
        read_only_fields = ['Report_name']

class IncidentDetailsSerializer(IncidentSerializer):
    """serializer for incident detail view """

    class Meta(IncidentSerializer.Meta):
        fields = IncidentSerializer.Meta.fields + ['description']



      