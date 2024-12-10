from django.urls import path
from . import views

urlpatterns = [
    path('search-destination/', views.search_destination_page, name='search_destination_page'),
    path('search-destination-api/', views.search_destination, name='search_destination'),
    path('search-hotels/', views.search_hotels, name='search_hotels'),
]