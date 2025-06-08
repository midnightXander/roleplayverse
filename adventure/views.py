from django.shortcuts import get_object_or_404, redirect, render
from battles.models import SoloBattle
from battles.solo_battle import *
from battles.solo_battle import _bot_action
from battles.solo_battle import _bot_action_minimax
from battles.solo_battle import _log_actions
from battles.solo_battle import _evaluate_actions
from users.models import Player
from utility import _solo_battle_character, get_solo_battle_characters
from .models import *
import json, random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.
# {
#     "name": "Naruto Uzumaki",
#     "rank": "Jounin",
#     "chakra_pool": 200,
#     "stamina_pool": 180,
#     "jutsus": [
#       
#     ]
#   }



def create_character(request):
    player = Player.objects.get(user=request.user)
    if request.method == 'POST':
        character_appearances = [ appearance.image.url for appearance in CharacaterAppearance.objects.all() ]
        appearance = request.FILES.get('appearance') if request.FILES.get('appearance') else random.choice(character_appearances)
        name = request.POST.get('name') 
        clan = request.POST.get('clan', random.choice(CLANS)),  # Randomly select a clan if not provided),
        character_data = {
            'name': f"{name} {clan}",  # Combine name and clan for character name
            'rank': 'Genin',  # Default rank, can be changed later
            'chakra_pool': 100,  # Default chakra pool 
            'stamina_pool': 100,  # Default stamina pool
            'health': 100,  # Default health
            'nindo' : request.POST.get('nindo', 'To become Hokage!'),  # Default nindo if not provided
            'appearance': appearance ,  # Use uploaded image or a random one
            'image' : appearance,
            'clan': clan,
            'gender': request.POST.get('gender'),
            'element': request.POST.get('element'),
            'inventory': [],  # Start with an empty inventory
            'basic_actions' : [
                { "name": 'Attack', 'chakra_cost': 10, 'stamina_cost' : 10},
                    { 'name': 'Defend', 'chakra_cost': 5, 'stamina_cost': 20},
                    { 'name': 'Focus', 'chakra_cost': 0, 'stamina_cost':0 },
                    { 'name': 'Heal', 'chakra_cost': 20, 'stamina_cost' : 5 },
                    { 'name': 'Substitution', 'chakra_cost': 15, 'stamina_cost': 10}
            ],
            # 'jutsus': request.POST.getlist('skills'),
            'jutsus' : [] # no special skills by default
        }
        
        adventure_player = AdventurePlayer.objects.create(
            player=player,
            character=character_data,
        )
        
        return HttpResponseRedirect('/adventure/game')


    return render(request, 'adventure/create.html')

@login_required
def game(request):
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player= player).first()
    if not adventure_player:
        return redirect('adventure:create_character')
    

    return render(request, 'adventure/game.html',{
        'player': player,
        'adventure_player': adventure_player,
    })

def training(request):
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player= player).first()
    if not adventure_player:
        return redirect('adventure:create_character')
    
    
    
    return render(request, 'adventure/training.html', {
        'player': player,
        'adventure_player': adventure_player,
    })


def init_training(request):
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player= player).first()
    if request.method == 'POST':
        characters = get_solo_battle_characters()
        player_character = adventure_player.character
        bot_character = random.choice(characters)
        # if bot_character['name'] == player_character['name'] : 
        #     bot_character = random.choice(characters)
        # if player_character not in characters:
        #     return JsonResponse({'message': 'character not found'})
        
        player_character['hp'] = player_character['health']
        bot_character['hp'] = 200
        player_character['chakra'] = player_character.get('chakra_pool',100)
        bot_character['chakra'] = bot_character.get('chakra_pool',100)


        battle = SoloBattle.objects.create(
            type = 'training',
            player = player,
            player_character = player_character,
            bot_character = bot_character,
        )

        battle.save()


        return JsonResponse({'message': 'battle initialized', 'bot_character': bot_character, 'player_character': player_character})

def training_battle_action(request):
    player = get_object_or_404(Player, user = request.user)
    if request.method == 'POST':
        # model = JsonTestModel.objects.get(id = 2)
        action = request.POST.get('action')
        
        battle = SoloBattle.objects.filter(player = player).order_by('-date_started')[0]
        player_character = battle.player_character
        bot_character = battle.bot_character
        possible_actions = player_character['basic_actions'] + player_character['jutsus']
        
        player_action = player_character['basic_actions'][0]

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
        

        rewards = {'xp' : 0, }
        if winner == 'player':
            #rewards = _reward_player(player)
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

def assign_random_mission(player):
    adventure_player = AdventurePlayer.objects.get(player = player)
    current_level = adventure_player.level
    eligible_missions = MissionTemplate.objects.filter(min_level__lte=current_level, max_level__gte=current_level)

    # Exclure missions déjà reçues récemment
    already_received = PlayerMission.objects.filter(player=player).values_list('template_id', flat=True)
    filtered = eligible_missions.exclude(id__in=already_received)

    if filtered.exists():
        selected = random.choice(filtered)
        return PlayerMission.objects.create(player=player, template=selected)

def check_mission_completion(player:Player, mission:PlayerMission):
    """    Vérifie si une mission est terminée et met à jour le statut du joueur en conséquence.
    """
    success = False

    if mission.template.mission_type == 'defeat':
        success = player.defeated_targets.count(mission.template.target) >= mission.template.quantity

    elif mission.template.mission_type == 'collect':
        success = player.inventory.count(mission.template.target) >= mission.template.quantity

    elif mission.template.mission_type == 'explore':
        success = mission.template.target in player.unlocked_zones

    if success:
        mission.status = 'done'
        mission.save()
        # Ajouter récompenses
        player.experience += mission.template.reward_exp
        if mission.template.reward_item:
            player.inventory.append(mission.template.reward_item)
        player.save()
