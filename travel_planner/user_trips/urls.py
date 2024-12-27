from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_trips, name='list_trips'),
    path('<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('create/', views.create_trip, name='create_trip'),
    path('delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/places/<str:place_type>/', views.list_places, name='list_places'),
    # path('trip/<int:trip_id>/add-place/', views.add_place_to_trip, name='add_place_to_trip'),
]