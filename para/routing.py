from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.urls import re_path,path
from chat import consumers
from battles import consumers as battle_consumers
from core.consumers import NotificationConsumer
from django.core.asgi import get_asgi_application

#URLS that handle WebSocket connection are placed here.

websocket_urlpatterns = [
    #re_path(
        
    #    r"ws/chat/(?P<chat_box_name>\w+)/$", consumers.ChatRoomConsumer.as_asgi(),
        #r"ws/chat/", consumers.ChatRoomConsumer.as_asgi()
    #),
    re_path(r"ws/chat/private/(?P<room_name>\w+)/$", consumers.PrivateChatConsumer.as_asgi()),
    re_path(r"ws/chat/group/(?P<family_name>\w+)/$", consumers.GroupChatConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    re_path(r"ws/battle/one_v_one/(?P<battle_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$",battle_consumers.BattleTextConsumer.as_asgi())

    
]

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
        )
          
    }
)

#application = ProtocolTypeRouter({
#    'websocket': URLRouter([
#        path('ws/chat/',consumers.ChatConsumer.as_asgi()),
#    ])
#})