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

    elif player_action.get('name') == 'Defend' or player_action.get('name') == 'Focus':
        ATTACKS:list = SPECIAL_ATTACKS
        ATTACKS.append(BASIC_ACTIONS[0]) #attack if the player defend or focus
        weights = [ 1 for weight in range(len(ATTACKS))]  
        weights[0] = 2 #attack with special attack
        action = random.choices(ATTACKS, weights=weights) #likely attack with special attack if the player defend or focus
        
        action = action[0]
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
        player_character['hp'] = min(current_hp, player_character.get('health', 200))
        print(f'player heal: ', player_character['hp'])
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
        print(f'player substituted: ', player_character['hp'])

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
        bot_character['hp'] = min(current_hp, bot_character.get('health', 200))

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
    elif bot_action.get('name') not in non_offensive_actions and player_action.get('name') not in ['Defend', 'Substitution']:
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



def evaluate_state(player_character, bot_character):
    #Example evaluation function
    # print("State: ",(bot_character['hp'] - player_character['hp']) + (bot_character['chakra'] - player_character['chakra']) )
    return (bot_character['hp'] - player_character['hp']) * 2 + (bot_character['chakra'] - player_character['chakra']) 


def _simulate_action(character, opponent, action, is_bot):
    attacks = [ jutsu['name'] for jutsu in character['jutsus']] 
    attacks.append(BASIC_ACTIONS[0]['name'])  # Add the basic attack action
    # print(attacks)
    if action['name'] in attacks:
        # If the action is an attack, calculate damage and apply it to the opponent
        damage = _damage(action.get('chakra_cost'))
        opponent['hp'] = max(opponent['hp'] - damage, 0)
    elif action['name'] == 'Focus':
        character['chakra'] = min(character['chakra'] + 40, character['chakra_pool'])
    elif action['name'] == 'Heal':
        character['hp'] = min(character['hp'] + 30, character.get('health', 200))
        character['chakra'] = max(character['chakra'] - 20, 0)
    elif action['name'] == 'Defend':
        # Reduce damage from opponent's attack
        damage = _damage(action.get('chakra_cost'))
        damage = damage // 2
        opponent['hp'] = max(opponent['hp'] - damage, 0)
    elif action['name'] == 'Substitution':
        # Avoid damage from opponent's attack
        damage = 0
        character['hp'] = min(character['hp'] + 100, character.get('health', 200))
        character['chakra'] = max(character['chakra'] - 5, 0)

    


def minimax(player_character, bot_character, depth, is_maximizing, alpha, beta):
    # Base case: Check for terminal state (win/loss) or maximum depth
    winner = _check_winner(player_character, bot_character)
    if winner == 'player':
        return 1000 #player wins
    elif winner == 'bot':
        return -1000
    elif depth == 0:
        return evaluate_state(player_character, bot_character)
    
    # Recursive case: Simulate actions
    if is_maximizing:
        max_eval = float('-inf')
        for action in bot_character['jutsus'] + BASIC_ACTIONS:
            # Simulate bot's action
            simulated_bot = bot_character.copy()
            simulated_player = player_character.copy()
            _simulate_action(simulated_bot, simulated_player, action, is_bot=True)

            # Recursively evaluate the state
            eval = minimax(simulated_player, simulated_bot, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return max_eval
    else:
        min_eval = float('inf')
        for action in player_character['jutsus'] + BASIC_ACTIONS:
            # Simulate player's action
            simulated_bot = bot_character.copy()
            simulated_player = player_character.copy()
            _simulate_action(simulated_player, simulated_bot, action, is_bot=False)

            # Recursively evaluate the state
            eval = minimax(simulated_player, simulated_bot, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return min_eval

def _bot_action_minimax(player_character, bot_character, depth=3):
    best_action = None
    max_eval = float('-inf')

    

    for action in bot_character['jutsus'] + BASIC_ACTIONS:
        # Simulate bot's action
        simulated_bot = bot_character.copy()
        simulated_player = player_character.copy()
        _simulate_action(simulated_bot, simulated_player, action, is_bot=True)

        # Evaluate the action using Minimax
        eval = minimax(simulated_player, simulated_bot, depth - 1, False, float('-inf'), float('inf'))
        if eval > max_eval:
            max_eval = eval
            best_action = action
    
    #If the bot can reduce the hp level of the player to less than 30, it will attack
    bot_attacks = bot_character['jutsus']
    bot_attacks.append(BASIC_ACTIONS[0])  # Add the basic attack action
    max_damage = 0
    
    for action in bot_attacks:
        damage = _damage(action['chakra_cost'])
        if damage > max_damage:
            max_damage = damage
            best_action = action

    #Focus if bot does not have enough chakra needed for his attack
    print(bot_character['chakra'], best_action['chakra_cost'])
    if best_action['chakra_cost'] >= bot_character['chakra']:
        best_action = BASIC_ACTIONS[2]  # Focus action
        return best_action
    
    player_hp_after_attack = max(player_character['hp'] - max_damage, 0)
    if player_hp_after_attack < 30 and best_action['name'] != 'Substitution':
        # If the bot can reduce the player's HP to less than 30, it will attack
        return best_action    

    

    return best_action    