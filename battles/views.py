from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse,Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from moderator.models import Moderator
from .models import *
from django.db.models import Q
from users.models import Player,Family,PlayerStat,PlayerNotification,notification_types,rankings,Badge,PlayerBadge
from users.users_utility import get_player
import core.models as core_models
import events.models as events_models
import events.views as events_views
import uuid
from datetime import datetime
from utility import get_characters,get_refree_questions,_parse_number,_time_since, get_solo_battle_characters, _solo_battle_character
import json
from django.views.decorators.csrf import csrf_exempt
import core.views as core_views
import users.views as users_views
import random
from api.models import PushSubscription
from api.utility import send_push_notification
from .solo_battle import *
from .solo_battle import _evaluate_actions, _bot_action, _log_actions
from .solo_battle import _bot_action_minimax
from pathlib import Path
import random

BASE_DIR = Path(__file__).resolve().parent

#manage progressions after a battle
#manage BP for starting a battle
#refree quizz

def _character_jutsus(name:str):
    characters = get_characters() 
    for character in characters['playable_characters']:
        if str(character['name']).lower() == name.lower():
            jutsus = character.get('jutsu','No Jutsu')
            return jutsus  

def _character(name:str):
    characters = get_characters() 
    for character in characters['playable_characters']:
        if str(character['name']).lower() == name.lower():
            
            return character 

            
            return character                  

def update_battle_spectators(player:Player, battle:Battle):
    spectators = battle.spectators.all()
    
    if player in spectators:
       
       return
    elif battle.status != 'ongoing':
        
        return
    elif player == battle.initiator or player == battle.opponent:
        return
    else:
        
        battle.spectators.add(player)
        battle.save()  

def can_refree(player:Player,battle:Battle):
    #check if player can refree  the battle
    #can refree if:
    #   battle status is  waiting_refree
    #   battle has no refree
    #   player is not a fighter in the battle

    if battle.status == battle_status[0] and not battle.refree:  
        if battle.initiator != player  and battle.opponent != player:  
            return True    
        
    return False

def battle_result(player, battle):
    if battle.status == 'finished':
        if battle.winner == player:
            return "win"
        else:
            return "defeat"
    else:
        return "TBD"    

def _referee_proposals_data(proposals):
    data = [{
        "id": proposal.id,
        "player":{
            "id": proposal.player.id,
            "player": str(proposal.player),
            "username": proposal.player.user.username,
            "rank": proposal.player.rank,
            "profile_picture": proposal.player.profile_picture.url,
        },
        
        "ratings": round((get_referee_rating(proposal.player)['timeliness']+get_referee_rating(proposal.player)['communication']+get_referee_rating(proposal.player)['fairness'])/3, 1),
        "date_sent":  _time_since(proposal.date_sent),

    } for proposal in proposals ]
    return data

def _referee_proposals(battle:Battle, player:Player):
    if player == battle.initiator:
        return  _referee_proposals_data(RefreeingProposal.objects.filter(battle = battle))
    else:
        return None

def _battle_data(player,battle):
    data = {
            "feed_item":'battle',
            "id":battle.id,
            "status": battle.status,
            "isFighter":player == battle.opponent or player == battle.initiator,
            "initiator": {
                "id": battle.initiator.id,
                "player":str(battle.initiator),
                "username": battle.initiator.user.username,
                "profile_picture": battle.initiator.profile_picture.url,
                "rank":battle.initiator.rank,
                'nickname': battle.initiator.nickname if battle.initiator.nickname else "No nickname",
                },
            "opponent": {
                "id": battle.opponent.id,
                "player":str(battle.opponent),
                "username": battle.opponent.user.username,
                "profile_picture": battle.opponent.profile_picture.url,
                "rank":battle.opponent.rank,
                "nickname": battle.opponent.nickname if battle.opponent.nickname else "No nickname",
                },
            "refree": {
                "id": battle.refree.id,
                "player":str(battle.refree),
                "username": battle.refree.user.username,
                "profile_picture": battle.refree.profile_picture.url,
                "rank":battle.refree.rank,
                "rating": 2,
                } if battle.refree else None, 
            "winner": {
                "id":battle.winner.id,
                "player":str(battle.winner),
            } if battle.winner else None,
            "result": battle_result(player=player, battle=battle),       
            "i_character": battle.i_character,
            "o_character": battle.o_character,
            "type":battle.type,
            "can_refree": can_refree(player, battle),
            "spectators": _parse_number(len(battle.spectators.all()), True),
            "referee_proposals": _referee_proposals(battle,player),
            "date": core_views._time_since(battle.date_started),
        }
    return data

def _battles_data(player:Player,battles):
    
    data = [
        {   
            "feed_item":'battle',
            "id":battle.id,
            "status": battle.status,
            "isFighter":player == battle.opponent or player == battle.initiator,
            "initiator": {
                "id": battle.initiator.id,
                "player":str(battle.initiator),
                "username": battle.initiator.user.username,
                "profile_picture": battle.initiator.profile_picture.url,
                "rank":battle.initiator.rank,
                "nickname": battle.opponent.nickname if battle.opponent.nickname else battle.initiator.user.username,
                },
            "opponent": {
                "id": battle.opponent.id,
                "player":str(battle.opponent),
                "username": battle.opponent.user.username,
                "profile_picture": battle.opponent.profile_picture.url,
                "rank":battle.opponent.rank,
                "nickname": battle.opponent.nickname if battle.opponent.nickname else battle.opponent.user.username,
                },
            "refree": {
                "id": battle.refree.id,
                "player":str(battle.refree),
                "username": battle.refree.user.username,
                "profile_picture": battle.refree.profile_picture.url,
                "rank":battle.refree.rank,
                "rating": 2,
                } if battle.refree else None, 
            "winner": {
                "id":battle.winner.id,
                "player":str(battle.winner),
            } if battle.winner else None,
            "result": battle_result(player=player, battle=battle),       
            "i_character": battle.i_character,
            "o_character": battle.o_character,
            "type":battle.type,
            "can_refree": can_refree(player, battle),
            "spectators": _parse_number(len(battle.spectators.all()),True),
            "referee_proposals":_referee_proposals(battle,player),
            "date": core_views._time_since(battle.date_started),
        } for battle in battles
    ]

    return data

def _battle_requests_data(player:Player,battle_requests):
    data = [
        {
            "id":request.id,
            "type": request.type,
            "sender": {
                "player":str(request.sender),
                "username": request.sender.user.username,
                "profile_picture": request.sender.profile_picture.url,
                "rank":request.sender.rank,
                },
            "character": request.character,
            "date_sent": core_views._time_since(request.date_sent),
            

        } for request in battle_requests
    ]

    return data

def _isReferee(player:Player):
    isRefree = False

    player_badges = player.badges.all()
    referee_badge = Badge.objects.get(title = 'Referee')
    if referee_badge in player_badges:
        return True
    
    return False

@login_required
def battles(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    # jsonTest = JsonTestModel.objects.create(
    #     json_data = {
    #         "name": "John",
    #         "age": 30,
    #         "city": "New York"
    #     }
    # )
    # jsonTest.save()
    # print(jsonTest.json_data['name'])
    characters = get_characters()
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"])
    battles = Battle.objects.all().order_by('-date_started')
    #requests = BattleRequest.objects.filter(hidden = False).exclude(sender = player).order_by('-date_sent')
    requests = BattleRequest.objects.filter(hidden = False).order_by('-date_sent')

    #remove requests where 2 battles had already being inititated from 
    for req in requests:
        if len(Battle.objects.filter(request = req)) >=2:
            req.hidden = True 

    #get the request senders
    
    request_senders = [ ]
    for req in requests:
        if req.sender not in request_senders:
            request_senders.append(req.sender)
    
    requests_list2 = [
        {
            f'sender': sender,
            'requests' : requests.filter(sender = sender),
            'length' : len(requests.filter(sender = sender)),
        } for sender in request_senders 
    ]
    # print(request_senders)
    # print(requests_list2)
    requests_list = []

    #Show Number of battles initiated for each request  

    #remove requests where 3 battles had already being inititated from 
    # for b_request in requests:
    #     r_battles = Battle.objects.filter(request = b_request)
    #     if len(r_battles)<=2:
    #         requests_list.append(b_request)

    battles_data = _battles_data(player, battles)

    context = {"requests":requests_list,
               "packed_requests":requests_list2,
               "characters":sorted_characters,
               "player":player,
               "n_notifs":core_views.get_notifs(player),
               "battles":battles_data
               }
    return render(request,"battles/battles.html",context)

def create_request(sender:Player, character:str, type:str):
    

    new_request = BattleRequest.objects.create(sender=sender,
                                                        character = character,
                                                            type = type)
    
    #SET THE EXPIRY DATE and other details HERE

    if type == battle_types[0]:
        request_cost = f_request_cost
    elif type == battle_types[1]:
        request_cost = s_request_cost
    else:
        request_cost = 400

    sender.battle_points = sender.battle_points - request_cost
    new_request.save()
    sender.save()

    #push notify some players a new request has been sent
    for player in Player.objects.exclude(sender):
        if player.family != sender.family:
            send_push_notification(
                PushSubscription.objects.filter(user = player.user).last(),
                {
                'title' : f"Requète de combat",
                'body' : f"{sender} a envoyé une requète de combat, clique pour répondre",
                'url' : '/battles',
                'icon' : '/static/images/logo/logo_1.png',
                },
                
            )



    return new_request

def request_battle(request):
    if request.method == "POST":
        sender = Player.objects.get(user = request.user)
        character = request.POST.get('character')
        type = request.POST['type']
        
        #messages.success(request, "request created")
        if not character:
            messages.error(request,"Choisi un personnage, clique sur l'image d'un personnage pour le selectionner et envoie ta requete") 
            return HttpResponseRedirect(reverse("battles:index")) 
        
        if type == "stake": 
            if sender.battle_points < request_cost:
                messages.error(request,"Pas assez de Jetons de combat")    
                
            elif not sender.family:
                messages.error(request,"Tu dois étre dans une famille pour faire des combats STAKE")    
                
            else:    
                new_request = BattleRequest.objects.create(sender=sender,
                                                        character = character,
                                                            type = type)
                new_request.save()
                #deduct the battle points needed to start a battle
                core_views.remove_points(sender, request_cost)
                messages.success(request,"Requète crée, ")

                
                #send a notif to the head of the family informing a member made a stake battle request
            
                
            
            
        elif type == "friendly":
            new_request = BattleRequest.objects.create(sender=sender,
                                                    character = character,
                                                        type = type)
            #SET THE EXPIRY DATE
            new_request.save()

            messages.success(request,"Requète crée")
        elif type == "":
            messages.error(request,"Choisi le type de  combat")  
        sender.save()    

        return HttpResponseRedirect(reverse("battles:index")) 
                    
        
    
def accept_battle(request,request_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user)
        character = request.POST['character']
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

                        notif = core_models.Notification.objects.create(
                            target = god_father,
                            url = '/battles',
                            content = f'{player} A accepté un combat stake pour votre famille',
                        )
                        notif.save()
                    except Exception as e:
                        print("An error occured sending notif to a god father in accept_battle view")    

            new_notif = core_models.Notification.objects.create(
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
            return JsonResponse({"status":"success","message":"Combat accepté, en attente d'arbitrage"})
        
        
        return JsonResponse({"status":"failed","message":message})
        


def init_battle(request,acceptor_id):
    player = get_object_or_404(Player, user = request.user) 
    if request.method == "POST":
        try:
            battle_acceptor = BattleAcceptor.objects.get(id = acceptor_id)
        except:
            message = 'Battle acceptance does not exist'
            return JsonResponse({"status":"failed","message":message})
        
        battle_request = battle_acceptor.request
        initiator = Player.objects.get(user = request.user)
        message = ''

        #check if there is already a battle from that request between the two players
        if player == battle_request.sender:
            
            if Battle.objects.filter(
                initiator = initiator,
                opponent = battle_acceptor.player,
                request = battle_request,
            ).exists():
                
                message = 'Ce combat a deja été initié'
            else:
                
                #all_battles = Battle.objects.all()
                new_battle = Battle.objects.create(
                    #id = len(all_battles)+1,
                    initiator = initiator,
                    i_character = battle_request.character,
                    opponent = battle_acceptor.player,
                    o_character = battle_acceptor.character,
                    type = battle_request.type,
                    request = battle_request,

                )

                #delete request if there are more than 3 persons that have accepted
                # if len(BattleAcceptor.objects.filter(request = battle_request))>=2:
                #     battle_request.delete()

                if len(Battle.objects.filter(request = battle_request))>=2:
                    #battle_request.delete()
                    battle_request.hidden = True
                    battle_request.save()
                    pass    
                    
                
                #Notify the acceptor
                new_notif = core_models.Notification.objects.create(
                    content = f"Ton combat contre {player} a été initié, un arbitre doit maintenant etre designé",
                    target = battle_acceptor.player,
                    url = f'/users/battles/{battle_acceptor.player.user.username}'

                )
                new_notif.save()
                send_push_notification(
                PushSubscription.objects.filter(user = battle_acceptor.player.user).last(),
                {
                'title' : f"Message de {battle_acceptor.player.user.username}",
                'body' : f"Ton combat contre {player} a été initié, un arbitre doit maintenant etre designé",
                'url' : f'/users/battles/{battle_acceptor.player.user.username}',
                'icon' : '/static/images/logo/logo_1.png',
                },
                battle_acceptor.player.user
                
            )


                new_battle.save()
                message = "combat initiée, maintenant en attente d'un arbitre"
                return JsonResponse({"status":"success","message": message})
        else:
            message = "Vous n'etes pas l'auteur de la requète"    
        
    return JsonResponse({"status":"failed","message":message})





def filter_battle(request, filter_num):
    if request.method == "GET":
        #filter_num = int(request.GET['filter'])
        player = get_player(request.user)
        if not player:
            return redirect('/users/signin')
        battles = Battle.objects.filter(status = battle_status[filter_num]).order_by('-date_started')
        if filter_num == 0:
            battles = battles.exclude(
                Q(initiator=player) | Q(opponent=player)
            )
        context = {"player":player,"battles":battles}
        message = "..."
        battles_data = _battles_data(player, battles)
        return JsonResponse({"status":"success", "message":message ,"battles":battles_data})
    return JsonResponse({"status":"error", "message":"Une erreur s'est produite"})

def battle_requests(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    requests = BattleRequest.objects.filter(hidden = False).exclude(sender = player).order_by('-date_sent')
    
    requests_data = _battle_requests_data(player, requests)
    return JsonResponse({"status":"success","requests":requests_data})    

def waiting_refree(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    battles = Battle.objects.filter(status = battle_status[0])
    context = {"player":player,"battles":battles}
    battles_data = [
        {
            "initiator": str(battle.initiator),
            "opponent": str(battle.opponent),
            "i_character": battle.i_character,
            "o_character": battle.o_character
        } for battle in battles
    ]
    return JsonResponse({"status":"success","battles":battles_data})

def not_yet_started(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    battles = Battle.objects.filter(status = battle_status[1])
    context = {"player":player,"battles":battles}

    return render(request, "battles/not_started.html", context)

@csrf_exempt
def refree_proposal(request, battle_id):
    if request.method == "POST":
        battle = Battle.objects.get(id = battle_id)
        player = Player.objects.get(user=request.user)
        refree_badge = Badge.objects.get(title = 'Referee')
        player_badges = player.badges.all()
        message = ''
        if RefreeingProposal.objects.filter(player = player, battle = battle).exists():
            message = 'Tu as déja fait une proposition pour ce combat'

        else:
            if battle.type == battle_types[1]: #At stake battles
                #check if the player is an official referee for him to make a proposal 
                if refree_badge in player_badges:
                    new_notif = PlayerNotification.objects.create(
                    sender = player,
                    target = battle.initiator,
                    notif_type = "refree_proposal",
                    )    
                    new_proposal = RefreeingProposal.objects.create(player=player, battle=battle)
                    new_proposal.save()
                    new_notif.save()
                    return JsonResponse({"status":"success","message":"Proposition envoyé"})
                else:
                    message = "Tu dois étre un arbitre officiel pour arbitrer un combat STAKE , Fais le teste d'arbitrage pour devenir arbitre officiel"
            else:
                notification_url = f'/users/challenges/{battle.initiator.user.username}' if battle.type == 'challenge' else f'/users/requests/{battle.initiator.user.username}'
                new_notif = core_models.Notification.objects.create(
                target = battle.initiator,
                content = f"{player} veut arbitrer un de tes combats, clique pour répondre",
                url = notification_url,
                )    
                new_proposal = RefreeingProposal.objects.create(player=player, battle=battle)
                new_proposal.save()
                new_notif.save()

                send_push_notification(
                    PushSubscription.objects.filter(user = battle.initiator.user).last(),
                    {
                    'title' : f"Proposition d'arbitrage",
                    'body' : f"{player} veut arbitrer un de tes combats, clique pour répondre",
                    'url' : notification_url,
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )

                return JsonResponse({"status":"success","message":"Proposition envoyé"})


    return JsonResponse({"status":"failed","message":message})

def validate_refree(request, proposal_id):
    player = get_object_or_404(Player, user = request.user) 
    if request.method == "POST":
        proposal = get_object_or_404(RefreeingProposal, id = proposal_id)

        response = request.POST.get('response')

        battle = proposal.battle
        message = ''
        if player == proposal.battle.initiator:
            if response != "accepted":
                message = "Proposition refusé"
                new_notif = core_models.Notification.objects.create(
                    target = proposal.player,
                    content = f"ta proposion d'arbitrer {battle.initiator} v {battle.opponent} a été refusé",
                    url = '/battles',
                ) 

                new_notif.save()   

                proposal.delete()

            elif battle.refree:
                message = "Il ya déja un arbitre pour ce combat"
            
            else:    
                battle.refree = proposal.player
                battle.status = battle_status[1]
                new_notif = core_models.Notification.objects.create(
                    target = battle.opponent,
                    content = f'ton combat contre {battle.initiator} est prét a commencé',
                    url = f'/battles/battle_room/{battle.id}',
                ) 
                new_notif2 = core_models.Notification.objects.create(
                    target = proposal.player,
                    content = f"ta proposition d'arbitrer le combat {battle.initiator} vs {battle.opponent} a été accepté, tu dois a présent mettre en place les régles du combat",
                    url = f'/battles/battle_room/{battle.id}',
                ) 
                new_notif.save() 
                new_notif2.save()

                send_push_notification(
                    PushSubscription.objects.filter(user = battle.opponent.user).last(),
                    {
                    'title' : f"Ton combat peut Commencer",
                    'body' : f"ton combat contre {battle.initiator} est prét a commencé",
                    'url' : f'/battles/battle_room/{battle.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )

                send_push_notification(
                    PushSubscription.objects.filter(user = proposal.player.user).last(),
                    {
                    'title' : f"Proposition d'arbitrage acceptée",
                    'body' : f"Ta proposition d'arbitrer le combat {battle.initiator} vs {battle.opponent} a été accepté, tu dois a présent mettre en place les régles du combat",
                    'url' : f'/battles/battle_room/{battle.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )

                battle.save()
                proposal.save()
                new_notif.save()
                message = "Arbitre validé, maintenant en attente du premier pavé"
                return JsonResponse({"status":"success","message": message})
        else:
            message = "Tu es l'auteur de la requète "
    return JsonResponse({"status":"failed","message":message})


def get_textpad_character(battle:Battle,textpad):
    if textpad.owner == battle.initiator:
        return battle.i_character
    elif textpad.owner == battle.opponent:
        return battle.o_character 
    else:
        return "personnage non-attribué"

def _canRateReferee(player:Player,battle:Battle):
    can_rate = False
    status = battle.status
    if status == "finished" and  (player == battle.initiator or player == battle.opponent):
        can_rate = True

def referee_rated(battle:Battle):
    initiator_rated = RefereeRating.objects.filter(battle = battle, player = battle.initiator).exists()
    opponent_rated = RefereeRating.objects.filter(battle = battle, player=battle.opponent).exists()
    if initiator_rated and opponent_rated:
        return True
    else:
        return False 

@login_required
def battle_room(request,battle_id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    battle = Battle.objects.get(id=battle_id)
    
    update_battle_spectators(player,battle)
    
    
    rules = Rule.objects.filter(battle = battle)
    

    role = "Spectateur"
    
    if player == battle.refree:
        role = "Arbitre"
        
    elif player == battle.initiator or player == battle.opponent:
        role = "Combattant"    

    ch_jutsus = ''
    character = ''
    i_character =  _character(battle.i_character)
    o_character = _character(battle.o_character)
    if player == battle.initiator:
        ch_jutsus = _character_jutsus(battle.i_character)
        character = _character(battle.i_character)
    if player == battle.opponent:
        ch_jutsus = _character_jutsus(battle.o_character)    
        character = _character(battle.o_character)


    textpads = TextPad.objects.filter(battle = battle)

    if len(textpads)>0:
        last_textpad = textpads.last()
        l_sender  = last_textpad.owner
    else:
        l_sender = None    

    textpads_data = [
        {
            "textpad":textpad,
            "character":get_textpad_character(battle, textpad)
        }
        for textpad in textpads 
    ]
    
    #get the last player to send a  textpad
    def can_rate(battle:Battle):
        if player == battle.refree:
            return False
        elif battle.type == 'friendly':
            return False
        elif RefereeRating.objects.filter(battle = battle, player = player).exists():
            return False
        elif player != battle.initiator and player != battle.opponent:
            return False    
        elif len(RefereeRating.objects.filter(battle = battle)) >= 2:
            return False
        elif battle.status != 'finished':
            return False
        else:
            return True

            
     
    
    context = {"player":player,
               "battle":battle,
               
               "rules":rules, 
               "rules_set": len(rules) >= 3,
               "textpads":textpads_data,
               "last_textpad": textpads_data[-1] if len(textpads_data)>0 else "",
               'jutsus': ch_jutsus,
               'i_character': i_character,
               'o_character': o_character,
               'spectators':  _parse_number(len(battle.spectators.all()),True),
                 "last_sender":l_sender,
                 "role":role,
                 "can_rate": can_rate(battle),
                 'referee_rated': referee_rated(battle),
                 "n_notifs":core_views.get_notifs(player=player),
                 

                 }
    
    if referee_rated(battle):
        initiator_rating = RefereeRating.objects.get(player = battle.initiator,battle = battle)
        # initiator_rating_data = {
        #     'player': {
        #         'username': str(initiator_rating.player),
        #         'player': initiator_rating.player.user.username,
        #     },
        #     'fairness': initiator_rating.fairness,
        #     'communication': initiator_rating.communication,
        #     'timeliness':initiator_rating.timeliness,
        # }
        opponent_rating = RefereeRating.objects.get(player = battle.opponent,battle = battle)
        ratings = [
            { 'category': 'Timeliness', 'initiator': initiator_rating.timeliness, 'opponent': opponent_rating.timeliness  },
            {'category': 'Communication', 'initiator': initiator_rating.communication, 'opponent': opponent_rating.communication},
            {'category': 'Fairness', 'initiator': initiator_rating.fairness, 'opponent': opponent_rating.fairness }
        ]
        opponent_rating = RefereeRating.objects.filter(player = battle.opponent).last()
        context['initiator_rating'] = initiator_rating
        context['opponent_rating'] = opponent_rating
        context['ratings'] = ratings

    return render(request,"battles/battle_room.html", context)

def send_textpad(request, battle_id):
    battle = Battle.objects.get(id = battle_id)
    player = Player.objects.get(user=request.user)
    textpads = TextPad.objects.filter(battle = battle)
    if len(textpads)>0:
        last_textpad = textpads.last()
        l_sender  = last_textpad.owner
    else:
        l_sender = None 
    if request.method == "POST":
        message = "impossible  d'envoyé le pavé"
        #create the textpad and update battle status

        #To verify:
        #player can send a textpad
        #it is player's turn
        #player is a fighter in the battle(either initiator or opponent)
        #it is the player's turn
        text = request.POST['text']

        hidden_action = request.POST.get('hidden_action', '')
        if player == battle.initiator or player == battle.opponent:
            #check if player can send the first textpad
            if len(textpads) == 0 and player != battle.initiator:
                message = f"L'adversaire {battle.initiator} doit envoyé le premier pavé"
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

                
                new_notif = core_models.Notification.objects.create(
                    target = opponent,
                    url = f'/battles/battle_room/{battle_id}',
                    content = f'{player} a envoyé son pavé dans votre combat',
                )
                new_notif2 = core_models.Notification.objects.create(
                    target = battle.refree,
                    url = f'/battles/battle_room/{battle_id}',
                    content = f"{player} a envoyé un pavé, tu dois l'évaluer",
                )

                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = opponent.user).last(),
                    {
                    'title' : f"Ton adversaire a envoyé son pavé",
                    'body' : f"{player} a envoyé son pavé dans votre combat",
                    'url' : f'/battles/battle_room/{battle_id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )

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
                new_notif2.save()
                message = 'pavé envoyé'
                return JsonResponse({'status':'success', 'message':message})

    return JsonResponse({'status':'error', 'message':message})        

def _most_reaction(textpad:TextPad):
    reactors = textpad.reactors.all()
    reactions = [

    ]
    for reactor in reactors:
        print(reactor.type)

        

def get_textpads(request, battle_id):
    battle = Battle.objects.get(id = battle_id)
    textpads = TextPad.objects.filter(battle = battle)
    player = get_player(request.user)
    

    textpads_data = [
        {
            'id' : textpad.id,
            "owner": textpad.owner.user.username,
            "text": textpad.text,
            "valid": textpad.valid,
            "character": get_textpad_character(battle,textpad),
            "time_since": core_views._time_since(textpad.date_sent),
            'index': index + 1,
            'comment' : textpad.refree_comment,
            'date_validated': core_views._time_since(textpad.date_validated) if textpad.date_validated else 'pas encore validé',
            'comment' : textpad.refree_comment,
            'hidden_action' : textpad.hidden_action if player == battle.refree or battle.status == 'finished' else None,
            'reactions' : textpad.reactors.all().count(),
            'comments' : TextPadComment.objects.filter(textpad = textpad).count(),
            'most_reaction' : textpad.most_made_reaction()['type'] if textpad.most_made_reaction() else '👍'

        } for index,textpad in enumerate(textpads)
    ] 

    return JsonResponse({"status":"success","textpads":textpads_data})

def _textpad_reactions_data(textpad_reactor:TextpadReactor):
    return {
        'date_added' : _time_since(textpad_reactor.date_added),
        'reaction' : textpad_reactor.type,
        'player' : textpad_reactor.player.user.username,
    }

def react_to_textpad(request, textpad_id):
    textpad = get_object_or_404(TextPad, id = textpad_id)
    player = get_player(request.user)

    if request.method == 'POST':
        
        reaction = request.POST.get('reaction','😂')
        
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
                new_notif = core_models.Notification.objects.create(
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
        reactions = [ _textpad_reactions_data(reactor) for reactor in TextpadReactor.objects.filter(textpad = textpad)]

        return JsonResponse({'status':'success', 'reactions': reactions})

def _textpad_comment_data(comment:TextPadComment):
    data:dict = {    
                "textpad_id" : comment.textpad.id,
                "id": comment.id,
                "text": comment.text,
                'body_full': comment.text,
                'body': comment.text[:197]+'...' if len(comment.text) > 200 else comment.text,
                "author": {
                    'id' : comment.author.id,
                    "player": str(comment.author),
                    "username": comment.author.user.username,
                    'profile_picture' : comment.author.profile_picture.url,
                },
                'parent' : {
                    "id": comment.parent.id,
                    "author": {
                        "id": comment.parent.author.id,
                        "username": comment.parent.author.user.username,
                        "player": str(comment.parent.author),
                        "profile_picture": comment.parent.author.profile_picture.url,
                    },
                    # "body_full" : comment.text,
                    # "body": comment.parent.text[:50] + '...' if len(comment.parent.text) > 50 else comment.parent.text,
                } if comment.parent else None,
                "timestamp":  _time_since(comment.date_added),
                'likes' : 0,
                'replies' : [ _textpad_comment_data(reply) for reply in TextPadComment.objects.filter(parent = comment).order_by("-date_added") ],
                #'is_reply' : TextPadComment.objects.filter(parent = ).exists()
            },
    
    # print(type(data))
    # if comment.parent:
    #     print(type(data))
        # data["parent"] = {
        #     "id": comment.parent.id,
        #     "author": {
        #         "id": comment.parent.author.id,
        #         "username": comment.parent.author.user.username,
        #         "player": str(comment.parent.author),
        #         "profile_picture": comment.parent.author.profile_picture.url,
        #     },
        #     "body_full" : comment.text,
        #     "body": comment.parent.text[:50] + '...' if len(comment.parent.text) > 50 else comment.parent.text,
        # }
    return data    
    

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
                    new_notif = core_models.Notification.objects.create(
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
                new_notif = core_models.Notification.objects.create(
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

                
                
        return JsonResponse({
            "status": "success",
            "comment": _textpad_comment_data(comment)
        })

def get_textpad_comments(request, textpad_id):
    textpad = get_object_or_404(TextPad, id=textpad_id)
    comments = TextPadComment.objects.filter(parent=None, textpad = textpad).order_by("-date_added")
    data = [_textpad_comment_data(comment) for comment in comments]
    
    return JsonResponse({ 'status': 'success', 'comments' : data}, safe=False)         


def rank_index(rank):
        for i in range(len(rankings)):
            if rank == rankings[i]:
                index = i
        return index

def update_rank(player:Player):
    r_index = rank_index(player.rank)
    if r_index < len(rankings):
        if player.progression >= 100:
            player.rank = rankings[r_index + 1]
            player.progression = 0
    else:
        print(f"{player.user.username} is at the max ranking already")        
    player.save()        
    #send a notif on the platform or via email to the player to inform him if 
    # he grew up


def update_points(family:Family, battle:Battle,member_progress):
    #Add points based on the 
    if family:
        user_godfather = family.god_father
        godfather = Player.objects.get(user = user_godfather)
    else:
        godfather = None    
    winner = battle.winner
    if winner and  winner.family == family:
        if battle.type == battle_types[1]:
            family.points += 10
            if member_progress >= 5:
                family.points += 3
            family.save()
    
        if godfather and godfather != winner:
            new_notif = core_models.Notification.objects.create(
                target = godfather,
                url = f'/users/family/{family.id}',
                content = f'{winner} a gagné un combat important!'

            )
            new_notif.save()    

        


def player_progress(battle:Battle,loser_rank):
    #points to consider:
    #-Type of the battle
    #-Difference in ranking
    #-Number of textpads needed to win(One Shots,...)
    #-Time needed to win the battle(Later)
    #opponent(If the opponent is a godfather)

    winner = battle.winner

    
    friendly_progress = 2
    challenge_progress = 4
    at_stake_progress = 5
    tournament_progress = 6
    
    progress = 1

    if battle.type == battle_types[0]:
        progress += friendly_progress
    elif battle.type == battle_types[1]:
        progress += at_stake_progress
    elif battle.type == 'tournament':
        progress +=  tournament_progress   
    elif battle.type == 'challenge':
        progress += challenge_progress
        #And if the opponent is a godfather then the progress is multiplied by 2    

    #get the difference in rankings between the winner and the loser and add progress accordingly    
    rank_diff = rank_index(loser_rank) - rank_index(winner.rank)

    if rank_diff > 0:
        #add progress according to the difference in rankings
        match rank_diff:
            case 1:
                progress += 2
            case 2:
                progress += 3
            case 3:
                progress += 4
            case 4:
                progress += 7 

    #add progress according to the number of textpads needed to win
    textpads_sent = TextPad.objects.filter(
        battle = battle,
        owner = winner
        )
    match len(textpads_sent):
        case 1:
            progress += 3
        case 2:
            progress += 2
        case 3:
            progress += 1

    #reduce according to the current ranking
    return progress                            

               

def evaluate_textpad(request, battle_id):
    #Fighters will be able to rate the refree for that battle
    player = Player.objects.get(user = request.user) 
    if request.method == "POST":
        battle = Battle.objects.get(id = battle_id) #get the battle id
        textpads = TextPad.objects.filter(battle=battle) #get the textpads for that battle
        if len(textpads)>0: #test if there is atleast 1 textpad sent

            #get the last textpad sent and set its validity based on 
            # what is sent by the refree
            textpad = textpads.last()      
            validity = request.POST["validity"]
            #convert to integer then to boolean 
            validity = int(validity)
            validity = bool(validity)
            
            
            
            textpad.valid = validity
            textpad.date_validated = timezone.now()
            textpad.refree_comment = request.POST.get('refree_comment', '')
            
            #index of the notification type based on if the textpad is accepted or not
            notif_index = 9
            message = "une erreur est survenu pendant l'evaluation du pavé"
            #verifications:
            #player is the referee of the battle
            #battle is on ongoing state

            #if the battle is at stake, manage family points 
        
            if player != battle.refree:
                message = "Tu n'es pas l'arbitre de ce combat"
            elif battle.status != battle_status[2]:
                message = "le combat n'es pas en cours"
            else:    
                if not validity: #if not valid, get the comment associated
                    notif_index = 10
                    textpad.refree_comment = request.POST.get("comment")
                    #MANAGE DRAWS
                    #get the winner and loser
                    loser = textpad.owner
                    winner = battle.initiator if loser == battle.opponent else battle.opponent
                        

                    #Update Family points
                    winner_family = winner.family
                    loser_family = loser.family

                    #####Send a notification here for the winner and the loser#####
                    win_notif = core_models.Notification.objects.create(
                    target = winner,
                    url = f'/battles/battle_room/{battle.id}',
                    content = "Tu as été declaré vainqueur du combat"
                    ) 
                    win_notif.save()

                    send_push_notification(
                        PushSubscription.objects.filter(user = winner.user).last(),
                        {
                        'title' : f"Tu as été declaré vainqueur du combat",
                        'body' : f"Tu as été declaré vainqueur du combat",
                        'url' : f'/battles/battle_room/{battle.id}',
                        'icon' : '/static/images/logo/logo_1.png',
                        },
                        
                    )
                    

                    # winnerstats.save()
                    # loserstats.save()

                    battle.winner = winner 
                    battle.status = battle_status[3]
                    battle.date_ended = datetime.now()
                    battle.defeat_motif =  'referee decision'

                    progress =  player_progress(battle=battle,loser_rank = loser.rank)
                    winner.progression +=  progress
                    
                    #update the player's rank if progression reached 100%
                    update_rank(winner)
                    update_points(family = winner.family, battle=battle, member_progress=progress)
                    winner.award_credits(40)

                    winner.save()
                    battle.save()
                     
                    if(battle.type == 'tournament'):
                        events_views._update_round(battle)

                #set the possibility to send a new text pad if the last one is valid 
                battle.can_send_textpad = validity
                if(validity):
                    notif_content = f'Ton pavé a été validé'
                    textpad.refree_comment = request.POST.get('refree_comment', '')
                    if textpad.owner == battle.initiator:
                        opponent = battle.opponent
                    elif textpad.owner == battle.opponent:
                        opponent = battle.initiator

                    notif = core_models.Notification.objects.create(
                        target = opponent,
                        content = f"Le pavé de ton adversaire a été validé, tu peux maintenant faire le tiens",
                        url = f'/battles/battle_room/{battle.id}',
                    )
                    notif.save()
                    send_push_notification(
                        PushSubscription.objects.filter(user = opponent.user).last(),
                        {
                        'title' : f"Le pavé de ton adversaire a été validé",
                        'body' : f"Le pavé de ton adversaire a été validé, tu peux maintenant faire le tiens",
                        'url' : f'/battles/battle_room/{battle.id}',
                        'icon' : '/static/images/logo/logo_1.png',
                        },
                        
                    )

                else:
                    notif_content = 'ton pavé a été refusé, tu as perdu le combat'  
                    #textpad.owner.progression  = textpad.owner.progression - 3
                    textpad.owner.save()  
                
                #create a notification for the textpad owner
                new_notif = core_models.Notification.objects.create(
                    target = textpad.owner,
                    url = f'/battles/battle_room/{battle.id}',
                    content = notif_content
                )
                send_push_notification(
                    PushSubscription.objects.filter(user = textpad.owner.user).last(),
                    {
                    'title' : f"Ton combat",
                    'body' : notif_content,
                    'url' : f'/battles/battle_room/{battle.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )  

                


                #save to db
                messages.success(request, message)
                message = 'Pavé validé'
                new_notif.save()
                textpad.save()   
                battle.save() 
                return JsonResponse({'status':'success', 'message': message})
        
    return JsonResponse({'status':'error', 'message': message})


def declare_winner(request, battle_id):
    if request.method == "POST":
        battle = Battle.objects.get(id=battle_id)
        
        if request.POST.get("player1"):
            player1 = request.POST["player1"]
            battle.winner = battle.initiator
            # playerstats = PlayerStat.objects.get(player = battle.initiator)
            # playerstats.wins += 1

            
        elif request.POST.get('player2'):
            player2 = request.POST['player2']
            battle.winner = battle.opponent
            # playerstats = PlayerStat.objects.get(player = battle.opponent)
            # playerstats.wins += 1
        
        # playerstats.save()
        battle.status = battle_status[3]
        battle.date_ended = datetime.now()

        battle.save()
        messages.success(request,f"{battle.winner} a gagné le combat")
        return HttpResponseRedirect(reverse("battles:battle_room",args=[battle_id]))

@csrf_exempt
def rules(request,battle_id):
    battle = Battle.objects.get(id = battle_id)
    message = "une erreur est survenu"
    if request.method == "POST":
        
        #get the rules in json
        rules = json.loads(request.body.decode('utf-8'))
        print(rules)
        #rules = { 'standard':[], 'specific1':[], 'specific2':[]}
        #set the initial rule type for the battle to be standard rules
        #rule_type = rule_types[0] 
        standard_rules = rules['standard']
        specific_rules1 = rules['specific1']
        specific_rules2 = rules['specific2']
        if len(standard_rules) >= 1 and len(specific_rules1)>=1 and len(specific_rules2)>=1:
            for rule in standard_rules:
                new_rule = Rule.objects.create(
                    battle = battle,
                    type = rule_types[0],
                    text = rule
                    )
                new_rule.save()
            for rule in specific_rules1:
                new_rule = Rule.objects.create(
                    battle = battle,
                    type = rule_types[1],
                    text = rule
                    )
                new_rule.save()
            for rule in specific_rules2:
                new_rule = Rule.objects.create(
                    battle = battle,
                    type = rule_types[2],
                    text = rule
                    )
                new_rule.save()           
            # for rule in rules:
            #     #change rule type based on the section from the frontend
            #     if rule['section'] == "specififc-rules-1":
            #         rule_type = rule_types[1]
            #     elif rule['section'] == "specififc-rules-2":
            #         rule_type = rule_types[2]   

            #     #create the rule in the db
            #     new_rule = Rule.objects.create(
            #         battle = battle,
            #         type = rule_type,
            #         text = rule['value']
            #         )
            #     new_rule.save()
            message = "rules set"
            notif1 = core_models.Notification.objects.create(
                target = battle.initiator,
                content = f"{battle.refree} a fixé les regles d'un de tes combats, tu peux desormais envoyé le premier pavé",
                url = f'/battles/battle_room/{battle.id}',
            )

            send_push_notification(
                PushSubscription.objects.filter(user = battle.initiator.user).last(),
                {
                'title' : f"Les régles de ton combat ont été fixées",
                'body' : f"{battle.refree} a fixé les regles d'un de tes combats, tu peux desormais envoyé le premier pavé",
                'url' : f'/battles/battle_room/{battle.id}',
                'icon' : '/static/images/logo/logo_1.png',
                },
            )


            notif2 = core_models.Notification.objects.create(
                target = battle.opponent,
                content = f"{battle.refree} a fixé les regles d'un combat dont tu participe",
                url = f'/battles/battle_room/{battle.id}',
            )

            send_push_notification(
                PushSubscription.objects.filter(user = battle.opponent.user).last(),
                {
                'title' : f"Les régles de ton combat ont été fixées",
                'body' : f"{battle.refree} a fixé les regles d'un combat dont tu participe",
                'url' : f'/battles/battle_room/{battle.id}',
                'icon' : '/static/images/logo/logo_1.png',
                },
            )

            notif1.save()
            notif2.save()
            battle.can_send_textpad = True
            battle.save()
            return JsonResponse({"status":"success","message":message, "rules":rules
            }) 
        else:
            message = "tu dois fixer toutes les régles"   
    return JsonResponse({"status":"error","message":message}) 

def rate_referee(request,battle_id):
    if request.method == "POST":
        battle = Battle.objects.get(id = battle_id)
        player = get_object_or_404(Player, user = request.user)
        fairness = request.POST.get('fairness')
        communication = request.POST.get('communication')
        timeliness = request.POST.get('timeliness')
        comment = request.POST.get('comment') or 'comment'
        print(comment)
        message = ''
        if player == battle.refree:
            message = "tu ne peux pas te noter toi meme"
        elif RefereeRating.objects.filter(battle = battle, player = player).exists():
            message = "Tu as déja donné une note a l'arbitre de ce combat"
        elif player != battle.initiator and player != battle.opponent:
            message = "Tu n'es pas un combattant dans ce duel"    
        elif len(RefereeRating.objects.filter(battle = battle)) > 1:
            message = "Les notes d'arbitrage ont deja été donné"
        elif battle.status != 'finished':
            message = "Le combat doit étre terminé avant de noter l'arbitrage"
        else:
            new_rating = RefereeRating.objects.create(
                player = player,
                fairness = fairness,
                timeliness = timeliness,
                communication = communication,
                comment = comment,
                battle = battle,
            )
            #send a notif to the referee
            new_notif = core_models.Notification.objects.create(
                target = battle.refree,
                content = f"{player} t'as noté dans un combat",
                url = f'battles/battle_room/{battle.id}',
            )

            new_rating.save()
            new_notif.save()
            message = 'Arbitre Noté'
            return JsonResponse({'status':'success','message':message})

    return JsonResponse({'status':'failure', 'message':message})

def get_referee_rating(player:Player):
    refereed_battles = Battle.objects.filter(refree = player)
    ratings = {
        "timeliness": 0,
        "fairness": 0,
        'communication':0,
    }
    for battle in refereed_battles:
        battle_ratings = RefereeRating.objects.filter(battle = battle)
        for rating in battle_ratings:
            ratings['timeliness'] = round((ratings['timeliness'] + rating.timeliness)/2,1)
            ratings['fairness'] = round((ratings['fairness'] + rating.fairness)/2,1)
            ratings['communication'] = round((ratings['communication'] + rating.communication)/2,1)

    return ratings        




def referees(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')

    referee_badge = Badge.objects.get(title = "Referee")
    referee_players = PlayerBadge.objects.filter(badge = referee_badge)
    referees = []
    for referee_player in referee_players:
        referee = referee_player.player
        referees.append({
            "id": referee.id,
            "player":{
                "username": referee.user.username,
                "player": str(referee)
            },
            "profile_picture": referee.profile_picture.url,
            "battles": len(Battle.objects.filter(refree = referee)),
            "ratings": get_referee_rating(referee),
        })


    return render(request,"battles/refrees.html",{
        "player":player,
        "n_notifs":core_views.get_notifs(player),
        "referees": referees,
    })
        


def get_number_of_battles(player:Player):
    #get the number of battles that the player did
    n_battles = len(Battle.objects.filter(
        Q(status = "finished") & ( Q(initiator = player) | Q(opponent=player) ) 
        ))
    return n_battles

def add_refree(player:Player):
    try:
        refree_badge = Badge.objects.get(title = 'Referee')
    except:
        #CHANGE this in accordance to the moderator
        print(f"Error getting badge")
        raise Http404
        
    player_badges = player.badges.all()
    if refree_badge in player_badges:
        print(f"{player.user.username} is already a refree")
    else:
        #add the refree badge to the player
        player.badges.add(refree_badge)
        
        player.save()
        
        
    

@login_required
def new_refree(request):
    #player will be eligible to take the refree test if:
        #player is in a family
        #player has refreed atleast X friendly battles
        #player has completed atleast X battles
        #player's rank is atleast D
        #is on the platform for atleast 2 months(not sure)
        # 
    #UPDATE THIS TO THE REAL VALUES      
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    n_notifs = core_views.get_notifs(player=player)
    n_battles = get_number_of_battles(player)
    refree_badge = Badge.objects.get(title = "Referee")
    player_badges = player.badges.all()
    #get the situations randomly from the list of situations
    random_index = random.randint(0, len(situations_1)-1)
    situation_1 = situations_1[random_index]
    situation_2 = situations_2[random_index]
    
    situations_file = os.path.join(BASE_DIR, 'refree_questions', 'fr\situations.json')

    with open(situations_file, 'r', encoding='utf-8') as file:
        situations_data = json.load(file)
        situation_1 = random.choice(situations_data)
        situation_2 = random.choice(situations_data)

    message = ""


    #update this condition to take only batttles refreed COMPLETELY and length > X
    has_refreed = len(
        Battle.objects.filter(refree = player, type = battle_types[0], status = battle_status[-1])
    ) >= 2
    if not has_refreed: message = "Tu dois avoir arbitrer au moins 2 combats stake" 

    
    rank_eligibility=True

    #TO BE ADDED AFTER WE REACH SOME USERS
    # if rank_index(player.rank) >= 1:rank_eligibility = True
    # else: message = "Tu dois étre au moins  de rang D pour faire le test"

    battles_eligibilty = False
    #Change to 2 LATER
    if n_battles>=1:battles_eligibilty =True
    else: message = 'Tu dois avoir completé au-moins 1 combat amicale pour prendre le test'


    in_family = False
    if player.family: in_family = True 
    else: message = "Tu dois étre dans une famille pour faire le test"
    

    eligible = in_family and (n_battles >= 1) #add other conditions later
    #check if player has taken a refree test recently and set the final eligibility based on that

    if RefreeTest.objects.filter(player = player).exists():
        eligible = False
        message = "Tu as deja fait le test récemment, tu seras en mesure de le refaire dans 5 de jours"

    if refree_badge in player_badges:
        eligible = False
        message = 'Tu es deja un arbitre officiel'

    questions = get_refree_questions()

    
    if request.method == "POST":
        #player has completed the Quizz
        #get his score and create it's RefreeTest model
        
        step = request.POST['step']
        step = int(step)
        
        if step == 1:
            quizScore =  int(request.POST['score'])

            new_test = RefreeTest.objects.create(
                player = player,
                quizScore = quizScore,
                situation_a = situation_1,
                situation_b = situation_2,
            )
            if quizScore >= 60:
                pass
                # new_test.validated = True
            
                # #add player as a refree on validation
                # add_refree(player)
  
            new_test.save()
            # return JsonResponse({"status":"success","message": f'1ere étape completée'})

            return JsonResponse({"status":"success","message": f'1ere étape completée', "test_id": new_test.id})
        #player has completed the test and is eligible to be a refree
        elif step == 2:    
            verdict1 = request.POST['verdict1']
            verdict2 = request.POST['verdict2']
            test = RefreeTest.objects.filter(player = player).last()
            test.verdict1  = verdict1
            test.verdict2 = verdict2

            #CHANGE THIS to be the moderator to determine validity
            test_passed = random.randint(0,1)
            test_passed = test_passed == 1
            # test.validated =  test_passed
            
            #simulate validation
            # test.validated = True
            
            # #add player as a refree on validation
            # add_refree(player)

            test.save()

            moderators = Moderator.objects.all()
            for moderator in moderators:
                print(f"sending notif to {moderator.user}")
                send_push_notification(PushSubscription.objects.filter(user = moderator.user).last(),
                {
                'title' : f"Nouveau test d'arbitrage",
                'body' : f"{player} a passer le test d'arbitrage, tu dois l'evaluer",
                'url' : f'/moderator',
                'icon' : '/static/images/logo/logo_1.png',
                },
                moderator.user
                )


            return JsonResponse({"status":"success","message": f'2eme étape completé', "test_passed": test_passed})
        
    eligible = not refree_badge in player_badges #Just for now, remove after we have sufficient referees to start with
    #eligible = True
    
    context = {
        "player" : player,
        "n_notifs" : n_notifs,
        "n_battles" : n_battles,
        "in_family" : in_family,
        "battles_eligibility": battles_eligibilty,
        "rank_eligibility": rank_eligibility, #player's rank should be atleast D
        "has_refreed":has_refreed,
        "eligible":eligible,
        "questions":questions[:8],
        "message":message,
        "situation1": situation_1,
        "situation2": situation_2,
        }
    
    return render(request,"battles/refrees/new_refree.html",context)

def send_challenge(request, target_id):
    player = Player.objects.get(user = request.user)
    target = get_object_or_404(Player, id = target_id)
    if request.method == 'POST':
        message = ''
        character = request.POST.get('character')
        if not character:
            message = 'choisie un perso'
        elif player.battle_points < CHALLENGE_COST:
            message = 'pas assez de Jetons de Combat'
        elif player == target:
            message = "Tu ne peux pas te challenger toi meme"    
        else:
            player.battle_points = player.battle_points - CHALLENGE_COST
            player.save()

            new_challenge = Challenge.objects.create(
                sender = player,
                target = target,
                sender_character = character,
            )
            # new_notif = core_models.Notification.objects.create(
            #     target = target,
            #     content = f'{player} challenged you to a battle',
            #     url = f'/users/{player.user.username}'
            # )

            #send push notification to the target
            send_push_notification(
                PushSubscription.objects.filter(user = target.user).last(),
                {
                'title' : f"Tu as été défié",
                'body' : f"{player} t'as défié pour un combat, tu peux l'accepter ou le refuser",
                'url' : f'/users/challenges/{player.user.username}',
                'icon' : '/static/images/logo/logo_1.png',
                },
                target.user
                
            )
            
            new_challenge.save()
            #new_notif.save()

            message = f'Tu as defié {target}, en attente de sa réponse'
            return JsonResponse({'status':'success','message':message})
        
    return JsonResponse({'status':'failed', 'message':message})    

def __notify_referees():
    r_badge = Badge.objects.get(title = 'Referee')
    for pb in  PlayerBadge.objects.filter(badge = r_badge):
        notif = core_models.Notification.objects.create(
            target = pb.player,
            url = '/battles',
            content = "Un nouveau combat est en attente d'arbitrage"
        )
        notif.save()

def answer_challenge(request, challenge_id):
    player = get_object_or_404(Player, user = request.user)
    challenge = get_object_or_404(Challenge, id = challenge_id)

    if request.method == "POST":
        response = request.POST['response']
        character = request.POST.get('character')
        challenge.answered = True 
        challenge.save() 

        if response == "accept":

            if challenge.target != player:
                message = "Vous n'etes pas la cible de ce challenge"
            elif challenge.accepted:
                message = 'Vous avez deja accepté ce challenge'
                 
            else:    
                message = "Challenge accepté,  en attente d'un arbitre pour le combat"

                new_battle = Battle.objects.create(
                        initiator = challenge.sender,
                        i_character = challenge.sender_character,
                        opponent = player,
                        o_character = character,
                        type = 'challenge',
                        status = 'waiting_refree'

                    )
                new_notif = core_models.Notification.objects.create(
                    target  = challenge.sender,
                    content = f'{player} a accepté le defi, un arbitre doit etre choisi pour debuter le combat',
                    url = f'/battles/referees',
                )
                #send push notification to the sender of the challenge
                send_push_notification(
                    PushSubscription.objects.filter(user = challenge.sender.user).last(),
                    {
                    'title' : f"Ton défi a été accepté",
                    'body' : f"{player} a accepté le défi, un arbitre doit etre choisi pour debuter le combat",
                    'url' : f'/users/challenges/{challenge.sender.user}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    challenge.sender.user
                    
                    
                )

                #challenge.delete()
                __notify_referees()
                new_battle.save()
                new_notif.save()
        else:
            
            message = "Challenge refusé"
            notif2 = core_models.Notification.objects.create(
                target  = challenge.sender,
                content = f'{player} a refusé ton défi',
                url = '#',
            )
            notif2.save()
            challenge.delete()
          
    return JsonResponse({'status':'success', 'message':message})


@login_required
def soloBattle(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    n_notifs = core_views.get_notifs(player=player)
    characters = get_solo_battle_characters()




    return render(request,"battles/solo.html", {
        'player':player,
        'n_notifs': n_notifs,
        'characters' : characters,
    })

@csrf_exempt
def init_solo_battle(request):
    player = get_object_or_404(Player, user = request.user)
    if request.method == "POST":
        player_character = request.POST.get('character')
        characters = get_solo_battle_characters()
        bot_character = characters[random.randint(0, len(characters)-1)]
        if bot_character['name'] == player_character : 
            bot_character = characters[random.randint(0, len(characters)-1)]
        # if player_character not in characters:
        #     return JsonResponse({'message': 'character not found'})
        player_character = _solo_battle_character(player_character)
        player_character['hp'] = 200
        bot_character['hp'] = 200
        player_character['chakra'] = player_character.get('chakra_pool',100)
        bot_character['chakra'] = bot_character.get('chakra_pool',100)


        battle = SoloBattle.objects.create(
            player = player,
            player_character = player_character,
            bot_character = bot_character,
        )

        battle.save()


        return JsonResponse({'message': 'battle initialized', 'bot_character': bot_character, 'player_character': player_character})

    return JsonResponse({'message':'bad request'})     

def _reward_player(player:Player):
    progression_boost = 2
    player.progression = player.progression + progression_boost
    player.save()
    update_rank(player)

    return {'xp' : f'{progression_boost}'}
 
def solo_battle_action(request):
    player = get_object_or_404(Player, user = request.user)
    if request.method == 'POST':
        # model = JsonTestModel.objects.get(id = 2)
        action = request.POST.get('action')
        
        battle = SoloBattle.objects.filter(player = player).order_by('-date_started')[0]
        player_character = battle.player_character
        bot_character = battle.bot_character
        possible_actions = BASIC_ACTIONS + player_character['jutsus']
        
        player_action = BASIC_ACTIONS[0]

        for act in possible_actions:
            if act['name'] == action:
                player_action = act

        bot_action = _bot_action(bot_character, player_action)
        print(bot_action.get('name'))
        bot_action = _bot_action_minimax(player_character, bot_character)
        print(bot_action.get('name'))
        new_logs = _log_actions(player_action, bot_action, player_character, bot_character)
        logs = json.loads(battle.log)
        for log in new_logs:
            logs.append(log)
        
        player_character, bot_character, new_logs, winner =  _evaluate_actions(player_character, bot_character, player_action, bot_action)
        logs = logs + new_logs
        # for log in logs:
        #     print(f"{log.get('timestamp')}: {log.get('text')} : {log.get('result')}")

        # new_log = {
        #     'text' : f"{action} performed",
        #     'type' : 'success',
        #     'result' : 'success',
        #     'timestamp': datetime.now().strftime("%H:%M"),
        #     }

        rewards = {'xp' : 0, }
        if winner == 'player':
            rewards = _reward_player(player)
            battle.result = 'win'
            battle.finished = True
            battle.date_ended = datetime.now()
        elif winner == 'bot':
            battle.result = 'lose'
            battle.finished = True
            battle.date_ended = datetime.now()
           
            

        
        battle.log = json.dumps(logs)
        battle.save()  

        return JsonResponse({'battle_logs': logs, 'player_character' : player_character, 'bot_character' : bot_character, 'winner' : winner, 'rewards': rewards})    




        