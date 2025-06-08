app_name = 'adventure'
from django.urls import path, include
from . import views
urlpatterns = [

    path('characters/create', views.create_character, name='create_character'),
    path('game', views.game, name='game'),
    path('training', views.training, name = 'training'),
    path('battles/training/init', views.init_training, name = 'init_training'),
    path('battles/training/action', views.training_battle_action, name = 'training_action'),


]
