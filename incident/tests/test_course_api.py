"""
tets for incident apis
"""

from decimal import Decimal


from django.contrib.auth import get_user_model

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient



from core.models import Incident

from incident.serializers import (
    IncidentSerializer,
    IncidentDetailsSerializer,
    )
from django.urls import reverse

INCIDENT_URL = reverse('incident:incident-list')

def details_ulr(incident_id):
    """create and return incident detail url """
    return reverse('incident:incident-detail', args = [incident_id])

def create_incident(user, **params):
    """create and retun a sample incident """
    defaults = {

        'title': 'sample incident title ',
        'time_completion_hr': 22,
        'price': Decimal('250.50'),
        'description': 'sample description',
        'link' : 'http://edu.com/incident/image1/',
        
    }
    defaults.update(params)

    incident = Incident.objects.create(user = user, **defaults)
    return incident

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicIncidentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INCIDENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED) 

class PrivateIncidentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@ex.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)


    def test_retrive_incident(self):
        """Test retrieving a list of incidents """
        create_incident(user= self.user)
        create_incident(user = self.user)

        res = self.client.get(INCIDENT_URL)

        incident = Incident.objects.all().order_by('-id')
        serializer = IncidentSerializer(incident, many= True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_incident_list_limited_to_user(self):
        """Test list of incidents is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_incident(user=other_user)
        create_incident(user=self.user)

        res = self.client.get(INCIDENT_URL)

        incidents = Incident.objects.filter(user=self.user)
        serializer = IncidentSerializer(incidents, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)   

    def test_get_incident_detail(self):
        """Test get incident detail."""
        incident = create_incident(user=self.user)

        url = details_ulr(incident.id)
        res = self.client.get(url)

        serializer = IncidentDetailsSerializer(incident)
        self.assertEqual(res.data, serializer.data)

    def test_create_incident(self):
        """Test creating a incident."""
        payload = {
            'title': 'Sample incident',
            'time_completion_hr': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(INCIDENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        incident = Incident.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(incident, key), value)
        self.assertEqual(incident.user, self.user)
         
    def test_partial_update(self):
        """Test partial update of a incident."""
        original_link = 'https://example.com/incident.pdf'
        incident = create_incident(
            user=self.user,
            title='Sample incident title',
            link=original_link,
        )

        payload = {'title': 'New incident title'}
        url = details_ulr(incident.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        incident.refresh_from_db()
        self.assertEqual(incident.title, payload['title'])
        self.assertEqual(incident.link, original_link)
        self.assertEqual(incident.user, self.user)

    def test_full_update(self):
        """Test full update of incident."""
        incident = create_incident(
            user=self.user,
            title='Sample incident title',
            link='https://exmaple.com/incident.pdf',
            description='Sample incident description.',
        )

        payload = {
            'title': 'New incident title',
            'link': 'https://example.com/new-incident.pdf',
            'description': 'New incident description',
            'time_completion_hr': 10,
            'price': Decimal('2.50'),
        }
        url = details_ulr(incident.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        incident.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(incident, k), v)
        self.assertEqual(incident.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the incident user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        incident = create_incident(user=self.user)

        payload = {'user': new_user.id}
        url = details_ulr(incident.id)
        self.client.patch(url, payload)

        incident.refresh_from_db()
        self.assertEqual(incident.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a incident successful."""
        incident = create_incident(user=self.user)

        url = details_ulr(incident.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Incident.objects.filter(id=incident.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users incident gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        incident = create_incident(user=new_user)

        url = details_ulr(incident.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Incident.objects.filter(id=incident.id).exists())
