import json,base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from .models import Message,Chat,FamilyMessage
from users.models import Player,Family,PlayerNotification,notification_types
from django.contrib.auth.models import User
from django.db.models import Q
from channels.db import database_sync_to_async
from core.views import _time_since
from core.models import Notification

from utility import encrypt_message

class PrivateChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def create_message(self,sender_name,receiver_name,content,image_data=None,image_name=None):
        sender_user = User.objects.get(username = sender_name)
        sender = Player.objects.get(user = sender_user)

        receiver_user = User.objects.get(username = receiver_name)
        receiver = Player.objects.get(user = receiver_user)


        new_msg = Message.objects.create(
                sender = sender,
                receiver = receiver,
                content = encrypt_message(content),
                chat=None
            )
        if image_data and image_name:
            print("setting image")
            new_msg.image.save(image_name, ContentFile(image_data))
            new_msg.save()
        try:
            #chat = Chat.objects.get(
            #        Q(initiator = sender) | Q(initiator = receiver) &
            #        Q(recipient = receiver ) | Q(recipient = sender)
            #    )
            all_chats = Chat.objects.all()
            chat = None
            for it_chat in all_chats:
                   print(it_chat)
                   
                   if str(it_chat) == f"{sender_name} and {receiver_name}" or str(it_chat) == f"{receiver_name} and {sender_name}":
                        chat = it_chat
                        break
            if chat is not None: 
                print("the chat is: ",chat)        
                chat.last_message_abbr = content[:20]
                chat.last_message_time_sent = new_msg.date_sent
                print("Existing chat between these two...")
                new_msg.chat = chat
                chat.save()
            else:
                new_chat = Chat.objects.create(
                initiator = sender,
                recipient = receiver,
                last_message_abbr = content[:20],
                last_message_time_sent = new_msg.date_sent,
            )
                new_msg.chat = new_chat
                print("New chat between these two")
                new_chat.save()

        except Chat.MultipleObjectsReturned:
            print("more than one objects were returned here are them:")
            print("sender: ",sender)
            print("receiver: ",receiver)
            chats = Chat.objects.filter(
                Q(initiator = sender) | Q(initiator = receiver) &
                    Q(recipient = receiver ) | Q(recipient = sender)
            )    
            print(chats)
        except Chat.DoesNotExist:
            new_chat = Chat.objects.create(
                initiator = sender,
                recipient = receiver,
                last_message_abbr = content[:20],
                last_message_time_sent = new_msg.date_sent,
            )
            new_msg.chat = new_chat
            print("New chat between these two")
            new_chat.save()
        new_notif = Notification.objects.create(
                target = receiver,
                url = f'/chats/dm/{sender_name}',
                content = f'{sender} sent you a message',
        )      

        new_msg.save()
        new_notif.save()
        return new_msg
    
    

    async def connect(self):
        print("connecting...")
        self.chat_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = self.scope["user"]
        self.group_name = f"chat_{self.chat_name}"
        print("group name",self.group_name)
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
    
        await self.accept()

    async def disconnect(self, code):
        print("disconnecting...")
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data, bytes_data = None):
        text_data_json = json.loads(text_data) #convert json data into python dictionnary
        message = text_data_json.get("content")
        sender_name = text_data_json["sender"]
        receiver_name = text_data_json["receiver"]
        base64_file = text_data_json.get('file')
        fileName = text_data_json.get('fileName')
        file_data = None
        available_file_name = None
        print("message receiver: ",receiver_name)
        print("file data:",base64_file, fileName)

        #Handle Image Upload
        if base64_file and fileName:
            file_data = base64.b64decode(base64_file)
            valid_file_name = get_valid_filename(fileName)
            available_file_name = default_storage.get_available_name(valid_file_name)

        
        messageObj = await self.create_message(sender_name,receiver_name,message, file_data, available_file_name)
        
        #await self.create_message(sender_name,receiver_name,message)

        await self.channel_layer.group_send(self.group_name,
            {
                'type':'private_message',
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                "content": message,
                "date_sent":_time_since(messageObj.date_sent),
                "profile_picture_url":  messageObj.sender.profile_picture.url,

            },
        )

        #send a notification to the user 
        await self.channel_layer.group_send(
            f'notifications_{receiver_name}',
            {
                'type':'new_private_message',
                'notif_type':'private_message',
                'content': f'New message: {message[:10]}...',
                "sender": sender_name,
                'timestamp': _time_since(messageObj.date_sent),
                'profile_picture': messageObj.sender.profile_picture.url,
                'message_type': 'private',
                'notif_type':'private_message',
                
            }
        )


    async def private_message(self,event):
        print("preparing...")
        sender_name = event["sender_name"]
        receiver_name = event["receiver_name"]
        content = event["content"]
       
        print("sending...")


        await self.send(text_data = json.dumps({ #convert data into json
            "sender_name": sender_name,
            "receiver_name": receiver_name,
            "content": content,
            

            #"date_sent": messageObj.date_sent
        })
        )
        print("message sent")
    

    





class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connecting...")
        self.chat_box_name = self.scope["url_route"]["kwargs"]["chat_box_name"]
        #self.chat_box_name = "room1"
        self.group_name = "chat_%s" % self.chat_box_name

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)

    #function to receive messages from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        await self.channel_layer.group_send(
           self.group_name,
           {
               "type":"chatbox_message",
               "message": message,
               "username": username,
           }
       ) 

    #receive message from room group
    async def chatbox_message(self, event):
        message = event["message"]
        username = event["username"]
        #send message and username of sender to websocket
        await self.send(
            text_data = json.dumps( #convert into json
                {
                    "message": message,
                    "username": username,
                }
            )
        )    

    pass


class GroupChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def create_family_message(self,sender,message,family_name, image_data=None,image_name=None):
        sender_user = User.objects.get(username = sender)
        player_sender = Player.objects.get(user=sender_user)
        family = Family.objects.get(name = family_name)

        new_msg = FamilyMessage.objects.create(
            sender = player_sender,
            family = family,
            content = encrypt_message(message)
        )
        #add the message sender to the list of readers
        new_msg.readers.add(player_sender)

        if image_data and image_name:
            print("setting image")
            new_msg.image.save(image_name, ContentFile(image_data))

        #create a notif for all members
        members = Player.objects.filter(family = family)
        members = members.exclude(user = sender_user)
        for member in members:
            new_notif = Notification.objects.create(
                    target = member,
                    url = f'/chats/group/{family}',
                    content = f'{sender} sent a message in {family}',
            )  
            new_notif.save()

        new_msg.save()
        return new_msg

    @database_sync_to_async
    def get_family(self,family_name):
        family = Family.objects.get(name = family_name)
        return family
    
    @database_sync_to_async
    def get_family_members(self,sender,family_name):
        sender_user = user = User.objects.get(username = sender)

        family = Family.objects.get(name = family_name)
        members = Player.objects.filter(family = family)
        members = members.exclude(user = sender_user)

        names = [member.user.username for member in members]

        return names 


    async def connect(self):
        print("connecting...")
        self.family_name = self.scope["url_route"]["kwargs"]["family_name"]
        self.group_name = f"chat_{self.family_name}"
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        
        await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)

    async def receive(self, text_data,bytes_data=None):
        print("message received")
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        base64_file = text_data_json.get('file')
        fileName = text_data_json.get('fileName')
        file_data = None
        available_file_name = None

        #Handle Image Upload
        if base64_file and fileName:
            file_data = base64.b64decode(base64_file)
            valid_file_name = get_valid_filename(fileName)
            available_file_name = default_storage.get_available_name(valid_file_name)
        
        messageObj = await self.create_family_message(sender,message,self.family_name,file_data,available_file_name)
        family = await self.get_family(self.family_name)

        await self.channel_layer.group_send(self.group_name,{
            'type':'family_chat_message',
            'message':message,
            'sender':sender,

        })

        #send  notifications to the family members 
        members = await self.get_family_members(sender, self.family_name)
        for member in members:
            await self.channel_layer.group_send(
                f'notifications_{member}',
                {
                    'type':'new_family_message',
                    'message_type':'family',
                    'notif_type':'family_message',
                    'content': f'{sender}: {message[:10]}...',
                    "sender": self.family_name,
                    'timestamp': _time_since(messageObj.date_sent),
                    'profile_picture': family.profile_picture.url,
                    
                }
            )

    async def family_chat_message(self,event):
        print("sending...")
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            "message":message,
            "sender":sender
        }))    
          