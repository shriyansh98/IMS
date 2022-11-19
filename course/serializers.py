"""
Serializers for course APIs
"""
from rest_framework import serializers

from core.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for courses."""

    class Meta:
        model = Course
        fields = ['id', 'title', 'time_completion_hr', 'price', 'link']
        read_only_fields = ['id']

class CourseDetailsSerializer(CourseSerializer):
    """serializer for course detail view """

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['description']



      