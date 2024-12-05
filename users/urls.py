from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # path('info',views.validate_info,name='validate'),
    path('test_template',views.test_template,name='test_template'),
    path('signup',views.register,name='register'),
    path('signin',views.login,name='login'),
    path('logout',views.logout_view,name='logout'),
    path('password/recover', views.password_recover, name = 'password_recover'),
    path('password/reset', views.password_reset, name = 'password_reset'),
    path('verify_username', views.verify_username, name="verify_username"),
    path('verify_email', views.verify_email, name="verify_email"),
    path('verify_password', views.verify_password, name="verify_password"),
    path('verify_passwords',views.verify_passwords, name= "verify_passwords"),

    path('families',views.families,name='families'), 
    path('families/rankings',views.family_rankings, name= 'family_rankings'),
    path('families/rankings/data',views.get_families_rankings, name = 'families_rankings_json'),


    path('profile',views.player_profile, name='profile'),

    # path('family',views.family,name="family"),
    path('family/new',views.new_family,name='new_family'),
    path('verify_family_name', views.verify_family_name, name="verify_family_name"),
       

    # path('battles',views.battles, name= 'battles'),
    path('posts/<str:name>',views.player_posts,name = 'player_posts'),
    path('battles/<str:name>',views.player_battles, name= 'player_battles'),
    path('requests',views.battle_requests, name='battle_requests'),
    path('requests/<str:name>',views.player_battle_requests, name='player_battle_requests'),
    path('statistics/<str:name>', views.stats, name = 'player_stats'),
    path('challenges/<str:name>', views.challenges, name = 'player_challenges'),

    path('send_request/Uv59f2JdwPpZS3ey<int:family_id>',views.send_request,name='send_request'),
    path('refuse_request/<int:notif_id>',views.refuse_request, name='refuse_request'),
    path('send_invite/<int:target_id>',views.send_invite,name="send_invite"),
    path('join_family/<int:notif_id>',views.join_family,name="join_family"),
    path('accept_request/<int:notif_id>',views.accept_request,name="accept_request"),
    path('family/Uv59f2JdwPpZS3ey<int:family_id>',views.family_page,name='family_page'),
    path('family/Uv59f2JdwPpZS3ey<int:family_id>/battles',views.family_battles,name='family_battles'),
    path('family/members/Uv59f2JdwPpZS3ey<int:family_id>', views.get_members, name = 'family_members'),
    path('family/promote/<int:player_id>',views.promote_member,name = 'promote_member'),
    path('family/demote/<int:player_id>',views.demote_member,name = 'demote_member'),
    path('family/remove/<int:player_id>',views.remove_member,name = 'remove_member'),
    

    path('notification/<int:id>/<str:type>',views.player_notif,name="notif"),
    path('players',views.get_players, name="players"),

    path('player/edit_info',views.edit_info, name = 'edit_info'),
    
   
    path('players/rankings', views.players_ranking, name = 'players_rankings'),    

    path('player/favorites',views.favorites, name = "favorites"),
    path('<str:name>',views.player,name='player'),

    
    
]