"""
URL mappings for the incident app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from incident import views


router = DefaultRouter()
router.register('incidents', views.IncidentViewSet)

app_name = 'incident'

urlpatterns = [
    path('', include(router.urls)),
]