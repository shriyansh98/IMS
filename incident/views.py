"""
Views for the incident APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Incident
from incident import serializers


class IncidentViewSet(viewsets.ModelViewSet):
    """View for manage incident APIs."""
    serializer_class = serializers.IncidentDetailsSerializer
    queryset = Incident.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve incident for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return the serializer class for request"""
        if self.action == 'list':
            return serializers.IncidentSerializer

        return self.serializer_class     

    def  perform_create(self, serializer):
        """create a new incident"""
        serializer.save(user = self.request.user)
        