from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.shortcuts import redirect,render
from django.http import HttpResponseRedirect,JsonResponse,Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q
from users.models import Player,Family,PlayerStat,PlayerNotification,notification_types,rankings,Badge,PlayerBadge
from users.users_utility import get_player
import core.models as core_models
import battles.models as battle_models
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
from battles.models import *




def eligible_to_monetization(player:Player):
    rank = player.rank
    battles_finished = Battle.objects.filter(status = 'finished').filter(
        Q(initiator = player) | Q(opponent = player)
    )
    battles_refereed = Battle.objects.filter(refree = player, status = 'finished')

    if rank != 'E' and (len(battles_finished) + len(battles_refereed)) >= 7:
        return True
    for tournament in events_models.Tournament.objects.all():
        if player == tournament.winner:
            return True

    
    return False    

def battle_views(player):
    """Function to get the total number of views from the battles of the player"""
    battles = Battle.objects.filter(Q(initiator=player) | Q(opponent=player))
    total_views = 0
    for battle in battles:
        total_views += battle.spectators.all().count()
    return total_views

def reactions_from_posts(player):
    """Function to get the total number of reactions and comments from the posts and textpads of the player"""
    posts = core_models.Post.objects.filter(author=player)
    #textpads = battle_models.TextPad.objects.filter(owner=player)
    total_reactions = 0
    for post in posts:
        total_reactions += post.likes
        comments = core_models.Comment.objects.filter(post = post).count()
        total_reactions += comments
    return total_reactions

def battles_finished(player):
    return Battle.objects.filter(status = 'finished').filter(
        Q(initiator = player) | Q(opponent = player)
    ).count()

def battles_refereed(player):
    return Battle.objects.filter(refree = player, status = 'finished').count()

def available_gains(rp_credits):
    gains = round(rp_credits/200,2)
    return gains

@login_required
def index(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    if not eligible_to_monetization(player):
        return redirect('/monetization/requirements')
    # Check if the player is eligible for monetization
    
    n_notifs = core_views.get_notifs(player=player)
    
    return render(request,"monetization/index.html", {
        'player':player,
        'n_notifs': n_notifs,
        'battle_views' : battle_views(player),
        'reactions' : reactions_from_posts(player),
        'battles_finished' : battles_finished(player),
        'battles_refereed' : battles_refereed(player), 
        'gains' : available_gains(player.rp_credits)
    })

@login_required
def requirements(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    n_notifs = core_views.get_notifs(player=player)

    battles_finished = Battle.objects.filter(status = 'finished').filter(
        Q(initiator = player) | Q(opponent = player)
    )

    battles_refereed = Battle.objects.filter(refree = player, status = 'finished')

    #redirect player if eligible
    if eligible_to_monetization(player):
        return redirect('/monetization')
    
    
    
    return render(request,"monetization/requirements.html", {
        'player':player,
        'n_notifs': n_notifs,
        'battles_completed': len(battles_finished),
        'battles_refereed': len(battles_refereed),
        
    })



