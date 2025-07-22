from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from api.utility import send_push_notification
import core.views as core_views
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required
from .models import *
from core.models import *
from battles.models import Battle, BattleRequest,Challenge, RefreeingProposal, TextPad,request_cost,battle_status
import battles.views as battle_views
import events.models as events_models

def create_post(request):
    if request.method == "POST":
        player = Player.objects.get(user = request.user)
        body = request.data.get("body")
        image = request.data.get('image')
        if body or image:
            postid = len(Post.objects.all()) + 1
            new_post = Post.objects.create(
                #id = postid,
                author=player,body=body,image = image)
            
            new_post_data = core_views._post_data(player,new_post)
            new_post.save()
            if body and len(body) > 30:
                users = User.objects.exclude(username = player.user.username)
                users = users.order_by('?')[:50] #get 15 random users
                for user in users:
                    send_push_notification(
                        PushSubscription.objects.filter(user = user).last(),
                        {
                            'title': f'{player}',
                            'body': f'{new_post.body[:30]}...',
                            'icon': f'{player.profile_picture.url}',
                            'url': f'/posts/{new_post.id}'
                        },
                    )

            return new_post_data 

def create_comment(request,post_id):
    body = request.data['body']
    if body != "":
        post  = get_object_or_404(Post, id = post_id)
        player = Player.objects.get(user = request.user)
        parent_id = request.POST.get("parent_id")
        parent = None
        notification_text = f"{player} a commenté votre publication" 
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
            notification_text = f"{player} a repondu ton commentaire sur une publication" 
        new_comment = Comment.objects.create(
            author = player,
            post = post,
            body = body,
            parent = parent,
        )

        #send a notification to the post author
        if player != post.author:
            new_notif = Notification.objects.create(
                target = post.author,
                content = notification_text,
                url = f'/posts/{post.id}',
                img_url = f"{player.profile_picture.url}"
            )
            new_notif.save()
            #send a push notification to the post author
            send_push_notification(PushSubscription.objects.filter(user = post.author.user).last(), {
                'title': notification_text,
                'body': f'{new_comment.body[:20]}...',
                'icon': f"{player.profile_picture.url}"
            })
        if new_comment.parent and new_comment.parent.author != new_comment.author:
            new_notif = Notification.objects.create(
                target = new_comment.parent.author,
                content = f"{player} a repondu a ton commentaire sur une publication",
                url = f'/posts/{post.id}',
                img_url = f"{new_comment.author.profile_picture.url}"
            )
            new_notif.save()
            #send a push notification to the post author
            send_push_notification(PushSubscription.objects.filter(user = new_comment.parent.author.user).last(), {
                'title': f"{new_comment.author} a repondu a ton commentaire sur une publication",
                'body': f'{new_comment.body[:20]}...',
                'icon': f"{new_comment.author.profile_picture.url}",
                'url' : f'/posts/{post.id}',
            },
            user = new_comment.parent.author.user
            )  


        new_comment.save()
        comment = core_views._get_comment(player, new_comment)
        return comment
            

def request_battle(request):
    if request.method == "POST":
        sender = Player.objects.get(user = request.user)
        character = request.data.get('character')
        type = request.data['type']
        message = ''
        #messages.success(request, "request created")
        if not character:
            message ="Choisi un personnage, clique sur l'image d'un personnage pour le selectionner et envoie ta requete" 
            return { "message": message, "request" : {} } 
        
        if type == "stake": 
            if sender.battle_points < request_cost:
                message = "Pas assez de Jetons de combat"    
                
            elif not sender.family:
                messages = "Tu dois étre dans une famille pour faire des combats STAKE"  
                
            else:    
                new_request = BattleRequest.objects.create(sender=sender,
                                                        character = character,
                                                            type = type)
                new_request.save()
                #deduct the battle points needed to start a battle
                core_views.remove_points(sender, request_cost)
                message = "Requète crée"
     
            #send a notif to the head of the family informing a member made a stake battle request
                return { "message": message, "request" : battle_views._battle_request_data(new_request)}
            
                
            
            
        elif type == "friendly":
            new_request = BattleRequest.objects.create(sender=sender,
                                                    character = character,
                                                        type = type)
            #SET THE EXPIRY DATE
            new_request.save()

            message="Requète crée"
        elif type == "":
            message = "Choisi le type de  combat"  
        sender.save()    

        return { "message": message, "request" : battle_views._battle_request_data(new_request) }
    

def send_textpad(request, battle_id):
    battle = Battle.objects.get(id = battle_id)
    player = Player.objects.get(user=request.user)
    textpads = TextPad.objects.filter(battle = battle)
    if len(textpads)>0:
        last_textpad = textpads.last()
        l_sender  = last_textpad.owner
    else:
        l_sender = None 
    
    message = "impossible  d'envoyé le pavé"
    #create the textpad and update battle status

    #To verify:
    #player can send a textpad
    #it is player's turn
    #player is a fighter in the battle(either initiator or opponent)
    #it is the player's turn
    text = request.data['text']

    hidden_action = request.data.get('hidden_action', '')
    if player == battle.initiator or player == battle.opponent:
        #check if player can send the first textpad
        if len(textpads) == 0 and player != battle.initiator:
            message = f"C'est a ton adversaire {battle.initiator} d'envoyer le premier pavé"
        elif len(text) == 0:
            message = "Le pavé ne peut pas étre vide" 
        elif l_sender == player:
            message = "C'est le tour de ton adversaire d'envoyé son pavé"
        elif not battle.can_send_textpad:
            message = "L'adversaire doit validé le dernier pavé avant de continuer"
        else:        
            text_pad = TextPad.objects.create(
                owner = player,
                battle= battle,
                text=text,
                hidden_action = hidden_action
            )
            battle.status = battle_status[2]
            if battle.type == 'tournament':
                tournament = events_models.TournamentBattle.objects.get(battle = battle).tournament
                tournament.status = 'ongoing'

            battle.can_send_textpad = False

            #determine the opponent of the player sending the textpad    
            if text_pad.owner == battle.initiator:
                opponent = battle.opponent
            elif text_pad.owner == battle.opponent:
                opponent = battle.initiator    

            
            new_notif = Notification.objects.create(
                target = opponent,
                url = f'/battles/battle_room/{battle_id}',
                content = f'{player} a envoyé son pavé dans votre combat',
            )

            #send push notification to the opponent and the referee
            send_push_notification(
                PushSubscription.objects.filter(user = opponent.user).last(),
                {
                'title' : f"Ton adversaire a envoyé son pavé",
                'body' : f"{player} a envoyé son pavé dans votre combat.",
                'url' : f'/battles/battle_room/{battle_id}',
                'icon' : '/static/images/logo/logo_1.png',
                },
                
            )

            if battle.refree:
                new_notif2 = Notification.objects.create(
                    target = battle.refree,
                    url = f'/battles/battle_room/{battle_id}',
                    content = f"{player} a envoyé un pavé, tu dois l'évaluer",
                )
                new_notif2.save()
                send_push_notification(
                    PushSubscription.objects.filter(user = battle.refree.user).last(),
                    {
                    'title' : f"Un pavé a été envoyé",
                    'body' : f"{player} a envoyé un pavé, tu dois l'évaluer",
                    'url' : f'/battles/battle_room/{battle_id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                )
            

            
            battle.save()
            text_pad.save()
            new_notif.save()
            
            message = 'pavé envoyé'

            return { 'message':message , 'textpad': battle_views._textpad_data(player,text_pad) }

    