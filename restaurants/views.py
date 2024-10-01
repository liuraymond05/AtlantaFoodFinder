from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from .models import Restaurant, Favorite, Review
from .forms import CustomUserForm, ReviewForm, PasswordResetCustomForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
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
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have successfully logged out!')
        return redirect('login')
    return render(request, 'restaurants/logout.html')

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


def restaurant_detail(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.save()
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = ReviewForm()
    
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant, 'reviews': reviews, 'form': form})

def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    if request.user != review.user:
        return redirect('restaurant_detail', restaurant_id=review.restaurant.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('restaurant_detail', restaurant_id=review.restaurant.id)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'edit_review.html', {'form': form, 'review': review})

def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    if request.user == review.user:
        review.delete()
    return redirect('restaurant_detail', restaurant_id=review.restaurant.id)


def add_review(request, place_id):
    restaurant = get_object_or_404(Restaurant, place_id=place_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        # Create the new review
        review = Review.objects.create(
            user=request.user,
            restaurant=restaurant,
            rating=rating,
            text=text
        )
        review.save()
        
    return redirect('restaurant_detail', place_id=restaurant.place_id)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
        else:
            messages.error(request, "Please put in a valid password.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'restaurants/reset.html', {"form": form})

def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetCustomForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password_new = form.cleaned_data['new_password1']

            try:
                user = User.objects.get(username=username)
                user.set_password(password_new)
                user.save()
                messages.success(request, 'Your password was successfully updated!')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'This user does not exist.')
    else:
        form = PasswordResetCustomForm()
    return render(request, 'restaurants/reset.html', {"form": form})