from django.shortcuts import render, redirect
from .forms import CustomUserForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant
from django.contrib import auth, messages
import json
import requests
from django.views.generic import TemplateView
from .models import Restaurant, Favorite
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

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

# Render the index page
#def index_view(request):
    #return render(request, 'restaurants/index.html')

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

# Define the home view
class HomeView(TemplateView):
    template_name = 'restaurants/index.html'  # Ensure this path is correct

def register_view(request):
    form = CustomUserForm()

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have made an account!')
            return redirect('login')
    else:
        messages.error(request, 'Please complete the entire form.')
    return render(request, 'restaurants/register.html', {'form': form})

def index_view(request):
    return

def favorite_restaurants_view(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).select_related('restaurant')
    # Create a list of favorite restaurants with their coordinates
    favorites_data = json.dumps(
        list(favorites.values('restaurant__name', 'restaurant__latitude', 'restaurant__longitude'))
    )

    return render(request, 'restaurants/favorites.html', {
        'favorites': favorites,
        'favorites_data': favorites_data  # Pass data to template
    })

def add_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
    return redirect('restaurant_detail', restaurant_id=restaurant.id)

def remove_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    Favorite.objects.filter(user=request.user, restaurant=restaurant).delete()
    return redirect('restaurant_detail', restaurant_id=restaurant.id)

# View to list favorites
def list_favorites(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You need to log in to view favorites.")
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    return render(request, 'restaurants/favorites.html', {'favorites': favorites})


def save_favorite(request, restaurant_id):
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
        return JsonResponse({'success': created, 'message': 'Added to favorites' if created else 'Already a favorite'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})