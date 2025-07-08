app_name = 'adventure'
from django.urls import path, include
from . import views
urlpatterns = [

    path('characters/create', views.create_character, name='create_character'),
    path('game', views.game, name='game'),
    path('inventory', views.inventory, name='inventory'),
    path('game/mission/<int:mission_id>', views.mission, name='mission'),
    path('training', views.training, name = 'training'),
    path('battles/training/init', views.init_training, name = 'init_training'),
    path('battles/training/action', views.training_battle_action, name = 'training_action'),
    path('battles/mission/<int:mission_id>/init', views.init_mission, name='init_mission'),
    path('battles/mission/<int:mission_id>/action', views.mission_battle_action, name = 'mission_action'),
    path('mission/<int:mission_id>/end', views.end_mission, name='end_mission'),

]
