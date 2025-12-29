
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse,Http404
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from users.views import _player_data
from .models import *
from django.db.models import Q
from users.models import Player,Family,FamilyMember
from users.users_utility import get_player
import core.views as core_views
import uuid
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from utility import decrypt_message,_date_time,_chat_date_time,_time_since,_parse_number,_time_since_last_seen
from cryptography.fernet import Fernet
from api.models import PushSubscription
from api.utility import send_push_notification



def check_family_membership(player:Player,family:Family):
    return player.family == family

def get_last_message(chat,chat_type='private'):
    if chat_type == "private":
        messages = Message.objects.filter(chat = chat)
        
    last_message = messages.last()
    if last_message:
        return {
            "sender":last_message.sender.user.username,
            "receiver":last_message.receiver.user.username,
            "content":decrypt_message(last_message.content),
            'image': last_message.image.url if last_message.image else None, 
            'date_sent': _chat_date_time(last_message.date_sent)
            }
    else:
        return ""
    

def get_player_last_seen(player:Player):
    last_seen = player.last_seen
    return _time_since_last_seen(last_seen)

def _get_private_messages_unreads(player:Player):
    return Message.objects.filter(receiver = player, read = False).count()

def _get_family_unreads(player:Player):
    family = player.family
    if family:
        family_messages = FamilyMessage.objects.filter(family = family)
        count = [1 for msg in family_messages if player not in msg.readers.all()]
        return sum(count)
    
    else:
        return 0    

def _chat_data(chat: Chat,player:Player):
    
    return {
        "initiator" : _player_data(chat.initiator),
        "recipient" : _player_data(chat.recipient),
        "last_message": get_last_message(chat,"private"),
        'unreads': {
                'number':_parse_number(chat.unreads(player)),
                'label':'unread' if _parse_number(chat.unreads(player)) != '' else ''
            },
            

    }


@login_required
def chats(request):
    current_player = get_player(request.user)
    if not current_player:
        return redirect('/users/signin')
    
    message_list=[]
    receivers = []


    family_last_message = FamilyMessage.objects.filter(family = current_player.family).order_by('-date_sent').first()
        
    if family_last_message:
        content =  decrypt_message(family_last_message.content)[:7]+'...'
        if family_last_message.image:
            content = f'sent an image'
        fl_message_data = {
            "sender":family_last_message.sender.user.username,
            'content': content,
            'image': family_last_message.image.url if family_last_message.image else None, 
            'date_sent': _date_time(family_last_message.date_sent),
            'unreads': {
               'number': _parse_number(_get_family_unreads(current_player)),
               'label': 'unread' if _parse_number(_get_family_unreads(current_player)) != '' else ''
            }
            
        }
    else:
        fl_message_data = ''

    active_players = Player.objects.exclude(id = current_player.id).order_by('-last_seen')[:5]
    active_players = [ _player_data(player) for player in active_players ]      

    context = {"chats":[],
               "active_players" : active_players,
               "player":current_player,
               "family_last_message":fl_message_data,
               "n_notifs": core_views.get_notifs(current_player),
               }
    return render(request,"chat/chats.html",context)

def fetch_chats(request, username):
    user = User.objects.get(username = username)
    player = get_player(user)
    if player:
        chats = Chat.objects.filter(
            Q(initiator = player) | Q(recipient = player)
        ).order_by("-last_message_time_sent")

        chats = [ _chat_data(chat,player) for chat in chats ]
        return JsonResponse({'status':'success','chats':chats})
    else:
        return JsonResponse({'status':'error'})

def getchats(player):
    chats = Chat.objects.filter(
        Q(initiator = player) | Q(recipient = player)
    ).order_by("-last_message_time_sent")

    return chats

def mark_as_read(message:Message):
    message.read = True
    message.save()

def _message_data(message:Message):
    return{
        "id":message.id,
        "sender":{
            'username':message.sender.user.username,
            'profile_picture': message.sender.profile_picture.url
            },
        "receiver":{
            'username':message.receiver.user.username,
            'profile_picture': message.sender.profile_picture.url,
            },
        "parent":_message_data(message.parent) if message.parent else None,    
        "content":decrypt_message(message.content),
        'image': message.image.url if message.image else None, 
        'date_sent': _date_time(message.date_sent),
        'read': message.read,
        'day': message.date_sent.strftime("%A"),
        'date': message.date_sent.strftime("%d %b %Y"),
        
        }

def get_messages(request,receiver_id):    
    #receiver_user = User.objects.get(username = receiver_name)
    receiver = Player.objects.get(id=receiver_id)
    sender = Player.objects.get(user=request.user)
    #messages = Message.objects.filter(Q(sender = sender or receiver) &
    #                                   Q(receiver = receiver or sender))
    messages = Message.objects.filter(
        Q(sender = sender) |  Q(sender=receiver), 
        Q(receiver = receiver) | Q(receiver = sender)).order_by("date_sent")
    
    for msg in messages:
        if msg.receiver == Player.objects.get(user = request.user):
            msg.mark_as_read()
            #mark_as_read(msg)

    messages_data = [ _message_data(message)
        for message in messages]
    return JsonResponse({"message":"success","messages":messages_data})

def mark_as_reader_family(player,family):
    messages = FamilyMessage.objects.filter(family = family)

def _family_message_data(message:FamilyMessage):
    return {   "id":message.id,          
            "sender":{
                        'username':message.sender.user.username,
                        'profile_picture': message.sender.profile_picture.url
                     },
                      "family":message.family.name,
                      "content":decrypt_message(message.content),
                      'image': message.image.url if message.image else None, 
                      'date_sent': _date_time(message.date_sent),
                      'day': message.date_sent.strftime("%A"),
                      'date': message.date_sent.strftime("%d %b %Y"),
                      'parent' : {
                          'id': message.parent.id,
                          "sender":{
                        'username':message.parent.sender.user.username,
                        'profile_picture': message.parent.sender.profile_picture.url
                        },
                        "content":decrypt_message(message.parent.content),
                        'image': message.parent.image.url if message.parent.image else None, 

                      } if message.parent else None
                        
                      
                       }

def get_family_messages(request, family_name):
    family = Family.objects.get(name = family_name)
    sender = Player.objects.get(user=request.user)

    messages = FamilyMessage.objects.filter(
        family = family
    ).order_by('date_sent')
    #Mark All family messages as read
    for msg in FamilyMessage.objects.filter(family = family):
        if sender not in msg.readers.all():
            msg.readers.add(sender)

    messages_data = [ _family_message_data(message)
        for message in messages
    ]
    return JsonResponse({"message":"success","messages":messages_data})

    

@login_required
def private_chat(request,receiver_name):
    
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    chats = getchats(player)
    try:
        receiver_user = User.objects.get(username = receiver_name)
        receiver = Player.objects.get(user=receiver_user)
        sender = Player.objects.get(user=request.user)
    except:
        return redirect('/')
       
    sent_messages = Message.objects.filter(sender = sender,receiver=receiver)
    sent_by_user = [x for x in sent_messages if x.sender==request.user]
    sent_by_receiver = [x for x in sent_messages if x.sender != request.user]

    chats_data = [
        {
            "chat": chat,
            "last_message": get_last_message(chat)
        }
        for chat in chats
    ]
    family_last_message = FamilyMessage.objects.filter(family = player.family).order_by('-date_sent').first()
    if family_last_message:
        content =  decrypt_message(family_last_message.content)[:7]+'...'
        if family_last_message.image:
            content = f'sent an image'
        fl_message_data = {
            "sender":family_last_message.sender.user.username,
            'content': content,
            'image': family_last_message.image.url if family_last_message.image else None, 
            'date_sent': _date_time(family_last_message.date_sent),
             
            # 'unreads': {
            #    'number': _parse_number(_get_family_unreads(player)),
            #    'label': 'unread' if _parse_number(_get_family_unreads(player)) != '' else ''
            # }
        }
    else:
        fl_message_data = ''  

    active_players = Player.objects.exclude(id = player.id).order_by('-last_seen')[:5]
    active_players = [ _player_data(player) for player in active_players ]      
        

    context = {"receiver":receiver,
               "active_players":active_players,
               'last_seen': get_player_last_seen(receiver),
               "sent_messages":sent_messages,               
                "sent":sent_by_user,
                "received":sent_by_receiver,
                "room":"room1", 
                "player":player, 
                "chats":chats_data,
                "family_last_message":fl_message_data}
    return render(request,"chat/private_chat.html",context)
        
@csrf_exempt       
def delete_private_message(request, message_id):
    if request.method == "DELETE":
        player = get_object_or_404(Player, user=request.user)
        respond = ''
        
        message = get_object_or_404(Message, id = message_id)
        if player != message.sender:
            respond = "Can't delete a message you did not sent"
        else:
            message.delete()
            return JsonResponse({'status':'success', 'message':'message deleted'})
       
    return JsonResponse({'status':'failed', 'respond':respond})        

@csrf_exempt       
def delete_family_message(request, message_id):
    if request.method == "DELETE":
        player = get_object_or_404(Player, user=request.user)
        respond = ''
        
        message = get_object_or_404(FamilyMessage, id = message_id)
        if player != message.sender and player.user != message.family.god_father:
            respond = "Can't delete a message you did not sent"
        elif player.family != message.family:
            respond = "Message was sent in a family you do not belong to"
        else:    
            message.delete()
            return JsonResponse({'status':'success', 'message':'message deleted'})
    return JsonResponse({'status':'failed', 'respond':respond})        


def send_message(request,receiver_id):
    if request.method == "POST":
        content = request.POST["content"]
        receiver = Player.objects.get(id = receiver_id)
        sender = Player.objects.get(user=request.user)
        

        new_msg = Message.objects.create(
            sender = sender,
            receiver = receiver,
            content = content,
            chat=None
        )
        #new_msg.save()
        try:
            chat = Chat.objects.get(
                Q(initiator = sender) | Q(initiator = receiver) &
                Q(recipient = sender ) | Q(recipient = receiver)
            )

            #chat = Chat.objects.get(
            #    Q(initiator = receiver) | Q(recipient = receiver)
            #)
            chat.last_message_abbr = content[:20]
            chat.last_message_time_sent= new_msg.date_sent
            #print("Existing chat between these two...")
            new_msg.chat = chat
            chat.save()
        except:
            new_chat = Chat.objects.create(
                initiator = sender,
                recipient = receiver,
                last_message_abbr = content[:20],
                last_message_time_sent= new_msg.date_sent,
            )
            new_msg.chat = new_chat
            #print("New chat between these two")
            new_chat.save()
        new_msg.save()

        return JsonResponse({'message':"success",
                             "content":new_msg.content,
                             "sender":new_msg.sender.user.username,
                             "receiver":new_msg.receiver.user.username,
                             "date_sent":new_msg.date_sent,
                            })

    return JsonResponse({'message':"error"})

def search(request):
    search_list = []
    if request.method == "POST":
        name = request.POST["username"] 
        searched_users = User.objects.filter(username__icontains = name) 
        print("searched_users: ",searched_users)
        searched_players = []
        #if not searched_users:
        for user in searched_users:
            if user.username != "xander_random":
                player = Player.objects.get(user=user)
                searched_players.append({"username":player.user.username})
        

    #context = {"searched_players":searched_players}
        return JsonResponse({"status":"success","searched_players":searched_players})            
    

##############  Message Test ###########################
def chat_box(request, chat_box_name):
    ctx = {"chat_box_name":chat_box_name}
    return render(request,"chat/chatbox.html",ctx)

def _mark_family_message_as_read(message: FamilyMessage, player:Player):
    message.readers.add(player)



@login_required
def family_chat(request,family_name):

    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
  
    family = Family.objects.get(name = family_name)
    if player.family != family:
        redirect('/home')

    #Add players found in the family to family members
    members = family.members.all()
    
    if player.family == family and not player in members:
        family.members.add(player)


    chats = Chat.objects.filter(
        Q(initiator = player) | Q(recipient = player)
    ).order_by("-last_message_time_sent")



    chats_data = [
        {
            "chat": chat,
            "last_message": get_last_message(chat)

        }
        for chat in chats
    ]

    

    family_last_message = FamilyMessage.objects.filter(family = player.family).order_by('-date_sent').first()
    if family_last_message:
        content =  decrypt_message(family_last_message.content)[:7]+'...'
        if family_last_message.image:
            content = f'sent an image'
        fl_message_data = {
            "sender":family_last_message.sender.user.username,
            'content': content,
            'image': family_last_message.image.url if family_last_message.image else None, 
            'date_sent': _date_time(family_last_message.date_sent)
        }
    else:
        fl_message_data = ''

    members = Player.objects.filter(family = family)        

    if check_family_membership(player, family):
        context = {
            "player":player,
            "family":family,
            "chats":chats_data,
            "family_last_message":fl_message_data,
            "members": members

            }   
        return render(request,"chat/family_chat.html",context)
    else:
        raise Http404

     