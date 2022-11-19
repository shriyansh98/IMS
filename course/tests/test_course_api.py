"""
tets for course apis
"""

from decimal import Decimal


from django.contrib.auth import get_user_model

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient



from core.models import Course

from course.serializers import (
    CourseSerializer,
    CourseDetailsSerializer,
    )
from django.urls import reverse

COURSE_URL = reverse('course:course-list')

def details_ulr(course_id):
    """create and return course detail url """
    return reverse('course:course-detail', args = [course_id])

def create_course(user, **params):
    """create and retun a sample course """
    defaults = {

        'title': 'sample course title ',
        'time_completion_hr': 22,
        'price': Decimal('250.50'),
        'description': 'sample description',
        'link' : 'http://edu.com/course/image1/',
        
    }
    defaults.update(params)

    course = Course.objects.create(user = user, **defaults)
    return course

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicCourseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COURSE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED) 

class PrivateCourseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@ex.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)


    def test_retrive_course(self):
        """Test retrieving a list of courses """
        create_course(user= self.user)
        create_course(user = self.user)

        res = self.client.get(COURSE_URL)

        course = Course.objects.all().order_by('-id')
        serializer = CourseSerializer(course, many= True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_course_list_limited_to_user(self):
        """Test list of courses is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_course(user=other_user)
        create_course(user=self.user)

        res = self.client.get(COURSE_URL)

        courses = Course.objects.filter(user=self.user)
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)   

    def test_get_course_detail(self):
        """Test get course detail."""
        course = create_course(user=self.user)

        url = details_ulr(course.id)
        res = self.client.get(url)

        serializer = CourseDetailsSerializer(course)
        self.assertEqual(res.data, serializer.data)

    def test_create_course(self):
        """Test creating a course."""
        payload = {
            'title': 'Sample course',
            'time_completion_hr': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(COURSE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(course, key), value)
        self.assertEqual(course.user, self.user)
         
    def test_partial_update(self):
        """Test partial update of a course."""
        original_link = 'https://example.com/course.pdf'
        course = create_course(
            user=self.user,
            title='Sample course title',
            link=original_link,
        )

        payload = {'title': 'New course title'}
        url = details_ulr(course.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.title, payload['title'])
        self.assertEqual(course.link, original_link)
        self.assertEqual(course.user, self.user)

    def test_full_update(self):
        """Test full update of course."""
        course = create_course(
            user=self.user,
            title='Sample course title',
            link='https://exmaple.com/course.pdf',
            description='Sample course description.',
        )

        payload = {
            'title': 'New course title',
            'link': 'https://example.com/new-course.pdf',
            'description': 'New course description',
            'time_completion_hr': 10,
            'price': Decimal('2.50'),
        }
        url = details_ulr(course.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(course, k), v)
        self.assertEqual(course.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the course user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        course = create_course(user=self.user)

        payload = {'user': new_user.id}
        url = details_ulr(course.id)
        self.client.patch(url, payload)

        course.refresh_from_db()
        self.assertEqual(course.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a course successful."""
        course = create_course(user=self.user)

        url = details_ulr(course.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users course gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        course = create_course(user=new_user)

        url = details_ulr(course.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Course.objects.filter(id=course.id).exists())
