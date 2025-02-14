from django.test import SimpleTestCase
from django.urls import reverse, resolve
from user_trips import views

class TestTripURLs(SimpleTestCase):
    def test_list_trips_url_resolves(self):
        url = reverse('list_trips')
        self.assertEqual(resolve(url).func, views.list_trips)
    
    def test_trip_detail_url_resolves(self):
        url = reverse('trip_detail', args=[1])
        self.assertEqual(resolve(url).func, views.trip_detail)
    
    def test_create_trip_url_resolves(self):
        url = reverse('create_trip')
        self.assertEqual(resolve(url).func, views.create_trip)
    
    def test_delete_trip_url_resolves(self):
        url = reverse('delete_trip', args=[1])
        self.assertEqual(resolve(url).func, views.delete_trip)
    
    def test_list_places_url_resolves(self):
        url = reverse('list_places', args=[1, 'attractions'])
        self.assertEqual(resolve(url).func, views.list_places)
    
    def test_add_place_to_trip_url_resolves(self):
        url = reverse('add_place_to_trip', args=[1])
        self.assertEqual(resolve(url).func, views.add_place_to_trip)
    
    def test_delete_place_from_trip_url_resolves(self):
        url = reverse('delete_place_from_trip', args=[1, 'restaurants', 'PizzaPlace'])
        self.assertEqual(resolve(url).func, views.delete_place_from_trip)
    
    def test_add_place_to_day_url_resolves(self):
        url = reverse('add_place_to_day', args=[1, 2])
        self.assertEqual(resolve(url).func, views.add_place_to_day)
    
    def test_delete_place_from_day_url_resolves(self):
        url = reverse('delete_place_from_day', args=[1, 2, 0])
        self.assertEqual(resolve(url).func, views.delete_place_from_day)
    
    def test_add_collaborator_url_resolves(self):
        url = reverse('add_collaborator', args=[1])
        self.assertEqual(resolve(url).func, views.add_collaborator)
    
    def test_remove_from_shared_url_resolves(self):
        url = reverse('remove_from_shared', args=[1])
        self.assertEqual(resolve(url).func, views.remove_from_shared)