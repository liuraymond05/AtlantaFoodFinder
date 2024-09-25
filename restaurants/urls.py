from django.urls import include, path
from . import views
from .views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Use HomeView for the root URL
    path('map/', views.map_view, name='map'),  # Map view for displaying the map
    path('search/', views.food_finder, name='food_finder'),  # Search view for finding restaurants
    path('login/', views.login_view, name='login'),  # Login view for user authentication
    path('logout/', views.logout_view, name='logout'),  # Logout view for user authentication
    path('register/', views.register_view, name='register'), #Register view for user authentication
    path('', views.index_view, name='index'),
    path('restaurant/<int:restaurant_id>/add_favorite/', views.add_favorite, name='add_favorite'),
    path('restaurant/<int:restaurant_id>/remove_favorite/', views.remove_favorite, name='remove_favorite'),
    path('favorites/', views.list_favorites, name='list_favorites'),
    path('save_favorite/<int:restaurant_id>/', views.save_favorite, name='save_favorite'),
]
