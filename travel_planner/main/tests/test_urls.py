from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class MainURLsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_homepage_url_resolves(self):
        """Test that the homepage URL is accessible and returns a 200 status."""
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_authenticated_user(self):
        """Test homepage URL for authenticated users."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)