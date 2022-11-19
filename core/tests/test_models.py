"""
tests for models
"""
from decimal import Decimal
from time import time
from turtle import title

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models




class ModelTests(TestCase):
    """TEST Models"""

    def test_create_user_with_email_successful(self):
        """Testing creating a user with an email is successful"""

        email = 'test@ex.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email= email,
            password = password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalizied(self):
        """Test email os normalised for new users"""
        sample_emails = [
            ['test1@EXAMPLE.COM','test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],

        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)    

    def test_new_user_without_email_raises_error(self):
        """test that creating a user without email raises a Value error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')


    def test_create_superuser(self):
        """test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_create_course(self):
        """test creating a course is successful"""
        user = get_user_model().objects.create_user(
            'test@ex.com',
            'testpass123',
        )    

        course = models.Course.objects.create(
            user= user,
            title= 'sample course name',
            time_completion_hr = 5,
            price = Decimal('350.50'),
            description = 'Sample description of the course',

        )

        self.assertEqual(str(course), course.title)
        