from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import Restaurant, Favorite
from .forms import CustomUserForm
import json
import requests

# View to render the map and restaurant markers
def map_view(request):
    restaurants = Restaurant.objects.all()
    restaurants_data = json.dumps(
        list(restaurants.values('name', 'latitude', 'longitude', 'address'))
    )
    return render(request, 'restaurants/map.html', {'restaurants_data': restaurants_data})

# View to handle restaurant search based on user input
def food_finder(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        cuisine = request.GET.get('cuisine', '')
        min_rating = request.GET.get('min_rating', 0)
        max_distance = request.GET.get('max_distance', 10)

        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': '33.749,-84.388',
            'radius': float(max_distance) * 1609.34,
            'type': 'restaurant',
            'keyword': query,
            'key': 'YOUR_GOOGLE_API_KEY'  # Replace with your actual Google API key
        }
        response = requests.get(places_url, params=params)
        results = response.json().get('results', [])

        filtered_restaurants = [
            {
                'name': place['name'],
                'address': place.get('vicinity', ''),
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng'],
                'rating': place.get('rating', 'N/A'),
                'cuisine_type': ', '.join(place.get('types', [])),
                'place_id': place.get('place_id')
            }
            for place in results if 'rating' in place and place['rating'] >= float(min_rating)
        ]

        return render(request, 'restaurants/search_results.html', {'restaurants': filtered_restaurants})

    return render(request, 'restaurants/search_results.html')

# Handle user login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')  # Redirect to home after login
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'restaurants/login.html')

# Handle user logout
def logout_view(request):
    auth.logout(request)
    messages.info(request, 'You have successfully logged out!')
    return redirect('/')

# Handle user registration
def register_view(request):
    form = CustomUserForm()

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully created an account!')
            return redirect('login')
    else:
        messages.error(request, 'Please complete the entire form.')
    return render(request, 'restaurants/register.html', {'form': form})

# Add a restaurant to favorites
@login_required
@require_POST
def add_to_favorites(request):
    data = json.loads(request.body)
    place_id = data.get('place_id')
    name = data.get('name')

    restaurant, created = Restaurant.objects.get_or_create(
        place_id=place_id,
        defaults={'name': name}
    )

    # Add to user's favorites
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        restaurant=restaurant
    )

    if created:
        return JsonResponse({'message': 'Added to favorites!'})
    else:
        return JsonResponse({'error': 'Restaurant is already in your favorites.'}, status=400)

# Remove a restaurant from favorites
@login_required
def remove_favorite(request, place_id):
    restaurant = get_object_or_404(Restaurant, place_id=place_id)
    Favorite.objects.filter(user=request.user, restaurant=restaurant).delete()
    return redirect('favorites')

# View user's favorites
@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    return render(request, 'restaurants/favorites.html', {'favorites': favorites})

class HomeView(TemplateView):
    template_name = 'restaurants/index.html'  # Ensure this path is correct
