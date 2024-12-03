from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
import json
from .models import TextPad,Battle
from users.models import Player,PlayerNotification,notification_types
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .models import battle_status


class BattleTextConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def new_text_pad(self,username, text ,battle_id):
        battle = Battle.objects.get(id = battle_id)
        user = User.objects.get(username = username)
        player = Player.objects.get(user=user)

        #create the textpad and update battle status
        text_pad = TextPad.objects.create(
            owner = player,
            battle= battle,
            text=text
        )
        battle.status = battle_status[2]
        battle.can_send_textpad = False

        #determine the opponent of the player sending the textpad    
        if text_pad.owner == battle.initiator:
            opponent = battle.opponent
        elif text_pad.owner == battle.opponent:
            opponent = battle.initiator    

        #create a new notification with the sender being the owner of the textpad
        # and the target being the opponent
        new_notif = PlayerNotification.objects.create(
            sender = player,
            target = opponent,
            notif_type = notification_types[3]
        )
        
        battle.save()
        text_pad.save()
        return text_pad
    
    #get the opponent of the sender of the textpad
    def get_opponent(self,text_pad):
        opponent = "Your opponent"
        battle = text_pad.battle
        if text_pad.owner == battle.initiator:
            opponent = battle.opponent
        elif text_pad.owner == battle.opponent:
            opponent = battle.initiator 
        
        return opponent.user.username #may change to just the whole player object for more possibilities    
    
    async def connect(self):
        self.battle_id = self.scope["url_route"]["kwargs"]["battle_id"]
        self.group_name = f"room_{self.battle_id}"
        await self.channel_layer.group_add(self.group_name,self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)    

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        text = text_data_json["text"]
        sender = text_data_json["sender"]

        text_pad = await self.new_text_pad(sender, text, self.battle_id)
        opponent = self.get_opponent(text_pad)

        #send the textpad as a message in the battle room
        await self.channel_layer.group_send(self.group_name, {
            "type":"battle_text_pad",
            "text":text,
            "sender":sender,
            "date_sent": text_pad.date_sent
        })    

        #dispatch a notification to the opponent of the textpad sender
        await self.channel_layer.group_send(
            f"notifications_{opponent}",{
            "type":"new_notification",
            "content": "New textpad in your battle",
            "sender":sender
        })

    async def battle_text_pad(self, event):
        text = event['text']
        sender = event['sender']
        date_sent = event["date_sent"]

        await self.send(text_data=json.dumps({
            "text":text,
            "sender":sender,
            #"date_sent": date_sent,  serialize date_sent into json serializable form before implementing this 
        }))    