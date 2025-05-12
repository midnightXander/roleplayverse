from utility import get_characters,get_refree_questions,_parse_number,_time_since, get_solo_battle_characters, _solo_battle_character
import json
from .models import BASIC_ACTIONS
import random
from datetime import datetime


def _bot_action(character, player_action:dict):
    SPECIAL_ATTACKS = character.get('jutsus')
    possible_actions = BASIC_ACTIONS + SPECIAL_ATTACKS
    action = random.choice(possible_actions)
    #allow bot to use substitution only if the player is attacking
    not_allowed_substitution_actions = ['Defend', 'Focus', 'Heal', 'Substitution']
    if action.get('name') == 'Substitution' and player_action.get('name') in not_allowed_substitution_actions:
        action = random.choice(possible_actions)

    elif player_action.get('name') == 'Defend':
        action = random.choice(SPECIAL_ATTACKS) #Use a special attack if the player defend

    if character.get('chakra') <= 0:
        action = BASIC_ACTIONS[2] #focus if no chakra left    

    return action

def _log_actions(player_action:dict, bot_action:dict, player_character:dict, bot_character:dict):    
    # Log the actions taken by both players
    new_log = []
    action = player_action.get('name')
    if action == 'Attack':
        text = f"{player_character['name']} attacked {bot_character['name']} with taijutsu"
    elif action == 'Focus':
        text = f"{player_character['name']} focused, regaining 40 chakra"
    elif action == 'Heal':
        text = f"{player_character['name']} healed, regaining 20 hp"
    elif action == 'Defend':
        text = f"{player_character['name']} defended against {bot_character['name']}'s action"
    elif action == 'Substitution':
        text = f"{player_character['name']} used substitution to dodge {bot_character['name']}'s attack"
    else:
        text = f"{player_character['name']} used {action} on {bot_character['name']}"

    new_log.append({
        'text': text,
        'type': 'player',
        'result': 'success',
        'timestamp': datetime.now().strftime("%H:%M"),
    }) 

    #Bot
    action = bot_action.get('name')
    if action == 'Attack':
        text = f"{bot_character['name']} attacked {player_character['name']} with taijutsu"
    elif action == 'Focus':
        text = f"{bot_character['name']} focused, regaining 40 chakra"
    elif action == 'Heal':
        text = f"{bot_character['name']} healed, regaining 20 hp"
    elif action == 'Defend':
        text = f"{bot_character['name']} took a defensive stance"
    elif action == 'Substitution':
        text = f"{bot_character['name']} used substitution to dodge {player_character['name']}'s attack"
    else:
        text = f"{bot_character['name']} used {action} on {player_character['name']}"                   

    new_log.append({
        'text': text,
        'type': 'bot',
        'result': 'success',
        'timestamp': datetime.now().strftime("%H:%M"),
    })
    
        
    return new_log

def _damage(chakra_cost):
    return random.randint(10, 20) + chakra_cost // 2

def _update_hp(character, damage):
    current_hp = character.get('hp')
    current_hp = current_hp - damage
    character['hp'] = max(current_hp, 0)
    return character['hp']

def _update_chakra(character, chakra_cost):
    current_chakra = character.get('chakra')
    current_chakra = current_chakra - chakra_cost
    character['chakra'] = max(current_chakra, 0)
    return character['chakra']
    

def _check_winner(player_character:dict, bot_character:dict):
    if player_character.get('hp') <= 0:
        return 'bot'
    elif bot_character.get('hp') <= 0:
        return 'player'
    return None

def _evaluate_actions(player_character:dict, bot_character:dict, player_action:dict, bot_action:dict):
    player_success = random.choice([1,2])
    result = 'succeded' if player_success == 1 else 'failed'
    new_log = []

    non_offensive_actions = ['Defend', 'Focus', 'Heal', 'Substitution']
    type = 'info'
    current_hp = player_character.get('hp')
    current_chakra = player_character.get('chakra')
    damage = 0
    text = f"{player_character['name']} used {player_action.get('name')}"
    if player_action.get('name') == 'Focus':
        chakra_pool = player_character.get('chakra_pool')
        current_chakra =  player_character.get('chakra') + 40
        player_character['chakra'] = min(current_chakra, chakra_pool)
        
    elif player_action.get('name') == 'Heal':
        current_hp = player_character.get('hp') + 30
        player_character['hp'] = min(current_hp, 200)
        #_update_chakra(player_character, player_action.get('chakra_cost'))

    elif player_action.get('name') == 'Defend':
        text = f" you defended against {bot_character['name']}'s attack"
        if bot_action.get('name') not in non_offensive_actions:
            damage = _damage(bot_action.get('chakra_cost'))
            damage = damage // 2
            text = f" your defense reduced damage, you take {damage} damage"
            type = 'warning'
        elif bot_action.get('name') == 'Substitution':
            damage = 0
            text = f" {bot_character['name']} dodged with substitution"
            type = 'info'
        current_hp = player_character.get('hp') - damage
        player_character['hp'] = max(current_hp, 0)

    elif player_action.get('name') not in non_offensive_actions:
        damage = _damage(player_action.get('chakra_cost'))
        text = f" you dealt {damage} damage"
        type = 'success'
        if bot_action.get('name') == 'Defend':
            damage = damage // 2
            text = f" {bot_character['name']} defended against your attack, you dealt {damage} damage"
            type = 'warning'
            current_bot_hp = bot_character.get('hp') - damage
            bot_character['hp'] = max(current_bot_hp, 0)
        elif bot_action.get('name') == 'Substitution':
            damage = 0
            text = f" {bot_character['name']} dodged your attack with substitution"
            type = 'warning'
        else:
            current_bot_hp = bot_character.get('hp') - damage
            bot_character['hp'] = max(current_bot_hp, 0) 
            text = f" you dealt {damage} damage" 
            type = 'success'
    elif player_action.get('name') == 'Substitution':
        damage = 0
        text = f" you dodged with substitution"
        type = 'success' 

    else:
        text = f"{player_character['name']} used {player_action.get('name')} on {bot_character['name']}"
        type = 'info'

    _update_chakra(player_character, player_action.get('chakra_cost'))

        

    new_log.append({
        'text': text,
        'type': type,
        'result': result,
        'timestamp': datetime.now().strftime("%H:%M"),
    })    

    #Evaluate actions by bot
    type = 'danger'
    if bot_action.get('name') == 'Focus':
        chakra_pool = bot_character.get('chakra_pool')
        current_chakra =  bot_character.get('chakra') + 40
        bot_character['chakra'] = min(current_chakra, chakra_pool)
    elif bot_action.get('name') == 'Heal':
        current_hp = bot_character.get('hp') + 30
        bot_character['hp'] = min(current_hp, 100)

    # elif bot_action.get('name') == 'Defend':
    #     text = f" {bot_character['name']} took a defensive  stance"
        # if player_action.get('name') not in non_offensive_actions:
        #     damage = _damage(player_action.get('chakra_cost'))
        #     damage = damage // 2
        #     text = f" {bot_character['name']} defended against your attack, you dealt {damage} damage"
        #     type = 'warning'
        # elif player_action.get('name') == 'Substitution':
        #     damage = 0
        #     type = 'info'
        # current_hp = bot_character.get('hp') - damage
        # bot_character['hp'] = max(current_hp, 0)
    elif bot_action.get('name') not in non_offensive_actions and player_action.get('name') != 'Defend':
        damage = _damage(bot_action.get('chakra_cost'))
        text = f"you took {damage} damage"
        type = 'danger'
        # if player_action.get('name') == 'Defend':
        #     damage = damage // 2
        #     text = f" you defended against {bot_character['name']}'s attack, you dealt {damage} damage"
        #     type = 'warning'
        # if player_action.get('name') == 'Substitution':
        #     damage = 0
        #     text = f" you dodged with substitution"
        #     type = 'info'
        current_hp = player_character.get('hp') - damage
        player_character['hp'] = max(current_hp, 0) 

    _update_chakra(bot_character, bot_action.get('chakra_cost'))
    new_log.append({
        'text': text,
        'type': type,
        'result': result,
        'timestamp': datetime.now().strftime("%H:%M"),
    })

    winner = _check_winner(player_character, bot_character)
    if winner == 'player':
        new_log.append({
            'text': f"{player_character['name']} won the battle",
            'type': 'success',
            'result': 'success',
            'timestamp': datetime.now().strftime("%H:%M"),
        })
    elif winner == 'bot':
        new_log.append({
            'text': f"{bot_character['name']} won the battle",
            'type': 'danger',
            'result': 'failed',
            'timestamp': datetime.now().strftime("%H:%M"),
        })
    # else:
    #     new_log.append({
    #         'text': "The battle ended in a draw",
    #         'type': 'info',
    #         'result': 'draw',
    #         'timestamp': datetime.now().strftime("%H:%M"),
    #     })

    return player_character, bot_character, new_log , winner      
