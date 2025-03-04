from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_trips, name='list_trips'),
    path('<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('create/', views.create_trip, name='create_trip'),
    path('delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/places/<str:place_type>/', views.list_places, name='list_places'),
    path('trip/<int:trip_id>/add-place/', views.add_place_to_trip, name='add_place_to_trip'),
    path('trip/<int:trip_id>/delete-place/<str:place_type>/<str:place_name>/', views.delete_place_from_trip, name='delete_place_from_trip'),
    path('trip/<int:trip_id>/day/<int:day_id>/add-place/', views.add_place_to_day, name='add_place_to_day'),
    path('trip/<int:trip_id>/day/<int:day_id>/delete-place/<int:place_index>/', views.delete_place_from_day, name='delete_place_from_day'),
    path('trip/<int:trip_id>/add-collaborator/', views.add_collaborator, name='add_collaborator'),
    path('trip/<int:trip_id>/remove-from-shared/', views.remove_from_shared, name='remove_from_shared'),
]