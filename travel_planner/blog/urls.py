from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_posts, name='list_posts'),
    path('post/<int:pk>/', views.get_post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
]