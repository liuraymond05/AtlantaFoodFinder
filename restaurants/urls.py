from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.map_view, name='map'),
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]