from django.shortcuts import get_object_or_404, redirect, render
from battles.models import SoloBattle
from battles.solo_battle import *
from battles.solo_battle import _bot_action
from battles.solo_battle import _bot_action_minimax
from battles.solo_battle import _log_actions
from battles.solo_battle import _evaluate_actions
from users.models import Player
from utility import _solo_battle_character, get_solo_battle_characters, get_adventure_character, get_adventure_characters
from .models import *
import json, random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os
import json


BASE_DIR = Path(__file__).resolve().parent
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
        new_appearance = CharacaterAppearance.objects.create(
            image=request.FILES.get('appearance'))
        new_appearance.save()
        appearance = new_appearance.image.url if request.FILES.get('appearance') else random.choice(character_appearances)
        
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
        
        AdventurePlayer.objects.create(
            player=player,
            character=character_data,
        ).save()
        
        return HttpResponseRedirect('/adventure/game')


    return render(request, 'adventure/create.html')


def create_zones():
    MapZone.objects.create(
                    name='Default Zone',
                    description="Default zone for later",
                    # min_level=zone.get('min_level', 1),
                    # max_level=zone.get('max_level', 100),
                    level_required=random.randint(1, 3),
                    data={}
                ).save()
    zones_file = os.path.join(BASE_DIR, 'static/jsons/zones.json')
    if not os.path.exists(zones_file):
        raise FileNotFoundError(f"Zones file not found at {zones_file}")
    with open(zones_file, 'r', encoding='utf-8') as file:
        zones_data = json.load(file)
        count = 0
        for zone in zones_data:
            zone_data = zone.get('data', {})
            if MapZone.objects.filter(name = zone['name'] ).exists():
                pass
            else:
                MapZone.objects.create(
                    name=zone['name'],
                    description=zone['description'],
                    # min_level=zone.get('min_level', 1),
                    # max_level=zone.get('max_level', 100),
                    level_required=zone.get('level_required', random.randint(1, 3)),
                    image=zone.get('image', None),
                    data=zone_data
                ).save()
                count += 1

    print(f'created {count} zones')            

def assign_zones_to_missions():
    missions_file = os.path.join(BASE_DIR, 'static/jsons/missions.json')
    if not os.path.exists(missions_file):
        raise FileNotFoundError(f"missions file not found at {missions_file}")
    with open(missions_file, 'r', encoding='utf-8') as file:
        missions_data = json.load(file)
        for mission in missions_data:
            min_level = mission.get('min_level',1)
            max_level = mission.get('max_level', 5)

            mission_zone = MapZone.objects.filter(level_required = min_level).order_by('?').first()
            if mission_zone:
                mission['zone'] = mission_zone.name
            else:
                mission['zone'] = 'Default Zone'    

    with open(missions_file, 'w') as f:
        json.dump(missions_data, f, indent=4)        


def create_missions():
    missions_file = os.path.join(BASE_DIR, 'static/jsons/missions.json')
    if not os.path.exists(missions_file):
        raise FileNotFoundError(f"missions file not found at {missions_file}")
    with open(missions_file, 'r', encoding='utf-8') as file:
        missions_data = json.load(file)
        count = 0
        for mission in missions_data:
            mission_data = mission.get('data', {})
            # obj,created = MissionTemplate.objects.get_or_create(
            #     title = mission['title'],
            #     defaults = mission,
            # )
            MissionTemplate.objects.create(
                title=mission['title'],
                description=mission['description'],
                min_level=mission.get('min_level', 1),
                max_level=mission.get('max_level', 100),
                mission_type=mission['mission_type'],
                target=mission.get('target', ''),
                quantity=mission.get('quantity', 1),
                reward_exp=mission.get('reward_exp', 50),
                reward_item=mission.get('reward_item', ''),
                zone = MapZone.objects.filter(name=mission.get('zone', 'Default Zone')).first()  # Assuming a default zone if not specified

            ).save()
            count += 1

        print(f"Created {count} missions")    


def _mission_data(mission:MissionTemplate):
    return {
        'id': mission.id,
        'title' : mission.title,
        'description' : mission.description,
        'min_level' : mission.min_level,
        'max_level' : mission.max_level,
        'type' : mission.mission_type,
        'target' : mission.target,
        'reward_exp' : mission.reward_exp,
        # 'zone' : {
        #     'name' : mission.zone.name
        # }
    }


def _zone_data(zone:MapZone):
    return {
        'id' : zone.id,
        'name'  : zone.name,
        'key' : zone.name.strip().lower().replace(' ', '-').replace("'", ''),
        'description' : zone.description,
        'missions' : [ _mission_data(mission) for mission in MissionTemplate.objects.filter(zone = zone) ]
    }


@login_required
def game(request):
    
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player= player).first()
    
    if not adventure_player:
        return redirect('adventure:create_character')
    
    # create_zones()
    # assign_zones_to_missions()
    # create_missions()
    # assign_random_mission(player)

    zones = MapZone.objects.filter(level_required__lte = adventure_player.level)
    zones = [_zone_data(zone) for zone in zones]
       


    return render(request, 'adventure/game.html',{
        'player': player,
        'adventure_player': adventure_player,
        'zones' : zones
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

@login_required
def mission(request, mission_id):
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player=player).first()
    if not adventure_player:
        return redirect('adventure:create_character')

    #mission = get_object_or_404(PlayerMission, id=mission_id, player=player)
    missionTemplate = get_object_or_404(MissionTemplate, id=mission_id)
    mission,created = PlayerMission.objects.get_or_create(
        player=player, template = missionTemplate)

    
    # if request.method == 'POST':
    #     check_mission_completion(player, mission)
    #     return redirect('adventure:game')

    return render(request, 'adventure/mission.html', {
        'player': player,
        'adventure_player': adventure_player,
        'mission': mission
    })

def init_mission(request, mission_id):
    player = Player.objects.get(user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player=player).first()
    player_mission = get_object_or_404(PlayerMission, id=mission_id, player=player)
    target = player_mission.template.target
    if request.method == 'POST':
        
        player_character = adventure_player.character
        # bot_character = get_adventure_character(target)
        bot_character = get_adventure_character("Bandit")
        if not bot_character:
            return JsonResponse({'message': 'target character not found'})
        
        #set the health based on the character level
        bot_character['health'] = bot_character.get('health', 100) + (bot_character.get('level') * 10)

        player_character['hp'] = player_character['health']
        bot_character['hp'] = bot_character.get('health', 100)
        player_character['chakra'] = player_character.get('chakra_pool',100)
        bot_character['chakra'] = bot_character.get('chakra_pool',100)
        #bot_character['image'] = bot_character.get('image', 'default_image.png')  # Ensure bot has an image

        battle = SoloBattle.objects.create(
            type = 'adventure',
            player = player,
            player_character = player_character,
            bot_character = bot_character,
        )

        battle.save()


        return JsonResponse({'message': 'battle initialized', 'bot_character': bot_character, 'player_character': player_character})

def mission_battle_action(request, mission_id):
    """Handle the battle action during a mission."""
    player = get_object_or_404(Player, user=request.user)
    adventure_player = AdventurePlayer.objects.filter(player=player).first()
    mission = get_object_or_404(PlayerMission, id=mission_id, player=player)
    if request.method == 'POST':
        action = request.POST.get('action')

        battle = SoloBattle.objects.filter(player=player).last()
        player_character = battle.player_character
        bot_character = battle.bot_character
        possible_actions = player_character['basic_actions'] + player_character['jutsus']

        player_action = player_character['basic_actions'][0]

        for act in possible_actions:
            if act['name'] == action:
                player_action = act

        bot_action = _bot_action(bot_character, player_action)
        bot_action = _bot_action_minimax(player_character, bot_character)

        new_logs = _log_actions(player_action, bot_action, player_character, bot_character)
        logs = json.loads(battle.log)
        for log in new_logs:
            logs.append(log)

        player_character, bot_character, new_logs, winner =  _evaluate_actions(player_character, bot_character, player_action, bot_action)
        logs = logs + new_logs


        rewards = {'xp' : 0, }
        if winner == 'player':
            rewards['xp'] += 50
            #rewards = _reward_player(player)
            battle.result = 'win'
            battle.finished = True
            battle.date_ended = datetime.now()
            check_mission_completion(player, mission)

        elif winner == 'bot':
            battle.result = 'lose'
            battle.finished = True
            battle.date_ended = datetime.now()

        battle.log = json.dumps(logs)
        battle.save()

        return JsonResponse({'battle_logs': logs, 'player_character' : player_character, 'bot_character' : bot_character, 'winner' : winner, 'rewards': rewards})