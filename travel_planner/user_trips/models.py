from django.contrib.auth.models import User
from django.db import models


class MyTrip(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trips"
    )
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    image_url = models.CharField(max_length=500, null=True, blank=True)
    chosen_hotel_id = models.IntegerField(null=True, blank=True)
    hotels_wishlist = models.TextField(null=True, blank=True)
    flights_wishlist = models.TextField(null=True, blank=True)

    def generate_trip_days(self):
        """Generate days for the trip based on the start and end dates."""
        if self.start_date and self.end_date:
            days = []
            current_date = self.start_date
            while current_date <= self.end_date:
                days.append(
                    TripDay(trip=self, date=current_date, activities="", restaurants_cafes="", notes="")
                )
                current_date += timedelta(days=1)
            TripDay.objects.bulk_create(days)


class TripDay(models.Model):
    trip = models.ForeignKey(
        MyTrip,
        on_delete=models.CASCADE,
        related_name="days"
    )
    date = models.DateField()
    activities = models.TextField(null=True, blank=True)
    restaurants_cafes = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)