from django.urls import path
from . import views

app_name = 'story'

urlpatterns = [
    path('',views.index,name='index'),
    path('character/create',views.create_character,name='create_character'),
    path('characters',views.characters,name='characters'),
    path('game/<int:character_id>',views.game,name='game'),

    path('array_test', views.array_test),
]