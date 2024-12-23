from django.urls import include, path
from . import views
from .views import HomeView, add_to_favorites, remove_favorite


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('map/', views.map_view, name='map'),
    path('search/', views.food_finder, name='food_finder'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('favorites/', views.favorites_view, name='favorite'),
    #path('add_to_favorites/', add_to_favorites, name='add_to_favorites'),
    path('add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),
    path('restaurant/<str:place_id>/add_review/', views.add_review, name='add_review'),
    path('change/', views.change_password_view, name='change'),
    path('reset/', views.reset_password_view, name='reset'),
]
