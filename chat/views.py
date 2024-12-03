
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse,Http404
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q
from users.models import Player,Family
from users.users_utility import get_player
import core.views as core_views
import uuid
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from utility import decrypt_message,_date_time,_time_since
from cryptography.fernet import Fernet




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
            'date_sent': _date_time(last_message.date_sent)
            }
    else:
        return ""
    

def get_player_last_seen(player:Player):
    last_seen = player.last_seen
    return _time_since(last_seen)

@login_required
def chats(request):
    current_player = get_player(request.user)
    if not current_player:
        return redirect('/users/signin')
    
    message_list=[]
    receivers = []
    
    chats = Chat.objects.filter(
        Q(initiator = current_player) | Q(recipient = current_player)
    ).order_by("-last_message_time_sent")
    
    #delete chats with no messages
    for chat in chats:
        chat_messages = Message.objects.filter(chat = chat)
        if not chat_messages.exists():
            chat.delete()

    chats_data = [
        {
            "chat": chat,
            "last_message": get_last_message(chat,"private")

        }
        for chat in chats
    ]

    family_last_message = FamilyMessage.objects.filter(family = current_player.family).order_by('-date_sent').first()
        
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

    context = {"chats":chats_data,
               "player":current_player,
               "family_last_message":fl_message_data,
               "n_notifs": core_views.get_notifs(current_player),
               }
    return render(request,"chat/chats.html",context)

def getchats(player):
    chats = Chat.objects.filter(
        Q(initiator = player) | Q(recipient = player)
    ).order_by("-last_message_time_sent")

    return chats

def get_messages(request,receiver_id):    
    #receiver_user = User.objects.get(username = receiver_name)
    receiver = Player.objects.get(id=receiver_id)
    sender = Player.objects.get(user=request.user)
    #messages = Message.objects.filter(Q(sender = sender or receiver) &
    #                                   Q(receiver = receiver or sender))
    messages = Message.objects.filter(
        Q(sender = sender) |  Q(sender=receiver), 
        Q(receiver = receiver) | Q(receiver = sender)).order_by("date_sent")
     
    messages_data = [{
        "id":message.id,
        "sender":{
            'username':message.sender.user.username,
            'profile_picture': message.sender.profile_picture.url
            },
        "receiver":{
            'username':message.receiver.user.username,
            'profile_picture': message.sender.profile_picture.url,
            },
        "content":decrypt_message(message.content),
        'image': message.image.url if message.image else None, 
        'date_sent': _date_time(message.date_sent)
        
        }
        for message in messages]
    return JsonResponse({"message":"success","messages":messages_data})

def get_family_messages(request, family_name):
    family = Family.objects.get(name = family_name)
    sender = Player.objects.get(user=request.user)

    messages = FamilyMessage.objects.filter(
        family = family
    ).order_by('date_sent')

    messages_data = [
        {   "id":message.id,          
            "sender":{
                        'username':message.sender.user.username,
                        'profile_picture': message.sender.profile_picture.url
                     },
                      "family":message.family.name,
                      "content":decrypt_message(message.content),
                      'image': message.image.url if message.image else None, 
                        'date_sent': _date_time(message.date_sent)
                      #"date_sent":str(message.date_sent.date().day)+"/"+str(message.date_sent.date().strftime("%B")) + " "+str(message.date_sent.time().strftime("%H:%M")) 
                       }for message in messages
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
        return JsonResponse({"status":"error"}) 
       
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
            'date_sent': _date_time(family_last_message.date_sent)
        }
    else:
        fl_message_data = ''    
        

    context = {"receiver":receiver,
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
            print("Existing chat between these two...")
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
            print("New chat between these two")
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

@login_required
def family_chat(request,family_name):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    family = Family.objects.get(name = family_name)
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

     