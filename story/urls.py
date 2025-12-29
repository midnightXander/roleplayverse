from django.urls import path
from . import views

app_name = 'story'

urlpatterns = [
    path('',views.index,name='index'),
    path('character/create',views.create_character,name='create_character'),
    path('characters',views.characters,name='characters'),
    path('game/<int:character_id>',views.game,name='game'),
    path('pass/<int:character_id>',views.subscribe_challenge,name='story_pass'),
    path('remove_ads',views.remove_ads,name='remove_ads'),

    
    path('textpads/<int:textpad_id>/comments',views.get_story_textpad_comments,name='textpad_comments'),
    path('textpads/react/<int:textpad_id>',views.react_to_story_textpad),
    path("textpads/<int:textpad_id>/comments/add", views.add_story_textpad_comment),
    path("textpads/<int:textpad_id>/reactors", views.story_textpad_reactors),
    

    path('array_test', views.array_test),
]