from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.index,name='index'),
    path('create', views.create,name='create'),
    path('tournaments/create', views.index,name='create_tournament'),
    path('tournament/battles/<uuid:tournament_id>', views.battles, name = 'battles'),
    path('tournaments/<uuid:id>', views.tournament, name='tournament'),
]

