from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.urls import reverse
from django.contrib.auth.models import User,auth
from django.http import JsonResponse,HttpResponseRedirect
from battles.solo_battle import _evaluate_actions, _log_actions
from monetization.models import Payment
from store.models import AffiliateProduct, Product
from users.models import Player,PlayerNotification,Family
from story.models import StoryCharacter
from story.views import _story_character
from django.contrib.auth.decorators import login_required
from .models import *
from events.models import Tournament
from battles.models import BASIC_ACTIONS, Battle,Challenge, RefreeingProposal
from chat.models import FamilyMessage
import battles.views as battle_views
import users.views as users_views
from pathlib import Path
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import os
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from users.users_utility import get_country, get_player
from utility import _solo_battle_character, _time_since,_parse_number,decrypt_message, get_solo_battle_characters,sendWelcomeEmail,generate_referall_code
from api.models import PushSubscription
from api.utility import send_push_notification
import random
from django.contrib.gis.geoip2 import GeoIP2
import re
import praw,time
from api.views import export_battle_data
from store.views import affiliate_product_data, product_data
import requests
from django.db.models import Count,Max
BASE_DIR = Path(__file__).resolve().parent.parent

def _duel_data(duel:Duel):
    duel_fighters = DuelFighter.objects.filter(duel = duel) 
    fighter1 = duel_fighters.first() if duel_fighters else None
    fighter2 = duel_fighters.last() if len(duel_fighters) > 1 else None

    return {
        'player1' : users_views._player_data(fighter1.player),
        'player1_character' : fighter1.character,
        'player2_character' : fighter2.character if fighter2 else None,
        'player2' : users_views._player_data(fighter2.player) if fighter2 else None,
        'winner' : users_views._player_data(duel.winner) if duel.winner else None,
        'status' : duel.status,
        'started_at' : duel.started_at,
        'ended_at' : duel.ended_at,
        'code' : duel.code,
    }

def _duel_ranking():
    
    def _winner_data(duel:Duel):
        data = users_views._player_data(duel.winner)
        data['wins'] = 0
        data['losses'] = 0
        data['player'] = {
                    'player': str(duel.winner),
                    'username':duel.winner.user.username,
                }
    
        return data

    
    duels = Duel.objects.exclude(winner=None)
    winners = []

    for duel in duels:
        if _winner_data(duel) not in winners:
            winners.append(_winner_data(duel))
            

    # print("TW:",winners)
    for winner in winners:
        for duel in duels:
            #update number of wins for each  winner
            if winner['id'] == duel.winner.id:
                winner['wins'] += 1 

    sorted_winners = sorted(winners, key = lambda winner: winner['wins'], reverse=True)

    return sorted_winners

@login_required
def index(request):
    player = get_player(request.user)
    if not player:
        #return redirect('/home')
        pass
    else:
        duels =  [ _duel_data(duel) for duel in  Duel.objects.filter(Q(duelfighter__player = player)).order_by('-started_at') ] if player else []
        affiliate_products = [  affiliate_product_data(product) for product in AffiliateProduct.objects.order_by("?") ] 


        return render(request,"duels/index.html", {
            'player' : player,
            'recent_duels': duels[:10],
            'top_players' : _duel_ranking(),
            'affiliate_products' : affiliate_products
        })

@login_required
def new_duel(request):
    player = get_player(request.user)
    if not player:
        return redirect('/home')
    else:
        characters = get_solo_battle_characters()

        if request.method == "POST":
            player_character = request.POST.get('character')
            player_character = _solo_battle_character(player_character)

            new_duel = Duel.objects.create()
            #new_duel.fighters.add(player)

            duel_fighter = DuelFighter.objects.create(duel = new_duel, player = player, character = player_character)
            #duel_fighter.character = player_character
            
            print(len(new_duel.fighters.all()))
            duel_fighter.save()
            new_duel.save()
            return JsonResponse({ 'message' : 'Duel Created', 'status' : 'success', 'character' : player_character, 'duel_code' : new_duel.code, 'date_created': new_duel.started_at.strftime("%d %b %Y %H:%M"), 'duel_link': f"https://roleplayverse.live/duels/{new_duel.code}"})



        return render(request,"duels/new.html", {
            'player' : player,
            'characters': characters
        })    


def join_duel(request, duel_code):
    player = get_player(request.user)
    duel = Duel.objects.filter(code = duel_code).first()
    if not player:
        return redirect('/home')
    else:
        characters = get_solo_battle_characters()

        if player in duel.fighters.all():
             return redirect(f'/duels/{duel.code}')

        if request.method == "POST":
            player_character = request.POST.get('character')
            player_character = _solo_battle_character(player_character)
            fighters = duel.fighters.all()
            if len(fighters) <= 1 and player not in fighters:
                duel_fighter = DuelFighter.objects.create(duel = duel, player = player, character = player_character)
                #duel_fighter.character = player_character
                
                print(len(duel.fighters.all()))
                duel_fighter.save()
                duel.save()
                return JsonResponse({ 'message' : 'joined duel', 'status' : 'success', 'character' : player_character, 'duel_code' : duel.code, 'date_created': duel.started_at.strftime("%d %b %Y %H:%M"), 'duel_link': f"https://roleplayverse.live/duels/{duel.code}"})
            else:
                return JsonResponse({'message' : 'Players have already been paired for this duel', 'status' : 'error'})


        return render(request,"duels/join.html", {
            'player' : player,
            'characters': characters,
            'duel' : _duel_data(duel)
        })    


def join_random_duel(request):
    player = get_player(request.user)
    #single_fighter_duels = Duel.objects.annotate(num_fighters=Count('fighters')).filter(num_fighters__lt=2)  
    if request.method == "POST":
        single_fighter_duels = (
        Duel.objects
        .annotate(num_fighters=Count('fighters'))
        .filter(num_fighters=1)
        .annotate(last_seen=Max('duelfighter__player__last_seen'))
        .order_by('-last_seen')
        )
        found_duels = [ _duel_data(duel) for duel in single_fighter_duels]   

        return JsonResponse({"status":'success', 'duel' : found_duels[0]})
    return JsonResponse({"status":'error'})    

def duel(request, duel_code):
    player = get_player(request.user)
    duel = Duel.objects.filter(code = duel_code).first()

    if not player:
        return redirect('/home')
    else:
        initatiator = DuelFighter.objects.filter(duel = duel).first().player
        opponent = DuelFighter.objects.filter(duel = duel).last().player

        

        fighters = duel.fighters.all()
        if player not in fighters and len(fighters) == 1:   
            return redirect(f"/duels/join/{duel_code}")
        
        if len(fighters) >= 2:
            #return redirect("/duels/fallback")
            print("Duel full")
            pass
        
        initiator_data = users_views._player_data(initatiator)
        initiator_data['display_name'] = "Toi" if player == initatiator else str(initatiator.user)
        
        opponent_data = users_views._player_data(opponent)
        opponent_data['display_name'] = "Toi" if player == opponent else str(opponent.user)
        
        if player in fighters:
            return render(request,"duels/game.html", {
                'player' : player,
                'duel' : duel,
                'initiator_data' : initiator_data,
                'opponent_data' : opponent_data
            })
        else:
            print("redirect to fallback page")
            return redirect("/duels")


def init_duel(request, duel_code):
    player = get_player(request.user)
    duel = Duel.objects.filter(code = duel_code).first()
    duel_fighters = DuelFighter.objects.filter(duel = duel) if duel else []
    player1 = DuelFighter.objects.filter(duel = duel, player = player).first() if duel else None
    player2 = duel_fighters.exclude(player = player).first() if duel else None

    if not player2:
        return JsonResponse({'status' : 'fallback', 'message' : 'Waiting for an opponent connection'})

    fighter1 = duel_fighters.filter(duel=duel).first() if duel else None
    fighter2 = duel_fighters.filter(duel=duel).last() if duel else None

    if request.method == "POST":

        fighter1_character = fighter1.character
        fighter2_character = fighter2.character

        player1_character = player1.character if player1 else None
        player2_character = player2.character if player2 else None
        #characters = get_solo_battle_characters()
        player_character = player1_character if player1 and player1.player == player else player2_character if player2 and player2.player == player else None
        opponent_character = player2_character if player1 and player1.player == player else player1
        # if player_character not in characters:
        #     return JsonResponse({'message': 'character not found'})
        # player1_character = _solo_battle_character(player1_character.get('name'))
        fighter1_character['hp'] = fighter1_character.get('hp',200)
        fighter2_character['hp'] = fighter2_character.get('hp',200)
        fighter1_character['chakra'] = fighter1_character.get('chakra',fighter1_character.get('chakra_pool',100))
        fighter2_character['chakra'] = fighter2_character.get('chakra',fighter2_character.get('chakra_pool',100))

        fighter1.character = fighter1_character
        fighter2.character = fighter2_character
        
        duel.save()
        fighter1.save()
        fighter2.save()
        logs = json.loads(duel.log)
        player1_data = users_views._player_data(fighter1.player)
        player1_data['display_name'] = "Toi" if fighter1.player == player else player1_data.get('name')
        player2_data = users_views._player_data(fighter2.player) 
        player2_data['display_name'] = "Toi" if fighter2.player == player else player2_data.get('name')

        return JsonResponse({'message': 'battle initialized', 'logs' : logs, 'player1' : player1_data, 'player2' : player2_data, 'opponent_character': fighter2_character, 'player_character': fighter1_character, 'current_character': player_character})

    return JsonResponse({'message':'bad request'})     


def last_fighter_action(fighter:DuelFighter):
    last_action = DuelAction.objects.filter(fighter = fighter, evaluated = False).order_by('-created_at').first() if fighter else None
    return last_action if last_action else None

def duel_action(request, duel_code):
    player = get_object_or_404(Player, user = request.user)
    duel = Duel.objects.filter(code = duel_code).first()
    current_fighter = DuelFighter.objects.filter(duel = duel, player = player).first() if duel else None
    opponent_fighter = DuelFighter.objects.filter(duel = duel).exclude(player = player).first() if duel else None

    if request.method == 'POST':
        # model = JsonTestModel.objects.get(id = 2)
        action = request.POST.get('action')


        if last_fighter_action(current_fighter):
            return JsonResponse({'message': 'You already performed an action, wait for your opponent.'})

        player_character = current_fighter.character if current_fighter else None
        opponent_character = opponent_fighter.character if opponent_fighter else None
        possible_actions = BASIC_ACTIONS + player_character['jutsus']
        
        player_action = BASIC_ACTIONS[0]

        for act in possible_actions:
            if act['name'] == action:
                player_action = act
                new_duel_action = DuelAction.objects.create(fighter = current_fighter, action = act)
                new_duel_action.save()

        opponent_action = last_fighter_action(opponent_fighter)
        logs = json.loads(duel.log)
        if opponent_action:
            print(opponent_action.action.get('name'))
            new_logs = _log_actions(player_action, opponent_action.action, player_character, opponent_character)
            for log in new_logs:
                logs.append(log)
            
            player_character, opponent_character, new_logs, winner =  _evaluate_actions(player_character, opponent_character, player_action, opponent_action.action)
            opponent_action.evaluated = True
            new_duel_action.evaluated = True
            opponent_action.save()
            new_duel_action.save()
            logs = logs + new_logs
            # for log in logs:
            #     print(f"{log.get('timestamp')}: {log.get('text')} : {log.get('result')}")

            # new_log = {
            #     'text' : f"{action} performed",
            #     'type' : 'success',
            #     'result' : 'success',
            #     'timestamp': datetime.now().strftime("%H:%M"),
            #     }

            # rewards = {'xp' : 0, }
            # if winner == 'player':
            #     rewards = battle_views._reward_player(player)
            #     battle.result = 'win'
            #     battle.finished = True
            #     battle.date_ended = datetime.now()
            # elif winner == 'opponent':
            #     battle.result = 'lose'
            #     battle.finished = True
            #     battle.date_ended = datetime.now()
            
        else:
            return JsonResponse({'message': 'waiting for opponent...'})        
            
        duel.log = json.dumps(logs)
        duel.save()  

        return JsonResponse({ 'status' : 'continue', 'battle_logs': logs, 'player_character' : player_character, 'opponent_character' : opponent_character, 'winner' : winner, 'rewards': []})    

