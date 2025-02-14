from django.test import SimpleTestCase
from django.urls import reverse, resolve
from hotel_finder import views

class TestUrls(SimpleTestCase):

    def test_search_hotels_url_resolves(self):
        url = reverse('search_hotels')
        self.assertEqual(resolve(url).func, views.search_hotels)