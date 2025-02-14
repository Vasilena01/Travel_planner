from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from user_trips.models import MyTrip, TripDay

class MyTripModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = MyTrip.objects.create(
            user=self.user,
            destination='Paris',
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 5),
            image_url='https://example.com/image.jpg',
            attractions=["Eiffel Tower", "Louvre Museum"],
            restaurants=["Le Meurice", "Chez Janou"]
        )
    
    def test_trip_creation(self):
        self.assertEqual(self.trip.user, self.user)
        self.assertEqual(self.trip.destination, 'Paris')
        self.assertEqual(self.trip.start_date, date(2025, 3, 1))
        self.assertEqual(self.trip.end_date, date(2025, 3, 5))
        self.assertEqual(self.trip.image_url, 'https://example.com/image.jpg')
        self.assertEqual(self.trip.attractions, ["Eiffel Tower", "Louvre Museum"])
        self.assertEqual(self.trip.restaurants, ["Le Meurice", "Chez Janou"])
    
    def test_generate_trip_days(self):
        self.trip.generate_trip_days()
        trip_days = TripDay.objects.filter(trip=self.trip).order_by('date')
        expected_dates = [date(2025, 3, d) for d in range(1, 6)]
        self.assertEqual(trip_days.count(), 5)
        for trip_day, expected_date in zip(trip_days, expected_dates):
            self.assertEqual(trip_day.date, expected_date)

    def test_shared_with_and_collaborators(self):
        user2 = User.objects.create_user(username='user2', password='password2')
        user3 = User.objects.create_user(username='user3', password='password3')
        self.trip.shared_with.add(user2)
        self.trip.collaborators.add(user3)
        self.assertIn(user2, self.trip.shared_with.all())
        self.assertIn(user3, self.trip.collaborators.all())

class TripDayModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = MyTrip.objects.create(
            user=self.user,
            destination='Rome',
            start_date=date(2025, 4, 10),
            end_date=date(2025, 4, 12)
        )
        self.trip_day = TripDay.objects.create(
            trip=self.trip,
            date=date(2025, 4, 10),
            places=["Colosseum", "Pantheon"]
        )
    
    def test_trip_day_creation(self):
        self.assertEqual(self.trip_day.trip, self.trip)
        self.assertEqual(self.trip_day.date, date(2025, 4, 10))
        self.assertEqual(self.trip_day.places, ["Colosseum", "Pantheon"])
    
    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            TripDay.objects.create(trip=self.trip, date=date(2025, 4, 10))