from django.test import SimpleTestCase
from django.urls import resolve, reverse
from destinations.views import category_destinations, destination_detail

class TestUrls(SimpleTestCase):
    def test_category_destinations_url(self):
        url = reverse('category_destinations', args=['europe'])
        self.assertEqual(resolve(url).func, category_destinations)

    def test_destination_detail_url(self):
        url = reverse('destination_detail', args=['Italy'])
        self.assertEqual(resolve(url).func, destination_detail)