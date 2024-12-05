from django.urls import path
from . import views
from authentication import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('auth/logout/', auth_views.logout_user, name='logout'),
]