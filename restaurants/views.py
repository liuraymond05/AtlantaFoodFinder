from django.shortcuts import render, redirect
from .models import Restaurant
from django.contrib import auth, messages
from .forms import LoginForm
import json
from django.core.serializers import serialize


# Create your views here.
def map_view(request):
    restaurants = Restaurant.objects.all()
    restaurants_data = json.dumps(
        list(restaurants.values('name', 'latitude', 'longitude', 'description'))
    )
    return render(request, 'restaurants/map.html', {'restaurants': restaurants})

def index_view(request):
    return render(request, 'restaurants/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'restaurants/login.html', {'form': LoginForm})

def logout_view(request):
    auth.logout(request)
    messages.info(request, 'You have successfully logged out!')
    return redirect('/')