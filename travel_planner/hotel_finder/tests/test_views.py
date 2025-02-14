import requests
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from datetime import date
from hotel_finder.forms import HotelSearchForm

class SearchHotelsViewTests(TestCase):
    def setUp(self):
        self.url = reverse('search_hotels')
        self.data = {
            'destination': 'Paris',
            'arrival_date': '2025-05-01',
            'departure_date': '2025-05-07',
            'adults': 2,
            'room_qty': 1,
            'children_age': '0'
        }

    @patch('hotel_finder.views.requests.get')
    def test_search_hotels_view_get(self, mock_get):
        user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel_finder/search_destination.html')
    
    # @patch('hotel_finder.views.requests.get')
    # def test_search_hotels_view_post_valid_data(self, mock_get):
    #     mock_response = mock_get.return_value
    #     mock_response.json.return_value = {
    #         'data': [{'dest_id': 1, 'hotel_name': 'Hotel 1'}]
    #     }      
    #     user = User.objects.create_user(username='testuser', password='password')
    #     self.client.login(username='testuser', password='password')
    #     response = self.client.post(self.url, data=self.data)
        
    #     self.assertEqual(response.status_code, 302)
    #     response = self.client.get(response.url)
    #     self.assertTemplateUsed(response, 'hotel_finder/search_destination.html')
    #     self.assertContains(response, 'No hotels found for the given search.')

    @patch('hotel_finder.views.requests.get')
    def test_search_hotels_view_post_invalid_date(self, mock_get):
        self.data['departure_date'] = self.data['arrival_date']
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)
    
    @patch('hotel_finder.views.requests.get')
    def test_search_hotels_view_post_invalid_past_date(self, mock_get):
        self.data['arrival_date'] = '2023-01-01'
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 302)

    @patch('hotel_finder.views.requests.get')
    def test_search_hotels_view_no_hotels_found(self, mock_get):
        user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        mock_get.return_value.json.return_value = {'data': []}
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hotels found. Please try again with different details.')