from django.db import models

# Create your models here.

class Destination(models.Model):
    name = models.CharField(max_length=200)
    capital = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100, blank=True)
    population = models.BigIntegerField()
    languages = models.JSONField()
    currencies = models.JSONField()
    image_url = models.URLField()
    maps_url = models.URLField(blank=True)
    flag_url = models.URLField()

    def __str__(self):
        return self.name
