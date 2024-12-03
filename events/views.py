from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,QuerySet
from django.urls import reverse
from django.contrib.auth.models import User,auth
from django.http import JsonResponse,HttpResponseRedirect
from users.models import Player,PlayerNotification,Family
from .models import *
from battles.models import Battle,tournament_cost
import battles.views as battle_views
from django.contrib.auth.decorators import login_required
from core.models import Notification
import  core.views as core_views
from pathlib import Path
import os
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone
from django.contrib import messages
import math,random
from utility import get_characters
from users.users_utility import get_player


def _tournament_data(tournament:Tournament):

    return {
        'type': 'tournament',
    }


@login_required
def index(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    tournaments = Tournament.objects.all().order_by('-date_created')
    tournaments_data = [
        {
            "type":"tournament",
            "tournament": tournament,
            
        } for tournament in tournaments
    ]
    events = tournaments_data

    context = {
        "player":player,
        "events":events,
        "n_notifs":core_views.get_notifs(player),
        
    }
    return render(request, "events/index.html", context)

@login_required
def create(request):
    return redirect('/home')
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    if request.method == "POST":
        event_type = request.POST['event_type']
        if event_type == "tournament":
            name = request.POST['name']
            start_date = request.POST['start_date']
            rules = request.POST['rules']
            n_participants = request.POST['n_participants']

            # new_tournament_proposal = TournamentRequest.objects.create(
            #     name = name,
            #     start_date = start_date,
            #     n_participants = n_participants,
            #     rules = rules,
            #     creator = player
            # )

            #perform other actions e.g send notification to the moderator to review the tournament proposal

            # new_tournament_proposal.save()

            rounds = math.ceil(math.log2(n_participants))
            #set the participation cost
            participation_cost = 500*((rounds/2))

            if(participation_cost > 1000):
                participation_cost = 1000
            
            #set the reward
            reward = 1000 * rounds 


            new_tournament = Tournament.objects.create(
                name = name,
                start_date = start_date,
                n_participants = n_participants,
                rules = rules,
                creator = player,
                participation_cost = participation_cost,
                reward = reward,
                cover = f"tournaments/covers/{tournament_covers[random.randint(0, len(tournament_covers)-1)]}"
            )
            new_tournament.save()
            messages.success(request, "Your event proposal has been submited")
            return HttpResponseRedirect(reverse("events:index"))

        elif event_type == "story":
            print("proposing a story")
        elif event_type == "royal_rumble":
            print("proposing a royal rumble")
        elif event_type == "quizz":
            print("proposing a quizz")

        
    
    context = {
        "player":player,
        "n_notifs":core_views.get_notifs(player),
    }
    return render(request, "events/create.html", context)


def _can_start(tournament:Tournament):
    can_start = False
    fighters = tournament.fighters.all()
    referees = tournament.refrees.all()
    if len(fighters) == tournament.n_participants and len(referees) == (tournament.n_participants/2):
        can_start =True

    #REMOVE THIS PART WHEN READY TO CREATE TOURNAMENTS IN PROD    
    elif len(fighters) == tournament.n_participants and len(referees) >= 1:    
        can_start = True

    return can_start    

def create_round_battles(tournament:Tournament, fighters, round=1):
    
    referees = list(tournament.refrees.all())
    registered_fighters = []
    registered_referees = []
    
    while len(registered_fighters) != len(fighters):
        
        random.shuffle(fighters)
        random.shuffle(referees)
        fighter1 = fighters[0]
        fighter2 = fighters[1]

        referee = referees[0]
        
        if fighter1 in registered_fighters or fighter2 in registered_fighters:
            #continue to shuffle if either of the fighters is already registered 
            continue
        
        if (referee in registered_referees and len(referees) == len(registered_referees)) or (referee not in registered_referees and len(referees) != len(registered_referees)):
            #register the fighters and the referee(assuring all referees are assigned a battle) if 
            registered_fighters.append(fighter1)
            registered_fighters.append(fighter2)
            registered_referees.append(referee)
            # fighter1_character = tournament.fighters.through.objects.get(tournament = tournament, fighter = fighter1).character
            # fighter2_character = tournament.fighters.through.objects.get(tournament = tournament, fighter = fighter2).character

            fighter1_character = FighterTournament.objects.get(tournament = tournament, fighter = fighter1).character
            fighter2_character = FighterTournament.objects.get(tournament = tournament, fighter = fighter2).character

            new_battle = Battle.objects.create(
            type = 'tournament',
            status = "not_started",
            initiator = fighter1,
            opponent = fighter2,
            i_character = fighter1_character,
            o_character = fighter2_character,
            refree = referee,
            #can_send_textpad = True
        )   
            tournament.battles.add(new_battle)
            #set the battleTournament round to the next round here for other rounds
            tournament_battle = TournamentBattle.objects.get(tournament = tournament, battle = new_battle)
            tournament_battle.round = round
            tournament.status = "ongoing"
            tournament.start_date = timezone.now()
            new_battle.save()
            tournament_battle.save()
            tournament.save()

           
        else:
            continue
    #SEND NOTIFS TO THE PLAYERS AND REFREES INVOLVED
    for player in fighters:
        new_notif = Notification.objects.create(
            target = player,
            content = f"The next round of the tournament {tournament.name} in which you are a fighter has started",
            url = f"/events/tournaments/{tournament.id}",
        )
        new_notif.save()

    for ref in referees:
        new_notif = Notification.objects.create(
        target = ref,
        content = f"The next round of the tournament {tournament.name} in which you are a referee has started",
        url = f"/events/tournaments/{tournament.id}",
    )
        new_notif.save()




def init_tournament(tournament:Tournament):
    fighters = list(tournament.fighters.all())
    referees = list(tournament.refrees.all())
    #create the first round battles, the first round has n_participants/2 battles
    
    registered_fighters = []
    registered_referees = []

    while len(registered_fighters) != len(fighters):
        
        random.shuffle(fighters)
        random.shuffle(referees)
        fighter1 = fighters[0]
        fighter2 = fighters[1]

        referee = referees[0]
        
        if fighter1 in registered_fighters or fighter2 in registered_fighters:
            #continue to shuffle if either of the fighters is already registered 
            continue
        
        if (referee in registered_referees and len(referees) == len(registered_referees)) or (referee not in registered_referees and len(referees) != len(registered_referees)):
            #register the fighters and the referee(assuring all referees are assigned a battle) if 
            registered_fighters.append(fighter1)
            registered_fighters.append(fighter2)
            registered_referees.append(referee)
            # fighter1_character = tournament.fighters.through.objects.get(tournament = tournament, fighter = fighter1).character
            # fighter2_character = tournament.fighters.through.objects.get(tournament = tournament, fighter = fighter2).character

            fighter1_character = FighterTournament.objects.get(tournament = tournament, fighter = fighter1).character
            fighter2_character = FighterTournament.objects.get(tournament = tournament, fighter = fighter2).character

            tournament_battle = Battle.objects.create(
            type = 'tournament',
            status = "not_started",
            initiator = fighter1,
            opponent = fighter2,
            i_character = fighter1_character,
            o_character = fighter2_character,
            refree = referee,
            #can_send_textpad = True
        )   
            tournament.battles.add(tournament_battle)
            
            #set the battleTournament round to the next round here for other rounds
            tournament.status = "not_started"
            tournament.start_date = timezone.now()
            tournament_battle.save()

           
        else:
            continue
    #SEND NOTIFS TO THE PLAYERS AND REFREES INVOLVED
    for player in fighters:
        new_notif = Notification.objects.create(
            target = player,
            content = f"The Tournament {tournament.name} in which you are a fighter has started",
            url = f"/events/tournaments/{tournament.id}",
        )
        new_notif.save()
    for ref in referees:
        new_notif = Notification.objects.create(
        target = ref,
        content = f"The Tournament {tournament.name} in which you are a referee has started",
        url = f"/events/tournaments/{tournament.id}",
    )
        new_notif.save()


def _roundsBattles(player:Player,tournament:Tournament, rounds):
    rounds_battles = {}
    for i in range(rounds):
        #filter out battles in the tournament for that round and append to rounds_battles
        #round_battles = tournament.battles.filter(through_defaults = {'round':i})
        tournament_battles = TournamentBattle.objects.filter(tournament = tournament, round = i+1)
        battles_ids = tournament_battles.values_list('battle',flat=True) 
        round_battles = [ Battle.objects.get(id = battle_id) for battle_id in battles_ids ]
        
        rounds_battles[i] = battle_views._battles_data(player, round_battles)
    return rounds_battles    

def _update_round(battle:Battle):
    # tournaments = Tournament.objects.all()
    winner = battle.winner
    

    # for tournament in tournaments:
    #     if battle in tournament.battles.all():
    #         battle_tournament = tournament
    #         break
    battle_tournament = TournamentBattle.objects.get(battle = battle).tournament
    if(battle_tournament):
        rounds = math.ceil(math.log2(battle_tournament.n_participants))

        fighter_tournament =  FighterTournament.objects.get(tournament = battle_tournament, fighter = winner)  
        current_round = fighter_tournament.round

        #if the current round is the last round(final), award the winner, send a notification to all fighters of the tournament and end the tournament
        if current_round == rounds:
            if winner == battle.initiator:
                loser = battle.opponent
            elif winner == battle.opponent:
                loser = battle.initiator

            #Reward winner
            core_views.add_points(winner,battle_tournament.reward)
            
            #Reward second
            reward2 = int(battle_tournament.reward / 2) 
            core_views.add_points(loser,reward2)

            new_notif = Notification.objects.create(
                target = winner,
                content = f'Congratulations you won the {battle_tournament.name} tournament, you are rewarded with {battle_tournament.reward} BP',
                url = f'/events/tournaments/{battle_tournament.id}',
            )
            new_notif.save()

            new_notif2 = Notification.objects.create(
                target = loser,
                content = f'You lost in the final of {battle_tournament.name} tournament, you are rewarded with {reward2} BP',
                url = f'/events/tournaments/{battle_tournament.id}',
            )
            new_notif2.save()

            for fighter in battle_tournament.fighters.exclude(
                Q(user = winner.user) | Q(user = loser.user)):
                battle_tournament.status = 'finished'

                new_notif = Notification.objects.create(
                    target = fighter,
                    content = f'The tournament {battle_tournament.name} has ended with {winner} being the winner',
                    url = f'/events/tournaments/{battle_tournament.id}',
                )

                new_notif.save()
                battle_tournament.save()
        else:
            #increase fighter round
            new_round = current_round + 1
            fighter_tournament.round = new_round
            fighter_tournament.save()

            new_notif  = Notification.objects.create(
                target = winner,
                content = f'You are in for the next round in the tournament {battle_tournament.name}',
                url = f'/events/tournaments/{battle_tournament.id}',
            )         
            new_notif.save()
            
            #if all the battles of the last round are finished, create the battles for the new round
            #get the battles of the last round
            tournament_battles = TournamentBattle.objects.filter(tournament = battle_tournament, round = current_round)
            battles_ids = tournament_battles.values_list('battle',flat=True) 
            current_round_battles = [ Battle.objects.get(id = battle_id) for battle_id in battles_ids ]
            current_round_battles = Battle.objects.filter(id__in = battles_ids)
            
            #if all battles are finished, create battles for the next round
            if len(current_round_battles.filter(status = 'finished')) == len(current_round_battles):
                #create battles for the next round
                new_round_fighters_tournament = FighterTournament.objects.filter(tournament = battle_tournament, round = new_round)
                
                new_round_fighters_ids = new_round_fighters_tournament.values_list('fighter',flat=True) 
                new_round_fighters = [ Player.objects.get(id = fighter_id) for fighter_id in new_round_fighters_ids ]
                create_round_battles(tournament = battle_tournament, fighters = new_round_fighters, round = new_round)


            
def battles(request, tournament_id):
    player = Player.objects.get(user = request.user)
    tournament = get_object_or_404(Tournament, id = tournament_id)
    rounds = math.ceil(math.log2(tournament.n_participants))

    battles = _roundsBattles(player, tournament, rounds)

    return JsonResponse({'status':'success','battles':battles})

def _can_participate(player:Player,tournament:Tournament):
    referees = tournament.refrees.all()
    fighters = tournament.fighters.all()
    can_participate = {
        'can': True,
        'message':''
    }
    if tournament.status != 'registering':
        can_participate['can'] = False
        can_participate['message'] = "Des joueurs ne peuvent plus s'inscrire a ce tournois"
    elif player  in fighters:
        can_participate['can'] = False
        can_participate['message'] = "Vous participer déja a ce tournois en tant que joueur"

    elif player in referees:
        can_participate['can'] = False
        can_participate['message'] = "Vous étes un arbitre dans ce tournois"   
    elif  len(fighters) >= tournament.n_participants:
        can_participate['can'] = False
        can_participate['message'] = "Le nombre de participants pour ce tournois est déja atteint" 
    
    return can_participate

@login_required
def tournament(request, id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    tournament = get_object_or_404(Tournament, id = id)
    characters = get_characters()
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"])
    referees = tournament.refrees.all()
    fighters = tournament.fighters.all()
    remaining_fighters = tournament.n_participants - len(fighters)
    remaining_referees = int((tournament.n_participants/2) - len(referees))
    rounds = math.ceil(math.log2(tournament.n_participants))

    rounds_battles = _roundsBattles(player,tournament, rounds)
    can_participate = _can_participate(player, tournament)
    battles = tournament.battles.all().order_by('-date_started')

    if request.method == "POST":
        join_type = request.POST['join_type']
        
        if join_type == 'fighter':
            character = request.POST['character']
            
            if player  in fighters:
                messages.error(request, f"You are already in this tournament")
            elif player in referees:
                messages.error(request, f"You can't fight in a tournament in which you are a referee")    
            elif  len(fighters) >= tournament.n_participants:
                   #if the number of participants have been reached
                   messages.error(request, f"The number of participants have already been reached")       
            elif player.battle_points < tournament_cost:
                messages.error(request, f"You do not have enough battle points to participate") 
            else:
                
                tournament.fighters.add(player, through_defaults={'character':character})
                
                player.save()
                tournament.save()
                core_views.remove_points(player, tournament.participation_cost)
                messages.success(request, f"You were added to the tournament succesfully with the character {character}")

                #initialize tournament if conditions are met    
                if _can_start(tournament):
                    init_tournament(tournament)

        elif join_type == 'referee':
            round1_battles = int(tournament.n_participants / 2)
            player_badges = player.badges.all()

            if len(referees) >= round1_battles:
                messages.error(request, f"The number of referees have already been reached") 
            
            elif not battle_views._isReferee(player):
                messages.error(request, f"You need to be an official referee to referee in a tournament") 
            
            elif player in referees:
                messages.error(request, f"You are already a referee in this tournament")
            
            elif player in fighters:
                messages.error(request, f"You can't referee in a tournament in which yoou are a fighter")      

            else:
                tournament.refrees.add(player)
                messages.success(request, f"You are now a referee in this tournament")
                tournament.save()
                #initialize tournament if conditions are met   
                if _can_start(tournament):
                    init_tournament(tournament)

        tournament.save()
        return HttpResponseRedirect(reverse("events:tournament", args=[tournament.id]))
            
    #init_tournament(tournament)
    context = {
        'tournament':tournament,
        'allowed_referees':int(tournament.n_participants/2),
        'referees': referees,
        'fighters':fighters,
        "remaining_fighters":remaining_fighters,
        "remaining_referees":remaining_referees,
        "player":player,
        "n_notifs":core_views.get_notifs(player),
        "characters":sorted_characters,
        'rounds_battles':rounds_battles,
        'can_participate': can_participate,
        'battles': battle_views._battles_data(player,battles)[:3]

        }

    return render(request, "events/tournaments/tournament.html", context)

def create_tournament(request):
    player = get_object_or_404(Player, user = request.user)
    context = {
        "player":player
    }
    return render(request, "events/tournaments/create.html", context)

