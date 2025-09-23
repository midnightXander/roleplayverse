from django.urls import path
from . import views

app_name = 'duels'

urlpatterns = [
    path('',views.index,name='index'),
    path('new',views.new_duel,name='new_duel'),
    path('join_random',views.join_random_duel,name='join_duel_random'),
   
    path('<str:duel_code>/init',views.init_duel,name='init'),
    path('<str:duel_code>/action',views.duel_action,name='action'),
    path('join/<str:duel_code>',views.join_duel,name='join_duela'),
    path('<str:duel_code>',views.duel,name='game'),
]