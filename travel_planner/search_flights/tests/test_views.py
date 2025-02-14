from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta
from search_flights.forms import FlightSearchForm

class SearchFlightsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('search_flights')

    def test_get_request(self):
        """Test GET request to the search_flights view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], FlightSearchForm)

    def test_post_request_valid_data(self):
        """Test POST request with valid form data."""
        self.client.login(username='testuser', password='testpassword')
        data = {
            'from_location': 'New York',
            'to_location': 'Los Angeles',
            'departure_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'adults': 2,
            'children': 1,
            'cabin_class': 'economy'
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('flights', response.context)
        self.assertIn('form', response.context)

    def test_post_request_invalid_data(self):
        """Test POST request with invalid form data."""
        self.client.login(username='testuser', password='testpassword')
        data = {
            'from_location': '',
            'to_location': 'Los Angeles',
            'departure_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'adults': 2,
            'children': 1,
            'cabin_class': 'economy'
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context)
        self.assertIn('form', response.context)

    def test_post_request_past_dates(self):
        """Test POST request with past dates."""
        self.client.login(username='testuser', password='testpassword')
        data = {
            'from_location': 'New York',
            'to_location': 'Los Angeles',
            'departure_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'return_date': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            'adults': 2,
            'children': 1,
            'cabin_class': 'economy'
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_message'], "Form is invalid. Please check the inputs.")

    def test_api_error_handling(self):
        """Test error handling when the API fails."""
        self.client.login(username='testuser', password='testpassword')
        data = {
            'from_location': 'Invalid Location',
            'to_location': 'Los Angeles',
            'departure_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'adults': 2,
            'children': 1,
            'cabin_class': 'economy'
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context)
        self.assertIn('Form is invalid. Please check the inputs.', response.context['error_message'])