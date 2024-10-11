from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(default=0.0)  # Set a default value for latitude
    longitude = models.FloatField(default=0.0)  # Set a default value for longitude
    address = models.CharField(max_length=255, default='')  # Default to an empty string
    contact_info = models.CharField(max_length=255, blank=True, null=True)  # Optional
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)  # Optional
    rating = models.FloatField(blank=True, null=True)  # Optional
    reviews = models.TextField(blank=True, null=True)  # Optional
    place_id = models.CharField(max_length=255, blank=True, null=True)  # Optional

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    place_id = models.CharField(max_length=255, default='default_value')

    class Meta:
        unique_together = ('user', 'restaurant')

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name}"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

