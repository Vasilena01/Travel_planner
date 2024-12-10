from django.urls import path
from . import views
from authentication import views as auth_views
from hotel_finder import views as hotel_finder_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('auth/logout/', auth_views.logout_user, name='logout'),
]