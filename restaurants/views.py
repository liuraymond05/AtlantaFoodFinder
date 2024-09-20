from django.shortcuts import render
from .models import Restaurant
import json
from django.core.serializers import serialize


# Create your views here.
def map_view(request):
    restaurants = Restaurant.objects.all()
    restaurants_data = json.dumps(
        list(restaurants.values('name', 'latitude', 'longitude', 'description'))
    )
    return render(request, 'restaurants/map.html', {'restaurants': restaurants})
