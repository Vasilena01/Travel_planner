from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class MyTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    image_url = models.CharField(max_length=500, null=True, blank=True)
    attractions = models.JSONField(default=list,  blank=True)
    restaurants = models.JSONField(default=list,  blank=True)

    def generate_trip_days(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            TripDay.objects.get_or_create(
                trip=self,
                date=current_date
            )
            current_date += timedelta(days=1)

class TripDay(models.Model):
    trip = models.ForeignKey(MyTrip, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    places = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['date']
        unique_together = ['trip', 'date']