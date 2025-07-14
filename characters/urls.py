from django.urls import path
from . import views

app_name = "characters"

urlpatterns = [
    path('',views.index, name='index'),
    path('all',views.all_characters, name='all_characters'),
]