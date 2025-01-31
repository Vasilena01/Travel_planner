from django.urls import path
from . import views

urlpatterns = [
    path('category/<str:category>/', views.category_destinations, name='category_destinations'),
    path('detail/<str:destination_name>/', views.destination_detail, name='destination_detail'),
] 