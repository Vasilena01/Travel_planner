from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_trips, name='list_trips'),
    path('<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('create/', views.create_trip, name='create_trip')
]