from django.urls import path
from . import views

app_name = 'search_flights'

urlpatterns = [
    path('', views.search_flights, name='search_flights'),
] 