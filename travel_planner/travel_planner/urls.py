from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('authentication.urls')),
    path('hotels/', include('hotel_finder.urls')),
    path('my-trips/', include('user_trips.urls')),
]