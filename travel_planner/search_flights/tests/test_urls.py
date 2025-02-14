from django.test import SimpleTestCase
from django.urls import reverse, resolve
from search_flights.views import search_flights

class TestUrls(SimpleTestCase):
    def test_search_flights_url_resolves(self):
        url = reverse('search_flights')
        self.assertEqual(resolve(url).func, search_flights)