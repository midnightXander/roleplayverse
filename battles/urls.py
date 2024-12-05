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

    path('rules/int:battle_id>', views.rules,name= 'rules'),
    path('battle_room/<int:battle_id>',views.battle_room, name="battle_room"),
    path('textpads/get/<int:battle_id>',views.get_textpads, name="get_textpads"),
    path('textpads/send/<int:battle_id>',views.send_textpad, name="send_textpad"),
    path('textpads/evaluate/<int:battle_id>',views.evaluate_textpad, name='evaluate_textpad'),

    path('declare_winner/<int:battle_id>', views.declare_winner, name = "declare_winner"),

    path('refree/send_proposal/<int:battle_id>',views.refree_proposal,name="refree_proposal"),
    path('refree/validate/<int:proposal_id>',views.validate_refree, name='validate_refree'),
    path('referees',views.referees, name ='referees'),
    path('refrees/new_refree',views.new_refree, name ='new_refree'),
    path('referee/rate/<int:battle_id>',views.rate_referee, name = 'rate_referee'),

    path('accept/<int:request_id>',views.accept_battle, name = 'accept'),
    path('new/<int:acceptor_id>',views.init_battle, name="new_battle"),

    path('challenge/send/<int:target_id>',views.send_challenge, name='send_challenge'),
    path('challenge/answer/<int:challenge_id>',views.answer_challenge, name='accept_challenge'),


    

    

    
]
