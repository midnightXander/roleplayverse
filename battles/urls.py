from django.urls import path
from . import views
app_name = 'battles'

urlpatterns = [
    path('',views.battles,name='index'),
    path('request',views.request_battle,name='request'),
    path('requests', views.battle_requests, name = 'requests'),
    path('waiting_refree',views.waiting_refree, name='waiting_refree'),
    path('not_started',views.not_yet_started, name="not_started"),

    path("filter/<int:filter_num>",views.filter_battle, name='filter'),

    path('rules/<int:battle_id>', views.rules,name= 'rules'),
    path('battle_room/<int:battle_id>',views.battle_room, name="battle_room"),
    path('textpads/get/<int:battle_id>',views.get_textpads, name="get_textpads"),
    path('textpads/send/<int:battle_id>',views.send_textpad, name="send_textpad"),
    path('textpads/evaluate/<int:battle_id>',views.evaluate_textpad, name='evaluate_textpad'),
    path('textpads/react/<int:textpad_id>',views.react_to_textpad, name='react_to_textpad'),
    path("textpads/<int:textpad_id>/comments/add", views.add_textpad_comment, name="add_textpad_comment"),
    path("textpads/<int:textpad_id>/comments/", views.get_textpad_comments, name="get_textpad_comments"),

    path('declare_winner/<int:battle_id>', views.declare_winner, name = "declare_winner"),

    path('refree/send_proposal/<int:battle_id>',views.refree_proposal,name="refree_proposal"),
    path('refree/validate/<int:proposal_id>',views.validate_refree, name='validate_refree'),
    path('referee/ai/<int:battle_id>',views.enable_ai_refreeing, name='enable_ai_refree'),
    path('referees',views.referees, name ='referees'),
    path('refrees/new_refree',views.new_refree, name ='new_refree'),
    path('referee/rate/<int:battle_id>',views.rate_referee, name = 'rate_referee'),

    path('accept/<int:request_id>',views.accept_battle, name = 'accept'),
    path('new/<int:acceptor_id>',views.init_battle, name="new_battle"),

    path('challenge/send/<int:target_id>',views.send_challenge, name='send_challenge'),
    path('challenge/answer/<int:challenge_id>',views.answer_challenge, name='accept_challenge'),

    path('solo',views.soloBattle, name='solo_battle'),
    path('solo/init',views.init_solo_battle, name='init_solo_battle'),
    path('solo/action',views.solo_battle_action, name='action_solo_battle'),


    

    

    
]
