from django.urls import path
from . import views

urlpatterns = [
    path('', views.acceuil, name='acceuil'),
    path('register/', views.register, name='register'),
    path('update_game_state/', views.update_game_state, name='update_game_state'),
]
