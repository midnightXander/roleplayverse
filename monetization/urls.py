app_name = 'monetization'
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('requirements', views.requirements, name='requirements'),
]
