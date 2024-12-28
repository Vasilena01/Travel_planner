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
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.attractions is None:
    #         self.attractions = []
    #     if self.restaurants is None:
    #         self.restaurants = []

    # def generate_trip_days(self):
    #     if self.start_date and self.end_date:
    #         days = []
    #         current_date = self.start_date
    #         while current_date <= self.end_date:
    #             days.append(
    #                 TripDay(trip=self, date=current_date)
    #             )
    #             current_date += timedelta(days=1)
    #         TripDay.objects.bulk_create(days)

# class TripList(models.Model):
#     LIST_TYPES = [
#         ('attractions', 'Attractions'),
#         ('restaurants', 'Restaurants'),
#         ('notes', 'Notes'),
#     ]
    
#     trip = models.ForeignKey(MyTrip, on_delete=models.CASCADE, related_name='lists')
#     title = models.CharField(max_length=200)
#     list_type = models.CharField(max_length=20, choices=LIST_TYPES)
#     created_at = models.DateTimeField(auto_now_add=True)

# class ListItem(models.Model):
#     trip_list = models.ForeignKey(TripList, on_delete=models.CASCADE, related_name='items')
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     address = models.CharField(max_length=500, blank=True, null=True)

# class TripDay(models.Model):
#     trip = models.ForeignKey(MyTrip, on_delete=models.CASCADE, related_name="days")
#     date = models.DateField()
#     notes = models.TextField(blank=True, null=True)

# class DayActivity(models.Model):
#     ACTIVITY_TYPES = [
#         ('attraction', 'Attraction'),
#         ('restaurant', 'Restaurant'),
#         ('note', 'Note')
#     ]
    
#     day = models.ForeignKey(TripDay, on_delete=models.CASCADE, related_name='activities')
#     list_item = models.ForeignKey(ListItem, on_delete=models.SET_NULL, null=True, blank=True)
#     activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
#     time = models.TimeField(null=True, blank=True)
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['time']