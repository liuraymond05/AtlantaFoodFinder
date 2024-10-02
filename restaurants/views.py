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
    return render(request, 'restaurants/map.html')


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
            'key': 'AIzaSyArjK69M4dg5Mdy8e_LukUKUgL2TOGNucs'  # Replace with your actual Google API key
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
@login_required
@require_POST
def save_favorite(request):
    data = json.loads(request.body)
    restaurant_name = data.get('name')  # Get the name from the request data

    # Fetch the restaurant based on the name
    restaurant = get_object_or_404(Restaurant, name=restaurant_name)

    # Create or get the favorite
    favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)

    if created:
        return JsonResponse({'message': 'Restaurant added to favorites!'}, status=201)
    else:
        return JsonResponse({'message': 'Restaurant is already in favorites.'}, status=409)


# Remove a restaurant from favorites
@login_required
def remove_favorite(request, favorite_id):
    try:
        favorite = Favorite.objects.get(id=favorite_id, user=request.user)
        favorite.delete()
        return JsonResponse({'message': 'Favorite removed successfully.'}, status=200)
    except Favorite.DoesNotExist:
        return JsonResponse({'message': 'Favorite not found.'}, status=404)


# View user's favorites
@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    return render(request, 'restaurants/favorites.html', {'favorites': favorites})


class HomeView(TemplateView):
    template_name = 'restaurants/index.html'  # Ensure this path is correct


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
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            review = get_object_or_404(Review, id=review_id, user=request.user)
            review.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def add_review(request, place_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            rating = data.get('rating')
            review_text = data.get('reviewText')

            # Create the new review instance (assuming you have a Review model)
            review = Review.objects.create(
                user=request.user,
                place_id=place_id,
                rating=rating,
                review_text=review_text,
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def submit_review(request, place_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            rating = data.get('rating')
            review_text = data.get('reviewText')

            # Here you can create a Review linked to the restaurant identified by place_id
            review = Review.objects.create(
                restaurant_id=place_id,  # Modify this as needed
                user=request.user,
                rating=rating,
                review_text=review_text
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def get_reviews(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return JsonResponse({
        'success': True,
        'review': {
            'rating': review.rating,
            'review_text': review.review_text,
        }
    })


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

def update_review(request, review_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            review = get_object_or_404(Review, id=review_id, user=request.user)
            review.rating = data.get('rating')
            review.review_text = data.get('reviewText')
            review.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})