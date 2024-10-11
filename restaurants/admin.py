from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Restaurant, Favorite

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'address', 'rating')
    search_fields = ('name', 'address')
    list_filter = ('rating',)

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'added_at')
    search_fields = ('user__username', 'restaurant__name')
    list_filter = ('added_at',)

# Register your models
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Favorite, FavoriteAdmin)
