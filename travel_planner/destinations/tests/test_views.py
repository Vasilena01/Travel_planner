from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json

class DestinationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    @patch('destinations.views.load_countries_data')
    @patch('requests.get')
    def test_category_destinations(self, mock_requests_get, mock_load_countries):
        mock_load_countries.return_value = [
            {'name': {'common': 'France'}, 'region': 'Europe', 'capital': ['Paris'], 'population': 67000000,
             'languages': {'fra': 'French'}, 'currencies': {'EUR': {}}, 'flags': {'png': 'test_flag_url'}}
        ]
        
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            'photos': [{'src': {'large': 'test_image_url'}}]
        }
        
        response = self.client.get(reverse('category_destinations', args=['europe']))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data['destinations']), 1)
        self.assertEqual(data['destinations'][0]['name'], 'France')

    @patch('destinations.views.load_countries_data')
    @patch('requests.get')
    def test_destination_detail(self, mock_requests_get, mock_load_countries):
        mock_load_countries.return_value = [
            {'name': {'common': 'Italy'}, 'cca2': 'IT', 'region': 'Europe', 'capital': ['Rome'],
             'population': 60000000, 'languages': {'ita': 'Italian'}, 'currencies': {'EUR': {}},
             'maps': {'googleMaps': 'test_map_url'}, 'flags': {'png': 'test_flag_url'}}
        ]

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            'photos': [{'src': {'large': 'test_image_url'}}]
        }

        response = self.client.get(reverse('destination_detail', args=['Italy']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Italy")
        self.assertContains(response, "test_map_url")