from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('authentication.urls')),
    path('hotels/', include('hotel_finder.urls')),
    path('my-trips/', include('user_trips.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)