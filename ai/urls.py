app_name = 'adventure'
from django.urls import path, include
from . import views
urlpatterns = [

    path('battle/<int:battle_id>/rules', views.create_rules, name='create_rules'),
    path('battle/<int:battle_id>/verdict', views.make_verdict, name='make_verdict'),

    path('story/avatars/images/create', views.generate_avatar_images, name='generate_avatar'),
    
]
