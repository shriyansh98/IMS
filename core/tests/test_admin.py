"""
test for django admin modification
"""
import email
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client



class AdminSitetests(TestCase):
    """test for django admin"""

    def setUp(self):
        """create user and email """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'adminuser@ex.com',
            password = 'testpass123',
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@ex.com',
            password = 'testpass123',
            name = 'test user',
        )
        
        
    def test_users_list(self):
        """test that users are listed in page """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)


    def test_edit_user_page(self):
        """test the edit user page work""" 
        url = reverse('admin:core_user_change',args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)   


    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
