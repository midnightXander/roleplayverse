from channels.generic.websocket import AsyncWebsocketConsumer
import json
class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"notifications_{self.user}"
        print(self.user)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        
        data = json.loads(text_data)
        notif_type = data.get('notif_type')
        content = data.get("content")
        sender = data.get("sender")
        profile_picture = data.get('profile_picture')
        timestamp = data.get('timestamp')

        if notif_type == 'private_message':
            await self.channel_layer.group_send(
                self.group_name,{
                    "type": "new_private_message",
                    "content": content,
                    'sender': sender,
                    'profile_picture':profile_picture,
                    'timestamp':timestamp,
                    'message_type': 'private',
                    #'notif_type':'textpad'
                }
            )
        elif notif_type == 'family_message':
                await self.channel_layer.group_send(
                self.group_name,{
                    "type": "new_family_message",
                    "content": content,
                    'sender': sender,
                    'profile_picture':profile_picture,
                    'timestamp':timestamp,
                    'message_type': 'family'
                    #'notif_type':'textpad'
                }
            )

    async def new_private_message(self,event):
        content = event['content']
        sender = event['sender']
        profile_picture = event['profile_picture']
        timestamp = event['timestamp']
        message_type = event['message_type']

        await self.send(text_data=json.dumps({
            "content":content,
            "sender":sender,
            'profile_picture':profile_picture,
            'timestamp':timestamp,
            "message_type":message_type
        })
        )
    async def new_family_message(self,event):
        content = event['content']
        sender = event['sender']
        profile_picture = event['profile_picture']
        timestamp = event['timestamp']
        message_type = event['message_type']

        await self.send(text_data=json.dumps({
            "content":content,
            "sender":sender,
            'profile_picture':profile_picture,
            'timestamp':timestamp,
            "message_type":message_type
        })
        )    

        