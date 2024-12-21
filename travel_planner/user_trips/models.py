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

    # TODO: delete it, for now just for debugging if needed
    def __str__(self):
        return f"{self.destination} ({self.start_date} - {self.end_date})"
