from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('ad_click', views.ad_click,name='index'),
   
]