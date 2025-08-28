app_name = 'monetization'
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('requirements', views.requirements, name='requirements'),

    path('creators/add/<str:identifier>', views.add_creator, name='add_creator'),
    path('creators/link/<str:identifier>', views.creator_link, name='creator_link'),
    path('creators/dashboard', views.creator_dashboard, name='creator_dashboard'),
]