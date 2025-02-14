from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from user_trips.models import MyTrip
from destinations.views import get_destinations_by_category

class HomepageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')

        # Create trips
        self.past_trip = MyTrip.objects.create(
            user=self.user, destination="Paris",
            start_date=timezone.now().date() - timedelta(days=10),
            end_date=timezone.now().date() - timedelta(days=5)
        )

        self.future_trip = MyTrip.objects.create(
            user=self.user, destination="London",
            start_date=timezone.now().date() + timedelta(days=2),
            end_date=timezone.now().date() + timedelta(days=7)
        )

        self.shared_trip = MyTrip.objects.create(
            user=self.other_user, destination="Rome",
            start_date=timezone.now().date() + timedelta(days=3),
            end_date=timezone.now().date() + timedelta(days=8)
        )
        self.shared_trip.shared_with.add(self.user)

    @patch('destinations.views.get_destinations_by_category')
    def test_homepage_anonymous_user(self, mock_get_destinations):
        """Test homepage renders correctly for anonymous users."""
        mock_get_destinations.return_value = ["Destination1", "Destination2"]
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/homepage.html')
        self.assertIn('destinations', response.context)
        self.assertNotIn('current_future_trips', response.context)

    @patch('destinations.views.get_destinations_by_category')
    def test_homepage_authenticated_user(self, mock_get_destinations):
        """Test homepage displays trips correctly for authenticated users."""
        mock_get_destinations.return_value = ["Destination1", "Destination2"]
        self.client.login(username='testuser', password='password')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/homepage.html')
        self.assertIn('current_future_trips', response.context)
        
        trips = response.context['current_future_trips']
        self.assertIn(self.future_trip, trips)
        self.assertIn(self.shared_trip, trips)
        self.assertNotIn(self.past_trip, trips)