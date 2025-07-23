from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from api.utility import send_push_notification
import core.views as core_views
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required

from users.users_utility import get_player
from utility import _parse_number
from .models import *
from core.models import *
from battles.models import Battle, BattleAcceptor, BattleRequest,Challenge, RefreeingProposal, TextPad, TextPadComment, TextpadReactor,request_cost,battle_status, battle_types,accept_cost
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

def react_post(request,post_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user) 
        post  = get_object_or_404(Post, id = post_id)
        reactions = Reaction.objects.filter(post = post, player = player)   

        reactions_data = [
            {"type":reaction.type,
             "player": str(reaction.player),
             "post": reaction.post.id,
             } for reaction in reactions
        ]
        for reaction in reactions:
            if reaction.player == player:
                
                reaction.delete()
                post.likes = post.likes - 1
                
                post.save()
                return {'message':'unliked','likes':post.likes}
        
            
        reaction = Reaction.objects.create(
            player = player,
            post = post,
            type = 'like',
        )
        
        post.likes = post.likes + 1
        reaction.save()
        post.save()

        #Send Push Notification if likes exceeds 10
        if post.likes == 5:
            send_push_notification(PushSubscription.objects.filter(user = post.author.user).last(), {
                'title': 'Votre publication a été aimé par 5 personnes',
                'body': f'Votre publication a été aimé par 5 personnes',
                'icon': '/static/images/logo/logo_1.png'
            },  )
        
        
        return {"message":"liked",'likes':post.likes}
    
    return {"status":"error"}    

def react_comment(request, comment_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user) 
        comment  = get_object_or_404(Comment, id = comment_id)
        reactions = CommentReaction.objects.filter(comment = comment, player = player)

        reactions_data = [
            {
            "type":reaction.type,
            "player": str(reaction.player),
            "comment": reaction.comment.id,
             
            } for reaction in reactions
        ]
        for reaction in reactions:
            if reaction.player == player:
                
                reaction.delete()
                comment.likes = comment.likes - 1
                
                comment.save()
                likes = len(CommentReaction.objects.filter(comment = comment))

                return {'message':'unliked','likes': _parse_number(likes)}
            
        reaction = CommentReaction.objects.create(
            player = player,
            comment = comment,
            type = 'like',
        )
        
        comment.likes = comment.likes + 1
        if comment.author != player:
            notif = Notification.objects.create(
                target = comment.author,
                content = f'{player} liked your comment: {comment.body[:10]}...',
                url = f'/posts/{comment.post.id}',
            )
            notif.save()

        reaction.save()
        comment.save()
        
        likes = len(CommentReaction.objects.filter(comment = comment))
        #Send Push Notification if likes exceeds 10
        if likes == 10:
            send_push_notification(PushSubscription.objects.filter(user = comment.author.user).last(), {
                'title': 'Votre commentaire a été aimé par 10 personnes',
                'body': f'Votre commentaire sur la publication de {comment.post.author} a été aimé par 10 personnes',
                'icon': '/static/images/logo/logo_1.png'
            })
        return {"message":"liked",'likes':_parse_number(likes)}
    
    return {"status":"error"}

def react_to_textpad(request, textpad_id):
    textpad = get_object_or_404(TextPad, id = textpad_id)
    player = get_player(request.user)

    if request.method == 'POST':
        
        reaction = request.data.get('reaction','😂')
        
        reactors = textpad.reactors.all()

        if player in reactors:
            player_reaction = TextpadReactor.objects.get(player = player, textpad = textpad)
            if reaction == player_reaction.type:
                textpad.reactors.remove(player)
            else:
                player_reaction.type = reaction  
                player_reaction.save()      
        else:
            textpad.reactors.add(player, through_defaults={'type': reaction})
            if player == textpad.owner:
                new_notif = Notification.objects.create(
                        target = textpad.owner,
                        url = f'/battles/battle_room/{textpad.battle.id}',
                        content = f"{player} a reagi a ton  pavé",
                        img_url = player.profile_picture.url
                    )
                new_notif.save()
                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = textpad.owner.user).last(),
                    {
                    'title' : f"Nouvelle reaction sur ton pavé",
                    'body' : f"{player} a reagi par '{reaction}' a ton pavé",
                    'url' : f'/battles/battle_room/{textpad.battle.id}',
                    'icon' : player.profile_picture.url,
                    },
                    
                )

        textpad.save()
        reactions = [ battle_views._textpad_reactions_data(reactor) for reactor in TextpadReactor.objects.filter(textpad = textpad)]

        return reactions

def add_textpad_comment(request, textpad_id):
    if request.method == 'POST':
        textpad = get_object_or_404(TextPad, id=textpad_id)
        author = get_player(request.user)  # Assuming Player is linked to User
        text = request.POST.get("body")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(TextPadComment, id=parent_id)

        comment = TextPadComment.objects.create(
            textpad=textpad, author=author, text=text, parent=parent
        )
        comment.save()

        if comment.author != textpad.owner:
            if comment.parent:
                if comment.parent.author != comment.author:
                    new_notif = Notification.objects.create(
                        target = comment.parent.author,
                        url = f'/battles/battle_room/{textpad.battle.id}',
                        content = f"{comment.author} a repondu a ton commentaire sur un pavé",
                        img_url = comment.author.profile_picture.url
                    )
                    new_notif.save()
                    #send push notification to the opponent and the referee
                    send_push_notification(
                        PushSubscription.objects.filter(user = comment.parent.author.user).last(),
                        {
                        'title' : f"Nouvelle reaction sur ton pavé",
                        'body' : f"{comment.author} a repondu a ton commentaire sur un pavé",
                        'url' : f'/battles/battle_room/{textpad.battle.id}',
                        'icon' : '/static/images/logo/logo_1.png',
                        },   
                    )
            else:
                new_notif = Notification.objects.create(
                    target = textpad.owner,
                    url = f'/battles/battle_room/{textpad.battle.id}',
                    content = f"{comment.author} a commenté ton pavé dans un combat",
                    img_url = comment.author.profile_picture.url
                )
                new_notif.save()
                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = textpad.owner.user).last(),
                    {
                    'title' : f"Nouvelle reaction sur ton pavé",
                    'body' : f"{comment.author} a repondu a ton commentaire sur un pavé",
                    'url' : f'/battles/battle_room/{textpad.battle.id}',
                    'icon' : comment.author.profile_picture.url,
                    },  
                ) 
        return battle_views._textpad_comment_data(comment)

def request_battle(request):
    if request.method == "POST":
        sender = Player.objects.get(user = request.user)
        character = request.data.get('character')
        type = request.data['type']
        
        #messages.success(request, "request created")
        if not character:
            message = "Choisi un personnage, clique sur l'image d'un personnage pour le selectionner et envoie ta requete"
            return {'message':message} 
        
        if type == "stake": 
            if sender.battle_points < request_cost:
                message = "Pas assez de Jetons de combat"
                
            elif not sender.family:
                message="Tu dois étre dans une famille pour faire des combats STAKE" 
            else:    
                new_request = BattleRequest.objects.create(sender=sender,
                                                        character = character,
                                                            type = type)
                new_request.save()
                #deduct the battle points needed to start a battle
                core_views.remove_points(sender, request_cost)
                message = "Requète crée"
                return {'message':message, "request" : battle_views._battle_request_data(new_request)}
                #send a notif to the head of the family informing a member made a stake battle request
        elif type == "friendly":
            new_request = BattleRequest.objects.create(sender=sender,
                                                    character = character,
                                                        type = type)
            #SET THE EXPIRY DATE
            new_request.save()
            message = "Requète crée"
            return JsonResponse({'message':message, "request" : battle_views._battle_request_data(new_request)})
        elif type == "":
            message="Choisi le type de  combat"
        sender.save()    
        return {'message':message} 

def accept_battle(request,request_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user)
        character = request.data['character']
        b_request = get_object_or_404(BattleRequest, id = request_id)
        
        #limit the number of acceptances for a battle to 3
        acceptors = BattleAcceptor.objects.filter(request = b_request)
        message = ''

        #check if the sender of the request is of the same family with the acceptor for STAKE requests
        if  b_request.type == battle_types[1] and player.family == b_request.sender.family:
            message = 'Vous ne pouvez pas faire des combats stake contre des membres de votre famille'
        elif not player.family and b_request.type == battle_types[1]:
            message = 'Vous devez étre dans une famille pour faire des combats stake'
        #check if there are more than 3 acceptors for the request already    
        elif len(acceptors)>=2:
            b_request.hidden = True
            message = "2 combats ont deja été initié de cette RDC"
        
        #check if the player has already accepted this request
        elif BattleAcceptor.objects.filter(player = player, request = b_request).exists():
            message = "Vous avez deja accepté cette RDC"

        elif  b_request.type == battle_types[1] and player.battle_points < accept_cost:
            message = "Vous n'avez pas assez de Jeton de Combat pour accepter cette requète"
        #create the acceptance if everything is ok
        else:    
            acceptor = BattleAcceptor.objects.create(
                player = player,
                request = b_request,
                character = character
            )
            core_views.remove_points(player, accept_cost)
            # NOTIFY The head of the family if it is a stake battle
            if b_request.type == 'stake':
                    try:
                        god_father_user = player.family.god_father
                        god_father = Player.objects.get(Player, user = god_father_user)

                        notif = Notification.objects.create(
                            target = god_father,
                            url = '/battles',
                            content = f'{player} A accepté un combat stake pour votre famille',
                        )
                        notif.save()
                    except Exception as e:
                        print("An error occured sending notif to a god father in accept_battle view")    

            new_notif = Notification.objects.create(
                target = b_request.sender,
                content = f"{player} a accepté ta requète de combat, clique pour aller commencer le combat",
                url = f'/users/requests/{b_request.sender.user.username}',
            )
            send_push_notification(
                PushSubscription.objects.filter(user = b_request.sender.user).last(),
                {
                'title' : f"Ton combat peut Commencer",
                'body' : f"{player} a accepté ta requète de combat, clique pour commencer le combat",
                'url' : f'/users/requests/{b_request.sender.user.username}',
                'icon' : '/static/images/logo/logo_1.png',
                },
                player.user
            )
            player.save()
            acceptor.save()
            new_notif.save()
            return {"message":"Combat accepté, en attente d'arbitrage"}
        return {"message":message}  