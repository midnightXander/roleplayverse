from django.urls import path
from . import views
app_name = 'chat'

urlpatterns = [
    path('',views.chats,name = "all"),
    path('search',views.search,name="search"),
    path('dm/<str:receiver_name>',views.private_chat,name="private_chat"),
    path('get_messages/<int:receiver_id>',views.get_messages,name="get_messages"),
    path('send_message/<int:receiver_id>',views.send_message,name="send_message"),
    #path('message/delete/<int:message_id>',),
    path('group/<str:family_name>',views.family_chat,name='family_chat'),
    path('group/get_messages/<str:family_name>',views.get_family_messages, name='get_family_messages'),
    path('messages/delete/private/<int:message_id>',views.delete_private_message, name = 'delete_private_message'),
    path('messages/delete/family/<uuid:message_id>',views.delete_family_message, name = 'delete_family_message'),

    #chat_box
    path('<str:chat_box_name>/',views.chat_box,name='chat_box'),
]
