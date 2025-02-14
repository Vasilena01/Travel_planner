from django.test import TestCase, RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from user_trips.models import MyTrip, TripDay
from user_trips.views import list_trips, trip_detail, create_trip, delete_trip, list_places, add_place_to_trip, delete_place_from_trip, add_place_to_day, delete_place_from_day, add_collaborator, remove_from_shared

class UserTripsViewsTests(TestCase):
    def setUp(self):
        
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword')

        # Create a trip for the test user
        self.trip = MyTrip.objects.create(
            user=self.user,
            destination='Test Destination',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            image_url='http://example.com/image.jpg'
        )

        # Create a trip day for the trip
        self.trip_day = TripDay.objects.create(
            trip=self.trip,
            date=date.today()
        )

    def test_list_trips(self):
        request = self.factory.get(reverse('list_trips'))
        request.user = self.user
        response = list_trips(request)

        self.assertEqual(response.status_code, 200)

    def test_trip_detail(self):
        request = self.factory.get(reverse('trip_detail', args=[self.trip.id]))
        request.user = self.user
        response = trip_detail(request, self.trip.id)

        self.assertEqual(response.status_code, 200)

    def test_create_trip(self):
        data = {
            'destination': 'New Destination',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
        request = self.factory.post(reverse('create_trip'), data=data)
        request.user = self.user
        response = create_trip(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(MyTrip.objects.filter(destination='New Destination').exists())

    def test_delete_trip(self):
        request = self.factory.post(reverse('delete_trip', args=[self.trip.id]))
        request.user = self.user
        response = delete_trip(request, self.trip.id)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(MyTrip.objects.filter(id=self.trip.id).exists())

    def test_list_places(self):
        request = self.factory.get(reverse('list_places', args=[self.trip.id, 'attractions']))
        request.user = self.user
        response = list_places(request, self.trip.id, 'attractions')

        self.assertEqual(response.status_code, 200)

    def test_add_place_to_trip(self):
        place_name = 'Test Place'
        place_address = 'Test Address'
        request = self.factory.get(reverse('add_place_to_trip', args=[self.trip.id]), {
            'name': place_name,
            'address': place_address,
            'type': 'attractions'
        })
        request.user = self.user
        response = add_place_to_trip(request, self.trip.id)

        self.assertEqual(response.status_code, 302)
        self.trip.refresh_from_db()
        self.assertTrue(any(place['name'] == place_name for place in self.trip.attractions))

    def test_delete_place_from_trip(self):
        place_name = 'Test Place'
        self.trip.attractions.append({'name': place_name, 'address': 'Test Address'})
        self.trip.save()

        request = self.factory.post(reverse('delete_place_from_trip', args=[self.trip.id, 'attractions', place_name]))
        request.user = self.user
        response = delete_place_from_trip(request, self.trip.id, 'attractions', place_name)

        self.assertEqual(response.status_code, 302)
        self.trip.refresh_from_db()
        self.assertFalse(any(place['name'] == place_name for place in self.trip.attractions))

    def test_add_place_to_day(self):
        place_name = 'Test Place'
        self.trip.attractions.append({'name': place_name, 'address': 'Test Address'})
        self.trip.save()

        request = self.factory.post(reverse('add_place_to_day', args=[self.trip.id, self.trip_day.id]), {
            'place_name': place_name,
            'place_type': 'attractions'
        })
        request.user = self.user
        response = add_place_to_day(request, self.trip.id, self.trip_day.id)

        self.assertEqual(response.status_code, 302)
        self.trip_day.refresh_from_db()
        self.assertTrue(any(place['name'] == place_name for place in self.trip_day.places))

    def test_delete_place_from_day(self):
        place_name = 'Test Place'
        self.trip_day.places.append({'name': place_name, 'address': 'Test Address', 'type': 'attractions'})
        self.trip_day.save()

        request = self.factory.post(reverse('delete_place_from_day', args=[self.trip.id, self.trip_day.id, 0]))
        request.user = self.user
        response = delete_place_from_day(request, self.trip.id, self.trip_day.id, 0)

        self.assertEqual(response.status_code, 302)
        self.trip_day.refresh_from_db()
        self.assertFalse(any(place['name'] == place_name for place in self.trip_day.places))

    # def test_add_collaborator(self):
    #     request = self.factory.post(reverse('add_collaborator', args=[self.trip.id]), {
    #         'collaborator': self.other_user.id
    #     })
    #     request.user = self.user
    #     response = add_collaborator(request, self.trip.id)

    #     self.assertEqual(response.status_code, 302)
    #     self.trip.refresh_from_db()
    #     self.assertTrue(self.other_user in self.trip.collaborators.all())

    # def test_remove_from_shared(self):
    #     self.trip.shared_with.add(self.other_user)
    #     self.trip.collaborators.add(self.other_user)
    #     self.trip.save()

    #     request = self.factory.post(reverse('remove_from_shared', args=[self.trip.id]))
    #     request.user = self.other_user
    #     response = remove_from_shared(request, self.trip.id)

    #     self.assertEqual(response.status_code, 302)
    #     self.trip.refresh_from_db()
    #     self.assertFalse(self.other_user in self.trip.shared_with.all())
    #     self.assertFalse(self.other_user in self.trip.collaborators.all())