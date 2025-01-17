from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_flights, name='search_flights'),
] 