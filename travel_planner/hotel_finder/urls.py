from django.urls import path
from . import views

urlpatterns = [
    path('search-hotels/', views.search_hotels, name='search_hotels'),
]