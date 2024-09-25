# models.py
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    reviews = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name
