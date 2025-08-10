from django.urls import path
from . import views

app_name = 'moderator'

urlpatterns = [
    path('',views.index,name='index'),
    path('signinxyz',views.signin, name = 'signin'),
    path('blog/create',views.create_post,name = 'create_post'),
    path('blog/edit/<int:post_id>',views.edit_blog_post,name = 'edit_post'),
    path('notifications/notify_player/<str:email>', views.notify_player, name='notify_player'),
    path('notifications/notify_all_players', views.notify_all_players, name='notify_all_players'),
    path('referee/add/<str:email>', views.add_player_as_refree, name='add_refereee'),

    path('tournament/update_round/<int:battle_id>', views.update_tournament_round, name='update_tournament_round'),
    path('tournament/init/<int:tournament_id>', views.start_tournament, name='init_tournament'),

    path('battle/end/<int:battle_id>', views.end_battle, name='end_battle'),
]